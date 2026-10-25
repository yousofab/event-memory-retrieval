"""Exploratory19B: edit-count-matched controls and an exact access null.

Registered after19A results. Never relabel this as an a-priori primary analysis.
"""
import argparse
from collections import Counter,defaultdict
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import time
from run_baselines import ROOT
from run_phase17_fixed_anchors import TurnIndex,anchor_cells,allocate,select_windows,score_windows,fingerprint
from run_phase18_feasibility import requirements,minimum_budget,feasible,witness_windows,classify,numeric_write
from run_phase19_session_access import select_anchors,writer_maps,mean_by_history,paired
from phase19_data import load_jobs


def matched_edit_anchors(pool,policy,identity,count=8):
    base=[p['turn_index'] for p in pool[:count]]
    target=select_anchors(pool,'reserve8',identity,count)
    d=len(set(target)-set(base))
    seed=int(policy.split('_')[1])
    material=f'phase19-edit|{seed}|{identity}'.encode()
    rng=random.Random(int.from_bytes(hashlib.sha256(material).digest(),'big'))
    selected=[base[0]]+rng.sample(base[1:],count-1-d)+rng.sample([p['turn_index'] for p in pool[count:]],d)
    order={p['turn_index']:i for i,p in enumerate(pool)}
    selected.sort(key=order.get)
    assert len(set(selected)-set(base))==d and base[0] in selected
    return selected


def access_null(pool,gold_sessions,d,count=8):
    """Exact rational expectation; label-aware evaluator, never a selector."""
    if not 0<=d<count or len(pool)<count or not gold_sessions:
        raise ValueError('Invalid null geometry')
    mandatory=pool[0]['session']
    base=[p['session'] for p in pool[1:count]]
    outside=[p['session'] for p in pool[count:]]
    keep=count-1-d
    def choose(n,k):return math.comb(n,k) if 0<=k<=n else 0
    den1=choose(len(base),keep);den2=choose(len(outside),d)
    if not den1 or not den2:raise ValueError('Infeasible edit count')
    def avoid(forbidden):
        if mandatory in forbidden:return Fraction(0)
        return Fraction(choose(sum(s not in forbidden for s in base),keep),den1)*Fraction(choose(sum(s not in forbidden for s in outside),d),den2)
    gs=sorted(gold_sessions)
    if len(gs)>count:
        complete=Fraction(0)
    else:
        complete=sum(((-1)**r)*avoid(set(subset)) for r in range(len(gs)+1)
                     for subset in itertools.combinations(gs,r))
    recall=sum(Fraction(1)-avoid({s}) for s in gs)/len(gs)
    assert 0<=complete<=1 and 0<=recall<=1
    return {'all_sessions_probability':float(complete),'mean_session_recall':float(recall),
        'all_sessions_fraction':[complete.numerator,complete.denominator],
        'mean_session_recall_fraction':[recall.numerator,recall.denominator]}


def summarize_b(rows,queries,base_rows,plan):
    lookup={(r['dataset'],r['sample_id'],r['question_id'],r['policy'],r['selector'],r['budget_words']):r for r in base_rows}
    out={}
    for dataset in ['locomo','evermem']:
        metric='all_evidence' if dataset=='locomo' else 'turn_recall'
        rs=[r for r in rows if r['dataset']==dataset and r['budget_words']==1024 and r['selector']=='writer']
        by_query=defaultdict(list)
        for r in rs:by_query[(r['sample_id'],r['question_id'])].append(r)
        per_history=defaultdict(list)
        null_diffs=defaultdict(list)
        observed_diffs=defaultdict(list)
        qlookup={(q['sample_id'],q['question_id']):q for q in queries if q['dataset']==dataset}
        for (sid,qid),controls in sorted(by_query.items()):
            target=lookup[(dataset,sid,qid,'reserve8','writer',1024)]
            per_history[sid].append(target[metric]-statistics.mean(c[metric] for c in controls))
            null_diffs[sid].append(target['all_gold_sessions']-qlookup[(sid,qid)]['edit_null']['all_sessions_probability'])
            observed_diffs[sid].append(target['all_gold_sessions']-statistics.mean(c['all_gold_sessions'] for c in controls))
        control_mean=statistics.mean(mean_by_history(rs,lambda r:r[metric]).values())
        estimates=[]
        for budget in plan['budget_words']:
            for selector in plan['selectors']:
                selected=[r for r in rows if r['dataset']==dataset and r['budget_words']==budget and r['selector']==selector]
                estimates.append({'budget_words':budget,'selector':selector,
                    'macro_primary_metric_control_mean':statistics.mean(mean_by_history(selected,lambda r:r[metric]).values()),
                    'macro_all_session_control_mean':statistics.mean(mean_by_history(selected,lambda r:r['all_gold_sessions']).values()),
                    'mean_words':statistics.mean(r['retrieved_words'] for r in selected)})
        out[dataset]={'outcome':metric,'questions':len(by_query),'control_seeds':len(plan['policies']),
            'primary_budget_mean_control_metric':control_mean,'estimates':estimates,
            'reserve8_minus_edit_control_mean':paired({k:statistics.mean(v) for k,v in per_history.items()}),
            'reserve8_session_access_minus_exact_edit_null':paired({k:statistics.mean(v) for k,v in null_diffs.items()}),
            'reserve8_session_access_minus_monte_carlo_controls':paired({k:statistics.mean(v) for k,v in observed_diffs.items()}),
            'edit_histogram':dict(sorted(Counter(q['edits'] for q in qlookup.values()).items())),
            'exact_expected_all_session_count':sum(q['edit_null']['all_sessions_probability'] for q in qlookup.values())}
    return out


