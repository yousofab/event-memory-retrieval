"""Deterministic public package for Phase 8; no source text in artifacts."""
import gzip
import hashlib
import json
from pathlib import Path
from run_baselines import ROOT


def package(source=ROOT / "results/phase8_causal.json"):
    raw = source.read_bytes()
    data = json.loads(raw)
    if data["phase"] != 8 or len(data["locomo_per_question"]) != 10476 or len(data["external_per_question"]) != 5640:
        raise ValueError("Unexpected Phase 8 result dimensions")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    summary = {key: value for key, value in data.items()
               if key not in ("locomo_per_question", "external_per_question")}
    summary["full_result_sha256"] = hashlib.sha256(raw).hexdigest()
    summary["compressed_result_sha256"] = hashlib.sha256(packed).hexdigest()
    summary["locomo_result_rows"] = len(data["locomo_per_question"])
    summary["external_result_rows"] = len(data["external_per_question"])
    dst = ROOT / "results/phase8_causal.json.gz"
    manifest = ROOT / "results/phase8_summary.json"
    dst.write_bytes(packed)
    manifest.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if gzip.decompress(dst.read_bytes()) != raw:
        raise AssertionError("Compression round-trip failed")
    return dst, manifest


if __name__ == "__main__":
    print(*package(), sep="\n")
