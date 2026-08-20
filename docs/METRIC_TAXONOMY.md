# Metric Taxonomy: Many Names, Fewer Independent Spectral Views

## Central distinction

The project begins from a broad fact: many readily computed bipartite pure-state entanglement quantities are functions of the same Schmidt spectrum. That does not mean every named quantity supplies independent information.

A scientifically clean atlas must distinguish:

1. **different formulas with identical ordering information**;
2. **genuinely different spectral sensitivities**;
3. **diagnostics that are not entanglement monotones**;
4. **aggregates over many cuts rather than one spectrum**.

## Rényi-order organization

Rényi order provides the most economical organizing axis.

| Order or class | Sensitivity | Canonical representative | Follow-up representative |
|---|---|---|---|
| \(q=0\) | support/rank | Schmidt rank or \(H_0\) | not yet in the main CSV |
| \(q=1/2\) | tail-sensitive | \(H_{1/2}\) | pure-state logarithmic negativity |
| \(q=1\) | bulk-weighted | von Neumann entropy | normalized half-chain VN entropy |
| \(q=2\) | head-weighted | purity or \(H_2\) | normalized linear entropy |
| \(q=\infty\) | largest eigenvalue only | \(\lambda_{\max}\) or \(H_\infty\) | normalized geometric coordinate |
| leading edge | first two eigenvalues | \(\lambda_2/\lambda_1\) or log gap | saved in spectrum-level extension, not main CSV |

The follow-up package therefore does something more precise than “include almost every easy metric”: it samples four widely separated Rényi-order equivalence classes, from tail sensitivity through the spectral head. That is broad and strategically meaningful, but it is not literally exhaustive.

## Exact equivalence classes

### The \(q=1/2\) class

For bipartite pure states:

\[
E_{\mathcal N}=H_{1/2},
\qquad
\mathcal N=\frac{R_{1/2}-1}{2}.
\]

Logarithmic negativity, negativity, \(H_{1/2}\), and \(R_{1/2}\) cannot contradict one another on spectral ordering. They differ only by strictly increasing transformations.

### The \(q=2\) class

\[
H_2=-\log P,
\qquad
L=1-P,
\qquad
R_2=1/P,
\]

with I-concurrence and I-tangle also determined by \(P\). These quantities provide one independent ordering class, not six independent votes.

### The \(q=\infty\) class

\[
H_\infty=-\log\lambda_{\max},
\qquad
E_G=1-\lambda_{\max},
\qquad
R_\infty=1/\lambda_{\max}.
\]

When the horizontal trajectory coordinate is already a function of \(\lambda_{\max}\), adding another \(q=\infty\) quantity as the vertical coordinate produces a degenerate representation.

## What can genuinely disagree?

Different Rényi orders can reverse their ordering on majorization-incomparable spectra. This is the useful source of metric competition.

For example,

\[
\boldsymbol x=(0.8,0.1,0.1,0),
\qquad
\boldsymbol y=(0.7,0.3,0,0)
\]

are incomparable by majorization. In bits,

| Metric | \(\boldsymbol x\) | \(\boldsymbol y\) | Ordering |
|---|---:|---:|---|
| \(H_{1/2}\) | 1.22118 | 0.93849 | \(x>y\) |
| \(H_1\) | 0.92193 | 0.88129 | \(x>y\) |
| \(H_2\) | 0.59946 | 0.78588 | \(x<y\) |
| \(H_\infty\) | 0.32193 | 0.51457 | \(x<y\) |

The contradiction is not a defect. The tail and bulk of \(\boldsymbol x\) are broader, while its leading eigenvalue is more concentrated. Different orders legitimately emphasize different parts of the redistribution.

## Entanglement measures versus spectral diagnostics

The following are retained because they can reveal mechanisms, but they should not be advertised as total entanglement orderings:

- \(\lambda_1-\lambda_2\);
- \(\lambda_2/\lambda_1\);
- \(\log(\lambda_1/\lambda_2)\);
- spacing-ratio statistics of the entanglement Hamiltonian;
- distance to a Marchenko–Pastur reference;
- spectral-edge outlier counts.

They add information beyond scalar entropies, but their interpretation is diagnostic and model-dependent.

## Fixed-cut metrics versus many-cut aggregates

The historical columns named `global_*` are not functions of the half-chain spectrum. They average one-qubit-versus-rest quantities over all sites:

- `global_vn` → mean one-site von Neumann entropy;
- `global_mw` → Meyer–Wallach \(Q\), exactly the mean normalized one-site linear entropy;
- `global_logneg` → mean one-site pure logarithmic negativity;
- `global_geo` → mean one-site geometric quantity.

The upgraded repository will retain the old names only as backward-compatible data aliases. Public text and regenerated tables will use explicit `mean_one_site_*` labels.

## Implication for evidence counting

A visual comparison between log-negativity and \(H_{1/2}\) is not an independent robustness test; they are mathematically identical for the present pure-state setting. Likewise, purity and linear entropy are the same ordering in opposite directions.

The strongest evidence for metric robustness comes from comparisons across equivalence classes—for example \(q=1/2\), \(q=1\), \(q=2\), and \(q=\infty\)—and from agreement that survives exact-boundary normalization.
