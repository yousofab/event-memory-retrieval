"""Registered post-result sensitivity: whole-session retrieval at equal word budgets."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import statistics
import subprocess

from run_baselines import ROOT
from run_phase15_role_retrieval import BM25, METHODS, PLAN, documents, evidence_ids, load_group


BUDGETS = (1024, 2048)


def select(order, lengths, budget):
    chosen = []
    remaining = budget
    for pos in order:
        cost = lengths[pos]
        if cost and cost <= remaining:
            chosen.append(pos)
            remaining -= cost
    return chosen, budget - remaining


def run(upstream, output):
    if output.exists():
        raise FileExistsError(output)
    sha = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if sha != PLAN["source_commit"]:
        raise ValueError("Memora source commit mismatch")
    rows = []
    for qfile in sorted((upstream / "data").glob("*/*/evaluation_questions_*.json")):
        group = qfile.parent
        sessions = load_group(group)
        ids = [s["session_id"] for s in sessions]
        docs = documents(sessions)
        indexes = {name: BM25(docs[name]) for name in METHODS}
        questions = json.loads(qfile.read_text(encoding="utf-8"))["questions"]
        for task, entries in questions.items():
            for q in entries:
                if any(s["date"] > q["question_date"] for s in sessions):
                    raise ValueError("Future session")
                active = evidence_ids(q, "memory_evidence")
                obsolete = evidence_ids(q, "forgetting_evidence")
                if not (active | obsolete) <= set(ids):
                    raise ValueError("Missing evidence session")
                for method in METHODS:
                    order = indexes[method].top(q["question"], len(sessions))
                    for budget in BUDGETS:
                        chosen, used = select(order, indexes[method].lengths, budget)
                        retrieved = {ids[pos] for pos in chosen}
                        assert used <= budget
                        rows.append({"period": group.parent.name, "persona": group.name,
                                     "question_id": q["question_id"], "task": task,
                                     "method": method, "budget": budget,
                                     "active_count": len(active), "obsolete_count": len(obsolete),
                                     "active_any": int(bool(retrieved & active)) if active else None,
                                     "active_all": int(active <= retrieved) if active else None,
                                     "obsolete_any": int(bool(retrieved & obsolete)) if obsolete else None,
                                     "selected_sessions": len(chosen), "spent_words": used})
        print(f"Budget complete {group.parent.name}/{group.name}", flush=True)
    assert len(rows) == 600 * 3 * 2
    overview = {}
    for budget in BUDGETS:
        block = [r for r in rows if r["budget"] == budget]
        overview[str(budget)] = {}
        for method in METHODS:
            subset = [r for r in block if r["method"] == method]
            overview[str(budget)][method] = {
                field: {"eligible": len(v), "sum": sum(v), "mean": round(statistics.mean(v), 6)}
                for field in ("active_any", "active_all", "obsolete_any", "selected_sessions", "spent_words")
                if (v := [r[field] for r in subset if r[field] is not None])}
        pair = defaultdict(dict)
        for row in block:
            key = (row["period"], row["persona"], row["question_id"])
            if row["active_any"] is not None:
                pair[key][row["method"]] = row["active_any"]
        assert len(pair) == 398 and all(len(v) == 3 for v in pair.values())
        delta = [p["role_corrected"] - p["assistant_only"] for p in pair.values()]
        groups = defaultdict(list)
        for key, values in pair.items():
            groups[key[:2]].append(values["role_corrected"] - values["assistant_only"])
        assert len(groups) == 30
        names = sorted(groups)
        rng = random.Random(15)
        draws = []
        for _ in range(2000):
            sample = [groups[names[rng.randrange(30)]] for _ in range(30)]
            draws.append(sum(map(sum, sample)) / sum(map(len, sample)))
        draws.sort()
        overview[str(budget)]["paired"] = {
            "eligible": len(delta), "corrected_only": delta.count(1),
            "assistant_only": delta.count(-1), "difference_mean": round(statistics.mean(delta), 6),
            "descriptive_cluster_bootstrap_95": [round(draws[49], 6), round(draws[1949], 6)]}
    result = {"phase": 15, "source_commit": sha, "post_result_amendment_commit": "d96b154a3a8dc1bb99503e8fab7ffd9c2e73f1f3",
              "protocol_sha256": hashlib.sha256((ROOT / "configs/phase15_plan.json").read_bytes()).hexdigest(),
              "word_budget_method": "whole-session, skip overlength, continue scanning, no zero-word sessions",
              "overview": overview, "rows": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    return overview


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT / "results/phase15_budget.json.gz")
    args = p.parse_args()
    print(json.dumps(run(args.upstream.resolve(), args.output), ensure_ascii=False, indent=2))
