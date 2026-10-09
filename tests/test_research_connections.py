"""Offline checks for source-specific literature navigation and its generated page."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_research_connections", ROOT / "scripts/build_research_connections.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
DATA = json.loads((ROOT / "metadata/research_connections.json").read_text(encoding="utf-8"))


def test_registry_has_distinct_sources() -> None:
    MODULE.validate(DATA)
    works = {work["id"]: work for work in DATA["works"]}
    assert works["analytical_note"]["url"] != works["trajectory_paper"]["url"]
    assert works["analytical_note"]["first_public_date"] == "2022-04-04"
    assert works["trajectory_paper"]["first_public_date"] == "2023-03-23"
    assert "version_policy" in works["repository"]


def test_generated_page_is_current() -> None:
    MODULE.build(ROOT, check=True)


def test_renderer_is_deterministic() -> None:
    assert MODULE.render(DATA) == MODULE.render(deepcopy(DATA))


def test_every_topic_has_source_and_scope() -> None:
    for row in DATA["questions"]:
        assert row["sources"] and row["scope"] and row["neighbors"]
        assert row["search_variants"]
        assert f'id="{row["id"]}"' in MODULE.render(DATA)


def test_invalid_source_is_rejected() -> None:
    invalid = deepcopy(DATA)
    invalid["questions"][0]["sources"] = ["unknown"]
    with pytest.raises(ValueError, match="Unknown source"):
        MODULE.validate(invalid)


def test_unsafe_navigation_is_rejected() -> None:
    invalid = deepcopy(DATA)
    invalid["questions"][0]["reading"][0]["path"] = "../other-repository/README.md"
    with pytest.raises(ValueError, match="Invalid repository path"):
        MODULE.validate(invalid)


def test_duplicate_identifiers_are_rejected() -> None:
    invalid = deepcopy(DATA)
    invalid["questions"].append(deepcopy(invalid["questions"][0]))
    with pytest.raises(ValueError, match="Duplicate identifier"):
        MODULE.validate(invalid)


def test_metadata_has_no_omission_ranking() -> None:
    for collection in ("works", "questions", "neighbors"):
        for row in DATA[collection]:
            assert not {"citation_omission", "omission_strength", "should_have_cited", "priority_rank"}.intersection(row)
