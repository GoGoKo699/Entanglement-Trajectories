"""Dataset schemas and migration utilities for trajectory observations."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np


SCHEMA_VERSION = "trajectory-observations-1.0"

IDENTITY_COLUMNS: tuple[str, ...] = (
    "model",
    "n",
    "run_id",
    "regime",
    "initial_state",
    "step",
    "tau",
)

CANONICAL_METRIC_COLUMNS: tuple[str, ...] = (
    "one_site_mean_vn",
    "one_site_mean_linear",
    "one_site_mean_logneg",
    "one_site_mean_geometric_linear",
    "half_vn",
    "half_linear",
    "half_logneg",
    "half_geometric_linear",
    "half_lambda_max",
    "half_min_entropy",
)

CANONICAL_COLUMNS: tuple[str, ...] = (
    "schema_version",
    *IDENTITY_COLUMNS,
    "initial_state_seed",
    "disorder_seed",
    *CANONICAL_METRIC_COLUMNS,
)

LEGACY_METRIC_MAP: dict[str, str] = {
    "global_vn": "one_site_mean_vn",
    "global_mw": "one_site_mean_linear",
    "global_logneg": "one_site_mean_logneg",
    "global_geo": "one_site_mean_geometric_linear",
    "half_vn": "half_vn",
    "half_linear": "half_linear",
    "half_logneg": "half_logneg",
    "half_geo": "half_geometric_linear",
}

LEGACY_COLUMNS: tuple[str, ...] = (*IDENTITY_COLUMNS, *LEGACY_METRIC_MAP.keys())

LEGACY_REGIME_MAP: dict[str, str] = {
    # Preserve the dynamical parameters while removing unproved phase labels.
    "tilted_chaotic": "tilted_field",
    "perturbed": "phase_perturbed",
    "ergodic_weak_disorder": "weak_disorder",
    "localized_strong_disorder": "strong_disorder",
}


def validate_legacy_frame(frame) -> None:
    missing = sorted(set(LEGACY_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Legacy trajectory table is missing columns: {missing}")
    if frame.empty:
        raise ValueError("Trajectory table is empty.")
    for column in LEGACY_METRIC_MAP:
        values = frame[column].to_numpy(dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError(f"Column {column} contains nonfinite values.")
        if values.min() < -1e-8 or values.max() > 1.0 + 1e-8:
            raise ValueError(f"Column {column} lies outside [0,1].")


def validate_canonical_frame(frame) -> None:
    missing = sorted(set(CANONICAL_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Canonical trajectory table is missing columns: {missing}")
    if frame.empty:
        raise ValueError("Trajectory table is empty.")
    versions = set(frame["schema_version"].astype(str))
    if versions != {SCHEMA_VERSION}:
        raise ValueError(f"Unexpected schema versions: {sorted(versions)}")
    for column in CANONICAL_METRIC_COLUMNS:
        values = frame[column].to_numpy(dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError(f"Column {column} contains nonfinite values.")
        if column == "half_min_entropy":
            if values.min() < -1e-8 or values.max() > 1.0 + 1e-8:
                raise ValueError(f"Column {column} lies outside [0,1].")
        elif values.min() < -1e-8 or values.max() > 1.0 + 1e-8:
            raise ValueError(f"Column {column} lies outside [0,1].")


def legacy_to_canonical(frame):
    """Convert the historical 15-column CSV to the explicit current schema."""
    import pandas as pd

    from .models import disorder_seed, initial_state_seed

    validate_legacy_frame(frame)
    out = pd.DataFrame(index=frame.index.copy())
    out["schema_version"] = SCHEMA_VERSION
    for column in IDENTITY_COLUMNS:
        out[column] = frame[column]
    out["regime"] = frame["regime"].astype(str).replace(LEGACY_REGIME_MAP)
    out["initial_state_seed"] = [
        initial_state_seed(str(m), int(n), str(r))
        for m, n, r in zip(frame["model"], frame["n"], frame["run_id"])
    ]
    out["disorder_seed"] = [
        disorder_seed(str(m), int(n), str(r))
        for m, n, r in zip(frame["model"], frame["n"], frame["run_id"])
    ]
    for legacy, canonical in LEGACY_METRIC_MAP.items():
        out[canonical] = frame[legacy].astype(float)
    d = np.power(2.0, out["n"].to_numpy(dtype=int) // 2)
    geo = out["half_geometric_linear"].to_numpy(dtype=float)
    p = 1.0 - ((d - 1.0) / d) * geo
    p = np.clip(p, 1.0 / d, 1.0)
    out["half_lambda_max"] = p
    out["half_min_entropy"] = -np.log2(p) / np.log2(d)
    return out.loc[:, CANONICAL_COLUMNS]


def canonical_to_legacy(frame):
    """Return a backward-compatible table with the historical column names."""
    import pandas as pd

    validate_canonical_frame(frame)
    out = pd.DataFrame({column: frame[column] for column in IDENTITY_COLUMNS})
    reverse = {canonical: legacy for legacy, canonical in LEGACY_METRIC_MAP.items()}
    for canonical, legacy in reverse.items():
        out[legacy] = frame[canonical]
    return out.loc[:, LEGACY_COLUMNS]


def read_trajectory_csv(path: str | Path, *, canonical: bool = True):
    import pandas as pd

    frame = pd.read_csv(path)
    if "schema_version" in frame.columns:
        validate_canonical_frame(frame)
        return frame if canonical else canonical_to_legacy(frame)
    validate_legacy_frame(frame)
    return legacy_to_canonical(frame) if canonical else frame


def write_trajectory_csv(frame, path: str | Path, *, canonical: bool = True) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if canonical:
        validate_canonical_frame(frame)
        frame.loc[:, CANONICAL_COLUMNS].to_csv(path, index=False, float_format="%.17g")
    else:
        validate_legacy_frame(frame)
        frame.loc[:, LEGACY_COLUMNS].to_csv(path, index=False, float_format="%.17g")
    return path
