"""Deterministically publish only numeric Phase 11 rows and aggregates."""
import gzip
import hashlib
import json

from run_baselines import ROOT


def package(source=ROOT / "results/phase11_retrieval.json"):
    raw = source.read_bytes()
    result = json.loads(raw)
    expected = 244 * (20 + 2 + 1) * 3
    if result["phase"] != 11 or len(result["per_query"]) != expected or len(result["meetings"]) != 35:
        raise ValueError("Incomplete Phase 11 result")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    compressed = ROOT / "results/phase11_retrieval.json.gz"
    summary = ROOT / "results/phase11_summary.json"
    compressed.write_bytes(packed)
    record = {key: value for key, value in result.items() if key != "per_query"}
    record["numeric_rows"] = expected
    record["full_result_sha256"] = hashlib.sha256(raw).hexdigest()
    record["compressed_result_sha256"] = hashlib.sha256(packed).hexdigest()
    summary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert gzip.decompress(packed) == raw
    return compressed, summary


if __name__ == "__main__":
    print(*package(), sep="\n")
