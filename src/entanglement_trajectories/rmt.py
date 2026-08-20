"""Haar/Wishart and Marchenko-Pastur reference diagnostics.

The reference layer is deliberately secondary to the exact feasible geometry.
It distinguishes exact finite-dimensional Haar means from large-d balanced
Marchenko-Pastur proxies and never treats either as a universal boundary or a
proved dynamical attractor.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import math
from typing import Mapping, Sequence

import numpy as np


REFERENCE_METRIC_COLUMNS: tuple[str, ...] = (
    "half_vn",
    "half_linear",
    "half_logneg",
    "half_geometric_linear",
)

GAP_RATIO_REFERENCE_MEANS: dict[str, float] = {
    "poisson": 2.0 * math.log(2.0) - 1.0,
    "goe_large_n_fit": 0.5307,
    "gue_large_n_fit": 0.5996,
    "gse_large_n_fit": 0.6744,
}


@dataclass(frozen=True)
class HaarReferenceTargets:
    n: int
    d_a: int
    d_b: int
    haar_mean_half_vn: float
    haar_mean_half_linear: float
    mp_asymptotic_half_logneg: float
    mp_edge_proxy_half_geometric_linear: float
    page_entropy_bits: float
    haar_mean_purity: float
    mp_sqrt_moment: float
    mp_upper_edge: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)

    def four_metric_vector(self) -> np.ndarray:
        return np.array(
            [
                self.haar_mean_half_vn,
                self.haar_mean_half_linear,
                self.mp_asymptotic_half_logneg,
                self.mp_edge_proxy_half_geometric_linear,
            ],
            dtype=float,
        )

    def exact_mean_vector(self) -> np.ndarray:
        return np.array([self.haar_mean_half_vn, self.haar_mean_half_linear], dtype=float)

    def asymptotic_proxy_vector(self) -> np.ndarray:
        return np.array(
            [self.mp_asymptotic_half_logneg, self.mp_edge_proxy_half_geometric_linear],
            dtype=float,
        )


@lru_cache(maxsize=None)
def harmonic_number(k: int) -> float:
    """Return ``H_k`` using stable double-precision summation."""
    if k < 1:
        return 0.0
    # NumPy vectorization is materially faster for the million-scale values
    # reached at n=20 while retaining more than enough float64 accuracy here.
    values = np.arange(1, int(k) + 1, dtype=np.float64)
    return float(np.sum(1.0 / values, dtype=np.float64))


def balanced_dimensions(n: int) -> tuple[int, int]:
    if n < 2:
        raise ValueError("n must be at least two.")
    m = n // 2
    return 1 << m, 1 << (n - m)


def haar_reference_targets(
    n: int, d_a: int | None = None, d_b: int | None = None
) -> HaarReferenceTargets:
    """Return clearly typed finite-Haar means and balanced-MP proxies."""
    if d_a is None or d_b is None:
        d_a, d_b = balanced_dimensions(n)
    d_a, d_b = int(d_a), int(d_b)
    if d_a > d_b:
        d_a, d_b = d_b, d_a
    if d_a <= 1 or d_b <= 1:
        return HaarReferenceTargets(
            int(n), d_a, d_b, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0
        )

    log2_da = math.log2(d_a)
    page_bits = (
        (harmonic_number(d_a * d_b) - harmonic_number(d_b)) / math.log(2.0)
        - (d_a - 1.0) / (2.0 * d_b * math.log(2.0))
    )
    vn = page_bits / log2_da

    mean_purity = (d_a + d_b) / (d_a * d_b + 1.0)
    linear = (d_a / (d_a - 1.0)) * (1.0 - mean_purity)

    if d_a == d_b:
        mp_sqrt_moment = 8.0 / (3.0 * math.pi)
        logneg = 1.0 + 2.0 * math.log2(mp_sqrt_moment) / log2_da
        mp_edge = 4.0
        geo = (d_a / (d_a - 1.0)) * (1.0 - mp_edge / d_a)
    else:
        mp_sqrt_moment = float("nan")
        logneg = float("nan")
        mp_edge = float("nan")
        geo = float("nan")

    def bounded(value: float) -> float:
        return float(np.clip(value, 0.0, 1.0)) if np.isfinite(value) else float("nan")

    return HaarReferenceTargets(
        n=int(n),
        d_a=d_a,
        d_b=d_b,
        haar_mean_half_vn=bounded(vn),
        haar_mean_half_linear=bounded(linear),
        mp_asymptotic_half_logneg=bounded(logneg),
        mp_edge_proxy_half_geometric_linear=bounded(geo),
        page_entropy_bits=float(page_bits),
        haar_mean_purity=float(mean_purity),
        mp_sqrt_moment=float(mp_sqrt_moment),
        mp_upper_edge=float(mp_edge),
    )


def reference_distance_components(
    row: Mapping[str, float], target: HaarReferenceTargets
) -> dict[str, float]:
    obs = np.array([float(row[column]) for column in REFERENCE_METRIC_COLUMNS], dtype=float)
    full = target.four_metric_vector()
    deltas = obs - full
    return {
        "reference_distance_4metric": float(np.sqrt(np.nanmean(deltas**2))),
        "haar_mean_distance_vn_linear": float(np.sqrt(np.mean(deltas[:2] ** 2))),
        "mp_proxy_distance_logneg_geo": float(np.sqrt(np.nanmean(deltas[2:] ** 2))),
        **{
            f"delta_{column}_minus_reference": float(delta)
            for column, delta in zip(REFERENCE_METRIC_COLUMNS, deltas)
        },
    }


def add_reference_columns_to_frame(frame):
    """Add target, deviation, and descriptive distance columns to a DataFrame."""
    import pandas as pd

    missing = sorted(set(("n", *REFERENCE_METRIC_COLUMNS)) - set(frame.columns))
    if missing:
        raise ValueError(f"Input table lacks reference-analysis columns: {missing}")
    out = frame.copy()
    targets = {int(n): haar_reference_targets(int(n)) for n in sorted(out["n"].unique())}

    target_column_map = {
        "reference_half_vn": "haar_mean_half_vn",
        "reference_half_linear": "haar_mean_half_linear",
        "reference_half_logneg": "mp_asymptotic_half_logneg",
        "reference_half_geometric_linear": "mp_edge_proxy_half_geometric_linear",
        "reference_page_entropy_bits": "page_entropy_bits",
        "reference_haar_mean_purity": "haar_mean_purity",
        "reference_mp_sqrt_moment": "mp_sqrt_moment",
        "reference_mp_upper_edge": "mp_upper_edge",
        "reference_d_a": "d_a",
        "reference_d_b": "d_b",
    }
    for output, attribute in target_column_map.items():
        mapping = {n: getattr(target, attribute) for n, target in targets.items()}
        out[output] = out["n"].map(mapping)

    component_rows = [
        reference_distance_components(row._asdict(), targets[int(row.n)])
        for row in out.itertuples(index=False)
    ]
    components = pd.DataFrame(component_rows, index=out.index)
    out = pd.concat([out, components], axis=1)
    targets_frame = pd.DataFrame([targets[n].as_dict() for n in sorted(targets)])
    return out, targets_frame


def summarize_reference_approach(frame):
    """Run-level descriptive summaries without arbitrary crossing thresholds."""
    import pandas as pd

    required = {
        "model",
        "n",
        "run_id",
        "regime",
        "initial_state",
        "step",
        "tau",
        "reference_distance_4metric",
        "haar_mean_distance_vn_linear",
        "mp_proxy_distance_logneg_geo",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Input table lacks summary columns: {missing}")

    rows: list[dict[str, float | int | str]] = []
    for (model, n, run_id), group in frame.groupby(["model", "n", "run_id"], sort=True):
        group = group.sort_values("step")
        tau = group["tau"].to_numpy(float)
        d4 = group["reference_distance_4metric"].to_numpy(float)
        de = group["haar_mean_distance_vn_linear"].to_numpy(float)
        da = group["mp_proxy_distance_logneg_geo"].to_numpy(float)
        idx = int(np.nanargmin(d4))
        if len(group) > 1 and np.std(tau) > 0.0 and np.std(d4) > 0.0:
            tau_rank = pd.Series(tau).rank(method="average").to_numpy()
            dist_rank = pd.Series(d4).rank(method="average").to_numpy()
            rank_corr = float(np.corrcoef(tau_rank, dist_rank)[0, 1])
        else:
            rank_corr = float("nan")
        steps_toward = int(np.sum(np.diff(d4) < 0.0))
        steps_away = int(np.sum(np.diff(d4) > 0.0))
        rows.append(
            {
                "model": str(model),
                "n": int(n),
                "run_id": str(run_id),
                "regime": str(group["regime"].iloc[0]),
                "initial_state": str(group["initial_state"].iloc[0]),
                "num_points": int(len(group)),
                "max_tau": float(tau[-1]),
                "start_reference_distance_4metric": float(d4[0]),
                "end_reference_distance_4metric": float(d4[-1]),
                "min_reference_distance_4metric": float(d4[idx]),
                "tau_at_min_reference_distance": float(tau[idx]),
                "net_reference_approach": float(d4[0] - d4[-1]),
                "post_minimum_rebound": float(d4[-1] - d4[idx]),
                "end_to_minimum_ratio": float(d4[-1] / d4[idx]) if d4[idx] > 0 else float("inf"),
                "time_distance_spearman": rank_corr,
                "steps_toward_reference": steps_toward,
                "steps_away_from_reference": steps_away,
                "end_haar_mean_distance_vn_linear": float(de[-1]),
                "end_mp_proxy_distance_logneg_geo": float(da[-1]),
            }
        )
    return pd.DataFrame(rows)


def marchenko_pastur_pdf_balanced(x: np.ndarray | float) -> np.ndarray | float:
    """Balanced MP density for ``x=d*lambda`` on ``(0,4)``."""
    values = np.asarray(x, dtype=float)
    out = np.zeros_like(values)
    mask = (values > 0.0) & (values < 4.0)
    out[mask] = np.sqrt((4.0 - values[mask]) / values[mask]) / (2.0 * math.pi)
    return float(out) if out.ndim == 0 else out


def marchenko_pastur_cdf_balanced(x: np.ndarray | float) -> np.ndarray | float:
    """Analytic balanced MP CDF.

    For ``0<x<4``, write ``x=4 sin^2(theta)``.  Then
    ``F(x)=(2 theta + sin(2 theta))/pi``.
    """
    values = np.asarray(x, dtype=float)
    clipped = np.clip(values, 0.0, 4.0)
    theta = np.arcsin(np.sqrt(clipped / 4.0))
    out = (2.0 * theta + np.sin(2.0 * theta)) / math.pi
    out = np.where(values <= 0.0, 0.0, out)
    out = np.where(values >= 4.0, 1.0, out)
    return float(out) if out.ndim == 0 else out


def mp_ks_distance_from_spectrum(lam: np.ndarray, d: int | None = None) -> float:
    values = np.asarray(lam, dtype=float)
    values = values[np.isfinite(values)]
    values = np.clip(values, 0.0, None)
    total = float(values.sum())
    if total <= 0.0:
        return float("nan")
    values /= total
    if d is None:
        d = values.size
    x = np.sort(float(d) * values)
    count = x.size
    if count == 0:
        return float("nan")
    cdf = np.asarray(marchenko_pastur_cdf_balanced(x), dtype=float)
    empirical_hi = np.arange(1, count + 1, dtype=float) / count
    empirical_lo = np.arange(0, count, dtype=float) / count
    return float(
        np.max(np.maximum(np.abs(empirical_hi - cdf), np.abs(empirical_lo - cdf)))
    )


def entanglement_gap_ratios(
    lam: np.ndarray,
    *,
    eps: float = 1e-14,
    scaled_window: tuple[float, float] | None = None,
) -> np.ndarray:
    """Adjacent ratios for ``xi=-log(lambda)`` without unfolding.

    ``scaled_window=(low,high)`` restricts to a contiguous window in
    ``x=d*lambda`` before forming adjacent spacings.  This is a descriptive
    bulk statistic; no symmetry class is inferred automatically.
    """
    values = np.asarray(lam, dtype=float)
    values = values[np.isfinite(values) & (values > eps)]
    if values.size < 4:
        return np.array([], dtype=float)
    values /= float(values.sum())
    d = int(np.asarray(lam).size)
    if scaled_window is not None:
        low, high = map(float, scaled_window)
        if not 0.0 <= low < high:
            raise ValueError("scaled_window must satisfy 0 <= low < high.")
        x = d * values
        values = values[(x >= low) & (x <= high)]
        if values.size < 4:
            return np.array([], dtype=float)
    xi = -np.log(np.sort(values)[::-1])
    spacings = np.diff(xi)
    if spacings.size < 2:
        return np.array([], dtype=float)
    left, right = spacings[:-1], spacings[1:]
    denominator = np.maximum(left, right)
    mask = denominator > eps
    if not np.any(mask):
        return np.array([], dtype=float)
    return np.clip(np.minimum(left[mask], right[mask]) / denominator[mask], 0.0, 1.0)


def spectrum_summary(
    lam: np.ndarray,
    *,
    rank_eps: float = 1e-14,
    bulk_window: tuple[float, float] = (0.05, 3.95),
) -> dict[str, float | int]:
    values = np.asarray(lam, dtype=float)
    values = values[np.isfinite(values)]
    values = np.clip(values, 0.0, None)
    total = float(values.sum())
    if total <= 0.0:
        raise ValueError("Spectrum has zero total weight.")
    values /= total
    d = values.size
    purity = float(np.dot(values, values))
    full_ratios = entanglement_gap_ratios(values, eps=rank_eps)
    bulk_ratios = entanglement_gap_ratios(
        values, eps=rank_eps, scaled_window=bulk_window
    )
    x = d * values
    low, high = bulk_window
    return {
        "schmidt_rank_eps_1e14": int(np.count_nonzero(values > rank_eps)),
        "lambda_max": float(np.max(values)),
        "lambda_max_scaled": float(d * np.max(values)),
        "effective_rank_over_d": float((1.0 / purity) / d),
        "mp_ks_distance": mp_ks_distance_from_spectrum(values, d=d),
        "ent_gap_ratio_full_mean": float(np.mean(full_ratios)) if full_ratios.size else float("nan"),
        "ent_gap_ratio_full_std": float(np.std(full_ratios)) if full_ratios.size else float("nan"),
        "ent_gap_ratio_full_count": int(full_ratios.size),
        "ent_gap_ratio_bulk_mean": float(np.mean(bulk_ratios)) if bulk_ratios.size else float("nan"),
        "ent_gap_ratio_bulk_std": float(np.std(bulk_ratios)) if bulk_ratios.size else float("nan"),
        "ent_gap_ratio_bulk_count": int(bulk_ratios.size),
        "mp_bulk_fraction_005_395": float(np.mean((x >= low) & (x <= high))),
        "mp_left_edge_fraction_lt005": float(np.mean(x < low)),
        "mp_right_outlier_fraction_gt4": float(np.mean(x > 4.0)),
    }
