"""Independent accuracy tests, separate from historical snapshot regression.

The decimal oracle does not call the production spectrum/entropy routines.
Only standard-library Decimal is needed; no new release dependency is added.
"""
from decimal import Decimal, localcontext
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from entanglement_trajectories.boundaries import assess_boundary_height, metric_bounds_fixed_lmax
from entanglement_trajectories.dynamics import (
    half_chain_spectrum, half_chain_schmidt_coefficients,
    single_qubit_spectra, random_product_state,
)
from entanglement_trajectories.metrics import (
    effective_rank, hartley_entropy, log_negativity_pure,
    log_negativity_from_schmidt_coefficients, renyi_entropy, schmidt_rank,
)
from entanglement_trajectories.spectra import (
    concentrated_spectrum, equal_tail_spectrum, schmidt_rank_bounds_fixed_lmax,
)
from entanglement_trajectories.simulation import all_observables


def decimal_bounds(p, d, q, normalized=False):
    """90-digit fixed-p oracle, with the documented canonical 1/k convention."""
    with localcontext() as ctx:
        ctx.prec = 90
        k0 = round(1.0 / p)
        if p == 1.0 / k0:
            p_dec = Decimal(1) / k0
            k, rem = k0, Decimal(0)
        else:
            num, den = p.as_integer_ratio()
            p_dec = Decimal(num) / den
            k = den // num
            rem = Decimal(den - k * num) / den
        concentrated = [(p_dec, k), (rem, 1)]
        uniform_tail = [(p_dec, 1), ((1 - p_dec) / (d - 1), d - 1)]
        divisor = Decimal(d).ln() if normalized else Decimal(2).ln()
        def value(terms):
            terms = [(x, count) for x, count in terms if x > 0 and count > 0]
            if q == 0:
                ent = Decimal(sum(count for _, count in terms)).ln()
            elif q == 1:
                ent = -sum(count * x * x.ln() for x, count in terms)
            elif math.isinf(q):
                ent = -max(x for x, _ in terms).ln()
            else:
                qd = Decimal(str(q))
                ent = sum(count * (qd * x.ln()).exp() for x, count in terms).ln() / (1 - qd)
            return float(ent / divisor)
        return value(concentrated), value(uniform_tail)


