"""Exploratory, label-free LSA event segmentation with the frozen BM25 retriever."""
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import scipy
import sklearn
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from run_baselines import ROOT, rank, sessions, words
from run_held_out import aggregate, sign_flip_paired_two_sided


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def training_texts(samples, development_ids):
    """Use conversational turns only, without any QA or supplied summaries."""
    return [turn.get("text") or ""
            for sid in sorted(development_ids)
            for _, turns in sessions(samples[sid]) for turn in turns]


def fit_lsa(texts, plan):
    settings = plan["vectorizer"]
    vectorizer = TfidfVectorizer(
        token_pattern=settings["token_pattern"], lowercase=settings["lowercase"],
        ngram_range=tuple(settings["ngram_range"]), min_df=settings["min_df"],
        max_features=settings["max_features"], norm=settings["norm"],
        use_idf=settings["use_idf"], smooth_idf=settings["smooth_idf"])
    matrix = vectorizer.fit_transform(texts)
    dimensions = plan["svd_components"]
    if matrix.shape[1] <= dimensions or matrix.shape[0] <= dimensions:
        raise ValueError("Development vocabulary/corpus is too small for the frozen SVD dimension")
    svd = TruncatedSVD(n_components=dimensions, n_iter=plan["svd_n_iter"],
                       random_state=plan["random_state"])
    svd.fit(matrix)
    return vectorizer, svd, {"training_turns": len(texts), "vocabulary_size": matrix.shape[1],
                             "dimensions": dimensions,
                             "explained_variance_ratio_sum": float(svd.explained_variance_ratio_.sum()),
                             "training_text_sha256": hashlib.sha256(
                                 json.dumps(texts, ensure_ascii=False).encode("utf-8")).hexdigest()}


def window_distance(left, right):
    """Cosine distance of adjacent mean turn vectors; silence is not a boundary."""
    a, b = left.mean(axis=0), right.mean(axis=0)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-15:
        return 0.0
    return 1.0 - float(np.clip(np.dot(a, b) / denom, -1.0, 1.0))


def semantic_segments(sample, vectorizer, svd, minimum, preferred, maximum, window):
    if not (0 < minimum <= preferred <= maximum) or window < 1:
        raise ValueError("Invalid segmentation settings")
    result = []
    for session_key, turns in sessions(sample):
        if not turns:
            continue
        token_lists = [words(turn.get("text") or "") for turn in turns]
        vectors = normalize(svd.transform(vectorizer.transform(
            [turn.get("text") or "" for turn in turns])), norm="l2")
        boundary = {i: window_distance(vectors[max(0, i-window):i],
                                       vectors[i:i+window]) for i in range(1, len(turns))}
        start = 0
        while start < len(turns):
            size, valid, admissible = 0, [], []
            for end in range(start + 1, len(turns) + 1):
                size += len(token_lists[end - 1])
                if size > maximum and end > start + 1:
                    break
                valid.append((end, size))
                if size >= minimum and end < len(turns):
                    admissible.append((end, size))
                if size > maximum:  # Same oversized-single-turn exception as Phase 3.
                    break
            if not valid:
                raise AssertionError("Missing segment endpoint")
            if valid[-1][0] == len(turns):
                stop = len(turns)
            elif admissible:
                stop = max(admissible, key=lambda candidate:
                           (boundary[candidate[0]], -abs(candidate[1] - preferred), -candidate[0]))[0]
            else:
                stop = valid[-1][0]
            group = turns[start:stop]
            tokens = [token for subturn in token_lists[start:stop] for token in subturn]
            result.append({"id": f"{session_key}:{len(result)}",
                           "turn_ids": [turn["dia_id"] for turn in group],
                           "tokens": tokens, "word_cost": len(tokens)})
            start = stop
    return result


def evidence_diagnostics(segments, gold_ids, budget):
    carrying = [segment for segment in segments if gold_ids.intersection(segment["turn_ids"])]
    return {"gold_segment_word_cost": sum(segment["word_cost"] for segment in carrying),
            "gold_segment_count": len(carrying),
            "structural_budget": sum(segment["word_cost"] for segment in carrying) > budget}


def select_ranked(ordered, segments, budget):
    """Same skip-if-over-budget policy as run_baselines.retrieve()."""
    chosen, remaining = [], budget
    for index in ordered:
        cost = segments[index]["word_cost"]
        if cost <= remaining:
            chosen.append(index)
            remaining -= cost
    return chosen


