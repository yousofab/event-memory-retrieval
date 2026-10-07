"""Check change-point behavior and partition invariants independently of LoCoMo."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_event_development import event_segments


class EventTests(unittest.TestCase):
    def test_topic_shift_cut_and_no_label_use(self):
        sample = {"conversation": {"session_1": [
            {"dia_id": "D1:1", "text": "cat kitten whiskers"},
            {"dia_id": "D1:2", "text": "cat kitten paws"},
            {"dia_id": "D1:3", "text": "train station railway"},
            {"dia_id": "D1:4", "text": "train station platform"}]}}
        before = event_segments(sample, 3, 6, 9, 1)
        self.assertEqual([s["turn_ids"] for s in before],
                         [["D1:1", "D1:2"], ["D1:3", "D1:4"]])
        sample.update(qa=[{"question": "cat", "answer": "secret", "evidence": ["D1:4"]}],
                      event_summary="train", observation="train", session_summary="train")
        self.assertEqual(before, event_segments(sample, 3, 6, 9, 1))

    def test_oversized_turn_kept_whole_and_no_loss(self):
        sample = {"conversation": {"session_1": [
            {"dia_id": "D1:1", "text": "a b c d e f g h i j"},
            {"dia_id": "D1:2", "text": "small turn"}],
            "session_2": [{"dia_id": "D2:1", "text": "more text"}]}}
        result = event_segments(sample, 2, 3, 5, 1)
        self.assertEqual([s["turn_ids"] for s in result],
                         [["D1:1"], ["D1:2"], ["D2:1"]])
        self.assertEqual(sum(s["word_cost"] for s in result), 14)


if __name__ == "__main__":
    unittest.main()
