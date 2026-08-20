# Author Clarification and Correction Record (2026 Draft)

## Status of this document

This is an author-prepared public repository clarification for the published article:

**Ruge Lin, "Entanglement Trajectory and its Boundary," Quantum 8, 1282 (2024).**

The journal article remains the version of record. This document identifies statements that should be read with corrected formulas or narrower scope. It accompanies the reproducible repository edition and may later support a concise formal corrigendum.

## What remains valid

The article introduced a useful representation: follow a quantum process through a plane whose coordinates are functions of the reduced Schmidt spectrum. The broader idea survives and is strengthened by the follow-up study:

- the ordered Schmidt-spectrum path is the common underlying object;
- familiar entanglement metrics are different nonlinear observations of that path;
- multiple projected paths form an entanglement-trajectory atlas;
- substantial model-specific morphology can survive changing and normalizing the metric;
- local disagreements between metrics are allowed and can reveal internal spectral redistribution.

## Material mathematical corrections

### 1. Exact entropy boundary

The three simple curves in the article are not the exact finite-dimensional boundary. For dimension `d` and `p=lambda_max`, the exact upper spectrum is the equal-tail spectrum and the exact lower spectrum packs as many entries equal to `p` as possible, followed by one remainder. The formulas are given in `docs/EXACT_SPECTRAL_GEOMETRY.md`.

### 2. Page formula

The article states `log(alpha)-alpha/(2 beta)` as an exact theorem. The exact complex-Haar mean is

\[
H_{\alpha\beta}-H_\beta-\frac{\alpha-1}{2\beta}.
\]

The expression in the article is the leading large-dimension approximation.

### 3. Deterministic mean matrix

For a matrix `H` whose entries all equal `gamma`, `HH^dagger` is rank one. It has one eigenvalue `alpha beta |gamma|^2` and `alpha-1` zero eigenvalues, not `alpha` identical nonzero eigenvalues.

The resulting dominant eigenvalue in the noisy model is an asymptotic strong-spike scale rather than an exact equality.

### 4. QFT

A global quantum Fourier transform does not generally preserve the Schmidt spectrum across a fixed bipartition. The overlap in the published numerical examples is specific to the chosen state families. The exact feasible boundary remains valid after a QFT because it applies to every valid spectrum, not because the trajectory is invariant.

### 5. Arithmetic union endpoint

`|P_(n-1)>` is product across the natural equal cut, but `|U_(n-1)>`, the equal superposition of every basis state except 0 and 1, has Schmidt rank two and strictly positive entropy for finite `n`. It approaches the product point rapidly as `n` grows.

### 6. Entanglement gap

The exact upper fixed-`lambda_max` gap uses `d-1`, not `d`. There is no universal inverse relation between entropy and gap over all spectra.

### 7. Additional direct corrections

- With natural logarithms, a one-qubit entropy is bounded by `log 2`, not 1.
- The post-SWAP Shor spectrum stated in the text is not normalized as written and must be corrected against the raw spectra.
- Quantum evolution may be continuous; plotted connecting segments merely fail to reconstruct unsampled dynamics.
- The empirical spectral distribution uses Dirac point masses; indicator functions describe its CDF.

## Scope clarifications

### Random matrix theory

Haar/Wishart and spiked-Wishart models are reference ensembles. Their typical curves are not exact or universal boundaries, and physical dynamics need not approach them.

### Computational usefulness

Neither low nor high scalar entropy alone determines classical simulability or quantum advantage. The repository no longer claims a universal narrow entropy band for useful quantum computation or that distance to an RMT curve measures computational value.

### Fingerprints and topology

The 2024 examples suggested recognizable path morphology. In the follow-up package, three non-equivalent exact-boundary-normalized metric classes have a shared standardized mode explaining approximately 90.26% of their total variance, and the relational geometry among trajectories remains substantially correlated across metric choices. The preservation is nevertheless hierarchical and local path structure is not invariant: exact vertical-turn counts agree across all three metrics on only 2 of 96 trajectories. Model-centroid morphology generalizes more strongly than unseen individual paths. The repository therefore uses quoted "topological invariant" only for an empirical coarse metric-robust trajectory class, not a formal topological invariant or a universal classifier.

## Corrected central statement

> Standard bipartite pure-state entanglement metrics are nonlinear projections of a common Schmidt-spectrum path. Across the quantum-chaos families tested in the follow-up package, exact-boundary-normalized trajectory projections preserve substantial model-specific morphology under changes of metric, while localized metric disagreements retain information about spectral redistribution that no single scalar measure captures.

## Detailed audit

The full location-by-location correction map is `metadata/paper_correction_ledger.csv`. Deterministic supporting calculations are generated under `outputs/paper_corrections/` by:

```bash
python analysis/verify_paper_corrections.py
```
