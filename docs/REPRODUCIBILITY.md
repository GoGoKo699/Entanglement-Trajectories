# Reproducibility

## Environment

The current implementation supports Python 3.10 or later for development. Install the broad compatibility dependencies declared in `pyproject.toml` with:

```bash
python -m pip install -e '.[analysis,test]'
```

Release `v1.0.0` has a separate canonical numerical environment: CPython `3.11.15` on `ubuntu-24.04`, with exact build and runtime locks under `requirements/`. See [Canonical release environment](RELEASE_ENVIRONMENT.md). A normal broad installation is not a substitute for the locked release job when reproducing release-level numerical snapshots.

The historical paper-era Qibo scripts are preserved for provenance and are not the recommended current workflow.

## Reproduction levels

### Level 0 — Rebuild the canonical machine-facing context

```bash
make public-context
```

This deterministically rebuilds `llms-full.txt` from the canonical public documents listed in `scripts/build_llms_full.py`. It does not alter scientific results.

### Level 1 — Rebuild the five public figures from included inputs

```bash
make public-figures
```

Generated figures and compact source tables are written under:

```text
outputs/public_figures/
```

The images under `figures/public/` are the validated release snapshot shown by the README. In the locked release job, rebuilt CSV source tables must preserve the file set, schema, row order, nonnumeric values, and finite/NaN patterns exactly; numerical entries must agree within `atol=rtol=1e-10`. Nonnumeric provenance records remain byte-identical. Rendered PNGs are validated for successful generation and dimensions; byte-level image identity is not required across graphics stacks.

### Level 2 — Automated scientific and repository validation

```bash
make test
make public-validate
make peer-review-check
```

The tests cover metric identities, exact boundaries, majorization, deterministic model dynamics, random-matrix tools, trajectory robustness, included-data regressions, metadata, archive integrity, and internal links. The peer-review verifier checks closure of the numerical-physics, exact-mathematics, figure-provenance, release-environment, wording, and selected-spectrum gates. Run the complete public-layer workflow with:

```bash
make public
```

### Level 3 — Rebuild analyses from the included trajectory and spectrum data

```bash
make rebuild-included
```

This workflow:

1. extracts the five selected complete-spectrum reruns;
2. regenerates the corrected Marchenko–Pastur and entanglement-spectrum diagnostics;
3. recomputes the metric-robustness, majorization, geometry, and classification analyses;
4. regenerates the analysis figures under `outputs/rebuild/`;
5. rebuilds the five public figures and validates the repository.

The classification and resampling analyses are intentionally more expensive than the public-figure workflow.
For a fast end-to-end workflow check, reduce only the resampling counts, for example `BOOTSTRAP=20 MANTEL_PERMUTATIONS=10 make rebuild-included`; the release-level quantitative tables use the documented default counts of 3,000 and 1,000.

### Level 4 — Quick independent trajectory regeneration

```bash
make quick
```

This regenerates all 16 runs at $n=10$, compares the result with the included canonical table, and runs the complete test suite. Outputs are written under `outputs/quick/`.

### Level 5 — Full state-vector regeneration

```bash
make full
```

This runs the deterministic trajectory workflow at $n=10,12,14,16,18,20$. The $n=20$ dense state-vector simulations can require substantial memory and runtime. Included-data reconstruction is the normal verification path.

## Canonical inputs and metadata

The current source of truth is:

- `data/trajectory_observations.csv` — 5,856 canonical scalar observations;
- `data/spectra_selected_n20.zip` — five selected complete-spectrum reruns;
- `data/public_analysis_inputs.zip` — derived tables used by the five public figures;
- `metadata/metric_registry.json` — canonical metric definitions and equivalence classes;
- `metadata/public_claims.json` — scoped exact, empirical, corrected, and limitation claims;
- `metadata/paper_correction_ledger.csv` — location-specific audit of the 2024 paper;
- `src/entanglement_trajectories/models.py` — model parameters, run IDs, and deterministic seed policy.

The original GPT-5.5 follow-up ZIP and frozen publication/repository metadata are preserved inside `legacy/historical_sources.zip`. The original root scripts remain recoverable from the `paper-2024-original` branch and Git history. They have been removed from the corrected `main` branch so that historical filenames cannot be mistaken for the supported implementation.

## Numerical conventions

- Reduced spectra are sorted and normalized before metric evaluation.
- Tiny negative eigenvalues caused by numerical diagonalization are handled by the canonical spectrum validator.
- Exact fixed-$\lambda_{\max}$ boundaries are evaluated pointwise rather than interpolated from a plotting grid.
- Collapsed feasible envelopes return an undefined relative coordinate rather than an arbitrary zero or one.
- The balanced Marchenko–Pastur CDF uses its corrected analytic expression.
- Majorization tests state their numerical tolerance explicitly.
- Pure-state logarithmic negativity, equivalent here to the Rényi-$1/2$ sector, is especially sensitive to tiny numerical Schmidt tails near product states; its regression tolerance is therefore recorded separately.
- The one-site geometric coordinate depends directly on a leading reduced-density-matrix eigenvalue. In the canonical CPython 3.11.15 / NumPy 2.4.6 hosted regression, its maximum absolute difference from the archived table is $2.449\times10^{-9}$. The release test therefore uses an absolute tolerance of $5\times10^{-9}$ for that coordinate only. This is a numerical-backend tolerance on a normalized quantity, not a scientific uncertainty interval.

## Release identity

The tagged Git commit identifies the exact repository source tree. [`RELEASE_ENVIRONMENT.md`](RELEASE_ENVIRONMENT.md) freezes the canonical Python environment, and [`RELEASE_QA.md`](RELEASE_QA.md) records the scientific, computational, and hosted-release checks. The repository validator also checks the structure and CRC integrity of the included data and provenance archives.

## Compact repository

Selected spectra and public-analysis inputs are bundled under `data/`; supported workflows extract them automatically into the ignored `outputs/` directory. The provenance archive under `legacy/` is retained for historical reconstruction and is not used by current analyses.

## XXZ convergence audit

Run the dedicated refinement study with:

```bash
make xxz-convergence
```

The compact frozen evidence is stored in `data/xxz_convergence_n10_n12_n14.zip`. The released scalar table retains the historical one-substep circuit and documents that interpretation explicitly.
