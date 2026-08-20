"""Spectrum-based entanglement measures and spectral diagnostics.

The input ``lam`` is always the reduced-density-matrix spectrum (squared
Schmidt coefficients), not the unsquared Schmidt coefficients.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from .spectra import normalize_spectrum


def _validate_base(base: float) -> float:
    base = float(base)
    if not np.isfinite(base) or base <= 0.0 or abs(base - 1.0) < 1e-15:
        raise ValueError("Logarithm base must be positive and different from one.")
    return base


def _log_base(x: float | np.ndarray, base: float) -> float | np.ndarray:
    return np.log(x) / math.log(_validate_base(base))


def _normalize_log_entropy(value: float, d: int, base: float) -> float:
    if d <= 1:
        return 0.0
    return float(value / _log_base(float(d), base))


def von_neumann_entropy(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    base: float = 2.0,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Return ``-sum_i lambda_i log(lambda_i)``."""
    p = normalize_spectrum(lam, atol=atol)
    nz = p[p > 0.0]
    value = -float(np.sum(nz * _log_base(nz, base)))
    return _normalize_log_entropy(value, p.size, base) if normalized else value


def renyi_entropy(
    lam: np.ndarray | list[float] | tuple[float, ...],
    q: float,
    *,
    base: float = 2.0,
    normalized: bool = False,
    support_tol: float = 1e-15,
    atol: float = 1e-12,
) -> float:
    """Return Rényi entropy of order ``q`` for ``q>=0``.

    ``q=0``, ``q=1``, and ``q=inf`` are handled by their exact limits.
    For finite positive ``q`` the computation uses log-sum-exp for stability.
    """
    p = normalize_spectrum(lam, atol=atol)
    q = float(q)
    if math.isnan(q) or q < 0.0:
        raise ValueError("This project defines Rényi entropy only for q >= 0.")
    if q == 0.0:
        rank = int(np.count_nonzero(p > support_tol))
        value = float(_log_base(float(rank), base))
    elif math.isinf(q):
        value = -float(_log_base(float(p[0]), base))
    elif abs(q - 1.0) <= 1e-10:
        value = von_neumann_entropy(p, base=base, normalized=False, atol=atol)
    else:
        nz = p[p > 0.0]
        log_terms = q * np.log(nz)
        m = float(np.max(log_terms))
        ln_sum = m + math.log(float(np.sum(np.exp(log_terms - m))))
        value = ln_sum / ((1.0 - q) * math.log(_validate_base(base)))
    return _normalize_log_entropy(value, p.size, base) if normalized else float(value)


