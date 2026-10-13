"""Phase 8: immutable turn-arrival writer and exploratory evidence retrieval.

No retrieval label, question, future turn or session-global vocabulary enters
OnlineWriter. Querying is after the complete history has been indexed.
"""
import argparse
import gzip
import hashlib
import json
import time
from collections import Counter, deque, defaultdict
from pathlib import Path

from run_baselines import ROOT, make_segments, rank, retrieve, sessions, words
from run_event_development import event_segments
from run_phase7_external import audit_record, public_sample, score, sha256


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OnlineWriter:
    def __init__(self, session_key, minimum=64, threshold=0.85, maximum=160, window=3):
        if not (minimum > 0 and 0 <= threshold <= 1 and maximum >= minimum and window > 0):
            raise ValueError("Invalid writer settings")
        self.session_key = session_key
        self.minimum, self.threshold, self.maximum = minimum, threshold, maximum
        self.previous = deque(maxlen=window)
        self.closed = []
        self.open_ids, self.open_tokens = [], []
        self.reasons = Counter()

    def _close(self, reason):
        if not self.open_ids:
            return
        tokens = self.open_tokens
        self.closed.append({"id": f"{self.session_key}:{len(self.closed)}",
                            "turn_ids": self.open_ids, "tokens": tokens,
                            "word_cost": len(tokens)})
        self.reasons[reason] += 1
        self.open_ids, self.open_tokens = [], []

    def accept(self, turn_id, text):
        tokens = words(text or "")
        now = set(tokens)
        past = set().union(*self.previous) if self.previous else set()
        overlap = len(now & past)
        union = len(now | past)
        novelty = 1 - overlap / union if union else 0.0
        if self.open_ids:
            if len(self.open_tokens) + len(tokens) > self.maximum:
                self._close("maximum")
            elif len(self.open_tokens) >= self.minimum and novelty >= self.threshold:
                self._close("novelty")
        self.open_ids.append(turn_id)
        self.open_tokens.extend(tokens)
        self.previous.append(now)

    def finish(self):
        self._close("session_end")
        return self.closed


def online_segments(sample, settings):
    output, reasons = [], Counter()
    for key, turns in sessions(sample):
        writer = OnlineWriter(key, settings["minimum_open_words_for_novelty_boundary"],
                              settings["novelty_threshold_inclusive"],
                              settings["maximum_segment_words"])
        for turn in turns:
            writer.accept(turn["dia_id"], turn.get("text") or "")
        output.extend(writer.finish())
        reasons.update(writer.reasons)
    return output, dict(sorted(reasons.items()))


