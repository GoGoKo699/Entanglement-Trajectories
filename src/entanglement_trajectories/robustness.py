"""Quantitative robustness analysis for the entanglement-trajectory atlas.

This module operationalizes the project's deliberately limited use of
"topological invariant".  It measures coarse stability under replacement of
one spectrum functional by another without asserting a formal topological
invariant.

The central half-chain metric representatives are:

* ``half_logneg``: Renyi order 1/2,
* ``half_vn``: Renyi order 1,
* ``half_linear``: the purity / Renyi-order-2 equivalence class.

The common horizontal coordinate is ``half_lambda_max`` (equivalently the Renyi
order-infinity / geometric coordinate).  Exact-boundary relative heights are
used where specified.  Degenerate fixed-lambda_max envelopes remain undefined
and are represented by NaN; distance functions use only finite overlap.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
import re
from pathlib import Path
from typing import Iterable, Literal, Sequence

import numpy as np

from .boundaries import relative_boundary_height
from .dataset import validate_canonical_frame
from .metrics import linear_entropy, log_negativity_pure, von_neumann_entropy
from .spectra import majorization_relation, normalize_spectrum

HALF_METRICS: tuple[str, ...] = ("half_vn", "half_linear", "half_logneg")
BOUNDARY_HEIGHT_COLUMNS = {
    "half_vn": "half_vn_boundary_height",
    "half_linear": "half_linear_boundary_height",
    "half_logneg": "half_logneg_boundary_height",
}
ONE_SITE_AGGREGATES: tuple[str, ...] = (
    "one_site_mean_vn",
    "one_site_mean_linear",
    "one_site_mean_logneg",
    "one_site_mean_geometric_linear",
)


def add_exact_boundary_coordinates(df, *, clip: bool = False):
    """Add direct fixed-``lambda_max`` relative heights to a canonical table."""
    validate_canonical_frame(df)
    out = df.copy()
    specifications = (
        ("von_neumann_entropy", "half_vn", BOUNDARY_HEIGHT_COLUMNS["half_vn"]),
        ("linear_entropy", "half_linear", BOUNDARY_HEIGHT_COLUMNS["half_linear"]),
        ("log_negativity_pure", "half_logneg", BOUNDARY_HEIGHT_COLUMNS["half_logneg"]),
    )
    for n, indices in out.groupby("n").groups.items():
        d = 1 << (int(n) // 2)
        p = out.loc[indices, "half_lambda_max"].to_numpy(dtype=float)
        for metric_id, value_column, output_column in specifications:
            values = out.loc[indices, value_column].to_numpy(dtype=float)
            out.loc[indices, output_column] = relative_boundary_height(
                metric_id,
                p,
                values,
                d,
                normalized_metric=True,
                base=2.0,
                on_degenerate="nan",
                clip=clip,
            )
    return out


@dataclass(frozen=True)
class CommonModeFit:
    """PCA-like decomposition of the three metric coordinates.

    The input coordinates are standardized before singular-value
    decomposition.  Component one is oriented to have positive total loading.
    Component two is oriented so the linear-entropy loading is non-positive,
    which makes serialized results deterministic.
    """

    columns: tuple[str, ...]
    mean: np.ndarray
    scale: np.ndarray
    components: np.ndarray
    explained_variance_ratio: np.ndarray
    finite_rows: int
    total_rows: int

    def transform(self, values: np.ndarray) -> np.ndarray:
        """Project rows into the fitted common/contrast coordinates."""
        arr = np.asarray(values, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != len(self.columns):
            raise ValueError("values must have shape (rows, number_of_metrics).")
        out = np.full((arr.shape[0], self.components.shape[0]), np.nan, dtype=float)
        finite = np.all(np.isfinite(arr), axis=1)
        if np.any(finite):
            out[finite] = ((arr[finite] - self.mean) / self.scale) @ self.components.T
        return out

    def as_dict(self) -> dict:
        return {
            "columns": list(self.columns),
            "mean": self.mean.tolist(),
            "scale": self.scale.tolist(),
            "components": self.components.tolist(),
            "explained_variance_ratio": self.explained_variance_ratio.tolist(),
            "finite_rows": int(self.finite_rows),
            "total_rows": int(self.total_rows),
        }


def _safe_spearman(x: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import spearmanr

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(finite) < 3:
        return float("nan")
    result = spearmanr(x[finite], y[finite])
    return float(result.statistic)


def _safe_pearson(x: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import pearsonr

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(finite) < 3:
        return float("nan")
    result = pearsonr(x[finite], y[finite])
    return float(result.statistic)


def _nan_rms_distance(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError("Distance arrays must have the same shape.")
    finite = np.isfinite(x) & np.isfinite(y)
    if not np.any(finite):
        return float("nan")
    return float(np.sqrt(np.mean((x[finite] - y[finite]) ** 2)))


def _nanmean_stack(arrays: Sequence[np.ndarray]) -> np.ndarray:
    if not arrays:
        raise ValueError("At least one array is required.")
    stack = np.stack([np.asarray(x, dtype=float) for x in arrays])
    finite_count = np.sum(np.isfinite(stack), axis=0)
    total = np.nansum(stack, axis=0)
    out = np.full(stack.shape[1:], np.nan, dtype=float)
    valid = finite_count > 0
    out[valid] = total[valid] / finite_count[valid]
    return out


def _condition_index(run_id: str) -> int:
    match = re.search(r"(\d+)$", str(run_id))
    if match is None:
        raise ValueError(f"run_id does not end in a condition index: {run_id!r}")
    return int(match.group(1))


def fit_common_metric_mode(
    df,
    *,
    coordinate: Literal["raw", "boundary"] = "boundary",
) -> CommonModeFit:
    """Fit a standardized common/contrast decomposition across three metrics."""
    validate_canonical_frame(df)
    work = add_exact_boundary_coordinates(df) if coordinate == "boundary" else df
    columns = (
        tuple(BOUNDARY_HEIGHT_COLUMNS[m] for m in HALF_METRICS)
        if coordinate == "boundary"
        else HALF_METRICS
    )
    values = work[list(columns)].to_numpy(dtype=float)
    finite = np.all(np.isfinite(values), axis=1)
    matrix = values[finite]
    if matrix.shape[0] < 3:
        raise ValueError("At least three finite rows are needed for a common-mode fit.")
    mean = matrix.mean(axis=0)
    scale = matrix.std(axis=0)
    if np.any(scale <= 0.0):
        raise ValueError("Every metric coordinate must have nonzero variance.")
    standardized = (matrix - mean) / scale
    _, singular, components = np.linalg.svd(standardized, full_matrices=False)
    variance = singular**2
    explained = variance / variance.sum()
    if float(np.sum(components[0])) < 0.0:
        components[0] *= -1.0
    # Deterministic orientation for the main contrast mode: q=2 negative.
    if components.shape[0] > 1 and components[1, 1] > 0.0:
        components[1] *= -1.0
    return CommonModeFit(
        columns=columns,
        mean=mean,
        scale=scale,
        components=components,
        explained_variance_ratio=explained,
        finite_rows=int(matrix.shape[0]),
        total_rows=int(values.shape[0]),
    )


def per_trajectory_common_mode_table(
    df,
    *,
    coordinate: Literal["raw", "boundary"] = "boundary",
):
    """Explained-variance ratios from separate standardized fits per trajectory."""
    import pandas as pd

    validate_canonical_frame(df)
    work = add_exact_boundary_coordinates(df) if coordinate == "boundary" else df
    columns = (
        [BOUNDARY_HEIGHT_COLUMNS[m] for m in HALF_METRICS]
        if coordinate == "boundary"
        else list(HALF_METRICS)
    )
    rows = []
    for key, group in work.groupby(["model", "n", "run_id"], sort=True):
        matrix = group[columns].to_numpy(dtype=float)
        matrix = matrix[np.all(np.isfinite(matrix), axis=1)]
        if matrix.shape[0] < 3 or np.any(matrix.std(axis=0) <= 0.0):
            explained = np.array([np.nan, np.nan, np.nan])
        else:
            standardized = (matrix - matrix.mean(axis=0)) / matrix.std(axis=0)
            singular = np.linalg.svd(standardized, compute_uv=False, full_matrices=False)
            variance = singular**2
            explained = variance / variance.sum()
        rows.append(
            {
                "model": key[0],
                "n": int(key[1]),
                "run_id": key[2],
                "coordinate": coordinate,
                "finite_points": int(matrix.shape[0]),
                "pc1_explained": float(explained[0]),
                "pc2_explained": float(explained[1]),
                "pc3_explained": float(explained[2]),
            }
        )
    return pd.DataFrame(rows)


def pairwise_metric_robustness(df):
    """Within-trajectory rank agreement and exact-boundary separation."""
    import pandas as pd

    validate_canonical_frame(df)
    enriched = add_exact_boundary_coordinates(df)
    rows = []
    for key, group in enriched.groupby(["model", "n", "run_id"], sort=True):
        group = group.sort_values("step")
        for first, second in combinations(HALF_METRICS, 2):
            a_raw = group[first].to_numpy(dtype=float)
            b_raw = group[second].to_numpy(dtype=float)
            a_boundary = group[BOUNDARY_HEIGHT_COLUMNS[first]].to_numpy(dtype=float)
            b_boundary = group[BOUNDARY_HEIGHT_COLUMNS[second]].to_numpy(dtype=float)
            overlap = np.isfinite(a_boundary) & np.isfinite(b_boundary)
            rows.append(
                {
                    "model": key[0],
                    "n": int(key[1]),
                    "run_id": key[2],
                    "metric_a": first,
                    "metric_b": second,
                    "raw_spearman": _safe_spearman(a_raw, b_raw),
                    "boundary_spearman": _safe_spearman(a_boundary, b_boundary),
                    "boundary_rmse": _nan_rms_distance(a_boundary, b_boundary),
                    "boundary_mae": float(
                        np.mean(np.abs(a_boundary[overlap] - b_boundary[overlap]))
                    )
                    if np.any(overlap)
                    else float("nan"),
                    "finite_overlap": int(np.count_nonzero(overlap)),
                    "total_points": int(len(group)),
                }
            )
    return pd.DataFrame(rows)


def one_site_aggregate_robustness(df):
    """Rank agreement among historical one-site-averaged coordinates.

    These columns aggregate a collection of one-site spectra and are not
    treated as functions of the single half-chain spectrum.
    """
    import pandas as pd

    validate_canonical_frame(df)
    rows = []
    for key, group in df.groupby(["model", "n", "run_id"], sort=True):
        group = group.sort_values("step")
        for first, second in combinations(ONE_SITE_AGGREGATES, 2):
            rows.append(
                {
                    "model": key[0],
                    "n": int(key[1]),
                    "run_id": key[2],
                    "metric_a": first,
                    "metric_b": second,
                    "spearman": _safe_spearman(
                        group[first].to_numpy(dtype=float),
                        group[second].to_numpy(dtype=float),
                    ),
                }
            )
    return pd.DataFrame(rows)


def resample_trajectory(
    group,
    metric: str,
    *,
    coordinate: Literal["raw", "boundary"] = "boundary",
    grid: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate one trajectory without bridging undefined exact envelopes.

    The largest-Schmidt-value coordinate is always interpolated on the common
    grid. Boundary-relative metric coordinates are interpolated separately on
    each contiguous finite run in the original samples, preserving internal
    intervals where the exact envelope collapses.
    """
    if metric not in HALF_METRICS:
        raise KeyError(f"Unsupported half-chain metric: {metric!r}")
    if grid is None:
        grid = np.linspace(0.0, 4.0, 41)
    grid = np.asarray(grid, dtype=float)
    ordered = group.sort_values("tau")
    tau = ordered["tau"].to_numpy(dtype=float)
    x = np.interp(grid, tau, ordered["half_lambda_max"].to_numpy(dtype=float))
    column = BOUNDARY_HEIGHT_COLUMNS[metric] if coordinate == "boundary" else metric
    y_values = ordered[column].to_numpy(dtype=float)
    finite_indices = np.flatnonzero(np.isfinite(y_values))
    y = np.full(grid.size, np.nan, dtype=float)
    if finite_indices.size:
        split_at = np.flatnonzero(np.diff(finite_indices) > 1) + 1
        for segment in np.split(finite_indices, split_at):
            if segment.size >= 2:
                segment_tau = tau[segment]
                inside = (grid >= float(segment_tau[0])) & (grid <= float(segment_tau[-1]))
                y[inside] = np.interp(grid[inside], segment_tau, y_values[segment])
            else:
                matches = np.flatnonzero(np.isclose(grid, tau[segment[0]], atol=1e-12, rtol=0.0))
                if matches.size:
                    y[matches] = float(y_values[segment[0]])
    return x, y


