"""Tests for paired boundary study, using only synthetic conversations."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase16_boundaries import partitions, select, writer_cuts
from run_phase15_role_retrieval import BM25


class Phase16Tests(unittest.TestCase):
    def setUp(self):
        self.session = {"session_id": 3, "persona": "sample", "date": "2026-01-01",
                        "conversation": [{"speaker": "user_agent", "message": "alpha " * 40},
                                         {"speaker": "ai_agent", "message": "beta " * 40},
                                         {"speaker": "user_agent", "message": "gamma " * 40},
                                         {"speaker": "ai_agent", "message": "delta " * 40}]}

    def test_online_prefix_does_not_move_closed_cuts(self):
        first, _ = writer_cuts(self.session)
        extended = dict(self.session, conversation=self.session["conversation"] +
                        [{"speaker": "user_agent", "message": "epsilon " * 40}])
        later, _ = writer_cuts(extended)
        self.assertEqual(first[:-1], later[:len(first)-1])

    def test_matched_count_and_source_words(self):
        writer_docs, writer_ids, counts, _, _ = partitions([self.session], "writer")
        for seed in range(5):
            docs, ids, other, _, _ = partitions([self.session], f"random_{seed}")
            self.assertEqual(counts, other)
            self.assertEqual(sum(map(len, writer_docs)), sum(map(len, docs)))
            self.assertEqual(writer_ids, ids)
            self.assertEqual(len(docs), len(writer_docs))

    def test_budget_and_newest_then_earlier_tie(self):
        one = dict(self.session, session_id=1)
        docs, ids, _, _, _ = partitions([one, self.session], "writer")
        index = BM25(docs)
        ordered = index.top("missingterm", index.n)
        self.assertEqual(ids[ordered[0]], 3)
        self.assertEqual(ordered[0], len(docs)-1)
        for budget in (64, 1024):
            chosen = select(ordered, index.lengths, budget)
            self.assertLessEqual(sum(index.lengths[i] for i in chosen), budget)
        self.assertEqual(select([0, 1, 2], [0, 200, 10], 20), [2])


if __name__ == "__main__":
    unittest.main()
