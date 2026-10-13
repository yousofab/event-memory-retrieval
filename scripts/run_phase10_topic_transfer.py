"""Phase 10: frozen causal boundaries versus QMSum human topic-span onsets.

Gold annotations are read only for scoring, after every partition is built.
Random baselines are exact-uniform valid partitions conditional on the online
writer's per-meeting count, not deployable online memory writers.
"""
import argparse
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from fetch_phase10_data import verify
from run_baselines import ROOT, make_segments, rank, words
from run_phase8_causal import online_segments


SEEDS = tuple(range(20))
TOLERANCES = (0, 1, 2, 5)
BUDGETS = (512, 1024, 2048)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample_for(meeting_id, source):
    turns = [{"dia_id": index, "text": turn["content"]}
             for index, turn in enumerate(source["meeting_transcripts"])]
    return {"sample_id": meeting_id, "conversation": {"session_1": turns}}


class UniformCountSampler:
    """Sample exactly uniformly from capped, contiguous K-segment partitions."""

    def __init__(self, lengths, target_count, maximum=160):
        self.lengths = lengths
        self.target_count = target_count
        self.maximum = maximum
        n = len(lengths)
        if not (1 <= target_count <= n) or any(x < 0 for x in lengths):
            raise ValueError("Invalid lengths or segment count")
        prefix = [0]
        for value in lengths:
            prefix.append(prefix[-1] + value)
        ends = []
        for start in range(n):
            valid = []
            for end in range(start + 1, n + 1):
                cost = prefix[end] - prefix[start]
                if cost > maximum and end != start + 1:
                    break
                valid.append(end)
                if cost > maximum:
                    break
            ends.append(valid)
        self.ends = ends
        self.n = n

        @lru_cache(None)
        def ways(start, remaining):
            if not remaining:
                return int(start == n)
            if n - start < remaining:
                return 0
            return sum(ways(end, remaining - 1) for end in ends[start])

        self.ways = ways
        if not ways(0, target_count):
            raise ValueError("No valid count-matched partition")

    def draw(self, seed, namespace):
        rng = random.Random(int.from_bytes(
            hashlib.sha256(f"{seed}|{namespace}".encode()).digest(), "big"))
        cuts, start, left = [], 0, self.target_count
        while left:
            draw = rng.randrange(self.ways(start, left))
            for end in self.ends[start]:
                weight = self.ways(end, left - 1)
                if draw < weight:
                    cuts.append((start, end))
                    start, left = end, left - 1
                    break
                draw -= weight
            else:
                raise AssertionError("Sampler path is incomplete")
        assert start == self.n
        return cuts


def chunks_from_cuts(tokenized, cuts):
    return [{"id": f"session_1:{index}", "turn_ids": list(range(start, end)),
             "tokens": [word for turn in tokenized[start:end] for word in turn],
             "word_cost": sum(map(len, tokenized[start:end]))}
            for index, (start, end) in enumerate(cuts)]


def check_partition(segments, n, maximum):
    observed = [index for segment in segments for index in segment["turn_ids"]]
    assert observed == list(range(n))
    assert all(segment["word_cost"] <= maximum or len(segment["turn_ids"]) == 1
               for segment in segments)


def boundaries(segments):
    return {segment["turn_ids"][0] for segment in segments[1:]}


def onset_coverage(gold, predicted, tolerance):
    return sum(any(abs(start - boundary) <= tolerance for boundary in predicted)
               for start in gold) / len(gold)


def query_turns(query, n):
    relevant = set()
    for span in query["relevant_text_span"]:
        start, stop = map(int, span)
        if not (0 <= start <= stop < n):
            raise ValueError("Out-of-range query label")
        relevant.update(range(start, stop + 1))
    if not relevant:
        raise ValueError("Empty specific-query evidence")
    return relevant


def score_query(query, gold, segments, method, seed, meeting_id, query_index):
    order = rank(query, segments)
    owned = {turn: index for index, segment in enumerate(segments)
             for turn in segment["turn_ids"]}
    required_cost = sum(segments[index]["word_cost"] for index in {owned[turn] for turn in gold})
    rows = []
    for budget in BUDGETS:
        selected, remaining = [], budget
        for index in order:
            cost = segments[index]["word_cost"]
            if cost <= remaining:
                selected.append(index)
                remaining -= cost
        found = {turn for index in selected for turn in segments[index]["turn_ids"]}
        rows.append({"meeting": meeting_id, "query_index": query_index,
                     "method": method, "seed": seed, "budget_words": budget,
                     "gold_turns": len(gold), "retrieved_gold_turns": len(gold & found),
                     "recall": len(gold & found) / len(gold),
                     "all_evidence_structurally_feasible": required_cost <= budget,
                     "retrieved_words": budget - remaining})
    return rows


