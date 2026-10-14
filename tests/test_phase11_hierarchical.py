import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_phase11_hierarchical import score_partition, select, turn_index


class HierarchicalRetrievalTests(unittest.TestCase):
    def test_candidate_budget_and_output_budget_are_separate(self):
        tokenized = [["alpha"] * 4, ["beta"] * 4, ["gamma"] * 4]
        segments = [
            {"id": "a", "turn_ids": [0, 1], "tokens": tokenized[0] + tokenized[1], "word_cost": 8},
            {"id": "b", "turn_ids": [2], "tokens": tokenized[2], "word_cost": 4},
        ]
        out = score_partition("beta", {1}, segments, tokenized, budget=4, routing_multiplier=2)
        self.assertEqual(out["flat_gold"], 0)
        self.assertEqual(out["candidate_gold"], 1)
        self.assertEqual(out["hier_gold"], 1)
        self.assertEqual(out["candidate_words"], 8)
        self.assertEqual(out["hier_words"], 4)

    def test_candidate_absence_is_not_repaired_by_turn_reranking(self):
        tokenized = [["alpha"] * 5, ["beta"] * 5, ["gamma"] * 5]
        segments = [{"id": str(i), "turn_ids": [i], "tokens": ts, "word_cost": len(ts)}
                    for i, ts in enumerate(tokenized)]
        a = score_partition("alpha", {2}, segments, tokenized, budget=5, routing_multiplier=1)
        self.assertEqual((a["candidate_gold"], a["hier_gold"]), (0, 0))
        self.assertEqual(select([0, 1], turn_index(tokenized, [0, 1]), 5)[1], 5)


if __name__ == "__main__":
    unittest.main()
