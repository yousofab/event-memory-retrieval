"""Frozen external transfer to LongMemEval-S; never trains on external records.

The source JSON stays outside Git. Gold labels enter only after segments and ranks
are constructed. Stored outputs contain metrics and identifiers, never source text.
"""
import argparse
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from run_baselines import ROOT, make_segments, rank, sessions
from run_event_development import event_segments
from run_phase6_semantic import fit_lsa, semantic_segments, training_texts


METHODS = ("fixed", "event", "semantic_lsa", "session")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def public_sample(record):
    """Adapt contents only: do not pass labels, roles, dates or answers to methods."""
    return {"conversation": {
        f"session_{i + 1}": [
            {"dia_id": f"session_{i + 1}:{j + 1}", "text": turn["content"]}
            for j, turn in enumerate(group)]
        for i, group in enumerate(record["haystack_sessions"])}}


def gold_labels(record):
    """Inspect gold separately from public_sample(), after structural validation."""
    ids, session_indices = set(), set()
    for i, group in enumerate(record["haystack_sessions"]):
        for j, turn in enumerate(group):
            if turn.get("has_answer") is True:
                ids.add(f"session_{i + 1}:{j + 1}")
                session_indices.add(i)
    return ids, session_indices


def audit_record(record):
    groups = record["haystack_sessions"]
    official_ids = record["haystack_session_ids"]
    if len(groups) != len(official_ids) or len(groups) != len(record["haystack_dates"]):
        raise ValueError("Inconsistent session arrays")
    if any(not isinstance(t.get("content"), str) for group in groups for t in group):
        raise ValueError("Non-text turn content")
    gold, marked_indices = gold_labels(record)
    if record["question_id"].endswith("_abs"):
        # Upstream retains misleading evidence metadata in abstention records.
        return None
    if not gold:
        raise ValueError("An answerable record lacks turn evidence")
    answer_ids = set(record["answer_session_ids"])
    if not answer_ids or len(answer_ids) != len(record["answer_session_ids"]):
        raise ValueError("Missing or repeated official answer session IDs")
    if not answer_ids <= set(official_ids):
        raise ValueError("Official evidence session is missing from haystack")
    if not {official_ids[i] for i in marked_indices} <= answer_ids:
        raise ValueError("Marked turn outside official evidence sessions")
    return gold, answer_ids, {official_ids[i] for i in marked_indices}, len(official_ids) != len(set(official_ids))


def select(order, segments, budget):
    selected, remaining = [], budget
    for index in order:
        cost = segments[index]["word_cost"]
        if cost <= remaining:
            selected.append(index)
            remaining -= cost
    return selected


def score(record, segments, order, gold, answer_ids, budget):
    selected = select(order, segments, budget)
    found = {turn_id for index in selected for turn_id in segments[index]["turn_ids"]}
    sessions_found = {record["haystack_session_ids"][int(tid.split(":")[0][8:]) - 1]
                      for tid in found}
    owner = {tid: i for i, seg in enumerate(segments) for tid in seg["turn_ids"]}
    needed = {owner[tid] for tid in gold}
    gold_cost = sum(segments[i]["word_cost"] for i in needed)
    used = sum(segments[i]["word_cost"] for i in selected)
    success = gold <= found
    if used > budget or (success and gold_cost > budget):
        raise AssertionError("Word-budget contract violated")
    return {"all_marked_turns": success, "all_official_sessions": answer_ids <= sessions_found,
            "marked_turns_found": len(gold & found), "marked_turns_total": len(gold),
            "retrieved_words": used, "retrieved_segments": len(selected),
            "gold_segment_count": len(needed), "gold_segment_word_cost": gold_cost,
            "structural_budget": gold_cost > budget}


