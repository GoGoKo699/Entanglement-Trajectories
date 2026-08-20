# Historical Material

The supported current implementation is located under:

```text
src/entanglement_trajectories/
scripts/
analysis/
tests/
```

Historical material is preserved for provenance, comparison, and reconstruction of the development record. It is not the current scientific or computational source of truth.

## Original 2024 repository state

The exact paper-era repository is preserved on the branch:

```text
paper-2024-original
```

at commit:

```text
81206df955622c31225f0d4f9c290e35d41ba381
```

That branch contains the original flat collection of figure-generation scripts associated with the published article.

The historical scripts were removed from the corrected `main` branch because several depended on obsolete software, unavailable inputs, incomplete conventions, or formulas superseded by the correction layer. Removing them from `main` prevents historical filenames from being mistaken for the supported implementation.

## Additional provenance archive

The file

```text
legacy/historical_sources.zip
```

preserves the original follow-up package and frozen repository metadata used during the forensic reconstruction.

## Authority order

When historical and current files differ, use the following order:

1. `metadata/public_claims.json` and `metadata/definitions.json`;
2. `SCIENTIFIC_POSITION.md`;
3. `CORRECTIONS.md` and `paper/AUTHOR_CLARIFICATION_2026.md`;
4. the exact mathematics and empirical-results documents under `docs/`;
5. the supported code and tests under `src/`, `analysis/`, `scripts/`, and `tests/`;
6. historical material under this directory and the `paper-2024-original` branch.

Historical code documents what was previously implemented. It does not override the corrected mathematical formulas, scientific qualifications, or current tested implementation.

## Licensing

The new-code and corrected-content licenses do not automatically relicense archived historical material.

- Current source code: BSD 3-Clause.
- New documentation, public figures, metadata, and curated data: CC BY 4.0.
- The published journal article remains governed by its publisher’s license.
- Archived files retain their previous legal status unless an individual file states otherwise.
