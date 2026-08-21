# Canonical Release Environment

## Purpose

The project keeps broad lower bounds in `pyproject.toml` so that the library can be used in newer compatible environments. Those bounds are not the archival numerical environment for release `v1.0.0`.

The canonical hosted release job is frozen separately:

| Component | Canonical value |
|---|---|
| Operating system | `ubuntu-24.04` GitHub-hosted runner |
| Architecture | `x86_64` |
| Python | CPython `3.11.15` |
| Python version file | `.python-version` |
| Build-tool lock | `requirements/release-build.txt` |
| Numerical/test lock | `requirements/release-py311.txt` |
| Machine-readable record | `environment/release-py311.json` |

The numerical and test-package versions were frozen from the dependency installation recorded in GitHub Actions run `32348216286` on 20 August 2026. That run installed the environment successfully; its later failures were in repository-file counting and an over-tight cross-backend regression tolerance, both repaired before this environment was frozen.

## Reproduce the canonical environment

Create an isolated CPython `3.11.15` environment and run:

```bash
python -m pip install -r requirements/release-build.txt
python -m pip install -r requirements/release-py311.txt
python -m pip install --no-deps --no-build-isolation -e .
python -m pip check
python scripts/verify_release_environment.py
make public
```

The verifier checks the exact Python patch version, every pinned Python distribution, and the deterministic environment variables used by CI.

## Determinism controls

The release job fixes:

```text
PYTHONHASHSEED=0
MPLBACKEND=Agg
OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
TZ=UTC
```

The single-thread settings reduce backend-dependent numerical variation in eigensolvers and reductions. They do not make results from different operating systems, CPU architectures, BLAS implementations, or Python versions bitwise identical.

## Release workflow

The external actions are referenced by full immutable commit SHAs, with their reviewed release tags recorded in `environment/release-py311.json`.

The blocking GitHub Actions job:

1. uses `ubuntu-24.04` and CPython `3.11.15`;
2. installs the two exact requirement locks;
3. installs this repository without dependency resolution;
4. runs `pip check` and the release-environment verifier;
5. rebuilds `llms-full.txt` and the public figures;
6. checks that the generated machine context and plotted source tables match the committed release records and that every public image renders successfully;
7. runs the scientific tests and public repository validator.

A green run on the final release commit is required before tagging `v1.0.0`.

## Compatibility outside the lock

A normal development installation remains:

```bash
python -m pip install -e '.[analysis,test]'
```

Such an installation is supported for development and portability testing, but it is not the canonical environment for reproducing the release-level numerical snapshots.