def _representation(
    group,
    metric: str,
    *,
    coordinate: Literal["raw", "boundary"],
    mode: Literal["y", "full", "endpoint"],
    grid: np.ndarray,
) -> np.ndarray:
    x, y = resample_trajectory(group, metric, coordinate=coordinate, grid=grid)
    if mode == "y":
        return y
    if mode == "full":
        return np.stack([x, y], axis=1).reshape(-1)
    if mode == "endpoint":
        return np.array([x[-1], y[-1]], dtype=float)
    raise ValueError(f"Unknown representation mode: {mode!r}")


def _pairwise_distance_matrix(representations: Sequence[np.ndarray]) -> np.ndarray:
    count = len(representations)
    matrix = np.zeros((count, count), dtype=float)
    for i in range(count):
        for j in range(i + 1, count):
            value = _nan_rms_distance(representations[i], representations[j])
            matrix[i, j] = matrix[j, i] = value
    return matrix


def _nearest_neighbors(distance_matrix: np.ndarray, row: int, k: int) -> set[int]:
    if k < 1 or k >= distance_matrix.shape[0]:
        raise ValueError("k must satisfy 1 <= k < number of trajectories.")
    order = [int(i) for i in np.argsort(distance_matrix[row]) if int(i) != int(row)]
    return set(order[:k])


