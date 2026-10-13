"""Phase 9: uniform random valid partitions matched to the online segment count.

The control is retrospective and intentionally does not read turn text except
for Unicode-regex word counts. Gold evidence is read only after construction.
"""
import argparse
import gzip
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from run_baselines import ROOT, rank, sessions, words
from run_phase8_causal import online_segments


SEEDS = tuple(range(20))
BUDGETS = (512, 1024, 2048)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def session_partition(lengths, target_count, seed, namespace, maximum=160):
    """Uniform among all turn-contiguous valid partitions with target_count.

    A single overlong turn is a valid whole segment; any multi-turn segment
    must cost no more than maximum. Integer completion counts avoid float bias.
    """
    n = len(lengths)
    if n == 0:
        if target_count:
            raise ValueError("Empty session cannot have segments")
        return []
    if not (1 <= target_count <= n):
        raise ValueError("Invalid target segment count")
    prefix = [0]
    for length in lengths:
        if length < 0:
            raise ValueError("Negative word length")
        prefix.append(prefix[-1] + length)

    def ends(start):
        for end in range(start + 1, n + 1):
            cost = prefix[end] - prefix[start]
            if cost > maximum and end != start + 1:
                break
            yield end
            if cost > maximum:
                break

    @lru_cache(None)
    def ways(start, remaining):
        if remaining == 0:
            return int(start == n)
        if n - start < remaining:
            return 0
        return sum(ways(end, remaining - 1) for end in ends(start))

    if not ways(0, target_count):
        raise ValueError("No valid count-matched partition")
    raw = f"{seed}|{namespace}".encode("utf-8")
    rng = random.Random(int.from_bytes(hashlib.sha256(raw).digest(), "big"))
    cuts, start, left = [], 0, target_count
    while left:
        total = ways(start, left)
        draw = rng.randrange(total)
        for end in ends(start):
            weight = ways(end, left - 1)
            if draw < weight:
                cuts.append((start, end))
                start, left = end, left - 1
                break
            draw -= weight
        else:
            raise AssertionError("Weighted sampling path missing")
    if start != n or len(cuts) != target_count:
        raise AssertionError("Invalid sampled partition")
    return cuts


def matched_segments(sample, settings, seed):
    online, _ = online_segments(sample, settings)
    target = Counter(segment["id"].split(":")[0] for segment in online)
    prepared, shapes = [], []
    for key, turns in sessions(sample):
        texts = [words(turn.get("text") or "") for turn in turns]
        cuts = session_partition([len(t) for t in texts], target[key], seed,
                                 f"{sample['sample_id']}|{key}", settings["maximum_segment_words"])
        for start, stop in cuts:
            group = turns[start:stop]
            tokens = [token for subtokens in texts[start:stop] for token in subtokens]
            prepared.append({"id": f"{key}:{len(prepared)}",
                             "turn_ids": [t["dia_id"] for t in group],
                             "tokens": tokens, "word_cost": len(tokens)})
            shapes.append({"session": key, "turns": stop - start, "words": len(tokens)})
    expected = [t["dia_id"] for _, turns in sessions(sample) for t in turns]
    observed = [tid for part in prepared for tid in part["turn_ids"]]
    if expected != observed or len(observed) != len(set(observed)) or len(prepared) != len(online):
        raise AssertionError("Coverage/count mismatch")
    for part in prepared:
        if part["word_cost"] > settings["maximum_segment_words"] and len(part["turn_ids"]) != 1:
            raise AssertionError("Oversized multi-turn chunk")
    return prepared, shapes


def select(order, segments, budget):
    chosen, remaining = [], budget
    for index in order:
        cost = segments[index]["word_cost"]
        if cost <= remaining:
            chosen.append(index)
            remaining -= cost
    return chosen


def evaluate(sample, manifest, segments, split, seed):
    rows = []
    owner = {tid: i for i, part in enumerate(segments) for tid in part["turn_ids"]}
    for item in manifest:
        question = sample["qa"][item["question_index"]]["question"]
        gold = set(item["evidence_ids"])
        needed = {owner[tid] for tid in gold}
        cost = sum(segments[i]["word_cost"] for i in needed)
        order = rank(question, segments)
        for budget in BUDGETS:
            chosen = select(order, segments, budget)
            found = {tid for index in chosen for tid in segments[index]["turn_ids"]}
            used = sum(segments[i]["word_cost"] for i in chosen)
            if used > budget or (gold <= found and cost > budget):
                raise AssertionError("Budget violation")
            rows.append({"split": split, "sample_id": sample["sample_id"],
                         "question_index": item["question_index"], "seed": seed,
                         "budget_words": budget, "all_evidence": gold <= found,
                         "structural_budget": cost > budget,
                         "retrieved_words": used})
    return rows


