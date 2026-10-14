"""Controlled segment-to-turn retrieval audit on the pinned Phase 10 corpus.

Gold spans are used only after construction and ranking. Phase 10 flat rows
are checked query by query to prevent an accidental baseline shift.
"""
import argparse
import gzip
import hashlib
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from fetch_phase10_data import verify
from run_baselines import ROOT, make_segments, rank, words
from run_phase8_causal import online_segments
from run_phase10_topic_transfer import (BUDGETS, SEEDS, UniformCountSampler,
                                        check_partition, chunks_from_cuts,
                                        query_turns, sample_for)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select(order, units, cap):
    selected, remaining = [], cap
    for index in order:
        cost = units[index]["word_cost"]
        if cost <= remaining:
            selected.append(index)
            remaining -= cost
    return selected, cap - remaining


def turn_index(tokenized, indices):
    return [{"id": f"turn:{i}", "turn_ids": [i], "tokens": tokenized[i],
             "word_cost": len(tokenized[i])} for i in indices]


def score_partition(query, gold, segments, tokenized, budget, routing_multiplier=4):
    order = rank(query, segments)
    flat, flat_words = select(order, segments, budget)
    flat_found = {i for s in flat for i in segments[s]["turn_ids"]}
    candidates, candidate_words = select(order, segments, routing_multiplier * budget)
    candidate_turn_ids = sorted(i for s in candidates for i in segments[s]["turn_ids"])
    candidate_turns = turn_index(tokenized, candidate_turn_ids)
    chosen, output_words = select(rank(query, candidate_turns), candidate_turns, budget)
    hier_found = {candidate_turn_ids[i] for i in chosen}
    assert candidate_words <= routing_multiplier * budget and output_words <= budget
    assert hier_found <= set(candidate_turn_ids)
    return {"flat_gold": len(gold & flat_found), "flat_words": flat_words,
            "flat_turns": len(flat_found),
            "hier_gold": len(gold & hier_found), "hier_words": output_words,
            "candidate_gold": len(gold & set(candidate_turn_ids)),
            "candidate_words": candidate_words, "candidate_segments": len(candidates),
            "candidate_turns": len(candidate_turn_ids), "selected_turns": len(chosen)}


def baseline_index(phase10):
    result = {}
    for row in phase10["per_query"]:
        key = row["meeting"], row["query_index"], row["method"], row["seed"], row["budget_words"]
        if key in result:
            raise AssertionError("Duplicate Phase 10 row")
        result[key] = row
    return result


def macro(rows, key, method, budget, seed=None):
    by_meeting = defaultdict(list)
    for row in rows:
        if row["method"] == method and row["budget_words"] == budget and row["seed"] == seed:
            by_meeting[row["meeting"]].append(row[key] / row["gold_turns"])
    assert len(by_meeting) == 35
    return statistics.mean(statistics.mean(group) for group in by_meeting.values())


def summary(rows, meetings):
    results = {}
    for budget in BUDGETS:
        source = {}
        for method in ("online", "fixed"):
            source[method] = {key: macro(rows, key, method, budget) for key in
                              ("flat_gold", "hier_gold", "candidate_gold")}
            source[method]["hier_minus_flat"] = source[method]["hier_gold"] - source[method]["flat_gold"]
        by_seed = [{key: macro(rows, key, "random", budget, seed) for key in
                    ("flat_gold", "hier_gold", "candidate_gold")} for seed in SEEDS]
        source["random_by_seed"] = by_seed
        source["random_hier_median"] = statistics.median(s["hier_gold"] for s in by_seed)
        source["random_flat_median"] = statistics.median(s["flat_gold"] for s in by_seed)
        source["random_at_least_online"] = sum(s["hier_gold"] >= source["online"]["hier_gold"]
                                              for s in by_seed)
        source["online_minus_random_hier_median"] = source["online"]["hier_gold"] - source["random_hier_median"]
        source["improvement_interaction"] = source["online"]["hier_minus_flat"] - statistics.median(
            s["hier_gold"] - s["flat_gold"] for s in by_seed)
        source["global_turn"] = macro(rows, "hier_gold", "global_turn", budget)
        results[str(budget)] = source

    per_meeting = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["budget_words"] == 1024:
            per_meeting[row["meeting"]][row["method"], row["seed"]].append(row["hier_gold"] / row["gold_turns"])
    meeting_scores = {}
    for m in meetings:
        mid = m["meeting"]
        group = per_meeting[mid]
        online = statistics.mean(group["online", None])
        randoms = [statistics.mean(group["random", s]) for s in SEEDS]
        meeting_scores[mid] = {"domain": m["domain"], "online": online,
                               "random_median": statistics.median(randoms),
                               "random_by_seed": randoms,
                               "fixed": statistics.mean(group["fixed", None]),
                               "global_turn": statistics.mean(group["global_turn", None])}
    rng = random.Random(11)
    ids = sorted(meeting_scores)
    boots = []
    for _ in range(2000):
        sample = [meeting_scores[ids[rng.randrange(35)]] for _ in ids]
        observed = statistics.mean(m["online"] for m in sample)
        null = statistics.median(statistics.mean(m["random_by_seed"][s] for m in sample)
                                 for s in SEEDS)
        boots.append(observed - null)
    boots.sort()
    return {"budgets": results, "meeting_1024": meeting_scores,
            "bootstrap_1024_percentile_95_descriptive": [boots[49], boots[1949]],
            "bootstrap_draws": 2000, "bootstrap_seed": 11}


