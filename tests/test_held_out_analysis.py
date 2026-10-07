"""Synthetic tests for summaries; never open held-out dataset here."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_held_out import aggregate, sign_flip_paired_two_sided


class AnalysisTests(unittest.TestCase):
    def test_conversation_rates_keep_denominator(self):
        rows = [{"method": "event", "budget_words": 1024, "sample_id": "a",
                 "all_evidence": success, "retrieved_words": 100, "retrieved_segments": 2}
                for success in (True, False, True)]
        out = aggregate(rows)
        self.assertEqual((out[0]["questions"], out[0]["all_evidence_count"]), (3, 2))
        self.assertAlmostEqual(out[0]["all_evidence_rate"], 2/3)

    def test_exact_sign_flip_is_two_sided_and_includes_zeros(self):
        self.assertEqual(sign_flip_paired_two_sided([1, 2]), 0.5)
        self.assertEqual(sign_flip_paired_two_sided([0, 0, 0]), 1.0)


if __name__ == "__main__":
    unittest.main()