def _mantel_permutation_pvalue(
    first: np.ndarray,
    second: np.ndarray,
    observed: float,
    *,
    permutations: int,
    rng: np.random.Generator,
) -> float:
    """One-sided label-permutation p-value for distance-matrix rank agreement."""
    if permutations <= 0 or not np.isfinite(observed):
        return float("nan")
    from scipy.stats import rankdata

    count = first.shape[0]
    upper = np.triu_indices(count, 1)
    rank_a = rankdata(first[upper], method="average").astype(float)
    rank_b = rankdata(second[upper], method="average").astype(float)
    rank_matrix_b = np.zeros_like(second, dtype=float)
    rank_matrix_b[upper] = rank_b
    rank_matrix_b[(upper[1], upper[0])] = rank_b
    rank_a -= rank_a.mean()
    norm_a = float(np.linalg.norm(rank_a))
    exceed = 0
    for _ in range(int(permutations)):
        perm = rng.permutation(count)
        values = rank_matrix_b[np.ix_(perm, perm)][upper].astype(float)
        values -= values.mean()
        denom = norm_a * float(np.linalg.norm(values))
        value = float(np.dot(rank_a, values) / denom) if denom > 0.0 else float("nan")
        if np.isfinite(value) and value >= observed - 1e-15:
            exceed += 1
    return float((exceed + 1) / (int(permutations) + 1))


