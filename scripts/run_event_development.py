"""Unsupervised lexical change-point segmentation and development-only selection."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from run_baselines import ROOT, retrieve, sessions, words


def cosine_dissimilarity(left, right, idf):
    a = Counter(token for turn in left for token in turn)
    b = Counter(token for turn in right for token in turn)
    aa = sum((value * idf[token]) ** 2 for token, value in a.items())
    bb = sum((value * idf[token]) ** 2 for token, value in b.items())
    if not aa or not bb:
        return 0.0
    dot = sum(value * b[token] * idf[token] ** 2 for token, value in a.items())
    return 1.0 - dot / math.sqrt(aa * bb)


def event_segments(sample, minimum, preferred, maximum, window):
    if not (0 < minimum <= preferred <= maximum) or window < 1:
        raise ValueError("Invalid segmentation settings")
    result = []
    for session_key, turns in sessions(sample):
        texts = [words(turn.get("text") or "") for turn in turns]
        df = Counter(token for tokens in texts for token in set(tokens))
        idf = {token: 1 + math.log((len(texts) + 1) / (count + 1)) for token, count in df.items()}
        boundary = {i: cosine_dissimilarity(texts[max(0, i-window):i],
                                            texts[i:i+window], idf)
                    for i in range(1, len(turns))}
        start = 0
        while start < len(turns):
            size, valid, admissible = 0, [], []
            for end in range(start + 1, len(turns) + 1):
                size += len(texts[end - 1])
                if size > maximum and end > start + 1:
                    break
                valid.append((end, size))
                if size >= minimum and end < len(turns):
                    admissible.append((end, size))
                if size > maximum:  # One long turn stays intact.
                    break
            if not valid:
                raise AssertionError("Missing segment endpoint")
            if valid[-1][0] == len(turns):
                stop = len(turns)
            elif admissible:
                stop = max(admissible, key=lambda candidate:
                           (boundary[candidate[0]], -abs(candidate[1] - preferred), -candidate[0]))[0]
            else:
                stop = valid[-1][0]  # Short forced piece or oversized single turn.
            group = turns[start:stop]
            tokens = [token for subturn in texts[start:stop] for token in subturn]
            result.append({"id": f"{session_key}:{len(result)}",
                           "turn_ids": [turn["dia_id"] for turn in group],
                           "tokens": tokens, "word_cost": len(tokens)})
            start = stop
    return result


def run():
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    search = json.loads((ROOT / "configs/phase3_search.json").read_text(encoding="utf-8"))
    raw = (ROOT / "data/raw/locomo10.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != protocol["sha256"]:
        raise ValueError("Dataset SHA-256 mismatch")
    audit = json.loads((ROOT / "results/phase1_audit.json").read_text(encoding="utf-8"))
    if audit["dataset_sha256"] != digest:
        raise ValueError("Phase 1 audit checksum mismatch")
    baseline = json.loads((ROOT / "results/phase2_development_baselines.json").read_text(encoding="utf-8"))
    if baseline["dataset_sha256"] != digest or baseline["target_fixed_words"] != search["preferred_segment_words"]:
        raise ValueError("Baseline and event run are inconsistent")
    samples = {sample["sample_id"]: sample for sample in json.loads(raw)}
    development = set(protocol["development_conversations"])
    selected = [item for item in audit["manifest"] if item["split"] == "development"]
    if {item["sample_id"] for item in selected} != development or len(selected) != audit["included_by_split"]["development"]:
        raise ValueError("Development manifest invalid")
    budgets = sorted([search["selection_budget_words"]] + search["other_reported_budgets_words"])
    rows, summaries, candidates = [], [], []
    for config in search["candidates"]:
        label = f"w{config['window_turns']}-max{config['maximum_segment_words']}"
        candidates.append(label)
        for sid in sorted(development):
            sample = samples[sid]
            segments = event_segments(sample, search["minimum_segment_words"],
                                      search["preferred_segment_words"], config["maximum_segment_words"],
                                      config["window_turns"])
            all_ids = [dia for seg in segments for dia in seg["turn_ids"]]
            expected = [turn["dia_id"] for _, turns in sessions(sample) for turn in turns]
            if all_ids != expected or len(all_ids) != len(set(all_ids)):
                raise AssertionError("The segmenter must partition the conversation in order")
            for item in (i for i in selected if i["sample_id"] == sid):
                question = sample["qa"][item["question_index"]]["question"]
                evidence = set(item["evidence_ids"])
                for budget in budgets:
                    chosen = retrieve(question, segments, budget)
                    found = {dia for index in chosen for dia in segments[index]["turn_ids"]}
                    used = sum(segments[index]["word_cost"] for index in chosen)
                    if used > budget:
                        raise AssertionError("Budget exceeded")
                    rows.append({"config": label, "sample_id": sid, "question_index": item["question_index"],
                                 "category": item["category"], "budget_words": budget,
                                 "all_evidence": evidence <= found, "evidence_found": len(evidence & found),
                                 "evidence_total": len(evidence), "retrieved_words": used})
            summaries.append({"config": label, "sample_id": sid, "segments": len(segments),
                              "segment_words_mean": sum(s["word_cost"] for s in segments) / len(segments),
                              "max_segment_words_observed": max(s["word_cost"] for s in segments)})
    groups = defaultdict(list)
    for row in rows:
        groups[(row["config"], row["budget_words"], row["sample_id"])].append(row)
    scores = []
    for label in candidates:
        rates = []
        for sid in sorted(development):
            group = groups[(label, search["selection_budget_words"], sid)]
            rates.append(sum(row["all_evidence"] for row in group) / len(group))
        config = next(c for c in search["candidates"] if label == f"w{c['window_turns']}-max{c['maximum_segment_words']}")
        scores.append({"config": label, "conversation_rates": rates,
                       "mean_conversation_rate": sum(rates) / len(rates), **config})
    winner = sorted(scores, key=lambda x: (-x["mean_conversation_rate"],
                                            x["maximum_segment_words"], x["window_turns"]))[0]
    output = {"dataset_sha256": digest, "split": "development_only", "search": search,
              "selection_scores": scores, "selected": winner, "segment_stats": summaries,
              "per_question": rows}
    dest = ROOT / "results/phase3_development_event.json"
    dest.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    frozen = {"dataset_sha256": digest, "development_selected_config": winner["config"],
              "event_minimum_words": search["minimum_segment_words"],
              "event_preferred_words": search["preferred_segment_words"],
              "event_maximum_words": winner["maximum_segment_words"],
              "event_window_turns": winner["window_turns"],
              "fixed_words": baseline["target_fixed_words"],
              "primary_budget_words": search["selection_budget_words"],
              "secondary_budgets_words": search["other_reported_budgets_words"],
              "selection_rule": search["selection_rule"],
              "primary_metric": protocol["precommitted_primary_metric"]}
    (ROOT / "configs/phase3_frozen.json").write_text(
        json.dumps(frozen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for score in scores:
        print(f"{score['config']}: {score['mean_conversation_rate']:.3f} "
              f"({', '.join(f'{r:.3f}' for r in score['conversation_rates'])})")
    print("Selected:", winner["config"])
    for budget in budgets:
        group = [r for r in rows if r["config"] == winner["config"] and r["budget_words"] == budget]
        baseline_group = [r for r in baseline["per_question"] if r["method"] == "fixed" and r["budget_words"] == budget]
        print(f"Budget {budget}: event {sum(r['all_evidence'] for r in group)}/{len(group)}; "
              f"fixed {sum(r['all_evidence'] for r in baseline_group)}/{len(baseline_group)}")
    return output


if __name__ == "__main__":
    run()
