#!/usr/bin/env python3
"""Quantify metric-robust entanglement-trajectory morphology and its limits."""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from entanglement_trajectories.dataset import read_trajectory_csv
from entanglement_trajectories.models import MODEL_LABELS, MODEL_ORDER
from entanglement_trajectories.plotting import save_figure
from entanglement_trajectories.robustness import (
    BOUNDARY_HEIGHT_COLUMNS,
    HALF_METRICS,
    add_exact_boundary_coordinates,
    cross_metric_classification,
    fit_common_metric_mode,
    majorization_tolerance_sensitivity,
    majorization_transition_audit,
    metric_direction_events,
    model_centroid_geometry_preservation,
    one_site_aggregate_robustness,
    pairwise_metric_robustness,
    per_trajectory_common_mode_table,
    trajectory_geometry_preservation,
    x_only_classification,
)

METRIC_LABELS = {
    "half_logneg": r"Renyi $q=1/2$",
    "half_vn": r"Renyi $q=1$",
    "half_linear": r"Renyi $q=2$ class",
}
PAIR_LABELS = {
    ("half_vn", "half_linear"): r"$q=1$ vs $q=2$",
    ("half_vn", "half_logneg"): r"$q=1$ vs $q=1/2$",
    ("half_linear", "half_logneg"): r"$q=2$ vs $q=1/2$",
}

FIGURE_METADATA = {
    "figure_01_common_metric_modes": {
        "question": "Does a shared metric coordinate survive exact-boundary normalization?",
        "answer": "Yes. The leading standardized component explains 90.26% of boundary-coordinate variance; the main contrast is order-2 dominated.",
        "alt_text": "Two bar charts show a dominant common component and a smaller contrast component with a large negative order-2 loading.",
    },
    "figure_02_metric_robustness_across_sizes": {
        "question": "Does within-trajectory cross-metric agreement persist from 10 to 20 qubits?",
        "answer": "Yes, but hierarchically: order 1 and order 1/2 remain closest, while pairs involving order 2 are weaker.",
        "alt_text": "Line plots of mean Spearman correlation across six sizes; raw curves remain near one and boundary-relative curves remain positive but metric-pair dependent.",
    },
    "figure_03_relational_geometry_preservation": {
        "question": "Is the distance and neighbor structure among physical trajectories preserved under metric replacement?",
        "answer": "Substantially, especially for order 1 versus order 1/2; full-path agreement is higher partly because lambda_max is shared.",
        "alt_text": "Two line charts compare distance-rank correlation and nearest-neighbor overlap for vertical-only and full trajectories.",
    },
    "figure_04_generalization_limits": {
        "question": "Does the trajectory act as a held-out model fingerprint?",
        "answer": "Model-centroid morphology generalizes well; unseen individual conditions are much weaker and do not clearly beat lambda_max alone.",
        "alt_text": "Two cross-metric accuracy heat maps, bright for held-out model centroids and much darker for simultaneously held-out individual size and condition.",
    },
    "figure_05_majorization_and_metric_competition": {
        "question": "Where do valid metric contradictions occur?",
        "answer": "Every observed contradiction in the selected full-spectrum audit occurs on a majorization-incomparable transition.",
        "alt_text": "Three stacked bars show only consensus on majorization-compatible transitions and a metric-competition segment only for incomparable spectra.",
    },
    "figure_06_common_mode_model_paths_n20": {
        "question": "Do model families remain distinct in the shared metric mode?",
        "answer": "The four n=20 model-centroid paths occupy distinct regions and directions in lambda_max versus common-mode coordinates.",
        "alt_text": "Four colored model-centroid paths follow visibly different routes in a shared two-dimensional trajectory plane.",
    },
    "figure_07_coarse_vs_fine_stability": {
        "question": "Which geometric properties survive metric replacement?",
        "answer": "Full-path arc-length and vertical total-variation orderings persist, origin-closed area is less stable, and exact local turn counts mostly change.",
        "alt_text": "Grouped bars show high arc-length rank agreement, moderate signed-area agreement, and low exact turn-count agreement.",
    },
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False), encoding="utf-8")


