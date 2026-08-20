"""Load and query the machine-readable metric registry."""
from __future__ import annotations

import json
from importlib.resources import files
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=1)
def load_metric_registry(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        resource = files("entanglement_trajectories.data").joinpath("metric_registry.json")
        data = json.loads(resource.read_text(encoding="utf-8"))
    else:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
    if "metrics" not in data or not isinstance(data["metrics"], list):
        raise ValueError("Metric registry must contain a list named 'metrics'.")
    ids = [row["metric_id"] for row in data["metrics"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Metric registry contains duplicate metric_id values.")
    return data


def metric_spec(metric_id: str, path: str | Path | None = None) -> dict[str, Any]:
    data = load_metric_registry(path)
    for row in data["metrics"]:
        if row["metric_id"] == metric_id or metric_id in row.get("aliases", []):
            return row
    raise KeyError(metric_id)
