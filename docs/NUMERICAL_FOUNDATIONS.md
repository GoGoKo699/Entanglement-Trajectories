# Numerical foundations

## Scope and status

This is an **unreleased numerical-maintenance update**, identified as
`numerical-foundations-2026-09-06`, on top of commit
`c58576bc188d603d4f6e03f4225954d3599a2d05`.

It improves finite-precision implementations of the existing mathematics. It
adds no dynamical family, new phase claim, topology theorem, or chronology-null
result. The 2024 article and the later repository evidence remain distinct.

The committed data, selected-spectrum archives, public figures, and numerical
claim records remain the preserved **v1.0.0 evidence snapshot**. The tag is not
moved. Version and citation fields still identify the existing release until a
later version is deliberately prepared. Newly generated trajectories carry an
extraction-method record and must not be passed off as the historical archive.

## 1. Fixed-largest-value spectra without remainder deletion

At fixed largest reduced eigenvalue `p`, the concentrated extremizer is

```math
\boldsymbol c(p)=(p,\ldots,p,r,0,\ldots,0),\qquad
k=\lfloor 1/p\rfloor,\qquad r=1-kp.
```

A probability tolerance must not turn a positive remainder into zero. For
`p = 1 - 1e-14` and `d = 1024`, the extremizer now retains `[p, 1-p, 0, ...]`.
The previous nearby-reciprocal rounding returned a product spectrum instead.
That discrepancy is particularly important for small positive Rényi orders,
not only for discontinuous Hartley entropy.

| Quantity at this represented input | Current value |
|---|---:|
| Concentrated rank | 2 |
| Lower Hartley entropy | 1 bit |
| Upper Hartley entropy | 10 bits |
| Lower Rényi entropy, q=0.1 | approximately 0.0625739038000 bits |
| Lower Rényi entropy, q=0.25 | approximately 0.00060807593344 bits |
| Lower Rényi entropy, q=1/2 | approximately 2.88423645e-7 bits |

The extremizer preserves the requested largest entry rather than repairing
normalization by moving that entry. Sums are one up to final floating-point
rounding. Validation tolerances still admit and clip tiny *out-of-domain*
roundoff; they do not alter an interior, valid input's support.

### Representation convention

Exactly the canonical Python float `1.0/k` denotes the reciprocal point `1/k`.
That explicitly documented convention is shared by the support-bound and
extremizer APIs. **Neighboring floats are not snapped to it.** Away from these
points, the decomposition uses the input's exact integer ratio before the
remainder is converted back to a float. This is not a symbolic-real API.

Tests cover exact reciprocals, both neighboring floats, and the near-product
counterexample, including small positive orders and normalized/unscaled
entropies. Independent 90-digit Decimal calculations are the test oracle.

## 2. Stable spectrum extraction

### One-qubit reductions

Near equal eigenvalues, extraction uses the normalized Bloch-vector length

```math
\Delta=
\frac{\sqrt{(\rho_{00}-\rho_{11})^2+4|\rho_{01}|^2}}
{\rho_{00}+\rho_{11}},\qquad
\lambda_\pm=(1\pm\Delta)/2.
```

The square root is evaluated with `hypot`. This avoids subtracting nearly
equal numbers in `sqrt(1-4*det(rho))`. Near purity, where the complementary
`1-Delta` subtraction is itself ill-conditioned, the implementation instead
uses direct SVD of the two-row coefficient matrix. The branch selects an
algorithm; it does **not** remove small singular values.

For a state with known probabilities `(0.5+1e-8, 0.5-1e-8)`, the local
verification obtains largest eigenvalue `0.50000001` with stable extraction;
the preserved determinant route returns approximately `0.5000000129047841`.

### Half-chain reductions

The default route performs SVD of the bipartite coefficient matrix directly,
without first forming `M @ M.conj().T`. The squares of the singular values are
the reduced spectrum. Pure-state logarithmic negativity can be computed from
the unsquared values:

```math
E_N=2\log_2\sum_i s_i.
```

The API distinguishes the inputs explicitly:

```python
from entanglement_trajectories import (
    half_chain_schmidt_coefficients,
    log_negativity_from_schmidt_coefficients,
)

s = half_chain_schmidt_coefficients(psi, n)  # unsquared, normalized coefficients
value = log_negativity_from_schmidt_coefficients(s, normalized=True)
```

