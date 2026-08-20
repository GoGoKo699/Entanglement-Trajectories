# Entanglement Trajectories

[![Paper DOI](https://img.shields.io/badge/Quantum-10.22331%2Fq--2024--03--14--1282-24557A)](https://doi.org/10.22331/q-2024-03-14-1282)
[![Python](https://img.shields.io/badge/Python-%E2%89%A53.10-3D7EA6)](pyproject.toml)
[![Code license](https://img.shields.io/badge/code-BSD--3--Clause-6D6BB5)](LICENSE)
[![Content license](https://img.shields.io/badge/content-CC--BY--4.0-55AFC9)](LICENSE)

**One Schmidt-spectrum path, many entanglement metrics.**

This repository is the corrected computational companion and follow-up evidence package for:

> Ruge Lin, “Entanglement Trajectory and its Boundary,” *Quantum* **8**, 1282 (2024). DOI: `10.22331/q-2024-03-14-1282`.

The journal article introduced an initial version of the idea. This repository preserves that insight, provides explicit mathematical corrections and scope clarifications, and tests the upgraded claim across four quantum-chaos families, six system sizes, and several non-equivalent functions of the Schmidt spectrum.

> **Central result.** For a fixed bipartition of a pure state, standard spectrum-based entanglement measures are nonlinear projections of one ordered Schmidt-spectrum path. Across the tested models, the normalized projections share a dominant common mode and preserve substantial coarse morphology, while local disagreements expose spectral redistributions that no single scalar measure can order completely.

![Conceptual map from one Schmidt-spectrum path to a trajectory atlas, shared morphology, and metric competition](figures/public/figure_01_one_spectrum_many_lenses.png)

## The object that unifies the metrics

For a pure state and a fixed bipartition, write the ordered reduced-density-matrix spectrum as

$$
\Gamma:t\longmapsto \boldsymbol{\lambda}(t)
=\bigl(\lambda_1(t),\ldots,\lambda_d(t)\bigr).
$$

A spectrum functional $E$ gives a projected trajectory

$$
\Gamma_E(t)=\bigl(\lambda_{\max}(t),E[\boldsymbol{\lambda}(t)]\bigr).
$$

The family $\{\Gamma_E\}$ is the **entanglement-trajectory atlas**. In the supplied follow-up data, the main fixed-cut lenses represent four separated Rényi sectors:

| Spectral lens | Implemented coordinate | What it emphasizes |
|---|---|---|
| $q=\tfrac12$ | pure-state logarithmic negativity | small and intermediate Schmidt weights |
| $q=1$ | von Neumann entropy | the spectrum in aggregate |
| $q=2$ class | linear entropy / purity | larger Schmidt weights |
| $q=\infty$ | $\lambda_{\max}$ / min-entropy / geometric class | the leading Schmidt weight |

These are not four unrelated definitions. They are different compressions of the same spectrum. They are also not redundant with one another, except within the explicitly documented equivalence classes.

## Exact geometry before random-matrix theory

At fixed $p=\lambda_{\max}$, every compatible $d$-dimensional spectrum lies between two majorization extremizers.

The equal-tail spectrum

$$
\boldsymbol u(p)=\left(p,\frac{1-p}{d-1},\ldots,\frac{1-p}{d-1}\right)
$$

maximizes every Schur-concave metric used here. The concentrated spectrum

$$
\boldsymbol c(p)=
(\underbrace{p,\ldots,p}_{k\ \mathrm{times}},r,0,\ldots,0),
\qquad
k=\left\lfloor\frac1p\right\rfloor,
\quad r=1-kp,
$$

minimizes it. These spectra define exact finite-dimensional feasible envelopes and a common boundary-relative coordinate for comparing different metrics.

![Exact fixed-largest-eigenvalue feasible arenas for von Neumann entropy, linear entropy, and pure-state logarithmic negativity](figures/public/figure_02_exact_metric_arenas.png)

Random matrix theory enters only afterward, as a family of Haar/Wishart or spiked-Wishart **reference ensembles** inside the exact arena. It does not define the exact boundary.

## What the follow-up study establishes

The included dataset contains 5,856 observations from 96 trajectories: four model families, four conditions per family, and sizes $n=10,12,14,16,18,20$.

| Controlled result | Value | Interpretation |
|---|---:|---|
| Common normalized metric mode | **90.26%** of variance | a strong shared trajectory component |
| Cluster-bootstrap 95% interval | **85.74%–93.79%** | uncertainty clustered by dynamical run |
| Median per-trajectory common-mode fraction | **94.75%** | the shared mode is not produced by only a few paths |
| Boundary-normalized rank agreement | **0.692–0.947** | robustness is strong but metric-pair dependent |
| Metric-competitive scalar steps | **808/5,760 = 14.03%** | disagreement is real, not excluded by the framework |
| Competition in selected full-spectrum audit | **50 events** | all 50 occur on majorization-incomparable transitions |
| Exact turn counts equal across all three metrics | **2/96 trajectories** | fine projected topology is not invariant |
| Held-out-size model-centroid accuracy | **0.917** | model-level morphology is reproducible |
| Size-and-condition-held-out individual accuracy | **0.368** | universal individual fingerprinting remains preliminary |

![Common-mode strength, cross-size agreement, and the distinction between coarse and fine path properties](figures/public/figure_03_metric_robustness_hierarchy.png)

### Agreement and disagreement have one mechanism

If two successive Schmidt spectra are comparable by majorization, all Schur-concave entropies must order them consistently. If they are incomparable, different Rényi sectors may legitimately move in opposite directions.

The selected full-spectrum audit contains 400 transitions:

- 111 majorization-compatible entanglement increases;
- 9 majorization-compatible decreases;
- 280 incomparable transitions;
- 50 metric-competition events, all in the incomparable sector.

Incomparability permits disagreement but does not require it: 230 incomparable transitions still show metric consensus.

![An explicit metric-order reversal, the majorization audit, and model-dependent competition rates](figures/public/figure_04_majorization_and_metric_competition.png)

## What the quoted “topological invariant” means

The phrase is retained as a historical conceptual label, but it is used only in the following operational sense:

> **A metric-robust trajectory class is the coarse path morphology that remains recognizable when one declared Schmidt-spectrum metric is replaced by another.**

**No formal topological invariant has been proved.**

It does **not** currently mean equality of coordinates, preservation of every turn or crossing, a homeomorphism, a homotopy class, a winding-number theorem, persistent-homology invariance, or universality over all cuts, states, dynamics, and notions of entanglement.

The preferred technical terms are **metric-robust trajectory class** and **projection-stable trajectory morphology**.

![Model-centroid common-mode trajectories and the limits of held-out fingerprint classification](figures/public/figure_05_model_morphology_and_limits.png)

## Corrections to the 2024 paper

The paper remains the journal version of record. This repository supplies an explicit author-correction layer. The central trajectory idea survives, but several statements require correction or narrowing. The most important are:

1. The paper’s three simple curves are not the exact counterexample-free boundary; the exact piecewise envelopes follow from majorization.
2. The stated Page expression is asymptotic; the exact finite-dimensional mean uses harmonic numbers.
3. The deterministic mean part of the noncentral Wishart construction is rank one, with one nonzero eigenvalue.
4. A global quantum Fourier transform does not generally preserve a Schmidt spectrum; the observed overlap is family-specific and numerical.
5. Random-matrix curves are conditional references, not exact boundaries or universal attractors.
6. “Topological invariant,” fingerprint, entanglement-gap, continuity, and computational-usefulness claims must be read with the narrower scope documented here.

Read the [correction summary](CORRECTIONS.md), the [author clarification](paper/AUTHOR_CLARIFICATION_2026.md), and the [location-specific correction ledger](metadata/paper_correction_ledger.csv).

## Reproduce the results

Python 3.10 or later is required.

```bash
python -m pip install -e '.[analysis,test]'
```

Rebuild the machine-facing context and five public figures from the canonical documents and included data:

```bash
make public-context
make public-figures
```

Run the automated tests and public metadata/link validation:

```bash
make test
make public-validate
```

The combined public-layer workflow is:

```bash
make public
```

Rebuild all analyses from the included trajectory and selected-spectrum data:

```bash
make rebuild-included
```

The complete state-vector regeneration through 20 qubits is separate and expensive:

```bash
make full
```

See [Reproducibility](docs/REPRODUCIBILITY.md) for output locations, deterministic seeds, numerical tolerances, and the distinction between included-data reconstruction and full simulation.

## Reading paths

| Time | Recommended path |
|---|---|
| 30 seconds | this summary and Figure 1 |
| 5 minutes | [Results at a glance](docs/RESULTS_AT_A_GLANCE.md) and [Corrections](CORRECTIONS.md) |
| 20 minutes | [Scientific overview](docs/SCIENTIFIC_OVERVIEW.md) and [Public figure story](docs/PUBLIC_FIGURE_STORY.md) |
| Technical audit | [Exact spectral geometry](docs/EXACT_SPECTRAL_GEOMETRY.md), [Analysis methods](docs/ANALYSIS_METHODS.md), and [Release QA](docs/RELEASE_QA.md) |
| Reproduction | [Reproducibility](docs/REPRODUCIBILITY.md) |
| AI or automated research assistant | [AI context](AI_CONTEXT.md) and [public claims JSON](metadata/public_claims.json) |
| Historical record | `legacy/` and the `paper-2024-original` branch |

## Repository map

```text
src/entanglement_trajectories/   canonical metrics, boundaries, models, and robustness tools
analysis/                        quantitative robustness and correction verification
scripts/                         reproducible simulations, figures, and validation workflows
data/                            canonical trajectories and compact spectrum/figure-input archives
figures/public/                  five GitHub-facing figures and the social preview
docs/                            scientific explanation, methods, limitations, and FAQ
paper/                           author clarification and narrow corrigendum draft
metadata/                        claims, definitions, metrics, figures, corrections, and manifest
legacy/                          provenance archive and historical-branch instructions
```

## Citation

The preferred citation is the published article:

```bibtex
@article{lin2024entanglement,
  title   = {Entanglement Trajectory and its Boundary},
  author  = {Lin, Ruge},
  journal = {Quantum},
  volume  = {8},
  pages   = {1282},
  year    = {2024},
  doi     = {10.22331/q-2024-03-14-1282}
}
```

Machine-readable citation records are provided in [`CITATION.cff`](CITATION.cff) and [`codemeta.json`](codemeta.json).

## Scope and nonclaims

This repository concerns pure-state dynamics, specified bipartitions or explicitly declared averages over cuts, and the implemented spectrum functionals. It does not silently extend the claim to mixed-state entanglement, genuine multipartite invariants, discord-like quantities, entanglement cost, every possible metric, or every notion of quantum chaos.

The complete public nonclaim list is maintained in [AI_CONTEXT.md](AI_CONTEXT.md) and [Limitations](docs/LIMITATIONS.md).

## Repository-edition status

Version `1.0.0` is the corrected public repository edition. It freezes the exact mathematical layer, the repaired follow-up computation, the quantitative metric-robustness result, the paper-correction record, and the human/AI discovery layer. The narrow journal corrigendum is recommended and drafted, but has not yet been submitted.
