"""Sampler contract tests: uniform integer weights, word cap, label isolation."""
import sys
import unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase9_controls import matched_segments, session_partition


class MatchedControlTests(unittest.TestCase):
    def test_exact_count_coverage_and_long_turn(self):
        lengths = [3, 4, 11, 2, 1]
        for seed in range(20):
            cuts = session_partition(lengths, 3, seed, "case", maximum=7)
            self.assertEqual(len(cuts), 3)
            self.assertEqual([i for a, b in cuts for i in range(a, b)], list(range(5)))
            for a, b in cuts:
                self.assertTrue(sum(lengths[a:b]) <= 7 or (b == a + 1 and lengths[a] > 7))
        self.assertEqual(session_partition(lengths, 3, 4, "case", 7),
                         session_partition(lengths, 3, 4, "case", 7))

    def test_uniform_completions_two_paths(self):
        seen = Counter(tuple(session_partition([1, 1, 1], 2, seed, "equal", 3))
                       for seed in range(200))
        self.assertEqual(set(seen), {((0, 1), (1, 3)), ((0, 2), (2, 3))})
        self.assertTrue(65 < min(seen.values()) <= max(seen.values()) < 135)

    def test_text_content_and_labels_do_not_influence_control_given_lengths(self):
        settings = {"minimum_open_words_for_novelty_boundary": 2,
                    "novelty_threshold_inclusive": 0.8, "maximum_segment_words": 5}
        a = {"sample_id": "toy", "conversation": {"session_1": [
            {"dia_id": "session_1:1", "text": "a b"},
            {"dia_id": "session_1:2", "text": "c d"},
            {"dia_id": "session_1:3", "text": "e f"}]}}
        b = {"sample_id": "toy", "conversation": {"session_1": [
            {"dia_id": "session_1:1", "text": "u v", "has_answer": True},
            {"dia_id": "session_1:2", "text": "w x"},
            {"dia_id": "session_1:3", "text": "y z"}]}, "qa": [{"answer": "u"}]}
        for seed in range(20):
            left, _ = matched_segments(a, settings, seed)
            right, _ = matched_segments(b, settings, seed)
            self.assertEqual([s["turn_ids"] for s in left], [s["turn_ids"] for s in right])


if __name__ == "__main__":
    unittest.main()
