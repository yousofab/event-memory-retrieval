"""Deterministically package Phase 10 numeric records, excluding raw text."""
import gzip
import hashlib
import json
from run_baselines import ROOT


def package(source=ROOT / "results/phase10_transfer.json"):
    raw = source.read_bytes()
    data = json.loads(raw)
    expected = 244 * (2 + 20) * 3
    if data["phase"] != 10 or len(data["meetings"]) != 35 or len(data["per_query"]) != expected:
        raise ValueError("Incomplete Phase 10 result")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    summary = {k: v for k, v in data.items() if k != "per_query"}
    summary["full_result_sha256"] = hashlib.sha256(raw).hexdigest()
    summary["compressed_result_sha256"] = hashlib.sha256(packed).hexdigest()
    summary["query_method_budget_rows"] = expected
    target = ROOT / "results/phase10_transfer.json.gz"
    manifest = ROOT / "results/phase10_summary.json"
    target.write_bytes(packed)
    manifest.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert gzip.decompress(target.read_bytes()) == raw
    return target, manifest


if __name__ == "__main__":
    print(*package(), sep="\n")
