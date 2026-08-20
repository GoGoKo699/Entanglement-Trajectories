# Scientific Position

## Governing philosophy

There are many useful scalar measures of entanglement because a Schmidt spectrum contains more information than one number can retain. The project should not search for a scalar that makes all other measures obsolete. It should identify the common object that the measures observe and explain both their agreements and their disagreements.

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

## Central claim for the upgraded repository

Standard bipartite pure-state entanglement measures are nonlinear projections of a common Schmidt-spectrum path. Across the tested pure-state chaos families, three non-equivalent metric classes share a dominant common trajectory mode and preserve substantial relational morphology after exact-boundary normalization. The preservation is hierarchical rather than exact, and local metric contradictions reveal internal spectral redistribution that no single scalar measure captures.

This claim has three distinct parts:

1. **Exact common origin.** The fixed-cut measures considered here are functions of the same spectrum.
2. **Empirical robustness.** Coarse trajectory morphology and the relative geometry among tested model families persist across several metric projections.
3. **Permitted disagreement.** Different metrics can contradict one another locally, especially when successive spectra are incomparable by majorization.

## Quantitative status of the follow-up study

The current follow-up data provide the following scoped support:

- the exact-boundary-normalized common metric mode explains 90.26% of total variance;
- the median separate-trajectory common-mode fraction is 94.75%;
- within-trajectory boundary-coordinate rank agreement ranges from 0.692 to 0.947 across the three independent metric pairs;
- vertical-only trajectory-space distance rankings are preserved with mean correlations from 0.644 to 0.961;
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

Unification therefore means explaining both behaviors through one spectrum path. It does not mean forcing all measures to agree.

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

The project may retain the phrase **“topological invariant”** as its conceptual language, but only with an explicit operational qualification.

At present it means:

> the coarse trajectory class that remains stable under replacing one declared spectrum functional by another.

It does **not** presently mean:

- equality of numerical trajectories;
- preservation of every turning point or self-intersection;
- a proved homeomorphism or homotopy class;
- a winding number or persistent-homology theorem;
- universality over every model, cut, state, and entanglement measure.

The preferred technical terms are **metric-robust trajectory class** and **projection-stable trajectory morphology**. A formal topological construction remains a possible later research direction.

## Role of random matrix theory

Random matrix theory is a secondary reference layer, not the exact geometric foundation. The hierarchy is:

1. exact feasible spectrum geometry;
2. Haar/fixed-trace Wishart reference ensembles;
3. spiked-Wishart conditional loci under stated assumptions;
4. empirical distance of physical trajectories from those references.

Marchenko-Pastur density, edge statistics, scalar entropy proximity, gap ratios, and higher spectral correlations are distinct diagnostics. Their disagreement is scientifically informative.

## Scope

The current central claim is limited to:

- pure-state dynamics;
- explicitly specified bipartitions or clearly defined averages over cuts;
- the representative spectrum functionals actually implemented;
- the four supplied dynamical families, sizes, parameters, and initial states;
- empirical metric robustness rather than universal formal invariance.

The one-site-averaged columns currently named `global_*` are functions of a collection of one-qubit spectra, not of the one half-chain spectrum. Mixed-state entanglement measures, genuine multipartite invariants, discord-like quantities, and operational entanglement costs require separate objects and are not silently absorbed into this claim.

## Relationship between the 2024 paper and the follow-up package

The published paper introduced the primitive idea: entanglement evolution can be represented as a path, the largest Schmidt value supplies an additional coordinate, and recognizable shape may survive a change of entanglement measure.

The follow-up package upgrades the evidence by adding four model families, six sizes, multiple runs, several normalized spectrum functionals, exact fixed-largest-eigenvalue envelopes, boundary-relative normalization, and spectrum-level random-matrix diagnostics.

The upgrade must preserve the original insight while correcting the paper’s exact boundary, Page-formula, rank-one, QFT, continuity, random-matrix, computational-interpretation, gap, fingerprint, and topology overstatements.

## Public nonclaims

The final repository must never imply that:

- all entanglement metrics always agree;
- every entanglement notion is a function of one Schmidt spectrum;
- a formal topological invariant has already been proved;
- random matrix theory supplies the exact feasible boundary;
- all tested dynamics converge to an RMT attractor;
- QFT generally preserves a Schmidt spectrum;
- low entropy alone guarantees efficient tensor-network simulation;
- high entropy alone makes a quantum state computationally useless;
- trajectory location alone certifies computational advantage;
- selected visual paths already constitute a universal classifier.