def trajectory_geometry_preservation(
    df,
    *,
    coordinate: Literal["raw", "boundary"] = "boundary",
    mode: Literal["y", "full"] = "y",
    grid: np.ndarray | None = None,
    k: int = 3,
    permutations: int = 0,
    seed: int = 20260819,
):
    """Compare the relational geometry of all trajectories across metrics.

    For each system size, the function constructs a distance matrix among the
    16 physical trajectories.  It then compares those matrices across metric
    choices by Spearman/Pearson correlation and nearest-neighbor overlap.

    ``mode='y'`` excludes the common largest-Schmidt-value coordinate and is
    therefore the nontrivial metric-coordinate test.  ``mode='full'`` uses the
    two-dimensional paths and intentionally records the contribution of the
    common horizontal coordinate.
    """
    import pandas as pd

    validate_canonical_frame(df)
    if coordinate == "boundary":
        required = tuple(BOUNDARY_HEIGHT_COLUMNS[m] for m in HALF_METRICS)
        work = df.copy() if all(column in df.columns for column in required) else add_exact_boundary_coordinates(df)
    else:
        work = df.copy()
    if grid is None:
        grid = np.linspace(0.0, 4.0, 41)
    grid = np.asarray(grid, dtype=float)
    rng = np.random.default_rng(seed)
    rows = []
    for n, size_frame in work.groupby("n", sort=True):
        keys = []
        representations: dict[str, list[np.ndarray]] = {metric: [] for metric in HALF_METRICS}
        for key, group in size_frame.groupby(["model", "run_id"], sort=True):
            keys.append((str(key[0]), str(key[1])))
            for metric in HALF_METRICS:
                representations[metric].append(
                    _representation(
                        group,
                        metric,
                        coordinate=coordinate,
                        mode=mode,
                        grid=grid,
                    )
                )
        matrices = {
            metric: _pairwise_distance_matrix(values)
            for metric, values in representations.items()
        }
        count = len(keys)
        upper = np.triu_indices(count, 1)
        for first, second in combinations(HALF_METRICS, 2):
            spearman = _safe_spearman(matrices[first][upper], matrices[second][upper])
            pearson = _safe_pearson(matrices[first][upper], matrices[second][upper])
            overlaps = []
            for row in range(count):
                neighbors_a = _nearest_neighbors(matrices[first], row, k)
                neighbors_b = _nearest_neighbors(matrices[second], row, k)
                overlaps.append(len(neighbors_a & neighbors_b) / k)
            pvalue = _mantel_permutation_pvalue(
                matrices[first],
                matrices[second],
                spearman,
                permutations=permutations,
                rng=rng,
            )
            rows.append(
                {
                    "n": int(n),
                    "coordinate": coordinate,
                    "mode": mode,
                    "metric_a": first,
                    "metric_b": second,
                    "distance_spearman": spearman,
                    "distance_pearson": pearson,
                    "knn_k": int(k),
                    "knn_overlap_mean": float(np.mean(overlaps)),
                    "knn_overlap_min": float(np.min(overlaps)),
                    "random_knn_overlap": float(k / (count - 1)),
                    "mantel_permutations": int(permutations),
                    "mantel_pvalue_one_sided": pvalue,
                    "num_trajectories": int(count),
                    "num_pair_distances": int(len(upper[0])),
                }
            )
    return pd.DataFrame(rows)


