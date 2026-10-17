"""Deterministic, non-transcript package for Phase 13."""
import gzip
import hashlib
import json

from run_baselines import ROOT


def package(source=ROOT / "results/phase13_provenance.json"):
    raw = source.read_bytes()
    result = json.loads(raw)
    expected = 72 * 3 * (3 + 20)
    if result["questions"] != 72 or len(result["rows"]) != expected or result["phase12_exact_baseline_rows"] != 144:
        raise ValueError("Incomplete Phase 13 result")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    compressed = ROOT / "results/phase13_provenance.json.gz"
    summary = ROOT / "results/phase13_summary.json"
    compressed.write_bytes(packed)
    public = {k: v for k, v in result.items() if k != "rows"}
    public.update({"numeric_rows": expected,
                   "full_result_sha256": hashlib.sha256(raw).hexdigest(),
                   "compressed_result_sha256": hashlib.sha256(packed).hexdigest()})
    summary.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert gzip.decompress(packed) == raw
    return compressed, summary


if __name__ == "__main__":
    print(*package(), sep="\n")
