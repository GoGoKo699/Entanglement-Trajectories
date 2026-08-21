# Peer-Review Release Audit

## Verdict

**Scientific release recommendation: GO, conditional on one green run of the locked `repository-qa` workflow on the final uploaded commit and application of the remaining GitHub discovery settings.**

This audit evaluates repository edition `1.0.0` as a corrected computational companion to:

> Ruge Lin, “Entanglement Trajectory and its Boundary,” *Quantum* **8**, 1282 (2024), DOI `10.22331/q-2024-03-14-1282`.

The article remains the journal version of record. The repository supplies a transparent author clarification, exact mathematical replacements, repaired code, and scoped follow-up evidence.

## Supported central statement

For a fixed bipartition of a pure state, the ordered Schmidt spectrum is the common state variable. Standard spectrum-based entanglement measures are nonlinear observables on that path. Across four tested dynamical families used to probe scrambling, recurrence, disorder, and spectral complexity, the exact-boundary-normalized metric projections share a dominant coarse mode while retaining legitimate local disagreements on majorization-incomparable spectral changes.

The supported conclusion is an empirical **metric-robust trajectory class**. It is not a formal topological invariant, exact metric equivalence, or a universal individual-run fingerprint.

## Main quantitative evidence

| Check | Frozen result |
|---|---:|
| Boundary-normalized first common mode | 0.902628 |
| Model-stratified design-cluster 95% sensitivity interval | 0.862613–0.934124 |
| Median separate-trajectory first-mode fraction | 0.947514 |
| Equal-trajectory-weight first mode | 0.912273 |
| Within-trajectory-standardized first mode | 0.918605 |
| First-difference first mode | 0.862160 |
| Metric-competitive scalar transitions | 808/5,760 |
| Selected full-spectrum competition events | 50 |
| Competition outside majorization-incomparable transitions | 0 |
| Held-out-size model-centroid full-path accuracy | 0.875 same metric; 0.673611 cross metric |
| Held-out-size model-centroid vertical-only accuracy | 0.763889 same metric; 0.375 cross metric |
| Size-and-condition-held-out individual full-path accuracy | 0.329861 same metric; 0.357639 cross metric |
| Corresponding largest-Schmidt-value path baseline | 0.416667 |

These values show a strong shared coarse component and model-level morphology within the designed dataset. They also show why the fingerprint claim must remain limited: vertical-only transfer is weaker, and unseen individual paths do not beat the shared horizontal-coordinate baseline under the strictest test.

## Closure of the four original release blockers

### 1. XXZ product-formula convergence

The released XXZ rows are now interpreted as fixed one-substep symmetric product-formula circuits generated from random-field XXZ terms, not convergence-controlled continuous-time Hamiltonian trajectories. The dedicated `n=10,12,14` study contains 3,528 observations and exhibits second-order refinement. The maximum `16→32` difference is 0.001662, while replacing the coarse XXZ rows by refined rows changes the global common-mode fraction by less than 0.001.

Evidence:

- `docs/XXZ_PRODUCT_FORMULA_CONVERGENCE.md`
- `data/xxz_convergence_n10_n12_n14.zip`
- `analysis/run_xxz_convergence.py`

### 2. End-to-end public-figure provenance

The public figure builder accepts freshly recomputed result tables through `--analysis-input-dir`, records exact input provenance, and is called that way by `make rebuild-included`. A controlled perturbation changes the corresponding figure. The frozen snapshot mode remains available for fast reconstruction.

Evidence:

- `docs/PUBLIC_FIGURE_PROVENANCE.md`
- `scripts/build_public_figures.py`
- `scripts/rebuild_all_from_included_data.sh`
- `figures/public/data/public_figure_input_provenance.json`

### 3. Exact Hartley/Rényi-zero semantics

Exact Schmidt rank and Hartley entropy now count every strictly positive represented eigenvalue. Thresholded numerical rank is a separately named diagnostic. At `d=1024`, `p=1-10^-14`, the exact Hartley envelope is `[1,10]` bits even though a `10^-15` threshold gives numerical rank one.

Evidence:

- `src/entanglement_trajectories/metrics.py`
- `src/entanglement_trajectories/boundaries.py`
- `docs/EXACT_SPECTRAL_GEOMETRY.md`
- `metadata/metric_registry.json`

### 4. Archival environment and CI

The canonical release environment is CPython 3.11.15 on Ubuntu 24.04 x86-64, with exact build and numerical dependency locks. The workflow uses immutable full-SHA action references, least-privilege permissions, deterministic thread settings, environment verification, public-source reconstruction, scientific tests, repository validation, and the peer-review release verifier.

Evidence:

- `.github/workflows/qa.yml`
- `.python-version`
- `requirements/release-build.txt`
- `requirements/release-py311.txt`
- `environment/release-py311.json`
- `docs/RELEASE_ENVIRONMENT.md`

## Additional peer-review repairs

The final tree also:

- uses gap-aware interpolation rather than bridging internal undefined boundary intervals;
- reports full-path, vertical-only, and largest-Schmidt-value-only fingerprint baselines together;
- uses model-stratified design-cluster sensitivity intervals and explicitly rejects population-level interpretation;
- calls `tau=step/n` a scaled iteration coordinate rather than universal physical time;
- stores selected Schmidt spectra in descending order with an explicit schema field;
- distinguishes full-path arc length, vertical total variation, origin-closed area, and exact turn count;
- includes primary references, split code/content licenses, and machine-readable claim, definition, metric, figure, correction, and audit records;
- retains the selected-spectrum audit as a five-run mechanism check rather than a model-wide frequency estimate.

The resolution of all 21 review items is recorded in `metadata/peer_review_issue_resolution.csv`.

## Repeated release checks

The final cumulative candidate passed:

- 76 automated tests;
- a complete included-data analysis with 3,000 model-stratified bootstrap resamples and 1,000 Mantel-style permutations;
- end-to-end figure generation from the freshly recomputed tables;
- exact Hartley near-product verification;
- reconstruction of all 405 selected Schmidt spectra and the 400-transition majorization audit;
- deterministic paper-correction checks;
- public links, image links, metadata, archive CRC, figure dimensions, JSON/YAML, Python syntax, shell syntax, wheel build, and isolated installation checks;
- the dedicated peer-review release verifier.

Run:

```bash
make public
make rebuild-included
python analysis/verify_paper_corrections.py --check-only
python scripts/verify_release_environment.py --structure-only
make peer-review-check
```

## Residual limitations

The release does not claim:

- convergence-controlled XXZ Hamiltonian dynamics for the historical one-substep rows;
- independent disorder or initial-state ensemble replication;
- a thermodynamic-limit result;
- a formal topological invariant;
- a universal chaos classifier;
- model-wide majorization-event frequencies from the five selected complete-spectrum runs;
- that the metric atlas consistently outperforms the largest-Schmidt-value coordinate for unseen individual paths.

A concise factual corrigendum to *Quantum* remains recommended after the repository release is frozen. That journal action is separate from the technical release gate.

## Final release gate

Create `v1.0.0` only after:

1. the cumulative patch is uploaded;
2. the locked hosted `repository-qa` workflow passes on that exact commit;
3. the DOI homepage, selected topics, and social-preview image are applied in GitHub settings.
