"""Post-result diagnostics, historical persona clustering, and exported figures.

This script never retunes or changes the registered primary analysis.
"""
from collections import defaultdict, Counter
import gzip, hashlib, json, random, statistics
from pathlib import Path
from run_baselines import ROOT


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def historical_persona_ci(rows):
    paired=defaultdict(dict)
    for r in rows:
        paired[(r['persona'],r['period'],r['question_id'])][r['method']]=r['active_any']
    groups=defaultdict(list)
    counts=Counter()
    for key, values in paired.items():
        assert set(values)=={'writer',*[f'random_{s}' for s in range(5)]}
        groups[key[0]].append(values['writer']-statistics.mean(values[f'random_{s}'] for s in range(5)))
        counts.update(values)
    assert len(paired)==398 and len(groups)==10
    rng=random.Random(17); personas=sorted(groups); draws=[]
    for _ in range(2000):
        draws.append(statistics.mean(v for p in rng.choices(personas,k=10) for v in groups[p]))
    draws.sort()
    def q(p):
        x=(len(draws)-1)*p;a=int(x)
        return draws[a]+(draws[min(a+1,len(draws)-1)]-draws[a])*(x-a)
    return {'questions':len(paired),'personas':len(groups),'writer_count':counts['writer'],
            'random_mean_count':statistics.mean(counts[f'random_{s}'] for s in range(5)),
            'question_weighted_difference':statistics.mean(v for vs in groups.values() for v in vs),
            'descriptive_persona_bootstrap95':[q(.025),q(.975)],
            'per_persona_question_count':{p:len(v) for p,v in sorted(groups.items())},
            'interpretation':'Post-hoc diagnostic, 10 persona clusters retaining all periods; not a new experiment or confirmatory interval.'}


def main():
    rows=read(ROOT/'results/phase17_rows.json.gz'); summary=json.loads((ROOT/'results/phase17_summary.json').read_text())
    diagnostics={}
    for dataset in ['locomo','qmsum']:
        r=[x for x in rows if x['dataset']==dataset and x['budget_words']==1024]
        methods={m:{(x['sample_id'],x['question_index']):x for x in r if x['method']==m} for m in ['centered','writer']}
        counts=Counter((methods['centered'][k]['all_evidence'],v['all_evidence']) for k,v in methods['writer'].items())
        by=[]
        for label,predicate in [('single_turn',lambda x:x['evidence_total']==1),('multiple_turns',lambda x:x['evidence_total']>1),('single_session',lambda x:x['gold_session_count']==1),('multiple_sessions',lambda x:x['gold_session_count']>1)]:
            for method in ['centered','writer']:
                rs=[x for x in methods[method].values() if predicate(x)]
                if rs: by.append({'stratum':label,'method':method,'questions':len(rs),'all_evidence_count':sum(x['all_evidence'] for x in rs),'mean_turn_recall':statistics.mean(x['turn_recall'] for x in rs)})
        diagnostics[dataset]={'discordance_centered_writer':{f'{a}_{b}':n for (a,b),n in sorted(counts.items())},'strata_descriptive':by,
          'all_gold_sessions_count':sum(x['all_gold_sessions'] for x in methods['writer'].values()),
          'capacity_shortfalls':{b:sum(x['retrieved_words']<b for x in rows if x['dataset']==dataset and x['method']=='writer' and x['budget_words']==b) for b in [512,1024,2048]}}
    diagnostics['status']='Post-result descriptive diagnostics; subgroups were listed in the local plan. No tuning.'
    (ROOT/'results/phase17_diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
    history=read(ROOT/'results/phase16_rows.json.gz')
    original=[r for r in history if r['budget_words']==1024 and r['active_count']>0 and r['method']!='session']
    equal=read(ROOT/'results/phase16_equal_selected.json.gz')['rows']
    old={'phase16_original_persona_reanalysis':historical_persona_ci(original),'phase16_equal_selected_persona_reanalysis':historical_persona_ci(equal),
      'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'results/phase16_rows.json.gz',ROOT/'results/phase16_equal_selected.json.gz']}}
    (ROOT/'results/phase17_historical_persona_audit.json').write_text(json.dumps(old,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    out=ROOT/'figures/phase17';out.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(10,3.4),layout='constrained')
    for ax,d in zip(axes,['locomo','qmsum']):
        cs=[c for c in summary[d]['contrasts'] if c['budget_words']==1024]
        for y,c in zip([1,0],cs):
            p=c['macro_difference']*100;lo,hi=[x*100 for x in c['descriptive_cluster_bootstrap95']]
            ax.errorbar(p,y,xerr=[[p-lo],[hi-p]],fmt='o',capsize=4,color='#096B73')
            ax.annotate(f'{p:+.2f} [{lo:+.2f}, {hi:+.2f}]',xy=(p,y),xytext=(0,12),textcoords='offset points',ha='center',fontsize=9)
        ax.axvline(0,color='#999',ls='--',lw=1);ax.set_yticks([1,0],['vs random mean','vs centered']);ax.set_ylim(-.45,1.55)
        ax.set_title('LoCoMo: all-evidence rate' if d=='locomo' else 'QMSum: relevant-turn recall');ax.set_xlabel('Writer difference (percentage points)')
        if d=='locomo':ax.axvline(2,color='#BC663D',ls=':',lw=1);ax.set_xlim(-.6,2.2)
    for ext in ['svg','png']:fig.savefig(out/f'contrasts_1024.{ext}',dpi=190)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.5),layout='constrained')
    for ax,d in zip(axes,['locomo','qmsum']):
        for method,label,color in [('centered','Centered','#444444'),('writer','Frozen writer','#096B73'),('random','Random mean','#BC663D')]:
            vals=[]
            for b in [512,1024,2048]:
                e=[x['macro_metric']*100 for x in summary[d]['estimates'] if x['budget_words']==b and (x['method'].startswith('random_') if method=='random' else x['method']==method)]
                vals.append(statistics.mean(e))
            ax.plot([512,1024,2048],vals,'o-',label=label,color=color)
        ax.set_title(d.upper());ax.set_xticks([512,1024,2048]);ax.set_xlabel('Word cap (actual use matched)');ax.set_ylabel('Macro metric (%)');ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=9)
    for ext in ['svg','png']:fig.savefig(out/f'budget_sensitivity.{ext}',dpi=190)
    plt.close(fig)
    for svg in out.glob('*.svg'):
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    print(json.dumps(old,indent=2))

if __name__=='__main__':main()
