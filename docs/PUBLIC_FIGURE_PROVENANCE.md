# Public-Figure Provenance

## Two deliberately separate workflows

The repository supports two figure-building modes.

### Frozen snapshot mode

```bash
make public-figures
```

This mode extracts `data/public_analysis_inputs.zip`. It is a fast check that
the committed public figures can be reconstructed from the compact release
snapshot without recomputing the full robustness analysis.

### Fresh end-to-end mode

```bash
make rebuild-included
```

This mode recomputes the metric-robustness, classification, majorization, and
fine-descriptor tables under `outputs/rebuild/results/`. It then calls:

```bash
python scripts/build_public_figures.py \
  --analysis-input-dir outputs/rebuild/results \
  --trajectory-input data/trajectory_observations.csv \
  --output-dir outputs/rebuild/public_figures
```

When `--analysis-input-dir` is supplied, the builder does not open the frozen
analysis-input archive.

## Required fresh inputs

The public figures consume the following analysis outputs:

```text
common_metric_modes.json
common_mode_timeseries.csv
fine_descriptor_robustness_summary.csv
majorization_transition_audit.csv
metric_pair_robustness_by_size.csv
metric_robustness_scientific_summary.json
```

Figure 2 obtains its observations directly from
`data/trajectory_observations.csv` and derives normalized min-entropy from
`half_lambda_max`; it does not require the historical
`reference_enriched_timeseries.csv` table.

## Machine-readable record

Every builder run writes:

```text
<output-dir>/data/public_figure_input_provenance.json
```

The record includes:

- archive or directory input mode;
- the declared analysis source;
- every required input filename, byte size, and SHA-256 digest;
- the canonical trajectory-table path, size, and digest;
- the figures requested;
- the output directory.

## Controlled perturbation test

The automated test suite performs two focused Figure 3 builds:

1. one from the frozen archive;
2. one from an explicit analysis directory in which the common-mode table is
   deliberately changed.

The test requires the resulting PNG digests to differ and verifies that the
plotted source CSV contains the changed numerical value. This closes the
failure mode in which a recomputed result could change while the public figure
silently continued to read an unrelated frozen archive.

## Hosted snapshot comparison

The locked GitHub Actions job rebuilds the snapshot under the canonical
CPython 3.11.15 environment. Nonnumeric provenance records must be
byte-identical. CSV source tables must have identical files, schemas, row
order, nonnumeric entries, and finite/NaN patterns; numeric entries are
compared with explicit absolute and relative tolerances of `1e-10`.

This distinction is deliberate. CSV text produced from the same floating-point
calculation can differ in harmless final decimal digits across Python/pandas
serialization paths. The comparator reports the worst absolute and relative
difference and still rejects any material numerical change. The canonical raw
trajectory and spectrum archives are not rounded or rewritten by this check.

Run the comparison directly with:

```bash
python scripts/compare_public_figure_data.py \
  --reference figures/public/data \
  --candidate outputs/public_figures/data \
  --atol 1e-10 --rtol 1e-10
```
