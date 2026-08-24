# Start Here

## Thirty-second version

The project asks what unifies the many scalar measures of bipartite pure-state entanglement.

The answer is the ordered Schmidt-spectrum path. Von Neumann entropy, Rényi entropies, purity, pure-state logarithmic negativity, min-entropy, geometric coordinates, and related quantities are different nonlinear observations of this path. Their projected paths form an **entanglement-trajectory atlas**.

Across four tested dynamical families used to probe scrambling, recurrence, disorder, and spectral complexity, the normalized trajectories share a strong common mode while retaining localized, mathematically permitted disagreements. This supports a **metric-robust trajectory class**, not a formal topological invariant.

Start with [Figure 1 and the README](README.md).

## Five-minute version

Read, in order:

1. [Results at a glance](docs/RESULTS_AT_A_GLANCE.md)
2. [Corrections to the 2024 paper](CORRECTIONS.md)
3. [Operational meaning of the quoted topological invariant](docs/OPERATIONAL_TOPOLOGICAL_INVARIANT.md)
4. [Limitations](docs/LIMITATIONS.md)

## Technical path

1. [Scientific overview](docs/SCIENTIFIC_OVERVIEW.md)
2. [Exact spectral geometry](docs/EXACT_SPECTRAL_GEOMETRY.md)
3. [Metric taxonomy](docs/METRIC_TAXONOMY.md)
4. [Majorization dynamics](docs/MAJORIZATION_AND_METRIC_DISAGREEMENT.md)
5. [Analysis methods](docs/ANALYSIS_METHODS.md)
6. [Fingerprint generalization limits](docs/FINGERPRINT_GENERALIZATION_LIMITS.md)
7. [Peer-review release audit](docs/PEER_REVIEW_RELEASE_AUDIT.md)
8. [Conceptual neighbors](docs/CONCEPTUAL_NEIGHBORS.md)
9. [Canonical release environment](docs/RELEASE_ENVIRONMENT.md)

## Reproduction path

```bash
python -m pip install -e '.[analysis,test]'
make public-context
make public-figures
make test
make public-validate
make peer-review-check
make rebuild-included
```

See [Reproducibility](docs/REPRODUCIBILITY.md) before running the expensive `make full` workflow.

## Machine-assisted research path

Use [AI_CONTEXT.md](AI_CONTEXT.md) as the canonical prose context and `metadata/public_claims.json` as the scoped claim registry. For literature discovery, use [Conceptual neighbors](docs/CONCEPTUAL_NEIGHBORS.md) and `metadata/conceptual_neighbors.json`. The authority order and common misinterpretations are recorded explicitly.
