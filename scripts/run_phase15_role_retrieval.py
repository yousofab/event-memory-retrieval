"""Phase 15: paired, session-level Memora retrieval under three role views.

Source labels are passed only to score_question(), never into the BM25 index.
Outputs contain counts, numeric flags and source question keys, no dialogue.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import heapq
import json
import math
from pathlib import Path
import random
import statistics
import subprocess

from run_baselines import ROOT, words
from audit_phase14_memora import references


PLAN = json.loads((ROOT / "configs/phase15_plan.json").read_text(encoding="utf-8"))
METHODS = ("assistant_only", "role_corrected", "user_only")
K_VALUES = (1, 5, 10)


class BM25:
    def __init__(self, documents):
        self.n = len(documents)
        self.tf = [Counter(doc) for doc in documents]
        self.lengths = [len(doc) for doc in documents]
        self.average = max(sum(self.lengths) / self.n, 1) if self.n else 1
        self.postings = defaultdict(list)
        for pos, tf in enumerate(self.tf):
            for term, count in tf.items():
                self.postings[term].append((pos, count))

    def top(self, query, count):
        score = defaultdict(float)
        for term in set(words(query)):
            post = self.postings.get(term, ())
            if not post:
                continue
            df = len(post)
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for pos, tf in post:
                norm = 0.25 + 0.75 * self.lengths[pos] / self.average
                score[pos] += idf * tf * 2.2 / (tf + 1.2 * norm)
        return heapq.nsmallest(count, range(self.n), key=lambda pos: (-score[pos], -pos))


def load_group(group):
    files = sorted((group / "conversations").glob("session_*.json"))
    items = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    ids = [item["session_id"] for item in items]
    assert ids == sorted(set(ids)) and ids
    for item in items:
        assert {t["speaker"] for t in item["conversation"]} <= {"ai_agent", "user_agent"}
    return items


def documents(sessions):
    output = {method: [] for method in METHODS}
    for session in sessions:
        by_role = {"ai_agent": [], "user_agent": []}
        all_turns = []
        for turn in session["conversation"]:
            tokens = words(turn.get("message") or "")
            by_role[turn["speaker"]].extend(tokens)
            all_turns.extend(tokens)
        output["assistant_only"].append(by_role["ai_agent"])
        output["role_corrected"].append(all_turns)
        output["user_only"].append(by_role["user_agent"])
        assert len(all_turns) == len(by_role["ai_agent"]) + len(by_role["user_agent"])
    return output


def evidence_ids(question, key):
    return set(references(question.get(key, {})))


def age_bin(fraction):
    if fraction <= 0.10:
        return "<=0.10"
    if fraction <= 0.50:
        return "(0.10,0.50]"
    return ">0.50"


def score_question(question, task, group, sessions, indexes, token_docs):
    ids = [s["session_id"] for s in sessions]
    position = {sid: i for i, sid in enumerate(ids)}
    active = evidence_ids(question, "memory_evidence")
    obsolete = evidence_ids(question, "forgetting_evidence")
    if not (active | obsolete) <= set(ids):
        raise ValueError("Missing evidence session")
    if any(s["date"] > question["question_date"] for s in sessions):
        raise ValueError("Future session relative to question date")
    overlap = active & obsolete
    age = (len(ids) - 1 - max(position[sid] for sid in active)) / len(ids) if active else None
    common = {"period": group.parent.name, "persona": group.name,
              "question_id": question["question_id"], "task": task,
              "active_count": len(active), "obsolete_count": len(obsolete),
              "overlap_count": len(overlap), "age_fraction_newest_active": round(age, 6) if age is not None else None,
              "age_bin": age_bin(age) if age is not None else None,
              "active_count_bin": None if not active else "1" if len(active) == 1 else "2-3" if len(active) <= 3 else "4+"}
    rows = []
    for method in METHODS:
        ranks = indexes[method].top(question["question"], max(K_VALUES))
        for k in K_VALUES:
            chosen = {ids[pos] for pos in ranks[:k]}
            found_active = chosen & active
            found_obsolete = chosen & obsolete
            rows.append({**common, "method": method, "k": k,
                         "active_found": len(found_active), "obsolete_found": len(found_obsolete),
                         "active_any": int(bool(found_active)) if active else None,
                         "active_all": int(active <= chosen) if active else None,
                         "active_fraction": round(len(found_active) / len(active), 6) if active else None,
                         "obsolete_any": int(bool(found_obsolete)) if obsolete else None,
                         "obsolete_all": int(obsolete <= chosen) if obsolete else None,
                         "obsolete_only_disjoint": int(bool(found_obsolete) and not found_active)
                         if active and obsolete and not overlap else None,
                         "word_cost": sum(len(token_docs[method][pos]) for pos in ranks[:k])})
    return rows


def mean_metric(rows, field):
    values = [row[field] for row in rows if row[field] is not None]
    return {"eligible": len(values), "mean": round(statistics.mean(values), 6) if values else None,
            "sum": round(sum(values), 6)}


def describe(rows):
    result = {"total_questions": len(rows) // (len(METHODS) * len(K_VALUES)), "methods": {}, "by_period": {},
              "by_task": {}, "by_active_count": {}, "by_age": {}, "by_overlap": {}}
    metric_fields = ("active_any", "active_all", "active_fraction", "obsolete_any", "obsolete_all",
                     "obsolete_only_disjoint", "word_cost")
    for method in METHODS:
        result["methods"][method] = {str(k): {f: mean_metric([r for r in rows if r["method"] == method and r["k"] == k], f)
                                                 for f in metric_fields} for k in K_VALUES}
    base = [r for r in rows if r["k"] == 5 and r["active_any"] is not None]
    pairs = defaultdict(dict)
    for r in base:
        key = (r["period"], r["persona"], r["question_id"])
        pairs[key][r["method"]] = r
    assert all(len(p) == 3 for p in pairs.values())
    differences = []
    for key, pair in pairs.items():
        a, b = pair["assistant_only"], pair["role_corrected"]
        differences.append({"period": a["period"], "persona": a["persona"], "task": a["task"],
                            "count_bin": a["active_count_bin"], "age_bin": a["age_bin"],
                            "overlap": "yes" if a["overlap_count"] else "no",
                            "delta": b["active_any"] - a["active_any"]})
    result["primary"] = {"eligible": len(differences), "difference_sum": sum(x["delta"] for x in differences),
                         "difference_mean": round(statistics.mean(x["delta"] for x in differences), 6),
                         "corrected_only": sum(x["delta"] == 1 for x in differences),
                         "assistant_only": sum(x["delta"] == -1 for x in differences),
                         "paired_equal": sum(x["delta"] == 0 for x in differences)}
    by_group = defaultdict(list)
    for row in differences:
        by_group[(row["period"], row["persona"])].append(row["delta"])
    assert len(by_group) == 30
    groups = sorted(by_group)
    rng = random.Random(15)
    draws = []
    for _ in range(2000):
        sample = [by_group[groups[rng.randrange(30)]] for _ in range(30)]
        draws.append(sum(map(sum, sample)) / sum(map(len, sample)))
    draws.sort()
    result["primary"]["descriptive_cluster_bootstrap_95"] = [round(draws[49], 6), round(draws[1949], 6)]
    result["primary"]["groups"] = 30
    for title, field in (("by_period", "period"), ("by_task", "task"),
                         ("by_active_count", "count_bin"), ("by_age", "age_bin"),
                         ("by_overlap", "overlap")):
        for key in sorted({r[field] for r in differences}):
            selected = [r["delta"] for r in differences if r[field] == key]
            result[title][key] = {"eligible": len(selected), "corrected_only": selected.count(1),
                                  "assistant_only": selected.count(-1),
                                  "difference_mean": round(statistics.mean(selected), 6)}
    return result


def run(upstream, output_summary, output_rows):
    if output_summary.exists() or output_rows.exists():
        raise FileExistsError("Phase 15 result already exists; do not overwrite")
    commit = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if commit != PLAN["source_commit"]:
        raise ValueError("Memora source commit mismatch")
    rows, group_stats = [], []
    keys = set()
    for qfile in sorted((upstream / "data").glob("*/*/evaluation_questions_*.json")):
        group = qfile.parent
        sessions = load_group(group)
        doc = documents(sessions)
        indexes = {name: BM25(doc[name]) for name in METHODS}
        questions = json.loads(qfile.read_text(encoding="utf-8"))["questions"]
        count = 0
        for task, entries in questions.items():
            for q in entries:
                key = (group.parent.name, group.name, q["question_id"])
                if key in keys:
                    raise ValueError("Duplicate question key")
                keys.add(key)
                rows.extend(score_question(q, task, group, sessions, indexes, doc))
                count += 1
        group_stats.append({"period": group.parent.name, "persona": group.name,
                            "sessions": len(sessions), "questions": count,
                            **{name + "_words": sum(map(len, doc[name])) for name in METHODS}})
        print(f"Completed {group.parent.name}/{group.name}: {count} questions", flush=True)
    assert len(group_stats) == 30 and len(keys) == 600
    summary = {"phase": 15, "source_commit": commit,
               "protocol_sha256": hashlib.sha256((ROOT / "configs/phase15_plan.json").read_bytes()).hexdigest(),
               "method": "session BM25, top-k; no answer model", "group_stats": group_stats,
               "summary": describe(rows)}
    output_summary.parent.mkdir(parents=True, exist_ok=True)
    output_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_rows.write_bytes(gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--summary", type=Path, default=ROOT / "results/phase15_summary.json")
    p.add_argument("--rows", type=Path, default=ROOT / "results/phase15_rows.json.gz")
    args = p.parse_args()
    result = run(args.upstream.resolve(), args.summary, args.rows)
    print(json.dumps(result["summary"]["primary"], ensure_ascii=False, indent=2))
