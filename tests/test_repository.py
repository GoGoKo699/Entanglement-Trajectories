"""Consolidated scientific and release tests for the compact repository.

The original modular test files are consolidated to keep the browser-upload
release below GitHub's per-upload file-count limit.
"""
# ===========================================================================
# Source module: test_aggregates.py
# ===========================================================================
import numpy as np

from entanglement_trajectories.aggregates import mean_cut_metric, meyer_wallach_q


def test_one_site_aggregates():
    spectra = np.array([
        [1.0, 0.0],
        [0.5, 0.5],
        [0.75, 0.25],
    ])
    expected = np.mean([0.0, 1.0, 0.75])
    assert np.isclose(meyer_wallach_q(spectra), expected)
    assert np.isclose(mean_cut_metric(spectra, "linear_entropy"), expected)


# ===========================================================================
# Source module: test_boundaries.py
# ===========================================================================
import math

import numpy as np
import pytest

from entanglement_trajectories.boundaries import (
    DegenerateEnvelopeError,
    boundary_curve,
    metric_bounds_fixed_lmax,
    relative_boundary_height,
)
from entanglement_trajectories.metrics import metric_value
from entanglement_trajectories.spectra import (
    concentrated_spectrum,
    equal_tail_spectrum,
    random_capped_spectrum,
)


ENTROPY_METRICS = [
    ("von_neumann_entropy", None),
    ("renyi_entropy", 0.25),
    ("renyi_half", None),
    ("renyi_two", None),
    ("renyi_three", None),
    ("renyi_entropy", 8.0),
    ("min_entropy", None),
    ("linear_entropy", None),
    ("log_negativity_pure", None),
    ("negativity_pure", None),
    ("effective_rank", 0.5),
    ("effective_rank", 1.0),
    ("effective_rank", 2.0),
    ("i_concurrence", None),
    ("i_tangle", None),
]


@pytest.mark.parametrize("metric,q", ENTROPY_METRICS)
def test_extremizers_saturate_registered_bounds(metric, q):
    d = 7
    for p in np.linspace(1/d, 1, 31):
        b = metric_bounds_fixed_lmax(metric, float(p), d, q=q, normalized=True)
        c = concentrated_spectrum(float(p), d)
        u = equal_tail_spectrum(float(p), d)
        assert np.isclose(metric_value(metric, c, q=q, normalized=True), b.lower, atol=2e-11)
        assert np.isclose(metric_value(metric, u, q=q, normalized=True), b.upper, atol=2e-11)
        assert b.lower <= b.upper + 2e-11


def test_random_spectra_obey_all_registered_bounds():
    rng = np.random.default_rng(424242)
    metrics = ENTROPY_METRICS + [
        ("purity", None),
        ("schmidt_gap", None),
        ("schmidt_ratio", None),
        ("entanglement_hamiltonian_gap", None),
    ]
    for d in (3, 5, 9):
        for p in np.linspace(1/d + 1e-6, 0.97, 11):
            for _ in range(20):
                lam = random_capped_spectrum(float(p), d, rng)
                for metric, q in metrics:
                    b = metric_bounds_fixed_lmax(metric, float(p), d, q=q, normalized=False)
                    value = metric_value(metric, lam, q=q, normalized=False)
                    assert value >= b.lower - 3e-10
                    if np.isfinite(b.upper):
                        assert value <= b.upper + 3e-10


def test_closed_form_schmidt_gap_bounds():
    d = 11
    for p in np.linspace(1/d, 0.99, 31):
        g = metric_bounds_fixed_lmax("schmidt_gap", p, d)
        lg = metric_bounds_fixed_lmax("entanglement_hamiltonian_gap", p, d, base=math.e)
        assert np.isclose(g.lower, max(0.0, 2*p-1), atol=2e-12)
        assert np.isclose(g.upper, p-(1-p)/(d-1), atol=2e-12)
        assert np.isclose(lg.lower, max(0.0, math.log(p/(1-p))), atol=2e-12)
        assert np.isclose(lg.upper, math.log(p*(d-1)/(1-p)), atol=2e-12)


