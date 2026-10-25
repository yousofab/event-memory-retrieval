"""Portable certificate verification. No raw transcripts, reader model or API."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
from run_baselines import ROOT
from run_phase17_fixed_anchors import allocate, candidate_bounds, fingerprint
from run_phase18_feasibility import requirements, minimum_budget, feasible, witness_windows, classify
from run_phase19_session_access import select_anchors, summarize


def direct_score(gold, windows):
    """Independent interval-union scorer; refuses duplicate/overlapping words."""
    by = defaultdict(list)
    for s,a,b in windows:
        if not isinstance(a,int) or not isinstance(b,int) or a<0 or b<=a:
            raise ValueError('Invalid source window')
        by[s].append((a,b))
    for values in by.values():
        values.sort()
        if any(a2<b1 for (a1,b1),(a2,b2) in zip(values,values[1:])):
            raise ValueError('Overlapping windows')
    gold = [g for g in gold if g['end']>g['start']]
    if not gold:
        raise ValueError('No nonempty gold')
    coverage = [sum(max(0,min(b,g['end'])-max(a,g['start'])) for a,b in by.get(g['session'],[])) for g in gold]
    lengths = [g['end']-g['start'] for g in gold]
    complete = sum(c==n for c,n in zip(coverage,lengths))
    gs = {g['session'] for g in gold}
    return {'all_evidence':int(complete==len(gold)),'any_evidence':int(complete>0),
        'turn_recall':complete/len(gold),'gold_word_recall':sum(coverage)/sum(lengths),
        'evidence_found':complete,'evidence_total':len(gold),'all_gold_sessions':int(gs<=by.keys()),
        'gold_session_recall':len(gs&by.keys())/len(gs)}


def validate(directory):
    plan = json.loads((ROOT/'configs/phase19_plan.json').read_text())
    payload = json.loads(gzip.decompress((directory/'phase19_queries.json.gz').read_bytes()))
    rows = json.loads(gzip.decompress((directory/'phase19_rows.json.gz').read_bytes()))
    runtime = json.loads((directory/'phase19_runtime.json').read_text())
    assert runtime['plan_sha256']==hashlib.sha256((ROOT/'configs/phase19_plan.json').read_bytes()).hexdigest()
    histories = {h['sample_id']:h for h in payload['histories']}
    records = {(q['dataset'],q['sample_id'],q['question_id']):q for q in payload['queries']}
    assert len(records)==len(payload['queries'])
    checked_thresholds = 0
    for q in records.values():
        pool = q['pool']
        assert len(pool)==plan['candidate_pool_turns']
        assert len({p['turn_index'] for p in pool})==len(pool)
        assert all(p['end']>p['start'] and p['anchor']==(p['start']+p['end']-1)//2 for p in pool)
        gold = [g for g in q['gold_spans'] if g['end']>g['start']]
        assert q['pool_all_gold_sessions']==int({g['session'] for g in gold}<={p['session'] for p in pool})
        for policy, data in q['policies'].items():
            anchors = select_anchors(pool,policy,f'{q["sample_id"]}|{q["question_id"]}')
            assert anchors == data['anchor_indices']
            entries = {p['turn_index']:p for p in pool}
            cells = data['cells']
            assert len(cells)==8 and [c['rank'] for c in cells]==list(range(8))
            assert [(c['session'],c['anchor']) for c in cells]==[(entries[i]['session'],entries[i]['anchor']) for i in anchors]
            groups=defaultdict(list)
            for c in cells:groups[c['session']].append(c)
            for sid,cs in groups.items():
                cs.sort(key=lambda c:c['anchor'])
                edges=[0]+[(a['anchor']+b['anchor'])//2+1 for a,b in zip(cs,cs[1:])]+[histories[q['sample_id']]['session_lengths'][sid]]
                assert [(c['left'],c['right']) for c in cs]==list(zip(edges,edges[1:]))
            expected, missing = requirements(cells,gold)
            assert expected==cells and missing==data['missing_gold_sessions']
            minimum=None if missing else minimum_budget(cells)
            assert minimum==data['minimum_total_budget']
            if minimum is not None:
                assert feasible(cells,allocate(cells,minimum))
                assert not feasible(cells,allocate(cells,minimum-1))
                checked_thresholds+=1
    seen = set()
    witnesses = 0
    unequal_costs = 0
    grouped=defaultdict(list)
    for r in rows:
        key=(r['dataset'],r['sample_id'],r['question_id'])
        identity=key+(r['policy'],r['selector'],r['budget_words'])
        assert identity not in seen
        seen.add(identity)
        q=records[key];data=q['policies'][r['policy']];cells=data['cells']
        assert r['selector'] in plan['selectors'] and r['budget_words'] in plan['budget_words']
        widths=allocate(cells,r['budget_words'])
        assert widths==r['widths']
        assert len(r['windows'])==8
        for c,w,(sid,a,b) in zip(cells,widths,r['windows']):
            lo,hi=candidate_bounds(c,w)
            assert sid==c['session'] and b-a==w and lo<=a<=hi
        assert r['retrieved_words']==sum(widths)==sum(b-a for s,a,b in r['windows'])
        assert r['retrieved_words']==min(r['budget_words'],sum(c['capacity'] for c in cells))
        assert r['selected_sessions']==len({s for s,a,b in r['windows']})
        scores=direct_score(q['gold_spans'],r['windows'])
        for field,value in scores.items():assert r[field]==value,(identity,field)
        can=int(feasible(cells,widths,data['missing_gold_sessions']))
        assert r['oracle_feasible']==can
        assert r['all_evidence']<=can<=r['all_gold_sessions']<=q['pool_all_gold_sessions']
        assert r['category']==classify(r['all_evidence'],can,data['missing_gold_sessions'])
        if r['selector']=='writer' and can:
            witness=witness_windows(cells,widths)
            assert direct_score(q['gold_spans'],witness)['all_evidence']==1
            witnesses+=1
        grouped[key+(r['policy'],r['budget_words'])].append(r)
    for rs in grouped.values():
        assert len(rs)==2 and {r['selector'] for r in rs}==set(plan['selectors'])
        assert rs[0]['widths']==rs[1]['widths'] and rs[0]['retrieved_words']==rs[1]['retrieved_words']
    assert len(rows)==len(records)*len(plan['policies'])*len(plan['selectors'])*len(plan['budget_words'])
    expected_summary=summarize(rows,plan)
    recorded_summary=json.loads((directory/'phase19_summary.json').read_text())
    assert expected_summary==recorded_summary
    assert checked_thresholds==runtime['finite_thresholds_checked']
    assert witnesses==runtime['feasible_witnesses_rescored']
    return {'passed':True,'queries':len(records),'rows':len(rows),'thresholds':checked_thresholds,
        'feasible_witnesses':witnesses,'paired_selector_cost_groups':len(grouped),
        'summary_recomputed':True,'source_backed_ranking_reproduction':'separate documented command',
        'raw_data_required':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,default=ROOT/'results')
    args=p.parse_args()
    print(json.dumps(validate(args.directory),indent=2,sort_keys=True))
