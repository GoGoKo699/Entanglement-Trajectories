#!/usr/bin/env python3
"""Compare committed and regenerated public-figure source tables.

Non-CSV files must be byte-identical. CSV files must have the same file set,
row order, column order, nonnumeric values, finite/NaN pattern, and numerical
values within explicitly declared floating-point tolerances. This avoids
mistaking harmless last-bit CSV serialization differences for scientific
provenance failures while still rejecting material changes.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


@dataclass(frozen=True)
class NumericDifference:
    file: str
    column: str
    max_absolute: float
    max_relative: float


def _files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _string_values(series: pd.Series) -> np.ndarray:
    return series.astype("string").fillna("<NA>").to_numpy(dtype=str)


def _compare_csv(
    reference: Path,
    candidate: Path,
    *,
    relative_name: str,
    atol: float,
    rtol: float,
) -> tuple[list[str], list[NumericDifference]]:
    errors: list[str] = []
    differences: list[NumericDifference] = []

    left = pd.read_csv(reference)
    right = pd.read_csv(candidate)

    if list(left.columns) != list(right.columns):
        return [
            f"{relative_name}: column mismatch; "
            f"reference={list(left.columns)!r}, candidate={list(right.columns)!r}"
        ], differences
    if left.shape != right.shape:
        return [
            f"{relative_name}: shape mismatch; "
            f"reference={left.shape}, candidate={right.shape}"
        ], differences

    for column in left.columns:
        left_series = left[column]
        right_series = right[column]
        left_numeric = is_numeric_dtype(left_series.dtype)
        right_numeric = is_numeric_dtype(right_series.dtype)

        if left_numeric != right_numeric:
            errors.append(
                f"{relative_name}:{column}: dtype class mismatch; "
                f"reference={left_series.dtype}, candidate={right_series.dtype}"
            )
            continue

        if not left_numeric:
            left_values = _string_values(left_series)
            right_values = _string_values(right_series)
            mismatch = np.flatnonzero(left_values != right_values)
            if mismatch.size:
                index = int(mismatch[0])
                errors.append(
                    f"{relative_name}:{column}: nonnumeric mismatch at row {index}; "
                    f"reference={left_values[index]!r}, candidate={right_values[index]!r}"
                )
            continue

        left_values = left_series.to_numpy(dtype=np.float64)
        right_values = right_series.to_numpy(dtype=np.float64)
        finite_pattern_equal = np.array_equal(np.isfinite(left_values), np.isfinite(right_values))
        nan_pattern_equal = np.array_equal(np.isnan(left_values), np.isnan(right_values))
        if not finite_pattern_equal or not nan_pattern_equal:
            errors.append(f"{relative_name}:{column}: finite/NaN pattern mismatch")
            continue

        close = np.isclose(
            left_values,
            right_values,
            atol=atol,
            rtol=rtol,
            equal_nan=True,
        )
        if not np.all(close):
            index = int(np.flatnonzero(~close)[0])
            errors.append(
                f"{relative_name}:{column}: numerical mismatch at row {index}; "
                f"reference={left_values[index]:.17g}, "
                f"candidate={right_values[index]:.17g}, "
                f"atol={atol:.1e}, rtol={rtol:.1e}"
            )

        finite = np.isfinite(left_values) & np.isfinite(right_values)
        if np.any(finite):
            absolute = np.abs(left_values[finite] - right_values[finite])
            denominator = np.maximum(
                np.maximum(np.abs(left_values[finite]), np.abs(right_values[finite])),
                np.finfo(np.float64).tiny,
            )
            relative = absolute / denominator
            differences.append(
                NumericDifference(
                    file=relative_name,
                    column=str(column),
                    max_absolute=float(np.max(absolute)),
                    max_relative=float(np.max(relative)),
                )
            )

    return errors, differences


def compare_directories(
    reference_root: Path,
    candidate_root: Path,
    *,
    atol: float,
    rtol: float,
) -> tuple[list[str], list[NumericDifference], int, int]:
    reference_files = _files(reference_root)
    candidate_files = _files(candidate_root)
    errors: list[str] = []

    reference_names = set(reference_files)
    candidate_names = set(candidate_files)
    missing = sorted(reference_names - candidate_names)
    extra = sorted(candidate_names - reference_names)
    if missing:
        errors.append(f"candidate is missing files: {missing}")
    if extra:
        errors.append(f"candidate has unexpected files: {extra}")

    differences: list[NumericDifference] = []
    csv_count = 0
    exact_count = 0
    for relative_name in sorted(reference_names & candidate_names):
        reference = reference_files[relative_name]
        candidate = candidate_files[relative_name]
        if reference.suffix.lower() == ".csv":
            csv_count += 1
            csv_errors, csv_differences = _compare_csv(
                reference,
                candidate,
                relative_name=relative_name,
                atol=atol,
                rtol=rtol,
            )
            errors.extend(csv_errors)
            differences.extend(csv_differences)
        else:
            exact_count += 1
            if reference.read_bytes() != candidate.read_bytes():
                errors.append(f"{relative_name}: non-CSV file is not byte-identical")

    return errors, differences, csv_count, exact_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--atol", type=float, default=1e-10)
    parser.add_argument("--rtol", type=float, default=1e-10)
    args = parser.parse_args()

    reference = args.reference.resolve()
    candidate = args.candidate.resolve()
    if not reference.is_dir():
        raise SystemExit(f"reference directory not found: {reference}")
    if not candidate.is_dir():
        raise SystemExit(f"candidate directory not found: {candidate}")
    if args.atol < 0.0 or args.rtol < 0.0:
        raise SystemExit("atol and rtol must be nonnegative")

    errors, differences, csv_count, exact_count = compare_directories(
        reference,
        candidate,
        atol=args.atol,
        rtol=args.rtol,
    )
    if errors:
        print("PUBLIC FIGURE SOURCE COMPARISON: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    if differences:
        worst_absolute = max(differences, key=lambda item: item.max_absolute)
        worst_relative = max(differences, key=lambda item: item.max_relative)
        absolute_text = (
            f"{worst_absolute.max_absolute:.3e} "
            f"({worst_absolute.file}:{worst_absolute.column})"
        )
        relative_text = (
            f"{worst_relative.max_relative:.3e} "
            f"({worst_relative.file}:{worst_relative.column})"
        )
    else:
        absolute_text = "0"
        relative_text = "0"

    print(
        "PUBLIC FIGURE SOURCE COMPARISON: PASS "
        f"({csv_count} CSV files numerically equivalent at "
        f"atol={args.atol:.1e}, rtol={args.rtol:.1e}; "
        f"{exact_count} non-CSV files byte-identical; "
        f"worst_abs={absolute_text}; worst_rel={relative_text})"
    )


if __name__ == "__main__":
    main()