def summarize(rows, prior):
    counts = defaultdict(int)
    per_conversation = defaultdict(int)
    for row in rows:
        if row["all_evidence"]:
            counts[row["split"], row["seed"], row["budget_words"]] += 1
            per_conversation[row["split"], row["seed"], row["budget_words"], row["sample_id"]] += 1
    prior_counts = defaultdict(int)
    for row in prior["locomo_per_question"]:
        if row["method"] == "online" and row["all_evidence"]:
            prior_counts[row["split"], row["budget_words"]] += 1
    def group(split, budget):
        values = [counts[split, seed, budget] for seed in SEEDS]
        observed = prior_counts[split, budget]
        return {"split": split, "budget_words": budget, "online_successes": observed,
                "null_successes_by_seed": values, "null_min": min(values),
                "null_median": statistics.median(values), "null_max": max(values),
                "null_at_least_online": sum(v >= observed for v in values),
                "null_repetitions": len(values)}
    outcome = [group(split, budget) for split in ("development", "held_out") for budget in BUDGETS]
    conversation = []
    for split in ("development", "held_out"):
        sids = sorted({r["sample_id"] for r in rows if r["split"] == split})
        for sid in sids:
            values = [per_conversation[split, seed, 1024, sid] for seed in SEEDS]
            online = sum(r["all_evidence"] for r in prior["locomo_per_question"]
                         if r["split"] == split and r["method"] == "online"
                         and r["budget_words"] == 1024 and r["sample_id"] == sid)
            conversation.append({"split": split, "sample_id": sid, "online_successes": online,
                                 "null_by_seed": values, "null_median": statistics.median(values),
                                 "null_min": min(values), "null_max": max(values)})
    return outcome, conversation


def run(data_path, prior_path, output_path):
    if output_path.exists():
        raise FileExistsError("Use a fresh Phase 9 output path")
    plan_path = ROOT / "configs/phase9_boundary_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    settings = json.loads((ROOT / "configs/phase8_causal_plan.json").read_text(encoding="utf-8"))["causal_writer"]
    audit = json.loads((ROOT / "results/phase1_audit.json").read_text(encoding="utf-8"))
    if sha(data_path) != protocol["sha256"] or audit["dataset_sha256"] != protocol["sha256"]:
        raise ValueError("Source/manifest provenance mismatch")
    raw = gzip.decompress(prior_path.read_bytes()) if prior_path.suffix == ".gz" else prior_path.read_bytes()
    prior = json.loads(raw)
    if prior["phase"] != 8 or prior["locomo_sha256"] != protocol["sha256"]:
        raise ValueError("Phase 8 comparator mismatch")
    samples = {s["sample_id"]: s for s in json.loads(data_path.read_text(encoding="utf-8"))}
    rows, shapes = [], []
    for split, ids in (("development", protocol["development_conversations"]),
                       ("held_out", protocol["held_out_conversations"])):
        for sid in sorted(ids):
            sample = samples[sid]
            eligible = [m for m in audit["manifest"] if m["sample_id"] == sid and m["split"] == split]
            for seed in SEEDS:
                segments, structure = matched_segments(sample, settings, seed)
                rows.extend(evaluate(sample, eligible, segments, split, seed))
                shapes.append({"split": split, "sample_id": sid, "seed": seed,
                               "segments": len(segments),
                               "one_turn_segments": sum(s["turns"] == 1 for s in structure),
                               "words_total": sum(s["words"] for s in structure),
                               "mean_words": sum(s["words"] for s in structure) / len(structure)})
        print(f"Phase 9: {split} complete", flush=True)
    expected = (274 + 599) * len(SEEDS) * len(BUDGETS)
    if len(rows) != expected:
        raise AssertionError("Incomplete question/seed/budget matrix")
    outcome, by_conversation = summarize(rows, prior)
    result = {"phase": 9, "status": "exploratory retrospective matched-count diagnostic",
              "plan_sha256": sha(plan_path), "locomo_sha256": sha(data_path),
              "phase8_result_sha256": hashlib.sha256(raw).hexdigest(),
              "budgets_words": BUDGETS, "seeds": SEEDS,
              "summary": outcome, "per_conversation": by_conversation,
              "shape": shapes, "per_question": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Phase 9 result saved", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--prior", type=Path, default=ROOT / "results/phase8_causal.json.gz")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase9_controls.json")
    args = parser.parse_args()
    run(args.data, args.prior, args.output)
