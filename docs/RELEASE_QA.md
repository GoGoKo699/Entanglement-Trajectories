# Release QA

## Release identity

- **Repository:** `GoGoKo699/Entanglement-Trajectories`
- **Repository edition:** `1.0.0`
- **Published companion article:** Ruge Lin, “Entanglement Trajectory and its Boundary,” *Quantum* **8**, 1282 (2024)
- **DOI:** `10.22331/q-2024-03-14-1282`
- **Historical paper-era branch:** `paper-2024-original`
- **Frozen historical commit:** `81206df955622c31225f0d4f9c290e35d41ba381`
- **Formal journal corrigendum:** not submitted

The published article remains the journal version of record. This repository provides an explicit author clarification, corrected mathematical layer, repaired computational implementation, and follow-up evidence.

## Scientific validation

### Exact Schmidt-spectrum geometry

The test suite verifies:

- normalization and ordering of reduced-density-matrix spectra;
- the equal-tail and concentrated fixed-$\lambda_{\max}$ majorization extremizers;
- exact finite-dimensional feasible envelopes for the implemented von Neumann, Rényi, purity/linear-entropy, pure-state logarithmic-negativity, effective-rank, geometric, and leading-edge quantities;
- endpoint and degenerate-envelope handling;
- majorization relations and explicit metric-order reversals.

### Published-paper corrections

The deterministic correction checks verify:

- the exact entropy boundaries at fixed largest Schmidt value;
- the exact finite-dimensional Page mean;
- the rank-one deterministic component of the noncentral Wishart construction;
- consistent Wishart and Marchenko–Pastur scaling;
- a direct counterexample to general QFT preservation of Schmidt spectra;
- the finite arithmetic-union endpoint;
- exact entanglement-gap envelopes;
- a counterexample to universal entropy-gap ordering.

The post-SWAP Shor spectrum printed in the 2024 article remains unresolved because it is not normalized as written. The repository records this issue without introducing an unverified replacement.

### Follow-up trajectories and spectra

The canonical trajectory dataset contains:

- four dynamical families;
- four conditions per family;
- six system sizes, $n=10,12,14,16,18,20$;
- 96 trajectories;
- 5,856 scalar observations.

The selected full-spectrum audit contains:

- five complete-spectrum runs at $n=20$;
- 81 saved times per run;
- 405 Schmidt spectra;
- spectrum dimension 1,024.

The repaired implementation uses the analytic balanced Marchenko–Pastur cumulative distribution rather than the inaccurate singular-grid integration used in the historical follow-up code.

### Metric-robustness result

The validated central results include:

- exact-boundary-normalized common-mode variance: `0.9026282298671149`;
- model-stratified design-cluster 95% interval: `[0.8626128030927239, 0.9341235189039404]`;
- median per-trajectory common-mode fraction: `0.9475141487435563`;
- metric-competitive scalar transitions: `808/5760`;
- metric-competition events in the selected full-spectrum audit: `50`;
- competition events outside the majorization-incomparable sector: `0`;
- gap-aware held-out-size model-centroid full-path accuracy: `0.875` in the same metric and `0.6736111111111112` across metrics;
- size-and-condition-held-out individual full-path accuracy: `0.3298611111111111` in the same metric and `0.35763888888888884` across metrics;

These results support an empirical **metric-robust trajectory class**. They do not establish a formal topological invariant or a universal individual-run fingerprint.

## Computational and reproducibility validation

The compact release package passed:

- **76 automated scientific and repository tests**;
- reconstruction of the public machine context;
- regeneration of all five public figures from included inputs;
- public metadata and internal-link validation;
- deterministic paper-correction checks;
- independent regeneration of all 16 $n=10$ runs and 656 recorded observations;
- selected-spectrum reconstruction for all 405 archived spectra;
- package wheel construction and isolated import;
- syntax checks for the current Python and shell code;
- CRC and schema checks for the four included data and provenance archives.

The regenerated public-figure source tables matched the committed release sources exactly, and all rendered images opened successfully with the declared dimensions. A controlled provenance test confirmed that changing a recomputed input changes the corresponding figure. The XXZ refinement archive was re-evaluated from its 3,528 frozen observations, and the exact Hartley near-product counterexample and thresholded numerical-rank separation were rechecked.

The final peer-review audit repeated the complete included-data analysis with 3,000 model-stratified bootstrap resamples and 1,000 Mantel-style permutations, then rebuilt the five public figures from those fresh tables. The dense state-vector simulation through every declared size up to $n=20$ was not repeated; its canonical dataset, an independent all-run $n=10$ regression, the selected-spectrum reconstruction, and the complete workflow remain included.

### Canonical release environment

The blocking hosted job uses:

- `ubuntu-24.04` on `x86_64`;
- CPython `3.11.15` from `.python-version`;
- exact build and runtime locks in `requirements/release-build.txt` and `requirements/release-py311.txt`;
- single-thread numerical environment variables recorded in `environment/release-py311.json`;
- `pip check`, an exact environment verifier, source-table comparisons and rendered-image checks, the scientific tests, and the public validator.

See [Canonical release environment](RELEASE_ENVIRONMENT.md).

## Hosted repository release gate

The `v1.0.0` release should be created only after:

1. the final cleanup commit is complete;
2. the locked `repository-qa` GitHub Actions release job passes on the final commit;
3. the repository description, DOI homepage, topics, and social preview have been applied.

A passing local package audit does not replace the final hosted Actions run.

## Assessment

Subject to the hosted release gate above, the repository is suitable as the corrected public computational companion to the 2024 article.

Its supported scientific hierarchy is:

```math
\begin{array}{c}
\text{Schmidt-spectrum path}
\\[4pt]
\downarrow
\\[4pt]
\text{multiple metric projections}
\\[4pt]
\downarrow
\\[4pt]
\text{trajectory atlas}
\\[4pt]
\downarrow
\\[4pt]
\left\{
\begin{array}{l}
\text{shared coarse morphology},\\[3pt]
\text{informative metric competition}.
\end{array}
\right.
\end{array}
```

Exact mathematical statements, conditional random-matrix references, empirical results, published-paper corrections, and unresolved questions are separated explicitly.