def test_boundary_relative_coordinate_is_exact_and_endpoint_safe():
    d = 8
    p = 0.41
    b = metric_bounds_fixed_lmax("von_neumann_entropy", p, d, normalized=True)
    assert np.isclose(relative_boundary_height("vn", p, b.lower, d, normalized_metric=True), 0.0)
    assert np.isclose(relative_boundary_height("vn", p, b.upper, d, normalized_metric=True), 1.0)
    assert np.isclose(relative_boundary_height("vn", p, 0.5*(b.lower+b.upper), d, normalized_metric=True), 0.5)
    assert math.isnan(relative_boundary_height("vn", 1.0, 0.0, d, normalized_metric=True))
    with pytest.raises(DegenerateEnvelopeError):
        relative_boundary_height("vn", 1.0, 0.0, d, normalized_metric=True, on_degenerate="raise")
    assert math.isnan(relative_boundary_height("geometric_linear", p, 0.5, d, normalized_metric=True))


def test_vectorized_boundary_and_curve():
    d = 16
    p = np.linspace(1/d, 1, 25)
    b = metric_bounds_fixed_lmax("renyi_entropy", p, d, q=0.5, normalized=True)
    assert np.asarray(b.lower).shape == p.shape
    assert np.all(np.asarray(b.lower) <= np.asarray(b.upper) + 1e-12)
    curve = boundary_curve("linear_entropy", d, normalized=True, points=77, x_coordinate="geometric_linear")
    assert curve["x"].shape == (77,)
    assert np.isclose(curve["x"][0], 1.0)
    assert np.isclose(curve["x"][-1], 0.0)

def test_fixed_by_p_metrics_have_degenerate_exact_bounds():
    for metric_id in ["largest_schmidt_value", "min_entropy", "geometric_linear", "geometric_log"]:
        bounds = metric_bounds_fixed_lmax(metric_id, 0.4, 4, normalized=False)
        assert bounds.degenerate
        assert bounds.lower_extremizer == "fixed_by_p"
        assert bounds.upper_extremizer == "fixed_by_p"
        assert np.isclose(bounds.lower, bounds.upper)


# ===========================================================================
# Source module: test_dataset.py
# ===========================================================================
from pathlib import Path

import numpy as np
import pandas as pd

