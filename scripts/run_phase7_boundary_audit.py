"""Post hoc, label-free description of why external segmenters often agree."""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

from run_baselines import ROOT, words
from run_event_development import event_segments
from run_phase6_semantic import fit_lsa, semantic_segments, training_texts
from run_phase7_external import public_sample, sha256


def endpoints(segments):
    return tuple(s["turn_ids"][-1] for s in segments)


def run(source_path, locomo_path, output_path):
    if output_path.exists():
        raise FileExistsError("Use a fresh diagnostic path")
    plan = json.loads((ROOT / "configs/phase7_external_plan.json").read_text(encoding="utf-8"))
    if sha256(source_path) != plan["external_dataset"]["sha256"]:
        raise ValueError("External source mismatch")
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    phase6 = json.loads((ROOT / "configs/phase6_semantic_plan.json").read_text(encoding="utf-8"))
    if sha256(locomo_path) != protocol["sha256"]:
        raise ValueError("Training source mismatch")
    frozen = json.loads((ROOT / "configs/phase3_frozen.json").read_text(encoding="utf-8"))
    locomo = {x["sample_id"]: x for x in json.loads(locomo_path.read_text(encoding="utf-8"))}
    vectorizer, svd, _ = fit_lsa(training_texts(locomo, protocol["development_conversations"]), phase6)
    counts = Counter()
    for record in json.loads(source_path.read_text(encoding="utf-8")):
        if record["question_id"].endswith("_abs"):
            continue
        sample = public_sample(record)
        lexical = event_segments(sample, frozen["event_minimum_words"],
                                 frozen["event_preferred_words"], frozen["event_maximum_words"],
                                 frozen["event_window_turns"])
        semantic = semantic_segments(sample, vectorizer, svd,
                                     frozen["event_minimum_words"], frozen["event_preferred_words"],
                                     frozen["event_maximum_words"], frozen["event_window_turns"])
        counts["questions"] += 1
        counts["identical_partitions"] += endpoints(lexical) == endpoints(semantic)
        for method, segments in (("lexical", lexical), ("semantic_lsa", semantic)):
            counts[f"segments_{method}"] += len(segments)
            counts[f"single_turn_segments_{method}"] += sum(len(s["turn_ids"]) == 1 for s in segments)
            counts[f"oversized_single_turn_segments_{method}"] += sum(
                len(s["turn_ids"]) == 1 and s["word_cost"] > frozen["event_maximum_words"]
                for s in segments)
        left = set(endpoints(lexical))
        right = set(endpoints(semantic))
        counts["shared_segment_endpoints"] += len(left & right)
        counts["different_segment_endpoints"] += len(left ^ right)
        for session in record["haystack_sessions"]:
            for turn in session:
                n = len(words(turn["content"]))
                counts["turns"] += 1
                counts["turns_over_160_words"] += n > frozen["event_maximum_words"]
    recorded_path = ROOT / "results/phase7_external.json"
    raw = (recorded_path.read_bytes() if recorded_path.exists() else
           gzip.decompress((ROOT / "results/phase7_external.json.gz").read_bytes()))
    result = {"status": "post_hoc_label_free_diagnostic", "external_dataset_sha256": sha256(source_path),
              "phase7_result_sha256": hashlib.sha256(raw).hexdigest(),
              "counts": dict(sorted(counts.items()))}
    recorded = json.loads(raw)
    if (counts["questions"] != recorded["audit_counts"]["answerable"] or
            counts["segments_lexical"] != recorded["audit_counts"]["segments_event"] or
            counts["segments_semantic_lsa"] != recorded["audit_counts"]["segments_semantic_lsa"]):
        raise AssertionError("Segment totals differ from Phase 7 record")
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--external", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    p.add_argument("--locomo", type=Path, default=ROOT / "data/raw/locomo10.json")
    p.add_argument("--output", type=Path, default=ROOT / "results/phase7_boundary_audit.json")
    args = p.parse_args()
    print(run(args.external, args.locomo, args.output))
