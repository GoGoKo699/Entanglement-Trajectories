# Results at a Glance

## One-sentence conclusion

Across the tested pure-state quantum-chaos families, several non-equivalent Schmidt-spectrum metrics share a dominant exact-boundary-normalized trajectory mode, while localized disagreements occur on majorization-incomparable spectral redistributions. The result supports an empirical **metric-robust trajectory class**, not exact invariance or a universal fingerprint.

## Scope of the controlled test

| Component | Included scope |
|---|---|
| Model families | brickwork Floquet QCA, open-chain kicked Ising, Balazs–Voros-style quantum baker, random-field XXZ |
| Conditions | four declared runs per model family |
| Sizes | $n=10,12,14,16,18,20$ |
| Scalar trajectories | 96 |
| Scalar observations | 5,856 |
| Non-equivalent vertical metric classes | Rényi $q=\tfrac12$, $q=1$, and $q=2$ class |
| Shared horizontal coordinate | $\lambda_{\max}$, equivalent to min-entropy/geometric coordinates |
| Selected complete-spectrum runs | 5 at $n=20$ |
| Selected complete-spectrum transitions | 400 |

## Main numbers

### Shared normalized mode

The first standardized common mode of the three boundary-relative vertical metrics explains

$$
90.26\%
$$

of total variance, with a run-cluster bootstrap 95% interval of

$$
85.74\%\text{–}93.79\%.
$$

The median common-mode fraction computed separately for each trajectory is 94.75%.

### Pairwise trajectory agreement

Mean within-trajectory Spearman correlations after exact-boundary normalization are:

| Pair | Mean $\rho$ |
|---|---:|
| von Neumann vs pure-state log-negativity | 0.947 |
| von Neumann vs order-2 class | 0.759 |
| order-2 class vs pure-state log-negativity | 0.692 |

The hierarchy is scientifically meaningful. The order-2 class responds more strongly to the head of the spectrum and contributes most of the principal contrast mode.

### Relational geometry

When only the metric-dependent vertical coordinates are used, pairwise trajectory-distance rankings remain correlated across metrics with mean Spearman values from 0.644 to 0.961. The strongest preservation is between the order-1 and order-1/2 lenses.

### Metric competition

Across 5,760 consecutive scalar steps:

| Event | Count | Fraction |
|---|---:|---:|
| consensus increase | 3,741 | 64.95% |
| consensus decrease | 1,162 | 20.17% |
| metric competition | 808 | 14.03% |
| stationary in all tested metrics | 49 | 0.85% |

Competition is model dependent:

| Model family | Competition fraction |
|---|---:|
| QCA | 4.51% |
| kicked Ising | 9.93% |
| quantum baker | 17.15% |
| random-field XXZ | 24.51% |

### Majorization mechanism

Among the 400 selected full-spectrum transitions:

| Majorization relation | Count |
|---|---:|
| compatible entanglement increase | 111 |
| compatible entanglement decrease | 9 |
| incomparable | 280 |

All 50 observed metric-competition events occur in the incomparable sector. None occurs on a majorization-compatible transition. Incomparability permits but does not force competition: 230 incomparable transitions still show consensus.

### Coarse morphology versus fine projected structure

Arc-length rankings remain highly stable across metrics, with correlations of 0.906–0.960. Exact turn counts agree for all three tested vertical metrics on only 2 of 96 trajectories. Thus, coarse path class is robust while fine projected topology is not.

### Fingerprint stress tests

| Classification target and holdout | Accuracy |
|---|---:|
| model centroid, same metric, held-out size | 0.917 |
| model centroid, cross metric, held-out size | 0.694 |
| individual path, same metric, held-out size | 0.521 |
| individual path, same metric, size and condition held out | 0.368 |
| $\lambda_{\max}$ path baseline, size and condition held out | 0.417 |
| chance | 0.250 |

The model-family morphology claim is stronger than the individual-fingerprint claim. Under the strictest holdout, the current atlas does not outperform the shared $\lambda_{\max}$ path baseline.

## Correct interpretation

Supported:

> The tested metric projections share a dominant coarse mode, preserve substantial relational morphology, and exhibit interpretable disagreements tied to majorization incomparability.

Not supported:

> All entanglement metrics are equivalent, a formal topological invariant has been proved, or every individual dynamical run can be identified from its trajectory.

## Sources

- machine-readable summary: `data/public_analysis_inputs.zip` (member `metric_robustness_scientific_summary.json`)
- regenerated analysis tables: `outputs/metric_robustness/results/` or `outputs/rebuild/results/`
- public source tables: `outputs/public_figures/data/`
- analysis methods: [ANALYSIS_METHODS.md](ANALYSIS_METHODS.md)
