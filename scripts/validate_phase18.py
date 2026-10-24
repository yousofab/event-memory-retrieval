"""Check Phase 18 numeric certificates against the frozen parent, without raw text.

The runner separately checks source labels and re-scores windows. This portable
validator checks the published geometry, certificates and historical identities;
it cannot establish semantic correctness of the original annotations.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

from run_baselines import ROOT
from run_phase17_fixed_anchors import allocate, fingerprint
from run_phase18_feasibility import CATEGORIES, summarize


def load(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def check_window(cells, widths, windows):
    assert len(windows) == len(cells) == len(widths) == 8
    for c, w, (s, a, b) in zip(cells, widths, windows):
        assert s == c['session'] and c['left'] <= a <= c['anchor'] < b <= c['right']
        assert b - a == w
        assert a <= c['required_left'] and b >= c['required_right']
    assert sum(b - a for s, a, b in windows) == sum(widths)


def validate(directory):
    plan = json.loads((ROOT / 'configs/phase18_plan.json').read_text())
    summary = json.loads((directory / 'phase18_summary.json').read_text())
    assert summary['plan_sha256'] == hashlib.sha256((ROOT / 'configs/phase18_plan.json').read_bytes()).hexdigest()
    for name, expected in summary['numeric_uncompressed_sha256'].items():
        assert hashlib.sha256(gzip.decompress((directory / name).read_bytes())).hexdigest() == expected
    parent_path = ROOT / plan['parent_rows_path']
    assert hashlib.sha256(parent_path.read_bytes()).hexdigest() == plan['parent_rows_compressed_sha256']
    parent = {(r['dataset'], r['sample_id'], r['question_index'], r['budget_words'], r['method']): r
              for r in load(parent_path)}
    queries = load(directory / 'phase18_queries.json.gz')
    rows = load(directory / 'phase18_rows.json.gz')
    assert len(queries) == 843 and len(rows) == 2529 and len(parent) == 55638
    query_map = {(q['dataset'], q['sample_id'], q['question_index']): q for q in queries}
    assert len(query_map) == len(queries)
    assert Counter(q['dataset'] for q in queries) == {'locomo': 599, 'qmsum': 244}
    thresholds_checked = 0
    for q in queries:
        cells = q['cells']
        assert len(cells) == 8 and q['nonempty_gold_turns'] > 0
        for c in cells:
            assert c['capacity'] == c['right'] - c['left']
            assert c['left'] <= c['required_left'] <= c['anchor'] < c['required_right'] <= c['right']
            assert c['required_width'] == c['required_right'] - c['required_left']
        n = q['minimum_total_budget']
        assert (n is None) == bool(q['missing_gold_sessions'])
        if n is not None:
            # Independent necessity/sufficiency check using the old slow allocator.
            assert 8 <= n <= sum(c['capacity'] for c in cells)
            widths = allocate(cells, n)
            assert all(w >= c['required_width'] for c, w in zip(cells, widths))
            assert any(w < c['required_width'] for c, w in zip(cells, allocate(cells, n - 1)))
            check_window(cells, widths, q['minimum_budget_witness'])
            thresholds_checked += 1
    identities, checked, witnesses = set(), 0, 0
    for r in rows:
        key = (r['dataset'], r['sample_id'], r['question_index'])
        identity = key + (r['budget_words'],)
        assert identity not in identities
        identities.add(identity)
        q = query_map[key]
        cells = q['cells']
        widths = allocate(cells, r['budget_words'])
        assert widths == r['cell_widths']
        assert sum(widths) == r['retrieved_words']
        stripped = [{k: c[k] for k in ['session', 'anchor', 'rank', 'left', 'right']} for c in cells]
        assert fingerprint([stripped, widths]) == r['opportunity_fingerprint']
        blockers = [i for i, (c, w) in enumerate(zip(cells, widths)) if w < c['required_width']]
        assert r['blocking_cells'] == blockers
        possible = not q['missing_gold_sessions'] and not blockers
        assert r['oracle_feasible'] == int(possible)
        assert possible == (q['minimum_total_budget'] is not None and r['budget_words'] >= q['minimum_total_budget'])
        assert (r['oracle_witness'] is not None) == possible
        if possible:
            check_window(cells, widths, r['oracle_witness'])
            witnesses += 1
        assert sorted(r['methods']) == sorted(plan['methods'])
        for method, metrics in r['methods'].items():
            old = parent[identity + (method,)]
            a, b, c = [metrics[k] for k in ['session_presence', 'all_turn_touch', 'all_complete']]
            assert all(v in (0, 1) for v in (a, b, c)) and c <= b <= a
            assert c <= int(possible)
            assert a == old['all_gold_sessions'] and c == old['all_evidence']
            assert old['retrieved_words'] == r['retrieved_words'] and old['opportunity_fingerprint'] == r['opportunity_fingerprint']
            expected = ('complete_success' if c else 'missing_gold_session' if q['missing_gold_sessions']
                        else 'window_geometry_infeasible' if not possible else 'feasible_selection_miss')
            assert metrics['category'] == expected and expected in CATEGORIES
            checked += 1
    recomputed = summarize(rows, queries, plan)
    assert all(summary[k] == recomputed[k] for k in ['locomo', 'qmsum', 'decision'])
    return {'phase': 18, 'queries': len(queries), 'query_budget_groups': len(rows),
        'historical_conditions_checked': checked, 'minimum_budget_thresholds_checked': thresholds_checked,
        'budget_witnesses_checked': witnesses, 'all_numeric_and_geometric_checks_passed': True,
        'source_label_scope': 'Source-to-geometry mapping is checked by the source-backed runner; this validator checks the stored geometry and frozen historical identities.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--directory', type=Path, default=ROOT / 'results')
    print(json.dumps(validate(p.parse_args().directory), indent=2))
