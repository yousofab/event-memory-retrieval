"""Phase 16: matched within-session boundaries, equal role view and word cap.

Only question text enters the BM25 index. Gold session IDs are used after
retrieval to score the selected documents. Raw dialogue is never exported.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import statistics
import subprocess

from run_baselines import ROOT, words
from run_phase8_causal import OnlineWriter
from run_phase9_controls import session_partition
from run_phase15_role_retrieval import BM25, evidence_ids, load_group


PLAN_PATH = ROOT / "configs/phase16_boundary_plan.json"
SETTINGS = json.loads((ROOT / "configs/phase8_causal_plan.json").read_text(encoding="utf-8"))["causal_writer"]
SEEDS = tuple(range(5))
BUDGETS = (512, 1024, 2048)
METHODS = ("writer",) + tuple(f"random_{seed}" for seed in SEEDS) + ("session",)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_turns(session):
    turns = session["conversation"]
    if any(t["speaker"] not in ("ai_agent", "user_agent") for t in turns):
        raise ValueError("Unrecognized speaker")
    return [words(t.get("message") or "") for t in turns]


def writer_cuts(session):
    writer = OnlineWriter(str(session["session_id"]),
                          SETTINGS["minimum_open_words_for_novelty_boundary"],
                          SETTINGS["novelty_threshold_inclusive"],
                          SETTINGS["maximum_segment_words"])
    for index, turn in enumerate(session["conversation"]):
        writer.accept(index, turn.get("message") or "")
    groups = writer.finish()
    cuts = []
    start = 0
    for group in groups:
        stop = start + len(group["turn_ids"])
        if group["turn_ids"] != list(range(start, stop)):
            raise AssertionError("Writer turn coverage changed")
        cuts.append((start, stop))
        start = stop
    if start != len(session["conversation"]):
        raise AssertionError("Writer lost a turn")
    return cuts, dict(writer.reasons)


def partitions(sessions, method):
    """Return documents ordered oldest session first, reverse within session.

    Phase 15 BM25 uses newest document on score ties. Reversing chunks within
    each session makes the EARLIER chunk win ties without changing the score.
    """
    documents, ids, counts, reasons, oversized = [], [], [], Counter(), 0
    for session in sessions:
        sid = session["session_id"]
        token_turns = source_turns(session)
        if method == "session":
            cuts = [(0, len(token_turns))] if token_turns else []
        else:
            writer, why = writer_cuts(session)
            if method == "writer":
                cuts = writer
                reasons.update(why)
            else:
                seed = int(method.split("_")[1])
                cuts = session_partition([len(t) for t in token_turns], len(writer),
                                         seed, f"{sid}|{session['persona']}|{session['date']}",
                                         SETTINGS["maximum_segment_words"])
        if [i for start, stop in cuts for i in range(start, stop)] != list(range(len(token_turns))):
            raise AssertionError("Nonpartition or lost turn")
        counts.append(len(cuts))
        for start, stop in reversed(cuts):
            tokens = [token for turn in token_turns[start:stop] for token in turn]
            if method != "session" and len(tokens) > SETTINGS["maximum_segment_words"]:
                if stop - start != 1:
                    raise AssertionError("Overlong multi-turn segment")
                oversized += 1
            documents.append(tokens)
            ids.append(sid)
    return documents, ids, counts, dict(reasons), oversized


def select(order, lengths, budget):
    chosen = []
    remaining = budget
    for pos in order:
        cost = lengths[pos]
        if cost and cost <= remaining:
            chosen.append(pos)
            remaining -= cost
    return chosen


def score(question, active, obsolete, method, index, ids):
    order = index.top(question, index.n)
    rows = []
    for budget in BUDGETS:
        chosen = select(order, index.lengths, budget)
        observed = {ids[pos] for pos in chosen}
        used = sum(index.lengths[pos] for pos in chosen)
        if used > budget:
            raise AssertionError("Budget violation")
        rows.append({"method": method, "budget_words": budget,
                     "active_any": int(bool(active & observed)) if active else None,
                     "obsolete_any": int(bool(obsolete & observed)) if obsolete else None,
                     "selected_documents": len(chosen),
                     "selected_sessions": len(observed), "retrieved_words": used})
    return rows


def summarize(rows, group_stats):
    groups = defaultdict(list)
    for r in rows:
        groups[r["method"], r["budget_words"]].append(r)
    methods = {}
    for (method, budget), subset in sorted(groups.items()):
        active = [r["active_any"] for r in subset if r["active_any"] is not None]
        obsolete = [r["obsolete_any"] for r in subset if r["obsolete_any"] is not None]
        methods[f"{method}/{budget}"] = {
            "questions": len(subset), "active_eligible": len(active), "active_hits": sum(active),
            "obsolete_eligible": len(obsolete), "obsolete_hits": sum(obsolete),
            "mean_documents": round(statistics.mean(r["selected_documents"] for r in subset), 6),
            "mean_sessions": round(statistics.mean(r["selected_sessions"] for r in subset), 6),
            "mean_words": round(statistics.mean(r["retrieved_words"] for r in subset), 6)}
    paired = defaultdict(dict)
    for row in rows:
        if row["budget_words"] == 1024 and row["active_any"] is not None:
            paired[row["period"], row["persona"], row["question_id"]][row["method"]] = row
    if len(paired) != 398 or any(set(p) != set(METHODS) for p in paired.values()):
        raise AssertionError("Unpaired active matrix")
    differences = []
    per_seed = {seed: [] for seed in SEEDS}
    for key, pair in sorted(paired.items()):
        writer = pair["writer"]["active_any"]
        control = [pair[f"random_{seed}"]["active_any"] for seed in SEEDS]
        differences.append((key[:2], writer - sum(control) / len(control), pair["writer"]["overlap_count"]))
        for seed, value in zip(SEEDS, control):
            per_seed[seed].append(value)
    by_group = defaultdict(list)
    for key, delta, _ in differences:
        by_group[key].append(delta)
    if len(by_group) != 30:
        raise AssertionError("Unexpected cluster count")
    rng = random.Random(16)
    keys = sorted(by_group)
    draws = []
    for _ in range(2000):
        chosen = [by_group[keys[rng.randrange(len(keys))]] for _ in keys]
        draws.append(sum(map(sum, chosen)) / sum(map(len, chosen)))
    draws.sort()
    values = [delta for _, delta, _ in differences]
    disjoint = [delta for _, delta, overlap in differences if overlap == 0]
    return {"methods": methods,
            "primary": {"eligible": len(values), "writer_hits": methods["writer/1024"]["active_hits"],
                        "random_hits_by_seed": [sum(per_seed[s]) for s in SEEDS],
                        "writer_minus_random_mean": round(statistics.mean(values), 6),
                        "descriptive_cluster_bootstrap_95": [round(draws[49], 6), round(draws[1949], 6)],
                        "disjoint_active_obsolete_eligible": len(disjoint),
                        "disjoint_difference_mean": round(statistics.mean(disjoint), 6)},
            "group_stats": group_stats}


def run(upstream, output_summary, output_rows):
    if output_summary.exists() or output_rows.exists():
        raise FileExistsError("Use fresh paths; do not overwrite Phase 16 results")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    commit = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if commit != plan["source_commit"]:
        raise ValueError("Memora commit differs from fixed source")
    rows, group_stats, qkeys = [], [], set()
    files = sorted((upstream / "data").glob("*/*/evaluation_questions_*.json"))
    if len(files) != 30:
        raise ValueError("Expected 30 source groups")
    for qfile in files:
        group = qfile.parent
        sessions = load_group(group)
        ids_available = {s["session_id"] for s in sessions}
        questions = []
        for task, entries in json.loads(qfile.read_text(encoding="utf-8"))["questions"].items():
            for question in entries:
                key = group.parent.name, group.name, question["question_id"]
                if key in qkeys:
                    raise ValueError("Duplicate question key")
                qkeys.add(key)
                active = evidence_ids(question, "memory_evidence")
                obsolete = evidence_ids(question, "forgetting_evidence")
                if not (active | obsolete) <= ids_available:
                    raise ValueError("Evidence session missing")
                if any(s["date"] > question["question_date"] for s in sessions):
                    raise ValueError("Future session leaked")
                questions.append((task, question, active, obsolete))
        shapes = {}
        for method in METHODS:
            tokens, docids, counts, reasons, overlong = partitions(sessions, method)
            if method.startswith("random_") and counts != shapes["writer"]["counts"]:
                raise AssertionError("Null document count differs within session")
            shapes[method] = {"counts": counts, "documents": len(tokens), "words": sum(map(len, tokens)),
                              "overlong_turns": overlong, "close_reasons": reasons}
            index = BM25(tokens)
            for task, question, active, obsolete in questions:
                common = {"period": group.parent.name, "persona": group.name,
                          "question_id": question["question_id"], "task": task,
                          "active_count": len(active), "obsolete_count": len(obsolete),
                          "overlap_count": len(active & obsolete)}
                rows.extend({**common, **row} for row in score(question["question"], active, obsolete,
                                                                 method, index, docids))
            del index, tokens
        group_stats.append({"period": group.parent.name, "persona": group.name,
                            "sessions": len(sessions), "questions": len(questions),
                            "writer_segments": shapes["writer"]["documents"],
                            "full_view_words": shapes["writer"]["words"],
                            "writer_overlong": shapes["writer"]["overlong_turns"],
                            "writer_reasons": shapes["writer"]["close_reasons"],
                            "random_counts_equal": all(shapes[f"random_{seed}"]["counts"] ==
                                                       shapes["writer"]["counts"] for seed in SEEDS),
                            "random_words_equal": all(shapes[f"random_{seed}"]["words"] ==
                                                      shapes["writer"]["words"] for seed in SEEDS)})
        print(f"Phase 16 {len(group_stats)}/30 {group.parent.name}/{group.name}", flush=True)
    if len(qkeys) != 600 or len(rows) != 600 * len(METHODS) * len(BUDGETS):
        raise AssertionError("Incomplete result matrix")
    data = {"phase": 16, "source_commit": commit, "plan_sha256": sha(PLAN_PATH),
            "phase8_writer_plan_sha256": sha(ROOT / "configs/phase8_causal_plan.json"),
            "status": "exploratory; source labels previously inspected", "seeds": SEEDS,
            "budgets_words": BUDGETS, **summarize(rows, group_stats)}
    output_summary.parent.mkdir(parents=True, exist_ok=True)
    output_rows.parent.mkdir(parents=True, exist_ok=True)
    output_summary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with gzip.open(output_rows, "wt", encoding="utf-8", compresslevel=9) as handle:
        json.dump(rows, handle, ensure_ascii=False, separators=(",", ":"))
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, default=ROOT.parent / "memora-upstream")
    parser.add_argument("--summary", type=Path, default=ROOT / "results/phase16_summary.json")
    parser.add_argument("--rows", type=Path, default=ROOT / "results/phase16_rows.json.gz")
    args = parser.parse_args()
    print(json.dumps(run(args.upstream, args.summary, args.rows)["primary"], indent=2))