def validate_inputs(raw, plan, frozen, protocol, audit, split):
    digest = hashlib.sha256(raw).hexdigest()
    if digest != plan["dataset_sha256"] or digest != protocol["sha256"] or digest != frozen["dataset_sha256"]:
        raise ValueError("Pinned dataset mismatch")
    if audit["dataset_sha256"] != digest:
        raise ValueError("Eligibility manifest checksum mismatch")
    if (frozen["event_minimum_words"], frozen["event_preferred_words"],
            frozen["event_maximum_words"], frozen["event_window_turns"]) != (64, 128, 160, 3):
        raise ValueError("Unexpected Phase 3 frozen segmentation")
    expected = set(protocol["development_conversations"] if split == "development" else
                   protocol["held_out_conversations"])
    selected = [item for item in audit["manifest"] if item["split"] == split]
    if len(selected) != audit["included_by_split"][split] or {i["sample_id"] for i in selected} != expected:
        raise ValueError("Split manifest invalid")
    if len({(i["sample_id"], i["question_index"]) for i in selected}) != len(selected):
        raise ValueError("Repeated question in eligibility manifest")
    return digest, expected, selected


def paired_analysis(rows, summary, budget):
    lookup = {(r["method"], r["budget_words"], r["sample_id"]): r for r in summary}
    sids = sorted({r["sample_id"] for r in rows})
    differences = {sid: lookup[("semantic_lsa", budget, sid)]["all_evidence_rate"] -
                    lookup[("event", budget, sid)]["all_evidence_rate"] for sid in sids}
    return {"conversation_differences_semantic_minus_lexical": differences,
            "mean_conversation_difference": sum(differences.values()) / len(differences),
            "exact_two_sided_sign_flip_reference_exploratory":
                sign_flip_paired_two_sided(list(differences.values()))}