def lo_como(data_path, manifest_path, plan, frozen):
    protocol = json.loads((ROOT / "configs/protocol.json").read_text(encoding="utf-8"))
    if digest(data_path) != protocol["sha256"] or frozen["dataset_sha256"] != protocol["sha256"]:
        raise ValueError("LoCoMo dataset checksum mismatch")
    audit = json.loads(manifest_path.read_text(encoding="utf-8"))
    if audit["dataset_sha256"] != protocol["sha256"]:
        raise ValueError("LoCoMo manifest checksum mismatch")
    samples = {sample["sample_id"]: sample for sample in json.loads(data_path.read_text(encoding="utf-8"))}
    budgets = sorted([plan["primary_budget_words"]] + plan["secondary_budgets_words"])
    rows, stats = [], []
    for split, ids in (("development", protocol["development_conversations"]),
                       ("held_out", protocol["held_out_conversations"])):
        for sid in sorted(ids):
            sample = samples[sid]
            items = [item for item in audit["manifest"] if item["sample_id"] == sid and item["split"] == split]
            online, reasons = online_segments(sample, plan["causal_writer"])
            prepared = {"online": online,
                        "event": event_segments(sample, frozen["event_minimum_words"],
                                                frozen["event_preferred_words"],
                                                frozen["event_maximum_words"], frozen["event_window_turns"]),
                        "fixed": make_segments(sample, "fixed", frozen["fixed_words"]),
                        "session": make_segments(sample, "session", frozen["fixed_words"])}
            expected = [t["dia_id"] for _, turns in sessions(sample) for t in turns]
            for method, segments in prepared.items():
                observed = [tid for seg in segments for tid in seg["turn_ids"]]
                if observed != expected or len(observed) != len(set(observed)):
                    raise AssertionError("Invalid turn partition")
                stats.append({"split": split, "sample_id": sid, "method": method,
                              "segments": len(segments), "turns": len(expected),
                              "one_turn_segments": sum(len(s["turn_ids"]) == 1 for s in segments),
                              "over_160_single_turn_segments": sum(len(s["turn_ids"]) == 1 and s["word_cost"] > 160 for s in segments),
                              "total_segment_words": sum(s["word_cost"] for s in segments),
                              "close_reasons": reasons if method == "online" else None})
            for item in items:
                query = sample["qa"][item["question_index"]]["question"]
                gold = set(item["evidence_ids"])
                for method, segments in prepared.items():
                    for budget in budgets:
                        chosen = retrieve(query, segments, budget)
                        found = {tid for index in chosen for tid in segments[index]["turn_ids"]}
                        rows.append({"split": split, "sample_id": sid,
                                     "question_index": item["question_index"], "method": method,
                                     "budget_words": budget, "all_evidence": gold <= found,
                                     "retrieved_words": sum(segments[index]["word_cost"] for index in chosen),
                                     "retrieved_segments": len(chosen),
                                     "structural_budget": sum(segments[i]["word_cost"] for i, s in enumerate(segments)
                                                              if gold.intersection(s["turn_ids"])) > budget})
    return rows, stats


def external(data_path, plan, prior_path):
    if sha256(data_path) != json.loads((ROOT / "configs/phase7_external_plan.json").read_text(encoding="utf-8"))["external_dataset"]["sha256"]:
        raise ValueError("External dataset checksum mismatch")
    prior_raw = gzip.decompress(prior_path.read_bytes()) if prior_path.suffix == ".gz" else prior_path.read_bytes()
    prior = json.loads(prior_raw)
    if prior["external_dataset_sha256"] != sha256(data_path):
        raise ValueError("Phase 7 external comparator provenance mismatch")
    baseline = {(r["question_id"], r["budget_words"], r["method"]): r
                for r in prior["per_question"]}
    records = json.loads(data_path.read_text(encoding="utf-8"))
    if len(records) != 500 or len({r["question_id"] for r in records}) != 500:
        raise ValueError("Expected 500 distinct external questions")
    budgets = sorted([plan["primary_budget_words"]] + plan["secondary_budgets_words"])
    rows, count = [], Counter()
    for pos, record in enumerate(records, 1):
        audited = audit_record(record)
        if audited is None:
            count["abstention_excluded"] += 1
            continue
        gold, answer_ids, _, _ = audited
        segments, reasons = online_segments(public_sample(record), plan["causal_writer"])
        order = rank(record["question"], segments)
        count["answerable"] += 1
        count["segments"] += len(segments)
        count["one_turn_segments"] += sum(len(s["turn_ids"]) == 1 for s in segments)
        count["oversized_single_turn_segments"] += sum(len(s["turn_ids"]) == 1 and s["word_cost"] > 160 for s in segments)
        for key, value in reasons.items():
            count[f"close_{key}"] += value
        expected = [t["dia_id"] for _, group in sessions(public_sample(record)) for t in group]
        observed = [tid for seg in segments for tid in seg["turn_ids"]]
        if observed != expected or len(set(observed)) != len(observed):
            raise AssertionError("External turn partition invalid")
        for budget in budgets:
            if (record["question_id"], budget, "event") not in baseline:
                raise AssertionError("Missing Phase 7 comparator")
            rows.append({"question_id": record["question_id"], "budget_words": budget,
                         "method": "online", "question_type": record["question_type"],
                         **score(record, segments, order, gold, answer_ids, budget)})
        if pos % 100 == 0:
            print(f"Phase 8 external: {pos}/500", flush=True)
    if count["answerable"] != 470 or count["abstention_excluded"] != 30:
        raise AssertionError("External eligibility changed")
    for r in prior["per_question"]:
        if r["method"] in ("event", "fixed", "session"):
            rows.append(r)
    return rows, dict(sorted(count.items())), hashlib.sha256(prior_raw).hexdigest()


