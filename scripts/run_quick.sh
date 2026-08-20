#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p outputs/quick
python scripts/validate_n10_regression.py \
  --reference data/trajectory_observations.csv \
  --current-output outputs/quick/trajectory_observations_n10.csv \
  --report outputs/quick/n10_regression_report.json
pytest -q
