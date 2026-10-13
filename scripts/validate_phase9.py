"""Verify saved Phase 9 matrix, plan/data provenance and Phase 8 comparators."""
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from run_baselines import ROOT


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check():
    manifest = json.loads((ROOT / "results/phase9_summary.json").read_text(encoding="utf-8"))
    packed = (ROOT / "results/phase9_controls.json.gz").read_bytes()
    raw = gzip.decompress(packed)
    result = json.loads(raw)
    assert sha(packed) == manifest["compressed_result_sha256"]
    assert sha(raw) == manifest["full_result_sha256"]
    assert result["plan_sha256"] == sha((ROOT / "configs/phase9_boundary_plan.json").read_bytes())
    assert result["locomo_sha256"] == json.loads((ROOT / "configs/protocol.json").read_text())["sha256"]
    phase8_raw = gzip.decompress((ROOT / "results/phase8_causal.json.gz").read_bytes())
    assert result["phase8_result_sha256"] == sha(phase8_raw)
    phase8 = json.loads(phase8_raw)
    rows = result["per_question"]
    assert len(rows) == manifest["question_seed_budget_rows"] == 52380
    pairs = set()
    counts = Counter()
    for row in rows:
        key = (row["split"], row["sample_id"], row["question_index"], row["seed"], row["budget_words"])
        assert key not in pairs and row["seed"] in range(20) and row["budget_words"] in (512, 1024, 2048)
        pairs.add(key)
        assert row["retrieved_words"] <= row["budget_words"]
        assert not row["all_evidence"] or not row["structural_budget"]
        counts[row["split"], row["seed"], row["budget_words"]] += row["all_evidence"]
    assert len(pairs) == 52380
    for item in result["summary"]:
        split, budget = item["split"], item["budget_words"]
        assert item["null_successes_by_seed"] == [counts[split, seed, budget] for seed in range(20)]
        prior = sum(r["all_evidence"] for r in phase8["locomo_per_question"]
                    if r["split"] == split and r["budget_words"] == budget and r["method"] == "online")
        assert item["online_successes"] == prior
    online_stats = {(x["split"], x["sample_id"]): x for x in phase8["locomo_segment_stats"] if x["method"] == "online"}
    assert len(result["shape"]) == 200
    for shape in result["shape"]:
        old = online_stats[shape["split"], shape["sample_id"]]
        assert shape["segments"] == old["segments"] and shape["words_total"] == old["total_segment_words"]
    print("Phase 9 digest, matrix, budgets, summaries and per-conversation segment counts verified")


if __name__ == "__main__":
    check()
