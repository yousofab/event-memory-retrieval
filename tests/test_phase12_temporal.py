import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase12_temporal import methods, pick, public_turns, score_record


class TemporalProtocol(unittest.TestCase):
    def test_gold_and_answer_not_enter_public_index(self):
        row = {"haystack_sessions": [[{"content": "same", "has_answer": True}],
                                      [{"content": "new", "has_answer": True}]],
               "answer": "private", "answer_session_ids": ["a", "b"]}
        assert public_turns(row) == [
            {"id": "0:0", "session_position": 0, "turn_position": 0,
             "turn_ids": ["0:0"], "word_cost": 1, "tokens": ["same"]},
            {"id": "1:0", "session_position": 1, "turn_position": 0,
             "turn_ids": ["1:0"], "word_cost": 1, "tokens": ["new"]}]

    def test_recency_uses_same_candidates_and_budget(self):
        turns = [{"id": str(i), "session_position": i, "turn_position": 0,
                  "word_cost": 4} for i in range(22)]
        orders = methods(list(range(22)), turns, "q", 20, 20)
        assert orders["recent_within_top20"][0] == 19
        for order in orders.values():
            assert set(order[:20]) == set(range(20))
            assert order[20:] == [20, 21]
            chosen, spent = pick(order, turns, 9)
            assert len(chosen) == 2 and spent == 8

    def test_old_only_is_not_latest(self):
        row = {"question_id": "q", "haystack_dates": ["2023/01/01", "2023/01/02"],
               "haystack_session_ids": ["a", "b"], "answer_session_ids": ["a", "b"],
               "haystack_sessions": [[{"content": "old", "has_answer": True}],
                                      [{"content": "new", "has_answer": True}]]}
        assert score_record(row, {"0:0"}, 1, 10)["older_only"] is True
        assert score_record(row, {"1:0"}, 1, 10)["later_found"] is True


if __name__ == "__main__":
    unittest.main()
