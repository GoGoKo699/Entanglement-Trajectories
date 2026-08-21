# Quantitative result: metric-robust trajectory morphology

## Result in one sentence

Across the tested pure-state dynamical families, three non-equivalent Schmidt-spectrum metric classes share a dominant common trajectory mode and preserve substantial relational morphology after exact-boundary normalization, but the preservation is hierarchical rather than exact.

## 1. A dominant common metric mode

The raw normalized metrics have a first standardized principal component explaining

\[
95.38\% 
\]

of their total variance. After every metric is placed in its exact fixed-\(\lambda_{\max}\) feasible interval, the first component still explains

\[
90.26\%,
\]

with a model-stratified design-cluster 95% sensitivity interval of approximately

\[
[86.26\%,93.41\%].
\]

Its three positive loadings are approximately

\[
(0.595,0.545,0.590)
\]

for Rényi orders \(1,2,1/2\), respectively. The leading contrast mode explains 9.31% and is dominated by the order-2 class, with loading approximately \(-0.837\). This gives the desired structure: a strong shared mode plus a real, interpretable metric contrast.

Separate fits to the 96 trajectories give a median common-mode fraction of 94.75%, with interquartile range 91.55%-96.50%. The minimum is 53.71%, occurring in a special QCA trajectory. The shared mode is therefore broad, not universal on every individual path.

### Weighting and representation sensitivity

The common-mode conclusion is not specific to one row-weighting convention. Independent sensitivity calculations give:

| Construction | First-mode variance fraction |
|---|---:|
| canonical row-weighted boundary levels | 0.9026 |
| equal total weight per trajectory | 0.9123 |
| standardize within each trajectory before pooling | 0.9186 |
| consecutive first differences | 0.8622 |

Leaving out one dynamical family at a time gives fractions from 0.8812 to 0.9111; separate size-by-size fits range from 0.8912 to 0.9514. These are sensitivity analyses of the designed dataset, not independent replications. The machine-readable values are in `metadata/common_mode_sensitivity.json`.

## 2. Within-trajectory agreement survives exact normalization

Cluster-averaged Spearman correlations are:

| Metric pair | Raw metrics | Exact-boundary coordinates | 95% interval after boundary normalization |
|---|---:|---:|---:|
| Rényi 1 vs 1/2 | 0.988 | 0.947 | 0.907-0.975 |
| Rényi 1 vs order-2 class | 0.980 | 0.759 | 0.636-0.857 |
| order-2 class vs Rényi 1/2 | 0.956 | 0.692 | 0.596-0.775 |

The hierarchy is physically sensible. Rényi orders 1 and 1/2 remain especially close, whereas the order-2 class supplies the strongest independent contrast.

## 3. The geometry among trajectories is partly preserved

Using only the metric-dependent vertical coordinate, the rank correlations between the 16-trajectory distance matrices, averaged over all six sizes, are:

| Metric pair | Mean distance-rank correlation | Minimum over sizes | Mean three-neighbor overlap |
|---|---:|---:|---:|
| Rényi 1 vs 1/2 | 0.961 | 0.931 | 0.806 |
| Rényi 1 vs order-2 class | 0.657 | 0.528 | 0.438 |
| order-2 class vs Rényi 1/2 | 0.644 | 0.550 | 0.406 |

The random expected three-neighbor overlap is 0.2. Every vertical-only distance comparison has a one-sided 1,000-permutation value no larger than 0.001.

When the common \(\lambda_{\max}\) coordinate is included, the mean distance-rank correlations rise to 0.946-0.993. Those full-path values are useful descriptions of the plotted atlas, but they must not be mistaken for wholly independent evidence because all projections share the same horizontal coordinate.

The six inter-model centroid distances are even more stable. In the vertical-only comparison, their mean rank agreement is approximately 0.77-0.98 across metric pairs; with the full path it is approximately 0.96-0.97.

## 4. Metric contradictions are real

Across 5,760 consecutive scalar steps:

| Event | Count | Fraction |
|---|---:|---:|
| consensus increase | 3,741 | 64.95% |
| consensus decrease | 1,162 | 20.17% |
| metric competition | 808 | 14.03% |
| stationary in all metrics | 49 | 0.85% |

The competition fraction is model dependent:

- QCA: 4.51%;
- kicked Ising: 9.93%;
- quantum baker: 17.15%;
- random-field XXZ: 24.51%.

The unification is therefore not numerical equivalence. It is a common dynamical organization that contains both consensus and competition.

## 5. Coarse structure persists; fine structure does not

Across metric pairs, the rank correlations of full-path arc length are 0.910-0.960. Vertical-only total-variation rankings are less stable, at 0.473-0.882, and origin-closed signed-area rankings range from 0.498 to 0.799. Exact vertical-turn counts agree for only 7.3%-20.8% of metric pairs, and all three metrics have identical turn counts on only 2 of 96 trajectories.

This is direct evidence against treating every projected path as formally topologically identical. The supported object is coarse morphology, not exact local path structure.

## Strongest defensible claim

> Across four tested dynamical families used to probe scrambling, recurrence, disorder, and spectral complexity, three non-equivalent Schmidt-spectrum metric classes share a dominant common trajectory mode and preserve substantial relational morphology after exact-boundary normalization. The preservation is hierarchical rather than exact, and local metric contradictions carry additional information. This supports an empirical metric-robust trajectory class, not a formal topological invariant.

## Scope

The result is limited to the supplied models, parameters, initial states, sizes, fixed half-chain cuts, and three independent vertical metric classes. The shared horizontal Rényi-infinity coordinate is analyzed separately. Mixed-state, multipartite, and operational entanglement notions are outside this test.
