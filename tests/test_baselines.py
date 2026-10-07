"""Small independent invariants for the retrieval implementation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_baselines import make_segments, rank, retrieve


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.sample = {"conversation": {
            "session_1": [
                {"dia_id": "D1:1", "text": "red apple"},
                {"dia_id": "D1:2", "text": "blue pear"},
                {"dia_id": "D1:3", "text": "green plum"}],
            "session_2": [{"dia_id": "D2:1", "text": "red plum"}]}}

    def test_fixed_preserves_turns_and_session_boundaries(self):
        chunks = make_segments(self.sample, "fixed", 3)
        self.assertEqual([s["turn_ids"] for s in chunks],
                         [["D1:1"], ["D1:2"], ["D1:3"], ["D2:1"]])
        self.assertEqual([s["word_cost"] for s in chunks], [2, 2, 2, 2])
        sessions = make_segments(self.sample, "session", 3)
        self.assertEqual([s["turn_ids"] for s in sessions],
                         [["D1:1", "D1:2", "D1:3"], ["D2:1"]])

    def test_budget_selects_whole_segments_and_stable_ties(self):
        chunks = make_segments(self.sample, "fixed", 2)
        self.assertEqual(rank("red", chunks)[:2], [0, 3])
        self.assertEqual(retrieve("red", chunks, 3), [0])
        self.assertEqual(sum(chunks[i]["word_cost"] for i in retrieve("red", chunks, 3)), 2)
        self.assertEqual(retrieve("red", make_segments(self.sample, "session", 2), 3), [1])

    def test_segmenter_ignores_nonconversation_fields(self):
        before = make_segments(self.sample, "fixed", 3)
        self.sample.update(qa=[{"question": "secret", "evidence": ["D1:1"]}],
                           event_summary="secret", observation="secret", session_summary="secret")
        self.assertEqual(before, make_segments(self.sample, "fixed", 3))


if __name__ == "__main__":
    unittest.main()
