"""Single frozen held-out evaluation; no tuning, no generated answers."""
import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

from run_baselines import ROOT, make_segments, retrieve, sessions
from run_event_development import event_segments


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row["method"], row["budget_words"], row["sample_id"])].append(row)
    out = []
    for (method, budget, sid), group in sorted(groups.items()):
        n = len(group)
        out.append({"method": method, "budget_words": budget, "sample_id": sid,
                    "questions": n, "all_evidence_count": sum(x["all_evidence"] for x in group),
                    "all_evidence_rate": sum(x["all_evidence"] for x in group) / n,
                    "mean_retrieved_words": sum(x["retrieved_words"] for x in group) / n,
                    "mean_retrieved_segments": sum(x["retrieved_segments"] for x in group) / n})
    return out


def sign_flip_paired_two_sided(differences):
    """Exploratory exact sign-flip randomization; zeros retained."""
    n = len(differences)
    if n == 0:
        raise ValueError("No paired differences")
    observed = abs(sum(differences))
    extreme = sum(abs(sum(sign * d for sign, d in zip(signs, differences))) >= observed - 1e-12
                  for signs in itertools.product((-1, 1), repeat=n))
    return extreme / 2 ** n


def paired_analysis(rows, summary, primary_budget):
    sids = sorted({r["sample_id"] for r in summary})
    lookup = {(r["method"], r["budget_words"], r["sample_id"]): r for r in summary}
    diffs = [lookup[("event", primary_budget, sid)]["all_evidence_rate"] -
             lookup[("fixed", primary_budget, sid)]["all_evidence_rate"] for sid in sids]
    cases = defaultdict(dict)
    for row in rows:
        if row["budget_words"] == primary_budget:
            cases[(row["sample_id"], row["question_index"])][row["method"]] = row["all_evidence"]
    if any(set(values) != {"event", "fixed", "session"} for values in cases.values()):
        raise AssertionError("Missing method for a held-out question")
    disagreements = {"event_only": 0, "fixed_only": 0, "both": 0, "neither": 0}
    for values in cases.values():
        if values["event"] and values["fixed"]:
            disagreements["both"] += 1
        elif values["event"]:
            disagreements["event_only"] += 1
        elif values["fixed"]:
            disagreements["fixed_only"] += 1
        else:
            disagreements["neither"] += 1
    return {"conversation_differences_event_minus_fixed": dict(zip(sids, diffs)),
            "mean_conversation_difference": sum(diffs) / len(diffs),
            "exact_two_sided_sign_flip_p_exploratory": sign_flip_paired_two_sided(diffs),
            "question_disagreement_counts_descriptive": disagreements}


def breakdown(rows, primary_budget):
    output = []
    for field in ("category", "gold_turn_group", "gold_session_group"):
        groups = defaultdict(list)
        for row in rows:
            if row["budget_words"] == primary_budget:
                groups[(field, str(row[field]), row["method"])].append(row)
        for (name, value, method), group in sorted(groups.items()):
            output.append({"field": name, "value": value, "method": method,
                           "questions": len(group), "successes": sum(x["all_evidence"] for x in group)})
    return output


