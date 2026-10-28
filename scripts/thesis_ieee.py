"""Number source citations by first appearance; keep original claim IDs in sidecars."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BASE='9dfb838d09d41a8269db557ffa16960a4adde2f3'
REPO='https://github.com/yousofab/event-memory-retrieval'
CODE=r'(?:P\d{2}|C\d{2}|S\d{2}[LFBDE]?|Z\d{2})'
INTERNAL={
 'S10':('docs/phase10.md','Phase 10: topic boundaries and evidence retrieval'),
 'S11':('docs/phase11.md','Phase 11: hierarchical evidence retrieval'),
 'S17':('docs/phase17.md','Phase 17: fixed-anchor controlled evaluation'),
 'S17L':('docs/phase17_state_ledger.md','Historical evidence and decision ledger'),
 'S18':('docs/phase18.md','Phase 18: exact evidence feasibility and failure diagnosis'),
 'S18F':('docs/phase18_formal_contract.md','Formal contract and proof of exact feasibility'),
 'S19':('docs/phase19.md','Phase 19: session access and evidence assembly'),
 'S19B':('docs/phase19b_amendment.md','Phase 19B: post-result matched-edit amendment'),
 'S19D':('results/phase19_diagnostics.json','Reference-granularity diagnostics'),
 'S19E':('docs/phase19_reproduce.md','Reproduction instructions for Phase 19'),
 'Z01':('thesis/tools_and_ai_register.json','Software versions and generative-assistance disclosure'),
 'Z02':('configs/phase6_semantic_plan.json','Registered LSA configuration and training policy'),
 'Z03':('thesis/evidence_ledger_integrated.json','Integrated numerical claim and source ledger'),
 'Z04':('results/phase1_audit.json','Initial LoCoMo eligibility and split audit')}
CLAIMS={**{f'C{i:02}':'S10' for i in range(1,4)},**{f'C{i:02}':'S11' for i in range(4,7)},
        **{f'C{i:02}':'S18' for i in range(7,10)},**{f'C{i:02}':'S19' for i in range(10,13)},
        'C13':'S19B','C14':'S17','C15':'S19D','C16':'Z04'}


def authors(names):
    def short(n):
        words=n.split();return ' '.join(w[0]+'.' for w in words[:-1])+' '+words[-1]
    if len(names)>6:return short(names[0])+' et al.'
    result=[short(n) for n in names]
    if len(result)==2:return ' and '.join(result)
    return result[0] if len(result)==1 else ', '.join(result[:-1])+', and '+result[-1]


def external_entry(r):
    key=r['id'];year=r['year'];doi=r.get('doi')
    venue={
      'P01':'Behav. Brain Sci., vol. 3, no. 3, pp. 417-424',
      'P02':'Psychol. Bull., vol. 133, no. 2, pp. 273-293',
      'P03':'eLife, version of record, Jul. 7',
      'P04':'Found. Trends Inf. Retr., vol. 4, nos. 1-2, pp. 1-174',
      'P05':'in Advances in Neural Information Processing Systems',
      'P06':'in Proc. 62nd Annu. Meeting Assoc. Comput. Linguistics, pp. 13851-13870',
      'P07':'in Proc. Conf. North Amer. Chapter Assoc. Comput. Linguistics, pp. 5905-5921',
      'P08':'in Proc. Int. Conf. Learn. Represent.',
      'P09':'in Proc. Int. Conf. Learn. Represent.',
      'P11':'Trans. Assoc. Comput. Linguist., vol. 12, pp. 157-173'}
    if key in venue:v=venue[key]
    else:
        identifier=re.search(r'(\d{4}\.\d{4,5})(v\d+)',r['url'])
        v='arXiv preprint, arXiv:'+identifier[1]+identifier[2] if identifier else 'arXiv preprint'
    text=f'{authors(r["authors"])}, “{r["title"]},” {v}, {year}.'
    if doi:text+=' doi: '+doi+'.'
    text+=' [Online]. Available: '+r['url']
    return {'key':key,'text':text,'url':r['url'],'kind':'external_primary'}


class References:
    def __init__(self):
        self.sources={r['id']:external_entry(r) for r in json.loads((ROOT/'thesis/literature_review_20261027.json').read_text())['sources']}
        for key,(path,title) in INTERNAL.items():
            ref='main' if key=='Z01' else BASE
            url=REPO+'/blob/'+ref+'/'+path
            self.sources[key]={'key':key,'path':path,'url':url,'kind':'project_artifact',
              'text':f'Y. Abolfathi Roozbahani, “{title},” event-memory-retrieval, 2026. [Online]. Available: {url}'}
        self.order=[]
        self.occurrences=[]

    def cite(self,keys):
        numbers=[]
        for key in keys:
            key=CLAIMS.get(key,key)
            if key not in self.sources:raise ValueError('Unknown reference '+key)
            if key not in self.order:self.order.append(key)
            n=self.order.index(key)+1
            if n not in numbers:numbers.append(n)
        self.occurrences.extend(numbers)
        return ', '.join(f'[{n}]' for n in sorted(numbers))

    def convert(self,text):
        def bracket(m):
            body=m[1]
            if not re.search(r'\b'+CODE+r'\b',body):return m[0]
            def expand(r):
                a,b=r[1],r[2]
                if a[0]!=b[0] or a[0] not in 'PC':raise ValueError(r[0])
                return ','.join(a[0]+str(i).zfill(2) for i in range(int(a[1:]),int(b[1:])+1))
            body=re.sub(r'('+CODE+r')\s+تا\s+('+CODE+r')',expand,body)
            return self.cite(re.findall(r'\b'+CODE+r'\b',body))
        text=re.sub(r'\[([^\[\]\n]+)\]',bracket,text)
        return re.sub(r'\b('+CODE+r')\b',lambda m:self.cite([m[1]]),text)

    def save(self):
        rows=[{'number':i+1,**self.sources[k]} for i,k in enumerate(self.order)]
        record={'style':'IEEE','ordering':'first appearance in the revised manuscript',
                'guide_url':'https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf',
                'references':rows,'citation_occurrences':self.occurrences}
        (ROOT/'thesis/ieee_reference_map.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        (ROOT/'thesis/references_ieee.md').write_text('# منابع\n\n'+'\n\n'.join(f'[{r["number"]}] {r["text"]}' for r in rows)+'\n')
        return rows