def reciprocal_points(d):
    points = {1.0, 1.0 - 1e-14, 0.41 if d >= 3 else 0.71}
    for k in {1, 2, 3, max(1, d // 2), d}:
        if k > d:
            continue
        center = 1.0 / k
        for p in (center, np.nextafter(center, 0.0), np.nextafter(center, 1.0)):
            if 1.0 / d <= p <= 1.0:
                points.add(float(p))
    return sorted(points)


@pytest.mark.parametrize('d', [2, 3, 7, 32, 1024])
def test_extremizers_keep_requested_p_and_every_positive_remainder(d):
    for p in reciprocal_points(d):
        c, u = concentrated_spectrum(p, d), equal_tail_spectrum(p, d)
        for spectrum in (c, u):
            assert spectrum[0] == p
            assert np.max(spectrum) == p
            assert np.all(spectrum >= 0.0)
            assert abs(math.fsum(map(float, spectrum)) - 1.0) <= 3e-16
            assert np.all(np.diff(spectrum) <= 0.0)
        lo, hi = schmidt_rank_bounds_fixed_lmax(p, d)
        assert schmidt_rank(c) == lo
        assert schmidt_rank(u) == hi
        assert hartley_entropy(c) == pytest.approx(math.log2(lo), abs=1e-14, rel=0)
        # atol must not become a valid-input support cutoff.
        assert np.array_equal(c, concentrated_spectrum(p, d, atol=1e-6))


@pytest.mark.parametrize('q', [0.0, 1e-6, 0.01, 0.1, 0.25, 0.5,
                              1.0 - 1e-11, 1.0, 1.0 + 1e-11, 2.0, 8.0, 1000.0, math.inf])
@pytest.mark.parametrize('d', [2, 7, 32, 1024])
def test_boundary_values_against_independent_decimal_oracle(d, q):
    for p in reciprocal_points(d):
        expected_lo, expected_hi = decimal_bounds(p, d, q)
        b = metric_bounds_fixed_lmax('renyi_entropy', p, d, q=q)
        np.testing.assert_allclose([b.lower, b.upper], [expected_lo, expected_hi], rtol=8e-13, atol=2e-15)
        if p < 1 and q > 0:
            assert b.lower > 0
        bn = metric_bounds_fixed_lmax('renyi_entropy', p, d, q=q, normalized=True)
        np.testing.assert_allclose([bn.lower, bn.upper], np.array([expected_lo, expected_hi]) / math.log2(d),
                                   rtol=8e-13, atol=2e-15)


def test_near_product_hartley_and_small_positive_renyi_are_consistent():
    p, d = 1.0 - 1e-14, 1024
    c = concentrated_spectrum(p, d)
    assert c[0] == p and c[1] == 1.0 - p
    assert hartley_entropy(c) == 1.0
    b = metric_bounds_fixed_lmax('hartley_entropy', p, d)
    assert (b.lower, b.upper) == (1.0, 10.0)
    assert renyi_entropy(c, 0.1) == pytest.approx(0.06257390380002315, rel=5e-14)
    assert renyi_entropy(c, 0.25) == pytest.approx(0.0006080759334404261, rel=5e-13)


def test_effective_rank_large_order_does_not_underflow():
    for q in [1000.0, 1e6, 1e308]:
        assert effective_rank([0.5, 0.5], q) == pytest.approx(2.0, rel=5e-14)
        assert 1.0 <= effective_rank([0.8, 0.15, 0.05], q) <= 1.26


@pytest.mark.parametrize('epsilon', [0.0, 1e-12, 1e-8, 1e-5, 0.24, 0.26])
def test_one_qubit_known_schmidt_pair_near_equal_eigenvalues(epsilon):
    expected = np.array([0.5 + epsilon, 0.5 - epsilon])
    psi = np.array([math.sqrt(expected[0]), 0, 0, 1j * math.sqrt(expected[1])])
    np.testing.assert_allclose(single_qubit_spectra(psi, 2), np.tile(expected, (2, 1)), rtol=0, atol=5e-16)


@pytest.mark.parametrize('n', [2, 6, 10, 14])
def test_product_state_lognegativity_is_roundoff_level_not_sqrt_roundoff(n):
    for seed in [17, 20260906]:
        psi = random_product_state(n, seed)
        m = all_observables(psi, n)
        assert abs(m['half_logneg']) < 3e-13
        assert abs(m['one_site_mean_logneg']) < 3e-13
        assert abs(m['half_vn']) < 3e-13
        assert abs(m['half_linear']) < 3e-13


@pytest.mark.parametrize('n,rank', [(6, 1), (6, 3), (7, 4), (10, 32)])
def test_svd_recovers_known_spectrum_after_local_basis_rotations(n, rank):
    rng = np.random.default_rng(140+n+rank)
    da, db = 1 << (n // 2), 1 << (n - n // 2)
    ua, _ = np.linalg.qr(rng.normal(size=(da,da)) + 1j*rng.normal(size=(da,da)))
    ub, _ = np.linalg.qr(rng.normal(size=(db,db)) + 1j*rng.normal(size=(db,db)))
    probabilities = np.sort(rng.dirichlet(np.ones(rank)))[::-1]
    diag = np.zeros((da,db), dtype=complex)
    diag[np.arange(rank), np.arange(rank)] = np.sqrt(probabilities)
    psi = (ua @ diag @ ub.T).T.ravel()
    expected = np.pad(probabilities, (0, da-rank))
    np.testing.assert_allclose(half_chain_spectrum(3.7*psi, n), expected, rtol=0, atol=3e-15)
    s = half_chain_schmidt_coefficients(psi, n)
    assert log_negativity_from_schmidt_coefficients(s) == pytest.approx(
        2*math.log2(np.sum(np.sqrt(probabilities))), rel=0, abs=1e-13)


def test_unsquared_coefficients_prevent_underflow_in_lognegativity():
    s = np.array([1.0, 1e-200])
    assert (s*s)[1] == 0.0  # a double cannot store the squared tail
    got = log_negativity_from_schmidt_coefficients(s)
    assert got > 0.0
    assert got == pytest.approx(2e-200 / math.log(2), rel=5e-15, abs=0)


def test_stable_svd_matches_gram_on_well_conditioned_full_rank_state():
    rng = np.random.default_rng(75)
    psi = rng.normal(size=1024) + 1j*rng.normal(size=1024)
    psi /= np.linalg.norm(psi)
    np.testing.assert_allclose(half_chain_spectrum(psi, 10),
                               half_chain_spectrum(psi, 10, extraction_method='release-v1'), rtol=0, atol=3e-15)
    assert not np.shares_memory(psi, half_chain_spectrum(psi, 10))


@pytest.mark.parametrize('psi,n', [(np.zeros(4),2), (np.ones(3),2), (np.array([np.nan,0,0,0]),2)])
def test_stable_extraction_rejects_invalid_states(psi,n):
    with pytest.raises(ValueError): half_chain_spectrum(psi,n)
    with pytest.raises(ValueError): single_qubit_spectra(psi,n)


def test_uncertainty_screen_rejects_near_collapsed_but_accepts_interior_height():
    metric = 'log_negativity_pure'
    d, p = 32, 0.9999999999999996
    b = metric_bounds_fixed_lmax(metric, p, d, normalized=True)
    v = 0.5 * (b.lower + b.upper)
    a = assess_boundary_height(metric, p, v, d, p_error=5e-13, value_error=2e-8, normalized_metric=True)
    assert np.isfinite(a.height)
    assert not a.reliable and np.isnan(a.usable_height)
    assert a.status == 'uncertainty_overlaps_collapsed_envelope'
    p=0.41
    b=metric_bounds_fixed_lmax(metric,p,d,normalized=True)
    a=assess_boundary_height(metric,p,0.5*(b.lower+b.upper),d,p_error=5e-13,value_error=2e-8,normalized_metric=True)
    assert a.reliable
    assert abs(a.height-0.5)<1e-14
    assert a.interval_lower < a.height < a.interval_upper


@pytest.mark.parametrize('metric', ['vn', 'linear', 'logneg'])
def test_propagated_intervals_cover_perturbed_point_evaluations(metric):
    rng=np.random.default_rng(109)
    for p in [0.13,0.251,0.41,0.73,0.97]:
        b=metric_bounds_fixed_lmax(metric,p,16,normalized=True)
        v=0.4*b.lower+0.6*b.upper
        pe,ve=1e-5,2e-6
        a=assess_boundary_height(metric,p,v,16,p_error=pe,value_error=ve,normalized_metric=True)
        for _ in range(10):
            pi=p+rng.uniform(-pe,pe); vi=v+rng.uniform(-ve,ve)
            bi=metric_bounds_fixed_lmax(metric,pi,16,normalized=True)
            height=(vi-bi.lower)/(bi.upper-bi.lower)
            assert a.interval_lower <= height <= a.interval_upper


def test_extraction_mode_metadata_and_safe_cli_default(tmp_path):
    root=Path(__file__).resolve().parents[1]
    from entanglement_trajectories.simulation import simulate_frame
    frame=simulate_frame(system_sizes=[4],run_ids=['QCA_3'],max_steps=1)
    assert frame.attrs['extraction_method']=='stable'
    with pytest.raises(ValueError): simulate_frame(system_sizes=[4],run_ids=['QCA_3'],extraction_method='unknown')
    import json
    out=tmp_path/'trajectory.csv'
    subprocess.run([sys.executable,str(root/'scripts/run_trajectory_experiment.py'),
                    '--sizes','4','--run-ids','QCA_3','--max-steps','1','--out',str(out)],check=True,capture_output=True)
    record=json.loads(out.with_suffix('.csv.metadata.json').read_text())
    assert record['extraction_method']=='stable'
    assert record['rows']==2
    assert 'outputs/current/trajectory_observations.csv' in (root/'scripts/run_trajectory_experiment.py').read_text()


def test_linear_entropy_retains_sub_ulp_tail_mass():
    from entanglement_trajectories.metrics import linear_entropy, i_tangle
    # The leading float rounds to one. Cross-weights still retain the tail;
    # subtracting purity from one would instead return zero.
    lam = [1.0, 1e-18, 0.0, 0.0]
    assert linear_entropy(lam) == pytest.approx(2e-18, rel=1e-14, abs=0.0)
    assert i_tangle(lam) == pytest.approx(4e-18, rel=1e-14, abs=0.0)


def test_figure02_grid_preserves_exact_binary_reciprocal_knots(tmp_path):
    import pandas as pd
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,str(root/'scripts/build_public_figures.py'),
                           '--figures','02','--output-dir',str(tmp_path)],cwd=root,
                          capture_output=True,text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    table=pd.read_csv(tmp_path/'data/figure_02_exact_metric_arenas_boundaries.csv')
    table=table[table.metric_id=='log_negativity_pure'].reset_index(drop=True)
    for power in range(11):
        row=table.iloc[140*power]
        assert row.lambda_max == 2.0**(-power)
        assert row.lower == pytest.approx(power/10,rel=0,abs=3e-15)
