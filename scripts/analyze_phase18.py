"""Summarize the registered audit and draw figures without changing old results."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads(gzip.decompress((ROOT / 'results' / name).read_bytes()))


def analyze(plots=True):
    rows = read('phase18_rows.json.gz')
    queries = read('phase18_queries.json.gz')
    qmap = {(q['dataset'], q['sample_id'], q['question_index']): q for q in queries}
    detail = {}
    for dataset in ('locomo', 'qmsum'):
        primary = [r for r in rows if r['dataset'] == dataset and r['budget_words'] == 1024]
        metrics = [r['methods']['writer'] for r in primary]
        counts = Counter(m['category'] for m in metrics)
        failures = len(primary) - counts['complete_success']
        detail[dataset] = {
            'writer_1024_criterion_counts': {k: sum(m[k] for m in metrics)
                for k in ['session_presence', 'all_turn_touch', 'all_complete']},
            'writer_1024_failure_counts': dict(sorted(counts.items())),
            'structurally_unrecoverable_under_frozen_space': counts['missing_gold_session'] + counts['window_geometry_infeasible'],
            'structural_share_of_recorded_failures': (counts['missing_gold_session'] + counts['window_geometry_infeasible']) / failures,
            'annotation_proxy_gaps_in_queries': {
                'session_minus_complete': sum(m['session_presence'] - m['all_complete'] for m in metrics),
                'touch_minus_complete': sum(m['all_turn_touch'] - m['all_complete'] for m in metrics)},
            'feasible_writer_misses': [{k: r[k] for k in ['sample_id', 'question_index']} |
                {'minimum_total_budget': qmap[(r['dataset'], r['sample_id'], r['question_index'])]['minimum_total_budget']}
                for r in primary if r['methods']['writer']['category'] == 'feasible_selection_miss']}
    detail['scope'] = 'Descriptive breakdown of registered outcomes; this is not evidence of answer accuracy or annotation validity.'
    (ROOT / 'results/phase18_diagnostics.json').write_text(json.dumps(detail, indent=2) + '\n')
    if not plots:
        return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
    out = ROOT / 'figures/phase18'
    out.mkdir(parents=True, exist_ok=True)
    categories = ['complete_success', 'missing_gold_session', 'window_geometry_infeasible', 'feasible_selection_miss']
    colors = ['#264B65', '#87929F', '#D6A45B', '#218979']
    labels = ['Complete', 'Session absent', 'Window infeasible', 'Feasible miss']
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.8), layout='constrained', gridspec_kw={'wspace': .12})
    handles = None
    for ax, dataset, n in zip(axes, ('locomo', 'qmsum'), (599, 244)):
        budgets = [512, 1024, 2048]
        c = [Counter(r['methods']['writer']['category'] for r in rows
            if r['dataset'] == dataset and r['budget_words'] == b) for b in budgets]
        left = [0] * 3
        local_handles = []
        for category, color, label in zip(categories, colors, labels):
            vals = [counts[category] for counts in c]
            bars = ax.barh(range(3), vals, left=left, color=color, label=label, height=.58)
            local_handles.append(bars[0])
            for y, value, offset in zip(range(3), vals, left):
                if value >= n * .12:
                    ax.text(offset + value / 2, y, str(value), ha='center', va='center',
                        color='white' if category in ('complete_success', 'feasible_selection_miss') else '#111111', fontsize=10)
            left = [a + b for a, b in zip(left, vals)]
        handles = local_handles
        ax.set_yticks(range(3), [str(b) for b in budgets])
        ax.invert_yaxis();ax.set_xlim(0, n);ax.set_xlabel('Queries')
        ax.set_title(f'{"LoCoMo" if dataset == "locomo" else "QMSum"} (n={n})', fontsize=11)
        ax.set_ylabel('Word cap' if dataset == 'locomo' else '')
        ax.grid(axis='x', alpha=.17);ax.set_axisbelow(True)
    fig.legend(handles, labels, loc='outside lower center', ncol=2, frameon=False, fontsize=9.5)
    for ext in ('png', 'svg'):
        fig.savefig(out / ('failure_decomposition.' + ext), dpi=220, bbox_inches='tight')
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.8), layout='constrained', gridspec_kw={'wspace': .18})
    for ax, dataset, n in zip(axes, ('locomo', 'qmsum'), (599, 244)):
        finite = sorted(q['minimum_total_budget'] for q in queries
                        if q['dataset'] == dataset and q['minimum_total_budget'] is not None)
        x = [8] + finite + [16384]
        y = [0] + [(i + 1) / n for i in range(len(finite))] + [len(finite) / n]
        ax.step(x, y, where='post', color='#264B65', linewidth=2, label='Exact feasible coverage')
        observed = [sum(r['methods']['writer']['all_complete'] for r in rows
                        if r['dataset'] == dataset and r['budget_words'] == b) / n for b in (512, 1024, 2048)]
        ax.plot([512, 1024, 2048], observed, 'o', color='#218979', label='Recorded writer', markersize=5)
        ax.axvline(1024, color='#A1A6AA', linestyle='--', linewidth=.9)
        ax.set_xscale('log', base=2);ax.set_xlim(16, 16384);ax.set_ylim(0, 1.02)
        ax.set_xticks([32, 128, 512, 2048, 8192], ['32', '128', '512', '2048', '8192'])
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.set_xlabel('Total word cap (log scale)')
        ax.set_ylabel('Complete annotated coverage' if dataset == 'locomo' else '')
        ax.set_title('LoCoMo' if dataset == 'locomo' else 'QMSum', fontsize=11)
        ax.grid(alpha=.17)
    fig.legend(*axes[0].get_legend_handles_labels(), loc='outside lower center', ncol=2, frameon=False, fontsize=9.5)
    for ext in ('png', 'svg'):
        fig.savefig(out / ('minimum_budget_frontier.' + ext), dpi=220, bbox_inches='tight')
    plt.close(fig)
    equations = {
        'feasibility_equation': r'$F_q(B)=\mathbf{1}[S_G\subseteq S_A]\prod_{i=1}^{k}\mathbf{1}[w_i(B)\geq r_i]$',
        'minimum_budget_equation': r'$B_{\min}=\max_i\left[\sum_j\min(c_j,r_i-1)+\sum_{j\leq i}\mathbf{1}(c_j\geq r_i)\right]$'}
    for name, equation in equations.items():
        fig = plt.figure(figsize=(7.4, .72))
        fig.text(.5, .5, equation, ha='center', va='center', fontsize=15, color='black')
        for ext in ('png', 'svg'):
            fig.savefig(out / (name + '.' + ext), dpi=300, bbox_inches='tight', pad_inches=.12)
        plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-plots', action='store_true')
    analyze(not parser.parse_args().no_plots)
