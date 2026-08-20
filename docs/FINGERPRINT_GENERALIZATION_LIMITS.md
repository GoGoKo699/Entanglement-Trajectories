# Trajectory fingerprints: generalization tests and limits

## Why this test is needed

A visually recognizable path is not automatically a reproducible fingerprint. A useful fingerprint should retain information when system size, condition, and metric are changed, and it should outperform simpler coordinates such as \(\lambda_{\max}\) alone.

The analysis uses a deliberately simple nearest-centroid classifier to test the claim without optimizing a machine-learning pipeline.

## Model-centroid result

For model-centroid paths with one system size held out, the same-metric full-path accuracy is

\[
0.917,
\]

and the mean cross-metric accuracy is

\[
0.694.
\]

Chance accuracy is 0.25. The \(\lambda_{\max}\)-only path baseline is 0.75.

This supports a limited statement: averaged model-family morphology is often recognizable across sizes and retains substantial cross-metric information. It does not establish that every metric adds information beyond the common horizontal coordinate for every train-test pairing.

## Individual-trajectory result

For unseen individual trajectories with one size held out, same-metric and cross-metric full-path accuracies are both about 0.52. Under the stricter simultaneous held-out-size and held-out-condition test:

- same-metric mean accuracy: 0.368;
- cross-metric mean accuracy: 0.398;
- \(\lambda_{\max}\)-only path baseline: 0.417.

The individual-path metric atlas therefore does not yet beat the shared horizontal coordinate under the most stringent test. The correct conclusion is not that fingerprints fail completely, but that the present data support **model-level morphology more strongly than universal individual-run identification**.

## What may be said publicly

Supported:

> Model-centroid trajectory morphology is distinguishable and partly transferable across entanglement metrics and system sizes in the supplied study.

Preliminary:

> Individual trajectories may contain model information beyond endpoints, but stronger datasets and held-out conditions are required.

Not supported:

- a universal trajectory classifier;
- identification of an unseen model family;
- robustness to arbitrary parameters, cuts, initial states, or time samplings;
- a claim that the metric atlas consistently outperforms \(\lambda_{\max}\) alone.

## Stronger future test

A publication-level fingerprint study would require a preregistered feature map and held-out:

- disorder realizations;
- initial states;
- parameter values;
- bipartitions;
- time resolutions;
- system sizes;
- entirely unseen dynamical families.

It should compare entropy-only, \(\lambda_{\max}\)-only, endpoint-only, full-spectrum, and combined-atlas baselines.
