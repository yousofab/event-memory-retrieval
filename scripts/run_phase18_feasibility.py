"""Offline, annotation-assisted exact audit of the frozen Phase 17 window space.

This is not a deployable retriever. Source roles, ranking and historical windows
are unchanged. Gold labels enter only the diagnostic after anchor construction.
The core uses the Python standard library and no answer model or judge.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

from run_baselines import ROOT
from fetch_phase10_data import verify
from run_phase10_topic_transfer import sample_for
from run_phase17_fixed_anchors import (TurnIndex, anchor_cells, allocate,
    candidate_bounds, fingerprint, score_windows, source_family, bootstrap_clusters)

PLAN = ROOT / 'configs/phase18_plan.json'
CATEGORIES = ['complete_success', 'missing_gold_session',
              'window_geometry_infeasible', 'feasible_selection_miss']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requirements(cells, gold):
    """Smallest in-cell interval containing the anchor and all annotated words."""
    if not cells:
        raise ValueError('No anchor cells')
    usable = [t for t in gold if t['end'] > t['start']]
    if not usable:
        raise ValueError('No nonempty annotated turn')
    available = {c['session'] for c in cells}
    missing = sorted({t['session'] for t in usable} - available)
    result = []
    for c in cells:
        if not c['left'] <= c['anchor'] < c['right']:
            raise ValueError('Invalid anchor geometry')
        pieces = [(max(c['left'], t['start']), min(c['right'], t['end']))
                  for t in usable if t['session'] == c['session']
                  and max(c['left'], t['start']) < min(c['right'], t['end'])]
        lo = min([c['anchor']] + [a for a, b in pieces])
        hi = max([c['anchor'] + 1] + [b for a, b in pieces])
        result.append({**c, 'capacity': c['right'] - c['left'],
                       'required_left': lo, 'required_right': hi,
                       'required_width': hi - lo})
    return result, missing


def minimum_budget(required):
    """Position of the last required allocation event, in the frozen RR order."""
    if not required:
        raise ValueError('No cells')
    capacities = [c['capacity'] for c in required]
    positions = []
    for i, c in enumerate(required):
        r = c['required_width']
        if not 1 <= r <= capacities[i]:
            raise ValueError('Invalid required width')
        positions.append(sum(min(cap, r - 1) for cap in capacities)
                         + sum(cap >= r for cap in capacities[:i + 1]))
    return max(positions)


def feasible(required, widths, missing=()):
    if len(required) != len(widths):
        raise ValueError('Width count differs from cell count')
    return not missing and all(w >= c['required_width']
                               for c, w in zip(required, widths))


def witness_windows(required, widths, missing=()):
    """Construct legal successful windows, or None with the exact infeasible flag."""
    if not feasible(required, widths, missing):
        return None
    result = []
    for c, w in zip(required, widths):
        lo, hi = candidate_bounds(c, w)
        lo = max(lo, c['required_right'] - w)
        hi = min(hi, c['required_left'])
        assert lo <= hi
        mid = (2 * c['anchor'] - w + 1) // 2
        starts = {lo, hi, max(lo, min(hi, mid)), max(lo, min(hi, mid + 1))}
        a = min(starts, key=lambda a: (abs(2 * a + w - 1 - 2 * c['anchor']), a))
        result.append((c['session'], a, a + w))
    return result


def turn_touch(index, gold_ids, windows):
    gold = [index.by_id[t] for t in gold_ids if index.by_id[t]['length']]
    found = sum(any(s == t['session'] and max(a, t['start']) < min(b, t['end'])
                    for s, a, b in windows) for t in gold)
    return int(found == len(gold))


def classify(complete, can_cover, missing):
    if complete:
        if not can_cover:
            raise AssertionError('Recorded success exceeds the exact bound')
        return 'complete_success'
    if missing:
        return 'missing_gold_session'
    if not can_cover:
        return 'window_geometry_infeasible'
    return 'feasible_selection_miss'


def load_jobs(plan):
    source = ROOT / plan['data']['locomo']['path']
    assert digest(source) == plan['data']['locomo']['sha256']
    manifest = json.loads((ROOT / plan['data']['locomo']['question_manifest']).read_text())
    jobs = []
    for sample in json.loads(source.read_text()):
        records = [r for r in manifest['manifest']
                   if r['sample_id'] == sample['sample_id'] and r['split'] == 'held_out']
        if records:
            jobs.append(('locomo', sample, [(r['question_index'],
                sample['qa'][r['question_index']]['question'], r['evidence_ids']) for r in records]))
    manifest = json.loads((ROOT / plan['data']['qmsum']['manifest']).read_text())
    qdir = ROOT / plan['data']['qmsum']['path']
    counts = verify(qdir, manifest)
    assert counts['meetings'] == 35 and counts['specific_queries'] == 244
    for item in manifest['files']:
        raw = json.loads((qdir / item['name']).read_text())
        name = Path(item['name']).stem
        queries = [(i, q['query'], sorted({t for a, b in q['relevant_text_span']
                   for t in range(int(a), int(b) + 1)}))
                   for i, q in enumerate(raw['specific_query_list'])]
        jobs.append(('qmsum', sample_for(name, raw), queries))
    return jobs


def numeric_write(path, obj):
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    with path.open('wb') as f:
        with gzip.GzipFile(fileobj=f, mode='wb', filename='', mtime=0) as z:
            z.write(raw)
    return hashlib.sha256(raw).hexdigest()


def quantile(values, p):
    values = sorted(values)
    if not values:
        return None
    x = (len(values) - 1) * p
    i = int(x)
    return values[i] + (values[min(i + 1, len(values) - 1)] - values[i]) * (x - i)


def macro(selected, getter):
    groups = defaultdict(list)
    for r in selected:
        groups[r['sample_id']].append(getter(r))
    return statistics.mean(statistics.mean(v) for v in groups.values())


def summarize(rows, queries, plan):
    result = {}
    for dataset in ('locomo', 'qmsum'):
        estimates = []
        for budget in plan['budget_words']:
            selected = [r for r in rows if r['dataset'] == dataset and r['budget_words'] == budget]
            oracle_count = sum(r['oracle_feasible'] for r in selected)
            for method in plan['methods']:
                cats = Counter(r['methods'][method]['category'] for r in selected)
                estimates.append({'budget_words': budget, 'method': method,
                    'questions': len(selected), 'counts': {k: cats[k] for k in CATEGORIES},
                    'oracle_all_complete_count': oracle_count,
                    'macro_oracle_all_complete': macro(selected, lambda r: r['oracle_feasible']),
                    'macro_session_presence': macro(selected, lambda r: r['methods'][method]['session_presence']),
                    'macro_all_turn_touch': macro(selected, lambda r: r['methods'][method]['all_turn_touch']),
                    'macro_all_complete': macro(selected, lambda r: r['methods'][method]['all_complete']),
                    'macro_headroom': macro(selected, lambda r: r['oracle_feasible'] - r['methods'][method]['all_complete'])})
        selected = [r for r in rows if r['dataset'] == dataset and r['budget_words'] == plan['primary_budget_words']]
        groups = defaultdict(list)
        for r in selected:
            groups[r['sample_id']].append(r['oracle_feasible'] - r['methods']['writer']['all_complete'])
        values = {k: statistics.mean(v) for k, v in groups.items()}
        families = {k: k if dataset == 'locomo' else source_family(k) for k in values}
        q = [r for r in queries if r['dataset'] == dataset]
        finite = [r['minimum_total_budget'] for r in q if r['minimum_total_budget'] is not None]
        result[dataset] = {'estimates': estimates,
            'writer_headroom_1024': {'macro_difference': statistics.mean(values.values()),
                'descriptive_cluster_bootstrap95': bootstrap_clusters(values, families,
                    seed=plan['uncertainty']['seed'], draws=plan['uncertainty']['draws']),
                'per_history': values, 'clusters': len(set(families.values()))},
            'minimum_budget': {'finite_queries': len(finite), 'missing_session_queries': len(q) - len(finite),
                'minimum': min(finite) if finite else None, 'median': quantile(finite, .5),
                'p90': quantile(finite, .9), 'maximum': max(finite) if finite else None}}
    theta = plan['decision_rule']['practical_headroom_percentage_points'] / 100
    gap = result['locomo']['writer_headroom_1024']['macro_difference']
    result['decision'] = {'headroom_below_two_points': gap < theta,
        'action': plan['decision_rule']['if_below'] if gap < theta else plan['decision_rule']['if_at_or_above']}
    return result


def run(output_dir):
    started = time.perf_counter()
    plan = json.loads(PLAN.read_text())
    names = ['phase18_queries.json.gz', 'phase18_rows.json.gz', 'phase18_summary.json']
    if any((output_dir / name).exists() for name in names):
        raise FileExistsError('Use a fresh directory; preserve recorded outcomes')
    assert digest(ROOT / plan['parent_rows_path']) == plan['parent_rows_compressed_sha256']
    assert digest(ROOT / plan['parent_plan_path']) == plan['parent_plan_sha256']
    original = json.loads(gzip.decompress((ROOT / plan['parent_rows_path']).read_bytes()))
    groups = defaultdict(list)
    for r in original:
        groups[(r['dataset'], r['sample_id'], r['question_index'], r['budget_words'])].append(r)
    queries, rows = [], []
    checked = 0
    for dataset, sample, jobs in load_jobs(plan):
        index = TurnIndex(sample)
        for qi, query, gold_ids in jobs:
            cells = anchor_cells(index, index.rank(query), count=plan['anchor_count'])
            assert len(cells) == plan['anchor_count']
            gold = [index.by_id[g] for g in gold_ids]
            required, missing = requirements(cells, gold)
            threshold = None if missing else minimum_budget(required)
            identity = {'dataset': dataset, 'sample_id': sample['sample_id'], 'question_index': qi}
            qrecord = {**identity, 'cells': required, 'missing_gold_sessions': missing,
                'nonempty_gold_turns': sum(t['length'] > 0 for t in gold),
                'empty_gold_turns': sum(t['length'] == 0 for t in gold),
                'gold_session_count': len({t['session'] for t in gold if t['length']}),
                'minimum_total_budget': threshold}
            if threshold is not None:
                w = allocate(cells, threshold)
                witness = witness_windows(required, w)
                assert witness is not None and score_windows(index, gold_ids, witness)['all_evidence'] == 1
                assert not feasible(required, allocate(cells, threshold - 1))
                qrecord['minimum_budget_witness'] = witness
            queries.append(qrecord)
            for budget in plan['budget_words']:
                widths = allocate(cells, budget)
                possible = int(feasible(required, widths, missing))
                assert possible == int(threshold is not None and budget >= threshold)
                witness = witness_windows(required, widths, missing)
                if witness is not None:
                    assert score_windows(index, gold_ids, witness)['all_evidence'] == 1
                row = {**identity, 'budget_words': budget, 'cell_widths': widths,
                    'retrieved_words': sum(widths), 'oracle_feasible': possible,
                    'opportunity_fingerprint': fingerprint([cells, widths]),
                    'blocking_cells': [i for i, (c, w) in enumerate(zip(required, widths)) if w < c['required_width']],
                    'oracle_witness': witness, 'methods': {}}
                old = groups[(dataset, sample['sample_id'], qi, budget)]
                assert sorted(r['method'] for r in old) == sorted(plan['methods'])
                for r in old:
                    assert r['opportunity_fingerprint'] == row['opportunity_fingerprint']
                    assert r['cell_widths'] == widths and r['retrieved_words'] == sum(widths)
                    for c, w, (s, a, b) in zip(cells, widths, r['windows']):
                        lo, hi = candidate_bounds(c, w)
                        assert s == c['session'] and lo <= a <= hi and b - a == w
                    metrics = score_windows(index, gold_ids, r['windows'])
                    assert all(metrics[k] == r[k] for k in metrics)
                    touch = turn_touch(index, gold_ids, r['windows'])
                    assert metrics['all_evidence'] <= touch <= metrics['all_gold_sessions']
                    row['methods'][r['method']] = {'session_presence': metrics['all_gold_sessions'],
                        'all_turn_touch': touch, 'all_complete': metrics['all_evidence'],
                        'category': classify(metrics['all_evidence'], possible, missing)}
                    checked += 1
                rows.append(row)
        print(dataset, sample['sample_id'], len(jobs), 'queries audited', flush=True)
    assert len(queries) == 843 and len(rows) == 2529 and checked == len(original) == 55638
    assert len(groups) == len(rows)
    summary = summarize(rows, queries, plan)
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes = {names[0]: numeric_write(output_dir / names[0], queries),
              names[1]: numeric_write(output_dir / names[1], rows)}
    summary.update({'phase': 18, 'plan_sha256': digest(PLAN),
        'registration_commit': subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', str(PLAN)], cwd=ROOT, text=True).strip(),
        'run_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'parent_rows_compressed_sha256': digest(ROOT / plan['parent_rows_path']),
        'locomo_sha256': digest(ROOT / plan['data']['locomo']['path']),
        'qmsum_manifest_sha256': digest(ROOT / plan['data']['qmsum']['manifest']),
        'queries': len(queries), 'query_budget_groups': len(rows), 'historical_conditions_rescored': checked,
        'numeric_uncompressed_sha256': hashes, 'total_wall_seconds': time.perf_counter() - started,
        'peak_rss_mib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'environment': {'python': sys.version, 'platform': platform.platform()},
        'interpretation': 'Exact only inside the frozen legal window space and relative to supplied annotations; exploratory reused-data diagnostic, no answer-accuracy evaluation.'})
    (output_dir / names[2]).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({d: summary[d]['writer_headroom_1024'] for d in ('locomo', 'qmsum')}, indent=2))
    print(json.dumps(summary['decision'], indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output-dir', type=Path, default=ROOT / 'results')
    run(p.parse_args().output_dir)
