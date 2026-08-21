# Corrections and Clarifications to the 2024 Paper

This repository records the author-correction map for *Entanglement Trajectory and its Boundary*, Quantum 8, 1282 (2024). It does not alter the journal version of record.

## Bottom line

The trajectory representation and the broader unification philosophy survive. The exact mathematical core is stronger after correction: the feasible arena is known exactly from the Schmidt spectrum. The article's simple boundary curves, exact Page theorem, rank-one argument, QFT invariance, arithmetic endpoint, and several computational interpretations require correction.

## Material corrections

| ID | Location | Topic | Required correction |
|---|---|---|---|
| PC-001 | p. 1, L5-L14 | Source of the boundary | Exact geometry: for fixed p=lambda_max, use the concentrated spectrum for the minimum and the equal-tail spectrum for the maximum. Describe Haar/Wishart or spiked-Wishart curves separately as probabilistic references. |
| PC-009 | p. 2, L65-L75 | Exact upper entropy boundary | Replace Eq. (3) by S_max(p;alpha)=-p log p-(1-p)log[(1-p)/(alpha-1)]. |
| PC-010 | p. 2, L70-L75 | Claim of a tight counterexample-free three-curve boundary | Call the old curves historical approximations and replace Figure 1 with exact piecewise envelopes. |
| PC-012 | p. 2, L76-L83 | Continuity of quantum evolution | Replace with a sampling caveat: connecting lines indicate temporal order and do not reconstruct the unsampled physical evolution. |
| PC-022 | p. 7, L270-L284 | Normalization of the stated post-SWAP spectrum | Correct the denominator after checking the raw circuit spectra and regenerate the explanatory sentence. |
| PC-026 | p. 11, L479-L487 | Scaling of the noise spectral edge | Restore the missing factor beta and express the separation condition in one consistent scaling convention. |
| PC-027 | p. 11, L488-L493 | Eigenvalues of the deterministic mean component | Replace the sentence and keep only the single nonzero eigenvalue. |
| PC-028 | p. 11, L494-L506 | Equality lambda_max=alpha\|gamma\|^2 | Use an approximation sign and state a norm-ratio or separated-spike assumption. |
| PC-031 | p. 11, L511-L523 | Exact Page formula | Replace Theorem 2 by the harmonic-number formula and label Eq. (23) asymptotic. |
| PC-032 | p. 13, L571-L598 | Elimination of the random trace | Mark the trace replacement as a large-dimension approximation or work directly with the fixed-trace Wishart ensemble. |
| PC-034 | p. 14, L701-L735 | Meaning of Eq. (32) | Rename Eq. (32) the large-size noncentral/spiked-Wishart reference curve under a separated-spike approximation. |
| PC-039 | p. 18, L937-L992 | Entanglement of the union endpoint U_{n-1} | State that U_{n-1} approaches the product point asymptotically but is not exactly product. Keep the zero-entanglement statement only for P_{n-1}. |
| PC-041 | p. 19, L1001-L1017 | Computational-basis amplitude versus Schmidt eigenvalue | Remove this identification and formulate any observed relation as an ensemble-specific numerical correlation. |
| PC-042 | p. 20, L1028-L1073 | Exact QFT preservation of entropy and lambda_max | Replace the exact claim by: the selected nonzero-mean random ensemble and arithmetic examples show approximate state-family-specific overlap under the tested Fourier transform. |
| PC-046 | p. 22, L1148-L1154 | Universal entropy-gap monotonicity and Li-Haldane attribution | Restrict monotonicity to the declared reference curve and remove the universal attribution. |
| PC-051 | p. 23, L1185-L1213 | Renyi order zero | Replace the statement and define the zero-eigenvalue convention explicitly. |

## Corrected hierarchy

1. **Exact:** finite-dimensional feasible envelopes derived from spectrum extremization and majorization.
2. **Conditional:** Haar/Wishart and separated-spike asymptotics under declared ensemble assumptions.
3. **Empirical:** metric-robust trajectory morphology in the tested four-model follow-up package.
4. **Open:** formal topology, universal fingerprinting, and links to computational advantage.

## What the repository says

- The Schmidt spectrum is the state variable; entanglement metrics are observables on it.
- Unification does not require universal agreement among metrics.
- Metric agreement has an exact majorization explanation; disagreement can signal incomparable spectral redistribution.
- The trajectory atlas provides the common representation.
- Quoted "topological invariant" means empirical coarse morphology stable across metric projections, not a proved topological invariant.
- Random matrix theory provides reference ensembles, not the exact boundary.

## Journal-status recommendation

The final repository should be completed first. After all corrected formulas, figures, code, and data are frozen, the author should contact *Quantum* with a concise factual corrigendum covering the objective mathematical and physical errors. The fuller conceptual reframing belongs in this repository clarification.

## Machine-readable record

The authoritative location-specific ledger is available as `metadata/paper_correction_ledger.csv`. Deterministic correction calculations are implemented in `analysis/verify_paper_corrections.py`.

## Quantitative clarification of “topology” and fingerprints

The follow-up data now support a dominant common metric mode and substantial cross-metric relational morphology after exact-boundary normalization. They do **not** support exact projected-path topology: exact vertical-turn counts agree across all three tested metric classes on only 2 of 96 trajectories. The quoted “topological invariant” should therefore mean an empirical coarse metric-robust trajectory class.

Model-centroid trajectories are distinguishable under leave-one-size-out tests, but unseen individual trajectories remain a preliminary fingerprint claim and do not clearly outperform the shared `lambda_max` path under the strictest size-plus-condition holdout.

All 50 observed metric-competition events in the selected full-spectrum audit occur on majorization-incomparable transitions. This supplies the corrected mechanism behind legitimate disagreement among entanglement metrics.
