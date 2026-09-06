#!/usr/bin/env python3
"""Independent fixed-p and spectrum-extraction verification.

Runs on the included data without editing it. The full mode regenerates all
16 n=10 trajectories twice: stable extraction and preserved release-v1
extraction. Decimal oracles use 70 digits and no production entropy kernels.
This is an implementation check, not external peer review or a new null study.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import pandas as pd
from entanglement_trajectories.boundaries import metric_bounds_fixed_lmax, assess_boundary_height
from entanglement_trajectories.dynamics import random_product_state, single_qubit_spectra
from entanglement_trajectories.metrics import hartley_entropy, renyi_entropy
from entanglement_trajectories.robustness import add_exact_boundary_coordinates, BOUNDARY_HEIGHT_COLUMNS
from entanglement_trajectories.simulation import all_observables, simulate_frame, write_simulation
from entanglement_trajectories.spectra import concentrated_spectrum

METRICS = [('vn','half_vn'),('linear','half_linear'),('logneg','half_logneg')]


def decimal_three_bounds(p: float, d: int):
    with localcontext() as ctx:
        ctx.prec = 70
        nearest = round(1.0 / p)
        if p == 1.0 / nearest:
            v = Decimal(1) / nearest; k = nearest; r = Decimal(0)
        else:
            numerator, denominator = p.as_integer_ratio()
            v=Decimal(numerator)/denominator; k=denominator//numerator
            r=Decimal(denominator-k*numerator)/denominator
        u=(1-v)/(d-1)
        def xlogx(x): return x*x.ln() if x else Decimal(0)
        vnlo=-(k*xlogx(v)+xlogx(r))/Decimal(d).ln()
        vnhi=-(xlogx(v)+(d-1)*xlogx(u))/Decimal(d).ln()
        factor=Decimal(d)/Decimal(d-1)
        linlo=(1-k*v*v-r*r)*factor
        linhi=(1-v*v-(d-1)*u*u)*factor
        lnlo=2*(k*v.sqrt()+r.sqrt()).ln()/Decimal(d).ln()
        lnhi=2*(v.sqrt()+(d-1)*u.sqrt()).ln()/Decimal(d).ln()
        return np.array([[float(vnlo),float(vnhi)], [float(linlo),float(linhi)], [float(lnlo),float(lnhi)]])


def pc1(matrix):
    values=np.asarray(matrix,float)
    finite=np.all(np.isfinite(values),axis=1)
    values=values[finite]
    z=(values-values.mean(axis=0))/values.std(axis=0)
    singular=np.linalg.svd(z,compute_uv=False)
    return {'pc1_fraction':float(singular[0]**2 / np.sum(singular**2)), 'complete_rows':int(finite.sum())}


def serializable(obj):
    if isinstance(obj,dict): return {k:serializable(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)): return [serializable(v) for v in obj]
    if isinstance(obj,(np.floating,float)):
        return float(obj) if math.isfinite(obj) else None
    if isinstance(obj,np.integer): return int(obj)
    if isinstance(obj,np.bool_): return bool(obj)
    return obj


def compare_frames(current, reference):
    order=['n','model','run_id','step']
    a=current.sort_values(order).reset_index(drop=True)
    b=reference.sort_values(order).reset_index(drop=True)
    if len(a)!=len(b): raise AssertionError('row counts differ')
    for col in ['model','n','run_id','regime','initial_state','step','initial_state_seed','disorder_seed']:
        if not a[col].astype(str).equals(b[col].astype(str)): raise AssertionError(f'metadata mismatch: {col}')
    records=[]
    for col in [c for c in a if c.startswith(('half_','one_site_'))]:
        delta=np.abs(a[col].to_numpy(float)-b[col].to_numpy(float)); i=int(delta.argmax())
        records.append({'metric':col,'max_absolute_difference':float(delta[i]),
                        'mean_absolute_difference':float(delta.mean()),
                        'rms_difference':float(np.sqrt(np.mean(delta**2))),
                        'worst_run':str(a.loc[i,'run_id']),'worst_step':int(a.loc[i,'step'])})
    return records


def run(out: Path, skip_n10=False):
    out.mkdir(parents=True,exist_ok=True)
    original_files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                    for directory in ('data','figures/public') for p in (ROOT/directory).rglob('*') if p.is_file()}
    summary={'schema_version':'entanglement-trajectories-numerical-foundations-1',
             'date':'2026-09-06','base_commit':'c58576bc188d603d4f6e03f4225954d3599a2d05',
             'implementation':'numerical-foundations-2026-09-06',
             'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
                            'platform':platform.platform()},
             'scope':'numerical foundations only; no chronology or matched-spectrum null tests'}
    p,d=1-1e-14,1024
    c=concentrated_spectrum(p,d)
    assert c[0]==p and c[1]==1-p and hartley_entropy(c)==1
    summary['near_product_extremizer']={'p':p,'dimension':d,'first_two':c[:2].tolist(),
        'hartley_lower':hartley_entropy(c),
        'renyi_lower_bits':{str(q):renyi_entropy(c,q) for q in [0.01,0.1,0.25,0.5]}}
    probs=np.array([0.5+1e-8,0.5-1e-8]); psi=np.array([np.sqrt(probs[0]),0.,0.,np.sqrt(probs[1])],complex)
    summary['one_qubit_equal_weight_test']={
        'target_largest':float(probs[0]),
        'stable_largest':float(single_qubit_spectra(psi,2)[0,0]),
        'release_v1_largest':float(single_qubit_spectra(psi,2,extraction_method='release-v1')[0,0])}
    product=random_product_state(14,20260906)
    stable=all_observables(product,14)
    release=all_observables(product,14,extraction_method='release-v1')
    assert abs(stable['half_logneg'])<3e-13
    summary['product_n14']={'stable':stable,'release_v1':release}

    df=pd.read_csv(ROOT/'data/trajectory_observations.csv')
    corrected=add_exact_boundary_coordinates(df)
    height_cols=[BOUNDARY_HEIGHT_COLUMNS[c] for _,c in METRICS]
    actual=corrected[height_cols].to_numpy(float)
    oracle=np.full_like(actual,np.nan)
    screened=np.full_like(actual,np.nan)
    bounds_errors=np.zeros(3)
    assessment_rows=[]
    budgets={'p_error':5e-13,'value_error':{'half_vn':5e-13,'half_linear':5e-13,'half_logneg':2e-7},
             'boundary_error':1e-13,'max_height_error':0.01,
             'status':'illustrative conservative screening allowances, NOT certified error bounds or confidence intervals'}
    for i,row in df.iterrows():
        d=1<<(int(row.n)//2); p=min(1.0,max(1.0/d,float(row.half_lambda_max)))
        refs=decimal_three_bounds(p,d)
        for j,(metric,column) in enumerate(METRICS):
            v=float(row[column]); lo,hi=refs[j]; width=hi-lo
            if width>1e-10: oracle[i,j]=(v-lo)/width
            b=metric_bounds_fixed_lmax(metric,p,d,normalized=True)
            bounds_errors[j]=max(bounds_errors[j],abs(b.lower-lo),abs(b.upper-hi))
            assessment=assess_boundary_height(metric,p,v,d,normalized_metric=True,
                    p_error=budgets['p_error'],value_error=budgets['value_error'][column],
                    boundary_error=budgets['boundary_error'],max_height_error=budgets['max_height_error'])
            screened[i,j]=assessment.usable_height
            assessment_rows.append({'row':i,'n':int(row.n),'run_id':row.run_id,'step':int(row.step),
                                    'metric':column,**asdict(assessment)})
    errors=np.abs(actual-oracle)
    finite_mask_equal=bool(np.array_equal(np.isfinite(actual),np.isfinite(oracle)))
    assert finite_mask_equal
    assert float(bounds_errors.max())<3e-13
    corrected_fit=pc1(actual); oracle_fit=pc1(oracle)
    with zipfile.ZipFile(ROOT/'data/public_analysis_inputs.zip') as z:
        snap=json.loads(z.read('metric_robustness_scientific_summary.json'))
    frozen=float(snap['common_mode']['boundary_pc1_explained'])
    assert abs(corrected_fit['pc1_fraction']-oracle_fit['pc1_fraction'])<2e-9
    assert abs(corrected_fit['pc1_fraction']-frozen)<1e-7
    records=pd.DataFrame(assessment_rows)
    records.to_csv(out/'boundary_height_assessments.csv',index=False,float_format='%.17g')
    summary['all_5856_boundary_check']={
        'rows':len(df),'decimal_digits':70,'frozen_pc1_fraction':frozen,
        'corrected_float':corrected_fit,'independent_decimal':oracle_fit,
        'float_vs_decimal_pc1_difference':abs(corrected_fit['pc1_fraction']-oracle_fit['pc1_fraction']),
        'float_vs_frozen_pc1_difference':abs(corrected_fit['pc1_fraction']-frozen),
        'max_absolute_bound_errors':dict(zip([c for _,c in METRICS],bounds_errors.tolist())),
        'max_absolute_height_errors':dict(zip([c for _,c in METRICS],np.nanmax(errors,axis=0).tolist())),
        'finite_masks_match':finite_mask_equal,
        'screening_allowances':budgets,
        'screening_counts':records.groupby(['metric','status']).size().rename('rows').reset_index().to_dict('records'),
        'screened_point_cloud':pc1(screened),
        'screening_note':'Not substituted for archived inference; this is an additional conditioning sensitivity check.'}
    if not skip_n10:
        fresh=simulate_frame(system_sizes=[10],extraction_method='stable')
        old=simulate_frame(system_sizes=[10],extraction_method='release-v1')
        write_simulation(fresh,out/'stable_n10.csv'); write_simulation(old,out/'release_v1_n10.csv')
        fresh_vs_old=compare_frames(fresh,old)
        fresh_vs_archive=compare_frames(fresh,df[df.n==10])
        for r in fresh_vs_old:
            # Containment only. The much tighter analytical tests define
            # numerical accuracy; the old noisy tails do not define truth.
            cap=1e-6 if ('logneg' in r['metric'] or r['metric']=='one_site_mean_geometric_linear') else 3e-12
            assert r['max_absolute_difference']<cap, r
        pd.DataFrame(fresh_vs_old).to_csv(out/'n10_extraction_comparison.csv',index=False)
        summary['n10_regeneration']={'rows':len(fresh),'trajectories':16,
            'stable_vs_release_v1':fresh_vs_old,'stable_vs_archived_data':fresh_vs_archive,
            'comparison_role':'drift containment; analytical tests, not historical tails, define accuracy'}
    else:
        summary['n10_regeneration']={'performed':False}
    final_files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                 for directory in ('data','figures/public') for p in (ROOT/directory).rglob('*') if p.is_file()}
    assert final_files==original_files
    summary['preserved_data_and_figure_files']={'count':len(original_files),'all_hashes_unchanged':True}
    summary['checks_passed']=True
    (out/'summary.json').write_text(json.dumps(serializable(summary),indent=2,allow_nan=False)+'\n')
    print('NUMERICAL FOUNDATIONS: PASS')
    print(json.dumps(serializable(summary['all_5856_boundary_check']),indent=2))
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/numerical_foundations')
    parser.add_argument('--skip-n10',action='store_true')
    args=parser.parse_args()
    run(args.output_dir,args.skip_n10)
