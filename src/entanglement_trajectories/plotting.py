"""Shared labels and exact-boundary plotting helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np

from .boundaries import boundary_curve, relative_boundary_height
from .models import MODEL_LABELS, MODEL_ORDER


METRIC_SPECS: dict[str, dict[str, str]] = {
    "vn": {"column": "half_vn", "metric_id": "von_neumann_entropy", "label": "von Neumann entropy"},
    "linear": {"column": "half_linear", "metric_id": "linear_entropy", "label": "linear entropy (Renyi-2 class)"},
    "logneg": {"column": "half_logneg", "metric_id": "log_negativity_pure", "label": "pure-state log-negativity (Renyi-1/2)"},
}


def natural_model_order(models: Iterable[str]) -> list[str]:
    values = list(dict.fromkeys(str(model) for model in models))
    ordered = [model for model in MODEL_ORDER if model in values]
    ordered.extend(sorted(model for model in values if model not in ordered))
    return ordered


def model_label(model: str) -> str:
    return MODEL_LABELS.get(str(model), str(model).replace("_", " "))


def run_label(group) -> str:
    run_id = str(group["run_id"].iloc[0])
    init = str(group["initial_state"].iloc[0])
    return f"{run_id} ({'random product' if init == 'random_product' else init.replace('_', ' ')})"


def linestyle(initial_state: str) -> str:
    return "--" if str(initial_state) == "random_product" else "-"


def exact_boundary_xy(d: int, metric_key: str, *, points: int = 1601):
    spec = METRIC_SPECS[metric_key]
    curve = boundary_curve(
        spec["metric_id"],
        d,
        normalized=True,
        base=2.0,
        points=points,
        x_coordinate="geometric_linear",
    )
    order = np.argsort(np.asarray(curve["x"], dtype=float))
    return (
        np.asarray(curve["x"], dtype=float)[order],
        np.asarray(curve["lower"], dtype=float)[order],
        np.asarray(curve["upper"], dtype=float)[order],
    )


def boundary_relative_from_geo(
    geo: np.ndarray,
    values: np.ndarray,
    d: int,
    metric_key: str,
) -> np.ndarray:
    geo = np.asarray(geo, dtype=float)
    p = 1.0 - ((d - 1.0) / d) * geo
    metric_id = METRIC_SPECS[metric_key]["metric_id"]
    return np.asarray(
        relative_boundary_height(
            metric_id,
            p,
            values,
            d,
            normalized_metric=True,
            base=2.0,
            on_degenerate="nan",
            clip=False,
        ),
        dtype=float,
    )


def save_figure(fig, pdf_path: Path, *, png_dpi: int = 180) -> tuple[Path, Path]:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    png_path = pdf_path.with_suffix(".png")
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=png_dpi, bbox_inches="tight")
    return pdf_path, png_path
