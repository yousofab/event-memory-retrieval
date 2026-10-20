"""Post-result Phase 16 sensitivity at paired equal selected document counts."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import statistics
import subprocess

from run_baselines import ROOT
from run_phase15_role_retrieval import BM25, evidence_ids, load_group
from run_phase16_boundaries import PLAN_PATH, SEEDS, METHODS, partitions, select, sha


AMENDMENT_REMOTE_COMMIT = "75e65685cc5ca92bb7c919de2c237f3226edf60e"


def run(upstream, output):
    if output.exists():
        raise FileExistsError("Use a fresh post-result sensitivity path")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    commit = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if commit != plan["source_commit"]:
        raise ValueError("Source commit mismatch")
    previous = json.loads(gzip.decompress((ROOT / "results/phase16_rows.json.gz").read_bytes()))
    control = {(r["period"], r["persona"], r["question_id"], r["method"]): r for r in previous
               if r["budget_words"] == 1024 and r["method"] != "session"}
    rows = []
    for qfile in sorted((upstream / "data").glob("*/*/evaluation_questions_*.json")):
        group = qfile.parent
        sessions = load_group(group)
        questions = [(q, evidence_ids(q, "memory_evidence"),
                      evidence_ids(q, "forgetting_evidence"))
                     for entries in json.loads(qfile.read_text(encoding="utf-8"))["questions"].values()
                     for q in entries]
        questions = [(q, active, obsolete) for q, active, obsolete in questions if active]
        per_question = defaultdict(dict)
        for method in METHODS[:-1]:
            documents, ids, _, _, _ = partitions(sessions, method)
            index = BM25(documents)
            for q, active, obsolete in questions:
                selected = select(index.top(q["question"], index.n), index.lengths, 1024)
                key = group.parent.name, group.name, q["question_id"]
                original = control[key + (method,)]
                found = int(bool(active & {ids[pos] for pos in selected}))
                if (original["selected_documents"] != len(selected) or
                    original["retrieved_words"] != sum(index.lengths[pos] for pos in selected) or
                    original["active_any"] != found):
                    raise AssertionError("Mismatch with original budgeted retrieval")
                per_question[key][method] = (selected, ids, index.lengths, active, obsolete)
            del index, documents
        for key, by_method in per_question.items():
            if set(by_method) != set(METHODS[:-1]):
                raise AssertionError("Incomplete paired sensitivity")
            common = min(len(by_method[m][0]) for m in METHODS[:-1])
            for method, (chosen, ids, lengths, active, obsolete) in by_method.items():
                prefix = chosen[:common]
                seen = {ids[pos] for pos in prefix}
                rows.append({"period": key[0], "persona": key[1], "question_id": key[2],
                             "method": method, "common_selected": common,
                             "active_any": int(bool(active & seen)),
                             "overlap_count": len(active & obsolete),
                             "selected_sessions": len(seen),
                             "retrieved_words": sum(lengths[pos] for pos in prefix)})
        print(f"Sensitivity {group.parent.name}/{group.name}: {len(per_question)} questions", flush=True)
    if len(rows) != 398 * 6 or any(not 0 <= r["retrieved_words"] <= 1024 for r in rows):
        raise AssertionError("Unexpected post-result matrix")
    pairs = defaultdict(dict)
    for row in rows:
        pairs[row["period"], row["persona"], row["question_id"]][row["method"]] = row
    differences = []
    for pair in pairs.values():
        if len({r["common_selected"] for r in pair.values()}) != 1:
            raise AssertionError("Different selected document count")
        differences.append((pair["writer"]["active_any"] -
                            statistics.mean(pair[f"random_{seed}"]["active_any"] for seed in SEEDS),
                            pair["writer"]["overlap_count"]))
    output_data = {"phase": 16, "status": "post-result exploratory sensitivity",
                   "source_commit": commit, "plan_sha256": sha(PLAN_PATH),
                   "amendment_remote_commit": AMENDMENT_REMOTE_COMMIT,
                   "amendment_sha256": sha(ROOT / "docs/phase16_post_result_amendment.md"),
                   "eligible": len(pairs), "methods": {},
                   "common_selected_min": min(r["common_selected"] for r in rows),
                   "common_selected_median": statistics.median(r["common_selected"] for r in rows),
                   "common_selected_max": max(r["common_selected"] for r in rows),
                   "writer_minus_random_mean": round(statistics.mean(d for d, _ in differences), 6),
                   "disjoint_count": sum(o == 0 for _, o in differences),
                   "disjoint_difference_mean": round(statistics.mean(d for d, o in differences if o == 0), 6),
                   "rows": rows}
    for method in METHODS[:-1]:
        subset = [r for r in rows if r["method"] == method]
        output_data["methods"][method] = {
            "active_hits": sum(r["active_any"] for r in subset),
            "mean_selected_sessions": round(statistics.mean(r["selected_sessions"] for r in subset), 6),
            "mean_words": round(statistics.mean(r["retrieved_words"] for r in subset), 6)}
    output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(output_data, f, ensure_ascii=False, separators=(",", ":"))
    return output_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, default=ROOT.parent / "memora-upstream")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase16_equal_selected.json.gz")
    args = parser.parse_args()
    result = run(args.upstream, args.output)
    print({k: v for k, v in result.items() if k != "rows"})
