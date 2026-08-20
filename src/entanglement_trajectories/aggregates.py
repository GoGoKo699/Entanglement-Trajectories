"""Aggregates over a collection of bipartitions.

These quantities are not functions of one half-chain spectrum.  They consume a
collection of one-site-versus-rest spectra and are kept separate to avoid the
misleading historical label ``global_*``.
"""
from __future__ import annotations

import numpy as np

from .metrics import metric_value
from .spectra import normalize_spectrum


def validate_spectrum_collection(spectra: np.ndarray, *, atol: float = 1e-12) -> np.ndarray:
    arr = np.asarray(spectra, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError("spectra must have shape (number_of_cuts, dimension).")
    return np.vstack([normalize_spectrum(row, atol=atol) for row in arr])


def mean_cut_metric(
    spectra: np.ndarray,
    metric_id: str,
    *,
    normalized: bool = True,
    base: float = 2.0,
    q: float | None = None,
    atol: float = 1e-12,
) -> float:
    arr = validate_spectrum_collection(spectra, atol=atol)
    values = [
        metric_value(metric_id, row, normalized=normalized, base=base, q=q, atol=atol)
        for row in arr
    ]
    return float(np.mean(values))


def meyer_wallach_q(one_site_spectra: np.ndarray, *, atol: float = 1e-12) -> float:
    """Return the Meyer-Wallach ``Q`` measure from all one-qubit spectra.

    For a pure n-qubit state this equals the mean normalized single-qubit linear
    entropy: ``Q = (1/n) sum_j 2(1-Tr rho_j^2)``.
    """
    arr = validate_spectrum_collection(one_site_spectra, atol=atol)
    if arr.shape[1] != 2:
        raise ValueError("Meyer-Wallach Q expects one-qubit spectra of length two.")
    return mean_cut_metric(arr, "linear_entropy", normalized=True, atol=atol)
