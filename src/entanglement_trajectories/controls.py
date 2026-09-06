"""Geometry-versus-chronology controls for fixed-cut entanglement data.

Joint shuffles preserve valid instantaneous metric tuples. Matched-spectrum
references are explicitly constructed distributions, not Haar ensembles or
uniform draws from the fixed-largest-eigenvalue polytope. No source data are
modified and no new dynamics are simulated by these controls.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np

from .boundaries import metric_bounds_fixed_lmax
from .spectra import concentrated_spectrum, equal_tail_spectrum

METRICS = ("half_vn", "half_linear", "half_logneg")
METRIC_IDS = ("vn", "linear", "logneg")
SHUFFLES = ("joint", "endpoints", "time_blocks")
REFERENCES = ("capped_gamma_0.25", "capped_gamma_1", "capped_gamma_4", "extremizer_segment")


@dataclass
class Panel:
    """One size, on its original recording grid; axes path, time, metric."""
    n: int
    keys: tuple[tuple[str, str], ...]
    steps: np.ndarray
    p: np.ndarray
    raw: np.ndarray
    lower: np.ndarray
    width: np.ndarray
    heights: np.ndarray
    mask: np.ndarray

    def tail(self, tau_min: float) -> "Panel":
        keep = self.steps / self.n >= tau_min
        if np.count_nonzero(keep) < 3:
            raise ValueError("The time window has fewer than three samples.")
        return Panel(self.n, self.keys, self.steps[keep], self.p[:, keep],
                     self.raw[:, keep], self.lower[:, keep], self.width[:, keep],
                     self.heights[:, keep], self.mask[:, keep])


def make_panels(frame, *, width_floor: float = 1e-10) -> list[Panel]:
    """Build aligned panels without interpolation, clipping heights, or gap filling."""
    from .dataset import validate_canonical_frame
    validate_canonical_frame(frame)
    if not np.isfinite(width_floor) or width_floor < 1e-10:
        raise ValueError("width_floor must be finite and at least 1e-10.")
    panels = []
    for n, rows in frame.groupby("n", sort=True):
        groups = list(rows.groupby(["model", "run_id"], sort=True))
        ordered = [g.sort_values("step") for _, g in groups]
        steps = ordered[0]["step"].to_numpy(int)
        if any(not np.array_equal(g["step"], steps) for g in ordered):
            raise ValueError("Paths of one size must share the original recording grid.")
        if np.any(np.diff(steps) != 1):
            raise ValueError("This control requires consecutive integer recording steps.")
        p = np.stack([g.half_lambda_max.to_numpy(float) for g in ordered])
        raw = np.stack([g[list(METRICS)].to_numpy(float) for g in ordered])
        d = 1 << (int(n) // 2)
        if np.any(p < 1/d - 1e-12) or np.any(p > 1 + 1e-12):
            raise ValueError("Invalid largest eigenvalue.")
        p = np.clip(p, 1/d, 1.0)
        lower, upper = [], []
        for metric in METRIC_IDS:
            b = metric_bounds_fixed_lmax(metric, p, d, normalized=True)
            lower.append(b.lower); upper.append(b.upper)
        lower = np.stack(lower, axis=-1); width = np.stack(upper, axis=-1) - lower
        mask = np.all(np.isfinite(raw) & (width > width_floor), axis=-1)
        heights = np.full_like(raw, np.nan)
        np.divide(raw - lower, width, out=heights, where=mask[..., None])
        panels.append(Panel(int(n), tuple(k for k, _ in groups), steps, p,
                            raw, lower, width, heights, mask))
    return panels


def common_fraction(values: np.ndarray) -> float:
    """PC1 share of the correlation matrix, excluding incomplete rows."""
    x = np.asarray(values, float).reshape(-1, 3)
    x = x[np.isfinite(x).all(axis=1)]
    if len(x) < 3:
        return float("nan")
    z = x - x.mean(axis=0)
    scale = np.linalg.norm(z, axis=0)
    if np.any(scale <= 1e-14):
        return float("nan")
    z /= scale
    return float(np.linalg.eigvalsh(z.T @ z)[-1] / 3.0)


def roughness_per_path(values: np.ndarray, *, scale_floor: float = 1e-10) -> np.ndarray:
    """Mean squared adjacent increments after within-path standardization.

    Each trajectory is weighted once, and all three vertical coordinates have
    unit within-path population variance. No edge bridges a missing sample.
    A path is omitted if any of its metric standard deviations is <= scale_floor.
    """
    x = np.asarray(values, float)
    valid = np.isfinite(x).all(axis=-1)
    count = valid.sum(axis=1)
    means = np.where(valid[..., None], x, 0.).sum(axis=1) / np.maximum(count[:, None], 1)
    z = np.where(valid[..., None], x - means[:, None], 0.0)
    sd = np.sqrt((z*z).sum(axis=1) / np.maximum(count[:, None], 1))
    eligible = (count >= 3) & (sd > scale_floor).all(axis=1)
    z /= np.where(sd > 0, sd, 1)[:, None, :]
    edges = valid[:, 1:] & valid[:, :-1]
    difference = np.diff(z, axis=1)
    numerator = ((difference*difference) * edges[..., None]).sum(axis=(1, 2))
    out = numerator / np.maximum(3*edges.sum(axis=1), 1)
    out[~eligible | (edges.sum(axis=1) == 0)] = np.nan
    return out


def distance_agreement(values: np.ndarray) -> float:
    """Mean cross-metric Spearman agreement of vertical path RMS distances.

    Uses native grids within each size. This differs from the release's
    common 41-point interpolation grid, so its values are a new control, not
    replacements for the archived path-distance summaries.
    """
    from scipy.stats import rankdata
    x = np.asarray(values, float)
    valid = np.isfinite(x).all(axis=-1).astype(float)
    x = np.where(valid[..., None].astype(bool), x, 0.)
    overlap = valid @ valid.T
    num = np.einsum('itk,jt->ijk', x*x, valid)
    num = num + num.transpose(1, 0, 2) - 2*np.einsum('itk,jtk->ijk', x, x)
    upper = np.triu_indices(len(x), 1)
    keep = overlap[upper] >= 3
    distances = np.sqrt(np.maximum(num[upper][keep], 0) / overlap[upper][keep, None])
    if len(distances) < 3:
        return float("nan")
    ranks = rankdata(distances, axis=0)
    ranks -= ranks.mean(axis=0)
    norms = np.linalg.norm(ranks, axis=0)
    if np.any(norms == 0):
        return float("nan")
    ranks /= norms
    correlation = ranks.T @ ranks
    return float(correlation[np.triu_indices(3, 1)].mean())


def evaluate(panels: list[Panel], *, metric_eps: float = 1e-10) -> dict[str, float]:
    """Summarize point-cloud, chronology and raw-direction statistics separately."""
    out = {}
    for name in ("heights", "raw"):
        arrays = [getattr(p, name) for p in panels]
        levels = np.concatenate([x.reshape(-1, 3) for x in arrays])
        differences = np.concatenate([np.diff(x, axis=1).reshape(-1, 3) for x in arrays])
        rough = np.concatenate([roughness_per_path(x) for x in arrays])
        out[f"{name}_level_pc1"] = common_fraction(levels)
        out[f"{name}_increment_pc1"] = common_fraction(differences)
        out[f"{name}_roughness"] = float(np.nanmean(rough))
        out[f"{name}_roughness_paths"] = int(np.isfinite(rough).sum())
        out[f"{name}_distance_agreement"] = float(np.nanmean([distance_agreement(x) for x in arrays]))
    # Boundary heights are not Schur-concave entanglement measures. Direction
    # competition and majorization are tested only on raw entanglement metrics.
    delta = np.concatenate([np.diff(p.raw, axis=1).reshape(-1, 3) for p in panels])
    competition = (delta > metric_eps).any(axis=1) & (delta < -metric_eps).any(axis=1)
    out["raw_competition_rate"] = float(competition.mean())
    out["raw_competition_count"] = int(competition.sum())
    out["raw_edges"] = len(delta)
    out["height_rows"] = sum(int(p.mask.sum()) for p in panels)
    out["height_edges"] = sum(int((p.mask[:, 1:] & p.mask[:, :-1]).sum()) for p in panels)
    return out


def shuffle_panel(panel: Panel, rng: np.random.Generator,
                  policy: Literal["joint", "endpoints", "time_blocks"] = "joint") -> Panel:
    """Shuffle complete instantaneous tuples within each path; masks stay fixed.

    Rows lacking a complete set of boundary heights are held at their original
    positions. All metrics, p and bounds move together. 'endpoints' additionally
    holds the first/last eligible rows fixed. 'time_blocks' shuffles within
    predeclared half-unit tau bins to retain the slow temporal envelope.
    """
    if policy not in SHUFFLES:
        raise ValueError(f"Unknown shuffle policy: {policy}")
    indices = np.broadcast_to(np.arange(len(panel.steps)), panel.mask.shape).copy()
    for j, mask in enumerate(panel.mask):
        eligible = np.flatnonzero(mask)
        if policy == "endpoints":
            eligible = eligible[1:-1]
        if policy == "time_blocks":
            bins = (2*panel.steps[eligible]) // panel.n
            parts = [eligible[bins == b] for b in np.unique(bins)]
        else:
            parts = [eligible]
        for part in parts:
            indices[j, part] = rng.permutation(part)
    row = np.arange(len(indices))[:, None]
    def perm(x): return x[row, indices]
    return Panel(panel.n, panel.keys, panel.steps.copy(), perm(panel.p), perm(panel.raw),
                 perm(panel.lower), perm(panel.width), perm(panel.heights), panel.mask.copy())


def capped_weights(weights: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Return tails t_i=min(p,c*w_i) summing to 1-p by active-set water filling.

    This construction is a pushforward of positive weights, NOT a conditional
    Dirichlet draw and NOT uniform on the capped simplex. It can have atoms on
    faces where additional entries equal p. These facts must accompany results.
    """
    w = np.asarray(weights, float).copy()
    p = np.asarray(p, float)
    if w.ndim != 2 or p.shape != (len(w),) or w.shape[1] < 1:
        raise ValueError("weights must have shape (rows,d-1); p must have shape (rows,).")
    d = w.shape[1] + 1
    if not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError("Weights must be finite and strictly positive.")
    if not np.isfinite(p).all() or (p < 1/d).any() or (p > 1).any():
        raise ValueError("p must lie in [1/d,1].")
    result = np.zeros_like(w)
    for _ in range(d):
        remaining = np.maximum(0., (1-p) - result.sum(axis=1))
        mass = w.sum(axis=1)
        proposal = np.divide(remaining, mass, out=np.zeros_like(mass), where=mass > 0)[:, None]*w
        saturated = proposal > p[:, None]
        done = ~saturated.any(axis=1)
        result[done] += proposal[done]
        w[done] = 0
        if done.all():
            break
        result[saturated] = np.broadcast_to(p[:, None], w.shape)[saturated]
        w[saturated] = 0
    else:
        raise ArithmeticError("Capped-weight active set failed to terminate.")
    if not np.allclose(result.sum(axis=1), 1-p, atol=2e-13, rtol=0):
        raise ArithmeticError("Capped tails have incorrect mass.")
    if np.any(result < 0) or np.any(result > p[:, None] + 2e-13):
        raise ArithmeticError("Capped tails violate the largest-value constraint.")
    return result


