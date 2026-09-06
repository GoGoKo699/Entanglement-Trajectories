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
    if not np.isfinite(base) or base <= 1.0:
        raise ValueError("Entropy and entanglement-energy units require a finite base greater than one.")
    return base


def _log_base(x: float | np.ndarray, base: float) -> float | np.ndarray:
    return np.log(x) / math.log(_validate_base(base))


def _normalize_log_entropy(value: float, d: int, base: float) -> float:
    if d <= 1:
        return 0.0
    return float(value / _log_base(float(d), base))


def _exact_support_size(p: np.ndarray) -> int:
    """Return the mathematical support size of a validated spectrum.

    Strictly positive represented entries count, irrespective of magnitude.
    This is intentionally different from a tolerance-based numerical rank.
    """
    return int(np.count_nonzero(p > 0.0))


def schmidt_rank(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> int | float:
    """Return the exact support size ``# {i : lambda_i > 0}``.

    The result is exact for the supplied floating-point spectrum after
    validation.  Tiny positive entries count.  Use
    :func:`numerical_schmidt_rank` when a declared threshold is intended.
    """
    p = normalize_spectrum(lam, atol=atol)
    rank = _exact_support_size(p)
    if normalized and p.size <= 1:
        return 0.0
    if not normalized:
        return rank
    return float((rank - 1.0) / (p.size - 1.0))


def numerical_schmidt_rank(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    threshold: float = 1e-12,
    relative: bool = False,
    normalized: bool = False,
    atol: float = 1e-12,
) -> int | float:
    """Return a threshold-dependent numerical Schmidt-rank diagnostic.

    With ``relative=False``, entries greater than the absolute ``threshold``
    count.  With ``relative=True``, the cutoff is
    ``threshold * lambda_max``.  This diagnostic is not the exact Schmidt rank
    and its threshold must be reported whenever it is used.
    """
    p = normalize_spectrum(lam, atol=atol)
    threshold = float(threshold)
    if not np.isfinite(threshold) or threshold < 0.0:
        raise ValueError("threshold must be finite and nonnegative.")
    if relative and threshold >= 1.0:
        raise ValueError("A relative threshold must be smaller than one.")
    cutoff = threshold * float(p[0]) if relative else threshold
    if cutoff >= float(p[0]):
        raise ValueError("The numerical-rank threshold removes the largest eigenvalue.")
    rank = int(np.count_nonzero(p > cutoff))
    if normalized and p.size <= 1:
        return 0.0
    if not normalized:
        return rank
    return float((rank - 1.0) / (p.size - 1.0))


def hartley_entropy(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    base: float = 2.0,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Return exact Hartley entropy ``H_0 = log(rank)``.

    No support threshold is applied.  For noisy numerical spectra this may be
    full rank even when a thresholded diagnostic is small; that distinction is
    mathematically intentional.
    """
    p = normalize_spectrum(lam, atol=atol)
    value = float(_log_base(float(_exact_support_size(p)), base))
    return _normalize_log_entropy(value, p.size, base) if normalized else value


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
    atol: float = 1e-12,
) -> float:
    """Return Rényi entropy of order ``q`` for ``q>=0``.

    ``q=0``, ``q=1``, and ``q=inf`` are handled by their exact limits.
    At ``q=0`` every strictly positive represented eigenvalue counts; no
    numerical-rank threshold is applied.  For finite positive ``q`` the
    computation uses log-sum-exp for stability.
    """
    p = normalize_spectrum(lam, atol=atol)
    q = float(q)
    if math.isnan(q) or q < 0.0:
        raise ValueError("This project defines Rényi entropy only for q >= 0.")
    if q == 0.0:
        value = hartley_entropy(p, base=base, normalized=False, atol=atol)
    elif math.isinf(q):
        value = -float(_log_base(float(p[0]), base))
    elif q == 1.0:
        value = von_neumann_entropy(p, base=base, normalized=False, atol=atol)
    else:
        nz = p[p > 0.0]
        logs = np.log(nz)
        if abs(q - 1.0) < 0.01:
            # sum(p**q) = 1 + sum(p * expm1((q-1)*log(p))).
            # Unlike subtracting log(sum(p**q)) from zero, this has a stable
            # q -> 1 limit and does not silently substitute a nearby order.
            offset = math.fsum(float(x) for x in nz * np.expm1((q - 1.0) * logs))
            entropy_nats = math.log1p(offset) / (1.0 - q)
        else:
            # Isolate the leading contribution so sub-ulp tail sums survive
            # near a product state; divide before multiplying for large q.
            leading_log = float(logs[0])
            with np.errstate(over="ignore", under="ignore"):
                tail = math.fsum(float(x) for x in np.exp(q * (logs[1:] - leading_log)))
            entropy_nats = (q / (1.0 - q)) * leading_log + math.log1p(tail) / (1.0 - q)
        value = entropy_nats / math.log(_validate_base(base))
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


def _linear_from_validated_spectrum(p: np.ndarray) -> float:
    """Evaluate 1-purity via positive cross-weights near a product point."""
    leading = float(p[0])
    tail = math.fsum(float(x) for x in p[1:])
    tail_square = math.fsum(float(x) * float(x) for x in p[1:])
    # (sum p)**2 - sum(p**2), avoiding subtraction of two numbers near one.
    return 2.0 * leading * tail + max(0.0, tail * tail - tail_square)


def linear_entropy(
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Return ``1-Tr(rho^2)`` or its dimension-normalized form."""
    p = normalize_spectrum(lam, atol=atol)
    value = _linear_from_validated_spectrum(p)
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
    atol: float = 1e-12,
) -> float:
    """Return the Hill/Rényi effective number ``R_q=exp(H_q)``.

    The result is independent of logarithm base.  At ``q=0`` this is the
    exact Schmidt rank of the represented spectrum.  The normalized form is
    ``(R_q-1)/(d-1)``.
    """
    p = normalize_spectrum(lam, atol=atol)
    q = float(q)
    if math.isnan(q) or q < 0.0:
        raise ValueError("Effective rank is defined here only for q >= 0.")
    if q == 0.0:
        value = float(_exact_support_size(p))
    elif math.isinf(q):
        value = 1.0 / float(p[0])
    else:
        # Avoid underflow of sum(p**q) at large finite q.
        value = math.exp(renyi_entropy(p, q, base=math.e, atol=atol))
    if normalized and p.size <= 1:
        return 0.0
    if not normalized:
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
    value = math.sqrt(2.0 * _linear_from_validated_spectrum(p))
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
    value = 2.0 * _linear_from_validated_spectrum(p)
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
    base = _validate_base(base)
    if not math.isfinite(zero_tol) or zero_tol < 0.0:
        raise ValueError("zero_tol must be finite and nonnegative.")
    p = normalize_spectrum(lam, atol=atol)
    second = float(p[1]) if p.size > 1 else 0.0
    if second <= zero_tol:
        return math.inf
    # A finite log gap must not overflow just because lambda_1/lambda_2 does.
    return (math.log(float(p[0])) - math.log(second)) / math.log(base)


def metric_value(
    metric_id: str,
    lam: np.ndarray | list[float] | tuple[float, ...],
    *,
    q: float | None = None,
    normalized: bool = False,
    base: float = 2.0,
    atol: float = 1e-12,
    **kwargs: Any,
) -> float | int:
    """Evaluate a canonical metric by registry identifier."""
    key = str(metric_id).strip().lower()
    aliases = {
        "vn": "von_neumann_entropy",
        "h1": "von_neumann_entropy",
        "renyi": "renyi_entropy",
        "h0": "hartley_entropy",
        "rank": "schmidt_rank",
        "numerical_rank": "numerical_schmidt_rank",
        "threshold_rank": "numerical_schmidt_rank",
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
        return hartley_entropy(lam, base=base, normalized=normalized, atol=atol)
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
        return schmidt_rank(lam, normalized=normalized, atol=atol)
    if key == "numerical_schmidt_rank":
        return numerical_schmidt_rank(lam, normalized=normalized, atol=atol, **kwargs)
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


def log_negativity_from_schmidt_coefficients(
    coefficients: np.ndarray | list[float],
    *,
    base: float = 2.0,
    normalized: bool = False,
    atol: float = 1e-12,
) -> float:
    """Pure-state log-negativity from UNSQUARED Schmidt coefficients.

    Use this with direct coefficient-matrix SVD. It avoids both the Gram
    matrix and squaring then taking square roots of tiny singular values.
    The supplied coefficients must be nonnegative with sum(s**2) ~= 1.
    This routine does not threshold singular values or infer algebraic rank.
    """
    base = _validate_base(base)
    s = np.asarray(coefficients, dtype=float)
    if s.ndim != 1 or s.size == 0 or not np.all(np.isfinite(s)) or np.any(s < 0):
        raise ValueError("Schmidt coefficients must be a nonempty finite nonnegative vector.")
    norm2 = math.fsum(float(x) * float(x) for x in s)
    if norm2 <= 0 or not math.isfinite(norm2) or abs(norm2 - 1.0) > atol:
        raise ValueError("Squared Schmidt coefficients must sum to one.")
    s = np.sort(s / math.sqrt(norm2))[::-1]
    log_sum = math.log(float(s[0])) + math.log1p(math.fsum(float(x) for x in s[1:]) / float(s[0]))
    value = 2.0 * max(0.0, log_sum) / math.log(base)
    return _normalize_log_entropy(value, s.size, base) if normalized else value
