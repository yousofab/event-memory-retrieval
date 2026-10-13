"""Deterministically package Phase 9 numeric records, without conversation text."""
import gzip
import hashlib
import json
from pathlib import Path
from run_baselines import ROOT


def package(source=ROOT / "results/phase9_controls.json"):
    raw = source.read_bytes()
    data = json.loads(raw)
    if data["phase"] != 9 or len(data["per_question"]) != 52380:
        raise ValueError("Unexpected Phase 9 result")
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    summary = {k: v for k, v in data.items() if k != "per_question"}
    summary["full_result_sha256"] = hashlib.sha256(raw).hexdigest()
    summary["compressed_result_sha256"] = hashlib.sha256(packed).hexdigest()
    summary["question_seed_budget_rows"] = len(data["per_question"])
    target = ROOT / "results/phase9_controls.json.gz"
    manifest = ROOT / "results/phase9_summary.json"
    target.write_bytes(packed)
    manifest.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if gzip.decompress(target.read_bytes()) != raw:
        raise AssertionError("Package round trip failed")
    return target, manifest


if __name__ == "__main__":
    print(*package(), sep="\n")
