"""Text-only views, strict reference mapping and source-quality audit for Phase19.

Answers, options, profiles and reference text never enter the source-only view.
Published audits contain counts, identifiers and hashes, never conversation text.
"""
from collections import Counter
import hashlib
import itertools
import json
import re
from run_baselines import ROOT, sessions, words
from run_phase17_fixed_anchors import TurnIndex, digest, fingerprint
from fetch_phase19_data import fetch


def parse_indices(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('invalid_reference_range')
    result = set()
    for part in value.split(','):
        m = re.fullmatch(r'\s*([1-9]\d*)\s*(?:-\s*([1-9]\d*)\s*)?', part)
        if not m:
            raise ValueError('invalid_reference_range')
        a, b = int(m[1]), int(m[2] or m[1])
        if a > b or b > 100000:
            raise ValueError('invalid_reference_range')
        result.update(range(a, b + 1))
    return sorted(result)


def text_only(sample):
    return {'sample_id': sample['sample_id'], 'conversation': {
        key: [{'dia_id': t['dia_id'], 'text': t.get('text') or ''} for t in turns]
        for key, turns in sessions(sample)}}


def ever_sample(topic, days):
    conversation, lookup = {}, {}
    seen_dates = set()
    for day in sorted(days, key=lambda d: d['date']):
        if day['date'] in seen_dates or str(day['topic_id']) != topic:
            raise ValueError('Duplicate date or wrong topic')
        seen_dates.add(day['date'])
        for group, messages in sorted(day['dialogues'].items(),
                key=lambda item: (int(re.search(r'\d+', item[0])[0]), item[0])):
            if not messages:
                continue
            key = f'session_{len(conversation) + 1}'
            turns = []
            last = 0
            for msg in messages:
                ix = msg['message_index']
                if not isinstance(ix, int) or ix <= last:
                    raise ValueError('Source message indices are not strictly increasing')
                last = ix
                loc = (day['date'], group, ix)
                if loc in lookup:
                    raise ValueError('Duplicate source message locator')
                tid = f'E{topic}|{day["date"]}|{group}|{ix}'
                lookup[loc] = tid
                if not isinstance(msg['dialogue'], str):
                    raise ValueError('Non-string source message')
                turns.append({'dia_id': tid, 'text': msg['dialogue']})
            conversation[key] = turns
    return {'sample_id': 'evermem-' + topic, 'conversation': conversation}, lookup


def ever_queries(topic, items, lookup, index):
    counts, reasons, included, seen = Counter(), [], [], set()
    for pos, q in enumerate(items):
        qid = q['id']
        counts['source_questions'] += 1
        if qid in seen:
            raise ValueError('Duplicate source question ID')
        seen.add(qid)
        if not qid.startswith('F_'):
            counts['outside_fine_grained_scope'] += 1
            continue
        try:
            if str(q['topic_id']) != topic:
                raise ValueError('wrong_topic')
            if not isinstance(q['Q'], str) or not q['Q'].strip():
                raise ValueError('empty_query')
            refs = q.get('R')
            if not isinstance(refs, list) or not refs:
                raise ValueError('missing_reference')
            gold = set()
            for ref in refs:
                for ix in parse_indices(ref['message_index']):
                    loc = (ref['date'], ref['group'], ix)
                    if loc not in lookup:
                        raise ValueError('unresolved_reference')
                    gold.add(lookup[loc])
            empty = sum(index.by_id[t]['length'] == 0 for t in gold)
            if empty == len(gold):
                raise ValueError('all_reference_messages_empty')
        except (ValueError, KeyError, TypeError) as e:
            reason = str(e) if isinstance(e, ValueError) else 'malformed_reference'
            counts['excluded_' + reason] += 1
            reasons.append({'question_id': qid, 'source_position': pos, 'reason': reason})
            continue
        included.append((qid, q['Q'], sorted(gold)))
        counts['included_queries'] += 1
        counts['empty_reference_occurrences'] += empty
        counts['included_' + '_'.join(qid.split('_')[:2])] += 1
    return included, {'counts': dict(sorted(counts.items())), 'exclusions': reasons,
                      'included_ids': [q[0] for q in included]}


def text_hashes(sample):
    return {hashlib.sha256(' '.join(w).encode()).hexdigest()
            for _, turns in sessions(sample) for t in turns
            if len(w := words(t['text'])) >= 12}


def load_jobs(plan):
    source = ROOT / plan['data']['locomo']['path']
    if digest(source) != plan['data']['locomo']['sha256']:
        raise ValueError('LoCoMo hash differs from plan')
    manifest = json.loads((ROOT / plan['data']['locomo']['manifest']).read_text())
    jobs, hashes, audits = [], {}, {}
    for sample in json.loads(source.read_text()):
        records = [r for r in manifest['manifest']
                   if r['sample_id'] == sample['sample_id'] and r['split'] == 'held_out']
        if records:
            view = text_only(sample)
            queries = [(str(r['question_index']), sample['qa'][r['question_index']]['question'],
                        sorted(set(r['evidence_ids']))) for r in records]
            jobs.append(('locomo', view, queries))
            hashes[view['sample_id']] = text_hashes(view)
    if sum(len(q) for d, s, q in jobs) != 599:
        raise ValueError('Historical eligibility changed')
    data_dir = ROOT / plan['data']['evermem']['path']
    files = fetch(data_dir)
    for topic in plan['data']['evermem']['evaluation_topics']:
        view, lookup = ever_sample(topic, json.loads((data_dir / topic / 'dialogue.json').read_text()))
        queries, audit = ever_queries(topic, json.loads((data_dir / topic / f'qa_{topic}.json').read_text()),
                                     lookup, TurnIndex(view))
        if not queries:
            raise ValueError('No eligible external queries; stop and report')
        jobs.append(('evermem', view, queries))
        hashes[view['sample_id']] = text_hashes(view)
        audits[topic] = audit
    pairs = []
    for a, b in itertools.combinations(sorted(hashes), 2):
        common = len(hashes[a] & hashes[b])
        if common:
            pairs.append({'a': a, 'b': b, 'shared_distinct_normalized_messages_12plus_words': common,
                          'distinct_a': len(hashes[a]), 'distinct_b': len(hashes[b])})
    # Topic01 is a schema fixture only. Compare overlap without scoring it.
    schema_path = data_dir / '01/dialogue.json'
    if schema_path.exists():
        schema, _ = ever_sample('01', json.loads(schema_path.read_text()))
        h = text_hashes(schema)
        for key in sorted(hashes):
            if key.startswith('evermem'):
                pairs.append({'a': 'schema-only-evermem-01', 'b': key,
                    'shared_distinct_normalized_messages_12plus_words': len(h & hashes[key]),
                    'distinct_a': len(h), 'distinct_b': len(hashes[key])})
    audit = {'source_files': files, 'evaluation_topic_audits': audits,
             'nontrivial_exact_text_overlap': pairs,
             'overlap_scope': 'Exact normalized text with at least12 words. Shared distractors/boilerplate may couple projects. Absence of exact overlap is not proof of semantic or generative independence.',
             'histories': [{'dataset': d, 'sample_id': s['sample_id'], 'questions': len(q),
                 'sessions': len(sessions(s)), 'turns': sum(len(t) for _, t in sessions(s)),
                 'words': sum(len(words(t['text'])) for _, ts in sessions(s) for t in ts),
                 'source_view_fingerprint': fingerprint(s)} for d, s, q in jobs]}
    return jobs, audit
