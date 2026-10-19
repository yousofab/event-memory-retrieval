import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase15_role_retrieval import BM25, age_bin, documents, score_question
from run_phase15_budget import select


class Phase15Tests(unittest.TestCase):
    def test_role_intervention_recovers_original_user_line(self):
        sessions = [{"session_id": 1, "date": "2025-01-01", "conversation": [
            {"speaker": "user_agent", "message": "lavender memory"},
            {"speaker": "ai_agent", "message": "okay"}]},
            {"session_id": 2, "date": "2025-01-01", "conversation": [
                {"speaker": "user_agent", "message": "nothing"},
                {"speaker": "ai_agent", "message": "okay"}]}]
        docs = documents(sessions)
        self.assertEqual(docs["assistant_only"][0], ["okay"])
        self.assertIn("lavender", docs["role_corrected"][0])
        self.assertEqual(BM25(docs["assistant_only"]).top("lavender", 1), [1])  # zero tie: newest
        self.assertEqual(BM25(docs["role_corrected"]).top("lavender", 1), [0])
        with tempfile.TemporaryDirectory() as temp:
            group = Path(temp) / "weekly" / "p"
            q = {"question_id": "q", "question": "lavender", "question_date": "2025-01-01",
                 "memory_evidence": {"items": [{"session_id": 1}]}, "forgetting_evidence": {}}
            rows = score_question(q, "remembering", group, sessions,
                                  {m: BM25(x) for m, x in docs.items()}, docs)
            at_one = {r["method"]: r for r in rows if r["k"] == 1}
            self.assertEqual(at_one["assistant_only"]["active_any"], 0)
            self.assertEqual(at_one["role_corrected"]["active_any"], 1)
            self.assertIsNone(at_one["role_corrected"]["obsolete_any"])

    def test_age_categories_and_missing_question_date(self):
        self.assertEqual([age_bin(v) for v in (0.10, 0.11, 0.50, 0.51)],
                         ["<=0.10", "(0.10,0.50]", "(0.10,0.50]", ">0.50"])
        sessions = [{"session_id": 1, "date": "2025-01-02", "conversation": []}]
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                score_question({"question_id": "q", "question": "x", "question_date": "2025-01-01",
                                "memory_evidence": {"x": [{"session_id": 1}]}}, "reasoning",
                               Path(temp) / "weekly" / "p", sessions,
                               {m: BM25([[]]) for m in ("assistant_only", "role_corrected", "user_only")},
                               {m: [[]] for m in ("assistant_only", "role_corrected", "user_only")})

    def test_budget_skips_oversized_and_empty_sessions(self):
        chosen, used = select([0, 1, 2, 3], [0, 1100, 700, 300], 1000)
        self.assertEqual(chosen, [2, 3])
        self.assertEqual(used, 1000)


if __name__ == "__main__":
    unittest.main()