from entanglement_trajectories.dataset import (
    CANONICAL_COLUMNS,
    LEGACY_COLUMNS,
    SCHEMA_VERSION,
    canonical_to_legacy,
    legacy_to_canonical,
    validate_canonical_frame,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "trajectory_observations.csv"

def test_canonical_dataset_and_legacy_roundtrip():
    canonical = pd.read_csv(DATA).head(50)
    validate_canonical_frame(canonical)
    assert list(canonical.columns) == list(CANONICAL_COLUMNS)
    assert set(canonical["schema_version"]) == {SCHEMA_VERSION}
    legacy = canonical_to_legacy(canonical)
    assert list(legacy.columns) == list(LEGACY_COLUMNS)
    rebuilt = legacy_to_canonical(legacy)
    validate_canonical_frame(rebuilt)
    for column in CANONICAL_COLUMNS:
        a = canonical[column]
        b = rebuilt[column]
        if a.dtype.kind in "if":
            assert np.allclose(a.to_numpy(float), b.to_numpy(float), atol=2e-15, equal_nan=True)
        else:
            assert a.astype(str).equals(b.astype(str))

def test_canonical_labels_are_parameter_descriptive():
    canonical = pd.read_csv(DATA)
    regimes = set(canonical["regime"].astype(str))
    assert "tilted_chaotic" not in regimes
    assert "ergodic_weak_disorder" not in regimes
    assert "localized_strong_disorder" not in regimes
    assert {"tilted_field", "weak_disorder", "strong_disorder"} <= regimes
    assert len(canonical) == 5856


# ===========================================================================
# Source module: test_dynamics.py
# ===========================================================================
import numpy as np

from entanglement_trajectories.dynamics import (
    HADAMARD,
    apply_1q_gate_inplace,
    apply_2q_adjacent_gate_inplace,
    basis_state,
    build_evolver,
    half_chain_spectrum,
    initialize_state,
    random_product_state,
    state_norm,
    xxz_pair_gate,
)
from entanglement_trajectories.models import run_by_id


def _full_one_qubit_operator(gate, q, n):
    factors = []
    for high_to_low in reversed(range(n)):
        factors.append(gate if high_to_low == q else np.eye(2))
    out = factors[0]
    for factor in factors[1:]:
        out = np.kron(out, factor)
    return out


def test_one_qubit_gate_little_endian_matches_explicit_operator():
    rng = np.random.default_rng(3)
    psi = rng.normal(size=8) + 1j * rng.normal(size=8)
    psi /= np.linalg.norm(psi)
    expected = _full_one_qubit_operator(HADAMARD, 1, 3) @ psi
    actual = psi.copy()
    apply_1q_gate_inplace(actual, HADAMARD, 1)
    assert np.allclose(actual, expected, atol=1e-14)


def test_adjacent_two_qubit_gate_matches_direct_two_qubit_action():
    rng = np.random.default_rng(7)
    psi = rng.normal(size=4) + 1j * rng.normal(size=4)
    psi /= np.linalg.norm(psi)
    gate = xxz_pair_gate(0.8, 0.17)
    actual = psi.copy()
    apply_2q_adjacent_gate_inplace(actual, gate, 0)
    assert np.allclose(actual, gate @ psi, atol=1e-14)


def test_half_chain_spectrum_product_and_bell_states():
    product = basis_state(2, 0)
    assert np.allclose(half_chain_spectrum(product, 2), [1.0, 0.0])
    bell = np.zeros(4, dtype=complex)
    bell[0] = bell[3] = 1 / np.sqrt(2)
    assert np.allclose(half_chain_spectrum(bell, 2), [0.5, 0.5], atol=1e-14)


def test_random_product_state_and_evolvers_preserve_norm():
    assert np.isclose(state_norm(random_product_state(6, 42)), 1.0, atol=1e-14)
    for run_id in ("QCA_3", "KI_4", "QB_3", "XXZ_2"):
        run = run_by_id(run_id)
        psi = initialize_state(run, 6)
        evolver = build_evolver(run, 6)
        for _ in range(4):
            evolver.step(psi)
        assert np.isclose(state_norm(psi), 1.0, atol=2e-13)


# ===========================================================================
# Source module: test_followup_regression.py
# ===========================================================================
"""Small fixed regression values independent of the large follow-up archive."""
import numpy as np

from entanglement_trajectories.metrics import (
    geometric_entanglement_linear,
    linear_entropy,
    log_negativity_pure,
    von_neumann_entropy,
)


def test_clifford_flat_spectrum_metrics():
    # A rank-four flat spectrum in d=32 matches the exact QCA-style values.
    lam = np.zeros(32)
    lam[:4] = 0.25
    assert np.isclose(von_neumann_entropy(lam, normalized=True), 2/5)
    assert np.isclose(linear_entropy(lam, normalized=True), (32/31)*(3/4))
    assert np.isclose(log_negativity_pure(lam, normalized=True), 2/5)
    assert np.isclose(geometric_entanglement_linear(lam, normalized=True), (32/31)*(3/4))


# ===========================================================================
# Source module: test_metrics.py
# ===========================================================================
import math

import numpy as np
import pytest

from entanglement_trajectories.metrics import (
    effective_rank,
    entanglement_hamiltonian_gap,
    geometric_entanglement_linear,
    geometric_entanglement_log,
    i_concurrence,
    i_tangle,
    linear_entropy,
    log_negativity_pure,
    metric_value,
    min_entropy,
    negativity_pure,
    purity,
    renyi_entropy,
    schmidt_gap,
    schmidt_ratio,
    von_neumann_entropy,
)


@pytest.mark.parametrize("d", [2, 3, 8, 16])
def test_product_and_uniform_endpoints(d):
    product = np.zeros(d); product[0] = 1.0
    uniform = np.full(d, 1.0/d)
    for spectrum, expected in [(product, 0.0), (uniform, 1.0)]:
        assert np.isclose(von_neumann_entropy(spectrum, normalized=True), expected)
        assert np.isclose(renyi_entropy(spectrum, 0.5, normalized=True), expected)
        assert np.isclose(renyi_entropy(spectrum, 2.0, normalized=True), expected)
        assert np.isclose(min_entropy(spectrum, normalized=True), expected)
        assert np.isclose(linear_entropy(spectrum, normalized=True), expected)
        assert np.isclose(log_negativity_pure(spectrum, normalized=True), expected)
        assert np.isclose(negativity_pure(spectrum, normalized=True), expected)
        assert np.isclose(geometric_entanglement_linear(spectrum, normalized=True), expected)
        assert np.isclose(geometric_entanglement_log(spectrum, normalized=True), expected)
        assert np.isclose(effective_rank(spectrum, 1.0, normalized=True), expected)
        assert np.isclose(effective_rank(spectrum, 2.0, normalized=True), expected)
        assert np.isclose(i_concurrence(spectrum, normalized=True), math.sqrt(expected))
        assert np.isclose(i_tangle(spectrum, normalized=True), expected)
    assert np.isclose(purity(product), 1.0)
    assert np.isclose(purity(uniform), 1.0/d)


def test_exact_equivalence_classes():
    lam = np.array([0.47, 0.26, 0.18, 0.09])
    assert np.isclose(log_negativity_pure(lam), renyi_entropy(lam, 0.5))
    assert np.isclose(min_entropy(lam), renyi_entropy(lam, math.inf))
    assert np.isclose(geometric_entanglement_log(lam), min_entropy(lam))
    assert np.isclose(effective_rank(lam, 2.0), 1.0/purity(lam))
    assert np.isclose(renyi_entropy(lam, 2.0), -math.log2(purity(lam)))
    assert np.isclose(i_tangle(lam, normalized=True), linear_entropy(lam, normalized=True))
    assert np.isclose(i_concurrence(lam, normalized=True)**2, linear_entropy(lam, normalized=True))
    assert np.isclose(negativity_pure(lam, normalized=True), (effective_rank(lam, 0.5)-1)/(len(lam)-1))


def test_order_disagreement_for_incomparable_spectra():
    x = np.array([0.8, 0.1, 0.1, 0.0])
    y = np.array([0.7, 0.3, 0.0, 0.0])
    assert von_neumann_entropy(x) > von_neumann_entropy(y)
    assert renyi_entropy(x, 2.0) < renyi_entropy(y, 2.0)
    assert min_entropy(x) < min_entropy(y)


def test_edge_diagnostics():
    lam = [0.7, 0.2, 0.1]
    assert np.isclose(schmidt_gap(lam), 0.5)
    assert np.isclose(schmidt_ratio(lam), 2/7)
    assert np.isclose(entanglement_hamiltonian_gap(lam, base=math.e), math.log(3.5))
    assert math.isinf(entanglement_hamiltonian_gap([1.0, 0.0]))


def test_metric_dispatch_and_errors():
    lam = [0.6, 0.3, 0.1]
    assert np.isclose(metric_value("vn", lam), von_neumann_entropy(lam))
    assert np.isclose(metric_value("h2", lam), renyi_entropy(lam, 2))
    assert np.isclose(metric_value("logneg", lam), log_negativity_pure(lam))
    with pytest.raises(ValueError):
        metric_value("renyi", lam)
    with pytest.raises(KeyError):
        metric_value("not_a_metric", lam)
    with pytest.raises(ValueError):
        renyi_entropy(lam, -1)


# ===========================================================================
# Source module: test_models.py
# ===========================================================================
from entanglement_trajectories.models import (
    MODEL_ORDER,
    all_runs,
    disorder_seed,
    initial_state_seed,
    run_by_id,
    stable_seed,
)


def test_model_registry_is_complete_and_unique():
    runs = all_runs()
    assert len(runs) == 16
    assert len({run.run_id for run in runs}) == 16
    assert {run.model for run in runs} == set(MODEL_ORDER)
    assert all(sum(run.model == model for run in runs) == 4 for model in MODEL_ORDER)


def test_stable_seeds_are_reproducible_and_scoped():
    assert stable_seed("init", "qca", 10, "QCA_2") == 3237567862
    assert initial_state_seed("qca", 10, "QCA_2") == 3237567862
    assert initial_state_seed("qca", 10, "QCA_1") is None
    assert disorder_seed("random_field_xxz", 10, "XXZ_2") == 3365613502
    assert disorder_seed("qca", 10, "QCA_2") is None


def test_run_lookup_and_labels_are_noninterpretive():
    assert run_by_id("KI_3").regime == "tilted_field"
    assert run_by_id("QB_3").regime == "phase_perturbed"
    assert run_by_id("XXZ_1").regime == "weak_disorder"
    assert run_by_id("XXZ_4").regime == "strong_disorder"


# ===========================================================================
# Source module: test_public_metadata.py
# ===========================================================================
from pathlib import Path
import subprocess
import sys


def test_public_repository_validation() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "analysis" / "validate_public_repository.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr


# ===========================================================================
# Source module: test_registry.py
# ===========================================================================
from pathlib import Path

import pytest

from entanglement_trajectories.registry import load_metric_registry, metric_spec

ROOT = Path(__file__).resolve().parents[1]


def test_registry_is_unique_and_complete():
    registry = load_metric_registry(ROOT / "metadata" / "metric_registry.json")
    rows = registry["metrics"]
    ids = [r["metric_id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert len(rows) == 27
    required = {
        "metric_id", "display_name", "family", "formula_latex", "input_object",
        "equivalence_class", "fixed_p_boundary", "implementation", "scope_notes",
    }
    for row in rows:
        assert required <= set(row)




def test_alias_lookup():
    row = metric_spec("half_vn", ROOT / "metadata" / "metric_registry.json")
    assert row["metric_id"] == "von_neumann_entropy"
    with pytest.raises(KeyError):
        metric_spec("unknown", ROOT / "metadata" / "metric_registry.json")


# ===========================================================================
# Source module: test_rmt.py
# ===========================================================================
from pathlib import Path
import tempfile
import zipfile

import numpy as np
from scipy.integrate import quad

from entanglement_trajectories.rmt import (
    GAP_RATIO_REFERENCE_MEANS,
    haar_reference_targets,
    marchenko_pastur_cdf_balanced,
    marchenko_pastur_pdf_balanced,
    mp_ks_distance_from_spectrum,
)

ROOT = Path(__file__).resolve().parents[1]

def test_balanced_mp_cdf_endpoints_monotonicity_and_integral():
    grid = np.linspace(-1.0, 5.0, 2001)
    cdf = marchenko_pastur_cdf_balanced(grid)
    assert cdf[0] == 0.0
    assert cdf[-1] == 1.0
    assert np.all(np.diff(cdf) >= -1e-14)
    for x in (0.01, 0.1, 0.5, 1.0, 2.5, 3.9):
        numeric = quad(lambda value: marchenko_pastur_pdf_balanced(value), 0.0, x, points=[0.0])[0]
        assert np.isclose(marchenko_pastur_cdf_balanced(x), numeric, atol=2e-11)

def test_balanced_mp_cdf_derivative_matches_density_away_from_edges():
    x = np.linspace(0.05, 3.95, 2000)
    derivative = np.gradient(marchenko_pastur_cdf_balanced(x), x)
    density = marchenko_pastur_pdf_balanced(x)
    assert np.max(np.abs(derivative[2:-2] - density[2:-2])) < 4e-3

def test_haar_reference_target_is_well_formed():
    target = haar_reference_targets(20)
    assert target.d_a == target.d_b == 1024
    assert 0.9 < target.haar_mean_half_vn < 1.0
    assert 0.99 < target.haar_mean_half_linear <= 1.0
    assert np.all((target.four_metric_vector() >= 0) & (target.four_metric_vector() <= 1))

def test_mp_ks_is_finite_for_included_spectra():
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(ROOT / "data" / "spectra_selected_n20.zip") as zf:
            zf.extractall(tmp)
        checked = 0
        for path in sorted(Path(tmp).glob("*.npz")):
            with np.load(path, allow_pickle=False) as data:
                spectra = data["spectra"]
            for spectrum in spectra[::20]:
                value = mp_ks_distance_from_spectrum(spectrum)
                assert np.isfinite(value) and 0.0 <= value <= 1.0
                checked += 1
        assert checked == 25

def test_gap_ratio_reference_values_are_ordered():
    values = GAP_RATIO_REFERENCE_MEANS
    assert values["poisson"] < values["goe_large_n_fit"] < values["gue_large_n_fit"] < values["gse_large_n_fit"]


# ===========================================================================
# Source module: test_robustness.py
# ===========================================================================
from pathlib import Path
import tempfile
import zipfile

import numpy as np
import pandas as pd

from entanglement_trajectories.robustness import (
    BOUNDARY_HEIGHT_COLUMNS,
    HALF_METRICS,
    add_exact_boundary_coordinates,
    cross_metric_classification,
    fit_common_metric_mode,
    majorization_transition_audit,
    metric_direction_events,
    pairwise_metric_robustness,
    trajectory_geometry_preservation,
    x_only_classification,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "trajectory_observations.csv"
_SPECTRA_TEMP = tempfile.TemporaryDirectory(prefix="entanglement_test_spectra_")
SPECTRA = Path(_SPECTRA_TEMP.name)
with zipfile.ZipFile(ROOT / "data" / "spectra_selected_n20.zip") as _zf:
    _zf.extractall(SPECTRA)


def load_frame() -> pd.DataFrame:
    return pd.read_csv(DATA)


def test_exact_boundary_coordinates_are_well_formed():
    frame = add_exact_boundary_coordinates(load_frame())
    for metric in HALF_METRICS:
        values = frame[BOUNDARY_HEIGHT_COLUMNS[metric]].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        assert finite.size > 0
        assert np.min(finite) >= -1e-8
        assert np.max(finite) <= 1.0 + 1e-8
    # Collapsed fixed-lambda_max envelopes are deliberately undefined.
    assert frame[list(BOUNDARY_HEIGHT_COLUMNS.values())].isna().any(axis=None)


def test_common_metric_mode_is_dominant_but_not_exact():
    frame = load_frame()
    raw = fit_common_metric_mode(frame, coordinate="raw")
    boundary = fit_common_metric_mode(frame, coordinate="boundary")
    assert np.isclose(raw.explained_variance_ratio.sum(), 1.0)
    assert np.isclose(boundary.explained_variance_ratio.sum(), 1.0)
    assert raw.explained_variance_ratio[0] > 0.94
    assert 0.85 < boundary.explained_variance_ratio[0] < 0.96
    assert np.all(boundary.components[0] > 0.0)
    assert boundary.components[1, 1] < -0.75


def test_pairwise_robustness_is_hierarchical():
    table = pairwise_metric_robustness(load_frame())
    means = table.groupby(["metric_a", "metric_b"])["boundary_spearman"].mean()
    q1_qhalf = means.loc[("half_vn", "half_logneg")]
    q1_q2 = means.loc[("half_vn", "half_linear")]
    q2_qhalf = means.loc[("half_linear", "half_logneg")]
    assert q1_qhalf > 0.90
    assert q1_q2 > 0.70
    assert q2_qhalf > 0.65
    assert q1_qhalf > q1_q2 > q2_qhalf


def test_y_only_relational_geometry_survives_metric_replacement():
    table = trajectory_geometry_preservation(
        load_frame(),
        coordinate="boundary",
        mode="y",
        k=3,
        permutations=0,
    )
    grouped = table.groupby(["metric_a", "metric_b"]).agg(
        mean_spearman=("distance_spearman", "mean"),
        mean_overlap=("knn_overlap_mean", "mean"),
        random_overlap=("random_knn_overlap", "mean"),
    )
    assert grouped["mean_spearman"].min() > 0.60
    assert np.all(grouped["mean_overlap"] > grouped["random_overlap"])
    assert grouped.loc[("half_vn", "half_logneg"), "mean_spearman"] > 0.93


def test_metric_competition_is_present_and_model_dependent():
    events = metric_direction_events(load_frame())
    assert len(events) == 5760
    fractions = events.groupby("model")["event_class"].apply(
        lambda values: float(np.mean(values == "metric_competition"))
    )
    assert fractions.min() > 0.04
    assert fractions.max() > 0.24
    assert fractions["random_field_xxz"] > fractions["qca"]


def test_all_selected_spectrum_metric_competition_is_majorization_incomparable():
    audit = majorization_transition_audit(
        SPECTRA,
        majorization_tol=1e-10,
        metric_tol=1e-10,
    )
    assert len(audit) == 400
    competition = audit[audit["metric_event"] == "metric_competition"]
    assert len(competition) == 50
    assert set(competition["majorization_relation"]) == {"incomparable"}
    assert int((audit["majorization_relation"] == "incomparable").sum()) == 280


def test_classification_stress_test_separates_centroid_and_individual_claims():
    frame = load_frame()
    centroid, _ = cross_metric_classification(
        frame,
        coordinate="boundary",
        mode="full",
        fold="centroid_leave_size",
    )
    stringent, _ = cross_metric_classification(
        frame,
        coordinate="boundary",
        mode="full",
        fold="individual_double_holdout",
    )
    centroid_diagonal = centroid[centroid.train_metric == centroid.test_metric]["accuracy"].mean()
    stringent_diagonal = stringent[
        stringent.train_metric == stringent.test_metric
    ]["accuracy"].mean()
    assert centroid_diagonal >= 0.875
    assert 0.25 < stringent_diagonal < 0.50
    assert centroid_diagonal > stringent_diagonal + 0.45


def test_lambda_max_baseline_is_recorded_for_fingerprint_claims():
    summary, _ = x_only_classification(
        load_frame(),
        mode="path",
        fold="individual_double_holdout",
    )
    accuracy = float(summary.loc[0, "accuracy"])
    assert 0.35 < accuracy < 0.50


# ===========================================================================
# Source module: test_simulation_regression.py
# ===========================================================================
from pathlib import Path

import numpy as np
import pandas as pd

from entanglement_trajectories.simulation import simulate_frame

ROOT = Path(__file__).resolve().parents[1]

def test_n10_all_model_regression_against_included_canonical_table():
    current = simulate_frame(system_sizes=[10], verbose=False)
    reference = pd.read_csv(ROOT / "data" / "trajectory_observations.csv")
    reference = reference[reference["n"] == 10].copy()
    order = ["n", "model", "run_id", "step"]
    reference = reference.sort_values(order).reset_index(drop=True)
    current = current.sort_values(order).reset_index(drop=True)
    assert len(current) == len(reference) == 656
    for column in ["model", "n", "run_id", "regime", "initial_state", "step"]:
        assert current[column].astype(str).equals(reference[column].astype(str))
    assert np.allclose(current["tau"], reference["tau"], atol=2e-15)
    absolute_tolerances = {
        "one_site_mean_vn": 5e-13,
        "one_site_mean_linear": 5e-13,
        # The one-site geometric coordinate depends on a leading eigenvalue.
        # Different NumPy/LAPACK builds can shift it slightly more than the
        # trace-based entropy and linear coordinates while remaining
        # numerically indistinguishable at the scientific scale.
        "one_site_mean_geometric_linear": 1e-10,
        "half_vn": 5e-13,
        "half_linear": 5e-13,
        "half_geometric_linear": 5e-13,
        # Rényi-1/2 quantities are sensitive to tiny numerical Schmidt tails
        # near product states.
        "one_site_mean_logneg": 7e-9,
        "half_logneg": 7e-9,
    }
    for column, atol in absolute_tolerances.items():
        actual = current[column].to_numpy(dtype=float)
        expected = reference[column].to_numpy(dtype=float)
        max_error = float(np.max(np.abs(actual - expected)))
        assert np.allclose(actual, expected, atol=atol, rtol=0.0), (
            f"{column}: max absolute error {max_error:.3e} exceeds {atol:.1e}"
        )


# ===========================================================================
# Source module: test_spectra.py
# ===========================================================================
import numpy as np
import pytest

from entanglement_trajectories.spectra import (
    SpectrumError,
    concentrated_spectrum,
    equal_tail_spectrum,
    majorization_relation,
    majorizes,
    normalize_spectrum,
    random_capped_spectrum,
)


def test_validation_and_sorting():
    got = normalize_spectrum([0.2, 0.5, 0.3])
    assert np.allclose(got, [0.5, 0.3, 0.2])
    with pytest.raises(SpectrumError):
        normalize_spectrum([0.5, 0.6])
    with pytest.raises(SpectrumError):
        normalize_spectrum([1.1, -0.1])


@pytest.mark.parametrize("d", [2, 3, 4, 8, 16])
def test_extremizers_are_valid_and_have_fixed_p(d):
    for p in np.linspace(1.0 / d, 1.0, 37):
        c = concentrated_spectrum(float(p), d)
        u = equal_tail_spectrum(float(p), d)
        for spectrum in (c, u):
            assert spectrum.shape == (d,)
            assert np.isclose(spectrum.sum(), 1.0)
            assert np.all(spectrum >= -1e-14)
            assert np.all(np.diff(spectrum) <= 1e-13)
            assert np.isclose(spectrum[0], p, atol=2e-12)
        assert majorizes(c, u)


@pytest.mark.parametrize("d,p", [(4, 0.25), (4, 1/3), (4, 0.4), (8, 0.2), (8, 1.0)])
def test_concentrated_pattern(d, p):
    c = concentrated_spectrum(p, d)
    assert np.all(c <= p + 1e-12)
    k = int(round(1/p)) if np.isclose(p, 1/round(1/p)) else int(np.floor(1/p))
    assert np.count_nonzero(c > 1e-14) in {k, k + 1}


def test_random_capped_spectrum_and_extremal_majorization():
    rng = np.random.default_rng(20260819)
    for d in (3, 4, 7, 12):
        for p in np.linspace(1.0 / d + 1e-6, 0.95, 13):
            c = concentrated_spectrum(float(p), d)
            u = equal_tail_spectrum(float(p), d)
            for _ in range(30):
                x = random_capped_spectrum(float(p), d, rng)
                assert np.isclose(x[0], p, atol=2e-11)
                assert majorizes(c, x, atol=2e-10)
                assert majorizes(x, u, atol=2e-10)


def test_majorization_incomparability_example():
    x = [0.8, 0.1, 0.1, 0.0]
    y = [0.7, 0.3, 0.0, 0.0]
    assert majorization_relation(x, y) == "incomparable"



# ===========================================================================
# Source module: test_release_environment.py
# ===========================================================================

def _parse_exact_lock(path):
    import re

    rows = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        assert line.count("==") == 1
        name, version = line.split("==", 1)
        key = re.sub(r"[-_.]+", "-", name.strip()).lower()
        assert key not in rows
        rows[key] = version.strip()
    return rows


def test_release_environment_metadata_and_locks_are_consistent():
    import json
    import re

    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "environment/release-py311.json").read_text())
    assert record["canonical_job"]["python_version"] == (
        root / ".python-version"
    ).read_text().strip()
    build = _parse_exact_lock(root / record["build_requirements_file"])
    runtime = _parse_exact_lock(root / record["runtime_requirements_file"])
    canonical = lambda name: re.sub(r"[-_.]+", "-", name).lower()
    assert build == {canonical(k): str(v) for k, v in record["build_packages"].items()}
    assert runtime == {canonical(k): str(v) for k, v in record["packages"].items()}
    assert len(runtime) >= 15
    assert record["canonical_job"]["workflow_actions"]["checkout_release"] == "v6.0.2"
    assert record["canonical_job"]["workflow_actions"]["setup_python_release"] == "v6.3.0"


def test_release_environment_verifier_structure_mode():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/verify_release_environment.py"),
            "--structure-only",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "RELEASE ENVIRONMENT: PASS" in result.stdout


def test_release_workflow_uses_exact_environment_and_provenance_checks():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/qa.yml").read_text(encoding="utf-8")
    required = [
        "runs-on: ubuntu-24.04",
        "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd",
        "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1",
        "python-version-file: .python-version",
        "requirements/release-build.txt",
        "requirements/release-py311.txt",
        "verify_release_environment.py",
        "git diff --exit-code -- llms-full.txt",
        "diff -qr figures/public/data outputs/public_figures/data",
        "Generated public images are readable and have release dimensions.",
        "permissions:",
        "contents: read",
    ]
    for phrase in required:
        assert phrase in workflow


# ===========================================================================
# Peer-review release regressions
# ===========================================================================

def test_gap_aware_resampling_preserves_internal_undefined_intervals():
    import pandas as pd
    from entanglement_trajectories.robustness import resample_trajectory
    group = pd.DataFrame({
        "tau": [0.0, 0.1, 0.2, 0.3, 0.4],
        "half_lambda_max": [1.0, 0.9, 0.8, 0.7, 0.6],
        "half_vn_boundary_height": [0.0, 0.2, np.nan, 0.6, 0.8],
    })
    grid = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
    _, y = resample_trajectory(group, "half_vn", coordinate="boundary", grid=grid)
    assert np.isnan(y[2])
    assert np.allclose(y[[0,1,3,4]], [0.0,0.2,0.6,0.8])

def test_xxz_release_interpretation_and_convergence_archive():
    import zipfile
    from entanglement_trajectories.models import run_by_id
    run = run_by_id("XXZ_1")
    assert run.parameters["simulation_interpretation"].startswith("fixed one-substep")
    archive = ROOT / "data" / "xxz_convergence_n10_n12_n14.zip"
    with zipfile.ZipFile(archive) as zf:
        assert zf.testzip() is None
        assert len([n for n in zf.namelist() if not n.endswith("/")]) == 6

def test_selected_spectra_have_descending_schema():
    import tempfile, zipfile
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(ROOT / "data" / "spectra_selected_n20.zip") as zf:
            zf.extractall(td)
        for path in Path(td).glob("*.npz"):
            with np.load(path, allow_pickle=False) as data:
                spectra = data["spectra"]
                assert np.all(np.diff(spectra, axis=1) <= 1e-14)
                assert str(data["spectrum_order"][0]) == "descending"

def test_references_and_split_license_exist():
    import json
    assert (ROOT / "REFERENCES.md").is_file()
    assert (ROOT / "LICENSE-CONTENT.md").is_file()
    references = json.loads((ROOT / "metadata" / "references.json").read_text())
    ids = [row["id"] for row in references["references"]]
    assert len(ids) >= 10 and len(ids) == len(set(ids))
