"""Schmidt-spectrum validation, extremizers, and majorization utilities."""
from __future__ import annotations

import math
from typing import Literal

import numpy as np


class SpectrumError(ValueError):
    """Raised when an array is not a valid probability spectrum."""


def normalize_spectrum(
    values: np.ndarray | list[float] | tuple[float, ...],
    *,
    sort: bool = True,
    atol: float = 1e-12,
) -> np.ndarray:
    """Return a validated probability spectrum.

    Small negative roundoff errors are clipped.  Inputs with a materially
    negative component, zero total weight, or a total differing from one by
    more than ``atol`` are rejected.  The returned array is descending by
    default and is always a copy.
    """
    arr0 = np.asarray(values)
    if arr0.ndim != 1 or arr0.size == 0:
        raise SpectrumError("A spectrum must be a nonempty one-dimensional array.")
    if np.iscomplexobj(arr0):
        if np.max(np.abs(np.imag(arr0))) > atol:
            raise SpectrumError("A spectrum must be real.")
        arr0 = np.real(arr0)
    arr = np.asarray(arr0, dtype=np.float64).copy()
    if not np.all(np.isfinite(arr)):
        raise SpectrumError("A spectrum must contain only finite values.")
    if np.min(arr) < -atol:
        raise SpectrumError(f"Spectrum contains a negative value below tolerance: {arr.min()}")
    arr[arr < 0.0] = 0.0
    total = float(arr.sum())
    if total <= 0.0:
        raise SpectrumError("A spectrum must have positive total weight.")
    if abs(total - 1.0) > atol:
        raise SpectrumError(f"Spectrum must sum to one; received {total:.17g}.")
    arr /= total
    if sort:
        arr.sort()
        arr = arr[::-1].copy()
    return arr


def validate_largest_value(p: float, d: int, *, atol: float = 1e-12) -> float:
    """Validate ``p=lambda_max`` for a ``d``-dimensional spectrum."""
    if isinstance(d, bool) or int(d) != d or d < 1:
        raise ValueError("d must be a positive integer.")
    d = int(d)
    p = float(p)
    if not np.isfinite(p):
        raise ValueError("p must be finite.")
    lower = 1.0 / d
    if p < lower - atol or p > 1.0 + atol:
        raise ValueError(f"p must satisfy 1/d <= p <= 1; got p={p}, d={d}.")
    return float(np.clip(p, lower, 1.0))


