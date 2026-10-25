"""Label-blind anchor policies and an offline, policy-specific evidence audit.

The retriever consumes text, query and session metadata only. Exact bounds use
annotations after all practical window selections have been computed.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import time

from run_baselines import ROOT, sessions
from run_phase8_causal import online_segments
from run_phase17_fixed_anchors import (TurnIndex, allocate, anchor_cells, fingerprint,
    score_windows, select_windows, bootstrap_clusters)
from run_phase18_feasibility import (requirements, minimum_budget, feasible,
    witness_windows, classify, numeric_write)
from phase19_data import load_jobs

PLAN = ROOT / 'configs/phase19_plan.json'


def group_labels(pool, policy, identity):
    labels = [p['session'] for p in pool]
    if policy.startswith('sham_'):
        seed = int(policy.split('_')[1])
        material = f'phase19|{seed}|{identity}'.encode()
        random.Random(int.from_bytes(hashlib.sha256(material).digest(), 'big')).shuffle(labels)
    return labels


def select_anchors(pool, policy, identity, count=8):
    """Input is ranked source metadata only, with no reference/query-label channel."""
    if len(pool) < count or len({p['turn_index'] for p in pool}) != len(pool):
        raise ValueError('Insufficient or duplicate source candidates')
    if policy == 'bm25':
        return [p['turn_index'] for p in pool[:count]]
    if policy not in ('reserve4', 'reserve8') and not policy.startswith('sham_'):
        raise ValueError('Unknown policy')
    r = 8 if policy == 'reserve8' else 4
    labels = group_labels(pool, policy, identity)
    selected, seen = set(), set()
    for pos, label in enumerate(labels):
        if label not in seen:
            selected.add(pos)
            seen.add(label)
            if len(seen) == r:
                break
    for pos in range(len(pool)):
        if len(selected) == count:
            break
        selected.add(pos)
    return [pool[pos]['turn_index'] for pos in sorted(selected)]


def writer_maps(sample, settings):
    parts, reasons = online_segments(sample, settings)
    result = {s: [0] for s, _ in sessions(sample)}
    for part in parts:
        s = part['id'].split(':')[0]
        result[s].append(result[s][-1] + part['word_cost'])
    return {s: sorted(set(v)) for s, v in result.items()}, reasons


def practical_retrieve(index, query, maps, plan, identity):
    order = index.rank(query)
    pool = [{'turn_index': i, 'session': index.turns[i]['session'],
             'start': index.turns[i]['start'], 'end': index.turns[i]['end'],
             'anchor': (index.turns[i]['start'] + index.turns[i]['end'] - 1) // 2}
            for i in order[:plan['candidate_pool_turns']]]
    selections = {}
    for policy in plan['policies']:
        anchors = select_anchors(pool, policy, identity, plan['anchor_count'])
        cells = anchor_cells(index, anchors, plan['anchor_count'])
        returned = {}
        for budget in plan['budget_words']:
            widths = allocate(cells, budget)
            returned[budget] = {'widths': widths,
                'centered': select_windows(cells, widths),
                'writer': select_windows(cells, widths, maps)}
        selections[policy] = {'anchors': anchors, 'cells': cells, 'returned': returned}
    return pool, selections, fingerprint(order)


def mean_by_history(rows, getter):
    by = defaultdict(list)
    for row in rows:
        by[row['sample_id']].append(getter(row))
    return {h: statistics.mean(v) for h, v in sorted(by.items())}


def paired(values, seed=19, draws=2000):
    histories = sorted(values)
    loo = [statistics.mean(values[j] for j in histories if j != h) for h in histories]
    return {'macro_difference': statistics.mean(values.values()), 'per_history': values,
        'descriptive_cluster_bootstrap95': bootstrap_clusters(values, {k: k for k in values}, seed, draws),
        'leave_one_history_out_range': [min(loo), max(loo)], 'histories': len(values)}


def summarize(rows, plan):
    groups = defaultdict(list)
    lookup = {}
    for r in rows:
        groups[(r['dataset'], r['policy'], r['selector'], r['budget_words'])].append(r)
        lookup[(r['dataset'], r['sample_id'], r['question_id'], r['policy'], r['selector'], r['budget_words'])] = r
    out = {}
    for dataset in ('locomo', 'evermem'):
        metric = 'all_evidence' if dataset == 'locomo' else 'turn_recall'
        estimates = []
        for key, rs in sorted(groups.items()):
            d, policy, selector, budget = key
            if d != dataset:
                continue
            estimates.append({'policy': policy, 'selector': selector, 'budget_words': budget,
                'questions': len(rs), 'all_evidence_count': sum(r['all_evidence'] for r in rs),
                'exact_feasible_count': sum(r['oracle_feasible'] for r in rs),
                'all_sessions_count': sum(r['all_gold_sessions'] for r in rs),
                'macro_primary_metric': statistics.mean(mean_by_history(rs, lambda r: r[metric]).values()),
                'macro_turn_recall': statistics.mean(mean_by_history(rs, lambda r: r['turn_recall']).values()),
                'macro_word_recall': statistics.mean(mean_by_history(rs, lambda r: r['gold_word_recall']).values()),
                'macro_session_recall': statistics.mean(mean_by_history(rs, lambda r: r['gold_session_recall']).values()),
                'macro_all_sessions': statistics.mean(mean_by_history(rs, lambda r: r['all_gold_sessions']).values()),
                'macro_feasible': statistics.mean(mean_by_history(rs, lambda r: r['oracle_feasible']).values()),
                'mean_words': statistics.mean(r['retrieved_words'] for r in rs),
                'mean_selected_sessions': statistics.mean(r['selected_sessions'] for r in rs),
                'categories': dict(sorted(Counter(r['category'] for r in rs).items()))})
        baseline = groups[(dataset, 'bm25', 'writer', 1024)]
        contrasts = {}
        for name, target, compare, outcome in [
            ('primary', 'reserve4', 'bm25', metric),
            ('reserve8_secondary', 'reserve8', 'bm25', metric),
            ('access_secondary', 'reserve4', 'bm25', 'all_gold_sessions'),
            ('session_recall_secondary', 'reserve4', 'bm25', 'gold_session_recall'),
            ('feasibility_secondary', 'reserve4', 'bm25', 'oracle_feasible'),
            ('word_recall_secondary', 'reserve4', 'bm25', 'gold_word_recall')]:
            diffs = mean_by_history(baseline, lambda r: lookup[(dataset, r['sample_id'], r['question_id'], target, 'writer',1024)][outcome]
                - lookup[(dataset,r['sample_id'],r['question_id'],compare,'writer',1024)][outcome])
            contrasts[name] = paired(diffs, plan['uncertainty']['seed'], plan['uncertainty']['bootstrap_draws'])
        sham_policies = [p for p in plan['policies'] if p.startswith('sham_')]
        sham_diff = mean_by_history(baseline, lambda r:
            lookup[(dataset,r['sample_id'],r['question_id'],'reserve4','writer',1024)][metric]
            - statistics.mean(lookup[(dataset,r['sample_id'],r['question_id'],p,'writer',1024)][metric] for p in sham_policies))
        contrasts['reserve4_minus_sham_mean_secondary'] = paired(sham_diff)
        interaction = mean_by_history(baseline, lambda r:
            (lookup[(dataset,r['sample_id'],r['question_id'],'reserve4','writer',1024)][metric]
             - lookup[(dataset,r['sample_id'],r['question_id'],'reserve4','centered',1024)][metric])
            - (r[metric] - lookup[(dataset,r['sample_id'],r['question_id'],'bm25','centered',1024)][metric]))
        contrasts['anchor_by_boundary_interaction_secondary'] = paired(interaction)
        transitions = {}
        for field in ['all_gold_sessions','oracle_feasible','all_evidence']:
            transitions[field] = dict(Counter(
                f'{r[field]}->{lookup[(dataset,r["sample_id"],r["question_id"],"reserve4","writer",1024)][field]}'
                for r in baseline))
        costs = Counter()
        for r in baseline:
            for p in plan['policies'][1:]:
                if r['retrieved_words'] != lookup[(dataset,r['sample_id'],r['question_id'],p,'writer',1024)]['retrieved_words']:
                    costs[p] += 1
        out[dataset] = {'primary_outcome': metric, 'estimates': estimates,
            'contrasts': contrasts, 'primary_budget_transitions': transitions,
            'primary_budget_unequal_actual_cost_vs_bm25': dict(costs)}
    rule = plan['decision_rule']
    passes = all(out[d]['contrasts']['primary']['macro_difference'] >= rule['minimum_practical_difference']
        and out[d]['contrasts']['primary']['leave_one_history_out_range'][0] >= 0
        and out[d]['contrasts']['reserve4_minus_sham_mean_secondary']['macro_difference'] > 0
        for d in out)
    out['decision'] = {'advance_condition_met': passes,
                      'action': rule['advance_condition'] if passes else rule['otherwise']}
    return out


def run(output_dir):
    started = time.perf_counter()
    clean_at_start = not bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip())
    plan = json.loads(PLAN.read_text())
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.glob('phase19_*')):
        raise FileExistsError('Use a fresh directory; never overwrite recorded outcomes')
    prior_paths = sorted((ROOT / 'results').glob('*'))
    prior_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in prior_paths if p.is_file() and not p.name.startswith('phase19_')}
    jobs, data_audit = load_jobs(plan)
    parent = json.loads(gzip.decompress((ROOT / 'results/phase17_rows.json.gz').read_bytes()))
    parent = {(r['sample_id'],str(r['question_index']),r['budget_words'],r['method']):r
              for r in parent if r['dataset']=='locomo' and r['method'] in plan['selectors']}
    # Settings are taken from the registered causal writer, not reconstructed from prose.
    settings = json.loads((ROOT / 'configs/phase8_causal_plan.json').read_text())['causal_writer']
    rows, records, histories = [], [], []
    baseline_checks, witness_checks, threshold_checks = 0, 0, 0
    for dataset, sample, queries in jobs:
        index = TurnIndex(sample)
        maps, reasons = writer_maps(sample, settings)
        histories.append({'dataset':dataset, 'sample_id':sample['sample_id'],
                          'session_lengths':index.session_lengths, 'writer_closure_reasons':reasons})
        for qi, query, gold_ids in queries:
            if time.perf_counter() - started > plan['resources']['soft_stop_minutes'] * 60:
                raise RuntimeError('Registered compute soft stop reached; do not silently subsample')
            identity = f'{sample["sample_id"]}|{qi}'
            # Every practical choice is complete before annotations enter the audit.
            pool, selected, ranking_hash = practical_retrieve(index, query, maps, plan, identity)
            gold = [{k:index.by_id[g][k] for k in ('session','start','end')} for g in gold_ids]
            usable = [g for g in gold if g['end'] > g['start']]
            if not usable:
                raise ValueError('All gold turns empty')
            gold_sessions = {g['session'] for g in usable}
            pool_sessions = {p['session'] for p in pool}
            query_record = {'dataset':dataset,'sample_id':sample['sample_id'], 'question_id':qi,
                'gold_spans':gold, 'pool':pool, 'ranking_fingerprint':ranking_hash,
                'pool_all_gold_sessions':int(gold_sessions <= pool_sessions), 'policies':{}}
            for policy, selection in selected.items():
                cells = selection['cells']
                required, missing = requirements(cells, usable)
                threshold = None if missing else minimum_budget(required)
                if threshold is not None:
                    assert feasible(required, allocate(cells,threshold))
                    assert not feasible(required, allocate(cells,threshold-1))
                    threshold_checks += 1
                query_record['policies'][policy] = {'anchor_indices':selection['anchors'],
                    'cells':required, 'missing_gold_sessions':missing,'minimum_total_budget':threshold}
                for budget, returned in selection['returned'].items():
                    widths = returned['widths']
                    can = int(feasible(required,widths,missing))
                    witness = witness_windows(required,widths,missing)
                    if witness is not None:
                        assert score_windows(index,gold_ids,witness)['all_evidence'] == 1
                        witness_checks += 1
                    for selector in plan['selectors']:
                        windows = returned[selector]
                        scored = score_windows(index,gold_ids,windows)
                        found_sessions = {s for s,a,b in windows}
                        used = sum(b-a for s,a,b in windows)
                        expected = min(budget,sum(c['right']-c['left'] for c in cells))
                        assert used == sum(widths) == expected
                        assert scored['all_evidence'] <= can <= scored['all_gold_sessions'] <= query_record['pool_all_gold_sessions']
                        row = {'dataset':dataset,'sample_id':sample['sample_id'],'question_id':qi,
                            'policy':policy,'selector':selector,'budget_words':budget,
                            'retrieved_words':used,'selected_sessions':len(found_sessions),
                            'gold_session_recall':len(gold_sessions & found_sessions)/len(gold_sessions),
                            'windows':windows,'widths':widths,'oracle_feasible':can,
                            'category':classify(scored['all_evidence'],can,missing),**scored}
                        rows.append(row)
                        if dataset=='locomo' and policy=='bm25':
                            p = parent[(sample['sample_id'],qi,budget,selector)]
                            for field in ['all_evidence','turn_recall','gold_word_recall','retrieved_words','all_gold_sessions']:
                                assert row[field] == p[field], (identity,field)
                            assert fingerprint(windows) == fingerprint(p['windows'])
                            baseline_checks += 1
            records.append(query_record)
        print(f'Phase19 {dataset} {sample["sample_id"]}: {len(queries)} queries complete',flush=True)
    assert baseline_checks == 3594
    numeric_write(output_dir / 'phase19_queries.json.gz', {'histories':histories,'queries':records})
    numeric_write(output_dir / 'phase19_rows.json.gz', rows)
    summary = summarize(rows,plan)
    (output_dir / 'phase19_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    (output_dir / 'phase19_data_audit.json').write_text(json.dumps(data_audit,indent=2,sort_keys=True)+'\n')
    for name, expected in prior_hashes.items():
        assert hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest()==expected,name
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    assert peak < plan['resources']['peak_rss_gib_limit']*1024
    runtime = {'phase':19,'plan_sha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        'implementation_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        'git_clean_at_start_of_scoring':clean_at_start,
        'python':platform.python_version(),'elapsed_seconds':time.perf_counter()-started,'peak_rss_mib':peak,
        'queries':len(records),'rows':len(rows),'baseline_conditions_reproduced':baseline_checks,
        'finite_thresholds_checked':threshold_checks,'feasible_witnesses_rescored':witness_checks,
        'preserved_previous_result_files':len(prior_hashes),'commercial_api_calls':0,'gpu_calls':0,
        'source_backed_reproduction':'requires pinned raw data; portable certificates checked separately'}
    (output_dir/'phase19_runtime.json').write_text(json.dumps(runtime,indent=2,sort_keys=True)+'\n')
    print(json.dumps(runtime,indent=2))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    run(p.parse_args().output_dir)
