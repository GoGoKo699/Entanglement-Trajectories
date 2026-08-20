#!/usr/bin/env python3
"""Validate the compact human- and AI-facing repository release."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "START_HERE.md",
    "AI_CONTEXT.md",
    "SCIENTIFIC_POSITION.md",
    "CORRECTIONS.md",
    "QA_REPORT.md",
    "UPLOAD_INSTRUCTIONS.md",
    "GITHUB_SETTINGS.md",
    "LICENSE",
    "CITATION.cff",
    "codemeta.json",
    "llms.txt",
    "llms-full.txt",
    "VERSION",
    "SHA256SUMS.txt",
    "metadata/release_manifest.json",
    "metadata/public_claims.json",
    "metadata/definitions.json",
    "metadata/discovery_terms.json",
    "metadata/figure_registry.json",
    "metadata/metric_registry.json",
    "metadata/paper_correction_ledger.csv",
    "data/trajectory_observations.csv",
    "data/spectra_selected_n20.zip",
    "data/public_analysis_inputs.zip",
    "legacy/historical_sources.zip",
    "docs/PUBLIC_FIGURE_STORY.md",
    "paper/AUTHOR_CLARIFICATION_2026.md",
    "paper/JOURNAL_CORRIGENDUM_CORE.md",
    ".github/workflows/qa.yml",
]

ARCHIVES = {
    "data/spectra_selected_n20.zip": 5,
    "data/public_analysis_inputs.zip": 7,
    "legacy/historical_sources.zip": 7,
}

PUBLIC_FIGURES = [
    "figure_01_one_spectrum_many_lenses.png",
    "figure_02_exact_metric_arenas.png",
    "figure_03_metric_robustness_hierarchy.png",
    "figure_04_majorization_and_metric_competition.png",
    "figure_05_model_morphology_and_limits.png",
]

HISTORICAL_ROOT_SCRIPTS = [
    "3D.py", "AME.py", "EC.py", "Gap.py", "Grover.py", "MPD.py",
    "Prime_Almost.py", "QFT.py", "Renyi.py", "Shor.py", "Shor_functions.py",
    "alphabeta.py", "bounds.py", "grover_3sat_functions.py",
    "grover_hash_functions.py", "mean_MPD.py",
]

TRANSIENT_PARTS = {"outputs", "__pycache__", ".pytest_cache", "build", "dist"}
SELF_REFERENTIAL = {"metadata/release_manifest.json", "SHA256SUMS.txt"}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def repository_files() -> list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and not any(part in TRANSIENT_PARTS or part.endswith(".egg-info") for part in p.parts)
        and p.suffix not in {".pyc", ".pyo"}
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text)


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)


def validate_manifest(files: list[Path], errors: list[str]) -> None:
    path = ROOT / "metadata/release_manifest.json"
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"cannot parse release manifest: {exc}")
        return

    actual_paths = {relative(path) for path in files}
    expected_tracked = actual_paths - SELF_REFERENTIAL
    entries = obj.get("files", [])
    entry_paths = {entry.get("path") for entry in entries}

    if obj.get("repository_file_count") != len(files):
        errors.append("release manifest repository_file_count mismatch")
    if obj.get("tracked_file_count") != len(entries):
        errors.append("release manifest tracked_file_count mismatch")
    if set(obj.get("self_referential_exclusions", [])) != SELF_REFERENTIAL:
        errors.append("release manifest self-referential exclusions mismatch")
    if entry_paths != expected_tracked:
        missing = sorted(expected_tracked - entry_paths)
        extra = sorted(entry_paths - expected_tracked)
        errors.append(f"release manifest path coverage mismatch; missing={missing}, extra={extra}")
        return

    by_path = {entry["path"]: entry for entry in entries}
    for rel in sorted(expected_tracked):
        file_path = ROOT / rel
        entry = by_path[rel]
        if entry.get("size_bytes") != file_path.stat().st_size:
            errors.append(f"manifest size mismatch: {rel}")
        if entry.get("sha256") != sha256(file_path):
            errors.append(f"manifest hash mismatch: {rel}")


def validate_sha_file(files: list[Path], errors: list[str]) -> None:
    path = ROOT / "SHA256SUMS.txt"
    records: dict[str, str] = {}
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            digest, rel = raw.split("  ", 1)
            records[rel] = digest
    except Exception as exc:
        errors.append(f"cannot parse SHA256SUMS.txt: {exc}")
        return

    expected = {relative(file_path) for file_path in files if relative(file_path) != "SHA256SUMS.txt"}
    if set(records) != expected:
        errors.append(
            "SHA256SUMS path coverage mismatch; "
            f"missing={sorted(expected-set(records))}, extra={sorted(set(records)-expected)}"
        )
        return
    for rel, digest in records.items():
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"invalid SHA-256 digest format: {rel}")
        elif digest != sha256(ROOT / rel):
            errors.append(f"SHA256SUMS hash mismatch: {rel}")


def main() -> None:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")

    files = repository_files()
    if len(files) > 100:
        errors.append(f"GitHub browser upload limit exceeded: {len(files)} files")
    for path in files:
        if path.stat().st_size > 25 * 1024 * 1024:
            errors.append(f"browser-upload file exceeds 25 MiB: {relative(path)}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "1.0.0":
        errors.append(f"unexpected VERSION: {version}")

    # Parse all current JSON records.
    for path in files:
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"invalid JSON {relative(path)}: {exc}")

    try:
        cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        if cff.get("version") != "1.0.0":
            errors.append("CITATION.cff version mismatch")
        if cff.get("repository-code") != "https://github.com/GoGoKo699/Entanglement-Trajectories":
            errors.append("CITATION.cff repository URL mismatch")
        if cff.get("preferred-citation", {}).get("doi") != "10.22331/q-2024-03-14-1282":
            errors.append("CITATION.cff preferred DOI mismatch")
    except Exception as exc:
        errors.append(f"cannot parse CITATION.cff: {exc}")

    try:
        codemeta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))
        if codemeta.get("version") != "1.0.0":
            errors.append("codemeta version mismatch")
        if codemeta.get("codeRepository") != "https://github.com/GoGoKo699/Entanglement-Trajectories":
            errors.append("codemeta repository URL mismatch")
    except Exception as exc:
        errors.append(f"cannot validate codemeta: {exc}")

    init_text = (ROOT / "src/entanglement_trajectories/__init__.py").read_text(encoding="utf-8")
    if '__version__ = "1.0.0"' not in init_text:
        errors.append("package __version__ mismatch")

    archive_members: dict[str, set[str]] = {}
    for rel, expected_count in ARCHIVES.items():
        try:
            with zipfile.ZipFile(ROOT / rel) as zf:
                bad = zf.testzip()
                members = {name for name in zf.namelist() if not name.endswith("/")}
                archive_members[rel] = members
                if bad:
                    errors.append(f"bad member in {rel}: {bad}")
                if len(members) != expected_count:
                    errors.append(f"unexpected member count in {rel}: {len(members)}")
        except Exception as exc:
            errors.append(f"cannot read {rel}: {exc}")

    # Archive-member evidence notation in machine-readable claims.
    claims_path = ROOT / "metadata/public_claims.json"
    try:
        claims = json.loads(claims_path.read_text(encoding="utf-8"))
        claim_rows = claims.get("claims", [])
        claim_ids = [row.get("id") for row in claim_rows]
        if len(claim_ids) != len(set(claim_ids)):
            errors.append("duplicate public claim IDs")
        for row in claim_rows:
            for source in row.get("source_paths", []):
                if "::" in source:
                    archive, member = source.split("::", 1)
                    if archive not in archive_members:
                        errors.append(f"claim references unknown archive: {source}")
                    elif member not in archive_members[archive]:
                        errors.append(f"claim references missing archive member: {source}")
                elif source.startswith("outputs/"):
                    # Declared generated evidence; produced by a documented workflow.
                    continue
                elif not (ROOT / source).exists():
                    errors.append(f"claim references missing source path: {source}")
    except Exception as exc:
        errors.append(f"cannot validate public claims: {exc}")

    # Registry uniqueness.
    try:
        registry = json.loads((ROOT / "metadata/metric_registry.json").read_text(encoding="utf-8"))
        metric_ids = [row["metric_id"] for row in registry["metrics"]]
        if len(metric_ids) != len(set(metric_ids)) or len(metric_ids) != 26:
            errors.append("metric registry count or uniqueness mismatch")
    except Exception as exc:
        errors.append(f"cannot validate metric registry: {exc}")

    # Canonical table dimensions without requiring pandas.
    try:
        with (ROOT / "data/trajectory_observations.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            row_count = sum(1 for _ in reader)
        if row_count != 5856:
            errors.append(f"unexpected trajectory row count: {row_count}")
        required_columns = {"schema_version", "model", "n", "run_id", "step", "half_vn", "half_linear", "half_logneg", "half_lambda_max"}
        if not required_columns <= set(header):
            errors.append("canonical trajectory table lacks required columns")
    except Exception as exc:
        errors.append(f"cannot validate trajectory table: {exc}")

    # Relative Markdown links in the canonical public layer.
    markdown = [
        ROOT / "README.md", ROOT / "START_HERE.md", ROOT / "AI_CONTEXT.md",
        ROOT / "CORRECTIONS.md", ROOT / "SCIENTIFIC_POSITION.md",
        ROOT / "UPLOAD_INSTRUCTIONS.md", ROOT / "GITHUB_SETTINGS.md",
        ROOT / "QA_REPORT.md",
    ] + sorted((ROOT / "docs").glob("*.md")) + sorted((ROOT / "paper").glob("*.md"))
    for path in markdown:
        for link in markdown_links(path):
            target = link.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"broken link in {relative(path)}: {link}")

    # Required scientific qualifications must be explicit.
    public_text = "\n".join(
        (ROOT / rel).read_text(encoding="utf-8")
        for rel in ["README.md", "AI_CONTEXT.md", "SCIENTIFIC_POSITION.md"]
    ).lower()
    required_qualifiers = [
        "no formal topological invariant has been proved",
        "random matrix theory enters only afterward",
        "individual fingerprinting remains preliminary",
        "majorization-incomparable",
    ]
    for phrase in required_qualifiers:
        if phrase not in public_text:
            errors.append(f"missing required scientific qualification: {phrase}")

    # Public images and social-preview dimensions.
    for name in PUBLIC_FIGURES:
        path = ROOT / "figures/public" / name
        if not path.is_file():
            errors.append(f"missing public figure: {name}")
        else:
            try:
                with Image.open(path) as image:
                    if min(image.size) < 900:
                        errors.append(f"public figure resolution too small: {name} {image.size}")
            except Exception as exc:
                errors.append(f"cannot open public figure {name}: {exc}")
    try:
        with Image.open(ROOT / "figures/public/social_preview.png") as image:
            if image.size != (1280, 640):
                errors.append(f"social preview dimensions mismatch: {image.size}")
    except Exception as exc:
        errors.append(f"cannot open social preview: {exc}")

    # Root historical scripts must be explicit non-executable notices.
    for rel in HISTORICAL_ROOT_SCRIPTS:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing historical compatibility stub: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if "Historical compatibility notice" not in text or "raise SystemExit" not in text:
            errors.append(f"historical root script is not a compatibility stub: {rel}")

    if (ROOT / "metadata/release_manifest.json").is_file():
        validate_manifest(files, errors)
    if (ROOT / "SHA256SUMS.txt").is_file():
        validate_sha_file(files, errors)

    if errors:
        print("PUBLIC VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    largest = max(files, key=lambda path: path.stat().st_size)
    print(
        "PUBLIC VALIDATION: PASS "
        f"({len(files)} repository files; largest={relative(largest)} "
        f"{largest.stat().st_size / 1024**2:.2f} MiB)"
    )


if __name__ == "__main__":
    main()
