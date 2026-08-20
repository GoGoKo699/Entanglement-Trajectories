# Journal Corrigendum Core: Technical Outline

## Status

This is a technical outline, not a journal submission. It compresses the 58-entry repository ledger into eleven factual correction bundles. Interpretive reframing and the expanded trajectory-atlas philosophy remain in the repository clarification rather than the journal notice.

## Proposed correction bundles

### JC-01 — Exact entropy feasible region and Figure 1

- Ledger entries: `PC-001, PC-007, PC-008, PC-009, PC-010, PC-011`
- Replacement: Replace the approximate three-curve boundary by the exact finite-dimensional fixed-lambda_max envelopes. Correct the numerical coefficient in the Figure 1 caption.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/exact_boundary_comparison.csv`

### JC-02 — Continuity and plotted interpolation

- Ledger entries: `PC-012`
- Replacement: State that unitary evolution may be continuous; plotted connecting segments only encode temporal ordering and do not reconstruct unsampled evolution.
- Dependency before submission: none

### JC-03 — Entropy units in the Grover and Shor discussions

- Ledger entries: `PC-016, PC-020`
- Replacement: With natural logarithms, one bit equals ln 2 nats; replace bounds written as 1 accordingly.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/paper_verification_results.json`

### JC-04 — Stated post-SWAP Shor spectrum

- Ledger entries: `PC-022`
- Replacement: Withdraw the spectrum as written because it sums to 3/2. Insert a corrected spectrum only after direct verification against archived circuit outputs.
- Dependency before submission: raw Shor spectrum regeneration
- Verification: `outputs/paper_corrections/shor_spectrum_normalization.csv`

### JC-05 — Noncentral Wishart scaling and deterministic rank-one component

- Ledger entries: `PC-026, PC-027, PC-028, PC-029`
- Replacement: Use a consistent 1/beta scaling, replace the claimed alpha-fold eigenvalue by one nonzero eigenvalue alpha beta |gamma|^2, and make the outlier/bulk statements asymptotic.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/rank_one_mean_matrix.json`

### JC-06 — Exact Page mean and fixed-trace normalization

- Ledger entries: `PC-031, PC-032, PC-033`
- Replacement: Replace the theorem by H_{alpha beta}-H_beta-(alpha-1)/(2 beta). Label ln alpha-alpha/(2 beta) and the trace replacement as large-size approximations.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/page_formula_comparison.csv`

### JC-07 — Status of Equations (32) and (33)

- Ledger entries: `PC-034, PC-035, PC-036`
- Replacement: Relabel Equation (32) as a large-size separated-spike reference curve, not an exact conditional mean or boundary. State the additional large-alpha approximation in Equation (33).
- Dependency before submission: none
- Verification: `outputs/paper_corrections/spiked_reference_vs_exact_boundary.csv`

### JC-08 — Arithmetic-union endpoint

- Ledger entries: `PC-039`
- Replacement: State that U_{n-1} has Schmidt rank two and positive entropy for every finite even n; it approaches the product point asymptotically.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/prime_union_endpoint.csv`

### JC-09 — Global QFT and Schmidt-spectrum invariance

- Ledger entries: `PC-041, PC-042`
- Replacement: Remove the identification of a Fourier amplitude with a reduced-state eigenvalue and withdraw exact QFT preservation. Retain only state-family-specific numerical overlap.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/qft_counterexample.json`

### JC-10 — Exact entanglement-gap arena and entropy-gap interpretation

- Ledger entries: `PC-044, PC-045, PC-046`
- Replacement: Use the exact fixed-lambda_max gap extrema, relabel the MP-edge curve as a reference, and remove the universal entropy-gap monotonicity claim.
- Dependency before submission: none
- Verification: `outputs/paper_corrections/exact_gap_boundary.csv`, `outputs/paper_corrections/entropy_gap_counterexample.json`

### JC-11 — Renyi order zero and status of Renyi reference curves

- Ledger entries: `PC-051, PC-053, PC-054`
- Replacement: Define H_0 as log rank, state support/domain conventions, and label the MP-derived Renyi curves as ensemble references rather than exact boundaries.
- Dependency before submission: the current exact Renyi-extrema implementation

## Scope excluded from the journal notice

The following belong in the public repository clarification unless the journal requests otherwise:

- the full Schmidt-spectrum/metric-atlas philosophy;
- quantified follow-up evidence for metric-robust morphology;
- AI-oriented discovery metadata and terminology;
- broad discussion of computational usefulness, fingerprinting, and formal topology;
- software modernization and archival restructuring.

## Submission gate

Do not submit this outline as-is. First regenerate and verify the unresolved Shor spectra, freeze the final corrected repository release, and convert the bundles into concise page/equation replacements checked against the journal typeset version.