For the tested `n=14` product state, normalized half-chain log-negativity falls
from approximately `1.60e-7` with the historical Gram-matrix route to
approximately `2.72e-16` with direct SVD. These are measured local values, not
promised identical last bits on every backend.

No spectral cutoff is introduced. SVD does not certify the algebraic Schmidt
rank of a floating-point state. `schmidt_rank` and `hartley_entropy` continue
to describe strictly positive *represented* entries; thresholded rank is a
separately declared diagnostic. Direct SVD may change runtime constants at
large sizes, although it does not change the intended state evolution.

NumPy documents that its SVD uses LAPACK and that reduced-matrix eigenvalues
are the squares of the singular values:
[NumPy SVD documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html).

## 3. Stable entropy arithmetic

Positive-order Rényi evaluation retains small tail sums using `log1p` and
handles orders near one using `expm1`, rather than silently replacing nearby
orders by q=1. High-order effective rank is evaluated through log entropy to
avoid underflow of the moment sum. Linear entropy is computed from
cross-weights, avoiding subtraction of two nearly equal values near a product
state. I-tangle and I-concurrence reuse that linear-entropy evaluation.

These are the same mathematical observables. Their numerical-accuracy targets
are defined by known states and independent oracles, not by historical
roundoff artifacts.

## 4. Input-error screening for boundary-relative heights

The algebraic coordinate

```math
r_E=\frac{E-E_{\min}(p)}{E_{\max}(p)-E_{\min}(p)}
```

can be poorly conditioned even when its denominator is nonzero. The ordinary
`relative_boundary_height` remains a point evaluation. For uncertain inputs,
use the separate screening API:

```python
from entanglement_trajectories import assess_boundary_height

assessment = assess_boundary_height(
    "logneg", p, measured_value, d,
    normalized_metric=True,
    p_error=5e-13,
    value_error=2e-7,
    boundary_error=1e-13,
    max_height_error=0.01,
)
height = assessment.usable_height  # NaN when unresolved
```

The supplied numbers are **explicit error allowances**, not automatically
estimated uncertainties. The implementation encloses numerator and denominator
ranges using monotonic extremal envelopes. If the denominator's range includes
zero, it refuses to certify a usable coordinate. Otherwise it compares a
conservative interval with the requested height-error budget. It does not
assume Gaussian errors or a particular correlation between p and E.

This is conditional numerical screening, not a statistical confidence interval
or a rigorous floating-point interval-arithmetic proof. It does not change raw
metrics, edit spectra, clip heights, or silently replace the archived analysis
masks.

Under the allowances recorded in `metadata/numerical_foundations_summary.json`,
59 previously finite log-negativity heights are unresolved near collapsed
envelopes. Those rows were already incomplete in the three-coordinate PCA
because their von Neumann/linear coordinates were undefined. The complete-row
count therefore remains 5,657 and the global PCA is unchanged by this extra
screening. Other scientifically justified error budgets may give different
screening counts.

## 5. Accuracy, compatibility, and preserved results

There are two explicit extraction modes:

| Mode | Purpose |
|---|---|
| `stable` (default) | New calculations with the improved numerical kernels |
| `release-v1` | Reproduce the old determinant/Gram extraction for historical snapshot comparison |

`release-v1` preserves the old extraction algorithms, not a second copy of
all historical software. The immutable tag is the full old implementation.
Existing archived-regression tolerances have not been widened. The quick
regression script was synchronized with the already declared CI tolerances.

The fixed-p boundary sensitivity check holds all **5,856 archived scalar
observations fixed** and changes only boundary evaluation:

| Evaluation | First-component variance fraction |
|---|---:|
| Preserved release summary | 0.9026282298671149 |
| Current float implementation | 0.9026282301130131 |
| Independent 70-digit formulas | 0.9026282301130129 |

The current float result differs from the independent calculation by about
`2.22e-16` and from the old summary by about `2.46e-10`. The 90.26% headline
survives this boundary-layer check. This is not a full replacement of the
archived state-vector data or a recomputation of every bootstrap table.

