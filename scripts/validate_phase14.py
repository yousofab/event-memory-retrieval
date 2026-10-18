"""Check aggregate Phase 14 results independently of the upstream corpus."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT / "configs/phase14_plan.json").read_text(encoding="utf-8"))
result = json.loads((ROOT / "results/phase14_summary.json").read_text(encoding="utf-8"))
assert result["upstream_commit"] == plan["upstream_commit"]
assert result["evaluator_sha256"] == plan["evaluator_sha256"]
groups = result["groups"]
assert len(groups) == 30 and len({(g["period"], g["persona"]) for g in groups}) == 30
assert Counter(g["period"] for g in groups) == {"weekly": 10, "monthly": 10, "quarterly": 10}
totals = result["totals"]
for key in totals:
    assert sum(g.get(key, 0) for g in groups) == totals[key], key
assert totals["sessions"] == sum(g["sessions"] for g in groups)
assert totals["speaker_user_agent"] + totals["speaker_ai_agent"] == totals["turns"]
assert totals["user_agent_memory_omitted_full_session"] <= totals["speaker_user_agent"]
assert totals["evidence_sessions_with_user_memory_turn"] + totals["evidence_sessions_without_user_memory_turn"] + totals["missing_evidence_sessions"] == totals["distinct_evidence_sessions"]
assert totals["questions_remembering"] == totals["questions_reasoning"] == totals["questions_recommending"] == 200
assert result["partial_branch_user_line_observed"]
assert "USER_SENTINEL_14" not in json.dumps(result)
print("Phase 14 validation passed: 30 groups, matching totals and branch checks")
