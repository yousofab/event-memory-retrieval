"""Phase 7 invariants for adaptation, label isolation and repeated source IDs."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase7_external import audit_record, gold_labels, public_sample, score
from run_baselines import make_segments


def fixture():
    return {"question_id": "example", "question_type": "single-session-user",
            "question": "When?", "answer": "later", "question_date": "2025-01-01",
            "haystack_session_ids": ["duplicate", "duplicate"],
            "haystack_dates": ["2024-01-01", "2024-02-01"],
            "answer_session_ids": ["duplicate"],
            "haystack_sessions": [
                [{"role": "user", "content": "first context", "has_answer": False}],
                [{"role": "assistant", "content": "second context", "has_answer": True}]]}


class Phase7ExternalTests(unittest.TestCase):
    def test_source_labels_never_enter_segmentation_input(self):
        record = fixture()
        public = public_sample(record)
        self.assertEqual(public["conversation"]["session_2"][0],
                         {"dia_id": "session_2:1", "text": "second context"})
        original = public_sample(record)
        record["haystack_sessions"][1][0]["has_answer"] = False
        record["answer"] = "changed"
        record["haystack_dates"] = ["changed", "changed"]
        self.assertEqual(public_sample(record), original)

    def test_duplicate_session_string_does_not_merge_gold_turns(self):
        record = fixture()
        gold, answer, marked, duplicate = audit_record(record)
        self.assertTrue(duplicate)
        self.assertEqual(gold, {"session_2:1"})
        self.assertEqual(marked, answer)
        sample = public_sample(record)
        segments = make_segments(sample, "session", 128)
        row = score(record, segments, [0, 1], gold, answer, 2)
        self.assertFalse(row["all_marked_turns"])
        self.assertTrue(row["all_official_sessions"])
        self.assertEqual(row["gold_segment_word_cost"], 2)

    def test_abstention_excluded_despite_misleading_metadata(self):
        record = fixture()
        record["question_id"] = "example_abs"
        self.assertIsNone(audit_record(record))
        self.assertEqual(len(gold_labels(record)[0]), 1)

    def test_marked_turn_outside_official_evidence_rejected(self):
        record = fixture()
        record["answer_session_ids"] = ["elsewhere"]
        with self.assertRaises(ValueError):
            audit_record(record)


if __name__ == "__main__":
    unittest.main()
