"""Derive inspectable diagnostics and export scientific figures from fixed rows."""
import argparse
from collections import Counter,defaultdict
import gzip
import json
from pathlib import Path
import statistics
from run_baselines import ROOT
from run_phase19_session_access import mean_by_history
from run_phase18_feasibility import quantile


def load(path):return json.loads(gzip.decompress(path.read_bytes()))


def analyze(directory,figures=True):
    a=load(directory/'phase19_queries.json.gz');ar=load(directory/'phase19_rows.json.gz')
    b=load(directory/'phase19b_queries.json.gz');br=load(directory/'phase19b_rows.json.gz')
    s=json.loads((directory/'phase19_summary.json').read_text())
    sb=json.loads((directory/'phase19b_summary.json').read_text())
    lookup={(r['dataset'],r['sample_id'],r['question_id'],r['policy'],r['selector'],r['budget_words']):r for r in ar}
    out={}
    examples=[]
    for d in ['locomo','evermem']:
        qs=[q for q in a['queries'] if q['dataset']==d]
        policies={}
        for p in qs[0]['policies']:
            edits=Counter(len(set(q['policies'][p]['anchor_indices'])-set(q['policies']['bm25']['anchor_indices'])) for q in qs)
            policies[p]={'changed_queries':len(qs)-edits[0],'edit_histogram':dict(sorted(edits.items()))}
        transitions={}
        for field in ['all_gold_sessions','oracle_feasible','all_evidence']:
            transitions[field]=dict(Counter(f'{lookup[(d,q["sample_id"],q["question_id"],"bm25","writer",1024)][field]}->{lookup[(d,q["sample_id"],q["question_id"],"reserve8","writer",1024)][field]}' for q in qs))
        lengths=[sum(g['end']-g['start'] for g in q['gold_spans']) for q in qs]
        messages=[sum(g['end']>g['start'] for g in q['gold_spans']) for q in qs]
        ngs=[len({g['session'] for g in q['gold_spans'] if g['end']>g['start']}) for q in qs]
        costs=[]
        for budget in [512,1024,2048]:
            for p in ['reserve4','reserve8']:
                differences=[lookup[(d,q['sample_id'],q['question_id'],p,'writer',budget)]['retrieved_words']
                    -lookup[(d,q['sample_id'],q['question_id'],'bm25','writer',budget)]['retrieved_words'] for q in qs]
                costs.append({'policy':p,'budget_words':budget,'unequal_pairs':sum(x!=0 for x in differences),'minimum_delta':min(differences),'maximum_delta':max(differences)})
            controls=[r for r in br if r['dataset']==d and r['budget_words']==budget and r['selector']=='writer']
            differences=[r['retrieved_words']-lookup[(d,r['sample_id'],r['question_id'],'reserve8','writer',budget)]['retrieved_words'] for r in controls]
            costs.append({'policy':'edit_controls','budget_words':budget,'query_seed_conditions':len(controls),
                          'unequal_pairs':sum(x!=0 for x in differences),'minimum_delta':min(differences),'maximum_delta':max(differences)})
        out[d]={'queries':len(qs),'histories':len({q['sample_id'] for q in qs}),'policies':policies,
            'pool_all_gold_session_count':sum(q['pool_all_gold_sessions'] for q in qs),
            'reserve8_transitions':transitions,
            'reference_granularity':{'median_words':quantile(lengths,.5),'p90_words':quantile(lengths,.9),'maximum_words':max(lengths),
                'reference_word_lower_bound_exceeds1024':sum(n>1024 for n in lengths),
                'median_messages':quantile(messages,.5),'p90_messages':quantile(messages,.9),
                'median_sessions':quantile(ngs,.5),'p90_sessions':quantile(ngs,.9),'more_than8_gold_sessions':sum(n>8 for n in ngs)},
            'actual_cost_audit':costs}
        for kind in ['gained_access_but_infeasible','lost_feasibility_with_sessions_retained']:
            for q in qs:
                base=lookup[(d,q['sample_id'],q['question_id'],'bm25','writer',1024)]
                target=lookup[(d,q['sample_id'],q['question_id'],'reserve8','writer',1024)]
                matches=(base['all_gold_sessions']==0 and target['all_gold_sessions']==1 and target['oracle_feasible']==0) if kind=='gained_access_but_infeasible' else (base['oracle_feasible']==1 and target['oracle_feasible']==0 and target['all_gold_sessions']==1)
                if not matches:continue
                data=q['policies']['reserve8'];violations=[{'session':c['session'],'rank':c['rank'],
                    'anchor':c['anchor'],'required_width':c['required_width'],'allocated_width':w,
                    'required_span':[c['required_left'],c['required_right']]}
                    for c,w in zip(data['cells'],target['widths']) if c['required_width']>w]
                examples.append({'selection':'post-result illustrative case, not an inferential sample','dataset':d,'sample_id':q['sample_id'],
                    'question_id':q['question_id'],'kind':kind,'baseline_complete':base['all_evidence'],
                    'reserve8_complete':target['all_evidence'],'baseline_minimum_budget':q['policies']['bm25']['minimum_total_budget'],
                    'reserve8_minimum_budget':data['minimum_total_budget'],'violating_cells':violations})
                break
    out['illustrative_cases']=examples
    out['condition_counts']={'unique_queries':len(a['queries']),'phase19a':len(ar),'phase19b':len(br),
        'total_query_policy_selector_budget_conditions':len(ar)+len(br),'independent_sample_warning':'Conditions, questions and seeds are not independent research replications.'}
    (directory/'phase19_diagnostics.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    if figures:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
            'savefig.dpi':200,'svg.hashsalt':'phase19-fixed'})
        target=ROOT/'figures/phase19';target.mkdir(parents=True,exist_ok=True)
        labels=['BM25 top8','Reserve4','Reserve8','Edit-matched mean']
        colors=['#284A63','#6F8C9E','#B14B3E','#B6C7CF']
        fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
        for ax,d,title in zip(axs,['locomo','evermem'],['LoCoMo | complete evidence','EverMemBench | complete-message recall']):
            vals=[next(r['macro_primary_metric'] for r in s[d]['estimates'] if r['policy']==p and r['selector']=='writer' and r['budget_words']==1024) for p in ['bm25','reserve4','reserve8']]+[sb[d]['primary_budget_mean_control_metric']]
            bars=ax.barh(labels,[v*100 for v in vals],color=colors,height=.62)
            ax.invert_yaxis();ax.set_xlim(0,90 if d=='locomo' else 25)
            ax.set_xlabel('Equal-history mean (%)');ax.set_title(title,fontweight='bold',fontsize=10)
            for bar,value in zip(bars,vals):ax.text(value*100+.3,bar.get_y()+bar.get_height()/2,f'{value*100:.2f}',va='center',fontsize=10)
        fig.suptitle('Fixed 1,024 source words | unchanged writer | edit control is exploratory',fontsize=11)
        for ext in ['png','svg']:fig.savefig(target/f'coverage1024.{ext}',metadata={'Date':None} if ext=='svg' else {})
        plt.close(fig)
        fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
        for ax,d in zip(axs,['locomo','evermem']):
            for offset,p,color in [(-.17,'bm25','#284A63'),(.17,'reserve8','#B14B3E')]:
                r=next(r for r in s[d]['estimates'] if r['policy']==p and r['selector']=='writer' and r['budget_words']==1024)
                values=[r['all_sessions_count'],r['exact_feasible_count'],r['all_evidence_count']]
                bars=ax.bar([x+offset for x in range(3)],values,width=.32,color=color,label=p)
                for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+max(values)*.02,str(value),ha='center',fontsize=9)
            ax.set_xticks(range(3),['All gold\nsessions','Exact complete\nfeasibility','Realized complete\nevidence'])
            ax.set_ylabel('Queries (descriptive counts)');ax.set_title(d);ax.legend(frameon=False)
            ax.set_ylim(0,560 if d=='locomo' else 72)
        fig.suptitle('Access gains can coexist with lower feasible and realized coverage',fontsize=12)
        for ext in ['png','svg']:fig.savefig(target/f'access_and_coverage.{ext}',metadata={'Date':None} if ext=='svg' else {})
        plt.close(fig)
        fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
        for ax,d in zip(axs,['locomo','evermem']):
            x=s[d]['contrasts']['reserve8_secondary']['per_history']
            ax.axvline(0,color='#7B858D',lw=.8)
            ax.scatter([v*100 for v in x.values()],range(len(x)),s=45,color='#B14B3E')
            ax.set_yticks(range(len(x)),list(x));ax.invert_yaxis();ax.set_title(d)
            ax.set_xlabel('Reserve8 minus BM25 (percentage points)')
        fig.suptitle('Every evaluated history shows a negative Reserve8 point effect at 1,024 words',fontsize=11)
        for ext in ['png','svg']:fig.savefig(target/f'per_history_effects.{ext}',metadata={'Date':None} if ext=='svg' else {})
        plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,2.1),layout='constrained');ax.axis('off')
        ax.text(.5,.78,r'$p_0(T)=\mathbf{1}\{g(t_1)\notin T\}\;\frac{\binom{7-n_b(T)}{7-d}}{\binom{7}{7-d}}\;\frac{\binom{56-n_o(T)}{d}}{\binom{56}{d}}$',ha='center',va='center',fontsize=21)
        ax.text(.5,.23,r'$\Pr(G\subseteq S_A)=\sum_{T\subseteq G}(-1)^{|T|}p_0(T)$',ha='center',va='center',fontsize=21)
        for ext in ['png','svg']:fig.savefig(target/f'edit_null_equation.{ext}',metadata={'Date':None} if ext=='svg' else {})
        plt.close(fig)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,default=ROOT/'results')
    p.add_argument('--no-plots',action='store_true')
    a=p.parse_args();result=analyze(a.directory,not a.no_plots)
    print(json.dumps(result['condition_counts'],indent=2))
