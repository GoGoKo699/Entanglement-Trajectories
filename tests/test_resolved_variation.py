"""No arbitrary PCA or rank correlation from numerically constant paths."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from entanglement_trajectories import robustness as r

@pytest.fixture
def frame():
    df = pd.read_csv(Path(__file__).parents[1] / "data/trajectory_observations.csv")
    group = next(iter(df.groupby(["model", "n", "run_id"], sort=True)))[1].copy()
    t = np.linspace(0., 1., len(group))
    for i, col in enumerate(r.HALF_METRICS):
        group[col] = .2 + .1 * t ** (i + 1)
    return group

@pytest.mark.parametrize("amplitude", [0., 1e-14, 1e-12])
def test_per_path_pca_omits_unresolved_coordinate(frame, amplitude):
    frame["half_vn"] = .5 + amplitude * np.linspace(0., 1., len(frame))
    row = r.per_trajectory_common_mode_table(frame, coordinate="raw").iloc[0]
    assert row.variation_status == "unresolved_variation"
    assert np.isnan(row.pc1_explained)
    assert row.scale_floor == 1e-10

@pytest.mark.parametrize("floor", [-1., np.inf, np.nan])
def test_bad_variation_allowance_rejected(frame, floor):
    with pytest.raises(ValueError):
        r.per_trajectory_common_mode_table(frame, coordinate="raw", scale_floor=floor)
    with pytest.raises(ValueError):
        r.pairwise_metric_robustness(frame, scale_floor=floor)


def test_resolved_fit_matches_independent_svd(frame):
    matrix=frame[list(r.HALF_METRICS)].to_numpy()
    standardized=(matrix-matrix.mean(axis=0))/matrix.std(axis=0)
    squared=np.linalg.svd(standardized,compute_uv=False)**2
    row=r.per_trajectory_common_mode_table(frame,coordinate="raw").iloc[0]
    assert row.variation_status=="resolved"
    assert row.pc1_explained==pytest.approx(squared[0]/squared.sum(),abs=2e-15)


def test_zero_floor_is_explicit_unprotected_convention(frame):
    frame["half_vn"] = .5 + 1e-12*np.linspace(0.,1.,len(frame))
    row=r.per_trajectory_common_mode_table(frame,coordinate="raw",scale_floor=0).iloc[0]
    assert row.variation_status=="resolved"


def test_pairwise_correlation_reports_status_but_keeps_distance(frame, monkeypatch):
    enriched=frame.copy()
    for col in r.HALF_METRICS:
        enriched[r.BOUNDARY_HEIGHT_COLUMNS[col]]=.4
    monkeypatch.setattr(r,"add_exact_boundary_coordinates",lambda _:enriched)
    table=r.pairwise_metric_robustness(frame)
    assert (table.boundary_variation_status=="unresolved_variation").all()
    assert table.boundary_spearman.isna().all()
    assert (table.boundary_rmse==0).all()
    assert (table.raw_variation_status=="resolved").all()


def test_pairwise_scale_uses_finite_overlap_only():
    x=np.array([0.,1e-14,2e-14,1.])
    y=np.array([.1,.2,.3,np.nan])
    value,status=r._resolved_spearman(x,y,1e-10)
    assert status=="unresolved_variation" and np.isnan(value)


def test_pca_insufficient_rows(frame):
    row=r.per_trajectory_common_mode_table(frame.iloc[:2],coordinate="raw").iloc[0]
    assert row.variation_status=="insufficient_points" and np.isnan(row.pc1_explained)