def run(output_dir,base_dir):
    start=time.perf_counter();output_dir.mkdir(parents=True,exist_ok=True)
    if any(output_dir.glob('phase19b_*')):raise FileExistsError('Use a fresh directory')
    clean=not bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip())
    plan_path=ROOT/'configs/phase19b_plan.json';plan=json.loads(plan_path.read_text())
    mainplan=json.loads((ROOT/'configs/phase19_plan.json').read_text())
    frozen={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in base_dir.glob('phase19_*') if p.is_file()}
    original=json.loads(gzip.decompress((base_dir/'phase19_queries.json.gz').read_bytes()))
    old={(q['dataset'],q['sample_id'],q['question_id']):q for q in original['queries']}
    base_rows=json.loads(gzip.decompress((base_dir/'phase19_rows.json.gz').read_bytes()))
    base_lookup={(r['dataset'],r['sample_id'],r['question_id'],r['policy'],r['selector'],r['budget_words']):r for r in base_rows}
    settings=json.loads((ROOT/'configs/phase8_causal_plan.json').read_text())['causal_writer']
    jobs,_=load_jobs(mainplan)
    rows,records=[],[];thresholds=witnesses=0;unequal=Counter()
    for dataset,sample,queries in jobs:
        index=TurnIndex(sample);maps,_=writer_maps(sample,settings)
        for qi,query,gold_ids in queries:
            if time.perf_counter()-start>1800:raise RuntimeError('Registered CPU soft stop')
            a=old[(dataset,sample['sample_id'],qi)]
            order=index.rank(query)
            assert fingerprint(order)==a['ranking_fingerprint']
            assert [p['turn_index'] for p in a['pool']]==order[:64]
            pool=a['pool'];identity=f'{sample["sample_id"]}|{qi}'
            choices={}
            for policy in plan['policies']:
                anchors=matched_edit_anchors(pool,policy,identity)
                cells=anchor_cells(index,anchors)
                returned={b:{s:select_windows(cells,allocate(cells,b),maps if s=='writer' else None)
                             for s in plan['selectors']} for b in plan['budget_words']}
                choices[policy]=(anchors,cells,returned)
            # All practical choices above are label-blind; the rest is evaluation.
            gold=a['gold_spans'];gs={g['session'] for g in gold if g['end']>g['start']}
            d=len(set(a['policies']['reserve8']['anchor_indices'])-set(a['policies']['bm25']['anchor_indices']))
            rec={k:a[k] for k in ['dataset','sample_id','question_id','gold_spans','pool','ranking_fingerprint','pool_all_gold_sessions']}
            rec.update(edits=d,edit_null=access_null(pool,gs,d),policies={})
            for policy,(anchors,cells,returned) in choices.items():
                required,missing=requirements(cells,gold)
                threshold=None if missing else minimum_budget(required)
                if threshold is not None:
                    assert feasible(required,allocate(cells,threshold))
                    assert not feasible(required,allocate(cells,threshold-1));thresholds+=1
                rec['policies'][policy]={'anchor_indices':anchors,'cells':required,
                    'missing_gold_sessions':missing,'minimum_total_budget':threshold}
                for b,methods in returned.items():
                    widths=allocate(cells,b);can=int(feasible(required,widths,missing))
                    if can:
                        w=witness_windows(required,widths)
                        assert score_windows(index,gold_ids,w)['all_evidence']==1;witnesses+=1
                    for selector,windows in methods.items():
                        scores=score_windows(index,gold_ids,windows)
                        cost=sum(e-s for sid,s,e in windows)
                        assert scores['all_evidence']<=can<=scores['all_gold_sessions']<=rec['pool_all_gold_sessions']
                        row={'dataset':dataset,'sample_id':sample['sample_id'],'question_id':qi,
                            'policy':policy,'selector':selector,'budget_words':b,'windows':windows,
                            'widths':widths,'retrieved_words':cost,'selected_sessions':len({s for s,a,b in windows}),
                            'gold_session_recall':len(gs&{s for s,a,b in windows})/len(gs),
                            'oracle_feasible':can,'category':classify(scores['all_evidence'],can,missing),**scores}
                        rows.append(row)
                        if cost!=base_lookup[(dataset,sample['sample_id'],qi,'reserve8',selector,b)]['retrieved_words']:
                            unequal[dataset]+=1
            records.append(rec)
        print(f'Phase19B {sample["sample_id"]}: {len(queries)} queries complete',flush=True)
    numeric_write(output_dir/'phase19b_queries.json.gz',{'histories':original['histories'],'queries':records})
    numeric_write(output_dir/'phase19b_rows.json.gz',rows)
    summary=summarize_b(rows,records,base_rows,plan)
    (output_dir/'phase19b_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    for name,h in frozen.items():assert hashlib.sha256((base_dir/name).read_bytes()).hexdigest()==h
    runtime={'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        'implementation_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        'git_clean_at_start_of_scoring':clean,'elapsed_seconds':time.perf_counter()-start,
        'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        'queries':len(records),'rows':len(rows),'finite_thresholds_checked':thresholds,
        'feasible_witnesses_rescored':witnesses,'preserved19a_hashes':frozen,
        'unequal_actual_cost_vs_reserve8':dict(unequal),'commercial_api_calls':0,'gpu_calls':0,
        'scope':'Exploratory after19A; see separate amendment chronology','python':platform.python_version()}
    assert runtime['peak_rss_mib']<4096
    (output_dir/'phase19b_runtime.json').write_text(json.dumps(runtime,indent=2,sort_keys=True)+'\n')
    print(json.dumps(runtime,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--base-dir',type=Path,default=ROOT/'results')
    a=p.parse_args();run(a.output_dir,a.base_dir)
