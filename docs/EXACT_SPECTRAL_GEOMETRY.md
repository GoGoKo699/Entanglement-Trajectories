# Exact Schmidt-Spectrum Geometry at Fixed Largest Eigenvalue

## 1. Convention and domain

For a bipartite pure state and one declared cut, let

\[
\boldsymbol\lambda=(\lambda_1,\ldots,\lambda_d),
\qquad
\lambda_1\ge\lambda_2\ge\cdots\ge\lambda_d\ge0,
\qquad
\sum_i\lambda_i=1.
\]

The entries are eigenvalues of the reduced density matrix—equivalently, squared Schmidt coefficients. Set

\[
p=\lambda_1,\qquad \frac1d\le p\le1.
\]

The fixed-\(p\) feasible set is

\[
\Delta_d(p)=
\left\{
\boldsymbol\lambda:\lambda_1=p,\ 
\lambda_1\ge\cdots\ge\lambda_d\ge0,\ 
\sum_i\lambda_i=1
\right\}.
\]

## 2. The two extremizing spectra

Define the equal-tail spectrum

\[
\boldsymbol u(p)=
\left(
 p,\frac{1-p}{d-1},\ldots,\frac{1-p}{d-1}
\right).
\]

Define

\[
k=\left\lfloor\frac1p\right\rfloor,
\qquad
r=1-kp,
\]

and the concentrated spectrum

\[
\boldsymbol c(p)=
(\underbrace{p,\ldots,p}_{k\text{ entries}},r,0,\ldots,0),
\]

with a zero remainder omitted.

### Majorization sandwich

For every \(\boldsymbol\lambda\in\Delta_d(p)\),

\[
\boxed{
\boldsymbol c(p)\succ\boldsymbol\lambda\succ\boldsymbol u(p)
}.
\]

This is the exact finite-dimensional foundation of the corrected trajectory arena.

### Proof sketch

For any \(m\), the sum of the largest \(m\) components of a feasible spectrum cannot exceed \(\min(mp,1)\). The concentrated spectrum attains this maximal partial sum at every \(m\), so it majorizes every feasible spectrum.

After the fixed first component \(p\), the remaining \(d-1\) entries have total weight \(1-p\). The sum of the largest \(m-1\) tail entries is at least \((m-1)(1-p)/(d-1)\). The equal-tail spectrum attains these minimal partial sums, so every feasible spectrum majorizes it.

Consequently:

- every Schur-concave spectrum functional is minimized by \(\boldsymbol c(p)\) and maximized by \(\boldsymbol u(p)\);
- every Schur-convex spectrum functional has the reverse numerical extrema.

This is stronger and more general than the approximate three-curve construction in the 2024 paper.

## 3. Rényi-family envelopes

For \(q>0\), \(q\ne1\),

\[
H_q(\boldsymbol\lambda)
=
\frac{1}{1-q}\log\sum_i\lambda_i^q.
\]

The exact fixed-\(p\) bounds are

\[
H_q^{\min}(p;d)
=
\frac{1}{1-q}\log\left(kp^q+r^q\right),
\]

and

\[
H_q^{\max}(p;d)
=
\frac{1}{1-q}
\log\left[
p^q+(d-1)^{1-q}(1-p)^q
\right].
\]

The \(r^q\) term is omitted when \(r=0\).

### Von Neumann limit \(q=1\)

\[
S_{\min}(p;d)
=-kp\log p-r\log r,
\]

\[
S_{\max}(p;d)
=-p\log p-(1-p)\log\frac{1-p}{d-1}.
\]

The binary entropy is the lower boundary only when \(p\ge1/2\). The curve \(-\log p\) touches the lower boundary only at reciprocal points \(p=1/k\).

### Hartley limit \(q=0\)

The exact minimum support size is

\[
R_0^{\min}(p)=\left\lceil\frac1p\right\rceil,
\]

so

\[
H_0^{\min}(p)=\log\left\lceil\frac1p\right\rceil.
\]

For \(p<1\), the equal-tail spectrum has full support and

\[
H_0^{\max}(p)=\log d.
\]

At \(p=1\), both bounds are zero. This discontinuity is intrinsic to rank and must not be hidden by numerical thresholding.

### Exact support versus numerical rank

The Hartley entropy in this repository uses the mathematical support of the represented spectrum:

\[
\operatorname{rank}(\boldsymbol\lambda)
=\#\{i:\lambda_i>0\}.
\]

Every strictly positive represented entry counts, irrespective of magnitude. A thresholded count

\[
R_{\varepsilon}=\#\{i:\lambda_i>\varepsilon\}
\]

is instead a **numerical Schmidt-rank diagnostic**. It can be useful for floating-point spectra, but it is threshold-dependent, is not the exact Rényi-\(0\) entropy, and must be reported together with \(\varepsilon\) and whether the threshold is absolute or relative to \(\lambda_{\max}\).

The fixed-\(p\) Hartley and Schmidt-rank boundaries are evaluated analytically from the support formulas above. They are not inferred by applying a numerical threshold to the extremizing spectra. The numerical concentrated-spectrum constructor may suppress remainders below its declared spectrum tolerance when evaluating continuous metrics. The discontinuous support formulas do not use that convention and are evaluated analytically.

### Min-entropy limit \(q=\infty\)

\[
H_\infty=-\log p.
\]

The fixed-\(p\) envelope collapses because the metric is completely determined by the horizontal coordinate.

## 4. Purity and the \(q=2\) class

