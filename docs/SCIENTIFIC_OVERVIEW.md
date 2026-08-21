# Scientific Overview

## 1. Why another representation of entanglement?

Entanglement is not naturally one-dimensional. Even for a fixed bipartition of a pure state, the reduced density matrix has a complete ordered spectrum. A scalar entanglement measure compresses that spectrum according to a chosen sensitivity: the leading eigenvalue, the bulk, the tail, or a weighted mixture.

This creates two persistent facts:

1. many useful scalar measures coexist because no one scalar retains the full spectrum;
2. valid measures can disagree because different spectral redistributions need not admit one total ordering.

The project’s unifying move is therefore not to select a winning metric. It is to elevate the **Schmidt-spectrum path** to the primary object and treat scalar metrics as observables on that path.

## 2. The trajectory atlas

For a fixed cut of a pure state, let

$$
\boldsymbol\lambda(t)=\bigl(\lambda_1(t),\ldots,\lambda_d(t)\bigr),
\qquad
\lambda_1\ge\cdots\ge\lambda_d\ge0,
\qquad
\sum_i\lambda_i=1.
$$

A spectrum functional $E$ gives

$$
\Gamma_E(t)=\bigl(\lambda_1(t),E[\boldsymbol\lambda(t)]\bigr).
$$

The collection of these projections is the entanglement-trajectory atlas. Each projection is incomplete. The atlas asks what is stable across the lenses and what is revealed only by their differences.

The included fixed-cut coordinates span separated Rényi sectors:

- $H_{1/2}$, equal to pure-state logarithmic negativity;
- $H_1$, the von Neumann entropy;
- the $H_2$ equivalence class, represented by linear entropy or purity;
- $H_\infty$, determined by $\lambda_{\max}$ and equivalent geometric coordinates.

The registry prevents aliases from being counted as independent evidence. For example, purity, linear entropy, Rényi-2 entropy, participation ratio, I-concurrence, and I-tangle are linked by strict transformations or shared sufficient statistics.

## 3. Exact spectrum geometry

At fixed $p=\lambda_{\max}$, the compatible spectra have exact majorization extremizers.

The equal-tail spectrum

$$
\boldsymbol u(p)=\left(p,\frac{1-p}{d-1},\ldots,\frac{1-p}{d-1}\right)
$$

is majorized by every compatible spectrum. The concentrated spectrum

$$
\boldsymbol c(p)=
(\underbrace{p,\ldots,p}_{k},r,0,\ldots,0),
\quad k=\lfloor1/p\rfloor,
\quad r=1-kp,
$$

majorizes every compatible spectrum.

Every Schur-concave metric used here therefore lies between its values on $\boldsymbol c(p)$ and $\boldsymbol u(p)$. This gives exact finite-dimensional envelopes and replaces the approximate three-curve arena in the published paper.

For a metric with a noncollapsed envelope, define

$$
r_E(\boldsymbol\lambda)=
\frac{E(\boldsymbol\lambda)-E_{\min}(\lambda_{\max})}
{E_{\max}(\lambda_{\max})-E_{\min}(\lambda_{\max})}.
$$

This boundary-relative coordinate removes the metric’s range and much of its universal feasible-region deformation before trajectories are compared. At product, maximally entangled, or otherwise collapsed-envelope endpoints, the relative coordinate is undefined rather than assigned an arbitrary number.

## 4. Why metrics agree

Majorization supplies a domain of compulsory agreement. If

$$
\boldsymbol\lambda(t)\succ\boldsymbol\lambda(t+\Delta t),
$$

then every Schur-concave entropy used here reports that the later spectrum is at least as entangled. The reverse majorization relation forces the reverse ordering.

This is the exact part of the unification: different entropy families share the same partial order whenever that order applies.

## 5. Why metrics disagree

Most pairs of high-dimensional spectra are not totally ordered by majorization. When neither spectrum majorizes the other, weight can move between the leading edge, bulk, and tail so that different Rényi sectors respond in opposite directions.