def model_centroid_geometry_preservation(
    df,
    *,
    coordinate: Literal["raw", "boundary"] = "boundary",
    mode: Literal["y", "full"] = "y",
    grid: np.ndarray | None = None,
):
    """Preservation of the six inter-model centroid distances across metrics."""
    import pandas as pd

    validate_canonical_frame(df)
    if coordinate == "boundary":
        required = tuple(BOUNDARY_HEIGHT_COLUMNS[m] for m in HALF_METRICS)
        work = df.copy() if all(column in df.columns for column in required) else add_exact_boundary_coordinates(df)
    else:
        work = df.copy()
    if grid is None:
        grid = np.linspace(0.0, 4.0, 41)
    grid = np.asarray(grid, dtype=float)
    rows = []
    models = sorted(str(x) for x in work["model"].unique())
    model_pairs = list(combinations(models, 2))
    for n, size_frame in work.groupby("n", sort=True):
        centroids: dict[str, dict[str, np.ndarray]] = {
            metric: {} for metric in HALF_METRICS
        }
        for metric in HALF_METRICS:
            for model in models:
                model_frame = size_frame[size_frame["model"] == model]
                reps = [
                    _representation(
                        group,
                        metric,
                        coordinate=coordinate,
                        mode=mode,
                        grid=grid,
                    )
                    for _, group in model_frame.groupby("run_id", sort=True)
                ]
                centroids[metric][model] = _nanmean_stack(reps)
        distances: dict[str, list[float]] = {metric: [] for metric in HALF_METRICS}
        for metric in HALF_METRICS:
            for model_a, model_b in model_pairs:
                distances[metric].append(
                    _nan_rms_distance(
                        centroids[metric][model_a], centroids[metric][model_b]
                    )
                )
        for first, second in combinations(HALF_METRICS, 2):
            rows.append(
                {
                    "n": int(n),
                    "coordinate": coordinate,
                    "mode": mode,
                    "metric_a": first,
                    "metric_b": second,
                    "distance_rank_spearman": _safe_spearman(
                        np.asarray(distances[first]), np.asarray(distances[second])
                    ),
                    "distance_pearson": _safe_pearson(
                        np.asarray(distances[first]), np.asarray(distances[second])
                    ),
                    "num_model_pairs": int(len(model_pairs)),
                }
            )
    return pd.DataFrame(rows)


def metric_direction_events(df, *, eps: float = 1e-10):
    """Classify consecutive samples by agreement among q=1/2, 1, and 2 metrics."""
    import pandas as pd

    validate_canonical_frame(df)
    rows = []
    for key, group in df.groupby(["model", "n", "run_id"], sort=True):
        ordered = group.sort_values("step").reset_index(drop=True)
        values = ordered[list(HALF_METRICS)].to_numpy(dtype=float)
        deltas = np.diff(values, axis=0)
        signs = np.where(deltas > eps, 1, np.where(deltas < -eps, -1, 0))
        for index, sign in enumerate(signs):
            nonzero = sign[sign != 0]
            if nonzero.size == 0:
                label = "stationary_all"
            elif np.all(nonzero > 0):
                label = "consensus_increase"
            elif np.all(nonzero < 0):
                label = "consensus_decrease"
            else:
                label = "metric_competition"
            rows.append(
                {
                    "model": key[0],
                    "n": int(key[1]),
                    "run_id": key[2],
                    "step_from": int(ordered.loc[index, "step"]),
                    "step_to": int(ordered.loc[index + 1, "step"]),
                    "tau_from": float(ordered.loc[index, "tau"]),
                    "tau_to": float(ordered.loc[index + 1, "tau"]),
                    "delta_half_vn": float(deltas[index, 0]),
                    "delta_half_linear": float(deltas[index, 1]),
                    "delta_half_logneg": float(deltas[index, 2]),
                    "direction_half_vn": int(sign[0]),
                    "direction_half_linear": int(sign[1]),
                    "direction_half_logneg": int(sign[2]),
                    "event_class": label,
                }
            )
    return pd.DataFrame(rows)


def _normalized_metric_triplet(spectrum: np.ndarray) -> np.ndarray:
    spectrum = normalize_spectrum(spectrum, atol=1e-8)
    return np.array(
        [
            von_neumann_entropy(spectrum, normalized=True, atol=1e-8),
            linear_entropy(spectrum, normalized=True, atol=1e-8),
            log_negativity_pure(spectrum, normalized=True, atol=1e-8),
        ],
        dtype=float,
    )


