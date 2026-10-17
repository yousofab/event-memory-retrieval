"""Recalculate publication invariants from compressed per-query numeric rows."""
import gzip
import hashlib
import json
from collections import Counter

from run_baselines import ROOT
from run_phase12_temporal import compact, summarize


def validate():
    summary = json.loads((ROOT / "results/phase12_summary.json").read_text())
    packed = (ROOT / "results/phase12_temporal.json.gz").read_bytes()
    assert hashlib.sha256(packed).hexdigest() == summary["compressed_result_sha256"]
    raw = gzip.decompress(packed)
    assert hashlib.sha256(raw).hexdigest() == summary["full_result_sha256"]
    full = json.loads(raw)
    rows, plan = full["rows"], full["plan"]
    assert summary["numeric_rows"] == len(rows) == 4752
    assert full["source_sha256"] == plan["source_sha256"]
    assert full["summary"] == summary["summary"] == summarize(rows, plan)
    grouped = Counter((r["question_id"], r["budget_words"]) for r in rows)
    assert len(grouped) == 72 * 3 and set(grouped.values()) == {22}
    assert all(0 <= r["spent_words"] <= r["budget_words"] for r in rows)
    assert all(not r["both_found"] or (r["older_found"] and r["later_found"]) for r in rows)
    assert all(not r["older_only"] or (r["older_found"] and not r["later_found"]) for r in rows)
    assert sum(not r["older_marked_available"] for r in rows if r["method"] == "bm25_turn" and
               r["budget_words"] == 1024) == 2
    return {"rows": len(rows), "questions": 72, "sha256": summary["compressed_result_sha256"]}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