The repository calls this **metric competition**. It is not a defect in the metrics. It is evidence that the spectrum moved in a way that cannot be compressed into one universal scalar ranking.

In the selected full-spectrum audit, every observed metric-competition event lies in the majorization-incomparable sector. Incomparability is permissive rather than deterministic: many incomparable transitions still give consensus.

## 6. The empirical metric-robust class

After exact-boundary normalization, the three tested vertical metric classes have a dominant common standardized mode explaining 90.26% of total variance. The common mode has positive loadings on all three metrics. The principal contrast mode is dominated by the order-2 class, consistent with its stronger sensitivity to the leading part of the spectrum.

This supports a hierarchy:

- a strong common coarse mode;
- metric-dependent deformation and contrast;
- localized metric competition;
- noninvariance of fine projected features such as exact turn counts.

The appropriate conclusion is **projection-stable coarse morphology**, not exact projected-path identity.

## 7. Dynamical examples motivated by scrambling and spectral complexity

The follow-up package includes four dynamical families used to probe scrambling, recurrence, disorder, and spectral complexity:

- brickwork Floquet QCA;
- open-chain kicked Ising;
- a Balazs–Voros-style quantum baker;
- a fixed symmetric product-formula circuit generated from random-field XXZ terms.

Across the included conditions and sizes, model-centroid trajectories retain recognizable separation in the shared metric mode. Held-out-size model-centroid classification is strong, including substantial cross-metric transfer. Performance drops for unseen individual conditions, especially when both size and condition are held out.

The result supports model-family morphology within the tested scope. It does not yet establish a universal chaos fingerprint.

## 8. Meaning of topology

The published paper used “topological invariant” as informal conceptual language for the stability of trajectory shape across metric choices. The upgraded evidence supports only a coarse operational version:

> a trajectory class is metric robust when its major stages and relational morphology remain stable under replacement of one declared spectrum functional by another.

Exact turns, self-intersections, signed areas, curvature, and homotopy type need not be preserved. A formal topological construction remains an open research direction and would require an explicit object, equivalence relation, coarse-graining rule, stability theorem, and validation under sampling and perturbation.

## 9. Role of random matrix theory

The exact arena is determined by spectrum geometry. Random matrix theory supplies conditional references:

1. finite-dimensional fixed-trace Haar/Wishart scalar references;
2. asymptotic Marchenko–Pastur one-point density;
3. spectral-edge diagnostics;
4. entanglement-Hamiltonian bulk-correlation diagnostics;
5. separated-spike approximations where their assumptions hold.

These diagnostics can disagree. A spectrum may have a bulk adjacent-gap ratio near a random-matrix reference while its one-point density or largest eigenvalue remains far away. Such disagreement is part of the spectral information, not something to suppress.

The follow-up data do not show one universal RMT attractor. Some selected paths approach the reference closely, some rebound, and others remain far from it.

## 10. Relationship to the 2024 paper

The paper introduced the useful primitive idea: entanglement evolution can be represented as a path; the largest Schmidt value supplies a complementary coordinate; recognizable path morphology may survive a change of metric.

The repository corrects or narrows:

- the exact entropy boundary;
- the finite-dimensional Page formula;
- the rank-one noncentral-Wishart algebra and scaling;
- general QFT invariance;
- the finite arithmetic-union endpoint;
- continuity language;
- entropy-gap interpretation;
- random-matrix boundary and attractor language;
- entropy-based claims about simulation and computational usefulness;
- topology and fingerprint claims.

The corrected project is stronger because exact geometry, conditional random-matrix references, empirical robustness, and open hypotheses are now kept separate.

## 11. Current scientific claim

> For fixed-cut bipartite pure-state dynamics, standard spectrum-based entanglement measures are nonlinear projections of one Schmidt-spectrum path. Across the tested dynamical families, three non-equivalent metric classes share a dominant exact-boundary-normalized trajectory mode and preserve substantial relational morphology. The preservation is hierarchical rather than exact, and local contradictions occur on majorization-incomparable spectral steps. This supports an empirical metric-robust trajectory class, not a formal topological invariant or universal individual-run fingerprint.
