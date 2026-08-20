#!/usr/bin/env python3
"""Rebuild the selected n=20 Schmidt-spectrum diagnostics.

The five NPZ trajectories are historical, hand-selected spectrum reruns from
GPT-5.5.  This script keeps those spectra unchanged, replaces the erroneous
numerically integrated balanced Marchenko-Pastur CDF with its analytic form,
uses the checkpoint-03 canonical metric layer, separates full-spectrum and
bulk adjacent-gap ratios, and produces one unambiguous current result set.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans"})

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from entanglement_trajectories.models import run_by_id, MODEL_LABELS
from entanglement_trajectories.plotting import linestyle, save_figure
from entanglement_trajectories.rmt import (
    GAP_RATIO_REFERENCE_MEANS,
    add_reference_columns_to_frame,
    haar_reference_targets,
    marchenko_pastur_cdf_balanced,
    marchenko_pastur_pdf_balanced,
    mp_ks_distance_from_spectrum,
    spectrum_summary,
)
from entanglement_trajectories.simulation import metrics_from_spectrum


def _model_label(model: str) -> str:
    return MODEL_LABELS.get(model, model.replace("_", " "))


def _write_csv(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.17g")
    return path


@lru_cache(maxsize=4)
def _legacy_mp_cdf_grid(num_grid: int = 20000) -> tuple[np.ndarray, np.ndarray]:
    """Reproduce the historical singular-grid integration bug for diagnosis only."""
    eps = 1e-10
    x = np.linspace(eps, 4.0, int(num_grid), dtype=np.float64)
    y = np.asarray(marchenko_pastur_pdf_balanced(x), dtype=float)
    dx = np.diff(x)
    area = np.concatenate([[0.0], np.cumsum(0.5 * (y[:-1] + y[1:]) * dx)])
    if area[-1] > 0.0:
        area /= area[-1]
    return x, area


def legacy_mp_cdf_balanced(x: np.ndarray) -> np.ndarray:
    values = np.asarray(x, dtype=float)
    grid_x, grid_cdf = _legacy_mp_cdf_grid()
    out = np.interp(values, grid_x, grid_cdf, left=0.0, right=1.0)
    out = np.where(values >= 4.0, 1.0, out)
    out = np.where(values <= 0.0, 0.0, out)
    return out


def legacy_mp_ks_distance(lam: np.ndarray) -> float:
    values = np.asarray(lam, dtype=float)
    values = values[np.isfinite(values)]
    values = np.clip(values, 0.0, None)
    values /= float(values.sum())
    x = np.sort(values.size * values)
    cdf = legacy_mp_cdf_balanced(x)
    count = x.size
    empirical_hi = np.arange(1, count + 1, dtype=float) / count
    empirical_lo = np.arange(0, count, dtype=float) / count
    return float(np.max(np.maximum(np.abs(empirical_hi - cdf), np.abs(empirical_lo - cdf))))


def load_and_analyze(
    spectra_dir: Path,
    copied_spectra_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    copied_spectra_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    bug_rows: list[dict] = []
    selection: list[dict] = []

    paths = sorted(spectra_dir.glob("*.npz"))
    if not paths:
        raise FileNotFoundError(f"No NPZ spectra found in {spectra_dir}")

    for source in paths:
        with np.load(source, allow_pickle=False) as data:
            spectra = np.asarray(data["spectra"], dtype=float)
            steps = np.asarray(data["steps"], dtype=int)
            n = int(np.asarray(data["n"]).ravel()[0])
            model = str(np.asarray(data["model"]).ravel()[0])
            run_id = str(np.asarray(data["run_id"]).ravel()[0])
            source_regime = str(np.asarray(data["regime"]).ravel()[0])
            initial_state = str(np.asarray(data["initial_state"]).ravel()[0])
        if spectra.ndim != 2 or spectra.shape[0] != steps.size:
            raise ValueError(f"Malformed spectra archive: {source}")
        run = run_by_id(run_id)
        if run.model != model:
            raise ValueError(f"Archive model/run mismatch in {source}")
        target = haar_reference_targets(n)

        copied = copied_spectra_dir / source.name
        if source.resolve() != copied.resolve():
            shutil.copy2(source, copied)
        selection.append(
            {
                "model": model,
                "run_id": run_id,
                "n": n,
                "source_regime": source_regime,
                "canonical_regime": run.regime,
                "initial_state": initial_state,
                "num_saved_spectra": int(spectra.shape[0]),
                "schmidt_dimension": int(spectra.shape[1]),
                "source_file": str(source),
                "current_file": str(copied),
                "selection_status": "historical hand-selected spectrum rerun",
            }
        )

        for step, spectrum in zip(steps, spectra):
            spectrum = np.clip(np.asarray(spectrum, dtype=float), 0.0, None)
            spectrum /= float(spectrum.sum())
            row = {
                "model": model,
                "n": n,
                "run_id": run_id,
                "regime": run.regime,
                "source_regime": source_regime,
                "initial_state": initial_state,
                "step": int(step),
                "tau": float(step / n),
                **metrics_from_spectrum(spectrum),
                **spectrum_summary(spectrum),
            }
            rows.append(row)
            current_ks = float(row["mp_ks_distance"])
            old_ks = legacy_mp_ks_distance(spectrum)
            bug_rows.append(
                {
                    "model": model,
                    "n": n,
                    "run_id": run_id,
                    "step": int(step),
                    "tau": float(step / n),
                    "mp_ks_analytic_current": current_ks,
                    "mp_ks_legacy_singular_grid": old_ks,
                    "legacy_minus_current": old_ks - current_ks,
                    "absolute_difference": abs(old_ks - current_ks),
                }
            )

    frame = pd.DataFrame(rows).sort_values(["model", "run_id", "step"]).reset_index(drop=True)
    enriched, targets = add_reference_columns_to_frame(frame)
    bug_frame = pd.DataFrame(bug_rows).sort_values(["model", "run_id", "step"]).reset_index(drop=True)
    registry = {
        "scope": "five historical hand-selected n=20 spectrum reruns",
        "selection_is_representative_sample": False,
        "selected_runs": selection,
        "models_present": sorted({item["model"] for item in selection}),
        "models_absent": sorted(set(MODEL_LABELS) - {item["model"] for item in selection}),
        "important_limitation": (
            "The saved spectra omit the quantum-baker family and most runs. "
            "They support selected-run diagnostics, not model-wide universality claims."
        ),
        "reference_targets": [record for record in targets.to_dict(orient="records")],
    }
    return enriched, bug_frame, registry


def endpoint_and_best(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    endpoints = []
    best = []
    for (model, run_id), group in frame.groupby(["model", "run_id"], sort=True):
        group = group.sort_values("step")
        endpoints.append(group.iloc[-1].to_dict())
        idx = group["reference_distance_4metric"].astype(float).idxmin()
        best.append(group.loc[idx].to_dict())
    return pd.DataFrame(endpoints), pd.DataFrame(best)


def figure_diagnostics(frame: pd.DataFrame, outdir: Path, n: int) -> list[Path]:
    sub = frame[frame["n"] == n]
    fig, axes = plt.subplots(3, 1, figsize=(9.2, 9.1), sharex=True)
    for (model, run_id), group in sub.groupby(["model", "run_id"], sort=True):
        group = group.sort_values("step")
        label = f"{_model_label(model)} / {run_id}"
        ls = linestyle(group["initial_state"].iloc[0])
        axes[0].plot(group["tau"], group["reference_distance_4metric"], linewidth=1.4, linestyle=ls, label=label)
        axes[1].plot(group["tau"], group["mp_ks_distance"], linewidth=1.4, linestyle=ls, label=label)
        axes[2].plot(group["tau"], group["ent_gap_ratio_bulk_mean"], linewidth=1.4, linestyle=ls, label=label)
    axes[0].set_ylabel("four-coordinate\nreference distance")
    axes[1].set_ylabel("analytic MP KS distance")
    axes[2].set_ylabel(r"bulk mean adjacent ratio $\langle r\rangle$")
    axes[2].set_xlabel(r"$\tau=t/n$")
    for ax in axes:
        ax.grid(True, alpha=0.25, linewidth=0.6)
    for name, value in GAP_RATIO_REFERENCE_MEANS.items():
        axes[2].axhline(value, linewidth=0.75, linestyle=":", alpha=0.78, label=name.replace("_large_n_fit", "").upper())
    axes[0].legend(fontsize=6.4, framealpha=0.88)
    axes[2].legend(fontsize=6.1, framealpha=0.88, ncol=4)
    fig.suptitle(
        f"Selected Schmidt-spectrum reference diagnostics, n={n}\n"
        "gap-ratio lines are comparison values, not automatic symmetry-class assignments"
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    pdf, png = save_figure(fig, outdir / f"figure_spectrum_01_diagnostics_n{n}.pdf")
    plt.close(fig)
    return [pdf, png]


def _load_final_spectra(spectra_dir: Path) -> list[tuple[str, str, np.ndarray]]:
    rows = []
    for path in sorted(spectra_dir.glob("*.npz")):
        with np.load(path, allow_pickle=False) as data:
            model = str(np.asarray(data["model"]).ravel()[0])
            run_id = str(np.asarray(data["run_id"]).ravel()[0])
            spectra = np.asarray(data["spectra"], dtype=float)
        spectrum = np.clip(spectra[-1], 0.0, None)
        spectrum /= float(spectrum.sum())
        rows.append((model, run_id, spectrum))
    return rows


def figure_final_density(spectra_dir: Path, outdir: Path, n: int) -> list[Path]:
    spectra = _load_final_spectra(spectra_dir)
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.8), sharex=True)
    xgrid = np.linspace(1e-5, 5.0, 1200)
    bins = np.linspace(0.0, 5.0, 121)
    for ax in axes:
        ax.plot(xgrid, marchenko_pastur_pdf_balanced(xgrid), linewidth=2.0, label="balanced MP density")
        for model, run_id, lam in spectra:
            ax.hist(
                lam.size * lam,
                bins=bins,
                density=True,
                histtype="step",
                linewidth=1.1,
                label=f"{_model_label(model)} / {run_id}",
            )
        ax.set_xlim(0.0, 5.0)
        ax.set_xlabel(r"scaled eigenvalue $x=d\lambda$")
        ax.grid(True, alpha=0.25, linewidth=0.6)
    axes[0].set_yscale("log")
    axes[0].set_ylim(1e-2, 2e2)
    axes[0].set_ylabel("density (log scale)")
    axes[0].set_title("Full one-point density view")
    axes[1].set_xlim(0.05, 5.0)
    axes[1].set_ylim(0.0, 3.0)
    axes[1].set_ylabel("density")
    axes[1].set_title("Bulk and upper-edge view")
    axes[1].legend(fontsize=6.2, framealpha=0.88)
    fig.suptitle(f"Endpoint one-point spectra versus balanced MP density, n={n}")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    pdf, png = save_figure(fig, outdir / f"figure_spectrum_02_endpoint_mp_density_n{n}.pdf")
    plt.close(fig)
    return [pdf, png]


def figure_final_cdf(spectra_dir: Path, outdir: Path, n: int) -> list[Path]:
    spectra = _load_final_spectra(spectra_dir)
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 7.0), sharex=True, sharey=True)
    xgrid = np.linspace(0.0, 8.0, 1200)
    for ax, (model, run_id, lam) in zip(axes.ravel(), spectra):
        x = np.sort(lam.size * lam)
        empirical = np.arange(1, x.size + 1, dtype=float) / x.size
        ax.step(x, empirical, where="post", linewidth=1.2, label="empirical CDF")
        ax.plot(xgrid, marchenko_pastur_cdf_balanced(xgrid), linewidth=1.7, label="analytic MP CDF")
        ks = mp_ks_distance_from_spectrum(lam)
        ax.set_xlim(0.0, 8.0)
        ax.set_title(
            f"{_model_label(model)} / {run_id}\nKS={ks:.3f}, max x={np.max(x):.1f}",
            fontsize=9,
        )
        ax.grid(True, alpha=0.25, linewidth=0.6)
    axes.ravel()[-1].axis("off")
    for row in range(2):
        axes[row, 0].set_ylabel("CDF")
    for ax in axes[-1, :2]:
        ax.set_xlabel(r"$x=d\lambda$ (display truncated at 8)")
    axes[0, 0].legend(fontsize=7.0, framealpha=0.88)
    fig.suptitle(f"Endpoint empirical CDF versus analytic balanced MP law, n={n}")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    pdf, png = save_figure(fig, outdir / f"figure_spectrum_03_endpoint_mp_cdf_n{n}.pdf")
    plt.close(fig)
    return [pdf, png]


def figure_endpoint_scorecard(endpoint: pd.DataFrame, outdir: Path, n: int) -> list[Path]:
    sub = endpoint[endpoint["n"] == n].copy()
    sub["label"] = [f"{_model_label(m)} / {r}" for m, r in zip(sub["model"], sub["run_id"])]
    metrics = [
        ("reference_distance_4metric", "four-coordinate reference distance", True),
        ("mp_ks_distance", "analytic MP KS distance", True),
        ("lambda_max_scaled", r"scaled largest eigenvalue $d\lambda_{\max}$", True),
        ("ent_gap_ratio_bulk_mean", r"bulk mean adjacent ratio $\langle r\rangle$", False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.0))
    for ax, (column, title, ascending) in zip(axes.ravel(), metrics):
        view = sub.sort_values(column, ascending=ascending).reset_index(drop=True)
        y = np.arange(len(view))
        ax.barh(y, view[column])
        ax.set_yticks(y)
        ax.set_yticklabels(view["label"], fontsize=7.3)
        ax.invert_yaxis()
        ax.set_title(title, fontsize=10)
        ax.grid(True, axis="x", alpha=0.25, linewidth=0.6)
        if column == "lambda_max_scaled":
            ax.set_xscale("log")
            ax.set_xlim(3.0, 1000.0)
            ax.axvline(4.0, linewidth=0.8, linestyle=":", label="MP upper edge 4")
            ax.legend(fontsize=7.0)
        if column == "ent_gap_ratio_bulk_mean":
            for name, value in GAP_RATIO_REFERENCE_MEANS.items():
                ax.axvline(value, linewidth=0.65, linestyle=":", alpha=0.75, label=name.replace("_large_n_fit", "").upper())
            ax.legend(fontsize=6.3, ncol=2)
    fig.suptitle(
        f"Endpoint scorecard for the five selected spectrum reruns, n={n}\n"
        "the diagnostics probe different spectral properties and need not agree"
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    pdf, png = save_figure(fig, outdir / f"figure_spectrum_04_endpoint_scorecard_n{n}.pdf")
    plt.close(fig)
    return [pdf, png]


def write_readme(outdir: Path, registry: dict, generated: list[Path]) -> Path:
    absent = ", ".join(registry["models_absent"]) or "none"
    text = f"""# Selected Schmidt-spectrum diagnostics

