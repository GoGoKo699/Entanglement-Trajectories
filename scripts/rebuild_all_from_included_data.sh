#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BOOTSTRAP="${BOOTSTRAP:-3000}"
MANTEL_PERMUTATIONS="${MANTEL_PERMUTATIONS:-1000}"

rm -rf outputs/rebuild
mkdir -p \
  outputs/rebuild/spectra_source \
  outputs/rebuild/spectra \
  outputs/rebuild/spectrum_data \
  outputs/rebuild/spectrum_analysis \
  outputs/rebuild/spectrum_figures \
  outputs/rebuild/results \
  outputs/rebuild/figures

python - <<'PY2'
from pathlib import Path
import zipfile
root = Path.cwd()
with zipfile.ZipFile(root / 'data' / 'spectra_selected_n20.zip') as zf:
    zf.extractall(root / 'outputs' / 'rebuild' / 'spectra_source')
PY2

python scripts/rebuild_spectrum_diagnostics.py \
  --input-spectra-dir outputs/rebuild/spectra_source \
  --copied-spectra-dir outputs/rebuild/spectra \
  --data-outdir outputs/rebuild/spectrum_data \
  --analysis-outdir outputs/rebuild/spectrum_analysis \
  --figure-outdir outputs/rebuild/spectrum_figures

python analysis/analyze_metric_robustness.py \
  --input data/trajectory_observations.csv \
  --spectra-dir outputs/rebuild/spectra \
  --result-dir outputs/rebuild/results \
  --figure-dir outputs/rebuild/figures \
  --bootstrap "$BOOTSTRAP" \
  --mantel-permutations "$MANTEL_PERMUTATIONS"

python scripts/build_public_figures.py \
  --analysis-input-dir outputs/rebuild/results \
  --trajectory-input data/trajectory_observations.csv \
  --output-dir outputs/rebuild/public_figures

python analysis/validate_public_repository.py
