#!/usr/bin/env python3
"""Run and summarize the XXZ product-formula convergence study.

The study keeps the model parameters, disorder seeds, initial-state seeds, record
interval, and observation grid fixed while changing only the number of symmetric
product-formula substeps per record interval.

Default scope: n=10,12,14; runs XXZ_1,...,XXZ_4; substeps 1,2,4,8,16,32.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from entanglement_trajectories.dynamics import (  # noqa: E402
    build_evolver,
    half_chain_spectrum,
    initialize_state,
)
from entanglement_trajectories.models import ModelRun, run_by_id  # noqa: E402
from entanglement_trajectories.robustness import (  # noqa: E402
    fit_common_metric_mode,
    metric_direction_events,
)
from entanglement_trajectories.simulation import metrics_from_spectrum  # noqa: E402

METRICS = (
    "half_vn",
    "half_linear",
    "half_logneg",
    "half_geometric_linear",
    "half_lambda_max",
    "half_min_entropy",
)


def parse_int_list(value: str) -> tuple[int, ...]:
    items = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not items or any(item <= 0 for item in items):
        raise argparse.ArgumentTypeError("expected a comma-separated list of positive integers")
    return items


def parse_str_list(value: str) -> tuple[str, ...]:
    items = tuple(part.strip() for part in value.split(",") if part.strip())
    if not items:
        raise argparse.ArgumentTypeError("expected a nonempty comma-separated list")
    return items


def refined_run(run_id: str, substeps: int) -> ModelRun:
    base = run_by_id(run_id)
    if base.model != "random_field_xxz":
        raise ValueError(f"{run_id!r} is not an XXZ run")
    parameters = dict(base.parameters)
    parameters["trotter_substeps"] = int(substeps)
    return ModelRun(
        base.model,
        base.run_id,
        base.regime,
        base.initial_state,
        parameters,
        base.description,
    )


def simulate_half_metrics(n: int, run_id: str, substeps: int) -> pd.DataFrame:
    run = refined_run(run_id, substeps)
    psi = initialize_state(run, int(n))
    evolver = build_evolver(run, int(n))
    rows: list[dict] = []
    for step in range(4 * int(n) + 1):
        spectrum = half_chain_spectrum(psi, int(n))
        rows.append(
            {
                "n": int(n),
                "run_id": run_id,
                "regime": run.regime,
                "initial_state": run.initial_state,
                "step": int(step),
                "tau": float(step / n),
                "trotter_substeps": int(substeps),
                **metrics_from_spectrum(spectrum),
            }
        )
        if step < 4 * int(n):
            evolver.step(psi)
    return pd.DataFrame(rows)


def pairwise_comparisons(frame: pd.DataFrame, substeps: tuple[int, ...]) -> pd.DataFrame:
    rows: list[dict] = []
    adjacent = list(zip(substeps[:-1], substeps[1:]))
    extra = []
    if 4 in substeps and 16 in substeps:
        extra.append((4, 16))
    if 8 in substeps and 32 in substeps:
        extra.append((8, 32))
    for (n, run_id), group in frame.groupby(["n", "run_id"], sort=True):
        by = {
            m: group[group.trotter_substeps == m].sort_values("step").reset_index(drop=True)
            for m in substeps
        }
        for a, b in adjacent + extra:
            row = {"n": int(n), "run_id": str(run_id), "substeps_a": int(a), "substeps_b": int(b)}
            for metric in METRICS:
                delta = by[a][metric].to_numpy(dtype=float) - by[b][metric].to_numpy(dtype=float)
                row[f"max_abs_{metric}"] = float(np.max(np.abs(delta)))
                row[f"rms_{metric}"] = float(np.sqrt(np.mean(delta**2)))
                row[f"endpoint_abs_{metric}"] = float(abs(delta[-1]))
            row["max_abs_over_metrics"] = max(row[f"max_abs_{metric}"] for metric in METRICS)
            row["rms_over_metrics"] = max(row[f"rms_{metric}"] for metric in METRICS)
            rows.append(row)
    return pd.DataFrame(rows)


def convergence_orders(comparisons: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    required = ((2, 4), (4, 8), (8, 16), (16, 32))
    for (n, run_id), group in comparisons.groupby(["n", "run_id"], sort=True):
        by = {(int(row.substeps_a), int(row.substeps_b)): row for _, row in group.iterrows()}
        if any(pair not in by for pair in required):
            continue
        for metric in METRICS:
            errors = [by[pair][f"rms_{metric}"] for pair in required]
            rows.append(
                {
                    "n": int(n),
                    "run_id": str(run_id),
                    "metric": metric,
                    "rms_2_4": errors[0],
                    "rms_4_8": errors[1],
                    "rms_8_16": errors[2],
                    "rms_16_32": errors[3],
                    "p_24_48": math.log(errors[0] / errors[1], 2.0),
                    "p_48_816": math.log(errors[1] / errors[2], 2.0),
                    "p_816_1632": math.log(errors[2] / errors[3], 2.0),
                }
            )
    return pd.DataFrame(rows)


def competition_table(frame: pd.DataFrame, *, eps: float = 1e-10) -> pd.DataFrame:
    rows: list[dict] = []
    metric_columns = ["half_vn", "half_linear", "half_logneg"]
    for (n, run_id, substeps), group in frame.groupby(
        ["n", "run_id", "trotter_substeps"], sort=True
    ):
        values = group.sort_values("step")[metric_columns].to_numpy(dtype=float)
        delta = np.diff(values, axis=0)
        signs = np.where(delta > eps, 1, np.where(delta < -eps, -1, 0))
        events = []
        for sign_row in signs:
            nonzero = sign_row[sign_row != 0]
            events.append(len(set(nonzero.tolist())) > 1)
        rows.append(
            {
                "n": int(n),
                "run_id": str(run_id),
                "trotter_substeps": int(substeps),
                "transitions": int(len(events)),
                "competition_count": int(sum(events)),
                "competition_fraction": float(np.mean(events)),
            }
        )
    return pd.DataFrame(rows)


def core_claim_sensitivity(frame: pd.DataFrame, canonical_path: Path) -> pd.DataFrame:
    if not canonical_path.is_file():
        return pd.DataFrame()
    canonical = pd.read_csv(canonical_path)
    rows: list[dict] = []
    for substeps in sorted(frame.trotter_substeps.unique()):
        work = canonical.copy()
        replacement = frame[frame.trotter_substeps == substeps]
        for _, row in replacement.iterrows():
            mask = (
                (work.model == "random_field_xxz")
                & (work.n == row.n)
                & (work.run_id == row.run_id)
                & (work.step == row.step)
            )
            for column in METRICS:
                work.loc[mask, column] = row[column]
        global_fit = fit_common_metric_mode(work, coordinate="boundary")
        global_events = metric_direction_events(work)
        xxz = work[(work.model == "random_field_xxz") & work.n.isin(sorted(frame.n.unique()))]
        xxz_fit = fit_common_metric_mode(xxz, coordinate="boundary")
        xxz_events = metric_direction_events(xxz)
        rows.append(
            {
                "substeps": int(substeps),
                "global_pc1_fraction": float(global_fit.explained_variance_ratio[0]),
                "global_competition_fraction": float(
                    (global_events.event_class == "metric_competition").mean()
                ),
                "global_competition_count": int(
                    (global_events.event_class == "metric_competition").sum()
                ),
                "xxz_scope_pc1_fraction": float(xxz_fit.explained_variance_ratio[0]),
                "xxz_scope_competition_fraction": float(
                    (xxz_events.event_class == "metric_competition").mean()
                ),
                "xxz_scope_competition_count": int(
                    (xxz_events.event_class == "metric_competition").sum()
                ),
            }
        )
    return pd.DataFrame(rows)


def build_summary(
    frame: pd.DataFrame,
    comparisons: pd.DataFrame,
    orders: pd.DataFrame,
    effect: pd.DataFrame,
) -> dict:
    summary = {
        "study": "XXZ product-formula refinement at fixed seeds and dt_record=0.25",
        "sizes": sorted(int(x) for x in frame.n.unique()),
        "run_ids": sorted(str(x) for x in frame.run_id.unique()),
        "substeps": sorted(int(x) for x in frame.trotter_substeps.unique()),
        "trajectory_rows": int(len(frame)),
        "recorded_trajectories": int(
            frame.groupby(["n", "run_id", "trotter_substeps"]).ngroups
        ),
        "metrics": list(METRICS),
        "pairwise_refinement": {},
        "observed_order_median": {},
        "core_claim_sensitivity": effect.to_dict(orient="records"),
    }
    for a, b in ((1, 2), (2, 4), (4, 8), (8, 16), (16, 32)):
        selected = comparisons[
            (comparisons.substeps_a == a) & (comparisons.substeps_b == b)
        ]
        if selected.empty:
            continue
        worst = selected.loc[selected.max_abs_over_metrics.idxmax()]
        summary["pairwise_refinement"][f"{a}_vs_{b}"] = {
            "overall_max_abs": float(selected.max_abs_over_metrics.max()),
            "overall_max_rms": float(selected.rms_over_metrics.max()),
            "worst_case": {
                "n": int(worst.n),
                "run_id": str(worst.run_id),
                "value": float(worst.max_abs_over_metrics),
            },
            "max_abs_by_metric": {
                metric: float(selected[f"max_abs_{metric}"].max()) for metric in METRICS
            },
        }
    if not orders.empty:
        for metric, group in orders.groupby("metric"):
            summary["observed_order_median"][str(metric)] = {
                "2_to_4_vs_4_to_8": float(group.p_24_48.median()),
                "4_to_8_vs_8_to_16": float(group.p_48_816.median()),
                "8_to_16_vs_16_to_32": float(group.p_816_1632.median()),
            }
    summary["decision"] = {
        "one_substep_converged": False,
        "convergence_control_reference": (
            "16 substeps checked against 32 for n=10,12,14"
        ),
        "recommended_current_dataset_interpretation": (
            "fixed one-substep symmetric product-formula circuit; "
            "not converged Hamiltonian dynamics"
        ),
    }
    return summary


def make_figures(
    frame: pd.DataFrame,
    comparisons: pd.DataFrame,
    effect: pd.DataFrame,
    outdir: Path,
) -> None:
    import matplotlib.pyplot as plt

    outdir.mkdir(parents=True, exist_ok=True)
    pairs = [(1, 2), (2, 4), (4, 8), (8, 16), (16, 32)]
    x: list[int] = []
    max_error: list[float] = []
    rms_error: list[float] = []
    for a, b in pairs:
        selected = comparisons[
            (comparisons.substeps_a == a) & (comparisons.substeps_b == b)
        ]
        if selected.empty:
            continue
        x.append(a)
        max_error.append(float(selected.max_abs_over_metrics.max()))
        rms_error.append(float(selected.rms_over_metrics.max()))
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.loglog(x, max_error, "o-", label="worst maximum absolute difference")
    ax.loglog(x, rms_error, "s-", label="worst RMS difference")
    if len(x) >= 2:
        reference = max_error[1] * (np.asarray(x, dtype=float) / x[1]) ** -2
        ax.loglog(x, reference, "--", label="second-order reference")
    ax.set_xlabel("product-formula substeps $m$")
    ax.set_ylabel("difference between $m$ and $2m$")
    ax.set_title("XXZ product-formula refinement is asymptotically second order")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "xxz_refinement_error.png", dpi=220)
    plt.close(fig)

    if 14 in set(frame.n.unique()) and {1, 4, 8, 16, 32} <= set(frame.trotter_substeps.unique()):
        selected = frame[(frame.n == 14) & (frame.run_id == "XXZ_4")]
        if not selected.empty:
            fig, ax = plt.subplots(figsize=(7.0, 5.2))
            for m in (1, 4, 8, 16, 32):
                part = selected[selected.trotter_substeps == m].sort_values("step")
                if part.empty:
                    continue
                ax.plot(
                    part.half_lambda_max,
                    part.half_vn,
                    marker="o",
                    markevery=8,
                    ms=3,
                    lw=1.5,
                    label=f"$m={m}$",
                )
            ax.set_xlabel("largest Schmidt value $\\lambda_{\\max}$")
            ax.set_ylabel("normalized von Neumann entropy")
            ax.set_title(
                "$n=14$, XXZ_4: the one-substep circuit is not the converged trajectory"
            )
            ax.grid(True, alpha=0.25)
            ax.legend(ncol=2)
            fig.tight_layout()
            fig.savefig(outdir / "xxz4_n14_trajectory_refinement.png", dpi=220)
            plt.close(fig)

    if not effect.empty:
        fig, ax = plt.subplots(figsize=(7.0, 4.6))
        ax.semilogx(
            effect.substeps,
            effect.global_pc1_fraction,
            "o-",
            base=2,
            label="global common-mode fraction",
        )
        ax.semilogx(
            effect.substeps,
            effect.xxz_scope_pc1_fraction,
            "s-",
            base=2,
            label="XXZ-scope common-mode fraction",
        )
        ax.set_xlabel("product-formula substeps $m$")
        ax.set_ylabel("first common-mode variance fraction")
        ax.set_title("The multi-metric common mode survives XXZ refinement")
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(outdir / "xxz_refinement_common_mode.png", dpi=220)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=parse_int_list, default=(10, 12, 14))
    parser.add_argument(
        "--run-ids",
        type=parse_str_list,
        default=("XXZ_1", "XXZ_2", "XXZ_3", "XXZ_4"),
    )
    parser.add_argument("--substeps", type=parse_int_list, default=(1, 2, 4, 8, 16, 32))
    parser.add_argument(
        "--outdir",
        type=Path,
        default=ROOT / "outputs" / "xxz_convergence",
    )
    parser.add_argument(
        "--canonical-data",
        type=Path,
        default=ROOT / "data" / "trajectory_observations.csv",
    )
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    for n in args.sizes:
        for run_id in args.run_ids:
            for substeps in args.substeps:
                started = time.time()
                part = simulate_half_metrics(n, run_id, substeps)
                frames.append(part)
                print(
                    f"n={n} run={run_id} substeps={substeps}: "
                    f"{len(part)} observations in {time.time()-started:.2f}s",
                    flush=True,
                )
    frame = pd.concat(frames, ignore_index=True)
    comparisons = pairwise_comparisons(frame, args.substeps)
    orders = convergence_orders(comparisons)
    competition = competition_table(frame)
    effect = core_claim_sensitivity(frame, args.canonical_data)
    summary = build_summary(frame, comparisons, orders, effect)

    frame.to_csv(args.outdir / "xxz_convergence_trajectories.csv", index=False)
    comparisons.to_csv(args.outdir / "xxz_convergence_comparisons.csv", index=False)
    orders.to_csv(args.outdir / "xxz_convergence_orders.csv", index=False)
    competition.to_csv(args.outdir / "xxz_competition_by_substeps.csv", index=False)
    if not effect.empty:
        effect.to_csv(args.outdir / "xxz_refinement_effect_on_core_claim.csv", index=False)
    (args.outdir / "xxz_convergence_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    make_figures(frame, comparisons, effect, args.outdir / "figures")
    print(f"Wrote convergence study to {args.outdir}")


if __name__ == "__main__":
    main()
