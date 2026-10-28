"""Synthesize committed measurements without running a new experiment.

Every numeric claim retains exact JSON pointers and source SHA256. --check
rebuilds in memory, checks the ledger and verifies all frozen baseline files.
Only the Python standard library is required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from check_supervisor_name import frozen_file_matches

ROOT = Path(__file__).resolve().parents[1]
BASE = 'db76c5eb85c019c840ad76ace7e9aa5043fac283'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build():
    docs = {}
    refs = {}
    claims = []

    def source(name):
        path = 'results/' + name + '.json'
        if path not in docs:
            raw = (ROOT / path).read_bytes()
            docs[path] = json.loads(raw)
            refs[path] = digest(raw)
        return path, docs[path]

    def ev(name, pointer):
        path, data = source(name)
        for key in pointer.strip('/').split('/'):
            data = data[int(key)] if isinstance(data, list) else data[key]
        return {'path': path, 'json_pointer': pointer, 'value': data}

    def estimate(name, dataset, **filters):
        _, data = source(name)
        matches = [(i, e) for i, e in enumerate(data[dataset]['estimates'])
                   if all(e.get(k) == v for k, v in filters.items())]
        if len(matches) != 1:
            raise ValueError((name, dataset, filters, len(matches)))
        return '/' + dataset + '/estimates/' + str(matches[0][0])

    def claim(key, text, status, evidence):
        claims.append({'id': key, 'claim_fa': text, 'status': status,
                       'evidence': evidence})

    claim('C01', 'هم‌راستایی تقریبی مرز با آغاز موضوع در QMSum',
          'registered primary metric; tolerance two turns; meeting macro', [
          ev('phase10_summary', '/summary/boundary/2/online_macro'),
          ev('phase10_summary', '/summary/boundary/2/random_median')])
    claim('C02', 'برتری مشاهده‌شده به تلورانس وابسته است',
          'registered zero-tolerance sensitivity', [
          ev('phase10_summary', '/summary/boundary/0/online_macro'),
          ev('phase10_summary', '/summary/boundary/0/random_median')])
    claim('C03', 'هم‌راستایی تقریبی به مزیت پوشش در مسیر تخت تبدیل نشد',
          'Phase10 secondary retrieval outcome; budget 1024 source words', [
          ev('phase10_summary', '/summary/retrieval/1024/online'),
          ev('phase10_summary', '/summary/retrieval/1024/random_median'),
          ev('phase10_summary', '/summary/retrieval/1024/fixed')])
    claim('C04', 'مسیر دومرحله‌ای مزیت مورد انتظار را نشان نداد',
          'Phase11 primary outcome on reused data', [
          ev('phase11_summary', '/summary/budgets/1024/online/hier_gold'),
          ev('phase11_summary', '/summary/budgets/1024/random_hier_median'),
          ev('phase11_summary', '/summary/budgets/1024/online_minus_random_hier_median')])
    claim('C05', 'پوشش نامزد و خروجی نهایی فاصله دارند',
          'descriptive pipeline contrast; different source-word capacities', [
          ev('phase11_summary', '/summary/budgets/1024/online/candidate_gold'),
          ev('phase11_summary', '/summary/budgets/1024/online/hier_gold')])
    claim('C06', 'برخورد با حداقل یک شاهد و کسر پوشش می‌توانند جهت متفاوت داشته باشند',
          'explicitly post-result exploratory metric', [
          ev('phase11_posthoc_diagnostics', '/any_flat/online'),
          ev('phase11_posthoc_diagnostics', '/any_hier/online')])
    p = estimate('phase18_summary', 'locomo', method='writer', budget_words=1024)
    claim('C07', 'افراز تشخیصی شکست‌های LoCoMo در فضای ثابت',
          'exact annotation-relative audit; 599 questions; fixed geometry', [
          ev('phase18_summary', p + '/counts'),
          ev('phase18_summary', p + '/questions')])
    claim('C08', 'سقف دقیق و ظرفیت بهبود به قرارداد ثابت وابسته‌اند',
          'offline label-assisted oracle; not achieved retrieval performance', [
          ev('phase18_summary', p + '/oracle_all_complete_count'),
          ev('phase18_summary', p + '/macro_oracle_all_complete'),
          ev('phase18_summary', p + '/macro_all_complete'),
          ev('phase18_summary', '/locomo/writer_headroom_1024')])
    p = estimate('phase18_summary', 'qmsum', method='writer', budget_words=1024)
    claim('C09', 'پوشش کامل تمام بازه‌های QMSum غالبا در فضای ثابت ناممکن است',
          'secondary complete-span metric; distinct from partial-turn recall', [
          ev('phase18_summary', p + '/counts'),
          ev('phase18_summary', p + '/oracle_all_complete_count')])
    claim('C10', 'سیاست اصلی رزرو چهار جلسه قاعده‌ی ادامه را تامین نکرد',
          'locally registered primary comparison; weak manipulation', [
          ev('phase19_summary', '/decision/advance_condition_met'),
          ev('phase19_summary', '/locomo/contrasts/primary/macro_difference'),
          ev('phase19_summary', '/evermem/contrasts/primary/macro_difference')])
    for key, dataset in [('C11', 'locomo'), ('C12', 'evermem')]:
        evidence = []
        for policy in ['bm25', 'reserve8']:
            p = estimate('phase19_summary', dataset, policy=policy,
                         selector='writer', budget_words=1024)
            evidence.extend(ev('phase19_summary', p + '/' + metric) for metric in
                            ['all_sessions_count', 'all_evidence_count',
                             'exact_feasible_count', 'macro_primary_metric'])
        claim(key, 'افزایش دسترسی همراه با افت پوشش در ' + dataset,
              'reserve8 secondary dose; source-specific endpoint', evidence)
    claim('C13', 'رزرو هشت جلسه در پوشش از میانگین کنترل تعویض هم‌تعداد پایین‌تر بود',
          'Phase19B post-result exploratory amendment; seeds averaged within query', [
          ev('phase19b_summary', '/locomo/reserve8_minus_edit_control_mean/macro_difference'),
          ev('phase19b_summary', '/evermem/reserve8_minus_edit_control_mean/macro_difference'),
          ev('phase19b_summary', '/locomo/exact_expected_all_session_count'),
          ev('phase19b_summary', '/evermem/exact_expected_all_session_count')])
    # Check the central decomposition independently of its prose representation.
    c = claims[6]['evidence'][0]['value']
    assert sum(c.values()) == 599
    assert c['complete_success'] + c['feasible_selection_miss'] == 468
    assert c['missing_gold_session'] + c['window_geometry_infeasible'] == 131
    assert claims[9]['evidence'][0]['value'] is False
    return {'schema_version': 1, 'base_commit': BASE, 'date': '2026-10-27',
            'activity': 'synthesis of existing outputs; no new experiment',
            'source_sha256': refs, 'claims': claims}


def frozen_manifest():
    paths = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    selected = [p for p in paths if p.startswith(('results/', 'configs/', 'deliverables/'))
                or p in ['docs/phase10.md', 'docs/phase11.md', 'docs/phase18.md',
                         'docs/phase19.md', 'docs/phase19_research_note_en.md',
                         'docs/phase18_formal_contract.md']]
    return {p: digest(subprocess.check_output(['git', 'show', BASE + ':' + p], cwd=ROOT))
            for p in selected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    folder = ROOT / 'thesis'
    ledger = build()
    if args.check:
        expected = json.loads((folder / 'evidence_ledger.json').read_text())
        if ledger != expected:
            raise ValueError('The claim ledger differs from committed source measurements')
        manifest = json.loads((folder / 'frozen_baseline_sha256.json').read_text())
        for path, checksum in manifest.items():
            if not frozen_file_matches(path, checksum):
                raise ValueError('Historical file changed: ' + path)
        print(json.dumps({'status': 'passed', 'claims': len(ledger['claims']),
                          'source_files': len(ledger['source_sha256']),
                          'frozen_files': len(manifest), 'new_experiments': 0}))
    else:
        folder.mkdir(exist_ok=True)
        (folder / 'evidence_ledger.json').write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + '\n')
        (folder / 'frozen_baseline_sha256.json').write_text(
            json.dumps(frozen_manifest(), ensure_ascii=False, indent=2) + '\n')
        print('Wrote thesis evidence ledger and historical preservation manifest')


if __name__ == '__main__':
    main()