def _bootstrap_pair_summary(
    table: pd.DataFrame,
    *,
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    """Model-stratified design-cluster sensitivity intervals.

    The four conditions within each dynamical family are resampled with
    replacement while all six sizes for a condition stay together. These are
    sensitivity intervals for the declared designed study, not population
    confidence intervals from independent disorder or parameter draws.
    """
    rng = np.random.default_rng(seed)
    rows = []
    statistics = ("raw_spearman", "boundary_spearman", "boundary_rmse", "boundary_mae")
    for (metric_a, metric_b), subset in table.groupby(["metric_a", "metric_b"], sort=True):
        cluster = (
            subset.groupby(["model", "run_id"], as_index=False)[list(statistics)]
            .mean(numeric_only=True)
            .reset_index(drop=True)
        )
        model_groups = {
            str(model): np.asarray(indices, dtype=int)
            for model, indices in cluster.groupby("model", sort=True).groups.items()
        }
        samples = {name: np.empty(iterations, dtype=float) for name in statistics}
        for index in range(iterations):
            selected = np.concatenate([
                rng.choice(indices, size=len(indices), replace=True)
                for indices in model_groups.values()
            ])
            for name in statistics:
                samples[name][index] = float(np.nanmean(cluster[name].to_numpy()[selected]))
        row = {
            "metric_a": metric_a,
            "metric_b": metric_b,
            "clusters": int(len(cluster)),
            "models": int(len(model_groups)),
            "resampling": "model-stratified design-cluster bootstrap",
            "bootstrap_iterations": int(iterations),
        }
        for name in statistics:
            observed = float(cluster[name].mean())
            lower, upper = np.quantile(samples[name], [0.025, 0.975])
            row[f"{name}_cluster_mean"] = observed
            row[f"{name}_ci_low"] = float(lower)
            row[f"{name}_ci_high"] = float(upper)
        rows.append(row)
    return pd.DataFrame(rows)


def _bootstrap_common_mode(
    enriched: pd.DataFrame,
    fit,
    *,
    iterations: int,
    seed: int,
) -> dict:
    """Fast model-stratified cluster bootstrap from sufficient statistics."""
    rng = np.random.default_rng(seed)
    columns = list(fit.columns)
    cluster_names: list[str] = []
    cluster_models: list[str] = []
    counts: list[int] = []
    sums: list[np.ndarray] = []
    cross_products: list[np.ndarray] = []
    for key, group in enriched.groupby(["model", "run_id"], sort=True):
        values = group[columns].to_numpy(dtype=float)
        values = values[np.all(np.isfinite(values), axis=1)]
        if not len(values):
            continue
        cluster_names.append(f"{key[0]}:{key[1]}")
        cluster_models.append(str(key[0]))
        counts.append(int(len(values)))
        sums.append(values.sum(axis=0))
        cross_products.append(values.T @ values)
    counts_array = np.asarray(counts, dtype=np.int64)
    sums_array = np.stack(sums, axis=0)
    cross_array = np.stack(cross_products, axis=0)
    model_indices = {
        model: np.asarray([i for i, value in enumerate(cluster_models) if value == model], dtype=int)
        for model in sorted(set(cluster_models))
    }
    ev1 = np.empty(iterations, dtype=float)
    loadings = np.empty((iterations, len(columns)), dtype=float)
    for index in range(iterations):
        chosen = np.concatenate([
            rng.choice(indices, size=len(indices), replace=True)
            for indices in model_indices.values()
        ])
        total_count = int(counts_array[chosen].sum())
        total_sum = sums_array[chosen].sum(axis=0)
        total_cross = cross_array[chosen].sum(axis=0)
        mean = total_sum / total_count
        covariance = total_cross / total_count - np.outer(mean, mean)
        scale = np.sqrt(np.maximum(np.diag(covariance), 0.0))
        if np.any(scale <= 0.0):
            ev1[index] = np.nan
            loadings[index] = np.nan
            continue
        correlation = covariance / np.outer(scale, scale)
        correlation = 0.5 * (correlation + correlation.T)
        eigenvalues, eigenvectors = np.linalg.eigh(correlation)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = np.maximum(eigenvalues[order], 0.0)
        component = eigenvectors[:, order[0]].astype(float)
        if component.sum() < 0.0:
            component *= -1.0
        ev1[index] = float(eigenvalues[0] / eigenvalues.sum())
        loadings[index] = component
    finite_ev = ev1[np.isfinite(ev1)]
    finite_loadings = loadings[np.all(np.isfinite(loadings), axis=1)]
    return {
        "cluster_unit": "model:run_id, all six sizes retained together",
        "resampling": "model-stratified with four designed conditions resampled within each model",
        "interpretation": "design-cluster sensitivity interval, not a population confidence interval",
        "clusters": cluster_names,
        "bootstrap_iterations": int(iterations),
        "valid_bootstrap_iterations": int(len(finite_ev)),
        "pc1_explained_observed": float(fit.explained_variance_ratio[0]),
        "pc1_explained_ci95": [float(x) for x in np.quantile(finite_ev, [0.025, 0.975])],
        "pc1_loading_observed": [float(x) for x in fit.components[0]],
        "pc1_loading_ci95": [
            [float(x) for x in np.quantile(finite_loadings[:, column], [0.025, 0.975])]
            for column in range(finite_loadings.shape[1])
        ],
    }


def _finite_index_segments(mask: np.ndarray) -> list[np.ndarray]:
    indices = np.flatnonzero(np.asarray(mask, dtype=bool))
    if not indices.size:
        return []
    split_at = np.flatnonzero(np.diff(indices) > 1) + 1
    return [segment for segment in np.split(indices, split_at) if segment.size]


def _fine_descriptor_table(enriched: pd.DataFrame) -> pd.DataFrame:
    def sign_changes(values: np.ndarray, eps: float = 1e-10) -> int:
        signs = np.where(values > eps, 1, np.where(values < -eps, -1, 0))
        signs = signs[signs != 0]
        return int(np.count_nonzero(signs[1:] != signs[:-1])) if len(signs) > 1 else 0

    rows = []
    for key, group in enriched.groupby(["model", "n", "run_id"], sort=True):
        group = group.sort_values("step")
        x_all = group["half_lambda_max"].to_numpy(dtype=float)
        for metric in HALF_METRICS:
            y_all = group[BOUNDARY_HEIGHT_COLUMNS[metric]].to_numpy(dtype=float)
            segments = _finite_index_segments(np.isfinite(x_all) & np.isfinite(y_all))
            full_arc_length = 0.0
            vertical_total_variation = 0.0
            origin_closed_signed_area = 0.0
            turns = 0
            finite_points = 0
            for segment in segments:
                x = x_all[segment]
                y = y_all[segment]
                finite_points += len(segment)
                if len(segment) >= 2:
                    dx = np.diff(x)
                    dy = np.diff(y)
                    full_arc_length += float(np.sum(np.hypot(dx, dy)))
                    vertical_total_variation += float(np.sum(np.abs(dy)))
                    turns += sign_changes(dy)
                    origin_closed_signed_area += float(
                        0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])
                    )
            rows.append({
                "model": key[0], "n": int(key[1]), "run_id": key[2],
                "metric": metric, "finite_points": int(finite_points),
                "finite_segments": int(len(segments)),
                "full_arc_length": full_arc_length,
                "vertical_total_variation": vertical_total_variation,
                "origin_closed_signed_area": origin_closed_signed_area,
                "vertical_turn_count": turns,
            })
    return pd.DataFrame(rows)


