"""Post-result descriptive analysis; boundary agreement is not boundary validity."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from run_baselines import ROOT, sessions, words
from run_event_development import event_segments
from run_phase6_semantic import fit_lsa, semantic_segments, training_texts


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boundaries(segments, sample):
    end_of_session = {turns[-1]["dia_id"] for _, turns in sessions(sample) if turns}
    return {segment["turn_ids"][-1] for segment in segments} - end_of_session


def run(data_path, output_path):
    if output_path.exists():
        raise FileExistsError("Diagnostics exist; select a fresh output path")
    files = {"semantic": ROOT / "results/phase6_held_out_lsa.json",
             "lexical": ROOT / "results/phase4_held_out.json",
             "plan": ROOT / "configs/phase6_semantic_plan.json",
             "protocol": ROOT / "configs/protocol.json"}
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in files.items()}
    result, prior, plan, protocol = (data[name] for name in ("semantic", "lexical", "plan", "protocol"))
    raw = data_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != result["dataset_sha256"] or result["phase6_plan_sha256"] != digest(files["plan"]):
        raise ValueError("Dataset or plan checksum mismatch")
    primary = result["primary_budget_words"]
    summary = []
    for budget in result["budgets_words"]:
        for source, method in ((result, "semantic_lsa"), (prior, "event"),
                               (prior, "fixed"), (prior, "session")):
            conv = [x for x in source["per_conversation"] if x["method"] == method and
                    x["budget_words"] == budget]
            if len(conv) != 7:
                raise ValueError("Incomplete conversation summaries")
            summary.append({"method": method, "budget_words": budget,
                            "successes": sum(x["all_evidence_count"] for x in conv),
                            "questions": sum(x["questions"] for x in conv),
                            "unweighted_mean_conversation_rate": sum(x["all_evidence_rate"] for x in conv) / 7,
                            "unweighted_mean_retrieved_words": sum(x["mean_retrieved_words"] for x in conv) / 7})
    semantic_rows = [x for x in result["per_question"] if x["budget_words"] == primary]
    lexical_rows = {(x["sample_id"], x["question_index"]): x for x in prior["per_question"]
                    if x["method"] == "event" and x["budget_words"] == primary}
    subgroup = []
    for field in ("category", "gold_turn_group", "gold_session_group"):
        for value in sorted({row[field] for row in semantic_rows}, key=str):
            group = [row for row in semantic_rows if row[field] == value]
            subgroup.append({"field": field, "value": value, "questions": len(group),
                             "semantic_successes": sum(row["all_evidence"] for row in group),
                             "lexical_successes": sum(lexical_rows[row["sample_id"],
                                                                    row["question_index"]]["all_evidence"]
                                                      for row in group)})
    diffs = result["paired_primary"]["conversation_differences_semantic_minus_lexical"]
    leave_one_out = {sid: sum(value for key, value in diffs.items() if key != sid) / 6 for sid in diffs}
    sample_map = {item["sample_id"]: item for item in json.loads(raw)}
    vectorizer, svd, training = fit_lsa(training_texts(sample_map, protocol["development_conversations"]), plan)
    if training["training_text_sha256"] != result["training"]["training_text_sha256"]:
        raise ValueError("Training corpus differs")
    comparison, unknown_tokens, tokens, unseen_turns, empty_turns, turn_count = [], 0, 0, 0, 0, 0
    for sid in sorted(protocol["held_out_conversations"]):
        sample = sample_map[sid]
        lexical = event_segments(sample, 64, 128, 160, 3)
        semantic = semantic_segments(sample, vectorizer, svd, 64, 128, 160, 3)
        a, b = boundaries(lexical, sample), boundaries(semantic, sample)
        comparison.append({"sample_id": sid, "lexical_segments": len(lexical),
                           "semantic_segments": len(semantic),
                           "lexical_internal_boundaries": len(a), "semantic_internal_boundaries": len(b),
                           "shared_exact_boundaries": len(a & b)})
        for _, turns in sessions(sample):
            for turn in turns:
                terms = words(turn.get("text") or "")
                tokens += len(terms)
                unknown_tokens += sum(term not in vectorizer.vocabulary_ for term in terms)
                turn_count += 1
                unseen_turns += bool(terms) and all(term not in vectorizer.vocabulary_ for term in terms)
                empty_turns += not terms
    assert all(next(row for row in result["segment_stats"] if row["sample_id"] == x["sample_id"])["segments"] ==
               x["semantic_segments"] for x in comparison)
    audit = {"phase": 6, "interpretation": "exploratory and descriptive; exact boundary overlap is not human event validity",
             "input_sha256": {name: digest(path) for name, path in files.items()},
             "dataset_sha256": result["dataset_sha256"], "budget_summary": summary,
             "subgroup_primary": subgroup,
             "semantic_primary": {"structural_budget": sum(r["structural_budget"] for r in semantic_rows),
                                  "feasible_missed": sum(not r["all_evidence"] and not r["structural_budget"]
                                                         for r in semantic_rows),
                                  "multiturn_gold_questions": sum(r["gold_turn_group"] == "multiple"
                                                                  for r in semantic_rows),
                                  "multiturn_gold_split_across_segments": sum(
                                      r["gold_turn_group"] == "multiple" and r["gold_segment_count"] > 1
                                      for r in semantic_rows)},
             "paired_primary": result["paired_primary"],
             "discordance_primary": result["discordance_primary_against_frozen_lexical"],
             "leave_one_conversation_out_difference": leave_one_out,
             "boundary_overlap": {"per_conversation": comparison,
                                  "total_lexical_internal_boundaries": sum(r["lexical_internal_boundaries"]
                                                                           for r in comparison),
                                  "total_semantic_internal_boundaries": sum(r["semantic_internal_boundaries"]
                                                                            for r in comparison),
                                  "shared_exact_boundaries": sum(r["shared_exact_boundaries"]
                                                                 for r in comparison)},
             "held_out_vocabulary_coverage": {"total_tokens": tokens, "out_of_vocabulary_tokens": unknown_tokens,
                                               "total_turns": turn_count, "nonempty_turns_without_known_tokens":
                                               unseen_turns, "empty_turns": empty_turns}}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved Phase 6 descriptive diagnostics with boundary overlap and paired sensitivity")
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase6_diagnostics.json")
    args = parser.parse_args()
    run(args.data, args.output)
