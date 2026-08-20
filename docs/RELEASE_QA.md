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
- cluster-bootstrap 95% interval: `[0.8574156931787958, 0.9379151738860936]`;
- median per-trajectory common-mode fraction: `0.9475141487435563`;
- metric-competitive scalar transitions: `808/5760`;
- metric-competition events in the selected full-spectrum audit: `50`;
- competition events outside the majorization-incomparable sector: `0`;
- same-metric held-out-size model-centroid accuracy: `0.9166666666666666`;
- size-and-condition-held-out individual-path accuracy: `0.3680555555555555`.

These results support an empirical **metric-robust trajectory class**. They do not establish a formal topological invariant or a universal individual-run fingerprint.

## Computational and reproducibility validation

The compact release package passed:

- **69 automated scientific and repository tests**;
- reconstruction of the public machine context;
- regeneration of all five public figures from included inputs;
- public metadata and internal-link validation;
- deterministic paper-correction checks;
- independent regeneration of all 16 $n=10$ runs and 656 recorded observations;
- selected-spectrum reconstruction for all 405 archived spectra;
- package wheel construction and isolated import;
- syntax checks for the current Python and shell code;
- CRC checks for the three included data and provenance archives.

The regenerated public figures were byte-identical to the archived release figures.

The complete dense state-vector simulation through every declared size up to $n=20$, and the complete 3,000-bootstrap/1,000-permutation recomputation, were not repeated during compact release assembly. Their canonical validated outputs and full workflows remain included.

## Hosted repository release gate

The `v1.0.0` release should be created only after:

1. the final cleanup commit is complete;
2. the hosted `repository-qa` GitHub Actions workflow passes;
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
