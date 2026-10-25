import copy
from collections import Counter
import itertools
import random
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from phase19_data import parse_indices, ever_sample, ever_queries, text_only
from run_phase17_fixed_anchors import TurnIndex
from run_phase19_session_access import select_anchors, group_labels, practical_retrieve, writer_maps
from validate_phase19 import direct_score


def pool_of(labels):
    return [{'turn_index':i,'session':s} for i,s in enumerate(labels)]


class SessionAccessTests(unittest.TestCase):
    def test_reservation_guarantee_on_random_pools(self):
        rng=random.Random(19)
        for _ in range(300):
            labels=[f's{rng.randrange(rng.randint(1,14))}' for _ in range(64)]
            pool=pool_of(labels)
            for policy,r in [('reserve4',4),('reserve8',8)]:
                chosen=select_anchors(pool,policy,'fixture|0')
                self.assertEqual(len(chosen),8)
                self.assertEqual(chosen,sorted(set(chosen)))
                self.assertIn(0,chosen)
                self.assertGreaterEqual(len({labels[i] for i in chosen}),min(r,len(set(labels))))
                self.assertLessEqual(len(set(chosen)-set(range(8))),r-1)

    def test_renaming_and_single_session_invariance(self):
        labels=['a']*20+['b']*20+['c']*24
        a=pool_of(labels);b=pool_of([{'a':'z','b':'q','c':'m'}[s] for s in labels])
        for policy in ['bm25','reserve4','reserve8','sham_19']:
            self.assertEqual(select_anchors(a,policy,'x'),select_anchors(b,policy,'x'))
            self.assertEqual(select_anchors(pool_of(['one']*64),policy,'x'),list(range(8)))

    def test_sham_histogram_and_identity_replay(self):
        p=pool_of(['a']*29+['b']*25+['c']*10)
        for seed in range(19,24):
            policy=f'sham_{seed}'
            a=group_labels(p,policy,'h|q')
            self.assertEqual(Counter(a),Counter(x['session'] for x in p))
            self.assertEqual(a,group_labels(p,policy,'h|q'))
        self.assertNotEqual(group_labels(p,'sham_19','h|q'),[x['session'] for x in p])

    def test_strict_reference_parser(self):
        self.assertEqual(parse_indices('1, 4-6, 6, 10-11'),[1,4,5,6,10,11])
        for invalid in ['',None,[], '0','3-1','1;2','1-2-3','1,','1.0','1,-2']:
            with self.assertRaises(ValueError):parse_indices(invalid)

    def test_source_indices_not_array_offsets_and_deduplicated_refs(self):
        days=[{'topic_id':'02','date':'2025-01-01','dialogues':{'Group 1':[
            {'message_index':2,'dialogue':'alpha beta'}, {'message_index':5,'dialogue':'gamma delta'}]}}]
        sample,lookup=ever_sample('02',days)
        ref={'date':'2025-01-01','group':'Group 1','message_index':'5'}
        qa=[{'id':'F_SH_x','topic_id':'02','Q':'gamma?','R':[ref,ref],'A':'poison'}]
        queries,audit=ever_queries('02',qa,lookup,TurnIndex(sample))
        self.assertEqual(len(queries[0][2]),1)
        qa[0]['R'][0]={**ref,'message_index':'1'}
        qa[0]['R']=qa[0]['R'][:1]
        queries,audit=ever_queries('02',qa,lookup,TurnIndex(sample))
        self.assertFalse(queries)
        self.assertEqual(audit['exclusions'][0]['reason'],'unresolved_reference')

    def test_duplicate_source_indices_fail(self):
        day={'topic_id':'02','date':'x','dialogues':{'Group 1':[
            {'message_index':1,'dialogue':'a'},{'message_index':1,'dialogue':'b'}]}}
        with self.assertRaises(ValueError):ever_sample('02',[day])

    def test_independent_scorer_cross_cell_union_and_overlap_rejection(self):
        gold=[{'session':'s','start':1,'end':5}]
        score=direct_score(gold,[('s',0,3),('s',3,5)])
        self.assertEqual(score['all_evidence'],1)
        self.assertEqual(direct_score(gold,[('s',0,3)])['gold_word_recall'],.5)
        self.assertEqual(direct_score(gold,[('other',0,3)])['all_gold_sessions'],0)
        with self.assertRaises(ValueError):direct_score(gold,[('s',0,3),('s',2,5)])

    def test_poison_fields_never_enter_retriever(self):
        sample={'sample_id':'fixture','conversation':{
            f'session_{s}':[{'dia_id':f'{s}:{i}','text':'alpha beta gamma '+str(i)} for i in range(25)]
            for s in range(1,5)},'qa':[{'question':'poison','answer':'secret','evidence':['bad']}],
            'event_summary':'poison','profiles':'poison'}
        other=copy.deepcopy(sample)
        other['qa']=[{'question':'different','answer':'irrelevant','evidence':['other']}]
        other['event_summary']='other';other['profiles']='other'
        a,b=text_only(sample),text_only(other)
        self.assertEqual(a,b)
        settings={'minimum_open_words_for_novelty_boundary':4,'novelty_threshold_inclusive':.85,'maximum_segment_words':16}
        plan={'candidate_pool_turns':64,'anchor_count':8,'policies':['bm25','reserve4','sham_19'],'budget_words':[32,64]}
        ma,_=writer_maps(a,settings);mb,_=writer_maps(b,settings)
        self.assertEqual(practical_retrieve(TurnIndex(a),'alpha',ma,plan,'f|1'),
                         practical_retrieve(TurnIndex(b),'alpha',mb,plan,'f|1'))


if __name__=='__main__':unittest.main()
