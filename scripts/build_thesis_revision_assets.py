"""Figures and source data for the supervisor's editorial revision; no new experiment."""
import hashlib
import io
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures/thesis_revision'


def read(name):
    return json.loads((ROOT / 'results' / (name + '.json')).read_text())


def data():
    p10, p11, p17, p18, p19 = [read(n) for n in
        ['phase10_summary', 'phase11_summary', 'phase17_summary', 'phase18_summary', 'phase19_summary']]
    contrasts = []
    for dataset, comparison in [('locomo','random_mean'), ('locomo','centered'), ('qmsum','random_mean')]:
        r = next(r for r in p17[dataset]['contrasts'] if r['budget_words']==1024 and r['comparison']==comparison)
        contrasts.append({'dataset':dataset, 'comparison':comparison,
                          'effect_pp':r['macro_difference']*100,
                          'interval_pp':[v*100 for v in r['descriptive_cluster_bootstrap95']]})
    counts = {ds:next(r for r in p18[ds]['estimates'] if r['method']=='writer' and r['budget_words']==1024)['counts']
              for ds in ['locomo','qmsum']}
    policies = {ds:{policy:next(r for r in p19[ds]['estimates']
                               if r['budget_words']==1024 and r['selector']=='writer' and r['policy']==policy)
                   for policy in ['bm25','reserve4','reserve8']} for ds in ['locomo','evermem']}
    return {'contrasts':contrasts,'counts':counts,'policies':policies,
            'qmsum_boundary':{k:{v:p10['summary']['boundary'][k][v]*100 for v in ['online_macro','random_median']} for k in ['0','2']},
            'qmsum_retrieval':{v:p11['summary']['budgets']['1024']['online'][v]*100 for v in ['candidate_gold','flat_gold','hier_gold']}}


