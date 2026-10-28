"""Extend the thesis evidence audit to the integrated manuscript.

No ranking, new data evaluation, correlation or model inference is run.
The check validates source linkage, citations and preservation of released files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from build_thesis_evidence import build as original_ledger
from build_thesis_literature import build as literature
from check_supervisor_name import frozen_file_matches, check as check_supervisor_name

ROOT = Path(__file__).resolve().parents[1]
BASE = '3dff8ac1db62cb8759487b67df322d4b5b458e7d'
CHAPTERS = ['01_introduction_fa.md', '02_related_work_fa.md', '03_methods_fa.md',
            '04_controlled_framework_fa.md', '05_qmsum_gap_fa.md',
            '06_diagnostics_fa.md', '07_discussion_fa.md', '08_conclusion_fa.md']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build():
    ledger = original_ledger()
    ledger['manuscript_base_commit'] = BASE
    ledger['activity'] = 'integrated thesis synthesis; no new experiment'

    def ev(name, pointer):
        path = 'results/' + name + '.json'
        raw = (ROOT / path).read_bytes()
        ledger['source_sha256'][path] = sha(raw)
        value = json.loads(raw)
        for key in pointer.strip('/').split('/'):
            value = value[int(key)] if isinstance(value, list) else value[key]
        return {'path': path, 'json_pointer': pointer, 'value': value}

    p = json.loads((ROOT / 'results/phase17_summary.json').read_text())
    evidence = []
    for dataset, comparison in [('locomo','random_mean'), ('locomo','centered'), ('qmsum','random_mean')]:
        found = [i for i,r in enumerate(p[dataset]['contrasts'])
                 if r['budget_words'] == 1024 and r['comparison'] == comparison]
        assert len(found) == 1
        prefix = '/' + dataset + '/contrasts/' + str(found[0])
        evidence += [ev('phase17_summary', prefix + '/' + k)
                     for k in ['macro_difference','descriptive_cluster_bootstrap95','clusters']]
    ledger['claims'].append({'id':'C14', 'claim_fa':'اثر راهنمای مرز در فرصت‌های ثابت به آستانه‌ی عملی نرسید',
                              'status':'Phase17 locally planned exploratory comparison on reused data', 'evidence':evidence})
    ledger['claims'].append({'id':'C15', 'claim_fa':'دانه‌بندی مرجع میان منبع‌ها متفاوت است',
                              'status':'descriptive annotation audit, not semantic answer impossibility',
                              'evidence':[ev('phase19_diagnostics','/'+d+'/reference_granularity')
                                          for d in ['locomo','evermem']]})
    ledger['claims'].append({'id':'C16', 'claim_fa':'تقسیم اولیه‌ی توسعه و ارزیابی LoCoMo',
                              'status':'historical split; evaluation data subsequently reused',
                              'evidence':[ev('phase1_audit','/included_by_split')]})
    return ledger


def manifest():
    names = subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    names = [n for n in names if n.startswith(('results/','configs/','deliverables/'))
             or n in ['thesis/evidence_ledger.json','thesis/frozen_baseline_sha256.json',
                      'thesis/batch1_validation.json']]
    return {n:sha(subprocess.check_output(['git','show',BASE+':'+n],cwd=ROOT)) for n in names}


def check():
    folder = ROOT/'thesis'
    expected = json.loads((folder/'evidence_ledger_integrated.json').read_text())
    assert expected == build(), 'The integrated evidence ledger is stale'
    frozen = json.loads((folder/'batch2_frozen_sha256.json').read_text())
    for name,checksum in frozen.items():
        assert frozen_file_matches(name, checksum), 'Historical file changed: '+name
    review = json.loads((folder/'literature_review_20261027.json').read_text())
    assert review == literature(), 'Literature metadata differs from the curated record'
    ids = {s['id'] for s in review['sources']}
    assert ids == set(re.findall(r'@\w+\{(P\d+),', (folder/'references.bib').read_text()))
    text = '\n'.join((folder/'chapters'/n).read_text() for n in CHAPTERS)
    text += (folder/'front_matter_fa.md').read_text()+(folder/'abstract_en.md').read_text()+(folder/'appendices_fa.md').read_text()
    assert set(re.findall(r'\bP\d{2}\b',text)) == ids, 'Unknown or unused primary-source citation'
    claims = {r['id'] for r in expected['claims']}
    assert set(re.findall(r'\bC\d{2}\b',text)) <= claims, 'Unknown claim reference'
    assert not re.search(r'نوری\s+\u0648\u0644\u0646\u062f\u0647', text)
    assert 'ۀ' not in text and 'هٔ' not in text
    assert len(CHAPTERS) == 8
    check_supervisor_name()
    result = {'status':'passed','chapters':8,'claims':len(claims),'primary_sources':len(ids),
              'numeric_sources':len(expected['source_sha256']), 'frozen_files':len(frozen),
              'new_experiments':0,'new_correlations':0,'model_inference_calls':0}
    print(json.dumps(result))
    return result


def main():
    p = argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    if args.check:
        check()
    else:
        (ROOT/'thesis/evidence_ledger_integrated.json').write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n')
        (ROOT/'thesis/batch2_frozen_sha256.json').write_text(json.dumps(manifest(),indent=2)+'\n')
        print('Wrote integrated evidence ledger and preservation manifest')


if __name__=='__main__':main()
