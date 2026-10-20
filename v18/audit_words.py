import sys
sys.path.insert(0,'v9')
"""Check lexical order, onsets, frame coverage and P(doom) impact ownership."""
import json
import math
from pathlib import Path
from word_score import token_state, norm
from impact_score_v9 import sample_impact, IMPACTS, PDOOM_LYRIC_INDICES

score = json.loads(Path('v18/word_timeline.json').read_text())
lines = json.loads(Path('work/lyrics.json').read_text())
actual = [norm(t['text']) for row in score for t in row]
expected = [norm(w) for row in lines for w in row[3].replace('|', ' ').split()]
assert actual == expected, 'Canonical lyric order changed'
counts = {}; complete = {}; maximum = 0
for frame in range(math.ceil(141.2 * 30)):
    t = frame / 30
    active = []
    for i, row in enumerate(score):
        for j, token in enumerate(row):
            state = token_state(t, token)
            if state['visible']:
                assert t >= token['start'], 'Word appears early'
                active.append((i, j))
                counts[i, j] = counts.get((i, j), 0) + 1
                if state['reveal'] >= .99:
                    complete[i, j] = complete.get((i, j), 0) + 1
    maximum = max(maximum, len(active))
    assert len(active) <= 2, 'Too many words at once'
missed = [(i, token['text']) for i, row in enumerate(score) for j, token in enumerate(row) if not counts.get((i, j))]
never_complete = [(i, token['text']) for i, row in enumerate(score) for j, token in enumerate(row) if not complete.get((i, j))]
assert not missed, missed
assert not never_complete, never_complete
events = []
for event in IMPACTS:
    if event.name not in PDOOM_LYRIC_INDICES:
        continue
    i = PDOOM_LYRIC_INDICES[event.name]
    token = next(t for t in score[i] if norm(t['text']) == 'pdoom')
    assert token['start'] <= event.time < token['end']
    events.append({'name': event.name, 'word_start': token['start'], 'word_end': token['end'], 'explosion': event.time})
assert len(events) == 4
assert not sample_impact(25.685)['events']
assert not sample_impact(62.060)['events']
report = {'total_tokens': len(actual), 'canonical_order': True, 'max_simultaneous': maximum,
          'missed_at_30fps': missed, 'never_fully_traced_at_30fps': never_complete,
          'no_early_words': True, 'pdoom_explosions': events, 'old_boom_blasts_removed': True}
Path('v18/token_validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
