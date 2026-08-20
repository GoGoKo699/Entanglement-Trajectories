# Haar/Wishart reference layer

## Role in the project

Random matrix theory does not define the exact feasible boundary of an entanglement trajectory. Exact boundaries follow from finite-dimensional spectrum optimization and majorization. The Haar/Wishart layer instead supplies a declared random-state reference inside that arena.

The current analysis therefore asks:

> At which sampled times and in which coordinates does a trajectory approach or depart from the selected random-state reference?

It does not ask whether all dynamics must converge to one universal attractor.

## Reference components

For subsystem dimensions `d_A <= d_B`, the exact complex-Haar mean von Neumann entropy is Page's finite-dimensional expression

\[
\mathbb E[S]
=H_{d_A d_B}-H_{d_B}-\frac{d_A-1}{2d_B}
\]

in natural logarithms. The current normalized coordinate divides by `ln d_A`.

The exact complex-Haar mean purity is

\[
\mathbb E[\operatorname{Tr}\rho_A^2]
=\frac{d_A+d_B}{d_A d_B+1},
\]

which gives the exact mean normalized linear entropy used here.

For balanced large dimensions, two additional proxies are derived from the Marchenko-Pastur density of the scaled eigenvalues `x=d lambda`:

- `E[sqrt(x)] = 8/(3 pi)` gives the asymptotic pure-state logarithmic-negativity proxy;
- the upper edge `x=4` gives the largest-eigenvalue geometric proxy.

The four-coordinate RMS distance is thus deliberately called a **mixed reference distance**. Its components are also reported separately as an exact-Haar-mean distance and an asymptotic-MP-proxy distance.

## Analytic balanced Marchenko-Pastur CDF

The balanced density is

\[
\rho_{\mathrm{MP}}(x)
=\frac{1}{2\pi}\sqrt{\frac{4-x}{x}},
\qquad 0<x<4.
\]

Writing `x=4 sin^2(theta)` gives

\[
F_{\mathrm{MP}}(x)
=\frac{2\theta+\sin(2\theta)}{\pi}.
\]

This analytic CDF is essential near `x=0`. A uniform trapezoidal grid treats the integrable square-root singularity badly and produced large KS errors in the historical executable source.

## Separate diagnostic layers

The package keeps the following distinct:

1. scalar entanglement-coordinate distance;
2. one-point Marchenko-Pastur density KS distance;
3. scaled largest-eigenvalue edge displacement;
4. effective-rank and support diagnostics;
5. adjacent-gap ratios of the entanglement Hamiltonian.

Agreement among these quantities is stronger evidence than any one quantity alone. Disagreement is also informative because each diagnostic emphasizes a different part of the spectrum.

## Adjacent-gap ratio convention

For positive reduced eigenvalues, define entanglement energies

\[
\xi_i=-\log\lambda_i
\]

and adjacent spacings `s_i=xi_{i+1}-xi_i`. The ratio is

\[
r_i=\frac{\min(s_i,s_{i+1})}{\max(s_i,s_{i+1})}.
\]

The current output reports:

- a full positive-spectrum mean;
- a bulk-window mean after selecting `0.05 <= d lambda <= 3.95`.

Reference values for Poisson, GOE, GUE, and GSE are shown only as comparison lines. The code does not infer a symmetry class from proximity to one mean value, and it does not claim that a mean ratio alone establishes random-matrix universality.

## Empirical conclusion from the supplied data

At `n=20`, some kicked-Ising and QCA runs come very close to the mixed reference, while the supplied quantum-baker and strong-disorder XXZ runs remain much farther away. Some trajectories reach a closer intermediate point and then rebound. The correct conclusion is heterogeneous, model- and run-dependent approach toward a reference.

Among the five saved full-spectrum reruns, a bulk adjacent-gap ratio can be close to a random-matrix comparison value even when the one-point density and spectral edge remain far from the balanced Haar/Wishart reference. This is why the diagnostics are kept separate.