def _event_from_deltas(deltas: np.ndarray, eps: float) -> str:
    signs = np.where(deltas > eps, 1, np.where(deltas < -eps, -1, 0))
    nonzero = signs[signs != 0]
    if nonzero.size == 0:
        return "stationary_all"
    if np.all(nonzero > 0):
        return "consensus_increase"
    if np.all(nonzero < 0):
        return "consensus_decrease"
    return "metric_competition"


def majorization_transition_audit(
    spectra_directory: str | Path,
    *,
    majorization_tol: float = 1e-10,
    metric_tol: float = 1e-10,
):
    """Audit consecutive full-spectrum transitions in the selected reruns."""
    import pandas as pd

    directory = Path(spectra_directory)
    files = sorted(directory.glob("*.npz"))
    if not files:
        raise FileNotFoundError(f"No NPZ spectra found in {directory}")
    rows = []
    for path in files:
        with np.load(path) as data:
            spectra = np.asarray(data["spectra"], dtype=float)
            steps = np.asarray(data["steps"], dtype=int)
            model = str(data["model"][0])
            run_id = str(data["run_id"][0])
            n = int(data["n"][0])
            regime = str(data["regime"][0])
            initial_state = str(data["initial_state"][0])
        for index in range(len(spectra) - 1):
            first = normalize_spectrum(spectra[index], atol=1e-8)
            second = normalize_spectrum(spectra[index + 1], atol=1e-8)
            relation = majorization_relation(first, second, atol=majorization_tol)
            relation_label = {
                "equal": "equivalent",
                "x_majorizes_y": "forward_entanglement_increase",
                "y_majorizes_x": "forward_entanglement_decrease",
                "incomparable": "incomparable",
            }[relation]
            delta = _normalized_metric_triplet(second) - _normalized_metric_triplet(first)
            event = _event_from_deltas(delta, metric_tol)
            rows.append(
                {
                    "source_file": path.name,
                    "model": model,
                    "n": n,
                    "run_id": run_id,
                    "regime": regime,
                    "initial_state": initial_state,
                    "step_from": int(steps[index]),
                    "step_to": int(steps[index + 1]),
                    "majorization_tolerance": float(majorization_tol),
                    "metric_tolerance": float(metric_tol),
                    "majorization_relation": relation_label,
                    "metric_event": event,
                    "delta_half_vn": float(delta[0]),
                    "delta_half_linear": float(delta[1]),
                    "delta_half_logneg": float(delta[2]),
                }
            )
    return pd.DataFrame(rows)


def majorization_tolerance_sensitivity(
    spectra_directory: str | Path,
    *,
    tolerances: Iterable[float] = (1e-12, 1e-10, 1e-8, 1e-7, 1e-6),
    metric_tol: float = 1e-10,
):
    """Summarize how numerical majorization tolerance changes classifications."""
    import pandas as pd

    rows = []
    for tolerance in tolerances:
        table = majorization_transition_audit(
            spectra_directory,
            majorization_tol=float(tolerance),
            metric_tol=metric_tol,
        )
        counts = table["majorization_relation"].value_counts()
        competition = table[table["metric_event"] == "metric_competition"]
        rows.append(
            {
                "majorization_tolerance": float(tolerance),
                "equivalent": int(counts.get("equivalent", 0)),
                "forward_entanglement_increase": int(
                    counts.get("forward_entanglement_increase", 0)
                ),
                "forward_entanglement_decrease": int(
                    counts.get("forward_entanglement_decrease", 0)
                ),
                "incomparable": int(counts.get("incomparable", 0)),
                "metric_competition": int(len(competition)),
                "competition_outside_incomparable": int(
                    np.count_nonzero(
                        competition["majorization_relation"].to_numpy()
                        != "incomparable"
                    )
                ),
            }
        )
    return pd.DataFrame(rows)


def _trajectory_records(work) -> list[dict]:
    records = []
    for key, group in work.groupby(["model", "n", "run_id"], sort=True):
        records.append(
            {
                "model": str(key[0]),
                "n": int(key[1]),
                "run_id": str(key[2]),
                "condition": _condition_index(str(key[2])),
                "group": group.sort_values("step"),
            }
        )
    return records


def _model_centroids(
    records: Sequence[dict],
    *,
    metric: str,
    coordinate: Literal["raw", "boundary"],
    mode: Literal["y", "full", "endpoint"],
    grid: np.ndarray,
    models: Sequence[str],
) -> dict[str, np.ndarray]:
    centroids = {}
    for model in models:
        features = [
            _representation(
                record["group"],
                metric,
                coordinate=coordinate,
                mode=mode,
                grid=grid,
            )
            for record in records
            if record["model"] == model
        ]
        if not features:
            raise ValueError(f"No training features for model {model!r}.")
        centroids[model] = _nanmean_stack(features)
    return centroids


