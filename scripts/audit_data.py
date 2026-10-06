"""Audit LoCoMo and freeze a text-only question manifest. Python standard library."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(data_path, protocol_path, output_path):
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    data_bytes = data_path.read_bytes()
    sha256 = hashlib.sha256(data_bytes).hexdigest()
    if sha256 != protocol["sha256"]:
        raise ValueError(f"Dataset SHA-256 mismatch: {sha256}")
    samples = json.loads(data_bytes)
    if not isinstance(samples, list):
        raise ValueError("Expected a list of conversations")
    dev, held = map(set, (protocol["development_conversations"], protocol["held_out_conversations"]))
    if dev & held or {s["sample_id"] for s in samples} != dev | held:
        raise ValueError("Split must be disjoint and cover the dataset exactly")

    totals, reasons, categories, per_conversation = Counter(), Counter(), Counter(), {}
    manifest = []
    for sample in samples:
        sid = sample["sample_id"]
        session_keys = sorted((k for k in sample["conversation"] if re.fullmatch(r"session_\d+", k)),
                              key=lambda k: int(k.split("_")[1]))
        turns = [turn for key in session_keys for turn in sample["conversation"][key]]
        ids = [turn["dia_id"] for turn in turns]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate dialog IDs in {sid}")
        by_id = dict(zip(ids, turns))
        counts = Counter(sessions=len(session_keys), turns=len(turns), questions=len(sample["qa"]))
        counts["image_turns"] = sum(bool(t.get("img_url")) for t in turns)
        counts["empty_text_turns"] = sum(not t.get("text") for t in turns)
        counts["missing_session_dates"] = sum(key + "_date_time" not in sample["conversation"] for key in session_keys)
        totals.update(counts)
        seen_eligible = set()
        for index, qa in enumerate(sample["qa"]):
            category = int(qa["category"])
            evidence = qa.get("evidence")
            if category not in protocol["included_categories"]:
                reason = "excluded_category"
            elif not isinstance(evidence, list) or not evidence:
                reason = "missing_evidence"
            elif any(not isinstance(e, str) or e not in by_id for e in evidence):
                reason = "unresolved_evidence"
            elif any(bool(by_id[e].get("img_url")) for e in evidence):
                reason = "image_evidence"
            elif (qa["question"], category, qa.get("answer"), tuple(evidence)) in seen_eligible:
                reason = "duplicate_eligible_question"
            else:
                reason = "included"
            reasons[reason] += 1
            if reason != "included":
                counts[reason] += 1
                continue
            seen_eligible.add((qa["question"], category, qa.get("answer"), tuple(evidence)))
            split = "development" if sid in dev else "held_out"
            item = {"sample_id": sid, "question_index": index, "category": category,
                    "evidence_ids": evidence, "split": split}
            manifest.append(item)
            categories[str(category)] += 1
            counts["included"] += 1
        per_conversation[sid] = dict(counts)
    if len(manifest) != reasons["included"]:
        raise AssertionError("Manifest count mismatch")
    output = {
        "dataset_sha256": sha256,
        "source_git_blob_sha1": protocol["git_blob_sha1"],
        "totals": dict(totals),
        "eligibility_reasons": dict(reasons),
        "included_by_category": dict(categories),
        "included_by_split": dict(Counter(x["split"] for x in manifest)),
        "per_conversation": per_conversation,
        "manifest": manifest
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "manifest"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--protocol", type=Path, default=ROOT / "configs/protocol.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase1_audit.json")
    args = parser.parse_args()
    run(args.data, args.protocol, args.output)
