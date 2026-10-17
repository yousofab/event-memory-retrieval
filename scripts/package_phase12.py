"""Publish deterministic compact results; leave the large raw JSON ignored."""
import gzip
import hashlib
import json

from run_baselines import ROOT


def package(source=ROOT / "results/phase12_temporal.json"):
    raw = source.read_bytes()
    result = json.loads(raw)
    expected = 72 * 3 * 22
    if result["questions"] != 72 or len(result["rows"]) != expected:
        raise ValueError("Incomplete Phase 12 result")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    compressed = ROOT / "results/phase12_temporal.json.gz"
    summary = ROOT / "results/phase12_summary.json"
    compressed.write_bytes(packed)
    record = {key: value for key, value in result.items() if key != "rows"}
    record["numeric_rows"] = expected
    record["full_result_sha256"] = hashlib.sha256(raw).hexdigest()
    record["compressed_result_sha256"] = hashlib.sha256(packed).hexdigest()
    summary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert gzip.decompress(packed) == raw
    return compressed, summary


if __name__ == "__main__":
    print(*package(), sep="\n")
