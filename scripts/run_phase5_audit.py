"""Post-hoc, read-only diagnostic audit of the frozen phase-4 result.

Recomputes primary-budget retrieval to check it against the recorded rows.
The output contains no source text, question, answer, or gold ID list.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from run_baselines import ROOT, make_segments, rank, sessions
from run_event_development import event_segments
from validate_held_out import validate


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_from_order(order, segments, budget):
    selected, remaining = [], budget
    for index in order:
        cost = segments[index]["word_cost"]
        if cost <= remaining:
            selected.append(index)
            remaining -= cost
    return selected


def diagnostic(gold, segments, order, selected, budget):
    """Structural feasibility is defined for the whole-segment budget only."""
    position = {index: place + 1 for place, index in enumerate(order)}
    owner = {turn_id: index for index, segment in enumerate(segments)
             for turn_id in segment["turn_ids"]}
    if len(owner) != sum(len(s["turn_ids"]) for s in segments):
        raise AssertionError("Duplicate turn ID in a segmentation")
    gold_indices = {owner[turn_id] for turn_id in gold}
    gold_cost = sum(segments[index]["word_cost"] for index in gold_indices)
    found = {turn_id for index in selected for turn_id in segments[index]["turn_ids"]}
    success = gold <= found
    reason = "success" if success else "structural_budget" if gold_cost > budget else "feasible_missed"
    return {"status": reason, "gold_segment_count": len(gold_indices),
            "gold_segment_word_cost": gold_cost,
            "worst_gold_rank": max(position[index] for index in gold_indices),
            "evidence_found": len(gold & found), "evidence_total": len(gold),
            "retrieved_words": sum(segments[index]["word_cost"] for index in selected),
            "retrieved_segments": len(selected), "all_evidence": success}


def leave_one_out(result):
    deltas = result["paired_primary"]["conversation_differences_event_minus_fixed"]
    if len(deltas) != 7:
        raise AssertionError("Expected seven independent conversation units")
    return {sid: sum(value for other, value in deltas.items() if other != sid) / 6
            for sid in sorted(deltas)}


def budget_transitions(result):
    by_case = defaultdict(dict)
    for row in result["per_question"]:
        by_case[(row["sample_id"], row["question_index"], row["method"])][row["budget_words"]] = row["all_evidence"]
    counts = Counter()
    for (_, _, method), outcomes in by_case.items():
        if set(outcomes) != {512, 1024, 2048}:
            raise AssertionError("Incomplete budget triplet")
        for low, high in ((512, 1024), (1024, 2048)):
            if outcomes[low] and not outcomes[high]:
                counts[(method, low, high)] += 1
    return [{"method": method, "from_budget": low, "to_budget": high,
             "success_to_failure": counts[(method, low, high)]}
            for low, high in ((512, 1024), (1024, 2048))
            for method in ("fixed", "event", "session")]


def run(data_path, output_path):
    if output_path.exists():
        raise FileExistsError("The phase-5 audit record is immutable; choose a new output path")
    validate()
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "configs/phase3_frozen.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "results/phase1_audit.json").read_text(encoding="utf-8"))
    held_path = ROOT / "results/phase4_held_out.json"
    held = json.loads(held_path.read_text(encoding="utf-8"))
    plan_path = ROOT / "configs/phase5_audit_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if (sha256(data_path) != protocol["sha256"] or
            sha256(data_path) != frozen["dataset_sha256"] or
            held["dataset_sha256"] != protocol["sha256"] or
            plan["primary_budget_words"] != held["primary_budget_words"]):
        raise ValueError("The source, frozen setting, or primary budget changed")
    budget = held["primary_budget_words"]
    samples = {s["sample_id"]: s for s in json.loads(data_path.read_bytes())}
    manifest = [x for x in audit["manifest"] if x["split"] == "held_out"]
    recorded = {(r["sample_id"], r["question_index"], r["method"]): r
                for r in held["per_question"] if r["budget_words"] == budget}
    if len(recorded) != 599 * 3 or len(manifest) != 599:
        raise AssertionError("Incomplete primary-budget record")
    details = {}
    for sid in sorted(protocol["held_out_conversations"]):
        sample = samples[sid]
        prepared = {
            "fixed": make_segments(sample, "fixed", frozen["fixed_words"]),
            "session": make_segments(sample, "session", frozen["fixed_words"]),
            "event": event_segments(sample, frozen["event_minimum_words"],
                                    frozen["event_preferred_words"], frozen["event_maximum_words"],
                                    frozen["event_window_turns"]),
        }
        expected = [turn["dia_id"] for _, turns in sessions(sample) for turn in turns]
        for method, segments in prepared.items():
            if [tid for s in segments for tid in s["turn_ids"]] != expected:
                raise AssertionError("Segmentation does not preserve all turns in order")
        for item in (x for x in manifest if x["sample_id"] == sid):
            qi = item["question_index"]
            question = sample["qa"][qi]["question"]
            gold = set(item["evidence_ids"])
            for method, segments in prepared.items():
                order = rank(question, segments)
                selected = choose_from_order(order, segments, budget)
                row = diagnostic(gold, segments, order, selected, budget)
                prior = recorded[(sid, qi, method)]
                for key in ("retrieved_words", "retrieved_segments", "evidence_found",
                            "evidence_total", "all_evidence"):
                    if row[key] != prior[key]:
                        raise AssertionError(f"Mismatch with phase 4: {sid}, {qi}, {method}, {key}")
                details[(sid, qi, method)] = row
    methods = {}
    for method in ("fixed", "event", "session"):
        rows = [value for (_, _, name), value in details.items() if name == method]
        states = Counter(row["status"] for row in rows)
        methods[method] = {
            "questions": len(rows), "outcome_counts": dict(sorted(states.items())),
            "structural_ceiling_count": len(rows) - states["structural_budget"],
            "median_worst_gold_rank": median(row["worst_gold_rank"] for row in rows),
            "multi_evidence_questions": sum(row["evidence_total"] > 1 for row in rows),
            "multi_evidence_split_across_segments": sum(row["evidence_total"] > 1 and
                                                          row["gold_segment_count"] > 1 for row in rows),
            "mean_gold_segment_word_cost": sum(row["gold_segment_word_cost"] for row in rows) / len(rows),
        }
        assert states["success"] == sum(r["all_evidence"] for r in held["per_question"]
                                        if r["budget_words"] == budget and r["method"] == method)
    discordant = []
    for item in manifest:
        sid, qi = item["sample_id"], item["question_index"]
        fixed, event = details[(sid, qi, "fixed")], details[(sid, qi, "event")]
        if fixed["all_evidence"] != event["all_evidence"]:
            winner = "event" if event["all_evidence"] else "fixed"
            loser = fixed if winner == "event" else event
            discordant.append({"sample_id": sid, "question_index": qi, "winner": winner,
                               "loser_status": loser["status"],
                               "fixed_gold_segments": fixed["gold_segment_count"],
                               "event_gold_segments": event["gold_segment_count"],
                               "fixed_gold_cost": fixed["gold_segment_word_cost"],
                               "event_gold_cost": event["gold_segment_word_cost"]})
    counts = Counter((r["winner"], r["loser_status"]) for r in discordant)
    output = {
        "analysis_status": plan["analysis_status"], "source_phase4_sha256": sha256(held_path),
        "phase5_plan_sha256": sha256(plan_path), "dataset_sha256": sha256(data_path),
        "primary_budget_words": budget, "questions_verified": len(manifest),
        "primary_rows_recomputed_and_matched": len(details),
        "method_diagnostics": methods,
        "discordance_summary": [{"winner": win, "loser_status": state, "count": counts[(win, state)]}
                                for win in ("event", "fixed")
                                for state in ("structural_budget", "feasible_missed")],
        "discordant_cases_no_text": discordant,
        "leave_one_conversation_out_mean_differences": leave_one_out(held),
        "budget_success_to_failure_transitions": budget_transitions(held),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase5_diagnostics.json")
    args = parser.parse_args()
    result = run(args.data, args.output)
    print("Matched", result["primary_rows_recomputed_and_matched"], "immutable phase-4 rows")
    for method, values in result["method_diagnostics"].items():
        print(method, values["outcome_counts"], "ceiling", values["structural_ceiling_count"])