def _fine_descriptor_summary(table: pd.DataFrame) -> pd.DataFrame:
    pivot = table.pivot_table(
        index=["model", "n", "run_id"], columns="metric",
        values=["full_arc_length", "vertical_total_variation", "origin_closed_signed_area", "vertical_turn_count"],
    )
    rows = []
    for metric_a, metric_b in combinations(HALF_METRICS, 2):
        rows.append({
            "metric_a": metric_a,
            "metric_b": metric_b,
            "full_arc_length_rank_spearman": float(spearmanr(pivot["full_arc_length"][metric_a], pivot["full_arc_length"][metric_b]).statistic),
            "vertical_total_variation_rank_spearman": float(spearmanr(pivot["vertical_total_variation"][metric_a], pivot["vertical_total_variation"][metric_b]).statistic),
            "origin_closed_area_rank_spearman": float(spearmanr(pivot["origin_closed_signed_area"][metric_a], pivot["origin_closed_signed_area"][metric_b]).statistic),
            "exact_turn_count_agreement": float(np.mean(pivot["vertical_turn_count"][metric_a].to_numpy() == pivot["vertical_turn_count"][metric_b].to_numpy())),
        })
    all_three = pivot["vertical_turn_count"].nunique(axis=1) == 1
    summary = pd.DataFrame(rows)
    summary.attrs["all_three_turn_count_agreement"] = float(all_three.mean())
    summary.attrs["all_three_turn_count_agreement_count"] = int(all_three.sum())
    summary.attrs["trajectories"] = int(len(all_three))
    return summary


def _event_summary(events: pd.DataFrame) -> pd.DataFrame:
    counts = events.groupby(["model", "n", "event_class"]).size().rename("count").reset_index()
    totals = counts.groupby(["model", "n"])["count"].transform("sum")
    counts["fraction"] = counts["count"] / totals
    return counts


