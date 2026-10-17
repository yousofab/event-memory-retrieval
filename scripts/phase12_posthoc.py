"""Post-result diagnostics; explicitly excluded from the registered primary analysis."""
import argparse
import json
import statistics
from pathlib import Path

from run_baselines import ROOT, rank
from run_phase12_temporal import public_turns, source_sha


def analyze(source, destination):
    plan = json.loads((ROOT / "configs/phase12_plan.json").read_text())
    if source_sha(source) != plan["source_sha256"]:
        raise ValueError("Source checksum mismatch")
    records = [r for r in json.loads(source.read_text()) if r["question_type"] == "knowledge-update"
               and not r["question_id"].endswith("_abs")]
    rows = []
    for record in records:
        turns = public_turns(record)
        order = rank(record["question"], turns)
        rank_of = {turns[i]["id"]: k + 1 for k, i in enumerate(order)}
        positions = [i for i, sid in enumerate(record["haystack_session_ids"])
                     if sid in record["answer_session_ids"]]
        old, new = sorted(positions)
        gold = {f"{new}:{j}" for j, turn in enumerate(record["haystack_sessions"][new])
                if turn.get("has_answer")}
        rows.append({"new_min_bm25_rank": min(rank_of[g] for g in gold),
                     "new_in_top20": any(rank_of[g] <= 20 for g in gold),
                     "later_sessions_after_new": len(record["haystack_sessions"]) - new - 1})
    assert len(rows) == 72
    out = {"status": "post-result explanatory audit, not registered endpoint",
           "questions": 72, "new_evidence_in_top20_count": sum(r["new_in_top20"] for r in rows),
           "new_evidence_top1_count": sum(r["new_min_bm25_rank"] == 1 for r in rows),
           "median_new_evidence_best_bm25_rank": statistics.median(r["new_min_bm25_rank"] for r in rows),
           "later_distractor_sessions_count": sum(r["later_sessions_after_new"] > 0 for r in rows),
           "median_later_distractor_sessions": statistics.median(r["later_sessions_after_new"] for r in rows)}
    destination.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase12_posthoc.json")
    args = parser.parse_args()
    print(json.dumps(analyze(args.source, args.output), indent=2))
