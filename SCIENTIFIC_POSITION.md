# Scientific Position

## Governing philosophy

There are many useful scalar measures of entanglement because a Schmidt spectrum contains more information than one number can retain. The common Schmidt spectrum explains both agreement and disagreement among those measures.

For a fixed bipartition of a pure state, that common object is the ordered Schmidt-spectrum path

\[
\Gamma:t\longmapsto \boldsymbol{\lambda}(t)
=\bigl(\lambda_1(t),\ldots,\lambda_d(t)\bigr).
\]

A spectrum-based entanglement measure \(E\) produces a projected trajectory

\[
\Gamma_E(t)=\bigl(\lambda_{\max}(t),E[\boldsymbol{\lambda}(t)]\bigr).
\]

The family of these projections is the **entanglement-trajectory atlas**.

> The Schmidt spectrum is the state variable; entanglement measures are observables on it; the trajectory atlas records what survives and what changes between those observables.

## Central claim

Standard bipartite pure-state entanglement measures are nonlinear projections of a common Schmidt-spectrum path. Across four tested dynamical families used to probe scrambling, recurrence, disorder, and spectral complexity, three non-equivalent metric classes share a dominant instantaneous common mode and substantial descriptive cross-metric morphology after exact-boundary normalization. The chronology controls separate this point-cloud agreement from temporal organization: the observed paths are smoother and contain more local raw-metric disagreements than the specified reorderings, but unusually high common-mode variance is not a dynamical discriminator. The preservation is hierarchical rather than exact, and local metric contradictions reveal internal spectral redistribution that no single scalar measure captures.

This claim has three distinct parts:

1. **Exact common origin.** The fixed-cut measures considered here are functions of the same spectrum.
2. **Empirical robustness.** Coarse trajectory morphology and the relative geometry among tested model families persist across several metric projections.
3. **Permitted disagreement.** Schur-concave metrics can contradict one another locally only when the spectrum pair is incomparable by majorization (subject to the declared numerical tolerances). Incomparability permits, but does not require, disagreement.

## Chronology controls

The historical common-mode percentage and classifier results remain descriptive evidence, not proofs of special temporal structure. Joint reordering preserves point-cloud PCA exactly; four constructed fixed-(d,p) references exhibit still higher agreement. Temporal smoothness and excess local metric competition survive the stated controls. The path-distance benefit is not uniform across sizes or order-preserving surrogates. See [geometry versus chronology](docs/GEOMETRY_VS_CHRONOLOGY.md) for the full comparison, including negative controls and limitations. These findings belong to the repository follow-up; the 2024 article introduced the trajectory representation.

## Quantitative evidence

The follow-up dataset supports the following results:

- the exact-boundary-normalized common metric mode explains 90.26% of total variance;
- the median separate-trajectory common-mode fraction is 94.75%;
- within-trajectory boundary-coordinate rank agreement ranges from 0.692 to 0.947 across the three independent metric pairs;
- vertical-only trajectory-space distance rankings are preserved with mean correlations from 0.643 to 0.961;
- metric competition occurs on 14.03% of scalar transitions and is strongly model dependent;
- all 50 metric-competition events in the selected full-spectrum audit occur on majorization-incomparable transitions;
- model-centroid morphology generalizes more strongly than unseen individual paths;
- exact local turn counts are not invariant.

These results support the phrase **metric-robust trajectory class**. They do not support a formal topological invariant, exact metric equivalence, or a universal individual-trajectory classifier.

## Agreement and disagreement

Agreement is not imposed by definition. It has a mathematical domain. When two spectra are comparable by majorization, Schur-concave entropies order them consistently. When they are incomparable, different entropy orders may respond differently to redistribution between the leading edge, bulk, and tail.

This leads to two useful dynamical categories:

- **Metric-consensus motion:** several measures report the same direction of change, consistent with a broad spectral concentration or broadening.
- **Metric-competitive motion:** valid measures report different directions, indicating a redistribution that cannot be summarized by a total scalar ordering.

The spectrum path explains both behaviors.

## Exact arena and normalization

At fixed \(p=\lambda_{\max}\), the equal-tail spectrum

\[
\left(p,\frac{1-p}{d-1},\ldots,\frac{1-p}{d-1}\right)
\]

maximizes the Schur-concave metrics used here. The compatible concentrated spectrum

\[
(\underbrace{p,\ldots,p}_{k\text{ entries}},r,0,\ldots,0),
\qquad k=\lfloor 1/p\rfloor,\quad r=1-kp,
\]

minimizes them. These extremizers define exact fixed-\(p\) envelopes.

For metrics with such envelopes, the common relative coordinate is

\[
r_E(\boldsymbol{\lambda})=
\frac{E(\boldsymbol{\lambda})-E_{\min}(\lambda_{\max})}
{E_{\max}(\lambda_{\max})-E_{\min}(\lambda_{\max})}.
\]

This removes metric-specific ranges and much of the universal feasible-region deformation before trajectories are compared.

## Meaning of “topological invariant”

The phrase **“topological invariant”** in the conceptual discussion denotes an empirical coarse trajectory class that remains stable across the declared spectrum functionals. Exact turn counts vary between metric projections; no homeomorphism or homotopy theorem underlies this usage.

The technical terms are **metric-robust trajectory class** and **projection-stable trajectory morphology**.

## Role of random matrix theory

Random matrix theory is a secondary reference layer, not the exact geometric foundation. The hierarchy is:

1. exact feasible spectrum geometry;
2. Haar/fixed-trace Wishart reference ensembles;
3. spiked-Wishart conditional loci under stated assumptions;
4. empirical distance of physical trajectories from those references.

Marchenko-Pastur density, edge statistics, scalar entropy proximity, gap ratios, and higher spectral correlations are distinct diagnostics. Their disagreement is scientifically informative.

## Scope

The central claim concerns:

- pure-state dynamics;
- explicitly specified bipartitions or clearly defined averages over cuts;
- the representative spectrum functionals actually implemented;
- the four supplied dynamical families, sizes, parameters, and initial states;
- empirical metric robustness rather than universal formal invariance.

The one-site-averaged columns named `global_*` are functions of a collection of one-qubit spectra. They must be distinguished from metrics of the half-chain spectrum.

## Relationship to the 2024 paper

The published paper introduced the trajectory representation: entanglement evolution appears as a path, the largest Schmidt value supplies an additional coordinate, and recognizable shape may survive a change of entanglement measure.

The repository follow-up supplies the four-model, six-size dataset, exact fixed-largest-eigenvalue envelopes, boundary-relative normalization, and spectrum-level diagnostics. [Corrections and clarifications](CORRECTIONS.md) record the mathematical and physical corrections to the article.