All 16 n=10 trajectories, totaling 656 observations, were regenerated with
both extraction modes. Ordinary half-chain entropy and largest-eigenvalue
coordinates agree at approximately machine precision. Differences of order
`1e-8` remain in the historical noisy geometric/log-negativity coordinates;
they are separately tabulated rather than hidden by changing an accuracy
target. Analytical tests establish the improvement at the sensitive states.

The global PCA is still a point-cloud statistic. This maintenance result is
not additional evidence for time-order-dependent morphology.

The Figure 2 logarithmic sampling grid is now constructed in base two so
its analytically exact power-of-two reciprocal knots remain exact. This fixes
a plotting-grid rounding artifact rather than snapping user-supplied spectra;
the public-data comparator retains its original tolerances.

## Freeze-audit API domain

The entropy and entanglement-energy APIs use finite logarithm bases greater than one, so their stated ranges and Schur directions remain valid. Fixed-p bounds validate a positive integer dimension before coercion. XXZ simulation rejects noninteger or nonpositive substep counts and nonpositive or nonfinite record intervals. Normalized support/effective-rank coordinates are zero in a one-dimensional Hilbert space; their unnormalized value remains one.

The entanglement-Hamiltonian gap is evaluated as a difference of logarithms rather than a potentially overflowing ratio. A strictly positive represented second eigenvalue therefore has a finite logarithmic gap, even when the ratio exceeds floating-point range. Exact zero still gives infinity.

These repairs do not change the supplied trajectories or the three metrics used in the control study. Extremely small positive Renyi orders remain sensitive to input rounding: separately rounded weights and a rounded largest eigenvalue can produce differences near a collapsed envelope. The input-error assessment, rather than a claim of arbitrary relative accuracy, governs that case.

## Numerically constant paths and historical summaries

Standardizing a coordinate whose variation is only numerical noise can produce arbitrary PCA fractions and rank correlations. Current per-trajectory PCA and half-chain within-trajectory Spearman calculations therefore declare a standard-deviation floor of `1e-10` in normalized-coordinate units, measured on each statistic's finite overlap. Unresolved cases return `NaN` with an eligibility status and the chosen floor. This is a numerical-resolution convention, not a proof that every smaller physical change is zero. `scale_floor=0` is an explicit unprotected option. Absolute metric separation remains reported.

This matters for the Clifford-reference QCA boundary paths, where nearly constant entropies must not be converted into standardized roundoff. The global point-cloud PCA and the later chronology controls are unaffected by this change. The chronology roughness already used this floor. Historical archived per-path minima, correlations, and fine-descriptor ranks are retained as snapshots, not certified precision estimates.

A fresh included-data analysis uses the current numerical kernels and the declared resolution floor. It is not required to reproduce all secondary v1.0.0 rank statistics exactly. Even before the floor is applied, recomputing very small or tied descriptor values can reorder them; the archived minimum per-path PCA changed from about 0.537 to 0.429 when roundoff was standardized. Neither is meaningful for those unresolved paths. Current tables expose eligibility rather than presenting such minima as scientific evidence. The frozen headline table remains historical, while current analysis tables and source provenance are written to `outputs/rebuild/`.

## 6. Reproduction

```bash
make test
make numerical-check
make public-context public-figures
python scripts/compare_public_figure_data.py \
  --reference figures/public/data \
  --candidate outputs/public_figures/data \
  --atol 1e-10 --rtol 1e-10
make public-validate peer-review-check
```

`make numerical-check` writes the independent boundary comparison, input-error
screening table, stable and historical n=10 trajectories, and their comparison
to `outputs/numerical_foundations/`. It checks that curated data and figures
were not modified. `--skip-n10` omits only the trajectory regeneration.

The suite has 79 existing cases plus 85 new parameterized numerical cases.
The oracle tests use the standard library; no new release dependency or
workflow permission is required. The pinned hosted environment is retained.

The maintenance verification was run locally on CPython 3.13.5, NumPy 2.3.5,
and pandas 2.2.3. The new uploaded commit still needs its own successful locked
GitHub Actions run. A previous commit's green status does not validate it.

The complete n=20 simulation, all 72 XXZ refinement trajectories, the full
3,000/1,000 resampling analysis, chronology-shuffled controls, and conditional
static-spectrum controls were **not** repeated in this checkpoint. They are
not required to establish the analytical kernel corrections, and they are not
represented here as having been performed.
