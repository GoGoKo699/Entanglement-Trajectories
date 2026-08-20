# Quantitative Analysis Methods

## Purpose

The quantitative analysis asks a deliberately limited question:

> Which properties of the entanglement trajectory survive when the vertical entanglement coordinate is replaced by another non-equivalent function of the same Schmidt spectrum?

The analysis is not designed to prove a formal topological invariant. It tests an empirical **metric-robust trajectory class** and records where the proposed unification fails.

## Data scope

The scalar trajectory table contains 5,856 observations from 96 trajectories:

- four dynamical families;
- four conditions per family;
- six even system sizes, from 10 to 20 qubits;
- one balanced half-chain spectrum per observation.

Five selected 20-qubit reruns additionally contain 405 complete Schmidt spectra, giving 400 consecutive full-spectrum transitions. These five runs are useful for the majorization audit but are not a representative model sample.

## Independent metric classes

The vertical coordinates represent three non-equivalent Rényi-order classes:

| Column | Interpretation | Spectral sensitivity |
|---|---|---|
| `half_logneg` | pure-state logarithmic negativity, equivalent to Rényi order 1/2 | tail sensitive |
| `half_vn` | von Neumann entropy, Rényi order 1 | bulk weighted |
| `half_linear` | normalized linear entropy, in the purity/Rényi-order-2 equivalence class | head weighted |

The shared horizontal coordinate is `half_lambda_max`, equivalent to the Rényi-order-infinity or bipartite geometric class. Strictly monotone aliases are not counted as independent metric evidence.

## Exact-boundary coordinates

For each metric \(E\), system dimension \(d\), and largest Schmidt value \(p\), the analysis evaluates the exact finite-dimensional lower and upper bounds directly at \(p\). The relative coordinate is

\[
r_E=\frac{E-E_{\min}(p;d)}{E_{\max}(p;d)-E_{\min}(p;d)}.
\]

It is recorded as undefined where the feasible interval collapses. No finite plotting grid is used for quantitative normalization.

## Common metric mode

The three metric coordinates are standardized and decomposed by singular-value decomposition. The first component is oriented with positive loadings and interpreted as a shared metric mode. The second component is oriented so that the order-2 loading is negative, exposing the principal metric contrast.

Two checks are reported:

1. one global decomposition over all finite observations;
2. separate decompositions for each of the 96 trajectories.

A cluster bootstrap resamples the 16 model-condition units while keeping all six sizes of each unit together. This avoids treating every time sample as an independent experimental replicate.

## Within-trajectory robustness

For each physical trajectory and each metric pair, the analysis reports:

- Spearman time-order correlation in the raw normalized metrics;
- Spearman correlation after exact-boundary normalization;
- boundary-coordinate root-mean-square separation;
- boundary-coordinate mean absolute separation.

The reported confidence intervals use the same 16 model-condition clusters.

## Relational trajectory geometry

Every trajectory is interpolated on the common grid

\[
\tau=0,0.1,\ldots,4.0.
\]

For each size and metric, a distance matrix is constructed among all 16 trajectories using root-mean-square distance over finite common coordinates. Metric pairs are compared through:

- Spearman and Pearson agreement of all 120 pair distances;
- overlap of each trajectory's three nearest neighbors;
- a one-sided label-permutation, Mantel-like rank test.

Two representations are kept separate:

- **vertical-only:** compares only the metric-dependent coordinate and is the nontrivial test;
- **full path:** compares \((\lambda_{\max},r_E)\) and therefore includes the shared horizontal coordinate.

The same analysis is repeated for four model-centroid paths, yielding six inter-model distances at each size.

## Generalization stress tests

A transparent nearest-centroid classifier is used only as a stress test, not as an optimized machine-learning claim. It is evaluated under:

- leave-one-size-out model-centroid testing;
- leave-one-size-out individual-trajectory testing;
- leave-one-condition-out testing;
- simultaneous held-out size and condition.

Training and testing metrics are varied independently. Endpoint-only, vertical-only, and full-path representations are retained. A `lambda_max`-only classifier supplies the necessary baseline.

## Metric-consensus and metric-competitive motion

For every consecutive scalar observation, the signs of the changes in the three independent metric classes are classified as:

- consensus increase;
- consensus decrease;
- metric competition;
- stationary in all three metrics.

The numerical direction tolerance is \(10^{-10}\).

## Full-spectrum majorization audit

For each selected consecutive spectrum pair, the code tests whether the first spectrum majorizes the second, the reverse relation holds, they are equivalent, or they are incomparable. The canonical numerical tolerance is \(10^{-10}\), with a sensitivity table from \(10^{-12}\) to \(10^{-6}\).

A majorization-compatible forward increase means that the earlier spectrum majorizes the later one, so every Schur-concave entropy must increase. A metric contradiction on such a transition would indicate either a software error or a tolerance problem.

## Fine-structure limits

Three simple path descriptors are compared across metrics:

- arc length;
- signed polygonal area;
- exact count of vertical-direction reversals.

The first two are coarse geometric summaries. Exact turn count is intentionally sensitive and is used to show that local trajectory structure is not invariant.

## Reproduction

Run:

```bash
make metric-robustness
```

or:

```bash
python analysis/analyze_metric_robustness.py
```

The default source tables are written under `outputs/metric_robustness/results/`; PDF and PNG figures are written under `outputs/metric_robustness/figures/`. The `make rebuild-included` workflow instead places them under `outputs/rebuild/`.