def _classify_feature(feature: np.ndarray, centroids: dict[str, np.ndarray]) -> tuple[str, float]:
    distances = {
        model: _nan_rms_distance(feature, centroid)
        for model, centroid in centroids.items()
    }
    finite = {model: value for model, value in distances.items() if np.isfinite(value)}
    if not finite:
        raise ValueError("No finite distance is available for classification.")
    prediction = min(finite, key=finite.get)
    return prediction, float(finite[prediction])


def cross_metric_classification(
    df,
    *,
    coordinate: Literal["raw", "boundary"] = "boundary",
    mode: Literal["y", "full", "endpoint"] = "full",
    fold: Literal[
        "centroid_leave_size",
        "individual_leave_size",
        "individual_leave_condition",
        "individual_double_holdout",
    ] = "individual_leave_size",
    grid: np.ndarray | None = None,
):
    """Nearest-centroid cross-metric generalization under declared holdouts.

    Every trajectory/metric representation is cached once. This leaves the
    transparent classifier unchanged while making the full fold-by-metric
    release analysis practical in continuous integration.
    """
    import pandas as pd

    validate_canonical_frame(df)
    if coordinate == "boundary":
        required = tuple(BOUNDARY_HEIGHT_COLUMNS[m] for m in HALF_METRICS)
        work = df.copy() if all(column in df.columns for column in required) else add_exact_boundary_coordinates(df)
    else:
        work = df.copy()
    if grid is None:
        grid = np.linspace(0.0, 4.0, 41)
    grid = np.asarray(grid, dtype=float)
    records = _trajectory_records(work)
    models = sorted({record["model"] for record in records})
    sizes = sorted({record["n"] for record in records})
    conditions = sorted({record["condition"] for record in records})

    def record_key(record: dict) -> tuple[str, int, str]:
        return record["model"], record["n"], record["run_id"]

    feature_cache: dict[tuple[str, int, str, str], np.ndarray] = {}
    for record in records:
        key = record_key(record)
        for metric in HALF_METRICS:
            feature_cache[(*key, metric)] = _representation(
                record["group"],
                metric,
                coordinate=coordinate,
                mode=mode,
                grid=grid,
            )

    def feature(record: dict, metric: str) -> np.ndarray:
        return feature_cache[(*record_key(record), metric)]

    def centroids(training: Sequence[dict], metric: str) -> dict[str, np.ndarray]:
        output: dict[str, np.ndarray] = {}
        for model in models:
            values = [feature(record, metric) for record in training if record["model"] == model]
            if not values:
                raise ValueError(f"No training features for model {model!r}.")
            output[model] = _nanmean_stack(values)
        return output

    if fold in {"centroid_leave_size", "individual_leave_size"}:
        fold_specs = [(size, None) for size in sizes]
    elif fold == "individual_leave_condition":
        fold_specs = [(None, condition) for condition in conditions]
    elif fold == "individual_double_holdout":
        fold_specs = [(size, condition) for size in sizes for condition in conditions]
    else:
        raise ValueError(f"Unknown fold: {fold!r}")

    predictions = []
    for held_size, held_condition in fold_specs:
        if fold in {"centroid_leave_size", "individual_leave_size"}:
            training = [record for record in records if record["n"] != held_size]
            testing_records = [record for record in records if record["n"] == held_size]
        elif fold == "individual_leave_condition":
            training = [record for record in records if record["condition"] != held_condition]
            testing_records = [record for record in records if record["condition"] == held_condition]
        else:
            training = [
                record for record in records
                if record["n"] != held_size and record["condition"] != held_condition
            ]
            testing_records = [
                record for record in records
                if record["n"] == held_size and record["condition"] == held_condition
            ]

        train_centroids = {metric: centroids(training, metric) for metric in HALF_METRICS}
        for train_metric in HALF_METRICS:
            model_centroids = train_centroids[train_metric]
            for test_metric in HALF_METRICS:
                if fold == "centroid_leave_size":
                    for model in models:
                        model_tests = [
                            feature(record, test_metric)
                            for record in testing_records
                            if record["model"] == model
                        ]
                        test_feature = _nanmean_stack(model_tests)
                        prediction, distance = _classify_feature(test_feature, model_centroids)
                        predictions.append({
                            "coordinate": coordinate, "mode": mode, "fold": fold,
                            "train_metric": train_metric, "test_metric": test_metric,
                            "held_size": int(held_size), "held_condition": np.nan,
                            "model": model, "run_id": "MODEL_CENTROID",
                            "prediction": prediction, "correct": bool(prediction == model),
                            "distance_to_prediction": distance,
                        })
                else:
                    for record in testing_records:
                        test_feature = feature(record, test_metric)
                        prediction, distance = _classify_feature(test_feature, model_centroids)
                        predictions.append({
                            "coordinate": coordinate, "mode": mode, "fold": fold,
                            "train_metric": train_metric, "test_metric": test_metric,
                            "held_size": int(held_size) if held_size is not None else np.nan,
                            "held_condition": int(held_condition) if held_condition is not None else np.nan,
                            "model": record["model"], "run_id": record["run_id"],
                            "prediction": prediction,
                            "correct": bool(prediction == record["model"]),
                            "distance_to_prediction": distance,
                        })

    prediction_table = pd.DataFrame(predictions)
    summary = (
        prediction_table.groupby(
            ["coordinate", "mode", "fold", "train_metric", "test_metric"],
            as_index=False,
        )
        .agg(accuracy=("correct", "mean"), correct=("correct", "sum"), predictions=("correct", "size"))
        .sort_values(["train_metric", "test_metric"])
    )
    return summary, prediction_table