def run(data_path, output_path):
    if output_path.exists():
        raise FileExistsError("A held-out result already exists; this command will not overwrite it")
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    plan_path = ROOT / "configs/phase4_analysis_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    frozen_path = ROOT / "configs/phase3_frozen.json"
    manifest_path = ROOT / "results/phase1_audit.json"
    if digest(frozen_path) != plan["frozen_config_sha256"] or digest(manifest_path) != plan["phase1_manifest_sha256"]:
        raise ValueError("Frozen config or eligibility manifest has changed")
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if frozen["primary_metric"] != protocol["precommitted_primary_metric"]:
        raise ValueError("Primary metric changed")
    raw = data_path.read_bytes()
    dataset_sha = hashlib.sha256(raw).hexdigest()
    if dataset_sha != protocol["sha256"] or dataset_sha != frozen["dataset_sha256"]:
        raise ValueError("Source data differs from the pinned version")
    audit = json.loads(manifest_path.read_text(encoding="utf-8"))
    if audit["dataset_sha256"] != dataset_sha:
        raise ValueError("Manifest refers to another dataset")
    held = set(protocol["held_out_conversations"])
    manifest = [item for item in audit["manifest"] if item["split"] == "held_out"]
    if (len(manifest) != plan["expected_held_out_questions"] or
            len(held) != plan["expected_held_out_conversations"] or
            {item["sample_id"] for item in manifest} != held or
            len({(item["sample_id"], item["question_index"]) for item in manifest}) != len(manifest)):
        raise ValueError("Held-out question set is inconsistent")
    samples = {sample["sample_id"]: sample for sample in json.loads(raw)}
    budgets = sorted([frozen["primary_budget_words"]] + frozen["secondary_budgets_words"])
    if budgets != [512, 1024, 2048] or frozen["development_selected_config"] != "w3-max160":
        raise ValueError("Unexpected settings for this frozen comparison")
    rows, segment_stats = [], []
    for sid in sorted(held):
        sample = samples[sid]
        expected_ids = [turn["dia_id"] for _, turns in sessions(sample) for turn in turns]
        prepared = {
            "fixed": make_segments(sample, "fixed", frozen["fixed_words"]),
            "session": make_segments(sample, "session", frozen["fixed_words"]),
            "event": event_segments(sample, frozen["event_minimum_words"],
                                    frozen["event_preferred_words"], frozen["event_maximum_words"],
                                    frozen["event_window_turns"])}
        for method, segments in prepared.items():
            observed_ids = [dia for segment in segments for dia in segment["turn_ids"]]
            if observed_ids != expected_ids or len(observed_ids) != len(set(observed_ids)):
                raise AssertionError("Invalid partition")
            segment_stats.append({"sample_id": sid, "method": method, "segments": len(segments),
                                  "source_words": sum(segment["word_cost"] for segment in segments),
                                  "mean_segment_words": sum(segment["word_cost"] for segment in segments) / len(segments),
                                  "max_segment_words": max(segment["word_cost"] for segment in segments),
                                  "scored_segments_per_question": len(segments)})
        for item in (m for m in manifest if m["sample_id"] == sid):
            question = sample["qa"][item["question_index"]]["question"]
            gold = set(item["evidence_ids"])
            for method, segments in prepared.items():
                for budget in budgets:
                    chosen = retrieve(question, segments, budget)
                    found = {dia for index in chosen for dia in segments[index]["turn_ids"]}
                    used = sum(segments[index]["word_cost"] for index in chosen)
                    if used > budget:
                        raise AssertionError("Budget overrun")
                    rows.append({"sample_id": sid, "question_index": item["question_index"],
                                 "category": item["category"], "gold_turn_group": "one" if len(gold) == 1 else "multiple",
                                 "gold_session_group": "one" if len({x.split(':')[0] for x in gold}) == 1 else "multiple",
                                 "method": method, "budget_words": budget,
                                 "all_evidence": gold <= found, "evidence_found": len(gold & found),
                                 "evidence_total": len(gold), "retrieved_words": used,
                                 "retrieved_segments": len(chosen)})
    summary = aggregate(rows)
    primary_budget = frozen["primary_budget_words"]
    paired = paired_analysis(rows, summary, primary_budget)
    output = {"dataset_sha256": dataset_sha, "frozen_config_sha256": digest(frozen_path),
              "manifest_sha256": digest(manifest_path), "analysis_plan_sha256": digest(plan_path),
              "split": "held_out", "primary_budget_words": primary_budget,
              "budgets_words": budgets, "question_count": len(manifest), "conversation_count": len(held),
              "segment_stats": segment_stats, "per_conversation": summary,
              "paired_primary": paired, "descriptive_breakdown": breakdown(rows, primary_budget),
              "per_question": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Held-out output saved; 599 questions x three methods x three budgets.")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase4_held_out.json")
    parser.add_argument("--run-held-out", action="store_true",
                        help="Acknowledge the one-time frozen held-out evaluation")
    args = parser.parse_args()
    if not args.run_held_out:
        parser.error("Pass --run-held-out to execute the final evaluation")
    run(args.data, args.output)
