"""Validate stored Phase 15 rows and both pre/post-result aggregates."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json

from run_baselines import ROOT
from run_phase15_role_retrieval import describe, METHODS, K_VALUES


def main():
    plan_path = ROOT / "configs/phase15_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    main_result = json.loads((ROOT / "results/phase15_summary.json").read_text(encoding="utf-8"))
    rows = json.loads(gzip.decompress((ROOT / "results/phase15_rows.json.gz").read_bytes()))
    extra = json.loads(gzip.decompress((ROOT / "results/phase15_budget.json.gz").read_bytes()))
    history = json.loads(gzip.decompress((ROOT / "results/phase15_history.json.gz").read_bytes()))
    assert main_result["protocol_sha256"] == extra["protocol_sha256"] == hashlib.sha256(plan_path.read_bytes()).hexdigest()
    assert main_result["source_commit"] == extra["source_commit"] == plan["source_commit"]
    assert extra["post_result_amendment_commit"] == "d96b154a3a8dc1bb99503e8fab7ffd9c2e73f1f3"
    assert len(main_result["group_stats"]) == 30
    assert sum(g["sessions"] for g in main_result["group_stats"]) == 27614
    assert sum(g["questions"] for g in main_result["group_stats"]) == 600
    assert all(g["assistant_only_words"] + g["user_only_words"] == g["role_corrected_words"]
               for g in main_result["group_stats"])
    assert len(rows) == 5400 and len(extra["rows"]) == 3600
    assert history["source_commit"] == plan["source_commit"]
    assert history["post_result_registration"] == "40377b91763ce64cd4b8786d3340badaa8d76487"
    assert history["history_questions"] == 156 and history["history_references"] == 755
    assert len(history["rows"]) == 156 * 3 * 5
    assert main_result["summary"] == describe(rows)
    keys = {(r["period"], r["persona"], r["question_id"]) for r in rows}
    assert len(keys) == 600
    by_key = Counter((r["period"], r["persona"], r["question_id"]) for r in rows)
    assert set(by_key.values()) == {9}
    assert all(r["method"] in METHODS and r["k"] in K_VALUES and r["active_found"] <= r["active_count"]
               and r["obsolete_found"] <= r["obsolete_count"] for r in rows)
    extra_rows = extra["rows"]
    assert {(r["period"], r["persona"], r["question_id"]) for r in extra_rows} == keys
    assert set(Counter((r["period"], r["persona"], r["question_id"]) for r in extra_rows).values()) == {6}
    assert all(r["method"] in METHODS and r["budget"] in (1024, 2048)
               and 0 <= r["spent_words"] <= r["budget"] and r["selected_sessions"] >= 0
               for r in extra_rows)
    for budget in (1024, 2048):
        pool = [r for r in extra_rows if r["budget"] == budget]
        result = extra["overview"][str(budget)]
        for method in METHODS:
            selected = [r for r in pool if r["method"] == method]
            for field, stats in result[method].items():
                values = [r[field] for r in selected if r[field] is not None]
                assert stats["eligible"] == len(values) and stats["sum"] == sum(values)
        pair = defaultdict(dict)
        for r in pool:
            if r["active_any"] is not None:
                pair[(r["period"], r["persona"], r["question_id"])][r["method"]] = r["active_any"]
        diff = [p["role_corrected"] - p["assistant_only"] for p in pair.values()]
        assert len(diff) == 398 and diff.count(1) == result["paired"]["corrected_only"]
        assert diff.count(-1) == result["paired"]["assistant_only"]
    # Structured outputs must contain no raw turn field or free-text question.
    assert all(r["history_count"] >= r["found_history"] and r["any_history"] == int(r["found_history"] > 0)
               for r in history["rows"])
    for obj in (main_result, rows, extra, history):
        text = json.dumps(obj, ensure_ascii=False)
        assert '"message"' not in text and '"question"' not in text
    print("Phase 15 validated: 600 keys, 30 groups, 5400 primary, 3600 budget, 2340 history rows")


if __name__ == "__main__":
    main()
