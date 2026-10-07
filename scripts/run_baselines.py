"""Deterministic fixed-turn and session retrieval baselines on development data.

No QA answer, evidence ID, event summary, observation or session summary enters
segmentation or ranking. Gold evidence IDs are used only by score().
"""
import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"\w+", re.UNICODE)


def words(text):
    return TOKEN.findall(text.lower())


def sessions(sample):
    conversation = sample["conversation"]
    keys = sorted((key for key in conversation if re.fullmatch(r"session_\d+", key)),
                  key=lambda key: int(key.split("_")[1]))
    return [(key, conversation[key]) for key in keys]


def make_segments(sample, method, target_words):
    result = []
    for session_key, turns in sessions(sample):
        groups = [turns] if method == "session" else []
        if method == "fixed":
            group, size = [], 0
            for turn in turns:
                length = len(words(turn.get("text") or ""))
                if group and size + length > target_words:
                    groups.append(group)
                    group, size = [], 0
                group.append(turn)
                size += length
            if group:
                groups.append(group)
        for group in groups:
            ids = [turn["dia_id"] for turn in group]
            tokens = [token for turn in group for token in words(turn.get("text") or "")]
            result.append({"id": f"{session_key}:{len(result)}", "turn_ids": ids,
                           "tokens": tokens, "word_cost": len(tokens)})
    return result


def rank(query, segments):
    """Same BM25 formula, tokenizer, and constants for both segmentations."""
    n = len(segments)
    if not n:
        return []
    lengths = [len(segment["tokens"]) for segment in segments]
    average = max(sum(lengths) / n, 1)
    term_freqs = [Counter(segment["tokens"]) for segment in segments]
    df = Counter(term for tf in term_freqs for term in tf)
    query_terms = set(words(query))
    scores = []
    for index, tf in enumerate(term_freqs):
        score = 0.0
        for term in query_terms & tf.keys():
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            count = tf[term]
            score += idf * count * 2.2 / (count + 1.2 * (0.25 + 0.75 * lengths[index] / average))
        scores.append(score)
    return sorted(range(n), key=lambda index: (-scores[index], index))


def retrieve(query, segments, budget):
    selected, remaining = [], budget
    for index in rank(query, segments):
        cost = segments[index]["word_cost"]
        if cost <= remaining:
            selected.append(index)
            remaining -= cost
    return selected


def run(data_path, manifest_path, protocol_path, output_path, target_words, budgets):
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    raw = data_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != protocol["sha256"]:
        raise ValueError("Dataset checksum differs from frozen protocol")
    audit = json.loads(manifest_path.read_text(encoding="utf-8"))
    if audit["dataset_sha256"] != digest:
        raise ValueError("Manifest checksum differs from dataset")
    samples = {item["sample_id"]: item for item in json.loads(raw)}
    dev = set(protocol["development_conversations"])
    manifest = [item for item in audit["manifest"] if item["split"] == "development"]
    if len(manifest) != audit["included_by_split"]["development"] or {m["sample_id"] for m in manifest} != dev:
        raise ValueError("Development manifest is incomplete")
    if target_words <= 0 or any(b <= 0 for b in budgets) or len(set(budgets)) != len(budgets):
        raise ValueError("Target and distinct budgets must be positive")
    rows = []
    segment_stats = {}
    for sid in sorted(dev):
        sample = samples[sid]
        ids = {turn["dia_id"] for _, turns in sessions(sample) for turn in turns}
        prepared = {method: make_segments(sample, method, target_words) for method in ("fixed", "session")}
        for method, segments in prepared.items():
            all_ids = [dia for segment in segments for dia in segment["turn_ids"]]
            if len(all_ids) != len(set(all_ids)) or set(all_ids) != ids:
                raise AssertionError(f"Turn partition invalid: {sid}, {method}")
            segment_stats[f"{sid}/{method}"] = {
                "segments": len(segments), "oversized_single_turn_segments": sum(
                    len(s["turn_ids"]) == 1 and s["word_cost"] > target_words for s in segments),
                "max_segment_words": max(s["word_cost"] for s in segments),
            }
        for item in (m for m in manifest if m["sample_id"] == sid):
            qa = sample["qa"][item["question_index"]]
            gold = set(item["evidence_ids"])
            for method, segments in prepared.items():
                for budget in sorted(budgets):
                    chosen = retrieve(qa["question"], segments, budget)
                    found = {dia for index in chosen for dia in segments[index]["turn_ids"]}
                    used = sum(segments[index]["word_cost"] for index in chosen)
                    if used > budget:
                        raise AssertionError("Retrieved word budget exceeded")
                    rows.append({"sample_id": sid, "question_index": item["question_index"],
                                 "category": item["category"], "method": method, "budget_words": budget,
                                 "all_evidence": gold <= found, "evidence_found": len(gold & found),
                                 "evidence_total": len(gold), "retrieved_words": used,
                                 "retrieved_segments": len(chosen)})
    summary = []
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["budget_words"], row["sample_id"])].append(row)
    for (method, budget, sid), group in sorted(grouped.items()):
        summary.append({"method": method, "budget_words": budget, "sample_id": sid,
                        "questions": len(group), "all_evidence_count": sum(r["all_evidence"] for r in group),
                        "all_evidence_rate": sum(r["all_evidence"] for r in group) / len(group),
                        "mean_retrieved_words": sum(r["retrieved_words"] for r in group) / len(group)})
    result = {"dataset_sha256": digest, "split": "development_only",
              "target_fixed_words": target_words, "budgets_words": sorted(budgets),
              "cost_definition": "regex Unicode word tokens in turn text only; whole segments selected; no truncation",
              "ranker": "BM25 k1=1.2 b=0.75; lowercase Unicode word tokens; query terms deduplicated; score descending then original segment order; greedy skip-if-over-budget",
              "segment_stats": segment_stats, "per_conversation": summary, "per_question": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in summary:
        print(f"{row['method']:7} {row['budget_words']:4} {row['sample_id']:7} "
              f"{row['all_evidence_count']:3}/{row['questions']:3} ({row['all_evidence_rate']:.3f}) "
              f"mean words {row['mean_retrieved_words']:.1f}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/phase1_audit.json")
    parser.add_argument("--protocol", type=Path, default=ROOT / "configs/protocol.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase2_development_baselines.json")
    parser.add_argument("--target-words", type=int, default=128)
    parser.add_argument("--budgets", nargs="+", type=int, default=[512, 1024, 2048])
    args = parser.parse_args()
    run(args.data, args.manifest, args.protocol, args.output, args.target_words, args.budgets)
