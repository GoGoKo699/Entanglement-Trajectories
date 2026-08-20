#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p outputs/full
python scripts/run_trajectory_experiment.py \
  --sizes 10 12 14 16 18 20 \
  --out outputs/full/trajectory_observations_full.csv
