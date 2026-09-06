"""Freeze audit: input contracts and extreme represented-spectrum diagnostics."""
from dataclasses import replace
import math
import numpy as np
import pytest
from entanglement_trajectories.boundaries import metric_bounds_fixed_lmax
from entanglement_trajectories.dynamics import build_evolver
from entanglement_trajectories.models import xxz_runs
from entanglement_trajectories.metrics import (
    entanglement_hamiltonian_gap, renyi_entropy, hartley_entropy,
    schmidt_rank, numerical_schmidt_rank, effective_rank,
)

@pytest.mark.parametrize("d", [True, np.bool_(True), 2.5, 0, -1])
def test_bound_dimension_rejected_before_coercion(d):
    with pytest.raises(ValueError):
        metric_bounds_fixed_lmax("vn", 1.0, d)

@pytest.mark.parametrize("base", [0.5, 1.0, 0.0, -2.0, float("inf"), float("nan")])
def test_entropy_units_have_positive_logarithm(base):
    for operation in [lambda: renyi_entropy([.6,.4], .5, base=base),
                      lambda: hartley_entropy([.6,.4], base=base),
                      lambda: metric_bounds_fixed_lmax("h0", .6, 4, base=base)]:
        with pytest.raises(ValueError): operation()

@pytest.mark.parametrize("tail", [1e-300, 1e-320, np.nextafter(0.,1.)])
def test_finite_log_gap_does_not_overflow(tail):
    result=entanglement_hamiltonian_gap([1.,tail])
    assert math.isfinite(result)
    assert result==pytest.approx(-math.log(tail),abs=2e-13)
    assert entanglement_hamiltonian_gap([1.,0.])==math.inf

@pytest.mark.parametrize("q", [0., .5, 1., 2., math.inf])
def test_normalized_rank_trivial_space(q):
    assert effective_rank([1.],q,normalized=True)==0.
    assert schmidt_rank([1.],normalized=True)==0.
    assert numerical_schmidt_rank([1.],normalized=True)==0.
    assert effective_rank([1.],q)==1.
    bounds=metric_bounds_fixed_lmax("effective_rank",1.,1,q=q,normalized=True)
    assert bounds.lower==bounds.upper==0.

@pytest.mark.parametrize("bad", [-1,0,1.5,True,float("nan"),float("inf")])
def test_invalid_substeps_rejected(bad):
    r=xxz_runs()[0]
    with pytest.raises(ValueError):
        build_evolver(replace(r,parameters={**r.parameters,"trotter_substeps":bad}),4)

@pytest.mark.parametrize("bad", [0.,-1.,float("nan"),float("inf")])
def test_invalid_record_interval_rejected(bad):
    r=xxz_runs()[0]
    with pytest.raises(ValueError):
        build_evolver(replace(r,parameters={**r.parameters,"dt_record":bad}),4)


def test_rank_alias_is_shared_by_metric_and_boundary_interfaces():
    a=metric_bounds_fixed_lmax("rank",.6,4)
    b=metric_bounds_fixed_lmax("schmidt_rank",.6,4)
    assert a==b
