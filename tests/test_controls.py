"""Structural null invariants and numerical sampler checks, not target-result fitting."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from entanglement_trajectories.controls import (
    Panel, REFERENCES, SHUFFLES, capped_weights, common_fraction,
    distance_agreement, evaluate, matched_panel, reference_summary,
    roughness_per_path, sample_matched_spectra, shuffle_panel, spectrum_metrics_batch,
)
from entanglement_trajectories.metrics import von_neumann_entropy,linear_entropy,log_negativity_pure


def panel():
    rng=np.random.default_rng(914)
    raw=rng.random((4,21,3))
    mask=np.ones((4,21),bool);mask[0,[0,5,6]]=False;mask[2,[9,20]]=False
    heights=np.where(mask[...,None],raw,np.nan)
    return Panel(10,tuple(('model',str(i)) for i in range(4)),np.arange(21),
        np.full((4,21),.5),raw,np.zeros_like(raw),np.ones_like(raw),heights,mask)


@pytest.mark.parametrize('policy',SHUFFLES)
def test_joint_shuffle_preserves_tuples_masks_and_point_cloud(policy):
    p=panel();q=shuffle_panel(p,np.random.default_rng(813),policy)
    assert np.array_equal(p.mask,q.mask)
    for i in range(4):
        assert sorted(map(tuple,p.raw[i]))==sorted(map(tuple,q.raw[i]))
        assert np.array_equal(p.raw[i,~p.mask[i]],q.raw[i,~p.mask[i]])
        if policy=='endpoints':
            endpoints=np.flatnonzero(p.mask[i])[[0,-1]]
            assert np.array_equal(p.raw[i,endpoints],q.raw[i,endpoints])
        if policy=='time_blocks':
            for b in np.unique(2*p.steps//p.n):
                select=(2*p.steps//p.n)==b
                assert sorted(map(tuple,p.raw[i,select]))==sorted(map(tuple,q.raw[i,select]))
    assert common_fraction(q.heights)==pytest.approx(common_fraction(p.heights),abs=2e-14)
    assert common_fraction(q.raw)==pytest.approx(common_fraction(p.raw),abs=2e-14)
    assert not np.array_equal(p.raw,q.raw)


def test_no_gap_bridge_in_roughness():
    x=np.array([[[0.,0.,0.],[1.,2.,3.],[np.nan]*3,[10.,20.,30.]]])
    y=x[np.isfinite(x).all(axis=-1)]
    sd=y.std(axis=0)
    expected=np.mean((np.array([1.,2.,3.])/sd)**2)
    assert roughness_per_path(x)[0]==pytest.approx(expected)


def test_smooth_sequence_is_rougher_when_jointly_shuffled():
    x=np.linspace(0.,1.,30)
    y=np.stack([x,x**2,np.sqrt(x)],axis=-1)[None,:,:]
    observed=roughness_per_path(y)[0]
    randomized=roughness_per_path(y[:,np.random.default_rng(222).permutation(30)])[0]
    assert observed<randomized/10


def test_stationary_paths_not_divided_by_tiny_variance():
    assert np.isnan(roughness_per_path(np.ones((2,5,3)))).all()
    assert np.isnan(common_fraction(np.ones((10,3))))


def test_distance_agreement_matches_direct_pair_computation():
    from scipy.stats import spearmanr
    x=panel().heights
    dist=[]
    for i in range(len(x)):
        for j in range(i+1,len(x)):
            mask=np.isfinite(x[i]).all(axis=1)&np.isfinite(x[j]).all(axis=1)
            dist.append(np.sqrt(((x[i,mask]-x[j,mask])**2).mean(axis=0)))
    dist=np.array(dist)
    expected=np.mean([spearmanr(dist[:,i],dist[:,j]).statistic for i,j in [(0,1),(0,2),(1,2)]])
    assert distance_agreement(x)==pytest.approx(expected,abs=1e-12)


@pytest.mark.parametrize('reference',REFERENCES)
@pytest.mark.parametrize('d',[2,7,32,1024])
def test_matched_spectra_are_feasible_and_reproducible(reference,d):
    p=np.array([1/d,np.nextafter(1/d,1),min(.3+1/d,1),.99,1-1e-14,1.])
    x=sample_matched_spectra(p,d,np.random.default_rng(143),reference)
    y=sample_matched_spectra(p,d,np.random.default_rng(143),reference)
    assert np.array_equal(x,y)
    assert x.shape==(len(p),d)
    assert (x>=0).all()
    np.testing.assert_allclose(x.max(axis=1),p,atol=3e-13,rtol=0)
    np.testing.assert_allclose(x.sum(axis=1),1,atol=3e-13,rtol=0)
    np.testing.assert_allclose(x[0],1/d,atol=3e-13,rtol=0)
    np.testing.assert_allclose(x[-1],np.r_[1,np.zeros(d-1)],atol=3e-13,rtol=0)


@pytest.mark.parametrize('alpha',[.25,1,4])
def test_capped_weight_characterization(alpha):
    rng=np.random.default_rng(28)
    w=rng.gamma(alpha,1,(9,31)); p=np.linspace(.04,.75,9)
    tails=capped_weights(w,p)
    for i in range(len(p)):
        free=tails[i] < p[i]-1e-12
        ratios=tails[i,free]/w[i,free]
        np.testing.assert_allclose(ratios,ratios[0],atol=2e-13,rtol=2e-13)
        np.testing.assert_allclose(tails[i],np.minimum(p[i],ratios[0]*w[i]),atol=2e-13)


@pytest.mark.parametrize('reference',REFERENCES)
def test_batch_metric_matches_package_functions(reference):
    x=sample_matched_spectra(np.array([1/32,.125,.4,.99,1-1e-14,1.]),32,np.random.default_rng(502),reference)
    actual=spectrum_metrics_batch(x)
    expected=np.array([[von_neumann_entropy(v,normalized=True),linear_entropy(v,normalized=True),
                        log_negativity_pure(v,normalized=True)] for v in x])
    np.testing.assert_allclose(actual,expected,atol=3e-13,rtol=0)


@pytest.mark.parametrize('bad',[np.nan,-.1,1.1])
def test_invalid_p_rejected(bad):
    with pytest.raises(ValueError): capped_weights(np.ones((1,3)),np.array([bad]))


def test_conditional_summary_never_reports_zero_tail_fraction():
    out=reference_summary({'heights_roughness':.1},[{'heights_roughness':2.},{'heights_roughness':3.}])
    assert out['heights_roughness']['lower_tail_fraction']==pytest.approx(1/3)
    assert out['heights_roughness']['upper_tail_fraction']==1.


def test_masks_keep_same_number_of_eligible_edges():
    p=panel();q=shuffle_panel(p,np.random.default_rng(521))
    a=evaluate([p]);b=evaluate([q])
    assert a['height_rows']==b['height_rows']
    assert a['height_edges']==b['height_edges']
    assert a['raw_level_pc1']==pytest.approx(b['raw_level_pc1'],abs=2e-14)
    assert a['heights_level_pc1']==pytest.approx(b['heights_level_pc1'],abs=2e-14)


def test_partial_missing_rows_excluded_jointly_in_roughness():
    x=np.array([[[0.,0.,0.],[1.,2.,3.],[500.,np.nan,900.],[10.,20.,30.]]])
    expected=x.copy();expected[0,2]=np.nan
    np.testing.assert_allclose(roughness_per_path(x),roughness_per_path(expected),atol=2e-14)


def test_analytical_joint_expectations_match_complete_permutation_enumeration():
    from itertools import permutations
    from entanglement_trajectories.controls import exact_joint_expectations
    raw=np.array([[[0.,0.,0.],[.1,.3,.5],[.8,.4,.6],[.5,.9,.1],[.3,.6,.9]]])
    mask=np.array([[False,True,True,True,True]])
    p=Panel(2,(('model','test'),),np.arange(5),np.full((1,5),.8),
            raw,np.zeros_like(raw),np.ones_like(raw),np.where(mask[...,None],raw,np.nan),mask)
    exact=exact_joint_expectations([p])[0]
    rough=[];comp=[]
    for perm in permutations(range(1,5)):
        idx=np.r_[0,perm]
        v=p.raw[:,idx];h=p.heights[:,idx]
        rough.append(roughness_per_path(h)[0])
        d=np.diff(v,axis=1)[0]
        comp.append(((d>1e-10).any(axis=1)&(d< -1e-10).any(axis=1)).sum())
    assert np.mean(rough)==pytest.approx(exact['exact_joint_mean_height_roughness'],abs=2e-14)
    assert np.mean(comp)==pytest.approx(exact['exact_joint_mean_raw_competition'],abs=2e-14)


def test_archived_control_results_match_draw_tables_and_sources():
    import hashlib
    import io
    import zipfile
    import pandas as pd
    root=Path(__file__).resolve().parents[1]
    summary_path=root/'metadata/geometry_chronology_controls.json'
    summary=json.loads(summary_path.read_text())
    assert (root/'docs/GEOMETRY_VS_CHRONOLOGY.md').is_file()
    assert summary['input_sha256']==hashlib.sha256((root/'data/trajectory_observations.csv').read_bytes()).hexdigest()
    for name,digest in summary['implementation_sha256'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
    with zipfile.ZipFile(root/'data/geometry_chronology_controls.zip') as z:
        assert z.testzip() is None
        assert json.loads(z.read('summary.json'))==summary
        assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in z.namelist())
        lookup={'joint':'chronology_joint.csv','endpoints':'chronology_endpoints.csv',
                'time_blocks':'chronology_time_blocks.csv','late_joint':'chronology_late.csv',
                'width_1e-6_joint':'chronology_width_1e-6.csv'}
        for key,name in lookup.items():
            stored=summary['chronology'][key]['statistics']
            observed={metric:r['observed'] for metric,r in stored.items()}
            draw=pd.read_csv(io.BytesIO(z.read(name)))
            recalculated=reference_summary(observed,draw.to_dict('records'))
            for metric,fields in stored.items():
                for field,value in fields.items():
                    assert recalculated[metric][field]==pytest.approx(value,abs=2e-12)
        for key,record in summary['matched_spectra'].items():
            draw=pd.read_csv(io.BytesIO(z.read(f'matched_{key}.csv')))
            recalculated=reference_summary(summary['observed'],draw.to_dict('records'))
            for metric,fields in record['statistics'].items():
                for field,value in fields.items():
                    assert recalculated[metric][field]==pytest.approx(value,abs=2e-12)


def test_control_cli_small_reproduction(tmp_path):
    import subprocess
    import sys
    root=Path(__file__).resolve().parents[1]
    out=tmp_path/'control_smoke'
    completed=subprocess.run([sys.executable,str(root/'analysis/run_geometry_chronology_controls.py'),
        '--output-dir',str(out),'--permutations','2','--reference-draws','1','--skip-stable-n10'],
        cwd=root,check=True,capture_output=True,text=True)
    summary=json.loads((out/'summary.json').read_text())
    assert summary['checks_passed'] is True
    assert summary['preservation']['all_unchanged'] is True
    assert set(summary['matched_spectra'])==set(REFERENCES)
    assert summary['chronology']['joint']['max_level_pc1_drift']<1e-12
    assert 'COMPLETE' in completed.stdout