def build():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'Nimbus Roman','font.size':11,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.titlesize':12,'savefig.dpi':240})
    d=data(); files=[]
    def save(fig,name):
        for ext in ['png','pdf']:
            buffer=io.BytesIO()
            fig.savefig(buffer,format=ext,bbox_inches='tight',pad_inches=.16,facecolor='white')
            raw=buffer.getvalue();assert len(raw)>100
            with tempfile.NamedTemporaryFile(dir=OUT,delete=False) as temporary:
                temporary.write(raw);staged=Path(temporary.name)
            staged.replace(OUT/(name+'.'+ext))
            assert (OUT/(name+'.'+ext)).read_bytes()==raw
        plt.close(fig);files.append(name)
    colors=['#25607b','#97b1bf','#aa6c39','#663c52']
    fig,ax=plt.subplots(figsize=(6.2,3.6));ax.axis('off')
    nodes=[(.36,.77,'Conversation history'),(.02,.46,'Frozen segmentation'),(.70,.46,'Fixed BM25\nturn index'),
           (.70,.13,'Anchors and cells'),(.36,.13,'Window selection'),(.02,.13,'Evidence audit')]
    for x,y,t in nodes:
        ax.add_patch(FancyBboxPatch((x,y),.27,.15,boxstyle='round,pad=.012',facecolor='#eef3f5',edgecolor=colors[0]))
        ax.text(x+.135,y+.075,t,ha='center',va='center',fontsize=10.5)
    for a,b in [(0,1),(0,2),(1,4),(2,3),(3,4),(4,5)]:
        x,y,_=nodes[a];xx,yy,_=nodes[b]
        start=(x+.135,y) if a in [0,1,2] else (x,y+.075)
        end=(xx+.135,yy+.15) if a in [0,1,2] else (xx+.27,yy+.075)
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=12,color=colors[0]))
    ax.text(.5,.015,'Shared fixed index; reference labels enter only the audit',ha='center',fontsize=10,color=colors[3])
    save(fig,'01_pipeline')
    fig,axes=plt.subplots(2,1,figsize=(6.1,4.0),gridspec_kw={'height_ratios':[2,1]},layout='constrained')
    for ax,items,labels in [(axes[0],d['contrasts'][:2],['Writer - random mean','Writer - centered']),
                            (axes[1],d['contrasts'][2:],['Writer - random mean'])]:
        for y,r in enumerate(items):
            lo,hi=r['interval_pp'];v=r['effect_pp']
            ax.errorbar(v,y,xerr=[[v-lo],[hi-v]],fmt='o',color=colors[0],capsize=4)
            ax.annotate(f'{v:+.2f}',(v,y),xytext=(0,9),textcoords='offset points',ha='center')
        ax.set_yticks(range(len(items)),labels);ax.axvline(0,color='#777',lw=.8)
        ax.axvline(2,color=colors[2],ls='--',lw=1);ax.set_xlim(-1.3,2.4)
        ax.set_ylim(-.7,len(items)-.3);ax.grid(axis='x',alpha=.18)
    axes[0].set_title('LoCoMo: complete-evidence coverage (7 histories)')
    axes[1].set_title('QMSum: relevant-turn coverage (10 source clusters)')
    axes[1].set_xlabel('Paired macro difference (percentage points)')
    save(fig,'02_controlled_effects')
    fig,axes=plt.subplots(1,2,figsize=(6.2,3.6),layout='constrained')
    x=np.arange(2);w=.34
    for j,(key,label) in enumerate([('online_macro','Writer'),('random_median','Random median')]):
        vals=[d['qmsum_boundary'][k][key] for k in ['0','2']]
        bars=axes[0].bar(x+(j-.5)*w,vals,w,label=label,color=colors[j]);axes[0].bar_label(bars,fmt='%.1f',fontsize=10,padding=3)
    axes[0].set_xticks(x,['Exact onset','Within 2 turns']);axes[0].set_title('Phase 10: onset alignment')
    axes[0].set_ylabel('Meeting macro (%)');axes[0].legend(frameon=False,fontsize=9)
    vals=[d['qmsum_retrieval'][k] for k in ['candidate_gold','flat_gold','hier_gold']]
    bars=axes[1].bar(range(3),vals,color=[colors[1],colors[0],colors[2]])
    axes[1].bar_label(bars,fmt='%.1f',padding=3,fontsize=10)
    axes[1].set_xticks(range(3),['Candidates\n4096 words','Flat\n1024 words','Two-stage\n1024 words'])
    axes[1].set_title('Phase 11: relevant-turn coverage')
    for ax in axes:ax.set_ylim(0,105);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    save(fig,'03_qmsum_gap')
    fig,ax=plt.subplots(figsize=(6.2,3.3),layout='constrained')
    keys=['complete_success','missing_gold_session','window_geometry_infeasible','feasible_selection_miss']
    labels=['Complete','Missing session','Geometry infeasible','Feasible selection miss']
    left=[0.,0.]
    for key,label,color in zip(keys,labels,colors):
        raw=[d['counts'][ds][key] for ds in ['locomo','qmsum']]
        vals=[raw[i]/sum(d['counts'][ds].values())*100 for i,ds in enumerate(['locomo','qmsum'])]
        ax.barh([1,0],vals,left=left,color=color,label=label,height=.5)
        for i,(v,n) in enumerate(zip(vals,raw)):
            if v>2:ax.text(left[i]+v/2,1-i,str(n),ha='center',va='center',color='white',fontsize=10)
        left=[left[i]+vals[i] for i in range(2)]
    ax.set_yticks([1,0],['LoCoMo (599)','QMSum (244)']);ax.set_xlim(0,100)
    ax.set_xlabel('Share of questions (%) - numbers inside bars are counts')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.24),ncol=2,frameon=False,fontsize=10)
    ax.set_title('Phase 18: exact diagnosis at 1024 source words')
    save(fig,'04_failure_decomposition')
    fig,ax=plt.subplots(figsize=(6.2,3.2),layout='constrained');x=np.arange(3)
    for j,(policy,label,color) in enumerate([('bm25','BM25',colors[0]),('reserve8','Reserve 8',colors[2])]):
        r=d['policies']['locomo'][policy];vals=[r[k] for k in ['all_sessions_count','exact_feasible_count','all_evidence_count']]
        bars=ax.bar(x+(j-.5)*.34,vals,.34,label=label,color=color);ax.bar_label(bars,padding=3,fontsize=10)
    ax.set_xticks(x,['All sessions accessible','Exact feasibility','Complete evidence'])
    ax.set_ylim(0,599);ax.set_ylabel('Questions out of 599');ax.legend(frameon=False)
    ax.set_title('Phase 19: LoCoMo, writer, 1024 source words');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    save(fig,'05_access_assembly_locomo')
    fig,axes=plt.subplots(1,2,figsize=(6.2,3.2),layout='constrained')
    vals1=[d['policies']['evermem'][p]['all_sessions_count'] for p in ['bm25','reserve8']]
    vals2=[d['policies']['evermem'][p]['macro_primary_metric']*100 for p in ['bm25','reserve8']]
    for ax,vals,title,ylabel,lim,fmt in [(axes[0],vals1,'All reference sessions accessible','Questions out of 609',80,'%d'),
                                      (axes[1],vals2,'Complete reference-message recall','Equal-project macro (%)',25,'%.2f')]:
        bars=ax.bar([0,1],vals,color=[colors[0],colors[2]],width=.55);ax.bar_label(bars,fmt=fmt,padding=3)
        ax.set_xticks([0,1],['BM25','Reserve 8']);ax.set_title(title,fontsize=11);ax.set_ylabel(ylabel);ax.set_ylim(0,lim)
        ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    save(fig,'06_access_assembly_external')
    sources={f'results/{n}.json':hashlib.sha256((ROOT/'results'/(n+'.json')).read_bytes()).hexdigest()
             for n in ['phase10_summary','phase11_summary','phase17_summary','phase18_summary','phase19_summary']}
    record={'activity':'visualization of existing results; no new experiment','source_sha256':sources,
            'values':d,'figures':files,'text_font':'Nimbus Roman','new_model_inference_calls':0}
    record['artifact_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(OUT.iterdir()) if p.suffix in ['.png','.pdf']}
    (ROOT/'thesis/revision_figure_data.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('Built',len(files),'source-backed figures')


if __name__=='__main__':
    build()