def run(data_dir, output):
    if output.exists():
        raise FileExistsError(output)
    plan_path = ROOT / "configs/phase11_plan.json"
    manifest_path = ROOT / "configs/phase10_source_manifest.json"
    prior_path = ROOT / "results/phase10_transfer.json.gz"
    manifest = json.loads(manifest_path.read_text())
    plan = json.loads(plan_path.read_text())
    counts = verify(data_dir, manifest)
    assert counts == {"meetings": 35, "turns": 20718, "topic_spans": 179, "onsets": 161,
                      "specific_queries": 244, "query_spans": 286}
    assert plan["source_revision"] == manifest["revision"]
    prior = json.loads(gzip.decompress(prior_path.read_bytes()))
    assert prior["source_manifest_sha256"] == digest(manifest_path)
    prior_index = baseline_index(prior)
    settings = json.loads((ROOT / "configs/phase8_causal_plan.json").read_text())["causal_writer"]
    rows, meetings, checked = [], [], set()
    for item in manifest["files"]:
        mid = item["name"].removesuffix(".json")
        source = json.loads((data_dir / item["name"]).read_bytes())
        sample = sample_for(mid, source)
        turns = sample["conversation"]["session_1"]
        tokenized = [words(t["text"]) for t in turns]
        online, _ = online_segments(sample, settings)
        fixed = make_segments(sample, "fixed", 128)
        assert len(online) == next(m["online_segments"] for m in prior["meetings"] if m["meeting"] == mid)
        sampler = UniformCountSampler([len(x) for x in tokenized], len(online), 160)
        partitions = [("online", None, online), ("fixed", None, fixed)]
        partitions += [("random", seed, chunks_from_cuts(tokenized, sampler.draw(seed, mid)))
                       for seed in SEEDS]
        for method, seed, segments in partitions:
            check_partition(segments, len(turns), 160 if method != "fixed" else 128)
            if method == "random":
                assert len(segments) == len(online)
        global_units = turn_index(tokenized, list(range(len(turns))))
        for qi, query in enumerate(source["specific_query_list"]):
            gold = query_turns(query, len(turns))
            for budget in BUDGETS:
                global_selected, global_words = select(rank(query["query"], global_units), global_units, budget)
                found = {global_units[i]["turn_ids"][0] for i in global_selected}
                rows.append({"meeting": mid, "query_index": qi, "method": "global_turn",
                             "seed": None, "budget_words": budget, "gold_turns": len(gold),
                             "hier_gold": len(gold & found), "hier_words": global_words})
            for method, seed, segments in partitions:
                for budget in BUDGETS:
                    scored = score_partition(query["query"], gold, segments, tokenized, budget)
                    key = mid, qi, method, seed, budget
                    baseline = prior_index[key]
                    assert baseline["gold_turns"] == len(gold)
                    assert scored["flat_gold"] == baseline["retrieved_gold_turns"]
                    assert scored["flat_words"] == baseline["retrieved_words"]
                    checked.add(key)
                    rows.append({"meeting": mid, "query_index": qi, "method": method,
                                 "seed": seed, "budget_words": budget, "gold_turns": len(gold), **scored})
        meetings.append({"meeting": mid, "domain": item["domain"], "queries": len(source["specific_query_list"]),
                         "turns": len(turns), "online_segments": len(online)})
        print(f"Phase 11 {len(meetings)}/35 {mid}", flush=True)
    assert len(checked) == len(prior_index) == 16104
    assert len(rows) == 16836
    observed = summary(rows, meetings)
    result = {"phase": 11, "status": "exploratory reuse of inspected QMSum test data",
              "plan_sha256": digest(plan_path), "source_manifest_sha256": digest(manifest_path),
              "phase10_full_result_sha256": hashlib.sha256(gzip.decompress(prior_path.read_bytes())).hexdigest(),
              "source_audit": counts, "flat_rows_checked_against_phase10": len(checked),
              "summary": observed, "meetings": meetings, "per_query": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=ROOT / "data/raw/qmsum_test")
    p.add_argument("--output", type=Path, default=ROOT / "results/phase11_retrieval.json")
    a = p.parse_args()
    run(a.data_dir, a.output)