def _classification_runs(df: pd.DataFrame, result_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summaries = []
    predictions = []
    for fold in (
        "centroid_leave_size",
        "individual_leave_size",
        "individual_leave_condition",
        "individual_double_holdout",
    ):
        for mode in ("endpoint", "y", "full"):
            summary, prediction = cross_metric_classification(
                df,
                coordinate="boundary",
                mode=mode,
                fold=fold,
            )
            summaries.append(summary)
            predictions.append(prediction)
    summary_table = pd.concat(summaries, ignore_index=True)
    prediction_table = pd.concat(predictions, ignore_index=True)

    x_summaries = []
    x_predictions = []
    for fold in (
        "centroid_leave_size",
        "individual_leave_size",
        "individual_leave_condition",
        "individual_double_holdout",
    ):
        for mode in ("endpoint", "path"):
            summary, prediction = x_only_classification(df, mode=mode, fold=fold)
            x_summaries.append(summary)
            x_predictions.append(prediction)
    x_summary = pd.concat(x_summaries, ignore_index=True)
    x_prediction = pd.concat(x_predictions, ignore_index=True)
    return summary_table, prediction_table, pd.concat(
        [x_summary.assign(table="summary"), x_prediction.assign(table="prediction")],
        ignore_index=True,
        sort=False,
    )


def _save_common_mode_figure(raw_fit, boundary_fit, path: Path) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3))
    x = np.arange(3)
    width = 0.36
    axes[0].bar(x - width / 2, raw_fit.explained_variance_ratio, width, label="raw normalized metrics")
    axes[0].bar(x + width / 2, boundary_fit.explained_variance_ratio, width, label="exact-boundary coordinates")
    axes[0].set_xticks(x, ["common mode", "contrast mode", "residual mode"])
    axes[0].set_ylim(0.0, 1.0)
    axes[0].set_ylabel("explained variance fraction")
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=0.2)

    load = boundary_fit.components[:2]
    positions = np.arange(3)
    axes[1].bar(positions - width / 2, load[0], width, label="common mode")
    axes[1].bar(positions + width / 2, load[1], width, label="contrast mode")
    axes[1].axhline(0.0, linewidth=0.8)
    axes[1].set_xticks(positions, [r"$q=1$", r"$q=2$ class", r"$q=1/2$"])
    axes[1].set_ylabel("standardized loading")
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y", alpha=0.2)
    fig.suptitle("A dominant common metric mode survives exact-boundary normalization")
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def _save_pair_robustness_figure(table: pd.DataFrame, path: Path) -> list[str]:
    by_size = (
        table.groupby(["n", "metric_a", "metric_b"], as_index=False)
        .agg(raw_spearman=("raw_spearman", "mean"), boundary_spearman=("boundary_spearman", "mean"))
    )
    fig, ax = plt.subplots(figsize=(8.7, 5.0))
    for pair, subset in by_size.groupby(["metric_a", "metric_b"], sort=True):
        label = PAIR_LABELS[pair]
        subset = subset.sort_values("n")
        ax.plot(subset["n"], subset["boundary_spearman"], marker="o", label=f"{label}, boundary-relative")
        ax.plot(subset["n"], subset["raw_spearman"], linestyle="--", alpha=0.55, label=f"{label}, raw")
    ax.set_ylim(0.4, 1.02)
    ax.set_xticks(sorted(table["n"].unique()))
    ax.set_xlabel("system size n")
    ax.set_ylabel("mean within-trajectory Spearman correlation")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.set_title("Metric agreement persists across all six sizes, but is order dependent")
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def _save_geometry_figure(table: pd.DataFrame, path: Path) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.5), sharex=True)
    for pair, subset in table.groupby(["metric_a", "metric_b"], sort=True):
        label = PAIR_LABELS[pair]
        for mode, style in (("y", "-"), ("full", "--")):
            part = subset[subset["mode"] == mode].sort_values("n")
            axes[0].plot(part["n"], part["distance_spearman"], marker="o", linestyle=style, label=f"{label}, {mode}")
            axes[1].plot(part["n"], part["knn_overlap_mean"], marker="o", linestyle=style, label=f"{label}, {mode}")
    axes[0].set_ylabel("Spearman correlation of 120 pair distances")
    axes[0].set_ylim(0.45, 1.02)
    axes[1].set_ylabel("mean overlap of 3-nearest-neighbor sets")
    axes[1].set_ylim(0.15, 1.02)
    axes[1].axhline(3 / 15, linestyle=":", label="random overlap expectation")
    for ax in axes:
        ax.set_xlabel("system size n")
        ax.set_xticks(sorted(table["n"].unique()))
        ax.grid(alpha=0.2)
    axes[0].legend(frameon=False, fontsize=7, ncol=2)
    axes[1].legend(frameon=False, fontsize=7, ncol=2)
    fig.suptitle("Relational trajectory geometry is preserved across metric projections")
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def _matrix_for(summary: pd.DataFrame, fold: str, mode: str) -> pd.DataFrame:
    part = summary[(summary["fold"] == fold) & (summary["mode"] == mode)]
    return part.pivot(index="train_metric", columns="test_metric", values="accuracy").reindex(index=HALF_METRICS, columns=HALF_METRICS)


