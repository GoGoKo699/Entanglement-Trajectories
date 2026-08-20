#!/usr/bin/env python3
"""Build the public-facing figure sequence for the corrected repository.

The script uses only included data and the canonical exact-boundary layer.
It writes PNG/PDF figures and the compact source tables used by each panel.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from entanglement_trajectories.boundaries import metric_bounds_fixed_lmax  # noqa: E402
from entanglement_trajectories.metrics import metric_value  # noqa: E402

import tempfile
import zipfile

OUT = ROOT / "outputs" / "public_figures"
DATA = OUT / "data"
OUT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
_INPUT_TEMP = tempfile.TemporaryDirectory(prefix="entanglement_public_inputs_")
INPUT_ROOT = Path(_INPUT_TEMP.name)
with zipfile.ZipFile(ROOT / "data" / "public_analysis_inputs.zip") as _zf:
    _zf.extractall(INPUT_ROOT)

# Cold palette with a restrained warm contrast for competition/limitations.
NAVY = "#24557A"
BLUE = "#3D7EA6"
CYAN = "#55AFC9"
INDIGO = "#6D6BB5"
VIOLET = "#8A6BBE"
SLATE = "#627484"
PALE = "#DCEAF2"
PALE2 = "#EEF4F7"
AMBER = "#D58A36"
CORAL = "#C96555"
GREEN = "#4F8B72"
DARK = "#25313A"
GREY = "#8D99A3"
LIGHT_GREY = "#D7DEE3"

MODEL_COLORS = {
    "qca": NAVY,
    "kicked_ising": CYAN,
    "quantum_baker": INDIGO,
    "random_field_xxz": CORAL,
}
MODEL_LABELS = {
    "qca": "Brickwork Floquet QCA",
    "kicked_ising": "Open-chain kicked Ising",
    "quantum_baker": "Balazs-Voros-style quantum baker",
    "random_field_xxz": "Random-field XXZ (Trotterized)",
}
METRIC_LABELS = {
    "half_vn": r"$q=1$",
    "half_linear": r"$q=2$ class",
    "half_logneg": r"$q=1/2$",
}
PAIR_COLORS = {
    ("half_vn", "half_logneg"): NAVY,
    ("half_vn", "half_linear"): INDIGO,
    ("half_linear", "half_logneg"): CYAN,
}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12.5,
            "axes.labelsize": 11.5,
            "legend.fontsize": 9.5,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linewidth": 0.7,
            "figure.dpi": 160,
            "savefig.dpi": 220,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save(fig: plt.Figure, stem: str, *, png_dpi: int = 220) -> None:
    fig.savefig(OUT / f"{stem}.png", bbox_inches="tight", dpi=png_dpi, facecolor="white")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _box(ax, xy, width, height, text, *, facecolor=PALE2, edgecolor=NAVY, fontsize=12, lw=1.5):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize, color=DARK)
    return patch


def _arrow(ax, start, end, *, color=SLATE, lw=1.6, mutation=13):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=mutation,
            linewidth=lw,
            color=color,
            connectionstyle="arc3,rad=0.0",
        )
    )


def build_figure_01() -> None:
    """One spectrum path, several nonlinear lenses."""
    fig, ax = plt.subplots(figsize=(14, 6.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.965, "One Schmidt-spectrum path, several entanglement lenses", ha="center", va="top", fontsize=22, weight="bold", color=DARK)
    ax.text(
        0.5,
        0.915,
        "Unification means a common latent object - not compulsory agreement of every scalar metric.",
        ha="center",
        va="top",
        fontsize=12.5,
        color=SLATE,
    )

    _box(
        ax,
        (0.035, 0.49),
        0.22,
        0.22,
        "Schmidt-spectrum path\n" + r"$\Gamma:t\mapsto\boldsymbol{\lambda}(t)$",
        facecolor=PALE,
        edgecolor=NAVY,
        fontsize=14.5,
    )
    ax.text(0.145, 0.445, "ordered reduced-density-matrix eigenvalues", ha="center", fontsize=10.1, color=SLATE)

    metrics = [
        (0.305, 0.69, "tail-sensitive\n" + r"$H_{1/2}$ / log-negativity", CYAN),
        (0.305, 0.49, "bulk-weighted\n" + r"$H_1$ / von Neumann", NAVY),
        (0.305, 0.29, "head-weighted\n" + r"$H_2$ / purity class", INDIGO),
        (0.305, 0.09, "spectral head\n" + r"$H_\infty$ / $\lambda_{\max}$", VIOLET),
    ]
    for x, y, text, color in metrics:
        _box(ax, (x, y), 0.235, 0.13, text, facecolor="white", edgecolor=color, fontsize=11.2, lw=1.8)
        _arrow(ax, (0.255, 0.60), (x, y + 0.065), color=color, lw=1.45)

    _box(
        ax,
        (0.595, 0.405),
        0.15,
        0.24,
        "trajectory atlas\n" + r"$\Gamma_E,\ E\in\mathcal{F}$",
        facecolor="white",
        edgecolor=SLATE,
        fontsize=13.2,
        lw=1.8,
    )
    for _, y, _, color in metrics:
        _arrow(ax, (0.54, y + 0.065), (0.595, 0.525), color=color, lw=1.2, mutation=10)

    _box(
        ax,
        (0.79, 0.59),
        0.18,
        0.18,
        "shared coarse morphology\nmetric-robust trajectory class",
        facecolor=PALE,
        edgecolor=NAVY,
        fontsize=12.3,
    )
    _box(
        ax,
        (0.79, 0.25),
        0.18,
        0.18,
        "local metric competition\ninternal spectral redistribution",
        facecolor="#F9EEE8",
        edgecolor=CORAL,
        fontsize=12.3,
    )
    _arrow(ax, (0.745, 0.525), (0.79, 0.68), color=NAVY, lw=1.55, mutation=12)
    _arrow(ax, (0.745, 0.525), (0.79, 0.34), color=CORAL, lw=1.55, mutation=12)

    ax.text(0.88, 0.52, "majorization identifies where\nSchur-concave metrics must agree", ha="center", va="center", fontsize=9.7, color=SLATE)
    ax.text(0.88, 0.19, "incomparable spectra leave room\nfor valid contradictions", ha="center", va="center", fontsize=9.7, color=SLATE)

    ax.text(
        0.5,
        0.025,
        "Exact layer: fixed-$\\lambda_{\\max}$ feasible envelopes   |   Empirical layer: robustness across four chaos families and six sizes",
        ha="center",
        va="bottom",
        fontsize=11,
        color=DARK,
    )
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    _save(fig, "figure_01_one_spectrum_many_lenses")

    concept = {
        "primary_object": "ordered Schmidt-spectrum path Gamma: t -> lambda(t)",
        "metric_lenses": ["Renyi-1/2 / pure-state logarithmic negativity", "Renyi-1 / von Neumann entropy", "Renyi-2 class / purity and linear entropy", "Renyi-infinity / largest Schmidt value"],
        "unifying_outputs": ["shared coarse morphology", "informative local metric competition"],
        "exact_mechanism": "majorization-compatible transitions impose consensus for Schur-concave metrics",
        "scope": "fixed-cut bipartite pure-state dynamics",
    }
    (DATA / "figure_01_concept.json").write_text(json.dumps(concept, indent=2) + "\n", encoding="utf-8")


def build_social_preview() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=100)
    fig.patch.set_facecolor("#F7FAFC")
    ax.set_facecolor("#F7FAFC")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.055, 0.86, "ENTANGLEMENT TRAJECTORIES", fontsize=27, weight="bold", color=DARK, va="top")
    ax.text(0.055, 0.75, "One Schmidt-spectrum path. Many entanglement metrics.", fontsize=17, color=NAVY, va="top")
    ax.text(0.055, 0.665, "Shared morphology, meaningful disagreement.", fontsize=15.5, color=SLATE, va="top")

    _box(ax, (0.055, 0.25), 0.24, 0.22, r"$\boldsymbol{\lambda}(t)$" + "\nSchmidt-spectrum path", facecolor=PALE, edgecolor=NAVY, fontsize=16.5)
    lens_y = [0.51, 0.37, 0.23]
    lens_text = [r"$H_{1/2}$", r"$H_1$", r"$H_2$"]
    lens_colors = [CYAN, NAVY, INDIGO]
    for y, text, color in zip(lens_y, lens_text, lens_colors):
        _box(ax, (0.37, y), 0.105, 0.095, text, facecolor="white", edgecolor=color, fontsize=16)
        _arrow(ax, (0.295, 0.36), (0.37, y + 0.047), color=color, lw=1.5)

    _box(ax, (0.53, 0.32), 0.12, 0.18, "trajectory\natlas", facecolor="white", edgecolor=SLATE, fontsize=15.5)
    for y, color in zip(lens_y, lens_colors):
        _arrow(ax, (0.475, y + 0.047), (0.53, 0.41), color=color, lw=1.35)

    _box(ax, (0.72, 0.45), 0.23, 0.15, "metric-robust\ntrajectory class", facecolor=PALE, edgecolor=NAVY, fontsize=16)
    _box(ax, (0.72, 0.18), 0.23, 0.15, "majorization-aware\nmetric competition", facecolor="#F9EEE8", edgecolor=CORAL, fontsize=16)
    _arrow(ax, (0.65, 0.41), (0.72, 0.525), color=NAVY, lw=1.6)
    _arrow(ax, (0.65, 0.41), (0.72, 0.255), color=CORAL, lw=1.6)

    ax.text(0.055, 0.09, "Corrected companion to Quantum 8, 1282 (2024)  |  DOI 10.22331/q-2024-03-14-1282", fontsize=11.5, color=SLATE)
    fig.subplots_adjust(0, 0, 1, 1)
    out = OUT / "social_preview.png"
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor(), bbox_inches=None, pad_inches=0)
    plt.close(fig)


def build_figure_02() -> None:
    """Exact metric arenas using normalized min entropy as shared x coordinate."""
    d = 1024
    x = np.linspace(0.0, 1.0, 1401)
    p = np.exp(-x * np.log(d))
    specs = [
        ("von_neumann_entropy", "half_vn", r"von Neumann entropy $H_1$"),
        ("linear_entropy", "half_linear", r"linear entropy / $H_2$ class"),
        ("log_negativity_pure", "half_logneg", r"pure-state log-negativity $H_{1/2}$"),
    ]
    df = pd.read_csv(INPUT_ROOT / "reference_enriched_timeseries.csv")
    df = df[df["n"] == 20].copy()

    fig, axes = plt.subplots(1, 3, figsize=(15.2, 4.8), sharex=True, sharey=True)
    boundary_rows = []
    for ax, (metric_id, col, title) in zip(axes, specs):
        bounds = metric_bounds_fixed_lmax(metric_id, p, d, normalized=True)
        lo = np.asarray(bounds.lower)
        hi = np.asarray(bounds.upper)
        ax.fill_between(x, lo, hi, color=PALE, alpha=0.95, label="exact feasible region")
        ax.plot(x, lo, color=NAVY, lw=1.8, label="concentrated-spectrum edge")
        ax.plot(x, hi, color=INDIGO, lw=1.8, label="equal-tail edge")
        ax.scatter(df["half_min_entropy"], df[col], s=8, color=AMBER, alpha=0.18, edgecolors="none", rasterized=True, label="included $n=20$ observations")
        ax.set_title(title)
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.015, 1.015)
        ax.set_xlabel(r"normalized min-entropy $H_\infty/\log d$")
        for xi, pi, l, h in zip(x, p, lo, hi):
            boundary_rows.append({"metric_id": metric_id, "h_inf_normalized": xi, "lambda_max": pi, "lower": l, "upper": h})
    axes[0].set_ylabel("normalized metric value")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Exact fixed-$\\lambda_{\\max}$ arenas place different metrics on a common spectral stage ($n=20$, $d=1024$)", fontsize=17, y=1.03, color=DARK)
    fig.tight_layout(rect=(0, 0.08, 1, 0.98))
    _save(fig, "figure_02_exact_metric_arenas")

    pd.DataFrame(boundary_rows).to_csv(DATA / "figure_02_exact_metric_arenas_boundaries.csv", index=False)
    df[["model", "n", "run_id", "step", "tau", "half_min_entropy", "half_vn", "half_linear", "half_logneg", "half_lambda_max"]].to_csv(
        DATA / "figure_02_exact_metric_arenas_points_n20.csv", index=False
    )


def build_figure_03() -> None:
    """Dominant common mode, size robustness, and coarse/fine hierarchy."""
    res = INPUT_ROOT
    modes = json.loads((res / "common_metric_modes.json").read_text(encoding="utf-8"))
    by_size = pd.read_csv(res / "metric_pair_robustness_by_size.csv")
    fine = pd.read_csv(res / "fine_descriptor_robustness_summary.csv")

    fig, axes = plt.subplots(1, 3, figsize=(16.0, 4.7))

    # A: explained variance.
    ax = axes[0]
    vals = np.asarray(modes["boundary"]["explained_variance_ratio"])
    labels = ["common", "contrast", "residual"]
    colors = [NAVY, AMBER, LIGHT_GREY]
    bars = ax.bar(labels, vals, color=colors, width=0.68)
    ci = modes["boundary_cluster_bootstrap"]["pc1_explained_ci95"]
    ax.errorbar([0], [vals[0]], yerr=[[vals[0] - ci[0]], [ci[1] - vals[0]]], fmt="none", ecolor=DARK, capsize=5, lw=1.5)
    for bar, value in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{100*value:.1f}%", ha="center", va="bottom", fontsize=10.5)
    ax.set_ylim(0, 1.03)
    ax.set_ylabel("explained variance fraction")
    ax.set_title("A. One dominant normalized mode")
    ax.text(
        0.98,
        0.96,
        f"common-mode cluster-bootstrap 95% CI:\n{100*ci[0]:.1f}%–{100*ci[1]:.1f}%",
        transform=ax.transAxes,
        fontsize=8.8,
        color=SLATE,
        va="top",
        ha="right",
    )

    # B: correlations across size.
    ax = axes[1]
    pair_order = [("half_vn", "half_logneg"), ("half_vn", "half_linear"), ("half_linear", "half_logneg")]
    for pair in pair_order:
        sub = by_size[(by_size["metric_a"] == pair[0]) & (by_size["metric_b"] == pair[1])]
        if sub.empty:
            sub = by_size[(by_size["metric_a"] == pair[1]) & (by_size["metric_b"] == pair[0])]
        label = f"{METRIC_LABELS[pair[0]]} vs {METRIC_LABELS[pair[1]]}"
        ax.plot(sub["n"], sub["boundary_spearman"], marker="o", lw=2.0, ms=5.5, color=PAIR_COLORS[pair], label=label)
    ax.set_ylim(0.55, 1.01)
    ax.set_xticks(sorted(by_size["n"].unique()))
    ax.set_xlabel("system size $n$")
    ax.set_ylabel("mean within-trajectory Spearman $\\rho$")
    ax.set_title("B. Agreement persists across size")
    ax.legend(frameon=False, loc="lower left")

    # C: coarse vs fine descriptors.
    ax = axes[2]
    pair_labels = []
    xloc = np.arange(len(fine))
    width = 0.24
    ax.bar(xloc - width, fine["arc_length_rank_spearman"], width, label="arc-length rank", color=NAVY)
    ax.bar(xloc, fine["signed_area_rank_spearman"], width, label="signed-area rank", color=INDIGO)
    ax.bar(xloc + width, fine["exact_turn_count_agreement"], width, label="exact turn-count agreement", color=AMBER)
    for _, row in fine.iterrows():
        pair_labels.append(f"{METRIC_LABELS[row['metric_a']]}\nvs\n{METRIC_LABELS[row['metric_b']]}")
    ax.set_xticks(xloc, pair_labels)
    ax.set_ylim(0, 1.03)
    ax.set_ylabel("cross-metric agreement")
    ax.set_title("C. Coarse structure survives; fine structure need not")
    ax.legend(frameon=False, loc="upper right", fontsize=8.7)

    fig.suptitle("Metric robustness is strong but hierarchical - not exact invariance", fontsize=17, y=1.03, color=DARK)
    fig.tight_layout()
    _save(fig, "figure_03_metric_robustness_hierarchy")

    pd.DataFrame(
        {
            "mode": labels,
            "explained_variance_fraction": vals,
            "pc1_ci_low": [ci[0], np.nan, np.nan],
            "pc1_ci_high": [ci[1], np.nan, np.nan],
        }
    ).to_csv(DATA / "figure_03_common_mode.csv", index=False)
    by_size.to_csv(DATA / "figure_03_metric_pair_robustness_by_size.csv", index=False)
    fine.to_csv(DATA / "figure_03_coarse_fine_stability.csv", index=False)


def build_figure_04() -> None:
    """Toy contradiction plus empirical majorization and competition rates."""
    res = INPUT_ROOT
    audit = pd.read_csv(res / "majorization_transition_audit.csv")
    summary = json.loads((INPUT_ROOT / "metric_robustness_scientific_summary.json").read_text(encoding="utf-8"))

    xspec = np.array([0.8, 0.1, 0.1, 0.0])
    yspec = np.array([0.7, 0.3, 0.0, 0.0])
    toy_metrics = [
        ("von_neumann_entropy", r"$H_1$"),
        ("renyi_two", r"$H_2$"),
        ("renyi_half", r"$H_{1/2}$"),
        ("min_entropy", r"$H_\infty$"),
    ]
    toy_rows = []
    for metric_id, label in toy_metrics:
        xv = metric_value(metric_id, xspec, normalized=False, base=math.e)
        yv = metric_value(metric_id, yspec, normalized=False, base=math.e)
        toy_rows.append({"metric_id": metric_id, "label": label, "x_value": xv, "y_value": yv, "more_entangled": "x" if xv > yv else "y" if yv > xv else "tie"})
    toy_df = pd.DataFrame(toy_rows)

    fig, axes = plt.subplots(1, 3, figsize=(16.3, 4.8))

    # A: incomparable spectra and metric reversals.
    ax = axes[0]
    idx = np.arange(4)
    width = 0.36
    ax.bar(idx - width / 2, xspec, width, label=r"$\boldsymbol{x}=(0.8,0.1,0.1,0)$", color=NAVY)
    ax.bar(idx + width / 2, yspec, width, label=r"$\boldsymbol{y}=(0.7,0.3,0,0)$", color=AMBER)
    ax.set_xticks(idx, [r"$\lambda_1$", r"$\lambda_2$", r"$\lambda_3$", r"$\lambda_4$"])
    ax.set_ylim(0, 0.92)
    ax.set_ylabel("Schmidt weight")
    ax.set_title("A. Incomparable spectra can reverse metric order")
    ax.legend(frameon=False, fontsize=8.6, loc="upper right")
    order_text = "\n".join([f"{row.label}: {row.more_entangled} is larger" for row in toy_df.itertuples()])
    ax.text(0.02, 0.51, order_text, transform=ax.transAxes, fontsize=9.2, va="top", ha="left", bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=LIGHT_GREY, alpha=0.95))

    # B: empirical majorization audit.
    ax = axes[1]
    ct = pd.crosstab(audit["majorization_relation"], audit["metric_event"])
    relation_order = ["forward_entanglement_increase", "forward_entanglement_decrease", "incomparable"]
    event_order = ["consensus_increase", "consensus_decrease", "metric_competition"]
    rel_labels = ["compatible\nincrease", "compatible\ndecrease", "incomparable"]
    event_colors = {"consensus_increase": NAVY, "consensus_decrease": CYAN, "metric_competition": CORAL}
    bottom = np.zeros(len(relation_order))
    rows = []
    for event in event_order:
        values = []
        for rel in relation_order:
            total = ct.loc[rel].sum() if rel in ct.index else 0
            count = int(ct.loc[rel, event]) if rel in ct.index and event in ct.columns else 0
            frac = count / total if total else 0.0
            values.append(frac)
            rows.append({"majorization_relation": rel, "metric_event": event, "count": count, "fraction_within_relation": frac})
        ax.bar(rel_labels, values, bottom=bottom, color=event_colors[event], label=event.replace("_", " "))
        bottom += np.asarray(values)
    ax.set_ylim(0, 1.03)
    ax.set_ylabel("fraction of selected transitions")
    ax.set_title("B. Competition appears only in the incomparable sector")
    ax.legend(frameon=False, fontsize=8.4, loc="upper left")

    # C: model dependence.
    ax = axes[2]
    model_frac = summary["metric_direction_events"]["competition_fraction_by_model"]
    models = ["qca", "kicked_ising", "quantum_baker", "random_field_xxz"]
    vals = [model_frac[m] for m in models]
    bars = ax.bar(["QCA", "kicked\nIsing", "quantum\nbaker", "random-field\nXXZ"], vals, color=[MODEL_COLORS[m] for m in models])
    for bar, value in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.009, f"{100*value:.1f}%", ha="center", va="bottom", fontsize=9.5)
    ax.set_ylim(0, 0.29)
    ax.set_ylabel("fraction of all scalar steps")
    ax.set_title("C. Metric competition is dynamics dependent")

    fig.suptitle("The trajectory atlas explains both consensus and contradiction", fontsize=17, y=1.03, color=DARK)
    fig.tight_layout()
    _save(fig, "figure_04_majorization_and_metric_competition")

    toy_df.to_csv(DATA / "figure_04_incomparable_spectra_metric_values.csv", index=False)
    pd.DataFrame(rows).to_csv(DATA / "figure_04_majorization_event_fractions.csv", index=False)
    pd.DataFrame({"model": models, "metric_competition_fraction": vals}).to_csv(DATA / "figure_04_competition_by_model.csv", index=False)


def build_figure_05() -> None:
    """Model-centroid morphology and generalization limits."""
    res = INPUT_ROOT
    common = pd.read_csv(res / "common_mode_timeseries.csv")
    summary = json.loads((INPUT_ROOT / "metric_robustness_scientific_summary.json").read_text(encoding="utf-8"))

    cent = common[common["n"] == 20].groupby(["model", "step"], as_index=False).agg(
        half_lambda_max=("half_lambda_max", "mean"),
        common_mode=("common_mode", "mean"),
        tau=("tau", "mean"),
    )

    fig, axes = plt.subplots(1, 2, figsize=(15.0, 5.2), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    for model in ["qca", "kicked_ising", "quantum_baker", "random_field_xxz"]:
        sub = cent[cent["model"] == model].dropna(subset=["common_mode"]).sort_values("step")
        ax.plot(sub["half_lambda_max"], sub["common_mode"], lw=2.25, color=MODEL_COLORS[model], label=MODEL_LABELS[model])
        if not sub.empty:
            ax.scatter(sub.iloc[0]["half_lambda_max"], sub.iloc[0]["common_mode"], s=32, color=MODEL_COLORS[model], marker="o", zorder=4)
            ax.scatter(sub.iloc[-1]["half_lambda_max"], sub.iloc[-1]["common_mode"], s=42, color=MODEL_COLORS[model], marker="s", zorder=4)
    ax.set_xlabel(r"largest Schmidt value $\lambda_{\max}$")
    ax.set_ylabel("shared metric-mode score")
    ax.set_title("A. Model-centroid paths remain morphologically distinct")
    ax.legend(frameon=False, fontsize=9.1, loc="upper right")
    ax.text(0.02, 0.02, "circle: first finite point   square: endpoint", transform=ax.transAxes, fontsize=8.7, color=SLATE)

    ax = axes[1]
    cls = summary["classification_stress_tests"]
    values = [
        cls["centroid_leave_size_full"]["same_metric_mean_accuracy"],
        cls["centroid_leave_size_full"]["cross_metric_mean_accuracy"],
        cls["individual_leave_size_full"]["same_metric_mean_accuracy"],
        cls["individual_double_holdout_full"]["same_metric_mean_accuracy"],
        [x["accuracy"] for x in cls["lambda_max_path_baselines"] if x["fold"] == "individual_double_holdout" and x["mode"] == "path"][0],
    ]
    labels = ["model centroid\nsame metric", "model centroid\ncross metric", "individual path\nheld-out size", "individual path\ndouble holdout", r"$\lambda_{\max}$ path\ndouble holdout"]
    colors = [NAVY, CYAN, INDIGO, CORAL, GREY]
    bars = ax.bar(np.arange(len(values)), values, color=colors)
    ax.axhline(cls["chance_accuracy"], color=DARK, linestyle="--", lw=1.2, label="chance")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.022, f"{value:.3f}", ha="center", va="bottom", fontsize=9.5)
    ax.set_xticks(np.arange(len(values)), labels, rotation=15, ha="right")
    ax.set_ylim(0, 1.03)
    ax.set_ylabel("nearest-centroid model accuracy")
    ax.set_title("B. Model-level morphology is stronger than individual fingerprinting")
    ax.legend(frameon=False, loc="upper right")

    fig.suptitle("Trajectory morphology carries model information, with explicit generalization limits", fontsize=17, y=1.03, color=DARK)
    fig.tight_layout()
    _save(fig, "figure_05_model_morphology_and_limits")

    cent.to_csv(DATA / "figure_05_common_mode_model_centroids_n20.csv", index=False)
    pd.DataFrame({"test": labels, "accuracy": values, "chance": cls["chance_accuracy"]}).to_csv(DATA / "figure_05_classification_summary.csv", index=False)


def copy_supplemental() -> None:
    supplemental = OUT / "supplemental"
    supplemental.mkdir(exist_ok=True)
    copies = [
        ROOT / "figures" / "spectrum_reference" / "figure_spectrum_04_endpoint_scorecard_n20.png",
        ROOT / "figures" / "spectrum_reference" / "figure_spectrum_04_endpoint_scorecard_n20.pdf",
        ROOT / "figures" / "rmt_reference" / "figure_reference_01_distance_n20.png",
        ROOT / "figures" / "rmt_reference" / "figure_reference_01_distance_n20.pdf",
    ]
    for source in copies:
        if source.exists():
            target = supplemental / source.name
            target.write_bytes(source.read_bytes())


def main() -> None:
    _style()
    build_figure_01()
    build_social_preview()
    build_figure_02()
    build_figure_03()
    build_figure_04()
    build_figure_05()
    print(f"Wrote public figures to {OUT}")


if __name__ == "__main__":
    main()