This directory contains the single current diagnostic set reconstructed from
the five full-spectrum NPZ trajectories saved by the GPT-5.5 follow-up study.

## Corrections applied

- The balanced Marchenko-Pastur CDF is evaluated analytically, rather than by a
  uniform trapezoidal grid across its integrable singularity at zero.
- Exact finite-Haar means and asymptotic MP proxies are labeled separately.
- Full-spectrum and interior-window entanglement-Hamiltonian adjacent-gap ratios
  are reported separately.
- Poisson, GOE, GUE, and GSE mean-ratio values are plotted only as descriptive
  references; no symmetry class is assigned automatically.
- Historical `corrected`/`uncorrected` duplicates are replaced by one current
  output set.  The old numerical bug is retained only in an audit comparison.

## Selection limitation

The available spectra are hand-selected runs, not a balanced model sample.
Models absent from this spectrum subset: **{absent}**.  The results therefore
support selected-run spectral comparisons, not universal claims across all four
families.

## Generated files

""" + "\n".join(f"- `{path.name}`" for path in generated) + "\n"
    path = outdir / "README.md"
    path.write_text(text, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-spectra-dir", type=Path, required=True)
    parser.add_argument("--copied-spectra-dir", type=Path, required=True)
    parser.add_argument("--data-outdir", type=Path, required=True)
    parser.add_argument("--analysis-outdir", type=Path, required=True)
    parser.add_argument("--figure-outdir", type=Path, required=True)
    parser.add_argument("--compare-corrected-csv", type=Path, default=None)
    args = parser.parse_args()

    args.data_outdir.mkdir(parents=True, exist_ok=True)
    args.analysis_outdir.mkdir(parents=True, exist_ok=True)
    args.figure_outdir.mkdir(parents=True, exist_ok=True)

    frame, bug_frame, registry = load_and_analyze(
        args.input_spectra_dir, args.copied_spectra_dir
    )
    endpoint, best = endpoint_and_best(frame)
    n_values = sorted(int(value) for value in frame["n"].unique())
    if len(n_values) != 1:
        raise ValueError(f"Expected one saved-spectrum size, found {n_values}")
    n = n_values[0]

    outputs = [
        _write_csv(frame, args.data_outdir / "spectrum_diagnostics_selected_n20.csv"),
        _write_csv(endpoint, args.data_outdir / "spectrum_endpoint_summary_selected_n20.csv"),
        _write_csv(best, args.data_outdir / "spectrum_best_reference_match_selected_n20.csv"),
        _write_csv(bug_frame, args.analysis_outdir / "mp_cdf_bug_comparison.csv"),
    ]
    registry_path = args.data_outdir / "selected_spectrum_registry.json"
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    outputs.append(registry_path)

    comparison = {
        "comparison_file_supplied": bool(args.compare_corrected_csv),
        "current_rows": int(len(frame)),
        "max_legacy_mp_ks_absolute_error": float(bug_frame["absolute_difference"].max()),
        "mean_legacy_mp_ks_absolute_error": float(bug_frame["absolute_difference"].mean()),
    }
    if args.compare_corrected_csv is not None:
        old = pd.read_csv(args.compare_corrected_csv)
        keys = ["model", "n", "run_id", "step"]
        merged = frame.merge(old, on=keys, suffixes=("_current", "_historical"), how="inner")
        comparison["historical_corrected_rows"] = int(len(old))
        comparison["matched_rows"] = int(len(merged))
        if "mp_ks_distance_current" in merged and "mp_ks_distance_historical" in merged:
            comparison["max_current_vs_historical_corrected_mp_ks_difference"] = float(
                np.max(np.abs(merged["mp_ks_distance_current"] - merged["mp_ks_distance_historical"]))
            )
    comparison_path = args.analysis_outdir / "spectrum_rebuild_comparison.json"
    comparison_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    outputs.append(comparison_path)

    figures: list[Path] = []
    figures.extend(figure_diagnostics(frame, args.figure_outdir, n))
    figures.extend(figure_final_density(args.copied_spectra_dir, args.figure_outdir, n))
    figures.extend(figure_final_cdf(args.copied_spectra_dir, args.figure_outdir, n))
    figures.extend(figure_endpoint_scorecard(endpoint, args.figure_outdir, n))
    readme = write_readme(args.figure_outdir, registry, figures)
    outputs.extend(figures)
    outputs.append(readme)

    manifest = {
        "source_spectra": str(args.input_spectra_dir),
        "current_spectra": str(args.copied_spectra_dir),
        "n": n,
        "num_runs": int(frame["run_id"].nunique()),
        "num_spectra": int(len(frame)),
        "mp_cdf": "analytic balanced MP CDF",
        "gap_ratio_policy": "full and x in [0.05,3.95] bulk-window values reported separately",
        "automatic_symmetry_class_assignment": False,
        "generated_files": [str(path) for path in outputs],
    }
    manifest_path = args.figure_outdir / "spectrum_diagnostics_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