def _save_classification_figure(summary: pd.DataFrame, x_summary: pd.DataFrame, path: Path) -> list[str]:
    centroid = _matrix_for(summary, "centroid_leave_size", "full")
    stringent = _matrix_for(summary, "individual_double_holdout", "full")
    x_centroid = float(
        x_summary[
            (x_summary["fold"] == "centroid_leave_size")
            & (x_summary["mode"] == "path")
        ]["accuracy"].iloc[0]
    )
    x_stringent = float(
        x_summary[
            (x_summary["fold"] == "individual_double_holdout")
            & (x_summary["mode"] == "path")
        ]["accuracy"].iloc[0]
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.0))
    for ax, matrix, title, baseline in (
        (axes[0], centroid, "Model centroids\nleave one size out", x_centroid),
        (axes[1], stringent, "Individual paths\nheld-out size and condition", x_stringent),
    ):
        image = ax.imshow(matrix.to_numpy(), vmin=0.25, vmax=1.0, aspect="auto")
        ax.set_xticks(range(3), [r"test $q=1$", r"test $q=2$", r"test $q=1/2$"])
        ax.set_yticks(range(3), [r"train $q=1$", r"train $q=2$", r"train $q=1/2$"])
        for row in range(3):
            for column in range(3):
                ax.text(
                    column,
                    row,
                    f"{matrix.iloc[row, column]:.2f}",
                    ha="center",
                    va="center",
                )
        ax.set_title(
            f"{title}\n" + fr"$\lambda_{{max}}$-only baseline {baseline:.2f}",
            fontsize=10,
        )
    colorbar_axis = fig.add_axes([0.915, 0.18, 0.018, 0.57])
    fig.colorbar(
        image,
        cax=colorbar_axis,
        label="nearest-centroid accuracy",
    )
    fig.suptitle(
        "Model-level morphology generalizes better than unseen individual conditions",
        y=0.985,
    )
    fig.subplots_adjust(
        left=0.08,
        right=0.87,
        bottom=0.16,
        top=0.76,
        wspace=0.38,
    )
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def _save_majorization_figure(table: pd.DataFrame, path: Path) -> list[str]:
    cross = pd.crosstab(table["majorization_relation"], table["metric_event"])
    relation_order = [
        "forward_entanglement_increase",
        "forward_entanglement_decrease",
        "incomparable",
    ]
    event_order = ["consensus_increase", "consensus_decrease", "metric_competition", "stationary_all"]
    cross = cross.reindex(index=relation_order, columns=event_order, fill_value=0)
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    bottom = np.zeros(len(cross))
    for event in event_order:
        values = cross[event].to_numpy(dtype=float)
        ax.bar(np.arange(len(cross)), values, bottom=bottom, label=event.replace("_", " "))
        bottom += values
    ax.set_xticks(
        np.arange(len(cross)),
        ["majorization-compatible\nincrease", "majorization-compatible\ndecrease", "incomparable spectra"],
    )
    ax.set_ylabel("consecutive full-spectrum transitions")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", alpha=0.2)
    ax.set_title("All observed metric contradictions occur on majorization-incomparable transitions")
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def _save_common_paths_figure(enriched: pd.DataFrame, fit, path: Path, n_focus: int = 20) -> list[str]:
    values = enriched[list(fit.columns)].to_numpy(dtype=float)
    scores = fit.transform(values)
    work = enriched.copy()
    work["common_mode"] = scores[:, 0]
    fig, ax = plt.subplots(figsize=(7.5, 5.4))
    order = [model for model in MODEL_ORDER if model in set(work["model"])]
    for model in order:
        sub = work[(work["n"] == n_focus) & (work["model"] == model)]
        centroid = sub.groupby("step", as_index=False)[["half_lambda_max", "common_mode"]].mean(numeric_only=True)
        finite = np.isfinite(centroid["common_mode"])
        ax.plot(centroid.loc[finite, "half_lambda_max"], centroid.loc[finite, "common_mode"], linewidth=2.0, label=MODEL_LABELS.get(model, model))
    ax.set_xlabel(r"largest Schmidt value $\lambda_{\max}$")
    ax.set_ylabel("common metric mode (standardized score)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    ax.set_title(f"Model-centroid paths in the shared metric mode, n={n_focus}")
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def _save_fine_descriptor_figure(summary: pd.DataFrame, path: Path) -> list[str]:
    labels = [PAIR_LABELS[(row.metric_a, row.metric_b)] for row in summary.itertuples()]
    x = np.arange(len(summary))
    width = 0.21
    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    ax.bar(x - 1.5 * width, summary["full_arc_length_rank_spearman"], width, label="full-path arc-length rank")
    ax.bar(x - 0.5 * width, summary["vertical_total_variation_rank_spearman"], width, label="vertical-variation rank")
    ax.bar(x + 0.5 * width, summary["origin_closed_area_rank_spearman"], width, label="origin-closed area rank")
    ax.bar(x + 1.5 * width, summary["exact_turn_count_agreement"], width, label="exact turn-count agreement")
    ax.set_xticks(x, labels)
    ax.set_ylim(-0.05, 1.02)
    ax.set_ylabel("agreement across 96 trajectories")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.set_title("Coarse descriptors persist; exact local turning structure does not")
    pdf, png = save_figure(fig, path)
    plt.close(fig)
    return [str(pdf), str(png)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "trajectory_observations.csv",
    )
    parser.add_argument(
        "--spectra-dir",
        type=Path,
        default=ROOT / "outputs" / "rebuild" / "spectra",
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=ROOT / "outputs" / "metric_robustness" / "results",
    )
    parser.add_argument(
        "--figure-dir",
        type=Path,
        default=ROOT / "outputs" / "metric_robustness" / "figures",
    )
    parser.add_argument("--bootstrap", type=int, default=3000)
    parser.add_argument("--mantel-permutations", type=int, default=1000)
    args = parser.parse_args()
    args.input = args.input.resolve()
    args.spectra_dir = args.spectra_dir.resolve()
    args.result_dir = args.result_dir.resolve()
    args.figure_dir = args.figure_dir.resolve()
    args.result_dir.mkdir(parents=True, exist_ok=True)
    args.figure_dir.mkdir(parents=True, exist_ok=True)

    frame = read_trajectory_csv(args.input, canonical=True)
    enriched = add_exact_boundary_coordinates(frame)

    raw_fit = fit_common_metric_mode(frame, coordinate="raw")
    boundary_fit = fit_common_metric_mode(frame, coordinate="boundary")
    common_modes = {
        "raw": raw_fit.as_dict(),
        "boundary": boundary_fit.as_dict(),
        "boundary_cluster_bootstrap": _bootstrap_common_mode(
            enriched, boundary_fit, iterations=args.bootstrap, seed=20260819
        ),
    }
    write_json(args.result_dir / "common_metric_modes.json", common_modes)

    per_trajectory = pd.concat(
        [
            per_trajectory_common_mode_table(frame, coordinate="raw"),
            per_trajectory_common_mode_table(frame, coordinate="boundary"),
        ],
        ignore_index=True,
    )
    per_trajectory.to_csv(args.result_dir / "common_mode_per_trajectory.csv", index=False)

    values = enriched[list(boundary_fit.columns)].to_numpy(dtype=float)
    scores = boundary_fit.transform(values)
    score_columns = enriched[
        ["model", "n", "run_id", "regime", "initial_state", "step", "tau", "half_lambda_max"]
    ].copy()
    score_columns["common_mode"] = scores[:, 0]
    score_columns["contrast_mode"] = scores[:, 1]
    score_columns["residual_mode"] = scores[:, 2]
    score_columns.to_csv(args.result_dir / "common_mode_timeseries.csv", index=False)

    robustness = pairwise_metric_robustness(frame)
    robustness.to_csv(args.result_dir / "metric_pair_robustness.csv", index=False)
    robustness_summary = _bootstrap_pair_summary(
        robustness, iterations=args.bootstrap, seed=20260820
    )
    robustness_summary.to_csv(args.result_dir / "metric_pair_robustness_summary.csv", index=False)
    robustness.groupby(["n", "metric_a", "metric_b"], as_index=False).mean(numeric_only=True).to_csv(
        args.result_dir / "metric_pair_robustness_by_size.csv", index=False
    )
    robustness.groupby(["model", "metric_a", "metric_b"], as_index=False).mean(numeric_only=True).to_csv(
        args.result_dir / "metric_pair_robustness_by_model.csv", index=False
    )

    one_site = one_site_aggregate_robustness(frame)
    one_site.to_csv(args.result_dir / "one_site_aggregate_robustness.csv", index=False)
    one_site.groupby(["metric_a", "metric_b"], as_index=False).agg(
        spearman_mean=("spearman", "mean"), spearman_min=("spearman", "min")
    ).to_csv(args.result_dir / "one_site_aggregate_robustness_summary.csv", index=False)

    geometry_tables = []
    centroid_geometry_tables = []
    for mode in ("y", "full"):
        geometry_tables.append(
            trajectory_geometry_preservation(
                frame,
                coordinate="boundary",
                mode=mode,
                k=3,
                permutations=args.mantel_permutations,
                seed=20260821 + (0 if mode == "y" else 1),
            )
        )
        centroid_geometry_tables.append(
            model_centroid_geometry_preservation(
                frame, coordinate="boundary", mode=mode
            )
        )
    geometry = pd.concat(geometry_tables, ignore_index=True)
    geometry.to_csv(args.result_dir / "trajectory_geometry_preservation.csv", index=False)
    centroid_geometry = pd.concat(centroid_geometry_tables, ignore_index=True)
    centroid_geometry.to_csv(args.result_dir / "model_centroid_geometry_preservation.csv", index=False)

    # Reuse the already computed boundary coordinates; this keeps the complete
    # analysis comfortably fast while preserving the public classification API.
    class_summary, class_predictions, x_tables = _classification_runs(enriched, args.result_dir)
    class_summary.to_csv(args.result_dir / "classification_summary.csv", index=False)
    class_predictions.to_csv(args.result_dir / "classification_predictions.csv", index=False)
    x_tables.to_csv(args.result_dir / "lambda_max_classification_baselines.csv", index=False)
    x_summary = x_tables[x_tables["table"] == "summary"].copy()

    events = metric_direction_events(frame)
    events.to_csv(args.result_dir / "metric_direction_events.csv", index=False)
    event_summary = _event_summary(events)
    event_summary.to_csv(args.result_dir / "metric_direction_event_summary.csv", index=False)

    majorization = majorization_transition_audit(args.spectra_dir)
    majorization.to_csv(args.result_dir / "majorization_transition_audit.csv", index=False)
    sensitivity = majorization_tolerance_sensitivity(args.spectra_dir)
    sensitivity.to_csv(args.result_dir / "majorization_tolerance_sensitivity.csv", index=False)

    fine = _fine_descriptor_table(enriched)
    fine.to_csv(args.result_dir / "fine_trajectory_descriptors.csv", index=False)
    fine_summary = _fine_descriptor_summary(fine)
    fine_summary.to_csv(args.result_dir / "fine_descriptor_robustness_summary.csv", index=False)

    # Compact scientific summary used by documentation and future AI metadata.
    per_boundary = per_trajectory[per_trajectory["coordinate"] == "boundary"]
    geometry_y = geometry[geometry["mode"] == "y"]
    geometry_full = geometry[geometry["mode"] == "full"]
    canonical_majorization = sensitivity.loc[
        np.isclose(
            sensitivity["majorization_tolerance"],
            1e-10,
            rtol=0.0,
            atol=1e-20,
        )
    ].iloc[0]
    cross = pd.crosstab(majorization["majorization_relation"], majorization["metric_event"])

    def classification_block(fold: str, mode: str) -> dict:
        part = class_summary[(class_summary["fold"] == fold) & (class_summary["mode"] == mode)]
        diagonal = part[part["train_metric"] == part["test_metric"]]["accuracy"]
        off = part[part["train_metric"] != part["test_metric"]]["accuracy"]
        return {
            "same_metric_mean_accuracy": float(diagonal.mean()),
            "cross_metric_mean_accuracy": float(off.mean()),
            "minimum_accuracy": float(part["accuracy"].min()),
            "maximum_accuracy": float(part["accuracy"].max()),
            "predictions_per_matrix_cell": int(part["predictions"].iloc[0]),
        }

    summary = {
        "scope": {
            "trajectory_rows": int(len(frame)),
            "trajectories": int(frame.groupby(["model", "n", "run_id"]).ngroups),
            "model_families": int(frame["model"].nunique()),
            "conditions_per_model": 4,
            "sizes": sorted(int(x) for x in frame["n"].unique()),
            "selected_full_spectrum_runs": int(majorization["run_id"].nunique()),
            "selected_full_spectrum_transitions": int(len(majorization)),
        },
        "common_mode": {
            "raw_pc1_explained": float(raw_fit.explained_variance_ratio[0]),
            "boundary_pc1_explained": float(boundary_fit.explained_variance_ratio[0]),
            "boundary_pc2_explained": float(boundary_fit.explained_variance_ratio[1]),
            "boundary_pc1_loadings": [float(x) for x in boundary_fit.components[0]],
            "boundary_pc2_loadings": [float(x) for x in boundary_fit.components[1]],
            "boundary_pc1_cluster_bootstrap_ci95": common_modes["boundary_cluster_bootstrap"]["pc1_explained_ci95"],
            "per_trajectory_pc1_median": float(per_boundary["pc1_explained"].median()),
            "per_trajectory_pc1_iqr": [
                float(per_boundary["pc1_explained"].quantile(0.25)),
                float(per_boundary["pc1_explained"].quantile(0.75)),
            ],
            "per_trajectory_pc1_minimum": float(per_boundary["pc1_explained"].min()),
            "finite_boundary_rows": int(boundary_fit.finite_rows),
            "total_rows": int(boundary_fit.total_rows),
        },
        "within_trajectory_metric_robustness": robustness_summary.to_dict(orient="records"),
        "trajectory_space_geometry": {
            "y_only_mean_spearman_by_pair": geometry_y.groupby(["metric_a", "metric_b"])["distance_spearman"].mean().reset_index().to_dict(orient="records"),
            "y_only_min_spearman_by_pair": geometry_y.groupby(["metric_a", "metric_b"])["distance_spearman"].min().reset_index().to_dict(orient="records"),
            "y_only_mean_knn_overlap_by_pair": geometry_y.groupby(["metric_a", "metric_b"])["knn_overlap_mean"].mean().reset_index().to_dict(orient="records"),
            "full_path_mean_spearman_by_pair": geometry_full.groupby(["metric_a", "metric_b"])["distance_spearman"].mean().reset_index().to_dict(orient="records"),
            "random_knn_overlap": float(3 / 15),
            "all_y_only_mantel_pvalues_at_most": float(geometry_y["mantel_pvalue_one_sided"].max()),
            "full_path_caveat": "Full-path correlations include the common lambda_max coordinate; y-only results are the nontrivial test of metric-coordinate preservation.",
        },
        "classification_stress_tests": {
            "chance_accuracy": 0.25,
            "centroid_leave_size_full": classification_block("centroid_leave_size", "full"),
            "centroid_leave_size_vertical": classification_block("centroid_leave_size", "y"),
            "individual_leave_size_full": classification_block("individual_leave_size", "full"),
            "individual_leave_size_vertical": classification_block("individual_leave_size", "y"),
            "individual_double_holdout_full": classification_block("individual_double_holdout", "full"),
            "individual_double_holdout_vertical": classification_block("individual_double_holdout", "y"),
            "lambda_max_path_baselines": x_summary[["fold", "mode", "accuracy", "predictions"]].to_dict(orient="records"),
            "interpretation": "Model-centroid morphology generalizes better than unseen individual conditions; the individual fingerprint claim remains preliminary.",
        },
        "metric_direction_events": {
            "overall_counts": {str(k): int(v) for k, v in events["event_class"].value_counts().items()},
            "overall_fractions": {str(k): float(v) for k, v in events["event_class"].value_counts(normalize=True).items()},
            "competition_fraction_by_model": {
                str(model): float(np.mean(group["event_class"] == "metric_competition"))
                for model, group in events.groupby("model", sort=True)
            },
        },
        "majorization_selected_spectra": {
            "canonical_tolerance": 1e-10,
            "forward_entanglement_increase": int(canonical_majorization["forward_entanglement_increase"]),
            "forward_entanglement_decrease": int(canonical_majorization["forward_entanglement_decrease"]),
            "incomparable": int(canonical_majorization["incomparable"]),
            "metric_competition": int(canonical_majorization["metric_competition"]),
            "competition_outside_incomparable": int(canonical_majorization["competition_outside_incomparable"]),
            "incomparable_consensus_transitions": int(
                cross.loc["incomparable"].get("consensus_increase", 0)
                + cross.loc["incomparable"].get("consensus_decrease", 0)
                + cross.loc["incomparable"].get("stationary_all", 0)
            ),
        },
        "fine_structure_limit": {
            "all_three_exact_turn_count_agreement_fraction": fine_summary.attrs["all_three_turn_count_agreement"],
            "all_three_exact_turn_count_agreement_count": fine_summary.attrs["all_three_turn_count_agreement_count"],
            "trajectories": fine_summary.attrs["trajectories"],
            "pair_summary": fine_summary.to_dict(orient="records"),
        },
        "recommended_claim": "Across four tested dynamical families used to probe scrambling, recurrence, disorder, and spectral complexity, three non-equivalent Schmidt-spectrum metric classes share a dominant common trajectory mode and preserve substantial relational morphology after exact-boundary normalization. The preservation is hierarchical rather than exact, and local metric contradictions occur on majorization-incomparable spectral steps. This supports an empirical metric-robust trajectory class, not a formal topological invariant or a universal individual-run fingerprint.",
    }
    write_json(args.result_dir / "metric_robustness_scientific_summary.json", summary)

    figure_files = []
    figure_files += _save_common_mode_figure(
        raw_fit, boundary_fit, args.figure_dir / "figure_01_common_metric_modes.pdf"
    )
    figure_files += _save_pair_robustness_figure(
        robustness, args.figure_dir / "figure_02_metric_robustness_across_sizes.pdf"
    )
    figure_files += _save_geometry_figure(
        geometry, args.figure_dir / "figure_03_relational_geometry_preservation.pdf"
    )
    figure_files += _save_classification_figure(
        class_summary, x_summary, args.figure_dir / "figure_04_generalization_limits.pdf"
    )
    figure_files += _save_majorization_figure(
        majorization, args.figure_dir / "figure_05_majorization_and_metric_competition.pdf"
    )
    figure_files += _save_common_paths_figure(
        enriched, boundary_fit, args.figure_dir / "figure_06_common_mode_model_paths_n20.pdf"
    )
    figure_files += _save_fine_descriptor_figure(
        fine_summary, args.figure_dir / "figure_07_coarse_vs_fine_stability.pdf"
    )

    figure_manifest = {
        "generated_by": "analysis/analyze_metric_robustness.py",
        "input": str(args.input.relative_to(ROOT)),
        "spectra_directory": str(args.spectra_dir.relative_to(ROOT)),
        "figures": [str(Path(path).relative_to(ROOT)) for path in figure_files],
        "figure_records": [
            {
                "figure_id": stem,
                **FIGURE_METADATA[stem],
                "pdf": str((args.figure_dir / f"{stem}.pdf").relative_to(ROOT)),
                "png": str((args.figure_dir / f"{stem}.png").relative_to(ROOT)),
            }
            for stem in FIGURE_METADATA
        ],
        "source_tables": [
            str(path.relative_to(ROOT))
            for path in sorted(args.result_dir.glob("*.csv"))
        ],
        "interpretation": summary["recommended_claim"],
    }
    write_json(args.figure_dir / "metric_robustness_figure_manifest.json", figure_manifest)
    print(args.result_dir)
    print(args.figure_dir)


if __name__ == "__main__":
    main()
