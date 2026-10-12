"""Make deterministic compact/public Phase 7 records from the full local JSON."""
import gzip
import hashlib
import json
from pathlib import Path

from run_baselines import ROOT


def package(source=ROOT / "results/phase7_external.json"):
    raw = source.read_bytes()
    result = json.loads(raw)
    if result["phase"] != 7 or len(result["per_question"]) != 5640:
        raise ValueError("Unexpected full Phase 7 result")
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    gz_path = ROOT / "results/phase7_external.json.gz"
    summary_path = ROOT / "results/phase7_summary.json"
    summary = {k: v for k, v in result.items() if k != "per_question"}
    summary["full_result_sha256"] = hashlib.sha256(raw).hexdigest()
    summary["compressed_result_sha256"] = hashlib.sha256(compressed).hexdigest()
    summary["full_result_rows"] = len(result["per_question"])
    gz_path.write_bytes(compressed)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if gzip.decompress(gz_path.read_bytes()) != raw:
        raise AssertionError("Compressed result does not round-trip")
    return gz_path, summary_path


if __name__ == "__main__":
    print(*package(), sep="\n")
