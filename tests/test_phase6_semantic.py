"""Controlled semantic boundaries, label isolation and retrieval compatibility."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_baselines import rank, retrieve
from run_phase6_semantic import (evidence_diagnostics, select_ranked, semantic_segments,
                                 training_texts, window_distance)


class IdentityVectorizer:
    def transform(self, texts):
        return texts


class DeliberateEncoder:
    def transform(self, texts):
        return np.array([[1.0, 0.0] if "garden" in text else [0.0, 1.0]
                         for text in texts])


class SemanticTests(unittest.TestCase):
    def setUp(self):
        self.sample = {"conversation": {"session_1": [
            {"dia_id": "D1:1", "text": "garden plant green"},
            {"dia_id": "D1:2", "text": "garden seed soil"},
            {"dia_id": "D1:3", "text": "travel flight train"},
            {"dia_id": "D1:4", "text": "travel ticket trip"}],
            "session_2": [{"dia_id": "D2:1", "text": "garden plant"}]}}

    def test_deliberate_boundary_and_label_isolation(self):
        a = semantic_segments(self.sample, IdentityVectorizer(), DeliberateEncoder(),
                              minimum=3, preferred=6, maximum=9, window=1)
        self.assertEqual([s["turn_ids"] for s in a],
                         [["D1:1", "D1:2"], ["D1:3", "D1:4"], ["D2:1"]])
        self.sample.update(qa=[{"question": "garden", "answer": "secret", "evidence": ["D1:4"]}],
                           event_summary="garden", observation="garden", session_summary="garden")
        b = semantic_segments(self.sample, IdentityVectorizer(), DeliberateEncoder(), 3, 6, 9, 1)
        self.assertEqual(a, b)
        texts = training_texts({"conv-26": self.sample}, ["conv-26"])
        self.assertEqual(texts, ["garden plant green", "garden seed soil", "travel flight train",
                                 "travel ticket trip", "garden plant"])

    def test_oversized_single_turn_and_structural_cost(self):
        self.sample["conversation"]["session_2"] = [
            {"dia_id": "D2:1", "text": "garden plant leaf root stem seed soil water flower"}]
        segments = semantic_segments(self.sample, IdentityVectorizer(), DeliberateEncoder(), 3, 6, 8, 1)
        self.assertEqual([s["turn_ids"] for s in segments][-1], ["D2:1"])
        self.assertEqual(segments[-1]["word_cost"], 9)
        self.assertEqual(evidence_diagnostics(segments, {"D2:1"}, 8),
                         {"gold_segment_word_cost": 9, "gold_segment_count": 1,
                          "structural_budget": True})

    def test_rank_once_select_matches_frozen_retriever(self):
        segments = semantic_segments(self.sample, IdentityVectorizer(), DeliberateEncoder(), 3, 6, 9, 1)
        for query in ("garden", "travel", "unknown", "garden travel"):
            ordered = rank(query, segments)
            for budget in (2, 5, 6, 10, 15):
                self.assertEqual(select_ranked(ordered, segments, budget), retrieve(query, segments, budget))

    def test_silent_window_and_orthogonal_change(self):
        self.assertEqual(window_distance(np.zeros((1, 2)), np.ones((1, 2))), 0)
        self.assertAlmostEqual(window_distance(np.array([[1, 0]]), np.array([[0, 1]])), 1)


if __name__ == "__main__":
    unittest.main()
