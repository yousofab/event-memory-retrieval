"""Independent tiny-space enumeration checks the exact diagnostic, not its text."""
import itertools
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from run_phase17_fixed_anchors import allocate
from run_phase18_feasibility import (requirements, minimum_budget, feasible,
                                    witness_windows, classify)


def brute_windows(cells, widths, gold):
    # Independent word-set enumerator: no candidate_bounds or feasibility formula.
    choices = []
    for c, w in zip(cells, widths):
        choices.append([(c['session'], a, a + w) for a in range(c['left'], c['right'] - w + 1)
                        if w > 0 and a <= c['anchor'] < a + w] if w else [None])
    wanted = {(t['session'], p) for t in gold for p in range(t['start'], t['end'])}
    for selection in itertools.product(*choices):
        seen = {(s, p) for win in selection if win is not None
                for s, a, b in [win] for p in range(a, b)}
        if wanted <= seen:
            return True
    return False


class ExactFeasibilityTests(unittest.TestCase):
    def test_exhaustive_independent_geometry_and_thresholds(self):
        rng = random.Random(18)
        for trial in range(240):
            capacities = [rng.randint(1, 5) for _ in range(rng.randint(1, 3))]
            cells, pos = [], 0
            for rank, cap in enumerate(capacities):
                cells.append({'session': 's', 'left': pos, 'right': pos + cap,
                              'anchor': pos + rng.randrange(cap), 'rank': rank})
                pos += cap
            a = rng.randrange(pos)
            gold = [{'session': 's', 'start': a, 'end': rng.randint(a + 1, pos)}]
            if trial % 5 == 0:
                b = rng.randrange(pos)
                gold.append({'session': 's', 'start': b, 'end': b + 1})
            req, missing = requirements(cells, gold)
            first = None
            for budget in range(1, pos + 1):
                widths = allocate(cells, budget)
                exact = brute_windows(cells, widths, gold)
                # The contract always retains one nonempty window per cell;
                # production budgets are >=8. Test below that threshold too.
                expected = exact and all(widths)
                self.assertEqual(feasible(req, widths, missing), bool(expected))
                if expected and first is None:
                    first = budget
                witness = witness_windows(req, widths, missing)
                if witness is not None:
                    wanted = {(t['session'], p) for t in gold for p in range(t['start'], t['end'])}
                    seen = {(s, p) for s, a, b in witness for p in range(a, b)}
                    self.assertTrue(wanted <= seen)
                    self.assertEqual([b - a for s, a, b in witness], widths)
            self.assertEqual(minimum_budget(req), first)

    def test_missing_session_is_impossible_at_full_capacity(self):
        cells = [{'session': 'a', 'left': 0, 'right': 10, 'anchor': 5, 'rank': 0}]
        req, missing = requirements(cells, [{'session': 'b', 'start': 1, 'end': 3}])
        self.assertEqual(missing, ['b'])
        self.assertFalse(feasible(req, [10], missing))
        self.assertIsNone(witness_windows(req, [10], missing))

    def test_cross_cell_turn_requires_both_sides_and_no_gap(self):
        cells = [{'session': 's', 'left': 0, 'right': 5, 'anchor': 2, 'rank': 0},
                 {'session': 's', 'left': 5, 'right': 10, 'anchor': 8, 'rank': 1}]
        req, missing = requirements(cells, [{'session': 's', 'start': 4, 'end': 7}])
        self.assertEqual([c['required_width'] for c in req], [3, 4])
        self.assertFalse(feasible(req, [3, 3]))
        self.assertTrue(feasible(req, [3, 4]))
        self.assertTrue(brute_windows(cells, [3, 4], [{'session': 's', 'start': 4, 'end': 7}]))

    def test_saturation_and_rank_order_affect_minimum_budget(self):
        cells = [{'session': 'a', 'left': 0, 'right': 1, 'anchor': 0, 'rank': 0},
                 {'session': 'b', 'left': 0, 'right': 7, 'anchor': 0, 'rank': 1}]
        req, _ = requirements(cells, [{'session': 'b', 'start': 0, 'end': 5}])
        self.assertEqual(minimum_budget(req), 6)
        self.assertEqual(allocate(cells, 6), [1, 5])

    def test_empty_annotation_policy_and_invalid_query(self):
        cells = [{'session': 'a', 'left': 0, 'right': 4, 'anchor': 0, 'rank': 0}]
        req, missing = requirements(cells, [{'session': 'b', 'start': 0, 'end': 0},
                                          {'session': 'a', 'start': 0, 'end': 2}])
        self.assertFalse(missing)
        self.assertEqual(req[0]['required_width'], 2)
        with self.assertRaises(ValueError):
            requirements(cells, [{'session': 'b', 'start': 0, 'end': 0}])

    def test_success_cannot_exceed_bound_and_categories_are_exclusive(self):
        self.assertEqual(classify(1, 1, []), 'complete_success')
        self.assertEqual(classify(0, 0, ['x']), 'missing_gold_session')
        self.assertEqual(classify(0, 0, []), 'window_geometry_infeasible')
        self.assertEqual(classify(0, 1, []), 'feasible_selection_miss')
        with self.assertRaises(AssertionError):
            classify(1, 0, [])

    def test_labels_alter_only_offline_requirements(self):
        cells = [{'session': 's', 'left': 0, 'right': 10, 'anchor': 5, 'rank': 0}]
        frozen = [dict(c) for c in cells]
        r1, _ = requirements(cells, [{'session': 's', 'start': 5, 'end': 6}])
        r2, _ = requirements(cells, [{'session': 's', 'start': 0, 'end': 10}])
        self.assertEqual(cells, frozen)
        self.assertNotEqual(r1[0]['required_width'], r2[0]['required_width'])


if __name__ == '__main__':
    unittest.main()
