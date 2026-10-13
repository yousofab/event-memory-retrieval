"""Audit published Phase 10 checksums, result matrix and metric aggregation."""
import gzip
import hashlib
import json
import math
from collections import Counter

from run_baselines import ROOT
from run_phase10_topic_transfer import BUDGETS, SEEDS, TOLERANCES, summarize


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check():
    summary = json.loads((ROOT / "results/phase10_summary.json").read_text())
    packed = (ROOT / "results/phase10_transfer.json.gz").read_bytes()
    raw = gzip.decompress(packed)
    result = json.loads(raw)
    assert sha(packed) == summary["compressed_result_sha256"]
    assert sha(raw) == summary["full_result_sha256"]
    assert result["plan_sha256"] == sha((ROOT / "configs/phase10_plan.json").read_bytes())
    assert result["source_manifest_sha256"] == sha((ROOT / "configs/phase10_source_manifest.json").read_bytes())
    assert result["seeds"] == list(SEEDS) and result["budgets_words"] == list(BUDGETS)
    assert result["tolerances_turns"] == list(TOLERANCES)
    assert len(result["meetings"]) == 35
    assert len(result["per_query"]) == summary["query_method_budget_rows"] == 16104
    names = {m["meeting"] for m in result["meetings"]}
    assert len(names) == 35
    assert sum(m["topic_onsets"] for m in result["meetings"]) == 161
    assert sum(m["specific_queries"] for m in result["meetings"]) == 244
    for m in result["meetings"]:
        assert 1 <= m["online_segments"] <= m["turns"]
        assert m["online_segments"] == sum(m["online_close_reasons"].values())
        for method in ("online", "random"):
            variants = ([m["boundary_coverage"]["online"]] if method == "online"
                        else m["boundary_coverage"]["random"].values())
            for item in variants:
                assert all(0 <= item[str(t)] <= 1 for t in TOLERANCES)
                assert all(item[str(a)] <= item[str(b)] for a, b in zip(TOLERANCES, TOLERANCES[1:]))
        assert len(m["boundary_coverage"]["random"]) == 20
    seen = set()
    counts = Counter()
    for row in result["per_query"]:
        assert row["meeting"] in names and row["budget_words"] in BUDGETS
        assert row["method"] in ("online", "fixed", "random")
        assert (row["seed"] in SEEDS) if row["method"] == "random" else row["seed"] is None
        key = (row["meeting"], row["query_index"], row["method"], row["seed"], row["budget_words"])
        assert key not in seen
        seen.add(key)
        counts[row["meeting"], row["method"], row["seed"], row["budget_words"]] += 1
        assert 0 <= row["retrieved_gold_turns"] <= row["gold_turns"]
        assert math.isclose(row["recall"], row["retrieved_gold_turns"] / row["gold_turns"])
        assert 0 <= row["retrieved_words"] <= row["budget_words"]
        assert row["recall"] < 1 or row["all_evidence_structurally_feasible"]
    for m in result["meetings"]:
        for method, seeds in (("online", [None]), ("fixed", [None]), ("random", SEEDS)):
            for seed in seeds:
                for budget in BUDGETS:
                    assert counts[m["meeting"], method, seed, budget] == m["specific_queries"]
    recomputed = summarize(result["meetings"], result["per_query"])
    assert recomputed == result["summary"] == summary["summary"]
    print("Phase 10 provenance, 16104 rows, budgets, boundaries and all aggregates verified")


if __name__ == "__main__":
    check()
