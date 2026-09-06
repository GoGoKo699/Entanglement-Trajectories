# Spectral geometry versus temporal order

## Result in one paragraph

The three entanglement coordinates share a strong instantaneous component, but **its size is not evidence of temporal organization by itself**. Jointly reordering each trajectory preserves its approximately 90.26% common-mode variance exactly. Four explicitly constructed, dimension- and largest-eigenvalue-matched static references produce still larger fractions, approximately 97.50% to 97.89%. In contrast, the observed chronological paths are substantially smoother and have more locally competing raw entanglement increments than their reordered counterparts. The useful distinction is therefore **a common spectral description, temporal smoothness, and informative local disagreement**, not a new universal dynamical invariant established by a large principal component.

This is a supplementary controlled analysis of the repository data, not a result demonstrated in the 2024 article. The released datasets, figures, numerical summaries, and `v1.0.0` tag are not replaced.

## Data and computation

The main input is `data/trajectory_observations.csv`: 96 designed trajectories, 5,856 observations, four dynamical families, and six sizes from 10 to 20 qubits. The vertical coordinates are normalized von Neumann entropy, normalized linear entropy, and pure-state logarithmic negativity. Boundary heights use the repaired numerical implementation, not the former remainder-snapping algorithm.

All three boundary heights are usable under the declared width cutoff at 5,657 rows. There are 5,512 adjacent complete-case edges on the original recording grids. No missing interval is interpolated or bridged. The raw-metric competition calculation separately uses all 5,760 recorded transitions.

The script runs 999 permutations for each primary chronological comparison and 199 complete realizations for each of four static reference generators. It also checks a late window, a stricter width cutoff, all-pair majorization on the selected spectra, and newly regenerated stable-extraction trajectories at n=10. The protocol is recorded before each production run. This is an exploratory follow-up with implementation smoke tests, not an externally preregistered experiment.

Detailed results and provenance are in [`../metadata/geometry_chronology_controls.json`](../metadata/geometry_chronology_controls.json). The full draw-level output tables are in [`../data/geometry_chronology_controls.zip`](../data/geometry_chronology_controls.zip).

## 1. What the chronology shuffles preserve

Within each trajectory, all metrics, the largest eigenvalue, and the corresponding bounds move together. A metric column is **never shuffled independently**: that would generally destroy the relationship between the metrics and a common physical spectrum.

Rows without a complete set of boundary heights remain at their original positions. Eligible rows are jointly permuted among the remaining slots. Thus the instantaneous tuples, trajectory membership, missing-value mask, number of usable edges, and global point-cloud statistics are preserved.

Three policies are reported:

- **Joint shuffle:** randomize all eligible temporal positions within each path.
- **Fixed-endpoint shuffle:** additionally preserve the first and last eligible row of each path.
- **Within-window shuffle:** randomize only within half-unit intervals of scaled iteration, using `floor(2*step/n)`. This preserves the coarse temporal envelope more closely. It is not a stationary block bootstrap.

The reference asks what changes when temporal order is removed under those specific constraints. It is not a simulation of another local Hamiltonian, and rejection is not proof of chaos or nonlinear dynamics. This separation between a specified surrogate and the property actually tested follows the surrogate-data methodology of Theiler et al. [1].

## 2. Common-mode variance is an instantaneous statistic

Let X contain the complete metric tuples. Reordering rows with a permutation P leaves the centered covariance unchanged because `(PX)^T(PX) = X^T X`; standardization is unchanged as well. The principal-component fractions therefore cannot depend on the visitation order of the point cloud.

| Statistic | Chronological data | Joint-shuffle mean | Central 95% of shuffle values |
|---|---:|---:|---:|
| Boundary-height level PC1 fraction | 0.902628 | 0.902628 | Identical apart from roundoff |
| Boundary-height increment PC1 fraction | 0.862160 | 0.908347 | 0.905679 to 0.910860 |

The approximately 86.22% increment result is order-sensitive, but it is **lower**, not higher, than the unrestricted shuffled reference. After retaining only `tau >= 1`, the increment fraction is 0.861104, within the corresponding shuffled range 0.854032 to 0.865022. Thus the original high increment fraction does not independently establish unusually strong chronological metric consensus.

This does not make the observed common component false. It changes what can be inferred from it.

## 3. Temporal smoothness and metric competition survive the controls

### Temporal roughness

For each nonconstant trajectory, each boundary-height coordinate is standardized using its own complete rows. Roughness is the mean squared adjacent standardized increment, averaged first over the three coordinates and then equally over eligible trajectories. Only originally adjacent complete rows contribute.

