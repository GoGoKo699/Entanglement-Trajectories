# Public Figure Story

The five public figures are organized as a reader question chain. Each figure has one primary task and a machine-readable registry entry in `metadata/figure_registry.json`.

## Figure 1 — What unifies the many entanglement metrics?

**Question:** Are the metrics unrelated definitions, or different views of one object?

**Answer:** For a fixed cut of a pure state, the ordered Schmidt-spectrum path is the common latent object. The declared entanglement metrics form a trajectory atlas. The atlas contains both a shared coarse mode and informative local disagreements.

**File:** `figures/public/figure_01_one_spectrum_many_lenses.png`

**Claim boundary:** conceptual organization plus exact common origin. It does not assert empirical strength by itself.

## Figure 2 — What part is exact?

**Question:** How can different metrics be compared without confusing their ranges and nonlinear feasible regions?

**Answer:** At fixed largest Schmidt value, majorization gives exact concentrated-spectrum and equal-tail boundaries. The included $n=20$ observations lie inside those finite-dimensional arenas. Boundary-relative normalization places the metrics on a common spectral stage.

**File:** `figures/public/figure_02_exact_metric_arenas.png`

**Claim boundary:** exact finite-dimensional spectrum geometry. The orange points illustrate the supplied data but are not needed for the theorem.

## Figure 3 — How strong is metric robustness?

**Question:** Is the shared shape merely visual, and is every detail preserved?

**Answer:** A dominant normalized common mode explains 90.26% of variance, and pairwise agreement persists across sizes. Full-path arc-length ordering is strong, vertical-only total-variation ordering is weaker but substantial for some metric pairs, and exact turn-count agreement is weak. Robustness is hierarchical, not exact.

**File:** `figures/public/figure_03_metric_robustness_hierarchy.png`

**Claim boundary:** controlled empirical evidence over the included model families, conditions, sizes, and metric classes.

## Figure 4 — How can valid metrics contradict one another?

**Question:** Does disagreement invalidate the unification?

**Answer:** No. An explicit incomparable pair reverses the metric ordering between Rényi sectors. In the selected complete-spectrum audit, competition appears only among majorization-incomparable transitions and varies strongly by dynamics.

**File:** `figures/public/figure_04_majorization_and_metric_competition.png`

**Claim boundary:** majorization gives a necessary domain for disagreement, not a sufficient condition. Many incomparable transitions still show consensus.

## Figure 5 — Do trajectories carry model information?

**Question:** Does the shared mode retain model-specific morphology, and how far does fingerprinting generalize?

**Answer:** Model-centroid full paths remain separated across held-out sizes, but vertical-only cross-metric transfer is substantially weaker. Individual-run accuracy falls sharply under unseen size-and-condition holdout and does not beat the largest-Schmidt-value path baseline in that strict test.

**File:** `figures/public/figure_05_model_morphology_and_limits.png`

**Claim boundary:** supports model-level morphology within the tested scope. It does not establish a universal individual-run fingerprint.

## Plot provenance

Run:

```bash
make public-figures
```

The builder is `scripts/build_public_figures.py`. Each plot has a compact CSV or JSON source table under `outputs/public_figures/data/`. The end-to-end rebuild passes freshly recomputed analysis tables explicitly to the builder.
