"""Behavioral invariants for the causal writer, not success-rate tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase8_causal import OnlineWriter, online_segments


class CausalWriterTests(unittest.TestCase):
    def test_future_append_cannot_change_closed_segments(self):
        w = OnlineWriter("session_1", minimum=2, threshold=0.8, maximum=20, window=3)
        w.accept("session_1:1", "apple apple")
        w.accept("session_1:2", "banana banana")
        closed = [(tuple(s["turn_ids"]), tuple(s["tokens"])) for s in w.closed]
        self.assertEqual(closed, [(('session_1:1',), ('apple', 'apple'))])
        w.accept("session_1:3", "pear pear")
        w.accept("session_1:4", "apple pear")
        self.assertEqual([(tuple(s["turn_ids"]), tuple(s["tokens"])) for s in w.closed[:1]], closed)

    def test_prefix_replay_same_closed_chunks(self):
        turns = ["alpha beta", "gamma delta", "gamma delta", "omega sigma", "one two"]
        streaming = OnlineWriter("session_1", minimum=2, threshold=0.8, maximum=5)
        for i, t in enumerate(turns, 1):
            streaming.accept(f"session_1:{i}", t)
            replay = OnlineWriter("session_1", minimum=2, threshold=0.8, maximum=5)
            for j, earlier in enumerate(turns[:i], 1):
                replay.accept(f"session_1:{j}", earlier)
            self.assertEqual(streaming.closed, replay.closed)

    def test_oversized_turn_and_session_reset(self):
        sample = {"conversation": {"session_1": [
            {"dia_id": "session_1:1", "text": "a b c d e f"},
            {"dia_id": "session_1:2", "text": "g"}],
            "session_2": [{"dia_id": "session_2:1", "text": "h"}]}}
        settings = {"minimum_open_words_for_novelty_boundary": 2,
                    "novelty_threshold_inclusive": 0.8, "maximum_segment_words": 5}
        segments, _ = online_segments(sample, settings)
        self.assertEqual([s["turn_ids"] for s in segments],
                         [["session_1:1"], ["session_1:2"], ["session_2:1"]])
        self.assertEqual([s["word_cost"] for s in segments], [6, 1, 1])

    def test_no_label_or_question_interface(self):
        sample = {"conversation": {"session_1": [
            {"dia_id": "session_1:1", "text": "a b c", "has_answer": True},
            {"dia_id": "session_1:2", "text": "d e", "answer": "secret"}]},
            "qa": [{"question": "secret", "evidence": "session_1:1"}]}
        settings = {"minimum_open_words_for_novelty_boundary": 2,
                    "novelty_threshold_inclusive": 0.8, "maximum_segment_words": 5}
        clean = {"conversation": {"session_1": [
            {"dia_id": "session_1:1", "text": "a b c"},
            {"dia_id": "session_1:2", "text": "d e"}]}}
        self.assertEqual(online_segments(sample, settings), online_segments(clean, settings))


if __name__ == "__main__":
    unittest.main()
