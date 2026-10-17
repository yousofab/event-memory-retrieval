import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_phase13_provenance import methods


class ProvenanceContract(unittest.TestCase):
    def test_one_cross_session_promotion_only(self):
        turns = [{"session_position": 0, "turn_position": i} for i in range(10)] + [
            {"session_position": 1, "turn_position": i} for i in range(10)]
        order = list(range(20))
        all_orders, available = methods(order, turns, "synthetic", 20, 20)
        self.assertTrue(available)
        self.assertEqual(all_orders["best_other_session_second"][:3], [0, 10, 1])
        self.assertEqual(all_orders["newest_other_session_second"][:3], [0, 19, 1])
        for key, values in all_orders.items():
            self.assertEqual(set(values), set(order))
            self.assertEqual(values[0], 0)
            if key != "bm25_turn":
                self.assertGreaterEqual(values[1], 10)

    def test_no_other_session_means_no_change(self):
        turns = [{"session_position": 0, "turn_position": i} for i in range(20)]
        all_orders, available = methods(list(range(20)), turns, "synthetic", 20, 20)
        self.assertFalse(available)
        self.assertTrue(all(v == list(range(20)) for v in all_orders.values()))


if __name__ == "__main__":
    unittest.main()
