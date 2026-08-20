#!/usr/bin/env python3
"""Regenerate n=10 trajectories and compare them with the GPT-5.5 table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from entanglement_trajectories.simulation import simulate_frame, write_simulation


def compare(current: pd.DataFrame, legacy: pd.DataFrame) -> dict:
    legacy = legacy[legacy["n"] == 10].copy()
    order = ["n", "model", "run_id", "step"]
    current = current.sort_values(order).reset_index(drop=True)
    legacy = legacy.sort_values(order).reset_index(drop=True)
    if len(current) != len(legacy):
        raise AssertionError(f"Row-count mismatch: {len(current)} versus {len(legacy)}")

    metadata = {}
    for column in ["model", "n", "run_id", "regime", "initial_state", "step"]:
        metadata[column] = bool(current[column].astype(str).equals(legacy[column].astype(str)))
    metadata["tau_max_abs_difference"] = float(
        np.max(np.abs(current["tau"].to_numpy(float) - legacy["tau"].to_numpy(float)))
    )

    columns = [
        "one_site_mean_vn",
        "one_site_mean_linear",
        "one_site_mean_logneg",
        "one_site_mean_geometric_linear",
        "half_vn",
        "half_linear",
        "half_logneg",
        "half_geometric_linear",
    ]
    differences = {}
    for column in columns:
        delta = np.abs(current[column].to_numpy(float) - legacy[column].to_numpy(float))
        differences[column] = {
            "max_abs_difference": float(np.max(delta)),
            "mean_abs_difference": float(np.mean(delta)),
        }
    pass_flags = {
        "metadata": all(value for key, value in metadata.items() if key != "tau_max_abs_difference")
        and metadata["tau_max_abs_difference"] <= 2e-15,
        "non_logneg_metrics": all(
            differences[column]["max_abs_difference"] <= 5e-13
            for column in columns
            if "logneg" not in column
        ),
        "logneg_metrics": all(
            differences[column]["max_abs_difference"] <= 7e-9
            for column in columns
            if "logneg" in column
        ),
    }
    return {
        "scope": "all 16 runs at n=10, 41 recorded points per run",
        "rows": int(len(current)),
        "metadata": metadata,
        "metric_differences": differences,
        "pass_flags": pass_flags,
        "passed": bool(all(pass_flags.values())),
        "logneg_note": (
            "H_1/2 is unusually sensitive to tiny numerical tail eigenvalues near product states; "
            "the independent implementations agree within 7e-9."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--current-output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    current = simulate_frame(system_sizes=[10], verbose=True)
    write_simulation(current, args.current_output)
    report = compare(current, pd.read_csv(args.reference))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["passed"]:
        raise SystemExit("n=10 regression failed")
    print(args.report)


if __name__ == "__main__":
    main()
