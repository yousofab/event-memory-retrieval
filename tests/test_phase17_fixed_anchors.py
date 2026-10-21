import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_phase17_fixed_anchors import (TurnIndex, anchor_cells, allocate, candidate_bounds,
    choose_window, select_windows, score_windows, boundary_maps, source_family)


class FixedAnchorTests(unittest.TestCase):
    def sample(self):
        return {'sample_id':'fixture','conversation':{'session_1':[
            {'dia_id':'a','text':'red target one two three'},
            {'dia_id':'b','text':'blue target four five six'},
            {'dia_id':'c','text':'green seven eight nine ten'}]}}

    def test_disjoint_cells_and_exact_capacity_allocation(self):
        ix=TurnIndex(self.sample()); cells=anchor_cells(ix,ix.rank('target'),3)
        self.assertEqual(sum(c['right']-c['left'] for c in cells),15)
        for budget in [1,8,15,30]:
            widths=allocate(cells,budget)
            self.assertEqual(sum(widths),min(budget,15))
            selected=select_windows(cells,widths)
            positions=[(s,p) for s,a,b in selected for p in range(a,b)]
            self.assertEqual(len(positions),len(set(positions)))

    def test_no_boundary_ablation_equals_center_for_every_feasible_window(self):
        for n in range(1,16):
            for anchor in range(n):
                cell={'session':'s','left':0,'right':n,'anchor':anchor}
                for width in range(1,n+1):
                    self.assertEqual(choose_window(cell,width),choose_window(cell,width,[0,n]))

    def test_boundary_changes_context_but_not_cost_or_candidates(self):
        cell={'session':'s','left':0,'right':20,'anchor':8}
        a=choose_window(cell,6)
        b=choose_window(cell,6,[0,8,20])
        self.assertEqual(a,('s',5,11))
        self.assertEqual(b,('s',8,14))
        self.assertEqual(candidate_bounds(cell,6),(3,8))

    def test_partial_gold_turn_is_not_complete_evidence(self):
        ix=TurnIndex(self.sample())
        partial=score_windows(ix,['a'],[('session_1',0,4)])
        self.assertEqual(partial['all_evidence'],0)
        self.assertEqual(partial['gold_word_recall'],.8)
        full=score_windows(ix,['a'],[('session_1',0,2),('session_1',2,5)])
        self.assertEqual(full['all_evidence'],1)

    def test_absent_gold_session_does_not_get_inserted_by_scoring(self):
        sample=self.sample()
        sample['conversation']['session_2']=[{'dia_id':'d','text':'different session witness'}]
        ix=TurnIndex(sample)
        result=score_windows(ix,['d'],[('session_1',0,5)])
        self.assertEqual(result['all_gold_sessions'],0)
        self.assertEqual(result['all_evidence'],0)

    def test_label_changes_do_not_enter_index_or_selector(self):
        sample=self.sample(); first=TurnIndex(sample)
        sample['qa']=[{'question':'secret','answer':'secret','evidence':['c']}]
        sample['conversation']['session_1'][0]['has_answer']=True
        second=TurnIndex(sample)
        order1=first.rank('target'); order2=second.rank('target')
        self.assertEqual(order1,order2)
        c1=anchor_cells(first,order1); c2=anchor_cells(second,order2)
        self.assertEqual(c1,c2)
        self.assertEqual(select_windows(c1,allocate(c1,10)),select_windows(c2,allocate(c2,10)))

    def test_positive_and_negative_synthetic_mechanism(self):
        # The same movement helps a right-side gold turn and hurts a left-side one.
        sample={'sample_id':'mechanism','conversation':{'session_1':[
            {'dia_id':'left','text':'a b c d e f g h'},
            {'dia_id':'right','text':'i j k l m n'},
            {'dia_id':'tail','text':'o p q r s t'}]}}
        ix=TurnIndex(sample)
        cell={'session':'session_1','left':0,'right':20,'anchor':8}
        center=choose_window(cell,6); moved=choose_window(cell,6,[0,8,20])
        self.assertGreater(score_windows(ix,['right'],[moved])['all_evidence'],score_windows(ix,['right'],[center])['all_evidence'])
        self.assertLess(score_windows(ix,['left'],[moved])['gold_word_recall'],score_windows(ix,['left'],[center])['gold_word_recall'])

    def test_cluster_family_respects_repeated_meetings(self):
        self.assertEqual(source_family('ES2004a'),source_family('ES2004d'))
        self.assertEqual(source_family('Bmr006'),source_family('Bmr023'))
        self.assertEqual(source_family('education_4'),source_family('education_17'))

    def test_frozen_writer_and_control_counts(self):
        import json
        root=Path(__file__).resolve().parents[1]
        settings=json.loads((root/'configs/phase8_causal_plan.json').read_text())['causal_writer']
        maps,stats=boundary_maps(self.sample(),settings)
        self.assertEqual(stats['writer_segments'],stats['random_segments_each'])
        self.assertTrue(all(m['session_1']==[0,15] for m in maps.values()))


if __name__=='__main__':unittest.main()
