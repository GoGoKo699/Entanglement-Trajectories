# Trajectory fingerprints: generalization tests and limits

## Why this test is needed

A visually recognizable path is not automatically a reproducible fingerprint. A useful fingerprint should retain information when system size, condition, and metric are changed, and it should outperform simpler coordinates such as \(\lambda_{\max}\) alone.

The analysis uses a deliberately simple nearest-centroid classifier to test the claim without optimizing a machine-learning pipeline.

## Model-centroid result

For model-centroid paths with one system size held out, the same-metric full-path accuracy is

\[
0.875,
\]

and the mean cross-metric accuracy is

\[
0.674.
\]

Chance accuracy is 0.25. The \(\lambda_{\max}\)-only path baseline is 0.75.

This supports a limited statement: averaged model-family morphology is often recognizable across sizes and retains substantial cross-metric information. It does not establish that every metric adds information beyond the common horizontal coordinate for every train-test pairing.

## Individual-trajectory result

For unseen individual trajectories with one size held out, same-metric and cross-metric full-path accuracies are both about 0.52. Under the stricter simultaneous held-out-size and held-out-condition test:

- same-metric full-path mean accuracy: 0.330;
- cross-metric full-path mean accuracy: 0.358;
- \(\lambda_{\max}\)-only path baseline: 0.417.

The individual-path metric atlas does not beat the shared horizontal coordinate under the most stringent test. The data support **model-level morphology more strongly than individual-run identification**.

## Interpretation

Model-centroid trajectory morphology is distinguishable and partly transferable across entanglement metrics and system sizes in the supplied study. Generalization is measured within the four tested model families and their declared conditions.

The strict individual-trajectory holdout limits the fingerprint interpretation: full-path accuracy is below the \(\lambda_{\max}\)-only baseline, and transfer to arbitrary states, cuts, parameters, or unseen model families is outside the measured scope.

## Vertical-coordinate-only result

Full-path classification includes the shared $\lambda_{\max}$ coordinate. Under the gap-aware analysis, held-out-size model-centroid accuracy is 0.764 in the same vertical metric and 0.375 across vertical metrics, compared with 0.875 and 0.674 for the full path. Under simultaneous held-out size and condition, the vertical-only values are 0.309 and 0.276, compared with 0.330 and 0.358 for the full path. Figure 5 therefore reports full-path, vertical-only, and $\lambda_{\max}$-only results together.
