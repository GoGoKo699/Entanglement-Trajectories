#!/usr/bin/env python3
"""Run deterministic trajectory simulations under the current schema."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from entanglement_trajectories.models import MODEL_ORDER
from entanglement_trajectories.simulation import DEFAULT_SYSTEM_SIZES, simulate_frame, write_simulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/trajectory_observations.csv"))
    parser.add_argument("--sizes", nargs="*", type=int, default=list(DEFAULT_SYSTEM_SIZES))
    parser.add_argument("--models", nargs="*", default=list(MODEL_ORDER))
    parser.add_argument("--run-ids", nargs="*", default=None)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--measure-every", type=int, default=1)
    parser.add_argument("--legacy-schema", action="store_true")
    args = parser.parse_args()

    frame = simulate_frame(
        system_sizes=args.sizes,
        models=args.models,
        run_ids=args.run_ids,
        max_steps=args.max_steps,
        measure_every=args.measure_every,
        verbose=True,
    )
    path = write_simulation(frame, args.out, legacy_schema=args.legacy_schema)
    print(path)


if __name__ == "__main__":
    main()
