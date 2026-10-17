"""Frozen Phase 12 retrieval-only audit on LongMemEval-S knowledge updates.

Ranking receives question, turn content, and array position. Evidence metadata and
answers are kept outside the ranking functions and read only by score_record.
"""
import argparse
import hashlib
import json
import random
import statistics
from pathlib import Path

from run_baselines import ROOT, rank, words


def source_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def public_turns(record):
    """Return content and encounter position only; no role/date/gold/answer."""
    result = []
    for si, group in enumerate(record["haystack_sessions"]):
        for ti, turn in enumerate(group):
            tokens = words(turn["content"])
            result.append({"id": f"{si}:{ti}", "session_position": si,
                           "turn_position": ti, "turn_ids": [f"{si}:{ti}"],
                           "word_cost": len(tokens), "tokens": tokens})
    return result


def methods(lexical, turns, qid, k=20, seeds=20):
    head, tail = lexical[:k], lexical[k:]
    assert len(head) == k and len(set(head)) == k
    result = {"bm25_turn": lexical,
              "recent_within_top20": sorted(head, key=lambda i: (-turns[i]["session_position"],
                                                                 -turns[i]["turn_position"], i)) + tail}
    for seed in range(seeds):
        shuffled = head.copy()
        random.Random(f"phase12:{qid}:{seed}").shuffle(shuffled)
        result[f"shuffled_within_top20:{seed}"] = shuffled + tail
    for order in result.values():
        assert set(order[:k]) == set(head) and order[k:] == tail
    return result


def pick(order, turns, budget):
    chosen, remaining = set(), budget
    for i in order:
        cost = turns[i]["word_cost"]
        if cost <= remaining:
            chosen.add(turns[i]["id"])
            remaining -= cost
    assert 0 <= remaining <= budget
    return chosen, budget - remaining


def score_record(record, selected, spent, budget):
    ids = record["haystack_session_ids"]
    assert len(ids) == len(record["haystack_sessions"]) == len(record["haystack_dates"])
    assert len(set(record["answer_session_ids"])) == 2
    evidence_positions = [i for i, sid in enumerate(ids) if sid in record["answer_session_ids"]]
    assert len(evidence_positions) == 2
    older, later = sorted(evidence_positions)
    assert record["question_id"][-4:] != "_abs"
    def marked(si):
        return {f"{si}:{ti}" for ti, t in enumerate(record["haystack_sessions"][si])
                if t.get("has_answer") is True}
    older_gold, later_gold = marked(older), marked(later)
    assert later_gold, "Answerable knowledge-update row lacks later marked evidence"
    assert spent <= budget
    old_found, new_found = bool(selected & older_gold), bool(selected & later_gold)
    return {"later_found": new_found, "older_found": old_found,
            "older_only": old_found and not new_found,
            "both_found": old_found and new_found,
            "all_later_found": later_gold <= selected,
            "older_marked_available": bool(older_gold),
            "spent_words": spent, "selected_turns": len(selected)}


def compact(rows, method, budget):
    x = [r for r in rows if r["method"] == method and r["budget_words"] == budget]
    assert len(x) == 72
    return {"questions": len(x), **{key: sum(r[key] for r in x) for key in
            ("later_found", "older_found", "older_only", "both_found", "all_later_found")},
            "mean_spent_words": round(statistics.mean(r["spent_words"] for r in x), 2)}


def summarize(rows, plan):
    budgets = [plan["primary_budget_words"], *plan["secondary_budgets_words"]]
    summary = {}
    for budget in budgets:
        baseline = compact(rows, "bm25_turn", budget)
        temporal = compact(rows, "recent_within_top20", budget)
        randoms = [compact(rows, f"shuffled_within_top20:{s}", budget)
                   for s in range(plan["random_order_seeds"])]
        summary[str(budget)] = {"bm25_turn": baseline, "recent_within_top20": temporal,
                                "random_later_by_seed": [v["later_found"] for v in randoms],
                                "random_later_median": statistics.median(v["later_found"] for v in randoms),
                                "temporal_minus_bm25": temporal["later_found"] - baseline["later_found"],
                                "temporal_minus_random_median": temporal["later_found"] -
                                statistics.median(v["later_found"] for v in randoms)}
    budget = plan["primary_budget_words"]
    mapping = {(r["question_id"], r["method"]): r["later_found"]
               for r in rows if r["budget_words"] == budget}
    qids = sorted({qid for qid, _ in mapping})
    assert len(qids) == 72
    rng, diffs = random.Random(12), []
    for _ in range(2000):
        sample = [qids[rng.randrange(len(qids))] for _ in qids]
        diffs.append(sum(mapping[q, "recent_within_top20"] - mapping[q, "bm25_turn"]
                         for q in sample) / len(sample))
    diffs.sort()
    summary["descriptive_paired_bootstrap_95_difference_fraction_1024"] = [diffs[49], diffs[1949]]
    summary["paired_discordance_1024"] = {
        "temporal_only": sum(mapping[q, "recent_within_top20"] and not mapping[q, "bm25_turn"] for q in qids),
        "bm25_only": sum(mapping[q, "bm25_turn"] and not mapping[q, "recent_within_top20"] for q in qids)}
    return summary


def run(source, output):
    if output.exists():
        raise FileExistsError(output)
    plan = json.loads((ROOT / "configs/phase12_plan.json").read_text(encoding="utf-8"))
    actual_sha = source_sha(source)
    if actual_sha != plan["source_sha256"]:
        raise ValueError("Pinned source checksum mismatch")
    records = json.loads(source.read_text(encoding="utf-8"))
    selected_records = [r for r in records if r["question_type"] == "knowledge-update"
                        and not r["question_id"].endswith("_abs")]
    assert len(selected_records) == plan["expected_questions"]
    assert len({r["question_id"] for r in selected_records}) == len(selected_records)
    rows, anomalies = [], {"date_order_disagreement": 0, "older_marker_missing": 0,
                           "repeated_session_ids": 0, "later_distractor_sessions": 0}
    for record in selected_records:
        turns = public_turns(record)
        lexical = rank(record["question"], turns)
        assert len(lexical) == len(turns) and len(set(lexical)) == len(turns)
        orders = methods(lexical, turns, record["question_id"],
                         plan["lexical_candidate_turns"], plan["random_order_seeds"])
        ids = record["haystack_session_ids"]
        indices = [i for i, sid in enumerate(ids) if sid in record["answer_session_ids"]]
        assert len(indices) == 2
        a, b = sorted(indices)
        anomalies["date_order_disagreement"] += record["haystack_dates"][a] >= record["haystack_dates"][b]
        anomalies["older_marker_missing"] += not any(t.get("has_answer") for t in record["haystack_sessions"][a])
        anomalies["repeated_session_ids"] += len(ids) != len(set(ids))
        anomalies["later_distractor_sessions"] += b < len(ids) - 1
        for budget in [plan["primary_budget_words"], *plan["secondary_budgets_words"]]:
            for method, order in orders.items():
                chosen, spent = pick(order, turns, budget)
                rows.append({"question_id": record["question_id"], "method": method,
                             "budget_words": budget,
                             **score_record(record, chosen, spent, budget)})
    result = {"source_sha256": actual_sha, "plan": plan, "questions": len(selected_records),
              "rows": rows, "audit": anomalies, "summary": summarize(rows, plan)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase12_temporal.json")
    args = parser.parse_args()
    result = run(args.source, args.output)
    print(json.dumps({"questions": result["questions"], "audit": result["audit"],
                      "summary": result["summary"]}, ensure_ascii=False, indent=2))