Six `QCA_1` paths have effectively constant boundary heights and are omitted from this standardization; the remaining 90 paths contribute. They are retained in statistics that do not divide by a trajectory-specific standard deviation. The exact omission rule is a standard-deviation floor of `1e-10`, not a result-selected model exclusion.

For a joint shuffle of F eligible rows, the exact expected roughness of each unit-population-variance coordinate is `2F/(F-1)`. Averaging those exact expectations gives 2.035954. The Monte Carlo mean is 2.034616, consistent with sampling variation.

| Chronology comparison | Observed roughness | Reference mean | Central 95% reference range |
|---|---:|---:|---:|
| Joint shuffle | 0.171083 | 2.034616 | 1.982565 to 2.086522 |
| First/last eligible rows fixed | 0.171083 | 1.807163 | 1.760183 to 1.854695 |
| Within half-unit iteration windows | 0.171083 | 0.542186 | 0.516920 to 0.567854 |
| Late window, `tau >= 1` | 0.429065 | 2.046863 | 1.988704 to 2.101283 |

The direction holds in every family: observed mean roughness is approximately 0.1995 for kicked Ising, 0.1254 for QCA, 0.1712 for the quantum baker, and 0.1769 for the XXZ-derived circuits, versus exact joint-shuffle expectations close to 2.036. These results establish smoothness relative to the stated reorderings, not a unique fingerprint of quantum chaos.

### Raw metric competition

Competition means at least one raw normalized entanglement metric increases and another decreases beyond the stated sign tolerance. **Boundary-height changes are not used for this majorization-related interpretation**, because boundary heights are not themselves Schur-concave entanglement monotones when p varies.

| Comparison | Observed competition rate | Reference mean | Central 95% reference range |
|---|---:|---:|---:|
| Joint shuffle | 14.03% | 5.68% | 5.14% to 6.20% |
| First/last eligible rows fixed | 14.03% | 5.79% | 5.28% to 6.35% |
| Within half-unit iteration windows | 14.03% | 11.06% | 10.45% to 11.67% |
| Late window, `tau >= 1` | 15.60% | 7.02% | 6.32% to 7.69% |

An independent exact all-pair calculation, accounting for frozen endpoints, gives a joint-shuffle expectation of 5.685%. The excess of chronological competition is therefore not a Monte Carlo implementation artifact. Family-resolved expectations and a sign-tolerance sweep from `1e-12` through `1e-7` are recorded in the output.

A useful reading is that nearby chronological spectra encounter metric-sensitive redistributions more often than random pairs drawn from the same trajectory. That is not equivalent to identifying a unique microscopic dynamical cause.

### Relational path geometry

Vertical-only RMS path distances are compared across metrics on the original grids, separately within each size. The average distance-rank agreement is 0.751632, compared with 0.650883 under joint shuffling. Most of that difference disappears when the coarse time envelope is preserved: the within-window reference mean is 0.743144.

This is a new native-grid control, not a replacement for the release's 41-point interpolated analysis. It is also not uniform across sizes: on the stable n=10 rerun, the observed boundary-height distance agreement is 0.764993 versus a joint-shuffle mean of 0.787679. No universal chronology-enhanced classifier claim follows.

## 4. Static references matched at each (d,p)

At each original recording point, keep the ambient Schmidt dimension d and the largest weight p. Replace the other eigenvalues independently of other times. All three metrics are recomputed from the **same** replacement spectrum.

Three generators start with independent positive gamma weights of shape alpha, with `alpha = 0.25, 1, 4`. A positive scale c is chosen so that the remaining entries satisfy

```math
\lambda_{j+1}=\min\{p,cw_j\},\qquad
\sum_{j=1}^{d-1}\lambda_{j+1}=1-p.
```

An active-set water-filling calculation enforces the constraint. These distributions are pushforwards of gamma weights. They are **not conditional Dirichlet distributions**, not Haar/Wishart ensembles, and not uniform samples of the capped simplex. They can place probability mass on faces where further entries equal p.

The fourth reference samples a uniform mixture parameter on the line segment between the equal-tail and concentrated fixed-p extremizers. It deliberately samples a one-dimensional subset, not the entire feasible region.

