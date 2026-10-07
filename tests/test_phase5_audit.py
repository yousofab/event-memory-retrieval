"""Check that diagnostic labels distinguish physical infeasibility from misses."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase5_audit import budget_transitions, choose_from_order, diagnostic, leave_one_out


class DiagnosticTests(unittest.TestCase):
    def test_structural_limit_and_feasible_miss_are_not_conflated(self):
        segments = [
            {"turn_ids": ["a"], "word_cost": 6},
            {"turn_ids": ["b"], "word_cost": 6},
            {"turn_ids": ["noise"], "word_cost": 5},
        ]
        order = [2, 0, 1]
        picked = choose_from_order(order, segments, 10)
        impossible = diagnostic({"a", "b"}, segments, order, picked, 10)
        self.assertEqual(impossible["status"], "structural_budget")
        feasible = diagnostic({"a"}, segments, order, picked, 6)
        self.assertEqual(feasible["status"], "feasible_missed")
        self.assertEqual(feasible["gold_segment_word_cost"], 6)
        self.assertEqual(diagnostic({"noise"}, segments, order, picked, 10)["status"], "success")

    def test_leave_one_out_uses_conversations_not_questions(self):
        values = {f"conv-{i}": float(i) for i in range(1, 8)}
        result = {"paired_primary": {"conversation_differences_event_minus_fixed": values}}
        means = leave_one_out(result)
        self.assertAlmostEqual(means["conv-1"], 4.5)
        self.assertAlmostEqual(means["conv-7"], 3.5)

    def test_budget_reversal_counts_each_case_once(self):
        rows = [{"sample_id": "s", "question_index": 0, "method": "fixed",
                 "budget_words": b, "all_evidence": value}
                for b, value in ((512, True), (1024, False), (2048, True))]
        output = budget_transitions({"per_question": rows})
        fixed = [row for row in output if row["method"] == "fixed"]
        self.assertEqual([row["success_to_failure"] for row in fixed], [1, 0])


if __name__ == "__main__":
    unittest.main()
