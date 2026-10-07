"""Validate the immutable phase-5 diagnostic result without reading raw data."""
import json
from collections import Counter

from run_baselines import ROOT
from run_phase5_audit import budget_transitions, leave_one_out, sha256


def validate():
    path = ROOT / "results/phase5_diagnostics.json"
    output = json.loads(path.read_text(encoding="utf-8"))
    held_path = ROOT / "results/phase4_held_out.json"
    plan_path = ROOT / "configs/phase5_audit_plan.json"
    held = json.loads(held_path.read_text(encoding="utf-8"))
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    assert output["analysis_status"] == "post_hoc_descriptive_after_phase4"
    assert output["source_phase4_sha256"] == sha256(held_path)
    assert output["phase5_plan_sha256"] == sha256(plan_path)
    assert output["dataset_sha256"] == protocol["sha256"]
    assert output["primary_budget_words"] == held["primary_budget_words"] == 1024
    assert output["questions_verified"] == 599
    assert output["primary_rows_recomputed_and_matched"] == 1797
    assert output["budget_success_to_failure_transitions"] == budget_transitions(held)
    expected_loo = leave_one_out(held)
    assert set(output["leave_one_conversation_out_mean_differences"]) == set(expected_loo)
    for sid, value in expected_loo.items():
        assert abs(output["leave_one_conversation_out_mean_differences"][sid] - value) < 1e-12
    for method, group in output["method_diagnostics"].items():
        states = group["outcome_counts"]
        assert set(states) <= {"success", "structural_budget", "feasible_missed"}
        assert sum(states.values()) == group["questions"] == 599
        assert group["structural_ceiling_count"] == 599 - states.get("structural_budget", 0)
        assert group["multi_evidence_questions"] == 90
        observed_success = sum(row["all_evidence"] for row in held["per_question"]
                               if row["budget_words"] == 1024 and row["method"] == method)
        assert states["success"] == observed_success
    assert set(output["method_diagnostics"]) == {"fixed", "event", "session"}
    cases = output["discordant_cases_no_text"]
    assert len(cases) == 45
    assert len({(x["sample_id"], x["question_index"]) for x in cases}) == 45
    allowed = {"sample_id", "question_index", "winner", "loser_status",
               "fixed_gold_segments", "event_gold_segments", "fixed_gold_cost", "event_gold_cost"}
    assert all(set(x) == allowed for x in cases)
    recorded = {(x["sample_id"], x["question_index"], x["method"]): x["all_evidence"]
                for x in held["per_question"] if x["budget_words"] == 1024}
    for case in cases:
        sid, qi = case["sample_id"], case["question_index"]
        assert case["winner"] in {"event", "fixed"}
        assert case["loser_status"] in {"structural_budget", "feasible_missed"}
        assert recorded[sid, qi, case["winner"]]
        assert not recorded[sid, qi, "fixed" if case["winner"] == "event" else "event"]
    counts = Counter((x["winner"], x["loser_status"]) for x in cases)
    for summary in output["discordance_summary"]:
        assert summary["count"] == counts[summary["winner"], summary["loser_status"]]
    assert sum(x["count"] for x in output["discordance_summary"]) == 45
    print("Validated phase-5 diagnostics, 1797 matched rows and 45 discordant case records.")
    print("SHA-256", sha256(path))


if __name__ == "__main__":
    validate()