def x_only_classification(
    df,
    *,
    mode: Literal["path", "endpoint"] = "path",
    fold: Literal[
        "centroid_leave_size",
        "individual_leave_size",
        "individual_leave_condition",
        "individual_double_holdout",
    ] = "individual_leave_size",
    grid: np.ndarray | None = None,
):
    """Largest-Schmidt-value baseline for the same classification folds."""
    import pandas as pd

    validate_canonical_frame(df)
    if grid is None:
        grid = np.linspace(0.0, 4.0, 41)
    grid = np.asarray(grid, dtype=float)
    records = _trajectory_records(df)
    models = sorted({record["model"] for record in records})
    sizes = sorted({record["n"] for record in records})
    conditions = sorted({record["condition"] for record in records})

    cache: dict[tuple[str, int, str], np.ndarray] = {}
    for record in records:
        ordered = record["group"].sort_values("tau")
        x = np.interp(
            grid,
            ordered["tau"].to_numpy(dtype=float),
            ordered["half_lambda_max"].to_numpy(dtype=float),
        )
        cache[(record["model"], record["n"], record["run_id"])] = (
            np.array([x[-1]], dtype=float) if mode == "endpoint" else x
        )

    def feature(record: dict) -> np.ndarray:
        return cache[(record["model"], record["n"], record["run_id"])]

    def centroids(training: Sequence[dict]) -> dict[str, np.ndarray]:
        return {
            model: _nanmean_stack([feature(record) for record in training if record["model"] == model])
            for model in models
        }

    if fold in {"centroid_leave_size", "individual_leave_size"}:
        fold_specs = [(size, None) for size in sizes]
    elif fold == "individual_leave_condition":
        fold_specs = [(None, condition) for condition in conditions]
    elif fold == "individual_double_holdout":
        fold_specs = [(size, condition) for size in sizes for condition in conditions]
    else:
        raise ValueError(f"Unknown fold: {fold!r}")

    rows = []
    for held_size, held_condition in fold_specs:
        if fold in {"centroid_leave_size", "individual_leave_size"}:
            training = [record for record in records if record["n"] != held_size]
            testing = [record for record in records if record["n"] == held_size]
        elif fold == "individual_leave_condition":
            training = [record for record in records if record["condition"] != held_condition]
            testing = [record for record in records if record["condition"] == held_condition]
        else:
            training = [
                record for record in records
                if record["n"] != held_size and record["condition"] != held_condition
            ]
            testing = [
                record for record in records
                if record["n"] == held_size and record["condition"] == held_condition
            ]
        model_centroids = centroids(training)
        if fold == "centroid_leave_size":
            for model in models:
                test_feature = _nanmean_stack([feature(record) for record in testing if record["model"] == model])
                prediction, distance = _classify_feature(test_feature, model_centroids)
                rows.append({
                    "mode": mode, "fold": fold, "held_size": int(held_size),
                    "held_condition": np.nan, "model": model, "run_id": "MODEL_CENTROID",
                    "prediction": prediction, "correct": bool(prediction == model),
                    "distance_to_prediction": distance,
                })
        else:
            for record in testing:
                prediction, distance = _classify_feature(feature(record), model_centroids)
                rows.append({
                    "mode": mode, "fold": fold,
                    "held_size": int(held_size) if held_size is not None else np.nan,
                    "held_condition": int(held_condition) if held_condition is not None else np.nan,
                    "model": record["model"], "run_id": record["run_id"],
                    "prediction": prediction, "correct": bool(prediction == record["model"]),
                    "distance_to_prediction": distance,
                })
    predictions = pd.DataFrame(rows)
    summary = (
        predictions.groupby(["mode", "fold"], as_index=False)
        .agg(accuracy=("correct", "mean"), correct=("correct", "sum"), predictions=("correct", "size"))
    )
    return summary, predictions