def summaries(rows):
    grouped = defaultdict(list)
    by_type = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["budget_words"])].append(row)
        by_type[(row["method"], row["budget_words"], row["question_type"])].append(row)
    def compact(group, dimensions):
        return {**dimensions, "questions": len(group),
                "all_marked_turns_count": sum(r["all_marked_turns"] for r in group),
                "all_official_sessions_count": sum(r["all_official_sessions"] for r in group),
                "structural_budget_count": sum(r["structural_budget"] for r in group),
                "mean_retrieved_words": sum(r["retrieved_words"] for r in group) / len(group)}
    return ([compact(group, {"method": m, "budget_words": b})
             for (m, b), group in sorted(grouped.items())],
            [compact(group, {"method": m, "budget_words": b, "question_type": t})
             for (m, b, t), group in sorted(by_type.items())])


def discordances(rows, budget):
    cases = defaultdict(dict)
    for row in rows:
        if row["budget_words"] == budget:
            cases[row["question_id"]][row["method"]] = row["all_marked_turns"]
    counts = Counter()
    for values in cases.values():
        if set(values) != set(METHODS):
            raise AssertionError("Missing primary-budget method")
        a, b = values["semantic_lsa"], values["event"]
        counts["both" if a and b else "semantic_only" if a else
               "lexical_only" if b else "neither"] += 1
    return {key: counts[key] for key in ("both", "semantic_only", "lexical_only", "neither")}