def sample_matched_spectra(p: np.ndarray, d: int, rng: np.random.Generator,
                            reference: str, *, segment_basis=None) -> np.ndarray:
    """Independent spectra with declared ambient d and identical largest value p."""
    if reference not in REFERENCES:
        raise ValueError(f"Unknown reference generator: {reference}")
    p = np.asarray(p, float).reshape(-1)
    if d < 2 or (p < 1/d).any() or (p > 1).any():
        raise ValueError("Invalid dimension or p.")
    if reference == "extremizer_segment":
        if segment_basis is None:
            c = np.stack([concentrated_spectrum(float(v), d) for v in p])
            u = np.stack([equal_tail_spectrum(float(v), d) for v in p])
        else:
            c, u = segment_basis
        mix = rng.random((len(p), 1))
        out = (1-mix)*c + mix*u
    else:
        alpha = float(reference.rsplit("_", 1)[1])
        weights = rng.gamma(alpha, 1., (len(p), d-1))
        # The declared alpha >= 0.25 makes underflow extraordinarily unlikely;
        # never silently turn an underflow into an exact support statement.
        if (weights <= 0).any():
            raise ArithmeticError("Gamma weight underflow; choose another seed or higher precision.")
        out = np.column_stack([p, capped_weights(weights, p)])
    if not np.allclose(out.sum(axis=1), 1., atol=3e-13, rtol=0):
        raise ArithmeticError("Matched spectrum normalization failure.")
    if not np.allclose(out.max(axis=1), p, atol=3e-13, rtol=0):
        raise ArithmeticError("Matched spectrum largest-value failure.")
    return out


