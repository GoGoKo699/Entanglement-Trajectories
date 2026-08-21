#!/usr/bin/env python3
"""Validate the canonical v1.0.0 release environment.

The default mode verifies the running interpreter, every pinned package, and
thread/determinism variables. ``--structure-only`` checks repository metadata
without requiring the caller to be inside the canonical environment.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "environment" / "release-py311.json"
PYTHON_VERSION = ROOT / ".python-version"


def canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_exact_requirements(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.count("==") != 1:
            raise ValueError(f"Release lock entry is not exact: {line!r}")
        name, version = line.split("==", 1)
        key = canonical_name(name.strip())
        if not key or not version.strip():
            raise ValueError(f"Malformed release lock entry: {line!r}")
        if key in result:
            raise ValueError(f"Duplicate release lock entry: {key}")
        result[key] = version.strip()
    return result


def validate_structure(record: dict) -> list[str]:
    errors: list[str] = []
    expected_python = PYTHON_VERSION.read_text(encoding="utf-8").strip()
    recorded_python = record["canonical_job"]["python_version"]
    if expected_python != recorded_python:
        errors.append(
            f".python-version={expected_python!r} differs from environment record={recorded_python!r}"
        )

    for key in ("build_requirements_file", "runtime_requirements_file"):
        relative = record[key]
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing requirements file: {relative}")
            continue
        locked = parse_exact_requirements(path)
        expected = {
            canonical_name(name): str(version)
            for name, version in record[
                "build_packages" if key == "build_requirements_file" else "packages"
            ].items()
        }
        if locked != expected:
            errors.append(f"{relative} differs from environment/release-py311.json")

    variables = record.get("determinism_environment", {})
    if not variables or any(str(value) == "" for value in variables.values()):
        errors.append("determinism_environment is missing or contains empty values")
    return errors


def validate_running_environment(record: dict, *, check_threads: bool) -> tuple[list[str], dict]:
    errors: list[str] = []
    observed: dict[str, object] = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": {},
        "environment": {},
    }
    expected_python = record["canonical_job"]["python_version"]
    if platform.python_version() != expected_python:
        errors.append(
            f"Python {platform.python_version()} is running; canonical release requires {expected_python}"
        )
    if platform.python_implementation() != record["canonical_job"]["python_implementation"]:
        errors.append("unexpected Python implementation")

    expected_distributions = {**record.get("build_packages", {}), **record["packages"]}
    for name, expected_version in expected_distributions.items():
        try:
            observed_version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"missing package: {name}=={expected_version}")
            continue
        observed["packages"][name] = observed_version
        if observed_version != expected_version:
            errors.append(
                f"package version mismatch: {name}=={observed_version}; expected {expected_version}"
            )

    if check_threads:
        for name, expected_value in record["determinism_environment"].items():
            observed_value = os.environ.get(name)
            observed["environment"][name] = observed_value
            if observed_value != expected_value:
                errors.append(
                    f"environment mismatch: {name}={observed_value!r}; expected {expected_value!r}"
                )
    return errors, observed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--structure-only",
        action="store_true",
        help="Validate lock-file and metadata consistency without checking installed versions.",
    )
    parser.add_argument(
        "--no-thread-check",
        action="store_true",
        help="Do not require the canonical thread and deterministic environment variables.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        help="Optional path for a machine-readable observed-environment report.",
    )
    args = parser.parse_args()

    record = json.loads(RECORD.read_text(encoding="utf-8"))
    errors = validate_structure(record)
    observed: dict[str, object] = {"structure_only": bool(args.structure_only)}
    if not args.structure_only:
        run_errors, run_observed = validate_running_environment(
            record, check_threads=not args.no_thread_check
        )
        errors.extend(run_errors)
        observed.update(run_observed)

    output = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "canonical_environment": record,
        "observed": observed,
    }
    if args.write_report:
        path = args.write_report
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    if errors:
        print("RELEASE ENVIRONMENT: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    mode = "structure" if args.structure_only else "exact"
    print(f"RELEASE ENVIRONMENT: PASS ({mode} verification)")


if __name__ == "__main__":
    main()
