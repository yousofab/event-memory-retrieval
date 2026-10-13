import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_phase10_data import git_blob_sha
from run_phase10_topic_transfer import (UniformCountSampler, boundaries,
                                        check_partition, chunks_from_cuts,
                                        onset_coverage, query_turns, sample_for)


class TopicTransferTests(unittest.TestCase):
    def test_uniform_partitions_are_valid_and_seeded(self):
        sampler = UniformCountSampler([40, 40, 40], 2, maximum=160)
        cuts = [sampler.draw(seed, "meeting") for seed in range(200)]
        options = {tuple(x) for x in cuts}
        self.assertEqual(options, {((0, 1), (1, 3)), ((0, 2), (2, 3))})
        self.assertTrue(70 < cuts.count([(0, 1), (1, 3)]) < 130)
        self.assertEqual(sampler.draw(17, "meeting"), sampler.draw(17, "meeting"))
        parts = chunks_from_cuts([["a"] * 40] * 3, cuts[0])
        check_partition(parts, 3, 160)

    def test_full_long_turn_and_inclusive_labels(self):
        sampler = UniformCountSampler([30, 190, 20], 3, maximum=160)
        for seed in range(10):
            parts = chunks_from_cuts([["x"] * 30, ["y"] * 190, ["z"] * 20],
                                     sampler.draw(seed, "long"))
            check_partition(parts, 3, 160)
            self.assertEqual(len(parts), 3)
        self.assertEqual(query_turns({"relevant_text_span": [["1", "2"], ["4", "4"]]}, 5),
                         {1, 2, 4})
        self.assertEqual(onset_coverage([2, 5], {3}, 1), 0.5)
        self.assertEqual(onset_coverage([2, 5], {3}, 0), 0.0)

    def test_public_sample_drops_annotation_fields(self):
        a = {"meeting_transcripts": [{"speaker": "A", "content": "alpha beta"}],
             "topic_list": [{"topic": "secret", "relevant_text_span": [["0", "0"]]}],
             "specific_query_list": [{"query": "secret", "relevant_text_span": [["0", "0"]]}]}
        sample = sample_for("test", a)
        self.assertEqual(sample["conversation"]["session_1"],
                         [{"dia_id": 0, "text": "alpha beta"}])
        self.assertNotIn("secret", repr(sample))
        self.assertEqual(git_blob_sha(b"hi"), "32f95c0d1244a78b2be1bab8de17906fabb2c4a8")


if __name__ == "__main__":
    unittest.main()
