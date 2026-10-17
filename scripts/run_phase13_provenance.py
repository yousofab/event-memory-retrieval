"""Phase 13: test one-step session diversity without gold in ranking.

Uses the unchanged Phase 12 tokenization, BM25 and whole-turn budget contract.
The official answer-session metadata is read only by the scoring function.
"""
import argparse
import gzip
import json
import random
import statistics
from pathlib import Path

from run_baselines import ROOT, rank
from run_phase12_temporal import public_turns, pick, score_record, source_sha


def methods(lexical, turns, qid, k=20, seeds=20):
    assert len(lexical) >= k and len(set(lexical)) == len(lexical)
    head = lexical[:k]
    first = head[0]
    other = [i for i in head[1:] if turns[i]["session_position"] != turns[first]["session_position"]]

    def promote(candidate):
        return [first, candidate] + [i for i in lexical if i != first and i != candidate]

    result = {"bm25_turn": lexical,
              "best_other_session_second": promote(other[0]) if other else lexical.copy(),
              "newest_other_session_second": promote(max(other, key=lambda i: (
                  turns[i]["session_position"], turns[i]["turn_position"], -lexical.index(i))))
              if other else lexical.copy()}
    for seed in range(seeds):
        candidate = random.Random(f"phase13:{qid}:{seed}").choice(other) if other else None
        result[f"random_other_session_second:{seed}"] = promote(candidate) if candidate is not None else lexical.copy()
    for order in result.values():
        assert len(order) == len(lexical) and set(order) == set(lexical)
        assert order[0] == first
        if other and order is not result["bm25_turn"]:
            assert order[1] in other
            assert [i for i in order[2:] if i not in (first, order[1])] == [
                i for i in lexical if i not in (first, order[1])]
    return result, bool(other)


def compact(rows, method, budget):
    x = [r for r in rows if r["method"] == method and r["budget_words"] == budget]
    assert len(x) == 72
    eligible = [r for r in x if r["older_marked_available"]]
    assert len(eligible) == 70
    return {"all_questions": 72, "paired_eligible": 70,
            "both_found_eligible": sum(r["both_found"] for r in eligible),
            "later_found_all": sum(r["later_found"] for r in x),
            "older_only_eligible": sum(r["older_only"] for r in eligible),
            "mean_spent_words": round(statistics.mean(r["spent_words"] for r in x), 2)}


def summary(rows, plan, changed):
    budgets = [plan["primary_budget_words"], *plan["secondary_budgets_words"]]
    output = {}
    for budget in budgets:
        bm = compact(rows, "bm25_turn", budget)
        best = compact(rows, "best_other_session_second", budget)
        newest = compact(rows, "newest_other_session_second", budget)
        shuffles = [compact(rows, f"random_other_session_second:{seed}", budget)
                    for seed in range(plan["random_other_session_seeds"])]
        output[str(budget)] = {"bm25_turn": bm, "best_other_session_second": best,
                               "newest_other_session_second": newest,
                               "random_both_by_seed": [z["both_found_eligible"] for z in shuffles],
                               "random_both_median": statistics.median(z["both_found_eligible"] for z in shuffles),
                               "best_minus_bm25": best["both_found_eligible"] - bm["both_found_eligible"],
                               "best_minus_random_median": best["both_found_eligible"] -
                               statistics.median(z["both_found_eligible"] for z in shuffles)}
    primary = plan["primary_budget_words"]
    index = {(r["question_id"], r["method"]): r for r in rows if r["budget_words"] == primary}
    ids = sorted(qid for qid in changed if index[qid, "bm25_turn"]["older_marked_available"])
    assert len(ids) == 70
    rng, differences = random.Random(13), []
    for _ in range(2000):
        sample = [ids[rng.randrange(len(ids))] for _ in ids]
        differences.append(sum(index[q, "best_other_session_second"]["both_found"] -
                               index[q, "bm25_turn"]["both_found"] for q in sample) / len(sample))
    differences.sort()
    output["descriptive_paired_bootstrap_95_difference_fraction_512"] = [differences[49], differences[1949]]
    output["paired_discordance_512"] = {
        "best_only": sum(index[q, "best_other_session_second"]["both_found"] and
                         not index[q, "bm25_turn"]["both_found"] for q in ids),
        "bm25_only": sum(index[q, "bm25_turn"]["both_found"] and
                         not index[q, "best_other_session_second"]["both_found"] for q in ids)}
    output["rank_lists_changed"] = {"best": sum(z["best"] for z in changed.values()),
                                    "newest": sum(z["newest"] for z in changed.values()),
                                    "other_session_available": sum(z["other"] for z in changed.values())}
    return output


def assert_phase12_parity(rows):
    prior = json.loads(gzip.decompress((ROOT / "results/phase12_temporal.json.gz").read_bytes()))
    old = {(r["question_id"], r["budget_words"]): r for r in prior["rows"]
           if r["method"] == "bm25_turn" and r["budget_words"] in (512, 1024)}
    now = {(r["question_id"], r["budget_words"]): r for r in rows
           if r["method"] == "bm25_turn" and r["budget_words"] in (512, 1024)}
    assert len(old) == len(now) == 144
    for key in old:
        assert all(old[key][field] == now[key][field] for field in
                   ("later_found", "older_found", "older_only", "both_found",
                    "all_later_found", "spent_words", "selected_turns")), key
    return 144


def run(source, output):
    if output.exists():
        raise FileExistsError(output)
    plan = json.loads((ROOT / "configs/phase13_plan.json").read_text(encoding="utf-8"))
    digest = source_sha(source)
    if digest != plan["source_sha256"]:
        raise ValueError("Pinned source checksum mismatch")
    records = [r for r in json.loads(source.read_text(encoding="utf-8"))
               if r["question_type"] == "knowledge-update" and not r["question_id"].endswith("_abs")]
    assert len(records) == plan["expected_answerable"]
    rows, changed = [], {}
    for record in records:
        qid = record["question_id"]
        turns = public_turns(record)
        orders, other = methods(rank(record["question"], turns), turns, qid,
                                plan["bm25_candidate_turns"], plan["random_other_session_seeds"])
        changed[qid] = {"other": other,
                        "best": orders["best_other_session_second"] != orders["bm25_turn"],
                        "newest": orders["newest_other_session_second"] != orders["bm25_turn"]}
        for budget in [plan["primary_budget_words"], *plan["secondary_budgets_words"]]:
            for method, order in orders.items():
                chosen, spent = pick(order, turns, budget)
                rows.append({"question_id": qid, "method": method, "budget_words": budget,
                             **score_record(record, chosen, spent, budget)})
    parity = assert_phase12_parity(rows)
    report = {"source_sha256": digest, "plan": plan, "questions": len(records),
              "phase12_exact_baseline_rows": parity, "rows": rows,
              "summary": summary(rows, plan, changed)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase13_provenance.json")
    args = parser.parse_args()
    result = run(args.source, args.output)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
