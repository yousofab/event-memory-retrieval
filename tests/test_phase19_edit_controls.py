from fractions import Fraction
import itertools
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_phase19_edit_controls import access_null,matched_edit_anchors
from run_phase19_session_access import select_anchors


class EditControlTests(unittest.TestCase):
    def test_exact_expectation_against_every_small_label_geometry(self):
        # Enumerate all64 binary session assignments, all permitted edits and
        # all actual subsets in a six-candidate/three-anchor analogue.
        for labels in itertools.product(['a','b'],repeat=6):
            pool=[{'turn_index':i,'session':s} for i,s in enumerate(labels)]
            for gold in [{'a'},{'b'},{'a','b'},{'absent'}]:
                for d in [0,1,2]:
                    scores=[];recalls=[]
                    for kept in itertools.combinations(range(1,3),2-d):
                        for added in itertools.combinations(range(3,6),d):
                            found={labels[i] for i in [0,*kept,*added]}
                            scores.append(int(gold<=found));recalls.append(Fraction(len(gold&found),len(gold)))
                    expected=access_null(pool,gold,d,count=3)
                    self.assertEqual(Fraction(*expected['all_sessions_fraction']),Fraction(sum(scores),len(scores)))
                    self.assertEqual(Fraction(*expected['mean_session_recall_fraction']),sum(recalls)/len(recalls))

    def test_exact_edit_count_top_rank_order_and_replay(self):
        for session_count in range(1,15):
            pool=[{'turn_index':i,'session':f's{i//max(1,64//session_count)}'} for i in range(64)]
            target=select_anchors(pool,'reserve8','h|q')
            d=len(set(target)-set(range(8)))
            for seed in range(100,110):
                selected=matched_edit_anchors(pool,f'edit_{seed}','h|q')
                self.assertEqual(len(selected),8)
                self.assertEqual(selected,sorted(set(selected)))
                self.assertIn(0,selected)
                self.assertEqual(len(set(selected)-set(range(8))),d)
                self.assertEqual(selected,matched_edit_anchors(pool,f'edit_{seed}','h|q'))

    def test_more_gold_sessions_than_anchors_impossible(self):
        pool=[{'turn_index':i,'session':str(i)} for i in range(64)]
        self.assertEqual(access_null(pool,{str(i) for i in range(9)},2)['all_sessions_probability'],0)


if __name__=='__main__':unittest.main()