def run(data_path, output_path, split):
    if output_path.exists():
        raise FileExistsError("Phase 6 result exists; choose a fresh output path")
    plan_path = ROOT / "configs/phase6_semantic_plan.json"
    frozen_path = ROOT / "configs/phase3_frozen.json"
    manifest_path = ROOT / "results/phase1_audit.json"
    protocol_path = ROOT / "configs/protocol.json"
    previous_path = ROOT / "results/phase4_held_out.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    audit = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw = data_path.read_bytes()
    digest, expected, selected = validate_inputs(raw, plan, frozen, protocol, audit, split)
    samples = {sample["sample_id"]: sample for sample in json.loads(raw)}
    if len(samples) != 10 or not set(protocol["development_conversations"]).issubset(samples):
        raise ValueError("Development conversations absent")
    before = time.perf_counter()
    vectorizer, svd, training = fit_lsa(training_texts(samples, protocol["development_conversations"]), plan)
    training_seconds = time.perf_counter() - before
    budgets = sorted([frozen["primary_budget_words"]] + frozen["secondary_budgets_words"])
    rows, segment_stats, segmentation_seconds, retrieval_seconds = [], [], 0.0, 0.0
    for sid in sorted(expected):
        begin = time.perf_counter()
        sample = samples[sid]
        segments = semantic_segments(sample, vectorizer, svd, frozen["event_minimum_words"],
                                     frozen["event_preferred_words"], frozen["event_maximum_words"],
                                     frozen["event_window_turns"])
        segmentation_seconds += time.perf_counter() - begin
        observed = [dia for s in segments for dia in s["turn_ids"]]
        required = [turn["dia_id"] for _, turns in sessions(sample) for turn in turns]
        if observed != required or len(observed) != len(set(observed)):
            raise AssertionError("Turn partition invalid")
        segment_stats.append({"sample_id": sid, "method": "semantic_lsa", "segments": len(segments),
                              "source_words": sum(s["word_cost"] for s in segments),
                              "mean_segment_words": sum(s["word_cost"] for s in segments) / len(segments),
                              "max_segment_words": max(s["word_cost"] for s in segments),
                              "oversized_single_turn_segments": sum(
                                  s["word_cost"] > frozen["event_maximum_words"] and len(s["turn_ids"]) == 1
                                  for s in segments)})
        for item in (m for m in selected if m["sample_id"] == sid):
            query = sample["qa"][item["question_index"]]["question"]
            gold = set(item["evidence_ids"])
            retrieval_start = time.perf_counter()
            ordered = rank(query, segments)
            for budget in budgets:
                chosen = select_ranked(ordered, segments, budget)
                found = {dia for index in chosen for dia in segments[index]["turn_ids"]}
                used = sum(segments[index]["word_cost"] for index in chosen)
                if used > budget:
                    raise AssertionError("Retrieved word budget exceeded")
                diagnostic = evidence_diagnostics(segments, gold, budget)
                success = gold <= found
                if success and diagnostic["structural_budget"]:
                    raise AssertionError("Impossible retrieval reported as success")
                rows.append({"sample_id": sid, "question_index": item["question_index"],
                             "category": item["category"], "method": "semantic_lsa",
                             "budget_words": budget, "all_evidence": success,
                             "evidence_found": len(gold & found), "evidence_total": len(gold),
                             "retrieved_words": used, "retrieved_segments": len(chosen),
                             "gold_turn_group": "one" if len(gold) == 1 else "multiple",
                             "gold_session_group": "one" if len({x.split(':')[0] for x in gold}) == 1 else "multiple",
                             **diagnostic})
            retrieval_seconds += time.perf_counter() - retrieval_start
    summary = aggregate(rows)
    paired = None
    previous_sha = None
    discordance = None
    if split == "held_out":
        recorded = json.loads(previous_path.read_text(encoding="utf-8"))
        previous_sha = sha256(previous_path)
        if (recorded["dataset_sha256"] != digest or
                recorded["frozen_config_sha256"] != sha256(frozen_path) or
                recorded["manifest_sha256"] != sha256(manifest_path)):
            raise ValueError("Phase 4 frozen comparison has changed")
        earlier = {(r["sample_id"], r["question_index"]): r["all_evidence"] for r in recorded["per_question"]
                   if r["method"] == "event" and r["budget_words"] == frozen["primary_budget_words"]}
        fresh = {(r["sample_id"], r["question_index"]): r["all_evidence"] for r in rows
                 if r["budget_words"] == frozen["primary_budget_words"]}
        if earlier.keys() != fresh.keys():
            raise ValueError("The paired question set differs from Phase 4")
        discordance = {"semantic_only": sum(fresh[k] and not earlier[k] for k in fresh),
                       "lexical_only": sum(earlier[k] and not fresh[k] for k in fresh),
                       "both": sum(fresh[k] and earlier[k] for k in fresh),
                       "neither": sum(not fresh[k] and not earlier[k] for k in fresh)}
        old_summary = recorded["per_conversation"]
        old_rows = [x for x in old_summary if x["method"] == "event" and
                    x["budget_words"] == frozen["primary_budget_words"]]
        paired = paired_analysis(rows + [r for r in recorded["per_question"]
                                     if r["method"] == "event" and
                                     r["budget_words"] == frozen["primary_budget_words"]],
                                     summary + old_rows, frozen["primary_budget_words"])
    output = {"phase": 6, "split": split, "interpretation": "post-Phase-4 exploratory extension",
              "dataset_sha256": digest, "phase6_plan_sha256": sha256(plan_path),
              "frozen_config_sha256": sha256(frozen_path), "manifest_sha256": sha256(manifest_path),
              "phase4_result_sha256": previous_sha,
              "primary_budget_words": frozen["primary_budget_words"], "budgets_words": budgets,
              "question_count": len(selected), "conversation_count": len(expected),
              "training": training,
              "dependencies": {"python": __import__("sys").version.split()[0], "numpy": np.__version__,
                               "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
              "timing_seconds_observed_machine": {"model_fit": training_seconds,
                                                  "segmentation": segmentation_seconds,
                                                  "retrieval": retrieval_seconds},
              "segment_stats": segment_stats, "per_conversation": summary,
              "paired_primary": paired,
              "discordance_primary_against_frozen_lexical": discordance,
              "per_question": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Phase 6 {split}: {len(rows)} rows, {len(selected)} questions, ",
          f"LSA fit {training_seconds:.2f}s, segmentation {segmentation_seconds:.2f}s, "
          f"retrieval {retrieval_seconds:.2f}s")
    for item in summary:
        if item["budget_words"] == frozen["primary_budget_words"]:
            print(item["sample_id"], item["all_evidence_count"], "/", item["questions"])
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--split", choices=("development", "held_out"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run(args.data, args.output or ROOT / f"results/phase6_{args.split}_lsa.json", args.split)
