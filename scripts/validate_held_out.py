"""Audit the recorded held-out result without rerunning retrieval or tuning."""
import hashlib
import json
from collections import Counter, defaultdict

from run_baselines import ROOT


def validate():
    path = ROOT / "results/phase4_held_out.json"
    output = json.loads(path.read_text(encoding="utf-8"))
    frozen = (ROOT / "configs/phase3_frozen.json").read_bytes()
    manifest = (ROOT / "results/phase1_audit.json").read_bytes()
    plan = (ROOT / "configs/phase4_analysis_plan.json").read_bytes()
    for key, content in (("frozen_config_sha256", frozen), ("manifest_sha256", manifest),
                         ("analysis_plan_sha256", plan)):
        assert output[key] == hashlib.sha256(content).hexdigest(), key
    audit = json.loads(manifest)
    selected = {(x["sample_id"], x["question_index"]): x for x in audit["manifest"] if x["split"] == "held_out"}
    assert len(selected) == output["question_count"] == 599
    assert len({sid for sid, _ in selected}) == output["conversation_count"] == 7
    rows = output["per_question"]
    assert len(rows) == 599 * 3 * 3
    keys = [(r["sample_id"], r["question_index"], r["method"], r["budget_words"]) for r in rows]
    assert len(set(keys)) == len(keys)
    for sid, qi in selected:
        assert {(m, b) for s, q, m, b in keys if (s, q) == (sid, qi)} == {
            (m, b) for m in ("fixed", "session", "event") for b in (512, 1024, 2048)}
    grouped = defaultdict(list)
    for row in rows:
        item = selected[(row["sample_id"], row["question_index"])]
        assert row["category"] == item["category"]
        assert row["evidence_total"] == len(set(item["evidence_ids"]))
        assert 0 <= row["retrieved_words"] <= row["budget_words"]
        assert 0 <= row["evidence_found"] <= row["evidence_total"]
        assert row["all_evidence"] == (row["evidence_found"] == row["evidence_total"])
        grouped[(row["sample_id"], row["method"], row["budget_words"])].append(row)
    for summary in output["per_conversation"]:
        group = grouped[(summary["sample_id"], summary["method"], summary["budget_words"])]
        assert len(group) == summary["questions"]
        assert sum(r["all_evidence"] for r in group) == summary["all_evidence_count"]
        assert abs(summary["all_evidence_rate"] - summary["all_evidence_count"] / len(group)) < 1e-12
    outcome = Counter((r["method"], r["budget_words"]) for r in rows if r["all_evidence"])
    print("Validated 5,391 unique result rows across 599 held-out questions.")
    for budget in (512, 1024, 2048):
        print(budget, "fixed", outcome[("fixed", budget)], "event", outcome[("event", budget)],
              "session", outcome[("session", budget)])
    print("SHA-256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    validate()
