"""Phase 14 contract tests; released data is fetched separately."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_phase14_memora import references, upstream_builder


class Phase14Tests(unittest.TestCase):
    def test_nested_evidence_references(self):
        evidence = {"items": [{"session_id": 3}, {"nested": {"session_id": 4}},
                              {"session_id": "5"}], "value": 7}
        self.assertEqual(list(references(evidence)), [3, 4])

    def test_pinned_source_roles_when_available(self):
        upstream = Path(__file__).resolve().parents[2] / "memora-upstream"
        if not upstream.exists():
            self.skipTest("Pinned upstream data not present; run the audit with --upstream")
        builder = upstream_builder(upstream)
        conv = [{"session_id": 1, "date": "2025-01-01", "conversation": [
            {"speaker": "user_agent", "message": "USER_SENTINEL_14"},
            {"speaker": "ai_agent", "message": "ASSISTANT_SENTINEL_14"}]}]
        context, meta = builder.build_conversation_context(conv, max_tokens=None)
        self.assertNotIn("USER_SENTINEL_14", context)
        self.assertIn("ASSISTANT_SENTINEL_14", context)
        self.assertFalse(meta["was_truncated"])


if __name__ == "__main__":
    unittest.main()
