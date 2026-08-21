# Included data

The repository contains four compact, version-controlled data objects.

- `trajectory_observations.csv`: the canonical 5,856-row trajectory table covering four model families, four conditions per family, and system sizes 10 through 20.
- `spectra_selected_n20.zip`: five selected complete Schmidt-spectrum reruns used for the majorization and spectrum-level audit. The selection is intentionally limited and is not a model-wide spectrum census.
- `public_analysis_inputs.zip`: frozen compact derived tables used for the fast public-figure snapshot rebuild. The end-to-end `make rebuild-included` workflow bypasses this archive and feeds freshly recomputed tables directly to the figure builder.
- `xxz_convergence_n10_n12_n14.zip`: the product-formula refinement study for all four XXZ conditions at $n=10,12,14$ and substep counts $1,2,4,8,16,32$.

All current analyses treat `trajectory_observations.csv` as the canonical scalar dataset. The original GPT-5.5 package is preserved inside `legacy/historical_sources.zip` for provenance, not as the current source of truth.

The selected NPZ spectra are stored in descending Schmidt-eigenvalue order and carry an explicit `spectrum_order="descending"` field.