def summarize(rows, group_fields, outcome):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[f] for f in group_fields)].append(row)
    return [{**dict(zip(group_fields, key)), "questions": len(group),
             "successes": sum(bool(r[outcome]) for r in group),
             "rate": sum(bool(r[outcome]) for r in group) / len(group),
             "structural_budget": sum(r["structural_budget"] for r in group)}
            for key, group in sorted(groups.items())]


def discordance(rows, id_fields, outcome, method_a, method_b, budget, extra_fields=()):
    groups = defaultdict(dict)
    for r in rows:
        if r["budget_words"] == budget and r["method"] in (method_a, method_b):
            groups[tuple(r[k] for k in id_fields)][r["method"]] = bool(r[outcome])
    result = Counter()
    for row in groups.values():
        if set(row) != {method_a, method_b}:
            raise AssertionError("Incomplete paired comparison")
        a, b = row[method_a], row[method_b]
        result["both" if a and b else "online_only" if a else "comparator_only" if b else "neither"] += 1
    return dict(sorted(result.items()))


def run(locomo, external_data, external_prior, output):
    if output.exists():
        raise FileExistsError("Use a fresh Phase 8 output path")
    plan_path = ROOT / "configs/phase8_causal_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "configs/phase3_frozen.json").read_text(encoding="utf-8"))
    if (plan["primary_budget_words"], sorted(plan["secondary_budgets_words"]),
        frozen["development_selected_config"], frozen["fixed_words"]) != (1024, [512, 2048], "w3-max160", 128):
        raise ValueError("Frozen methods/budgets changed")
    start = time.perf_counter()
    local_rows, local_stats = lo_como(locomo, ROOT / "results/phase1_audit.json", plan, frozen)
    local_seconds = time.perf_counter() - start
    external_rows, external_stats, prior_sha = external(external_data, plan, external_prior)
    primary = plan["primary_budget_words"]
    output_data = {"phase": 8, "status": "exploratory; previously examined datasets",
                   "phase8_plan_sha256": digest(plan_path), "locomo_sha256": digest(locomo),
                   "external_sha256": sha256(external_data),
                   "phase7_comparator_sha256": prior_sha,
                   "timing_seconds_observed_machine": {"locomo": local_seconds,
                                                       "external": time.perf_counter() - start - local_seconds},
                   "locomo_summary": summarize(local_rows, ("split", "budget_words", "method"), "all_evidence"),
                   "locomo_segment_stats": local_stats,
                   "locomo_discordance_held_event": discordance([r for r in local_rows if r["split"] == "held_out"],
                         ("sample_id", "question_index"), "all_evidence", "online", "event", primary),
                   "locomo_discordance_held_fixed": discordance([r for r in local_rows if r["split"] == "held_out"],
                         ("sample_id", "question_index"), "all_evidence", "online", "fixed", primary),
                   "external_summary": summarize(external_rows, ("budget_words", "method"), "all_marked_turns"),
                   "external_stats": external_stats,
                   "external_discordance_event": discordance(external_rows, ("question_id",),
                         "all_marked_turns", "online", "event", primary),
                   "locomo_per_question": local_rows, "external_per_question": external_rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(output_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Phase 8 complete", flush=True)
    return output_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--locomo", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--external", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    parser.add_argument("--phase7", type=Path, default=ROOT / "results/phase7_external.json.gz")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase8_causal.json")
    args = parser.parse_args()
    run(args.locomo, args.external, args.phase7, args.output)
