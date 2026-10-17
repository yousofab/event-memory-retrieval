"""Validate packaged Phase 13 rows, metrics, and exact Phase 12 baseline parity."""
import gzip
import hashlib
import json
from collections import Counter

from run_baselines import ROOT
from run_phase13_provenance import assert_phase12_parity, summary


def validate():
    public = json.loads((ROOT / "results/phase13_summary.json").read_text())
    packed = (ROOT / "results/phase13_provenance.json.gz").read_bytes()
    assert hashlib.sha256(packed).hexdigest() == public["compressed_result_sha256"]
    raw = gzip.decompress(packed)
    assert hashlib.sha256(raw).hexdigest() == public["full_result_sha256"]
    full = json.loads(raw)
    rows, plan = full["rows"], full["plan"]
    assert len(rows) == public["numeric_rows"] == 4968
    assert full["source_sha256"] == plan["source_sha256"]
    assert assert_phase12_parity(rows) == public["phase12_exact_baseline_rows"] == 144
    counts = Counter((r["question_id"], r["budget_words"]) for r in rows)
    assert len(counts) == 216 and set(counts.values()) == {23}
    assert all(0 <= r["spent_words"] <= r["budget_words"] for r in rows)
    eligible = [r for r in rows if r["budget_words"] == 512 and r["method"] == "bm25_turn"
                and r["older_marked_available"]]
    assert len(eligible) == 70
    changed = {r["question_id"]: {} for r in rows}
    # Reproduce all aggregate counts other than the rank-order change audit,
    # which is copied from the run and checked against the 72 record ceiling.
    recomputed = summary(rows, plan, {qid: {"best": False, "newest": False, "other": False}
                                      for qid in changed})
    observed = public["summary"].copy()
    changed_counts = observed.pop("rank_lists_changed")
    recomputed.pop("rank_lists_changed")
    assert recomputed == observed
    assert all(0 <= n <= 72 for n in changed_counts.values())
    return {"rows": len(rows), "questions": 72, "phase12_parity": 144,
            "compressed_sha256": public["compressed_result_sha256"]}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