def _exact_reciprocal_decomposition(
    p: float,
    d: int,
    *,
    atol: float = 1e-12,
) -> tuple[int, float]:
    """Return the exact represented-float decomposition ``1 = k p + r``.

    Only the canonical floating-point reciprocal ``1.0 / k`` is treated as an
    exact reciprocal.  This helper is used for discontinuous support/rank
    statements, where an arbitrarily small positive remainder matters.
    """
    p = validate_largest_value(p, d, atol=atol)
    nearest = int(round(1.0 / p))
    if 1 <= nearest <= d and p == 1.0 / nearest:
        return nearest, 0.0
    numerator, denominator = p.as_integer_ratio()
    k = min(d, max(1, denominator // numerator))
    remainder_numerator = denominator - k * numerator
    if remainder_numerator < 0:
        raise ArithmeticError(
            f"Invalid exact reciprocal decomposition: p={p}, k={k}, "
            f"remainder numerator={remainder_numerator}."
        )
    r = remainder_numerator / denominator
    if r < 0.0 or r >= p:
        raise ArithmeticError(
            f"Invalid exact reciprocal decomposition: p={p}, k={k}, r={r}."
        )
    return int(k), float(r)


def _reciprocal_decomposition(p: float, d: int, *, atol: float = 1e-12) -> tuple[int, float]:
    """Return a tolerance-stabilized decomposition for continuous metrics.

    A remainder smaller than the declared spectrum tolerance is treated as
    zero.  This avoids amplifying floating-point noise near reciprocal values
    in continuous entropy boundaries.  Discontinuous support/rank statements
    use :func:`_exact_reciprocal_decomposition` instead.
    """
    p = validate_largest_value(p, d, atol=atol)
    inv = 1.0 / p
    nearest = int(round(inv))
    if 1 <= nearest <= d and abs(p - 1.0 / nearest) <= atol * max(1.0, p):
        return nearest, 0.0
    k = min(d, max(1, int(np.floor(inv))))
    r = 1.0 - k * p
    if abs(r) <= atol:
        r = 0.0
    if r < -atol or r > p + atol:
        raise ArithmeticError(f"Invalid reciprocal decomposition: p={p}, k={k}, r={r}.")
    return k, float(np.clip(r, 0.0, p))


def schmidt_rank_bounds_fixed_lmax(
    p: float,
    d: int,
    *,
    atol: float = 1e-12,
) -> tuple[int, int]:
    """Return exact minimum and maximum support sizes at fixed ``lambda_max``.

    The minimum is ``ceil(1/p)`` and is attained by the concentrated spectrum.
    For ``p < 1`` the equal-tail spectrum has full support, so the maximum is
    ``d``; at ``p = 1`` both ranks are one.  No tolerance-based support cutoff
    is used.
    """
    p = validate_largest_value(p, d, atol=atol)
    d = int(d)
    k, r = _exact_reciprocal_decomposition(p, d, atol=atol)
    minimum = k + int(r > 0.0)
    maximum = 1 if p == 1.0 else d
    if not (1 <= minimum <= maximum <= d):
        raise ArithmeticError(
            f"Invalid fixed-lambda_max support bounds: p={p}, d={d}, "
            f"minimum={minimum}, maximum={maximum}."
        )
    return int(minimum), int(maximum)


def equal_tail_spectrum(p: float, d: int, *, atol: float = 1e-12) -> np.ndarray:
    """Spectrum that maximizes every Schur-concave functional at fixed ``p``.

    It is ``(p, (1-p)/(d-1), ..., (1-p)/(d-1))`` for ``d>1``.
    """
    p = validate_largest_value(p, d, atol=atol)
    d = int(d)
    if d == 1:
        return np.array([1.0], dtype=np.float64)
    tail = (1.0 - p) / (d - 1)
    out = np.full(d, tail, dtype=np.float64)
    out[0] = p
    return normalize_spectrum(out, atol=max(atol, 1e-14))


def concentrated_spectrum(p: float, d: int, *, atol: float = 1e-12) -> np.ndarray:
    """Spectrum that minimizes every Schur-concave functional at fixed ``p``.

    With ``k=floor(1/p)`` and ``r=1-kp``, this is
    ``(p repeated k times, r, 0, ...)``, omitting a zero remainder.
    """
    p = validate_largest_value(p, d, atol=atol)
    d = int(d)
    if d == 1:
        return np.array([1.0], dtype=np.float64)
    k, r = _reciprocal_decomposition(p, d, atol=atol)
    out = np.zeros(d, dtype=np.float64)
    out[:k] = p
    if r > 0.0:
        if k >= d:
            raise ArithmeticError("Positive remainder does not fit in the declared dimension.")
        out[k] = r
    # Correct only sub-ulp accumulation without changing the extremizer pattern.
    residual = 1.0 - float(out.sum())
    if abs(residual) <= 10.0 * atol:
        positive = np.flatnonzero(out > 0.0)
        out[positive[-1]] += residual
    return normalize_spectrum(out, atol=max(100.0 * atol, 1e-13))


def random_capped_spectrum(
    p: float,
    d: int,
    rng: np.random.Generator | None = None,
    *,
    atol: float = 1e-12,
) -> np.ndarray:
    """Generate a feasible spectrum with largest component exactly ``p``.

    The distribution is not uniform on the capped simplex; it is intended for
    deterministic validation and property tests.  Every generated tail entry
    lies in ``[0,p]`` and the tail sums to ``1-p``.
    """
    p = validate_largest_value(p, d, atol=atol)
    d = int(d)
    if d == 1:
        return np.array([1.0], dtype=np.float64)
    if rng is None:
        rng = np.random.default_rng()
    remaining = 1.0 - p
    tail = np.empty(d - 1, dtype=np.float64)
    for i in range(d - 2):
        slots_after = d - 2 - i
        low = max(0.0, remaining - slots_after * p)
        high = min(p, remaining)
        if high < low - atol:
            raise ArithmeticError("Capped-simplex sampler reached an infeasible interval.")
        value = low if high - low <= atol else float(rng.uniform(low, high))
        tail[i] = value
        remaining -= value
    tail[-1] = remaining
    out = np.concatenate(([p], tail))
    out.sort()
    out = out[::-1]
    # The first entry may be tied with p but cannot exceed it materially.
    if out[0] > p + 100.0 * atol:
        raise ArithmeticError("Generated tail exceeds the declared largest component.")
    return normalize_spectrum(out, atol=max(100.0 * atol, 1e-11))


def majorizes(
    x: np.ndarray | list[float] | tuple[float, ...],
    y: np.ndarray | list[float] | tuple[float, ...],
    *,
    atol: float = 1e-12,
) -> bool:
    """Return whether probability vector ``x`` majorizes ``y``."""
    xs = normalize_spectrum(x, atol=atol)
    ys = normalize_spectrum(y, atol=atol)
    if xs.size != ys.size:
        raise ValueError("Majorization requires vectors of the same dimension.")
    if xs.size == 1:
        return True
    return bool(np.all(np.cumsum(xs)[:-1] >= np.cumsum(ys)[:-1] - atol))


def majorization_relation(
    x: np.ndarray | list[float] | tuple[float, ...],
    y: np.ndarray | list[float] | tuple[float, ...],
    *,
    atol: float = 1e-12,
) -> Literal["equal", "x_majorizes_y", "y_majorizes_x", "incomparable"]:
    """Classify the majorization relation between two spectra."""
    xs = normalize_spectrum(x, atol=atol)
    ys = normalize_spectrum(y, atol=atol)
    if xs.size != ys.size:
        raise ValueError("Majorization requires vectors of the same dimension.")
    if np.allclose(xs, ys, atol=atol, rtol=0.0):
        return "equal"
    xy = majorizes(xs, ys, atol=atol)
    yx = majorizes(ys, xs, atol=atol)
    if xy and not yx:
        return "x_majorizes_y"
    if yx and not xy:
        return "y_majorizes_x"
    if xy and yx:
        return "equal"
    return "incomparable"
