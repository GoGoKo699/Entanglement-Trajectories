# Release QA Report

## Release

- Repository edition: `1.0.0`
- Release date: 2026-08-20
- Intended repository: `GoGoKo699/Entanglement-Trajectories`
- Published companion article: Ruge Lin, “Entanglement Trajectory and its Boundary,” *Quantum* **8**, 1282 (2024), DOI `10.22331/q-2024-03-14-1282`
- Public-repository state during this audit: not yet uploaded
- Formal journal corrigendum: recommended and drafted, but not submitted

## Release gate

The compact repository release passed its local scientific, computational, metadata, integrity, and browser-upload checks. No unresolved critical or high-severity release defect remains in the repository package.

One scientific issue is intentionally unresolved rather than guessed: the post-SWAP Shor spectrum printed in the 2024 paper is not normalized as written. A replacement is deferred until the archived circuit spectrum is regenerated directly.

## Scientific checks

### Exact metric layer

The automated suite verifies:

- spectrum normalization and ordering;
- exact fixed-$\lambda_{\max}$ majorization extremizers;
- von Neumann, Rényi, purity/linear, pure-state logarithmic-negativity, effective-rank, geometric, and leading-edge identities;
- exact metric envelopes and endpoint handling;
- majorization relations and explicit metric-order reversals;
- analytic balanced Marchenko–Pastur CDF behavior;
- deterministic model definitions and seeds.

### Paper-correction calculations

```bash
python analysis/verify_paper_corrections.py --check-only
```

Result: all deterministic correction checks passed. These cover the exact entropy and gap arenas, the exact Page mean, rank-one deterministic Wishart component, QFT counterexample, finite arithmetic-union endpoint, entropy-gap counterexample, and related unit/scaling checks.

### Included selected spectra

The selected-spectrum reconstruction processed:

- 5 complete-spectrum runs;
- 81 saved times per run;
- 405 spectra total;
- Schmidt-spectrum dimension 1,024.

The corrected analytic Marchenko–Pastur KS calculation is finite and bounded on every checked spectrum. Reproducing the historical singular-grid implementation gives a maximum absolute KS error of approximately `0.7525833948` and a mean absolute error of approximately `0.4437556468`, confirming that the repair is material.

### Metric-robustness analysis

An end-to-end reduced-resampling smoke run of `analysis/analyze_metric_robustness.py` completed successfully after extracting the included spectra. Resampling counts were reduced only for workflow time; deterministic central quantities reproduced the release values:

- boundary-normalized common-mode variance: `0.9026282298671149`;
- scalar metric-competition events: `808` of `5,760` transitions;
- selected full-spectrum metric-competition events: `50`;
- competition events outside the majorization-incomparable sector: `0`;
- same-metric held-out-size model-centroid accuracy: `0.9166666666666666`;
- same-metric size-and-condition-held-out individual accuracy: `0.3680555555555555`.

The release-level bootstrap interval and Mantel statistics in the bundled public-analysis inputs use the documented 3,000 bootstrap resamples and 1,000 permutations.

## Computational checks

### Automated test suite

```bash
pytest -q
```

Result: **69 tests passed**.

The suite is consolidated into one file to keep the browser-upload package below the per-upload file-count limit. It retains the scientific tests from the modular development package.

### Public-layer workflow

```bash
make public
```

Result: passed. This rebuilt `llms-full.txt`, regenerated the five public figures from the included compact inputs, ran the complete test suite, and validated the public repository layer.

All six tracked PNG assets—the five public figures and social preview—were byte-identical to the regenerated versions. The social preview is `1280 × 640` pixels.

### Independent $n=10$ regeneration

```bash
make quick
```

Result: passed for all 16 model/run combinations and 656 recorded observations.

Maximum differences from the included canonical table were:

- time coordinate: `1.11e-16`;
- non-logarithmic-negativity metrics: at most `3.67e-14`;
- one-site mean logarithmic negativity: `6.08e-9`;
- half-chain logarithmic negativity: `3.95e-9`.

The separately documented logarithmic-negativity tolerance reflects Rényi-$1/2$ sensitivity to tiny numerical Schmidt tails near product states.

### Build and isolated import

A wheel was built without network access using the installed build backend, installed into an isolated environment with system scientific packages, and imported successfully.

- imported package version: `1.0.0`;
- bundled metric-registry records: `26`.

### Syntax and shell checks

- all current Python modules compiled successfully;
- all supported shell scripts passed `bash -n`;
- transient caches and build artifacts were removed before packaging.

## Metadata and discovery checks

The release validator checks:

- `CITATION.cff`, `codemeta.json`, JSON registries, and version consistency;
- uniqueness of public claim IDs and metric IDs;
- archive-member evidence links in the public claim registry;
- internal Markdown links;
- required qualifications around topology, random-matrix theory, majorization, and individual fingerprinting;
- public figure readability dimensions;
- historical root scripts as explicit compatibility notices rather than silently active legacy code;
- canonical data dimensions and required columns.

The human-facing and AI-facing authority layers are synchronized through `README.md`, `AI_CONTEXT.md`, `SCIENTIFIC_POSITION.md`, the public claim/definition registries, and deterministic `llms-full.txt` construction.

## Integrity and browser-upload checks

The final release contains fewer than 100 repository files, every file is below 25 MiB, and no enclosing directory is stored inside the upload ZIP. The manifest covers every non-self-referential repository file. `SHA256SUMS.txt` covers every repository file except itself.

The three included nested ZIP archives pass CRC checks:

- `data/spectra_selected_n20.zip`;
- `data/public_analysis_inputs.zip`;
- `legacy/historical_sources.zip`.

The final external upload ZIP is independently extracted and revalidated before handover.

## Deliberately excluded expensive reruns

The following were not repeated during final compact-package assembly:

- the complete dense state-vector simulation through all declared sizes up to $n=20$;
- the full 3,000-resample/1,000-permutation robustness recomputation.

Both are exposed by the repository workflows. The included canonical tables and public-analysis inputs originate from the previously validated full checkpoint package, while this release assembly reran the exact mathematics, selected-spectrum reconstruction, public layer, all tests, all $n=10$ trajectories, and a reduced-resampling end-to-end robustness workflow.

## Final assessment

The package is suitable for the planned workflow: preserve the historical branch, upload the extracted repository contents to `main`, rename the repository, apply the discovery settings, and allow GitHub Actions to rerun the public QA workflow on the hosted tree.
