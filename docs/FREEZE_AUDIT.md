# Frozen-scope audit: September 2026

## Decision and scope

The repository is suitable to freeze as a corrected computational companion and a finite designed-data follow-up, after the checks on the final merged commit pass. Existing release tags are not moved. This is an AI-assisted numerical and consistency audit, not independent journal peer review and not a proof that undiscovered defects are impossible.

The audit starts from commit `88d8e420ee292359cb5fb6c10869534c9e59cb03`. A bounded API and interpretation patch closes the findings below. No new physical model, new ensemble claim, or stronger topology claim is introduced.

## Repairs

- Fixed-p boundary routines validate the dimension before integer coercion and reject booleans and fractional dimensions.
- Entropy and entanglement-energy units require finite logarithm bases greater than one.
- The entanglement-Hamiltonian gap uses a difference of logarithms. A strictly positive second eigenvalue no longer becomes an infinite gap through an intermediate ratio overflow.
- Normalized support and effective-rank coordinates are zero in the one-dimensional space, consistently with the exact boundary API; raw ranks remain one.
- XXZ substep counts must be positive integers. Record intervals must be finite and positive. Negative counts can no longer silently produce an empty evolution loop.
- The primary claim registry and scientific entry documents now include the geometry-versus-chronology controls and their negative results. Historical numerical snapshots remain explicitly identified as such.

Thirty regression cases cover these API findings. None changes a declared physical run or the three metric coordinates used by the control study. The control archive is regenerated from the hardened source, rather than assigning new implementation hashes to old output tables.

## Checks and independent probes

The standard suite contains 233 cases after this patch. The audit additionally runs the public-figure rebuild and numerical source comparison, the paper-correction checks, the numerical-foundations command, the full included-data analysis with its default 3,000 bootstrap and 1,000 permutation settings, and the full geometry/chronology study with 999 chronology draws and 199 draws for each matched-spectrum law.

Independent local probes supplement those workflows: 585 high-precision entropy cases; 500 random spectra with 5,000 metric-envelope comparisons; 36 analytical Schmidt-state constructions; direct partial-transpose checks; 32 independently assembled small-system step operators covering all 16 model conditions at n=4 and n=5; exact-matrix-exponential XXZ refinement and magnetization checks; independent Marchenko-Pastur quadrature and Page means; and all 16,200 distinct pairs in the selected-spectrum archive. Scripts and detailed measurements are retained in the companion freeze-audit evidence package.

The random-spectrum test distinguishes exact identities from rounded input contracts. Two naive fixed-float-p comparisons at very small positive Renyi order differ by several parts in 10^9 near a collapsed two-level envelope. Their separately rounded input components imply a largest-value uncertainty below one floating-point step; the discrepancies are enclosed by the explicit input-rounding allowance. This is not evidence of a majorization violation or a claim of arbitrary relative accuracy. The naive discrepancies remain in the audit record.

## What is and is not established

The common spectrum and majorization geometry remain the mathematical framework. The approximately 90.26% point-cloud mode is descriptive, not an order-sensitive test. Chronological smoothness and excess local metric competition survive the specified reorderings. Constructed matched spectra can have stronger common-mode fractions; chronology does not improve path-distance agreement uniformly. These limits are part of the result, not exceptions to hide.

The full n=20 physical simulation suite and the complete large-system XXZ convergence production are not regenerated in this freeze audit. Included archives, reproduction paths, independent small-system operators, and contained reruns are checked. Historical one-substep XXZ rows remain circuits, not convergence-controlled continuous-time Hamiltonian trajectories. The pinned package set is a declared reproducibility environment, not a bitwise-frozen operating-system image.

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

Full controls require a fresh output directory. The hosted pull-request and post-merge checks identify the exact audited revision. No new release is implied by this document; version/tag metadata should be updated coherently only when a new release is intentionally created.
