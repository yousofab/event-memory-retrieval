"""Independent numeric and opportunity-contract checks for Phase 17."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
from run_baselines import ROOT
from run_phase17_fixed_anchors import METHODS, summarize, digest


def validate(directory):
    summary=json.loads((directory/'phase17_summary.json').read_text())
    raw=gzip.decompress((directory/'phase17_rows.json.gz').read_bytes())
    rows=json.loads(raw)
    assert hashlib.sha256(raw).hexdigest()==summary['numeric_rows_sha256']
    assert summary['plan_sha256']==digest(ROOT/'configs/phase17_plan.json')
    assert len(rows)==55638
    grouped=defaultdict(list); identities=set()
    for r in rows:
        identity=(r['dataset'],r['sample_id'],r['question_index'],r['budget_words'],r['method'])
        assert identity not in identities;identities.add(identity)
        grouped[identity[:-1]].append(r)
        assert r['method'] in METHODS and r['budget_words'] in [512,1024,2048]
        assert 0<r['retrieved_words']<=r['budget_words']
        # Saturated anchor sessions can contain fewer words than the cap.
        # Exact equality is between methods; the runner also verifies min(B, capacity).
        assert r['selected_windows']==8 and len(r['windows'])==8
        assert r['cell_widths']==[b-a for s,a,b in r['windows']]
        spans=defaultdict(list)
        for s,a,b in r['windows']:
            assert 0<=a<b;spans[s].append((a,b))
        for ranges in spans.values():
            ranges.sort()
            assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]))
        assert len(spans)==r['selected_sessions']
        assert sum(b-a for s,a,b in r['windows'])==r['retrieved_words']
        assert r['all_evidence']==int(r['evidence_found']==r['evidence_total'])
        assert r['any_evidence']==int(r['evidence_found']>0)
        assert r['turn_recall']==r['evidence_found']/r['evidence_total']
        assert 0<=r['gold_word_recall']<=1
        assert r['empty_gold_turns']==0
    for group in grouped.values():
        assert sorted(r['method'] for r in group)==sorted(METHODS)
        for field in ['opportunity_fingerprint','retrieved_words','selected_windows','selected_sessions','candidate_windows','cell_widths']:
            assert len({json.dumps(r[field]) for r in group})==1,(field,group[0])
    for dataset,count in [('locomo',599),('qmsum',244)]:
        assert len({(r['sample_id'],r['question_index']) for r in rows if r['dataset']==dataset})==count
    recomputed=summarize(rows)
    assert all(summary[d]==recomputed[d] for d in ['locomo','qmsum'])
    print(json.dumps({'rows':len(rows),'paired_query_budget_groups':len(grouped),
                     'exact_equal_cost_and_opportunities':True,'numeric_hash':summary['numeric_rows_sha256']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=ROOT/'results')
    validate(p.parse_args().directory)