def spectrum_metrics_batch(spectra: np.ndarray) -> np.ndarray:
    """The same three normalized spectral functionals, evaluated in batches."""
    from scipy.special import xlogy
    x = np.asarray(spectra, float)
    if x.ndim != 2 or x.shape[1] < 2 or not np.isfinite(x).all() or (x < 0).any():
        raise ValueError("Invalid batch of spectra.")
    if not np.allclose(x.sum(axis=1), 1, atol=3e-12, rtol=0):
        raise ValueError("Spectra must be normalized.")
    d = x.shape[1]
    vn = -xlogy(x, x).sum(axis=1)/math.log(d)
    linear = (x*(1-x)).sum(axis=1) * d/(d-1)
    logneg = 2*np.log(np.sqrt(x).sum(axis=1))/math.log(d)
    return np.column_stack([vn, linear, logneg])


def matched_panel(panel: Panel, rng: np.random.Generator, reference: str,
                  *, segment_basis=None) -> tuple[Panel, dict[str, float]]:
    d = 1 << (panel.n // 2)
    values = sample_matched_spectra(panel.p.ravel(), d, rng, reference,
                                    segment_basis=segment_basis)
    raw = spectrum_metrics_batch(values).reshape(panel.raw.shape)
    heights = np.full_like(raw, np.nan)
    np.divide(raw-panel.lower, panel.width, out=heights, where=panel.mask[..., None])
    result = Panel(panel.n, panel.keys, panel.steps.copy(), panel.p.copy(), raw,
                   panel.lower, panel.width, heights, panel.mask.copy())
    diagnostics = {"max_mass_error": float(np.max(np.abs(values.sum(axis=1)-1))),
                   "max_lmax_error": float(np.max(np.abs(values.max(axis=1)-panel.p.ravel()))),
                   "smallest_height": float(np.nanmin(heights)),
                   "largest_height": float(np.nanmax(heights))}
    return result, diagnostics


def reference_summary(observed: dict, records: list[dict]) -> dict:
    """Reference quantiles and add-one directional tail fractions.

    For fixed designed trajectories these are conditional surrogate summaries,
    not population p-values or a probability that a physical theory is true.
    """
    output = {}
    for metric, value in observed.items():
        if not metric.endswith(("pc1", "roughness", "agreement", "rate")):
            continue
        samples = np.array([r[metric] for r in records], float)
        samples = samples[np.isfinite(samples)]
        if not len(samples):
            continue
        tol = 1e-12
        output[metric] = {"observed": value, "reference_mean": float(samples.mean()),
            "reference_q025": float(np.quantile(samples, .025)),
            "reference_q975": float(np.quantile(samples, .975)),
            "observed_minus_reference_mean": float(value - samples.mean()),
            "lower_tail_fraction": float((1+np.count_nonzero(samples <= value+tol))/(len(samples)+1)),
            "upper_tail_fraction": float((1+np.count_nonzero(samples >= value-tol))/(len(samples)+1)),
            "draws": len(samples)}
    return output


def exact_joint_expectations(panels: list[Panel], *, metric_eps: float = 1e-10) -> list[dict]:
    """Analytical joint-shuffle means, independently of Monte Carlo draws.

    Distinct eligible endpoints are a uniform ordered pair from F rows.
    A unit-population-variance coordinate therefore has expected squared
    increment 2F/(F-1). Raw metric competition is averaged over the exact
    pair table, including edges with one or two frozen endpoints.
    """
    records = []
    for p in panels:
        roughness = roughness_per_path(p.heights)
        for i, key in enumerate(p.keys):
            mask = p.mask[i]
            eligible = np.flatnonzero(mask)
            count = len(eligible)
            x = p.raw[i]
            delta = x[None, :, :] - x[:, None, :]
            competition = (delta > metric_eps).any(axis=2) & (delta < -metric_eps).any(axis=2)
            expected = 0.
            for j in range(len(mask)-1):
                if mask[j] and mask[j+1]:
                    expected += competition[np.ix_(eligible, eligible)].sum() / (count*(count-1))
                elif mask[j]:
                    expected += competition[eligible, j+1].mean()
                elif mask[j+1]:
                    expected += competition[j, eligible].mean()
                else:
                    expected += float(competition[j, j+1])
            records.append({'model':key[0], 'run_id':key[1], 'n':p.n,
                'eligible_rows':count, 'raw_edges':len(mask)-1,
                'observed_height_roughness':float(roughness[i]),
                'exact_joint_mean_height_roughness':2*count/(count-1) if np.isfinite(roughness[i]) else float('nan'),
                'observed_raw_competition':int(competition[np.arange(len(mask)-1),np.arange(1,len(mask))].sum()),
                'exact_joint_mean_raw_competition':float(expected)})
    return records
