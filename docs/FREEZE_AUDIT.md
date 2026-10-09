# Numerical Validation Record — September 2026

This AI-assisted numerical and consistency audit covers the finite designed dataset and its reproducibility workflows. It is an internal validation record, not independent journal peer review.

## Validated numerical contracts

- Fixed-p boundaries require an integer dimension and reject booleans and fractional dimensions.
- Entropy and entanglement-energy units require finite logarithm bases greater than one.
- The entanglement-Hamiltonian gap uses a difference of logarithms, avoiding ratio overflow for a strictly positive second eigenvalue.
- Normalized support and effective-rank coordinates are zero in the one-dimensional space; raw ranks remain one.
- XXZ substep counts require positive integers, and record intervals require finite positive values.
- Scientific claims distinguish point-cloud geometry from chronology, with historical numerical snapshots identified explicitly.

Thirty regression cases cover the API contracts, and eleven further cases cover resolved variation. The geometry/chronology control archive is generated from the audited source.

## Checks and independent probes

The audit includes 244 standard test cases. The audit additionally runs the public-figure rebuild and numerical source comparison, the paper-correction checks, the numerical-foundations command, the full included-data analysis with its default 3,000 bootstrap and 1,000 permutation settings, and the full geometry/chronology study with 999 chronology draws and 199 draws for each matched-spectrum law.

Independent local probes supplement those workflows: 585 high-precision entropy cases; 500 random spectra with 5,000 metric-envelope comparisons; 36 analytical Schmidt-state constructions; direct partial-transpose checks; 32 independently assembled small-system step operators covering all 16 model conditions at n=4 and n=5; exact-matrix-exponential XXZ refinement and magnetization checks; independent Marchenko-Pastur quadrature and Page means; and all 16,200 distinct pairs in the selected-spectrum archive. Scripts and detailed measurements are retained in the companion freeze-audit evidence package.

The random-spectrum test distinguishes exact identities from rounded input contracts. Two naive fixed-float-p comparisons at very small positive Renyi order differ by several parts in 10^9 near a collapsed two-level envelope. Their separately rounded input components imply a largest-value uncertainty below one floating-point step; the discrepancies are enclosed by the explicit input-rounding allowance. This is not evidence of a majorization violation or a claim of arbitrary relative accuracy. The naive discrepancies remain in the audit record.

## Interpretation and validation scope

The common spectrum and majorization geometry remain the mathematical framework. The approximately 90.26% point-cloud mode is descriptive, not an order-sensitive test. Chronological smoothness and excess local metric competition survive the specified reorderings. Constructed matched spectra can have stronger common-mode fractions; chronology does not improve path-distance agreement uniformly.

The audit checks included archives, reproduction paths, independent small-system operators, and contained reruns. Its check set excludes full n=20 physical regeneration and complete large-system XXZ convergence production. Historical one-substep XXZ rows represent circuits, with the Hamiltonian comparison governed by the refinement study. The pinned package set specifies Python dependencies; operating-system and numerical-backend differences can still affect final floating-point digits.

## Numerically constant paths and historical summaries

Standardizing a coordinate whose variation is only numerical noise can produce arbitrary PCA fractions and rank correlations. Current per-trajectory PCA and half-chain within-trajectory Spearman calculations therefore declare a standard-deviation floor of `1e-10` in normalized-coordinate units, measured on each statistic's finite overlap. Unresolved cases return `NaN` with an eligibility status and the chosen floor. This is a numerical-resolution convention, not a proof that every smaller physical change is zero. `scale_floor=0` is an explicit unprotected option. Absolute metric separation remains reported.

This matters for the Clifford-reference QCA boundary paths, where nearly constant entropies must not be converted into standardized roundoff. The global point-cloud PCA is unaffected, and chronology roughness uses the same floor. Historical archived per-path minima, correlations, and fine-descriptor ranks are retained as snapshots, not certified precision estimates.

A fresh included-data analysis uses the current numerical kernels and the declared resolution floor. It is not required to reproduce all secondary v1.0.0 rank statistics exactly. Even before the floor is applied, recomputing very small or tied descriptor values can reorder them; the archived minimum per-path PCA changed from about 0.537 to 0.429 when roundoff was standardized. Neither is meaningful for those unresolved paths. Current tables expose eligibility rather than presenting such minima as scientific evidence. The frozen headline table remains historical, while current analysis tables and source provenance are written to `outputs/rebuild/`.

## Reproduction

In a fresh working copy with the documented dependencies:

```bash
make test
make public
make numerical-check
make rebuild-included
make geometry-chronology-controls
make peer-review-check
```

Full controls require a fresh output directory. Hosted checks identify the audited revision.

The [fresh-versus-historical statistics](../metadata/freeze_audit_statistics.json) record the pinned-hosted values, eligibility decisions, and source fingerprints.