def purity(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Return ``Tr(rho^2)=sum_i lambda_i^2``.

    With ``normalized=True`` this returns the concentration coordinate
    ``(d*P-1)/(d-1)``, equal to zero for the uniform spectrum and one for a
    product spectrum.  Its direction is opposite to entanglement.
    """
    p = normalize_spectrum(lam, atol=atol)
    value = float(np.dot(p, p))
    if not normalized or p.size <= 1:
        return value
    return float((p.size * value - 1.0) / (p.size - 1.0))


def linear_entropy(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Return ``1-Tr(rho^2)`` or its dimension-normalized form."""
    p = normalize_spectrum(lam, atol=atol)
    value = 1.0 - float(np.dot(p, p))
    if not normalized or p.size <= 1:
        return value
    return float((p.size / (p.size - 1.0)) * value)


def log_negativity_pure(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    base: float = 2.0,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Pure-state logarithmic negativity.

    ``E_N = 2 log(sum_i sqrt(lambda_i)) = H_{1/2}(lambda)``.
    """
    return renyi_entropy(lam, 0.5, base=base, normalized=normalized, atol=atol)


def negativity_pure(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Pure-state negativity ``((sum sqrt(lambda))^2-1)/2``.

    The normalized value divides by the maximally entangled value ``(d-1)/2``.
    """
    p = normalize_spectrum(lam, atol=atol)
    value = 0.5 * (float(np.sum(np.sqrt(p))) ** 2 - 1.0)
    value = max(0.0, value)
    if not normalized or p.size <= 1:
        return float(value)
    return float(2.0 * value / (p.size - 1.0))


def min_entropy(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    base: float = 2.0,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Return Rényi min-entropy ``H_inf=-log(lambda_max)``."""
    return renyi_entropy(lam, math.inf, base=base, normalized=normalized, atol=atol)


def geometric_entanglement_linear(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Bipartite pure-state geometric measure in linear form ``1-lambda_max``."""
    p = normalize_spectrum(lam, atol=atol)
    value = 1.0 - float(p[0])
    if not normalized or p.size <= 1:
        return value
    return float((p.size / (p.size - 1.0)) * value)


def geometric_entanglement_log(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    base: float = 2.0,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Logarithmic geometric measure ``-log(lambda_max)=H_inf``."""
    return min_entropy(lam, base=base, normalized=normalized, atol=atol)


def effective_rank(
    lam: np.ndarray | list[float] | tuple[float, ...],
    q: float = 1.0,
    *,
    normalized: bool = False,
    support_tol: float = 1e-15,
    atol: float = 1e-12,
) -> float:
    """Return the Hill/Rényi effective number ``R_q=exp(H_q)``.

    The result is independent of logarithm base.  The normalized form is
    ``(R_q-1)/(d-1)``.
    """
    p = normalize_spectrum(lam, atol=atol)
    q = float(q)
    if math.isnan(q) or q < 0.0:
        raise ValueError("Effective rank is defined here only for q >= 0.")
    if q == 0.0:
        value = float(np.count_nonzero(p > support_tol))
    elif math.isinf(q):
        value = 1.0 / float(p[0])
    elif abs(q - 1.0) <= 1e-10:
        nz = p[p > 0.0]
        value = math.exp(-float(np.sum(nz * np.log(nz))))
    else:
        value = float(np.sum(p**q)) ** (1.0 / (1.0 - q))
    if not normalized or p.size <= 1:
        return float(value)
    return float((value - 1.0) / (p.size - 1.0))


def i_concurrence(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Pure-state I-concurrence ``sqrt(2*(1-purity))``."""
    p = normalize_spectrum(lam, atol=atol)
    value = math.sqrt(max(0.0, 2.0 * (1.0 - float(np.dot(p, p)))))
    if not normalized or p.size <= 1:
        return value
    maximum = math.sqrt(2.0 * (1.0 - 1.0 / p.size))
    return float(value / maximum)


def i_tangle(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Squared I-concurrence ``2*(1-purity)``."""
    p = normalize_spectrum(lam, atol=atol)
    value = 2.0 * (1.0 - float(np.dot(p, p)))
    if not normalized or p.size <= 1:
        return float(value)
    maximum = 2.0 * (1.0 - 1.0 / p.size)
    return float(value / maximum)


def schmidt_gap(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    atol: float = 1e-12,
) -> float:
    """Return the ordinary leading Schmidt-eigenvalue gap ``lambda_1-lambda_2``."""
    p = normalize_spectrum(lam, atol=atol)
    second = float(p[1]) if p.size > 1 else 0.0
    return float(p[0] - second)


def schmidt_ratio(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    atol: float = 1e-12,
) -> float:
    """Return the edge ratio ``lambda_2/lambda_1`` in ``[0,1]``."""
    p = normalize_spectrum(lam, atol=atol)
    second = float(p[1]) if p.size > 1 else 0.0
    return float(second / p[0])


def entanglement_hamiltonian_gap(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    base: float = math.e,
    atol: float = 1e-12,
    zero_tol: float = 0.0,
) -> float:
    """Return ``log(lambda_1/lambda_2)``.

    The value is infinite when the second eigenvalue is at or below
    ``zero_tol``.  This is the gap between the two lowest entanglement energies
    ``xi_i=-log(lambda_i)``.
    """
    p = normalize_spectrum(lam, atol=atol)
    second = float(p[1]) if p.size > 1 else 0.0
    if second <= zero_tol:
        return math.inf
    return float(_log_base(float(p[0] / second), base))


def metric_value(
    metric_id: str,
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    q: float | None = None,
    normalized: bool = False,
    base: float = 2.0,
    atol: float = 1e-12,
    **kwargs: Any,
) -> float:
    """Evaluate a canonical metric by registry identifier."""
    key = str(metric_id).strip().lower()
    aliases = {
        "vn": "von_neumann_entropy",
        "h1": "von_neumann_entropy",
        "renyi": "renyi_entropy",
        "h0": "hartley_entropy",
        "hhalf": "renyi_half",
        "h2": "renyi_two",
        "hinf": "min_entropy",
        "linear": "linear_entropy",
        "logneg": "log_negativity_pure",
        "geo": "geometric_linear",
        "gap": "schmidt_gap",
        "log_gap": "entanglement_hamiltonian_gap",
    }
    key = aliases.get(key, key)
    if key == "von_neumann_entropy":
        return von_neumann_entropy(lam, base=base, normalized=normalized, atol=atol)
    if key == "renyi_entropy":
        if q is None:
            raise ValueError("renyi_entropy requires q.")
        return renyi_entropy(lam, q, base=base, normalized=normalized, atol=atol)
    if key == "hartley_entropy":
        return renyi_entropy(lam, 0.0, base=base, normalized=normalized, atol=atol, **kwargs)
    if key == "renyi_half":
        return renyi_entropy(lam, 0.5, base=base, normalized=normalized, atol=atol)
    if key == "renyi_two":
        return renyi_entropy(lam, 2.0, base=base, normalized=normalized, atol=atol)
    if key == "renyi_three":
        return renyi_entropy(lam, 3.0, base=base, normalized=normalized, atol=atol)
    if key == "min_entropy":
        return min_entropy(lam, base=base, normalized=normalized, atol=atol)
    if key == "purity":
        return purity(lam, normalized=normalized, atol=atol)
    if key == "linear_entropy":
        return linear_entropy(lam, normalized=normalized, atol=atol)
    if key == "log_negativity_pure":
        return log_negativity_pure(lam, base=base, normalized=normalized, atol=atol)
    if key == "negativity_pure":
        return negativity_pure(lam, normalized=normalized, atol=atol)
    if key == "geometric_linear":
        return geometric_entanglement_linear(lam, normalized=normalized, atol=atol)
    if key == "geometric_log":
        return geometric_entanglement_log(lam, base=base, normalized=normalized, atol=atol)
    if key == "effective_rank":
        if q is None:
            q = 1.0
        return effective_rank(lam, q, normalized=normalized, atol=atol, **kwargs)
    if key == "participation_ratio":
        return effective_rank(lam, 2.0, normalized=normalized, atol=atol)
    if key == "schmidt_rank":
        return effective_rank(lam, 0.0, normalized=normalized, atol=atol, **kwargs)
    if key == "i_concurrence":
        return i_concurrence(lam, normalized=normalized, atol=atol)
    if key == "i_tangle":
        return i_tangle(lam, normalized=normalized, atol=atol)
    if key == "largest_schmidt_value":
        return float(normalize_spectrum(lam, atol=atol)[0])
    if key == "schmidt_gap":
        return schmidt_gap(lam, atol=atol)
    if key == "schmidt_ratio":
        return schmidt_ratio(lam, atol=atol)
    if key == "entanglement_hamiltonian_gap":
        return entanglement_hamiltonian_gap(lam, base=base, atol=atol, **kwargs)
    raise KeyError(f"Unknown metric identifier: {metric_id!r}")
