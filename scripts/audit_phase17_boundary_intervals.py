"""Post-result audit of zero-word parts versus effective boundary intervals.

Turn-partition counts remain matched by the registered sampler. Deduplicating
word offsets can remove a zero-word part without changing returned window cost.
This audit records that distinction; it does not modify any experiment output.
"""
import json
from pathlib import Path
from run_phase17_fixed_anchors import ROOT,boundary_maps
from run_phase10_topic_transfer import sample_for


def main():
    settings=json.loads((ROOT/'configs/phase8_causal_plan.json').read_text())['causal_writer']
    manifest=json.loads((ROOT/'results/phase1_audit.json').read_text())
    ids={r['sample_id'] for r in manifest['manifest'] if r['split']=='held_out'}
    jobs=[('locomo',s) for s in json.loads((ROOT/'data/raw/locomo10.json').read_text()) if s['sample_id'] in ids]
    jobs += [('qmsum',sample_for(p.stem,json.loads(p.read_text()))) for p in sorted((ROOT/'data/raw/qmsum_test').glob('*.json'))]
    output=[];differences=[]
    for dataset,sample in jobs:
        maps,stats=boundary_maps(sample,settings)
        counts={m:sum(max(0,len(b)-1) for b in ss.values()) for m,ss in maps.items()}
        output.append({'dataset':dataset,'sample':sample['sample_id'],'turn_partition_count_each':stats['writer_segments'],'effective_nonempty_intervals':counts})
        for method,count in counts.items():
            if count!=stats['writer_segments']:
                differences.append({'dataset':dataset,'sample':sample['sample_id'],'method':method,'partition_count':stats['writer_segments'],'effective_nonempty_intervals':count})
    result={'status':'Post-result integrity audit; no tuning or primary result changes','histories':len(jobs),'differences':differences,'rows':output,
            'interpretation':'Registered control matches whole-turn partition counts. Zero-word parts can make effective nonempty interval counts smaller: see each recorded difference. Output windows, costs and candidate opportunities remain exactly paired.'}
    (ROOT/'results/phase17_empty_boundary_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'histories':len(jobs),'differences':differences},indent=2))

if __name__=='__main__':main()
