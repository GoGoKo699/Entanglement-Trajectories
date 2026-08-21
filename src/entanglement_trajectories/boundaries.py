"""Exact fixed-largest-Schmidt-value envelopes.

No interpolation is used.  Every bound is evaluated directly at the requested
``p=lambda_max``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

from .metrics import metric_value
from .spectra import (
    concentrated_spectrum,
    equal_tail_spectrum,
    schmidt_rank_bounds_fixed_lmax,
    validate_largest_value,
)


class DegenerateEnvelopeError(ValueError):
    """Raised when a boundary-relative coordinate is requested on a collapsed envelope."""


@dataclass(frozen=True)
class Bounds:
    """Numerical lower and upper metric values at fixed ``lambda_max``."""

    lower: float | np.ndarray
    upper: float | np.ndarray
    lower_extremizer: str
    upper_extremizer: str
    degenerate: bool | np.ndarray


_SCHUR_CONCAVE = {
    "von_neumann_entropy",
    "renyi_entropy",
    "hartley_entropy",
    "renyi_half",
    "renyi_two",
    "renyi_three",
    "min_entropy",
    "linear_entropy",
    "log_negativity_pure",
    "negativity_pure",
    "geometric_linear",
    "geometric_log",
    "effective_rank",
    "participation_ratio",
    "schmidt_rank",
    "i_concurrence",
    "i_tangle",
}
_SCHUR_CONVEX = {"purity"}
_EQUAL_TAIL_MIN = {"schmidt_ratio", "purity"}
_CONCENTRATED_MIN = {
    "schmidt_gap",
    "entanglement_hamiltonian_gap",
}
_FIXED_BY_P = {
    "largest_schmidt_value",
    "min_entropy",
    "geometric_linear",
    "geometric_log",
}


def _canonical(metric_id: str) -> str:
    key = str(metric_id).strip().lower()
    aliases = {
        "vn": "von_neumann_entropy",
        "h1": "von_neumann_entropy",
        "h0": "hartley_entropy",
        "hhalf": "renyi_half",
        "h2": "renyi_two",
        "hinf": "min_entropy",
        "linear": "linear_entropy",
        "logneg": "log_negativity_pure",
        "geo": "geometric_linear",
        "gap": "schmidt_gap",
        "log_gap": "entanglement_hamiltonian_gap",
        "renyi": "renyi_entropy",
    }
    return aliases.get(key, key)


def _is_zero_order_metric(key: str, q: float | None) -> bool:
    if key in {"hartley_entropy", "schmidt_rank"}:
        return True
    if key in {"renyi_entropy", "effective_rank"} and q is not None:
        return float(q) == 0.0
    return False


def _exact_zero_order_bounds(
    key: str,
    p: float,
    d: int,
    *,
    normalized: bool,
    base: float,
    atol: float,
) -> tuple[float, float, str, str]:
    rank_lower, rank_upper = schmidt_rank_bounds_fixed_lmax(p, d, atol=atol)
    if key in {"hartley_entropy", "renyi_entropy"}:
        base = float(base)
        if not np.isfinite(base) or base <= 0.0 or abs(base - 1.0) < 1e-15:
            raise ValueError("Logarithm base must be positive and different from one.")
        if normalized:
            if d <= 1:
                lower = upper = 0.0
            else:
                denominator = math.log(float(d))
                lower = math.log(float(rank_lower)) / denominator
                upper = math.log(float(rank_upper)) / denominator
        else:
            denominator = math.log(base)
            lower = math.log(float(rank_lower)) / denominator
            upper = math.log(float(rank_upper)) / denominator
    else:
        if normalized:
            if d <= 1:
                lower = upper = 0.0
            else:
                lower = (rank_lower - 1.0) / (d - 1.0)
                upper = (rank_upper - 1.0) / (d - 1.0)
        else:
            lower, upper = float(rank_lower), float(rank_upper)
    return float(lower), float(upper), "concentrated", "equal_tail"


def _scalar_bounds(
    metric_id: str,
    p: float,
    d: int,
    *,
    q: float | None,
    normalized: bool,
    base: float,
    atol: float,
) -> tuple[float, float, str, str]:
    key = _canonical(metric_id)
    p = validate_largest_value(p, d, atol=atol)
    if _is_zero_order_metric(key, q):
        return _exact_zero_order_bounds(
            key,
            p,
            d,
            normalized=normalized,
            base=base,
            atol=atol,
        )
    concentrated = concentrated_spectrum(p, d, atol=atol)
    equal_tail = equal_tail_spectrum(p, d, atol=atol)
    kwargs = dict(q=q, normalized=normalized, base=base, atol=atol)

    if key in _FIXED_BY_P:
        value = metric_value(key, concentrated, **kwargs)
        return value, value, "fixed_by_p", "fixed_by_p"
    if key in _SCHUR_CONCAVE:
        lower = metric_value(key, concentrated, **kwargs)
        upper = metric_value(key, equal_tail, **kwargs)
        return lower, upper, "concentrated", "equal_tail"
    if key in _SCHUR_CONVEX:
        lower = metric_value(key, equal_tail, **kwargs)
        upper = metric_value(key, concentrated, **kwargs)
        return lower, upper, "equal_tail", "concentrated"
    if key == "schmidt_gap":
        return (
            metric_value(key, concentrated, **kwargs),
            metric_value(key, equal_tail, **kwargs),
            "concentrated",
            "equal_tail",
        )
    if key == "schmidt_ratio":
        return (
            metric_value(key, equal_tail, **kwargs),
            metric_value(key, concentrated, **kwargs),
            "equal_tail",
            "concentrated",
        )
    if key == "entanglement_hamiltonian_gap":
        return (
            metric_value(key, concentrated, **kwargs),
            metric_value(key, equal_tail, **kwargs),
            "concentrated",
            "equal_tail",
        )
    raise KeyError(f"No exact fixed-p boundary rule is registered for {metric_id!r}.")


def metric_bounds_fixed_lmax(
    metric_id: str,
    p: float | np.ndarray | list[float],
    d: int,
    *,
    q: float | None = None,
    normalized: bool = False,
    base: float = 2.0,
    atol: float = 1e-12,
) -> Bounds:
    """Return exact numerical bounds at fixed ``p=lambda_max``.

    The function accepts a scalar or an array of ``p`` values.  For entropy and
    effective-rank families, ``q`` is required only for the generic identifiers
    ``renyi_entropy`` and ``effective_rank``.  Zero-order support boundaries are
    evaluated analytically rather than inferred from a numerical threshold.
    """
    arr = np.asarray(p, dtype=np.float64)
    scalar = arr.ndim == 0
    flat = arr.reshape(-1)
    lo = np.empty_like(flat)
    hi = np.empty_like(flat)
    lower_kind = upper_kind = ""
    for i, pi in enumerate(flat):
        lo[i], hi[i], lk, uk = _scalar_bounds(
            metric_id,
            float(pi),
            int(d),
            q=q,
            normalized=normalized,
            base=base,
            atol=atol,
        )
        if i == 0:
            lower_kind, upper_kind = lk, uk
        elif (lk, uk) != (lower_kind, upper_kind):
            raise ArithmeticError("Extremizer labels changed across one boundary request.")
        if np.isfinite(lo[i]) and np.isfinite(hi[i]) and lo[i] > hi[i] + 100.0 * atol:
            raise ArithmeticError(
                f"Computed lower bound exceeds upper bound for metric={metric_id}, p={pi}: "
                f"{lo[i]} > {hi[i]}"
            )
    deg = np.isclose(lo, hi, atol=100.0 * atol, rtol=0.0)
    if scalar:
        return Bounds(float(lo[0]), float(hi[0]), lower_kind, upper_kind, bool(deg[0]))
    return Bounds(lo.reshape(arr.shape), hi.reshape(arr.shape), lower_kind, upper_kind, deg.reshape(arr.shape))


def relative_boundary_height(
    metric_id: str,
    p: float | np.ndarray | list[float],
    value: float | np.ndarray | list[float],
    d: int,
    *,
    q: float | None = None,
    normalized_metric: bool = False,
    base: float = 2.0,
    on_degenerate: Literal["nan", "zero", "midpoint", "raise"] = "nan",
    clip: bool = False,
    atol: float = 1e-12,
) -> float | np.ndarray:
    """Map a metric value to its relative position between exact fixed-p bounds.

    A collapsed envelope does not define a relative height.  The default is to
    return ``NaN`` rather than silently assigning an arbitrary endpoint.
    """
    p_arr, v_arr = np.broadcast_arrays(np.asarray(p, dtype=float), np.asarray(value, dtype=float))
    bounds = metric_bounds_fixed_lmax(
        metric_id,
        p_arr,
        d,
        q=q,
        normalized=normalized_metric,
        base=base,
        atol=atol,
    )
    lower = np.asarray(bounds.lower, dtype=float)
    upper = np.asarray(bounds.upper, dtype=float)
    denom = upper - lower
    deg = np.asarray(bounds.degenerate, dtype=bool) | ~np.isfinite(denom) | (np.abs(denom) <= 100.0 * atol)
    out = np.empty_like(v_arr, dtype=float)
    good = ~deg
    out[good] = (v_arr[good] - lower[good]) / denom[good]
    if np.any(deg):
        if on_degenerate == "raise":
            raise DegenerateEnvelopeError("Boundary-relative coordinate is undefined on a collapsed envelope.")
        fill = {"nan": np.nan, "zero": 0.0, "midpoint": 0.5}.get(on_degenerate)
        if fill is None:
            raise ValueError(f"Unknown on_degenerate policy: {on_degenerate!r}")
        out[deg] = fill
    if clip:
        out = np.clip(out, 0.0, 1.0)
    return float(out) if out.ndim == 0 else out


def boundary_curve(
    metric_id: str,
    d: int,
    *,
    q: float | None = None,
    normalized: bool = True,
    base: float = 2.0,
    points: int = 1001,
    x_coordinate: Literal["lambda_max", "geometric_linear"] = "lambda_max",
    atol: float = 1e-12,
) -> dict[str, np.ndarray | str]:
    """Construct a directly evaluated exact boundary curve for plotting."""
    if points < 2:
        raise ValueError("points must be at least two.")
    p = np.linspace(1.0 / d, 1.0, int(points))
    bounds = metric_bounds_fixed_lmax(
        metric_id, p, d, q=q, normalized=normalized, base=base, atol=atol
    )
    if x_coordinate == "lambda_max":
        x = p
    elif x_coordinate == "geometric_linear":
        x = (d / (d - 1.0)) * (1.0 - p) if d > 1 else np.zeros_like(p)
    else:
        raise ValueError(f"Unknown x_coordinate: {x_coordinate!r}")
    return {
        "x": np.asarray(x),
        "p": p,
        "lower": np.asarray(bounds.lower),
        "upper": np.asarray(bounds.upper),
        "metric_id": _canonical(metric_id),
        "x_coordinate": x_coordinate,
        "lower_extremizer": bounds.lower_extremizer,
        "upper_extremizer": bounds.upper_extremizer,
    }
