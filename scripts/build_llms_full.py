#!/usr/bin/env python3
"""Build ``llms-full.txt`` from the canonical public Markdown sources.

The file is an optional navigation aid. The machine-readable claim registry remains
canonical for numerical and scoped scientific claims.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "llms-full.txt"

SOURCES: tuple[tuple[str, str], ...] = (
    ("Canonical AI context", "AI_CONTEXT.md"),
    ("Scientific overview", "docs/SCIENTIFIC_OVERVIEW.md"),
    ("Results at a glance", "docs/RESULTS_AT_A_GLANCE.md"),
    ("Exact spectral geometry", "docs/EXACT_SPECTRAL_GEOMETRY.md"),
    ("Operational metric-robust trajectory class", "docs/OPERATIONAL_TOPOLOGICAL_INVARIANT.md"),
    ("Corrections to the 2024 paper", "CORRECTIONS.md"),
    ("Primary references", "REFERENCES.md"),
    ("XXZ product-formula convergence", "docs/XXZ_PRODUCT_FORMULA_CONVERGENCE.md"),
    ("Limitations", "docs/LIMITATIONS.md"),
    ("Peer-review release audit", "docs/PEER_REVIEW_RELEASE_AUDIT.md"),
    ("Canonical release environment", "docs/RELEASE_ENVIRONMENT.md"),
    ("Reproducibility", "docs/REPRODUCIBILITY.md"),
)

HEADER = """# Entanglement Trajectories - full machine-readable context

> Corrected computational companion and follow-up evidence for Ruge Lin, “Entanglement Trajectory and its Boundary,” Quantum 8, 1282 (2024), DOI 10.22331/q-2024-03-14-1282.

This file concatenates the canonical public context. Scoped numerical claims in `metadata/public_claims.json` remain authoritative. Historical material under `legacy/` and the pinned historical branch are not part of this canonical context.
"""


def normalize(text: str) -> str:
    """Return normalized UTF-8 Markdown with one terminal newline."""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"


def main() -> None:
    sections = [HEADER.rstrip()]
    for title, relative in SOURCES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"Missing canonical source: {relative}")
        sections.extend(
            [
                "",
                f"<!-- canonical-source: {relative} -->",
                f"## {title}",
                "",
                normalize(path.read_text(encoding="utf-8")).rstrip(),
            ]
        )
    OUTPUT.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
