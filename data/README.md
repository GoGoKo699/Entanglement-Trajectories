# Included data

The repository contains three compact, checksum-tracked data objects.

- `trajectory_observations.csv`: the canonical 5,856-row trajectory table covering four model families, four conditions per family, and system sizes 10 through 20.
- `spectra_selected_n20.zip`: five selected complete Schmidt-spectrum reruns used for the majorization and spectrum-level audit. The selection is intentionally limited and is not a model-wide spectrum census.
- `public_analysis_inputs.zip`: compact derived tables used to reproduce the five public figures without rerunning the expensive state-vector simulations.

All current analyses treat `trajectory_observations.csv` as the canonical scalar dataset. The original GPT-5.5 package is preserved inside `legacy/historical_sources.zip` for provenance, not as the current source of truth.