def run(external_path, locomo_path, output_path):
    if output_path.exists():
        raise FileExistsError("Phase 7 output exists; choose a fresh path")
    plan_path = ROOT / "configs/phase7_external_plan.json"
    phase6_path = ROOT / "configs/phase6_semantic_plan.json"
    phase6_result_path = ROOT / "results/phase6_development_lsa.json"
    frozen_path = ROOT / "configs/phase3_frozen.json"
    protocol_path = ROOT / "configs/protocol.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    phase6 = json.loads(phase6_path.read_text(encoding="utf-8"))
    prior = json.loads(phase6_result_path.read_text(encoding="utf-8"))
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if sha256(external_path) != plan["external_dataset"]["sha256"]:
        raise ValueError("External dataset SHA-256 mismatch")
    if (sha256(locomo_path) != protocol["sha256"] or
            phase6["dataset_sha256"] != protocol["sha256"] or
            prior["dataset_sha256"] != protocol["sha256"]):
        raise ValueError("LoCoMo or Phase 6 provenance mismatch")
    if ((frozen["event_minimum_words"], frozen["event_preferred_words"],
         frozen["event_maximum_words"], frozen["event_window_turns"],
         frozen["fixed_words"]) != (64, 128, 160, 3, 128)
        or frozen["primary_budget_words"] != plan["primary_budget_words"]
        or sorted(frozen["secondary_budgets_words"]) != sorted(plan["secondary_budgets_words"])):
        raise ValueError("Frozen segmentation/budget does not match plan")
    source = {sample["sample_id"]: sample for sample in json.loads(locomo_path.read_text(encoding="utf-8"))}
    start = time.perf_counter()
    vectorizer, svd, training = fit_lsa(training_texts(source, protocol["development_conversations"]), phase6)
    if training["training_text_sha256"] != prior["training"]["training_text_sha256"]:
        raise AssertionError("Phase 6 training text has changed")
    fit_seconds = time.perf_counter() - start
    del source
    records = json.loads(external_path.read_text(encoding="utf-8"))
    if len(records) != 500 or len({r["question_id"] for r in records}) != len(records):
        raise ValueError("External record set differs from official 500 unique questions")
    budgets = sorted([plan["primary_budget_words"]] + plan["secondary_budgets_words"])
    rows, stats = [], Counter()
    process_start = time.perf_counter()
    for position, record in enumerate(records, 1):
        audited = audit_record(record)
        if audited is None:
            stats["abstention_excluded"] += 1
            stats["abstention_with_marked_turns"] += bool(gold_labels(record)[0])
            stats["abstention_with_answer_session_ids"] += bool(record["answer_session_ids"])
            stats["duplicate_session_ids_abstention"] += (
                len(record["haystack_session_ids"]) != len(set(record["haystack_session_ids"])))
            continue
        gold, answer_ids, marked_session_ids, duplicate_session_ids = audited
        if marked_session_ids != answer_ids:
            stats["incomplete_turn_label_sessions"] += 1
        if duplicate_session_ids:
            stats["duplicate_session_ids_answerable"] += 1
        stats["answerable"] += 1
        stats["marked_turns"] += len(gold)
        sample = public_sample(record)
        expected = [t["dia_id"] for _, group in sessions(sample) for t in group]
        texts = [t["text"] for _, group in sessions(sample) for t in group]
        transformed = vectorizer.transform(texts)
        stats["external_turns"] += len(texts)
        stats["lsa_zero_vocabulary_turns"] += int(sum(transformed.indptr[1:] == transformed.indptr[:-1]))
        prepared = {
            "fixed": make_segments(sample, "fixed", frozen["fixed_words"]),
            "event": event_segments(sample, frozen["event_minimum_words"],
                                    frozen["event_preferred_words"], frozen["event_maximum_words"],
                                    frozen["event_window_turns"]),
            "semantic_lsa": semantic_segments(sample, vectorizer, svd,
                                               frozen["event_minimum_words"],
                                               frozen["event_preferred_words"],
                                               frozen["event_maximum_words"], frozen["event_window_turns"]),
            "session": make_segments(sample, "session", frozen["fixed_words"]),
        }
        for method in METHODS:
            segments = prepared[method]
            observed = [tid for seg in segments for tid in seg["turn_ids"]]
            if observed != expected or len(set(observed)) != len(observed):
                raise AssertionError("Partition coverage/order is invalid")
            stats[f"segments_{method}"] += len(segments)
            order = rank(record["question"], segments)
            for budget in budgets:
                rows.append({"question_id": record["question_id"],
                             "question_type": record["question_type"],
                             "label_session_mismatch": marked_session_ids != answer_ids,
                             "duplicate_session_ids": duplicate_session_ids,
                             "method": method, "budget_words": budget,
                             **score(record, segments, order, gold, answer_ids, budget)})
        if position % 50 == 0:
            print(f"Phase 7: {position}/500 source records processed", flush=True)
    if stats["answerable"] != 470 or stats["abstention_excluded"] != 30:
        raise AssertionError("Eligibility audit differs from the registered amendment")
    if (stats["incomplete_turn_label_sessions"] != 32 or
            stats["duplicate_session_ids_answerable"] != 12 or
            stats["duplicate_session_ids_abstention"] != 1 or
            stats["abstention_with_marked_turns"] != 9):
        raise AssertionError("Source audit differs from registered amendments")
    overall, by_type = summaries(rows)
    unique_id_session_summary, _ = summaries([r for r in rows if not r["duplicate_session_ids"]])
    output = {"phase": 7, "status": "external exploratory transfer; not official QA benchmark",
              "external_dataset_sha256": sha256(external_path),
              "locomo_training_sha256": sha256(locomo_path),
              "phase7_plan_sha256": sha256(plan_path),
              "phase7_label_amendment_sha256": sha256(ROOT / "docs/phase7_label_amendment.md"),
              "phase7_source_audit_amendment_sha256": sha256(ROOT / "docs/phase7_source_audit_amendment.md"),
              "phase6_plan_sha256": sha256(phase6_path),
              "phase3_frozen_sha256": sha256(frozen_path),
              "primary_budget_words": plan["primary_budget_words"], "budgets_words": budgets,
              "training": training,
              "audit_counts": dict(sorted(stats.items())),
              "timing_seconds_observed_machine": {"model_fit": fit_seconds,
                                                  "external_processing": time.perf_counter() - process_start},
              "summary": overall, "by_question_type": by_type,
              "unique_session_id_subset_summary": unique_id_session_summary,
              "discordance_primary_lsa_vs_lexical": discordances(rows, plan["primary_budget_words"]),
              "per_question": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Phase 7 complete: 470 answerable questions,", len(rows), "metric rows", flush=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", type=Path, default=ROOT / "data/raw/longmemeval_s_cleaned.json")
    parser.add_argument("--locomo", type=Path, default=ROOT / "data/raw/locomo10.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase7_external.json")
    args = parser.parse_args()
    run(args.external, args.locomo, args.output)
