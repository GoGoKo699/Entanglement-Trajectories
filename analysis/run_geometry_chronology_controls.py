#!/usr/bin/env python3
"""Run joint chronology shuffles and explicit fixed-(d,lambda_max) references.

No historical data or figure is overwritten. These are finite designed-study
controls, not a formal invariance theorem, independent physical ensembles,
or a claim of nonlinearity merely from rejecting random chronological order.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import pandas as pd
from entanglement_trajectories.controls import (
    METRICS, SHUFFLES, REFERENCES, make_panels, evaluate, shuffle_panel,
    matched_panel, reference_summary, spectrum_metrics_batch, exact_joint_expectations,
)
from entanglement_trajectories.spectra import concentrated_spectrum, equal_tail_spectrum

BASE_COMMIT = '5434afa1bf545e28d9912f5e2c0a9958bf5c260f'


def clean_json(value):
    if isinstance(value, dict): return {str(k): clean_json(v) for k,v in value.items()}
    if isinstance(value, (tuple,list)): return [clean_json(v) for v in value]
    if isinstance(value, np.ndarray): return clean_json(value.tolist())
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,float)): return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)): return bool(value)
    return value


def save_json(path, value):
    path.write_text(json.dumps(clean_json(value), indent=2, allow_nan=False) + '\n')


def file_hash(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def chronology(panels, count, seed, policy):
    rng = np.random.default_rng(seed)
    observed = evaluate(panels)
    records = []
    invariant_drift = 0.
    for draw in range(count):
        shuffled = [shuffle_panel(p,rng,policy) for p in panels]
        values = evaluate(shuffled)
        values['draw'] = draw
        records.append(values)
        for key in ('heights_level_pc1','raw_level_pc1'):
            invariant_drift = max(invariant_drift, abs(values[key]-observed[key]))
        if values['height_rows'] != observed['height_rows'] or values['height_edges'] != observed['height_edges']:
            raise AssertionError('Joint shuffle changed the finite-support graph.')
    if invariant_drift > 1e-12:
        raise AssertionError('The point-cloud common mode is not invariant under row permutation.')
    return records, {'seed':seed, 'policy':policy, 'statistics':reference_summary(observed,records),
                     'max_level_pc1_drift':invariant_drift}


def selected_spectrum_control(archive, draws, seed):
    """All-pair majorization tables reused for randomized 81-time paths."""
    import io
    rng=np.random.default_rng(seed)
    runs=[]; inputs=[]
    with zipfile.ZipFile(archive) as z:
        for name in sorted(n for n in z.namelist() if n.endswith('.npz')):
            with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as a:
                spectra=np.asarray(a['spectra'],float)
                metrics=spectrum_metrics_batch(spectra)
                c=np.cumsum(spectra,axis=1)[:,:-1]
                # All rows already normalized/ordered in the archive.
                major=np.array([np.all(v[None,:]>=c-1e-10,axis=1) for v in c])
                incomparable=~(major | major.T)
                delta=metrics[None,:,:]-metrics[:,None,:]
                competition=(delta>1e-10).any(axis=2)&(delta< -1e-10).any(axis=2)
                runs.append((incomparable,competition))
                inputs.append({'file':name, 'spectra':len(spectra),
                    'all_distinct_pair_competition':int(np.triu(competition,1).sum()),
                    'all_distinct_pair_competition_outside_incomparable':int(np.triu(competition & ~incomparable,1).sum())})
    def counts(orders):
        result={'transitions':0,'incomparable':0,'competition':0,'competition_outside_incomparable':0}
        for (inc,comp),idx in zip(runs,orders):
            a,b=idx[:-1],idx[1:]
            result['transitions']+=len(a)
            result['incomparable']+=int(inc[a,b].sum())
            result['competition']+=int(comp[a,b].sum())
            result['competition_outside_incomparable']+=int((comp[a,b]&~inc[a,b]).sum())
        return result
    observed=counts([np.arange(len(a)) for a,b in runs])
    records=[]
    for draw in range(draws):
        records.append({'draw':draw,**counts([rng.permutation(len(a)) for a,b in runs])})
    summary={'seed':seed,'observed':observed,'all_pair_tables':inputs,'reference':{}}
    for key in observed:
        x=np.array([r[key] for r in records])
        summary['reference'][key]={'mean':float(x.mean()),'q025':float(np.quantile(x,.025)),'q975':float(np.quantile(x,.975))}
    return records,summary


def run(output: Path, *, permutations=999, reference_draws=199, seed=20260906,
        stable_n10=True):
    if permutations<1 or reference_draws<1: raise ValueError('Draw counts must be positive.')
    output=output.resolve()
    for folder in ('data','figures','metadata','src','tests'):
        protected=(ROOT/folder).resolve()
        if output==protected or protected in output.parents:
            raise ValueError('Output must not overwrite curated repository directories.')
    output.mkdir(parents=True,exist_ok=True)
    if (output/'summary.json').exists():
        raise FileExistsError('Use a new output directory; existing study results are not overwritten.')
    data=ROOT/'data/trajectory_observations.csv'
    protected={str(p.relative_to(ROOT)):file_hash(p)
               for folder in ('data','figures/public') for p in (ROOT/folder).rglob('*') if p.is_file()}
    protocol={
      'schema_version':'entanglement-geometry-chronology-controls-1',
      'base_commit':BASE_COMMIT,'seed':seed,'permutations':permutations,'reference_draws':reference_draws,
      'primary_statistics':['heights_level_pc1 (invariance diagnostic)',
          'heights_roughness (equal-path, within-path standardized)',
          'heights_increment_pc1 (standardized pooled adjacent differences)'],
      'secondary_statistics':['raw_competition_rate','heights_distance_agreement (native grid)',
          'raw-coordinate counterparts','selected-spectrum majorization'],
      'chronology_policies':list(SHUFFLES),'late_time_sensitivity':'tau >= 1; joint permutation',
      'width_floor':1e-10,'width_sensitivity':1e-6,'roughness_scale_floor':1e-10,
      'metric_sign_tolerance':1e-10,
      'mask_policy':'Freeze incomplete boundary-coordinate rows; jointly shuffle complete tuples among their original eligible positions. No interpolation or bridging gaps.',
      'time_blocks':'floor(2*step/n), half-unit tau bins; not a block permutation or stationary bootstrap',
      'references':list(REFERENCES),
      'reference_scope':'Independent tail draws at every recorded time with the original dimension and lambda_max path fixed. No rank, purity, spectrum density, conservation law, or local dynamical constraint is matched.',
      'reference_distributions':'Three gamma-weight water-fill pushforwards and one uniform extremizer-segment mixture. None is Haar or uniform on the feasible polytope.',
      'inference':'Point-cloud PCA cannot test temporal order. Surrogate tails are conditional finite-design diagnostics, not population confidence or proof of chaos. A high value in a static reference is a counterexample to interpreting high PC1 alone as dynamical evidence.',
      'recorded_before_production_run':True,
      'study_status':'Exploratory follow-up; implementation smoke tests preceded this run; not externally preregistered.'}
    save_json(output/'protocol.json',protocol)
    summary={'protocol':protocol,'input_sha256':file_hash(data),
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'platform':platform.platform()},
      'implementation_sha256':{str(p.relative_to(ROOT)):file_hash(p) for p in [Path(__file__), ROOT/'src/entanglement_trajectories/controls.py', ROOT/'src/entanglement_trajectories/boundaries.py', ROOT/'src/entanglement_trajectories/metrics.py', ROOT/'src/entanglement_trajectories/spectra.py']},
      'chronology':{},'matched_spectra':{}}
    frame=pd.read_csv(data)
    panels=make_panels(frame)
    summary['observed']=evaluate(panels)
    exact=pd.DataFrame(exact_joint_expectations(panels))
    exact.to_csv(output/'exact_joint_expectations.csv',index=False,float_format='%.17g')
    summary['analytic_joint_reference']={
        'mean_height_roughness':float(exact.exact_joint_mean_height_roughness.mean()),
        'raw_competition_rate':float(exact.exact_joint_mean_raw_competition.sum()/exact.raw_edges.sum()),
        'by_model':{str(k):{'observed_roughness':float(g.observed_height_roughness.mean()),
             'reference_mean_roughness':float(g.exact_joint_mean_height_roughness.mean()),
             'observed_competition_rate':float(g.observed_raw_competition.sum()/g.raw_edges.sum()),
             'reference_mean_competition_rate':float(g.exact_joint_mean_raw_competition.sum()/g.raw_edges.sum())}
            for k,g in exact.groupby('model')}}
    sensitivity=[]
    for eps in [1e-12,1e-10,1e-8,1e-7]:
        counts=pd.DataFrame(exact_joint_expectations(panels,metric_eps=eps))
        sensitivity.append({'metric_eps':eps,
            'observed_count':int(counts.observed_raw_competition.sum()),
            'reference_expected_count':float(counts.exact_joint_mean_raw_competition.sum()),
            'observed_rate':float(counts.observed_raw_competition.sum()/counts.raw_edges.sum()),
            'reference_expected_rate':float(counts.exact_joint_mean_raw_competition.sum()/counts.raw_edges.sum())})
    summary['competition_tolerance_sensitivity']=sensitivity
    summary['observed_by_model']={str(model):evaluate(make_panels(g)) for model,g in frame.groupby('model')}
    pd.DataFrame([{'model':p.keys[i][0],'run_id':p.keys[i][1],'n':p.n,
        'recorded_rows':len(p.steps),'complete_height_rows':int(p.mask[i].sum()),
        'complete_adjacent_edges':int((p.mask[i,1:]&p.mask[i,:-1]).sum())}
        for p in panels for i in range(len(p.keys))]).to_csv(output/'sample_support.csv',index=False)
    for offset,policy in enumerate(SHUFFLES):
        records,recap=chronology(panels,permutations,seed+100+offset,policy)
        pd.DataFrame(records).to_csv(output/f'chronology_{policy}.csv',index=False,float_format='%.17g')
        summary['chronology'][policy]=recap
        print('Chronology',policy,'complete',flush=True)
    late=[p.tail(1.) for p in panels]
    records,recap=chronology(late,permutations,seed+110,'joint')
    pd.DataFrame(records).to_csv(output/'chronology_late.csv',index=False,float_format='%.17g')
    summary['chronology']['late_joint']=recap
    strict=make_panels(frame,width_floor=1e-6)
    records,recap=chronology(strict,min(permutations,199),seed+111,'joint')
    pd.DataFrame(records).to_csv(output/'chronology_width_1e-6.csv',index=False,float_format='%.17g')
    summary['chronology']['width_1e-6_joint']=recap
    summary['width_sensitivity_observed']=evaluate(strict)

    segment_basis=[]
    for p in panels:
        d=1<<(p.n//2)
        segment_basis.append((np.stack([concentrated_spectrum(float(v),d) for v in p.p.ravel()]),
                              np.stack([equal_tail_spectrum(float(v),d) for v in p.p.ravel()])))
    for index,reference in enumerate(REFERENCES):
        rng=np.random.default_rng(seed+200+index)
        records=[]; late_records=[]; diag={'max_mass_error':0.,'max_lmax_error':0.,'smallest_height':1.,'largest_height':0.}
        start=time.monotonic()
        for draw in range(reference_draws):
            samples=[]
            for p,basis in zip(panels,segment_basis):
                sampled,diagnostics=matched_panel(p,rng,reference,segment_basis=basis)
                samples.append(sampled)
                for key,value in diagnostics.items():
                    diag[key]=min(diag[key],value) if key=='smallest_height' else max(diag[key],value)
            records.append({'draw':draw,**evaluate(samples)})
            late_records.append({'draw':draw,**evaluate([p.tail(1.) for p in samples])})
        pd.DataFrame(records).to_csv(output/f'matched_{reference}.csv',index=False,float_format='%.17g')
        pd.DataFrame(late_records).to_csv(output/f'matched_late_{reference}.csv',index=False,float_format='%.17g')
        summary['matched_spectra'][reference]={'seed':seed+200+index,'diagnostics':diag,
            'statistics':reference_summary(summary['observed'],records),
            'late_statistics':reference_summary(evaluate(late),late_records),
            'spectra_generated':reference_draws*len(frame)}
        print('Matched',reference,'complete',round(time.monotonic()-start,2),'seconds',flush=True)
    records,recap=selected_spectrum_control(ROOT/'data/spectra_selected_n20.zip',permutations,seed+300)
    pd.DataFrame(records).to_csv(output/'selected_spectra_chronology.csv',index=False)
    summary['selected_spectra']=recap
    if stable_n10:
        from entanglement_trajectories.simulation import simulate_frame,write_simulation
        stable=simulate_frame(system_sizes=[10],extraction_method='stable')
        write_simulation(stable,output/'stable_n10.csv')
        stable_panels=make_panels(stable)
        summary['stable_n10']={'observed':evaluate(stable_panels),
                              'archive_n10_observed':evaluate([p for p in panels if p.n==10])}
        records,recap=chronology(stable_panels,min(permutations,199),seed+400,'joint')
        pd.DataFrame(records).to_csv(output/'stable_n10_joint.csv',index=False,float_format='%.17g')
        summary['stable_n10']['joint_control']=recap
    after={str(p.relative_to(ROOT)):file_hash(p)
           for folder in ('data','figures/public') for p in (ROOT/folder).rglob('*') if p.is_file()}
    if after!=protected: raise AssertionError('Historical data or figure bytes changed.')
    summary['preservation']={'file_count':len(protected),'all_unchanged':True,'input_hashes':protected}
    summary['checks_passed']=True
    save_json(output/'summary.json',summary)
    print('GEOMETRY / CHRONOLOGY CONTROLS: COMPLETE',flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'outputs/geometry_chronology')
    parser.add_argument('--permutations',type=int,default=999)
    parser.add_argument('--reference-draws',type=int,default=199)
    parser.add_argument('--seed',type=int,default=20260906)
    parser.add_argument('--skip-stable-n10',action='store_true')
    args=parser.parse_args()
    run(args.output_dir,permutations=args.permutations,reference_draws=args.reference_draws,
        seed=args.seed,stable_n10=not args.skip_stable_n10)
