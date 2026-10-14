"""Validate Phase 11 published rows, provenance, budgets and Phase 10 baseline."""
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict

from run_baselines import ROOT
from run_phase11_hierarchical import summary


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def validate():
    record = json.loads((ROOT / "results/phase11_summary.json").read_bytes())
    compressed = (ROOT / "results/phase11_retrieval.json.gz").read_bytes()
    raw = gzip.decompress(compressed)
    data = json.loads(raw)
    old = json.loads(gzip.decompress((ROOT / "results/phase10_transfer.json.gz").read_bytes()))
    assert sha(compressed) == record["compressed_result_sha256"]
    assert sha(raw) == record["full_result_sha256"]
    assert data["plan_sha256"] == sha((ROOT / "configs/phase11_plan.json").read_bytes())
    assert data["source_manifest_sha256"] == sha((ROOT / "configs/phase10_source_manifest.json").read_bytes())
    assert data["phase10_full_result_sha256"] == record["phase10_full_result_sha256"]
    assert data["phase10_full_result_sha256"] == sha(gzip.decompress((ROOT / "results/phase10_transfer.json.gz").read_bytes()))
    assert data["flat_rows_checked_against_phase10"] == 16104
    assert len(data["meetings"]) == 35 and len(data["per_query"]) == record["numeric_rows"] == 16836
    assert data["source_audit"] == old["source_audit"]
    assert data["summary"] == record["summary"]
    old_rows = {(r["meeting"], r["query_index"], r["method"], r["seed"], r["budget_words"]): r
                for r in old["per_query"]}
    counts = Counter()
    keys = set()
    for r in data["per_query"]:
        key = r["meeting"], r["query_index"], r["method"], r["seed"], r["budget_words"]
        assert key not in keys
        keys.add(key)
        assert r["budget_words"] in (512, 1024, 2048)
        assert 0 <= r["hier_gold"] <= r["gold_turns"]
        assert 0 <= r["hier_words"] <= r["budget_words"]
        counts[r["method"], r["seed"], r["budget_words"]] += 1
        if r["method"] == "global_turn":
            assert r["seed"] is None
            continue
        previous = old_rows[key]
        assert (r["gold_turns"], r["flat_gold"], r["flat_words"]) == (
            previous["gold_turns"], previous["retrieved_gold_turns"], previous["retrieved_words"])
        assert 0 <= r["flat_gold"] <= r["flat_turns"]
        assert 0 <= r["hier_gold"] <= r["selected_turns"] <= r["candidate_turns"]
        assert r["hier_gold"] <= r["candidate_gold"] <= r["gold_turns"]
        assert 0 <= r["candidate_words"] <= 4 * r["budget_words"]
        assert 0 <= r["flat_words"] <= r["budget_words"]
    assert len(keys) == 16836
    for budget in (512, 1024, 2048):
        for method, seeds in (("online", [None]), ("fixed", [None]),
                              ("global_turn", [None]), ("random", range(20))):
            for seed in seeds:
                assert counts[method, seed, budget] == 244
    calculated = summary(data["per_query"], data["meetings"])
    assert calculated == data["summary"]
    for budget in (512, 1024, 2048):
        b = str(budget)
        assert math.isclose(calculated["budgets"][b]["online"]["flat_gold"],
                            old["summary"]["retrieval"][b]["online"])
    print("Phase 11 source and plan hashes, 16,836 rows, all 16,104 paired Phase 10 rows, budgets and aggregates verified")


if __name__ == "__main__":
    validate()
