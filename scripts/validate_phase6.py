"""Validate Phase 6 output against frozen manifests and Phase 4 without raw text."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from run_baselines import ROOT
from run_held_out import aggregate, sign_flip_paired_two_sided


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path):
    output = json.loads(path.read_text(encoding="utf-8"))
    split = output["split"]
    assert split in ("development", "held_out")
    sources = {"phase6_plan_sha256": ROOT / "configs/phase6_semantic_plan.json",
               "frozen_config_sha256": ROOT / "configs/phase3_frozen.json",
               "manifest_sha256": ROOT / "results/phase1_audit.json"}
    for name, source in sources.items():
        assert output[name] == digest(source), name
    plan = json.loads(sources["phase6_plan_sha256"].read_text(encoding="utf-8"))
    manifest = json.loads(sources["manifest_sha256"].read_text(encoding="utf-8"))
    selected = {(m["sample_id"], m["question_index"]): m for m in manifest["manifest"]
                if m["split"] == split}
    assert output["dataset_sha256"] == plan["dataset_sha256"] == manifest["dataset_sha256"]
    assert output["question_count"] == len(selected)
    assert output["conversation_count"] == len({sid for sid, _ in selected})
    assert output["budgets_words"] == [512, 1024, 2048]
    assert output["training"]["dimensions"] == plan["svd_components"]
    assert output["training"]["training_turns"] > 0
    rows = output["per_question"]
    assert len(rows) == len(selected) * 3
    lookup = {(r["sample_id"], r["question_index"], r["budget_words"]): r for r in rows}
    assert len(lookup) == len(rows)
    assert set(lookup) == {(sid, qi, budget) for sid, qi in selected for budget in (512, 1024, 2048)}
    for (sid, qi, budget), row in lookup.items():
        assert row["method"] == "semantic_lsa" and row["category"] == selected[(sid, qi)]["category"]
        assert row["evidence_total"] == len(set(selected[(sid, qi)]["evidence_ids"]))
        assert 0 <= row["evidence_found"] <= row["evidence_total"]
        assert row["all_evidence"] == (row["evidence_found"] == row["evidence_total"])
        assert 0 <= row["retrieved_words"] <= budget
        assert row["gold_segment_word_cost"] >= 0 and row["gold_segment_count"] >= 1
        assert row["structural_budget"] == (row["gold_segment_word_cost"] > budget)
        assert not (row["all_evidence"] and row["structural_budget"])
    assert aggregate(rows) == output["per_conversation"]
    assert all(s["method"] == "semantic_lsa" and s["segments"] > 0 and
               s["source_words"] > 0 for s in output["segment_stats"])
    if split == "held_out":
        prior_path = ROOT / "results/phase4_held_out.json"
        assert output["phase4_result_sha256"] == digest(prior_path)
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        before = {(r["sample_id"], r["question_index"]): r["all_evidence"] for r in prior["per_question"]
                  if r["method"] == "event" and r["budget_words"] == 1024}
        after = {(r["sample_id"], r["question_index"]): r["all_evidence"] for r in rows
                 if r["budget_words"] == 1024}
        assert before.keys() == after.keys() and len(before) == 599
        counts = {"semantic_only": sum(after[k] and not before[k] for k in after),
                  "lexical_only": sum(before[k] and not after[k] for k in after),
                  "both": sum(after[k] and before[k] for k in after),
                  "neither": sum(not after[k] and not before[k] for k in after)}
        assert counts == output["discordance_primary_against_frozen_lexical"]
        scores = {(r["sample_id"], r["method"]): r["all_evidence_rate"] for r in
                  output["per_conversation"] + prior["per_conversation"] if r["budget_words"] == 1024}
        differences = {sid: scores[(sid, "semantic_lsa")] - scores[(sid, "event")]
                       for sid in sorted({sid for sid, _ in before})}
        paired = output["paired_primary"]
        assert paired["conversation_differences_semantic_minus_lexical"] == differences
        assert abs(paired["mean_conversation_difference"] - sum(differences.values()) / 7) < 1e-12
        assert paired["exact_two_sided_sign_flip_reference_exploratory"] == sign_flip_paired_two_sided(
            list(differences.values()))
    else:
        assert output["paired_primary"] is None and output["phase4_result_sha256"] is None
    counts = Counter(r["budget_words"] for r in rows if r["all_evidence"])
    print(f"Validated Phase 6 {split}: {len(rows)} unique rows, {len(selected)} questions")
    print("Successes by budget:", dict(sorted(counts.items())))
    print("SHA-256", digest(path))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "held_out"), required=True)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    validate(args.input or ROOT / f"results/phase6_{args.split}_lsa.json")
