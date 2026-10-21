"""Boundary-conditioned context allocation with exactly paired opportunities.

The selector API receives text, a query and boundary maps, never evidence.
Only score_windows reads labels. Numeric outputs contain no source text.
"""
import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import sys
import time

from run_baselines import ROOT, sessions, words
from run_phase8_causal import online_segments
from run_phase10_topic_transfer import UniformCountSampler, sample_for
from fetch_phase10_data import verify

PLAN_PATH = ROOT / 'configs/phase17_plan.json'
METHODS = ['centered', 'writer'] + [f'random_{s:02}' for s in range(20)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class TurnIndex:
    def __init__(self, sample):
        self.turns, self.by_id, self.session_lengths = [], {}, {}
        for session, turns in sessions(sample):
            offset = 0
            for turn in turns:
                tokens = words(turn.get('text') or '')
                entry = {'id': turn['dia_id'], 'session': session,
                         'start': offset, 'end': offset + len(tokens),
                         'tf': Counter(tokens), 'length': len(tokens)}
                if entry['id'] in self.by_id:
                    raise ValueError('Duplicate source turn ID')
                self.by_id[entry['id']] = entry
                if tokens:
                    self.turns.append(entry)
                offset += len(tokens)
            self.session_lengths[session] = offset
        self.n = len(self.turns)
        self.average = max(sum(t['length'] for t in self.turns) / max(self.n, 1), 1)
        self.df = Counter(token for t in self.turns for token in t['tf'])

    def rank(self, query):
        terms = sorted(set(words(query)))
        scores = []
        for turn in self.turns:
            value = 0.0
            for token in terms:
                count = turn['tf'].get(token, 0)
                if count:
                    idf = math.log(1 + (self.n - self.df[token] + .5) / (self.df[token] + .5))
                    value += idf * count * 2.2 / (count + 1.2 * (.25 + .75 * turn['length'] / self.average))
            scores.append(value)
        return sorted(range(self.n), key=lambda i: (-scores[i], i))


def boundary_maps(sample, settings):
    writer, reasons = online_segments(sample, settings)
    target = Counter(part['id'].split(':')[0] for part in writer)
    maps = {m: {} for m in METHODS if m != 'centered'}
    for key, turns in sessions(sample):
        lengths = [len(words(t.get('text') or '')) for t in turns]
        offsets = [0]
        for length in lengths:
            offsets.append(offsets[-1] + length)
        parts = [p for p in writer if p['id'].split(':')[0] == key]
        ends, pos = [], 0
        for p in parts:
            pos += p['word_cost']
            ends.append(pos)
        maps['writer'][key] = sorted(set([0] + ends))
        if not turns:
            for seed in range(20):
                maps[f'random_{seed:02}'][key] = [0]
            continue
        sampler = UniformCountSampler(lengths, target[key], settings['maximum_segment_words'])
        for seed in range(20):
            cuts = sampler.draw(seed, f"phase17|{sample['sample_id']}|{key}")
            assert len(cuts) == len(parts)
            maps[f'random_{seed:02}'][key] = sorted(set([0] + [offsets[b] for a, b in cuts]))
    return maps, {'writer_segments': len(writer), 'closure_reasons': reasons,
                  'random_segments_each': len(writer)}


def anchor_cells(index, order, count=8):
    anchors = []
    for i in order[:count]:
        t = index.turns[i]
        anchors.append({'session': t['session'], 'anchor': (t['start'] + t['end'] - 1) // 2,
                        'rank': len(anchors)})
    grouped = defaultdict(list)
    for a in anchors:
        grouped[a['session']].append(a)
    for session, group in grouped.items():
        group.sort(key=lambda a: a['anchor'])
        edges = [0] + [(a['anchor'] + b['anchor']) // 2 + 1 for a, b in zip(group, group[1:])] + [index.session_lengths[session]]
        for i, a in enumerate(group):
            a.update(left=edges[i], right=edges[i + 1])
            assert a['left'] <= a['anchor'] < a['right']
    return anchors


def allocate(cells, budget):
    if budget <= 0:
        raise ValueError('Budget must be positive')
    widths = [0] * len(cells)
    remaining = min(budget, sum(c['right'] - c['left'] for c in cells))
    while remaining:
        for i, c in enumerate(cells):
            if widths[i] < c['right'] - c['left'] and remaining:
                widths[i] += 1
                remaining -= 1
    return widths


def candidate_bounds(cell, width):
    if not 0 < width <= cell['right'] - cell['left']:
        raise ValueError('Invalid window width')
    return max(cell['left'], cell['anchor'] - width + 1), min(cell['anchor'], cell['right'] - width)


def choose_window(cell, width, boundaries=None):
    lo, hi = candidate_bounds(cell, width)
    anchor = cell['anchor']
    if boundaries is None:
        start, end = cell['left'], cell['right']
    else:
        p = bisect_right(boundaries, anchor) - 1
        start, end = boundaries[p], boundaries[p + 1]
        assert start <= anchor < end
    def key(a):
        overlap = max(0, min(a + width, end) - max(a, start))
        return (-overlap, abs(2 * a + width - 1 - 2 * anchor), a)
    chosen = min(range(lo, hi + 1), key=key)
    return (cell['session'], chosen, chosen + width)


def select_windows(cells, widths, maps=None):
    return [choose_window(c, w, None if maps is None else maps[c['session']])
            for c, w in zip(cells, widths) if w]


def score_windows(index, gold_ids, windows):
    gold = [index.by_id[t] for t in gold_ids]
    empty = sum(t['length'] == 0 for t in gold)
    gold = [t for t in gold if t['length']]
    if not gold:
        raise ValueError('No nonempty gold turn')
    by_session = defaultdict(list)
    for sid, start, end in windows:
        by_session[sid].append((start, end))
    lengths, complete = [], 0
    for t in gold:
        covered = sum(max(0, min(end, t['end']) - max(start, t['start']))
                      for start, end in by_session[t['session']])
        assert covered <= t['length']
        lengths.append(covered)
        complete += covered == t['length']
    sessions_gold = {t['session'] for t in gold}
    return {'all_evidence': int(complete == len(gold)), 'any_evidence': int(complete > 0),
            'evidence_found': complete, 'evidence_total': len(gold), 'empty_gold_turns': empty,
            'turn_recall': complete / len(gold),
            'gold_word_recall': sum(lengths) / sum(t['length'] for t in gold),
            'all_gold_sessions': int(sessions_gold <= by_session.keys()),
            'gold_session_count': len(sessions_gold)}


def source_family(name):
    if name.startswith(('ES', 'IS', 'TS')):
        return name[:-1]
    if name.startswith(('Bed', 'Bmr', 'Bro')):
        return name[:3]
    return name.split('_')[0]


def bootstrap_clusters(values, families, seed=17, draws=2000):
    groups = defaultdict(list)
    for key, value in values.items():
        groups[families[key]].append(value)
    keys = sorted(groups)
    rng = random.Random(seed)
    estimates = []
    for _ in range(draws):
        selected = [v for k in rng.choices(keys, k=len(keys)) for v in groups[k]]
        estimates.append(statistics.mean(selected))
    estimates.sort()
    def quantile(p):
        x = (len(estimates) - 1) * p
        a = int(x)
        return estimates[a] + (estimates[min(a + 1, len(estimates)-1)] - estimates[a]) * (x-a)
    return [quantile(.025), quantile(.975)]


def summarize(rows):
    result = {}
    for dataset in sorted({r['dataset'] for r in rows}):
        subset = [r for r in rows if r['dataset'] == dataset]
        metric = 'all_evidence' if dataset == 'locomo' else 'turn_recall'
        estimates, cluster_values = [], {}
        for budget in [512, 1024, 2048]:
            for method in METHODS:
                selected = [r for r in subset if r['budget_words'] == budget and r['method'] == method]
                by = defaultdict(list)
                for r in selected:
                    by[r['sample_id']].append(r[metric])
                means = {k: statistics.mean(v) for k, v in by.items()}
                cluster_values[(budget, method)] = means
                estimates.append({'budget_words': budget, 'method': method, 'questions':len(selected),
                    'all_evidence_count':sum(r['all_evidence'] for r in selected),
                    'any_evidence_count':sum(r['any_evidence'] for r in selected),
                    'macro_metric':statistics.mean(means.values()),
                    'mean_gold_word_recall':statistics.mean(r['gold_word_recall'] for r in selected),
                    'mean_words':statistics.mean(r['retrieved_words'] for r in selected),
                    'mean_windows':statistics.mean(r['selected_windows'] for r in selected),
                    'mean_sessions':statistics.mean(r['selected_sessions'] for r in selected),
                    'changed_from_centered_queries':sum(r['windows_changed'] > 0 for r in selected)})
        contrasts = []
        for budget in [512, 1024, 2048]:
            writer = cluster_values[(budget, 'writer')]
            families = {k:(k if dataset == 'locomo' else source_family(k)) for k in writer}
            for comparison in ['random_mean', 'centered']:
                difference = {k:writer[k] - (statistics.mean(cluster_values[(budget,m)][k] for m in METHODS[2:])
                              if comparison == 'random_mean' else cluster_values[(budget,'centered')][k]) for k in writer}
                contrasts.append({'budget_words':budget, 'comparison':comparison,
                    'macro_difference':statistics.mean(difference.values()),
                    'descriptive_cluster_bootstrap95':bootstrap_clusters(difference, families),
                    'clusters':len(set(families.values())), 'per_sample_differences':difference})
        result[dataset] = {'metric':metric, 'estimates':estimates, 'contrasts':contrasts}
    return result


def run(output_dir):
    started = time.perf_counter()
    plan = json.loads(PLAN_PATH.read_text())
    if (output_dir / 'phase17_rows.json.gz').exists():
        raise FileExistsError('Use a fresh output directory; never overwrite recorded outcomes')
    source = ROOT / 'data/raw/locomo10.json'
    assert digest(source) == plan['primary_source']['sha256']
    manifest = json.loads((ROOT / 'results/phase1_audit.json').read_text())
    qmanifest = json.loads((ROOT / 'configs/phase10_source_manifest.json').read_text())
    qdir = ROOT / 'data/raw/qmsum_test'
    counts = verify(qdir, qmanifest)
    assert counts['specific_queries'] == 244 and counts['meetings'] == 35
    settings = json.loads((ROOT / 'configs/phase8_causal_plan.json').read_text())['causal_writer']
    jobs = []
    for sample in json.loads(source.read_text()):
        questions = [q for q in manifest['manifest'] if q['sample_id'] == sample['sample_id'] and q['split'] == 'held_out']
        if questions:
            jobs.append(('locomo', sample, [(q['question_index'], sample['qa'][q['question_index']]['question'],
                          q['evidence_ids']) for q in questions]))
    for item in qmanifest['files']:
        raw = json.loads((qdir / item['name']).read_text())
        name = Path(item['name']).stem
        queries = []
        for i, q in enumerate(raw['specific_query_list']):
            gold = sorted({t for a,b in q['relevant_text_span'] for t in range(int(a), int(b)+1)})
            queries.append((i, q['query'], gold))
        jobs.append(('qmsum', sample_for(name, raw), queries))
    assert sum(len(q) for d,s,q in jobs if d == 'locomo') == 599
    rows, stats, timing = [], [], Counter()
    for dataset, sample, queries in jobs:
        t = time.perf_counter()
        index = TurnIndex(sample)
        timing['index_seconds'] += time.perf_counter() - t
        t = time.perf_counter()
        maps, boundary_stats = boundary_maps(sample, settings)
        timing['boundaries_and_controls_seconds'] += time.perf_counter() - t
        stats.append({'dataset':dataset,'sample_id':sample['sample_id'], 'indexed_turns':index.n,
                      'source_words':sum(index.session_lengths.values()), **boundary_stats})
        for qi, query, gold in queries:
            if dataset == 'locomo' and any(index.by_id[g]['length'] == 0 for g in gold):
                raise ValueError('Empty LoCoMo evidence violates frozen contract')
            t = time.perf_counter()
            order = index.rank(query)
            cells = anchor_cells(index, order)
            timing['shared_ranking_seconds'] += time.perf_counter() - t
            for budget in plan['budgets_words']:
                widths = allocate(cells, budget)
                centered = select_windows(cells, widths)
                common = {'dataset':dataset,'sample_id':sample['sample_id'], 'question_index':qi,
                          'budget_words':budget,'retrieved_words':sum(widths), 'selected_windows':sum(w>0 for w in widths),
                          'selected_sessions':len({c['session'] for c,w in zip(cells,widths) if w}),
                          'candidate_windows':sum(hi-lo+1 for c,w in zip(cells,widths) if w for lo,hi in [candidate_bounds(c,w)]),
                          'opportunity_fingerprint':fingerprint([cells,widths]), 'cell_widths':widths}
                assert sum(widths) == min(budget,sum(c['right']-c['left'] for c in cells))
                for method in METHODS:
                    t = time.perf_counter()
                    windows = select_windows(cells,widths,None if method == 'centered' else maps[method])
                    timing[f'select_{method}_seconds'] += time.perf_counter() - t
                    assert sum(b-a for s,a,b in windows) == sum(widths)
                    for c,w,(s,a,b) in zip(cells,widths,windows):
                        assert s == c['session'] and c['left'] <= a <= c['anchor'] < b <= c['right'] and b-a == w
                    metrics = score_windows(index,gold,windows)
                    rows.append({**common,'method':method,**metrics,
                                 'windows_changed':sum(a!=b for a,b in zip(windows,centered)),
                                 'windows':windows})
        print(dataset,sample['sample_id'],len(queries),'queries completed',flush=True)
    assert len(rows) == (599+244)*22*3
    summary = summarize(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
    with (output_dir/'phase17_rows.json.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='') as z:
            z.write(raw)
    summary.update({'phase':17,'plan_sha256':digest(PLAN_PATH),
        'protocol_commit':subprocess.check_output(['git','log','-1','--format=%H','--','configs/phase17_plan.json'],cwd=ROOT,text=True).strip(),
        'locomo_sha256':digest(source),'qmsum_manifest_sha256':digest(ROOT/'configs/phase10_source_manifest.json'),
        'rows':len(rows),'numeric_rows_sha256':hashlib.sha256(raw).hexdigest(),'source_stats':stats,
        'timing_seconds':dict(timing),'total_wall_seconds':time.perf_counter()-started,
        'peak_rss_mib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        'environment':{'python':sys.version,'platform':platform.platform(),'processor':platform.processor()},
        'interpretation':'Exploratory reused datasets; complete annotated turn coverage, not answer accuracy. No public preregistration.'})
    (output_dir/'phase17_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({d:summary[d]['contrasts'][:2] for d in ['locomo','qmsum']},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args = parser.parse_args()
    sys.setrecursionlimit(10000)
    run(args.output_dir)
