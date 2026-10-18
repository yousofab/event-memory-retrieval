"""Audit the released Memora direct-model formatter without invoking an API.

Only aggregate counts are persisted. The upstream method is AST-extracted from
the pinned release; its production imports and model clients are never loaded.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / "configs/phase14_plan.json").read_text(encoding="utf-8"))
SAMPLE = "weekly/marketing_manager/conversations/session_0146.json"


def upstream_builder(upstream):
    source = upstream / PLAN["evaluator_path"]
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != PLAN["evaluator_sha256"]:
        raise ValueError("Upstream evaluator SHA-256 mismatch")
    tree = ast.parse(source.read_text(encoding="utf-8"))
    klass = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "PromptBuilder")
    methods = [x for x in klass.body if isinstance(x, ast.FunctionDef) and x.name in ("__init__", "build_conversation_context")]
    assert len(methods) == 2
    # The method remains exactly upstream code; only the class wrapper/imports
    # and token counter are provided here. No cap is passed to the method.
    module = ast.Module(body=[ast.ClassDef(name="PromptBuilder", bases=[], keywords=[],
                                           body=methods, decorator_list=[])], type_ignores=[])
    ast.fix_missing_locations(module)
    env = {"Optional": Optional, "List": List, "Dict": Dict, "Any": Any,
           "Tuple": Tuple, "count_tokens": lambda s, _: len(s.split()),
           "MAX_CONTEXT_TOKENS_HARD_CAP": 10**15}
    exec(compile(module, str(source), "exec"), env)
    return env["PromptBuilder"](model_name=None)


def references(node):
    if isinstance(node, dict):
        if "session_id" in node and isinstance(node["session_id"], int):
            yield node["session_id"]
        for value in node.values():
            yield from references(value)
    elif isinstance(node, list):
        for value in node:
            yield from references(value)


def audit(upstream):
    git_sha = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if git_sha != PLAN["upstream_commit"]:
        raise ValueError("Upstream commit mismatch")
    builder = upstream_builder(upstream)
    synthetic = {"session_id": 1, "date": "2025-01-01", "conversation": [
        {"speaker": "user_agent", "message": "USER_SENTINEL_14", "share_memory": True},
        {"speaker": "ai_agent", "message": "ASSISTANT_SENTINEL_14"}]}
    original, meta = builder.build_conversation_context([synthetic], max_tokens=None)
    aliased = {**synthetic, "conversation": [{**t, "speaker": "user"} if t["speaker"] == "user_agent" else t for t in synthetic["conversation"]]}
    corrected, meta2 = builder.build_conversation_context([aliased], max_tokens=None)
    assert "USER_SENTINEL_14" not in original and "ASSISTANT_SENTINEL_14" in original
    assert "User: USER_SENTINEL_14" in corrected and meta["was_truncated"] is False and meta2["was_truncated"] is False
    sample = json.loads((upstream / "data" / SAMPLE).read_text(encoding="utf-8"))
    sample_marker = next(t["message"] for t in sample["conversation"] if t.get("share_memory") and t["speaker"] == "user_agent")
    original_sample, _ = builder.build_conversation_context([sample], max_tokens=None)
    aliased_sample = {**sample, "conversation": [{**t, "speaker": "user"} if t["speaker"] == "user_agent" else t for t in sample["conversation"]]}
    corrected_sample, _ = builder.build_conversation_context([aliased_sample], max_tokens=None)
    # This marker is in no assistant reply in the fixed sample. We assert only
    # the direct line omission, and record no message text in the output.
    assert "User: " + sample_marker not in original_sample
    assert "User: " + sample_marker in corrected_sample
    partial, partial_meta = builder.build_conversation_context([{
        "session_id": 1, "date": "2025-01-01", "conversation": [
            {"speaker": "user_agent", "message": "PARTIAL_SENTINEL_14"},
            {"speaker": "ai_agent", "message": "word " * 350}]}], max_tokens=140)
    assert partial_meta["was_truncated"] and "User: PARTIAL_SENTINEL_14" in partial

    groups = []
    totals = Counter()
    for question_path in sorted((upstream / "data").glob("*/*/evaluation_questions_*.json")):
        group_dir = question_path.parent
        sessions = sorted((group_dir / "conversations").glob("session_*.json"))
        ids = set()
        memory_ids = set()
        counts = Counter()
        for path in sessions:
            obj = json.loads(path.read_text(encoding="utf-8"))
            ident = obj["session_id"]
            if ident in ids:
                raise ValueError("Duplicate session id")
            ids.add(ident)
            counts["sessions"] += 1
            for turn in obj["conversation"]:
                role = turn.get("speaker", "unknown")
                counts["turns"] += 1
                counts["speaker_" + role] += 1
                if role == "user_agent":
                    counts["user_agent_omitted_full_session"] += 1
                    if turn.get("share_memory") is True:
                        counts["user_agent_memory_omitted_full_session"] += 1
                        memory_ids.add(ident)
                if role == "ai_agent":
                    counts["ai_agent_included_full_session"] += 1
        counts["sessions_with_user_memory_turn"] = len(memory_ids)
        questions = json.loads(question_path.read_text(encoding="utf-8"))["questions"]
        ref_ids = set()
        for task, entries in questions.items():
            counts["questions_" + task] = len(entries)
            for q in entries:
                for field in ("memory_evidence", "forgetting_evidence"):
                    refs = list(references(q.get(field, {})))
                    counts[field + "_references"] += len(refs)
                    ref_ids.update(refs)
        counts["distinct_evidence_sessions"] = len(ref_ids)
        counts["missing_evidence_sessions"] = len(ref_ids - ids)
        counts["evidence_sessions_with_user_memory_turn"] = len(ref_ids & memory_ids)
        counts["evidence_sessions_without_user_memory_turn"] = len((ref_ids & ids) - memory_ids)
        groups.append({"period": group_dir.parent.name, "persona": group_dir.name, **dict(sorted(counts.items()))})
        # Do not add distinct-set counts across groups to global unique count.
        for key, val in counts.items():
            totals[key] += val
    assert len(groups) == 30
    assert totals["sessions"] > 0 and totals["user_agent_omitted_full_session"] == totals["speaker_user_agent"]
    return {"phase": 14, "upstream_commit": git_sha,
            "evaluator_sha256": PLAN["evaluator_sha256"],
            "branch_condition": "complete-session, no truncation; max_tokens=None and model_name=None",
            "sample_session_path": SAMPLE,
            "sample_sha256": hashlib.sha256((upstream / "data" / SAMPLE).read_bytes()).hexdigest(),
            "synthetic_user_line_original": False, "synthetic_user_line_aliased": True,
            "sample_memory_user_line_original": False, "sample_memory_user_line_aliased": True,
            "partial_branch_user_line_observed": True,
            "totals": dict(sorted(totals.items())), "groups": groups,
            "limits": ["No answer-model rerun", "No score inference", "Partial-session branch uses a different role condition", "Assistant echoes may retain user facts"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT / "results/phase14_summary.json")
    args = p.parse_args()
    result = audit(args.upstream.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], sort_keys=True))


if __name__ == "__main__":
    main()
