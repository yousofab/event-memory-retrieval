"""Independent recomputation of stored aggregate and source provenance checks."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import statistics

from run_baselines import ROOT
from run_phase16_boundaries import BUDGETS, METHODS, SEEDS, summarize


def main():
    summary = json.loads((ROOT / "results/phase16_summary.json").read_text(encoding="utf-8"))
    rows = json.loads(gzip.decompress((ROOT / "results/phase16_rows.json.gz").read_bytes()))
    plan = ROOT / "configs/phase16_boundary_plan.json"
    assert summary["plan_sha256"] == hashlib.sha256(plan.read_bytes()).hexdigest()
    assert summary["source_commit"] == json.loads(plan.read_text(encoding="utf-8"))["source_commit"]
    assert len(rows) == 600 * len(METHODS) * len(BUDGETS) == 12600
    assert len(summary["group_stats"]) == 30
    assert sum(g["sessions"] for g in summary["group_stats"]) == 27614
    assert sum(g["questions"] for g in summary["group_stats"]) == 600
    assert all(g["random_counts_equal"] and g["random_words_equal"] for g in summary["group_stats"])
    keys = Counter((r["period"], r["persona"], r["question_id"]) for r in rows)
    assert len(keys) == 600 and set(keys.values()) == {len(METHODS) * len(BUDGETS)}
    assert all(r["method"] in METHODS and r["budget_words"] in BUDGETS and
               0 <= r["retrieved_words"] <= r["budget_words"] and
               0 <= r["selected_sessions"] <= r["selected_documents"] for r in rows)
    assert all(r["active_any"] in (None, 0, 1) and r["obsolete_any"] in (None, 0, 1) for r in rows)
    assert all(r["active_any"] is None if r["active_count"] == 0 else r["active_any"] is not None
               for r in rows)
    assert all(r["obsolete_any"] is None if r["obsolete_count"] == 0 else r["obsolete_any"] is not None
               for r in rows)
    recomputed = summarize(rows, summary["group_stats"])
    assert summary["methods"] == recomputed["methods"]
    assert summary["primary"] == recomputed["primary"]
    for budget in BUDGETS:
        for seed in SEEDS:
            assert summary["methods"][f"random_{seed}/{budget}"]["active_eligible"] == 398
    # The whole-session full-role view must agree exactly with the Phase 15
    # corrected view under the two previously scored whole-word budgets.
    prior = json.loads(gzip.decompress((ROOT / "results/phase15_budget.json.gz").read_bytes()))
    for budget in (1024, 2048):
        old = [r for r in prior["rows"] if r["method"] == "role_corrected" and r["budget"] == budget]
        new = [r for r in rows if r["method"] == "session" and r["budget_words"] == budget]
        assert len(old) == len(new) == 600
        # Only the active evidence eligibility and success flags are compared;
        # phase 15 and 16 store group/order via different traversal sequences.
        by_key = {(r["period"], r["persona"], r["question_id"]): r for r in old}
        for r in new:
            a = by_key[r["period"], r["persona"], r["question_id"]]
            assert r["active_any"] == a["active_any"]
    for obj in (summary, rows):
        serialized = json.dumps(obj, ensure_ascii=False)
        assert '"message"' not in serialized and '"question"' not in serialized and '"answer"' not in serialized
    sensitivity = json.loads(gzip.decompress((ROOT / "results/phase16_equal_selected.json.gz").read_bytes()))
    assert sensitivity["source_commit"] == summary["source_commit"]
    assert sensitivity["plan_sha256"] == summary["plan_sha256"]
    assert sensitivity["amendment_sha256"] == hashlib.sha256(
        (ROOT / "docs/phase16_post_result_amendment.md").read_bytes()).hexdigest()
    assert sensitivity["amendment_remote_commit"] == "75e65685cc5ca92bb7c919de2c237f3226edf60e"
    extra = sensitivity["rows"]
    assert len(extra) == 398 * 6
    paired = defaultdict(dict)
    for r in extra:
        paired[(r["period"], r["persona"], r["question_id"])][r["method"]] = r
        assert r["retrieved_words"] <= 1024 and r["active_any"] in (0, 1)
    assert len(paired) == sensitivity["eligible"] == 398
    assert all(set(p) == set(METHODS[:-1]) and len({r["common_selected"] for r in p.values()}) == 1
               for p in paired.values())
    for method in METHODS[:-1]:
        chosen = [r for r in extra if r["method"] == method]
        assert sensitivity["methods"][method]["active_hits"] == sum(r["active_any"] for r in chosen)
    differences = [pair["writer"]["active_any"] -
                   statistics.mean(pair[f"random_{seed}"]["active_any"] for seed in SEEDS)
                   for pair in paired.values()]
    assert sensitivity["writer_minus_random_mean"] == round(statistics.mean(differences), 6)
    assert '"message"' not in json.dumps(sensitivity) and '"question"' not in json.dumps(sensitivity)
    print("Phase 16 validated: 30 groups, 600 questions, 12600 main rows, 2388 sensitivity rows and Phase 15 anchor")


if __name__ == "__main__":
    main()
