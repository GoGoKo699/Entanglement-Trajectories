# Majorization, Metric Consensus, and Metric Competition

## Majorization as the exact consensus relation

For descending spectra \(\boldsymbol x\) and \(\boldsymbol y\),

\[
\boldsymbol x\succ\boldsymbol y
\]

means

\[
\sum_{i=1}^m x_i
\ge
\sum_{i=1}^m y_i
\quad
\text{for }m=1,\ldots,d-1,
\]

with equal total sums. The vector \(\boldsymbol x\) is then more concentrated, while \(\boldsymbol y\) is more mixed.

Every Schur-concave entropy obeys

\[
\boldsymbol x\succ\boldsymbol y
\quad\Longrightarrow\quad
H_q(\boldsymbol x)\le H_q(\boldsymbol y).
\]

Thus majorization-compatible motion gives an exact domain in which the entropic metrics must agree on direction.

## Incomparability leaves room for contradiction

Majorization is only a partial order. If neither spectrum majorizes the other, no scalar entropy is required to agree with every other scalar entropy.

Consider

\[
\boldsymbol x=(0.8,0.1,0.1,0),
\qquad
\boldsymbol y=(0.7,0.3,0,0).
\]

The first cumulative sum is larger for \(\boldsymbol x\), but the first two sum is smaller:

\[
0.8>0.7,
\qquad
0.9<1.0.
\]

The spectra are therefore incomparable. The metric values in bits are:

| Metric | \(x\) | \(y\) | Reported direction |
|---|---:|---:|---|
| \(H_{1/2}\) | 1.22118 | 0.93849 | \(x\) more entangled |
| \(H_1\) | 0.92193 | 0.88129 | \(x\) more entangled |
| \(H_2\) | 0.59946 | 0.78588 | \(y\) more entangled |
| \(H_\infty\) | 0.32193 | 0.51457 | \(y\) more entangled |

This is the exact form of the philosophical point: unification does not mean universal agreement. It means locating agreement and disagreement inside one Schmidt-spectrum dynamics.

## Dynamical classification

For consecutive spectra \(\boldsymbol\lambda(t)\) and \(\boldsymbol\lambda(t+\Delta t)\), the upgraded analysis will classify each step as:

1. **equal or numerically indistinguishable**;
2. **forward-majorization motion**;
3. **reverse-majorization motion**;
4. **majorization-incomparable motion**.

The first three categories impose consistent ordering on all Schur-concave entropies. The fourth is the only category in which genuine cross-order competition can occur.

## Metric-consensus event

A step is a metric-consensus event when the declared representatives—currently \(q=1/2,1,2,\infty\)—move in the same entanglement direction beyond numerical tolerance.

Consensus may occur even without a strict majorization relation, so the analysis should distinguish:

- **majorization-certified consensus**;
- **empirical consensus without majorization certification**.

## Metric-competitive event

A step is metric-competitive when at least two independent Rényi-order classes change in opposite directions. Aliases in the same equivalence class must not be counted as independent disagreement.

The event record should include:

- the two spectra or their hashes;
- the majorization relation;
- changes in \(H_{1/2},H_1,H_2,H_\infty\);
- changes at the leading edge \(\lambda_1,\lambda_2\);
- numerical tolerances;
- model, size, run, cut, and time.

## Why trajectory geometry is useful

A scalar metric hides whether a change came from the leading eigenvalue, the bulk, the tail, or a redistribution among them. The trajectory atlas turns the disagreement pattern into geometric information:

- shared large-scale arcs identify metric-robust organization;
- splits between charts identify spectral redistribution;
- edge diagnostics can localize whether the change is dominated by \(\lambda_1\) and \(\lambda_2\);
- full-spectrum diagnostics can determine whether the bulk or tail is responsible.

The candidate “topological invariant” is therefore not the absence of contradiction. It is the coarse path structure that persists while these local contradictions remain visible.