| Static reference | Mean boundary-height level PC1 | Central 95% realization range |
|---|---:|---:|
| Capped gamma, alpha=0.25 | 0.978359 | 0.977728 to 0.978932 |
| Capped gamma, alpha=1 | 0.978701 | 0.977786 to 0.979485 |
| Capped gamma, alpha=4 | 0.978887 | 0.977989 to 0.979708 |
| Extremizer-segment mixture | 0.974957 | 0.973918 to 0.976102 |
| **Observed dynamical data** | **0.902628** | Not a reference ensemble |

These results are constructive counterexamples to using high common-mode variance alone as evidence of special dynamical organization. They **do not prove that spectral geometry forces a 90% common mode** or quantify a percentage of variance caused by dynamics. The reference generators and the empirical (d,p) distribution both matter; the original p(t) path is retained.

The raw competition rate likewise depends on the reference law: mean rates range from approximately 8.51% to 18.59%, bracketing the observed 14.03%. Consequently, 14.03% by itself is not an identifying dynamical signature.

No energy constraint, locality constraint, conserved sector, Schmidt-rank profile, purity, or full spectral density is matched. Every generated probability spectrum is admissible for some bipartite pure state of the declared dimensions, but successive draws need not follow any of the studied physical update rules.

## 5. Full-spectrum majorization control

The five selected n=20 runs contain 405 spectra and 400 adjacent transitions. Their chronological ordering gives 280 incomparable transitions and 50 competition events. Joint reordering of each full spectrum sequence gives mean counts of approximately 118.4 and 8.71, respectively; the central 95% ranges are 106 to 132 and 4 to 14.

No competition event occurs outside the incomparable sector in either ordering. All 16,200 distinct within-run spectrum pairs were also checked at the declared tolerances. This illustrates why the zero-violation result is fundamentally a spectral-order consistency check: Schur-concavity and majorization apply to pairs regardless of their chronological order [3]. Temporal order changes which pairs are encountered and how frequently, not the theorem itself.

The selected five runs remain a limited audit sample. They do not become representative of every family or condition through permutation.

## 6. Numerical sensitivity and inferential scope

Using a stricter minimum boundary width of `1e-6` retains 5,645 complete rows. The observed common-mode fraction becomes 0.902045, and the qualitative roughness, competition, and increment comparisons remain unchanged.

The stable-extraction n=10 trajectories were regenerated, not inferred by relabeling the old CSV. Their observed statistics agree closely with the archived n=10 subset: for example, boundary increment PC1 changes by about `5e-9`, while raw competition remains 96 of 640 transitions. This checks numerical containment at n=10, not a full stable-extraction rerun through n=20.

Reported reference ranges are central 95% intervals **of the explicitly generated surrogate values**, not population confidence intervals. Directional tail fractions use `(1 + exceedances)/(1 + draws)` [2]. Values at the simulation floor, such as 0.001 for 999 shuffles, do not mean zero probability or a posterior probability that the proposed physical interpretation is true. The secondary statistics are exploratory; no claim is based on unadjusted threshold crossing in one selected statistic.

## Reproduce

```bash
make geometry-chronology-controls
```

Equivalently:

```bash
python analysis/run_geometry_chronology_controls.py \
  --permutations 999 --reference-draws 199 --seed 20260906 \
  --output-dir outputs/geometry_chronology
```

Use a new output directory for a rerun. The script refuses to overwrite completed results or curated input directories. It writes the protocol, full draw-level tables, analytical expectations, a stable n=10 rerun, input and implementation hashes, and the machine-readable summary. The automated test suite checks tuple preservation, unchanged masks, analytical permutation expectations, feasible spectra, independent metric agreement, and archive consistency. It does not require a particular scientifically favorable outcome.

## References

[1] J. Theiler, S. Eubank, A. Longtin, B. Galdrikian, and J. D. Farmer, “Testing for nonlinearity in time series: the method of surrogate data,” *Physica D* 58, 77–94 (1992). DOI: [10.1016/0167-2789(92)90102-S](https://doi.org/10.1016/0167-2789(92)90102-S).

[2] B. Phipson and G. K. Smyth, “Permutation P-values Should Never Be Zero: Calculating Exact P-values When Permutations Are Randomly Drawn,” *Statistical Applications in Genetics and Molecular Biology* 9, Article 39 (2010). DOI: [10.2202/1544-6115.1585](https://doi.org/10.2202/1544-6115.1585).

[3] M. A. Nielsen, “Conditions for a Class of Entanglement Transformations,” *Physical Review Letters* 83, 436–439 (1999). DOI: [10.1103/PhysRevLett.83.436](https://doi.org/10.1103/PhysRevLett.83.436).
