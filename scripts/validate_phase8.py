"""Independent integrity checks against Phase 4 and Phase 7 comparators."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from run_baselines import ROOT


def check():
    summary = json.loads((ROOT / "results/phase8_summary.json").read_text(encoding="utf-8"))
    packed = (ROOT / "results/phase8_causal.json.gz").read_bytes()
    raw = gzip.decompress(packed)
    result = json.loads(raw)
    sha = lambda payload: hashlib.sha256(payload).hexdigest()
    assert sha(packed) == summary["compressed_result_sha256"]
    assert sha(raw) == summary["full_result_sha256"]
    assert result["phase8_plan_sha256"] == sha((ROOT / "configs/phase8_causal_plan.json").read_bytes())
    assert result["locomo_sha256"] == json.loads((ROOT / "configs/protocol.json").read_text())["sha256"]
    assert result["external_sha256"] == json.loads((ROOT / "configs/phase7_external_plan.json").read_text())["external_dataset"]["sha256"]
    local, external = result["locomo_per_question"], result["external_per_question"]
    assert len(local) == summary["locomo_result_rows"] == 10476
    assert len(external) == summary["external_result_rows"] == 5640
    old = json.loads((ROOT / "results/phase4_held_out.json").read_text(encoding="utf-8"))
    old_lookup = {(r["sample_id"], r["question_index"], r["method"], r["budget_words"]): r
                  for r in old["per_question"]}
    for row in local:
        assert row["retrieved_words"] <= row["budget_words"]
        if row["split"] == "held_out" and row["method"] in ("fixed", "event", "session"):
            prior = old_lookup[(row["sample_id"], row["question_index"], row["method"], row["budget_words"])]
            assert (row["all_evidence"], row["retrieved_words"], row["retrieved_segments"]) == (prior["all_evidence"], prior["retrieved_words"], prior["retrieved_segments"])
    assert len(old_lookup) == sum(row["split"] == "held_out" and row["method"] != "online" for row in local)
    old_ext = json.loads((ROOT / "results/phase7_summary.json").read_text(encoding="utf-8"))
    assert result["phase7_comparator_sha256"] == old_ext["full_result_sha256"]
    assert Counter(r["method"] for r in external) == {"online": 1410, "event": 1410, "fixed": 1410, "session": 1410}
    for row in external:
        assert row["retrieved_words"] <= row["budget_words"]
        assert not row["all_marked_turns"] or not row["structural_budget"]
    for row in result["locomo_summary"]:
        group = [r for r in local if (r["split"], r["budget_words"], r["method"]) ==
                 (row["split"], row["budget_words"], row["method"])]
        assert len(group) == row["questions"] and sum(r["all_evidence"] for r in group) == row["successes"]
    for row in result["external_summary"]:
        group = [r for r in external if (r["budget_words"], r["method"]) == (row["budget_words"], row["method"])]
        assert len(group) == row["questions"] and sum(r["all_marked_turns"] for r in group) == row["successes"]
    print("Phase 8 package, budgets, summaries, and Phase 4/7 comparator equivalence verified")


if __name__ == "__main__":
    check()