def summarize(meetings, rows):
    boundary = {}
    for tolerance in TOLERANCES:
        observed = statistics.mean(m["boundary_coverage"]["online"][str(tolerance)] for m in meetings)
        null = [statistics.mean(m["boundary_coverage"]["random"][str(seed)][str(tolerance)]
                                for m in meetings) for seed in SEEDS]
        boundary[str(tolerance)] = {"online_macro": observed, "random_macro_by_seed": null,
                                    "random_median": statistics.median(null),
                                    "random_at_least_online": sum(x >= observed for x in null)}
    domain = {}
    for label in ("academic", "product", "committee"):
        subset = [m for m in meetings if m["domain"] == label]
        observed = statistics.mean(m["boundary_coverage"]["online"]["2"] for m in subset)
        null = [statistics.mean(m["boundary_coverage"]["random"][str(seed)]["2"]
                                for m in subset) for seed in SEEDS]
        domain[label] = {"meetings": len(subset), "online_macro": observed,
                         "random_macro_by_seed": null, "random_median": statistics.median(null)}
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["meeting"], row["method"], row["seed"], row["budget_words"]].append(row["recall"])
    retrieval = {}
    for budget in BUDGETS:
        observed = {}
        for method in ("online", "fixed"):
            observed[method] = statistics.mean(statistics.mean(grouped[m["meeting"], method, None, budget])
                                               for m in meetings)
        null = [statistics.mean(statistics.mean(grouped[m["meeting"], "random", seed, budget])
                                for m in meetings) for seed in SEEDS]
        retrieval[str(budget)] = {**observed, "random_macro_by_seed": null,
                                  "random_median": statistics.median(null),
                                  "random_at_least_online": sum(x >= observed["online"] for x in null)}
    return {"boundary": boundary, "domains": domain, "retrieval": retrieval}


def run(data_dir, output_path):
    plan_path = ROOT / "configs/phase10_plan.json"
    manifest_path = ROOT / "configs/phase10_source_manifest.json"
    plan = json.loads(plan_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    assert plan["source_revision"] == manifest["revision"]
    counts = verify(data_dir, manifest)
    expected = plan["source_audit_before_scoring"]
    assert counts == {"meetings": expected["meetings"] if "meetings" in expected else plan["meetings"],
                      "turns": expected["turns"], "topic_spans": expected["topic_spans"],
                      "onsets": expected["unique_nonzero_topic_span_starts"],
                      "specific_queries": expected["specific_queries"],
                      "query_spans": expected["specific_query_spans"]}
    settings = json.loads((ROOT / "configs/phase8_causal_plan.json").read_text())["causal_writer"]
    records, rows = [], []
    for item in manifest["files"]:
        meeting_id = item["name"].removesuffix(".json")
        source = json.loads((data_dir / item["name"]).read_bytes())
        sample = sample_for(meeting_id, source)
        turns = sample["conversation"]["session_1"]
        tokenized = [words(t["text"]) for t in turns]
        online, reasons = online_segments(sample, settings)
        fixed = make_segments(sample, "fixed", 128)
        n = len(turns)
        check_partition(online, n, 160)
        assert [t for s in fixed for t in s["turn_ids"]] == list(range(n))
        gold = sorted({int(span[0]) for topic in source["topic_list"]
                       for span in topic["relevant_text_span"] if int(span[0]) > 0})
        assert gold
        coverage = {"online": {str(t): onset_coverage(gold, boundaries(online), t)
                                for t in TOLERANCES}, "random": {}}
        sam = UniformCountSampler([len(t) for t in tokenized], len(online), 160)
        queries = [(i, q["query"], query_turns(q, n))
                   for i, q in enumerate(source["specific_query_list"])]
        for method, segments in (("online", online), ("fixed", fixed)):
            for index, query, evidence in queries:
                rows.extend(score_query(query, evidence, segments, method, None, meeting_id, index))
        for seed in SEEDS:
            cuts = sam.draw(seed, meeting_id)
            segments = chunks_from_cuts(tokenized, cuts)
            check_partition(segments, n, 160)
            assert len(segments) == len(online)
            coverage["random"][str(seed)] = {
                str(t): onset_coverage(gold, boundaries(segments), t) for t in TOLERANCES}
            for index, query, evidence in queries:
                rows.extend(score_query(query, evidence, segments, "random", seed, meeting_id, index))
        records.append({"meeting": meeting_id, "domain": item["domain"], "turns": n,
                        "topic_onsets": len(gold), "specific_queries": len(queries),
                        "online_segments": len(online), "fixed_segments": len(fixed),
                        "online_close_reasons": reasons, "boundary_coverage": coverage,
                        "overlong_turns": sum(len(t) > 160 for t in tokenized)})
        print(f"Phase 10 {len(records)}/{len(manifest['files'])}: {meeting_id}", flush=True)
    assert len(rows) == counts["specific_queries"] * (2 + len(SEEDS)) * len(BUDGETS)
    summary = summarize(records, rows)
    result = {"phase": 10, "status": "prospectively specified external exploratory diagnostic",
              "plan_sha256": sha256(plan_path), "source_manifest_sha256": sha256(manifest_path),
              "source_revision": manifest["revision"], "source_audit": counts,
              "seeds": SEEDS, "tolerances_turns": TOLERANCES, "budgets_words": BUDGETS,
              "summary": summary, "meetings": records, "per_query": rows}
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/raw/qmsum_test")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase10_transfer.json")
    args = parser.parse_args()
    run(args.data_dir, args.output)