Purity is Schur-convex:

\[
P=\sum_i\lambda_i^2.
\]

Its exact bounds are

\[
P_{\min}(p;d)
=p^2+\frac{(1-p)^2}{d-1},
\]

\[
P_{\max}(p;d)
=kp^2+r^2.
\]

Linear entropy \(L=1-P\) reverses these numerical extrema. The dimension-normalized form used in the follow-up package is

\[
\widetilde L
=
\frac{d}{d-1}(1-P).
\]

The following quantities are strictly monotone transformations of the same \(q=2\) information:

- Rényi entropy \(H_2=-\log P\);
- purity \(P\);
- linear entropy \(1-P\);
- participation ratio \(R_2=1/P\);
- I-concurrence \(C_I=\sqrt{2(1-P)}\);
- I-tangle \(\tau_I=2(1-P)\).

They may look different geometrically when plotted, but they cannot disagree on the ordering of two spectra.

## 5. Pure-state negativity and the \(q=1/2\) class

For a bipartite pure state,

\[
E_{\mathcal N}
=
2\log\sum_i\sqrt{\lambda_i}
=
H_{1/2}(\boldsymbol\lambda).
\]

The ordinary negativity is

\[
\mathcal N
=
\frac{\left(\sum_i\sqrt{\lambda_i}\right)^2-1}{2}.
\]

Thus logarithmic negativity, negativity, \(H_{1/2}\), and the effective number \(R_{1/2}\) carry the same spectral ordering for pure states. Their fixed-\(p\) bounds follow directly by evaluating the concentrated and equal-tail spectra.

This identity does not extend unchanged to generic mixed states.

## 6. Effective Schmidt numbers

The Rényi/Hill effective number is

\[
R_q
=
\left(\sum_i\lambda_i^q\right)^{1/(1-q)},
\]

with

\[
R_1=e^{S},
\qquad
R_2=\frac1P,
\qquad
R_\infty=\frac1p,
\qquad
R_0=\operatorname{rank}(\rho_A).
\]

Because \(R_q\) is a strictly increasing transformation of \(H_q\), it has the same extremizing spectra and ordering information. A convenient dimension normalization is

\[
\widetilde R_q=\frac{R_q-1}{d-1}.
\]

## 7. Geometric measures and coordinate redundancy

For bipartite pure states, the linear geometric measure is

\[
E_G=1-p,
\]

and the logarithmic form is

\[
E_G^{\log}=-\log p=H_\infty.
\]

The follow-up package uses

\[
\widetilde E_G=\frac{d}{d-1}(1-p)
\]

as its horizontal coordinate. Therefore geometric entanglement, min-entropy, and \(\lambda_{\max}\) are not independent coordinates in this atlas. They are different scales for the same spectral-head information.

## 8. Exact leading-edge diagnostic bounds

Let \(\lambda_2\) be the second-largest eigenvalue. At fixed \(p=\lambda_1\),

\[
\frac{1-p}{d-1}
\le \lambda_2
\le \min(p,1-p).
\]

### Ordinary Schmidt gap

\[
g=\lambda_1-\lambda_2.
\]

Its exact bounds are

\[
\boxed{
g_{\min}(p;d)=\max(0,2p-1)
},
\]

\[
\boxed{
g_{\max}(p;d)=p-\frac{1-p}{d-1}=\frac{dp-1}{d-1}
}.
\]

### Leading ratio

\[
r_{21}=\frac{\lambda_2}{\lambda_1}
\]

has exact bounds

\[
\frac{1-p}{(d-1)p}
\le r_{21}
\le \min\left(1,\frac{1-p}{p}\right).
\]

### Entanglement-Hamiltonian gap

For entanglement energies \(\xi_i=-\log\lambda_i\),

\[
\Delta_\xi=\xi_2-\xi_1=\log\frac{p}{\lambda_2}.
\]

Its exact bounds are

\[
\boxed{
\Delta_{\min}(p;d)
=
\max\left\{0,\log\frac{p}{1-p}\right\}
},
\]

\[
\boxed{
\Delta_{\max}(p;d)
=
\log\frac{p(d-1)}{1-p}
}.
\]

At \(p=1\), the logarithmic gap is infinite. These gap quantities are spectral diagnostics, not universal entanglement monotones.

## 9. Boundary-relative normalization

For a metric with a noncollapsed exact envelope,

\[
r_E(\boldsymbol\lambda)
=
\frac{
E(\boldsymbol\lambda)-E_{\min}(p)
}{
E_{\max}(p)-E_{\min}(p)
}.
\]

This operation is distinct from dimension normalization. It asks where the spectrum lies inside the exact feasible interval available at its current \(p\).

The coordinate is undefined when

\[
E_{\max}(p)=E_{\min}(p).
\]

This occurs at the product and maximally entangled endpoints for entropy-like measures and at every \(p\) for metrics determined solely by \(p\). The corrected implementation returns `NaN` by default rather than assigning an arbitrary 0 or 1.

## 10. Computational verification

The current exact-boundary implementation was checked by:

- 108,500 random spectrum–metric comparisons over dimensions 2 through 32;
- direct majorization tests against both extremizers;
- exhaustive enumeration of 1,261 feasible lattice spectra for \(d=4\), \(p=0.4\);
- 1,800 random-spectrum identity checks among equivalent metrics;
- re-evaluation of 405 saved \(d=1024\) spectra from the follow-up package.

All exact-bound tests passed. The maximum observed bound violation was at floating-point roundoff level.
