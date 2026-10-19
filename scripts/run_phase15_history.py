"""Exploratory content-history coverage; intentionally separate from gold ID recall."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import statistics
import subprocess

from run_baselines import ROOT
from run_phase15_role_retrieval import BM25, METHODS, PLAN, documents, evidence_ids, load_group
from run_phase15_budget import select


def run(upstream, output):
    if output.exists():
        raise FileExistsError(output)
    commit = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if commit != PLAN["source_commit"]:
        raise ValueError("Source commit mismatch")
    rows = []
    references = 0
    for qfile in sorted((upstream / "data").glob("*/*/evaluation_questions_*.json")):
        group = qfile.parent
        questions = json.loads(qfile.read_text(encoding="utf-8"))["questions"]
        target = [q for q in questions["remembering"] if "session_history" in q.get("memory_evidence", {})]
        if not target:
            continue
        sessions = load_group(group)
        ids = [s["session_id"] for s in sessions]
        id_set = set(ids)
        docs = documents(sessions)
        indexes = {method: BM25(docs[method]) for method in METHODS}
        for q in target:
            history = q["memory_evidence"]["session_history"]
            assert history and all(isinstance(sid, int) for sid in history) and set(history) <= id_set
            assert not evidence_ids(q, "memory_evidence")
            assert all(s["date"] <= q["question_date"] for s in sessions)
            references += len(history)
            for method in METHODS:
                rank = indexes[method].top(q["question"], len(sessions))
                for label, pos in (("top1", rank[:1]), ("top5", rank[:5]), ("top10", rank[:10]),
                                   ("words1024", select(rank, indexes[method].lengths, 1024)[0]),
                                   ("words2048", select(rank, indexes[method].lengths, 2048)[0])):
                    selected = {ids[i] for i in pos}
                    rows.append({"period": group.parent.name, "persona": group.name, "question_id": q["question_id"],
                                 "method": method, "selection": label, "history_count": len(set(history)),
                                 "any_history": int(bool(selected & set(history))),
                                 "found_history": len(selected & set(history)),
                                 "selected_sessions": len(pos), "spent_words": sum(indexes[method].lengths[i] for i in pos)})
    assert len(rows) == 156 * 3 * 5 and references == 755
    overview = {}
    for selection in ("top1", "top5", "top10", "words1024", "words2048"):
        subset = [r for r in rows if r["selection"] == selection]
        by_method = {}
        pairs = defaultdict(dict)
        for method in METHODS:
            m = [r for r in subset if r["method"] == method]
            by_method[method] = {"hit": sum(r["any_history"] for r in m),
                                 "mean_sessions": round(statistics.mean(r["selected_sessions"] for r in m), 3),
                                 "mean_words": round(statistics.mean(r["spent_words"] for r in m), 3)}
            for r in m:
                pairs[(r["period"], r["persona"], r["question_id"])][method] = r["any_history"]
        assert len(pairs) == 156 and all(len(p) == 3 for p in pairs.values())
        delta = [p["role_corrected"] - p["assistant_only"] for p in pairs.values()]
        overview[selection] = {"methods": by_method, "paired": {"corrected_only": delta.count(1),
                              "assistant_only": delta.count(-1), "difference_fraction": round(statistics.mean(delta), 6)}}
    result = {"phase": 15, "source_commit": commit, "post_result_registration": "40377b91763ce64cd4b8786d3340badaa8d76487",
              "history_questions": 156, "history_references": references,
              "label": "session_history coverage, not direct active-evidence recall", "overview": overview, "rows": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    return overview


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT / "results/phase15_history.json.gz")
    args = p.parse_args()
    print(json.dumps(run(args.upstream.resolve(), args.output), ensure_ascii=False, indent=2))
