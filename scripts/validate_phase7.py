"""Independent consistency check of immutable Phase 7 outputs without source text."""
import gzip
import hashlib
import json
from collections import Counter, defaultdict

from run_baselines import ROOT
from run_phase7_external import METHODS, sha256


def validate():
    path = ROOT / "results/phase7_external.json"
    compact_path = ROOT / "results/phase7_external.json.gz"
    summary_path = ROOT / "results/phase7_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    zipped = compact_path.read_bytes()
    raw = gzip.decompress(zipped)
    if (hashlib.sha256(zipped).hexdigest() != summary["compressed_result_sha256"] or
            hashlib.sha256(raw).hexdigest() != summary["full_result_sha256"] or
            (path.exists() and path.read_bytes() != raw)):
        raise AssertionError("Full and compressed result differ")
    data = json.loads(raw)
    if any(data[k] != v for k, v in summary.items()
           if k not in ("full_result_sha256", "compressed_result_sha256", "full_result_rows")):
        raise AssertionError("Browsable summary differs from full record")
    plan = json.loads((ROOT / "configs/phase7_external_plan.json").read_text(encoding="utf-8"))
    if (data["external_dataset_sha256"] != plan["external_dataset"]["sha256"] or
            data["phase7_plan_sha256"] != sha256(ROOT / "configs/phase7_external_plan.json") or
            data["phase7_label_amendment_sha256"] != sha256(ROOT / "docs/phase7_label_amendment.md") or
            data["phase7_source_audit_amendment_sha256"] != sha256(
                ROOT / "docs/phase7_source_audit_amendment.md")):
        raise ValueError("Source or registered-protocol checksum differs")
    rows = data["per_question"]
    budgets = {512, 1024, 2048}
    if (len(rows) != 470 * len(METHODS) * len(budgets) or
            len({(r["question_id"], r["method"], r["budget_words"]) for r in rows}) != len(rows)):
        raise ValueError("Missing or repeated method/question/budget rows")
    items = defaultdict(set)
    grouped = defaultdict(list)
    for r in rows:
        if (r["method"] not in METHODS or r["budget_words"] not in budgets or
                r["retrieved_words"] > r["budget_words"] or r["retrieved_words"] < 0 or
                r["all_marked_turns"] != (r["marked_turns_found"] == r["marked_turns_total"]) or
                r["structural_budget"] != (r["gold_segment_word_cost"] > r["budget_words"]) or
                r["marked_turns_total"] < 1 or r["marked_turns_found"] > r["marked_turns_total"] or
                (r["structural_budget"] and r["all_marked_turns"])):
            raise AssertionError("Row violates a budget or evidence invariant")
        if any(key in r for key in ("text", "question", "answer", "has_answer", "gold_ids", "turn_ids")):
            raise AssertionError("Source text/labels leaked into the output")
        items[r["question_id"]].add((r["method"], r["budget_words"]))
        grouped[(r["method"], r["budget_words"])].append(r)
    if len(items) != 470 or any(v != {(m, b) for m in METHODS for b in budgets} for v in items.values()):
        raise AssertionError("Methods/budgets differ between questions")
    recorded = {(r["method"], r["budget_words"]): r for r in data["summary"]}
    if set(grouped) != set(recorded):
        raise AssertionError("Missing summary rows")
    for key, group in grouped.items():
        r = recorded[key]
        if any((r[name] != value) for name, value in (
                ("questions", len(group)),
                ("all_marked_turns_count", sum(t["all_marked_turns"] for t in group)),
                ("all_official_sessions_count", sum(t["all_official_sessions"] for t in group)),
                ("structural_budget_count", sum(t["structural_budget"] for t in group)))):
            raise AssertionError("Summary differs from per-question data")
    by_type = defaultdict(list)
    for row in rows:
        by_type[(row["method"], row["budget_words"], row["question_type"])].append(row)
    for entry in data["by_question_type"]:
        group = by_type.pop((entry["method"], entry["budget_words"], entry["question_type"]))
        if len(group) != entry["questions"] or sum(r["all_marked_turns"] for r in group) != entry["all_marked_turns_count"]:
            raise AssertionError("Question-type summary mismatch")
    if by_type:
        raise AssertionError("Unreported question type")
    primary = defaultdict(dict)
    for row in grouped[("semantic_lsa", 1024)] + grouped[("event", 1024)]:
        primary[row["question_id"]][row["method"]] = row["all_marked_turns"]
    counts = Counter("both" if v["semantic_lsa"] and v["event"] else
                     "semantic_only" if v["semantic_lsa"] else
                     "lexical_only" if v["event"] else "neither" for v in primary.values())
    if dict(counts) != data["discordance_primary_lsa_vs_lexical"]:
        raise AssertionError("Pairing mismatch")
    if (data["audit_counts"]["answerable"] != 470 or
            data["audit_counts"]["abstention_excluded"] != 30 or
            data["audit_counts"]["incomplete_turn_label_sessions"] != 32):
        raise AssertionError("Eligibility/label audit mismatch")
    diagnostic_path = ROOT / "results/phase7_boundary_audit.json"
    if diagnostic_path.exists():
        diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
        if diagnostic["phase7_result_sha256"] != hashlib.sha256(raw).hexdigest():
            raise AssertionError("Post hoc boundary audit refers to another result")
    return {"questions": len(items), "rows": len(rows), "primary_discordance": dict(counts)}


if __name__ == "__main__":
    print(validate())
