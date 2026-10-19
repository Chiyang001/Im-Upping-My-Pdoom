"""V9 sung-token choreography, independent of the renderer and GPU.

``plan_tokens(words, a, b, transcript)`` returns one item per existing glyph GPU.
The indices remain identical to ``words``.  A group has at most two words, but
each word still enters at its own sung onset.  No future word is ever visible.
``token_state(t, token)`` supplies the entry/hold/exit envelopes and a local
motion cue; the renderer applies that cue inside its existing 3D word matrix.

The supplied transcript has several split words and phonetic mistranscriptions.
The indexed spans below merge those ASR pieces without inventing uniform lyric
timing.  Untouched words retain both measured onset and measured end.
"""

import difflib
import math
import re


LINE_STARTS = (
    1.42, 5.58, 9.08, 12.94, 16.2, 22.2, 26.06, 29.68, 31.78,
    38.12, 41.16, 44.72, 48.64, 52.56, 58.4, 62.34, 65.94,
    68.2, 73.96, 77.34, 80.68, 84.72, 89.86, 94.86, 98.7,
    102.32, 104.54, 109.4, 115.0, 118.7, 124.04, 127.9,
    131.46, 136.9,
)

# Each tuple is an inclusive ASR-word span for the corresponding canonical
# lyric token.  This also repairs the timing of words whose spellings differ.
_ASR_SPANS = {
    5: ((0, 0), (1, 2), (3, 3), (4, 5), (6, 6), (7, 7),
        (8, 8), (9, 9), (10, 10)),
    6: tuple((i, i) for i in range(10)),
    7: tuple((i, i) for i in range(5)),
    11: ((0, 0), (1, 1), (2, 2), (4, 4)),
    14: ((0, 0), (1, 2), (3, 3), (4, 5), (6, 6), (7, 7),
         (8, 8), (9, 9), (10, 10)),
    15: ((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
         (6, 6), (7, 8), (9, 9)),
    16: ((0, 1), (2, 2), (3, 3), (4, 4)),
    23: ((0, 0), (1, 2), (3, 3), (4, 5), (6, 6), (7, 7),
         (8, 8), (9, 9), (10, 10)),
    24: ((0, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6),
         (7, 7), (8, 8), (9, 9), (10, 10)),
    25: tuple((i, i) for i in range(7)),
    26: ((0, 2), (3, 3), (4, 4)),
    27: ((0, 0), (1, 2), (3, 3), (4, 4), (5, 5), (6, 6),
         (7, 7), (8, 8), (9, 9), (10, 10)),
    28: ((0, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
         (8, 8)),
    29: tuple((i, i) for i in range(6)),
    30: ((0, 0), (1, 2), (3, 3), (4, 5), (6, 6), (7, 7),
         (8, 9), (10, 10), (11, 11)),
    31: ((0, 0), (1, 1), (2, 3), (4, 4), (5, 5), (6, 6),
         (7, 8)),
    32: ((0, 0), (1, 1), (2, 3), (4, 4), (5, 5), (6, 6),
         (7, 7)),
}

_FUNCTION = {
    'i', 'im', 'your', 'you', 'youre', 'my', 'in', 'of', 'the', 'a',
    'an', 'was', 'is', 'are', 'and', 'but', 'now', 'there', 'thats',
    'with', 'to', 'on', 'as', 'by', 'from', 'it', 'all', 'for', 'we',
    'well', 'did', 'just', 'til', 'cause', 'dont', 'please', 'me', 'let',
}
_COMPOUNDS = {
    ('chinese', 'room'), ('training', 'loss'), ('training', 'run'),
    ('shinigami', 'eyes'), ('omega', 'points'), ('left', 'turn'),
    ('safe', 'enough'), ('hundred', 'thousand'), ('safety', 'fence'),
    ('von', 'neumanns'), ('pretraining', 'days'), ('coming', 'soon'),
}
_SOLO = {
    'pdoom', 'foom', 'boom', '1e30', 'agi', 'chatgpt', 'sydney',
    'gato', 'nervous', 'drop', 'boss', 'singularitys', 'optimizing',
    'accelerating', 'atoms', 'rearranging', 'basilisk', 'nvda', 'mlp',
    'obsolete', 'cdr', 'paperclips', 'killswitch', 'pto', 'nowhere',
    'fuse', 'orthogonality', 'blues', 'transformers', 'disobey',
    'postchinchilla', 'superdense', 'gpu', 'rlhf', 'askew', 'loom',
    'recursive', 'selfupgrade', 'ilya', 'show',
}


def norm(word):
    return re.sub('[^a-z0-9]', '', str(word).lower())


def _clamp(x, lo=0.0, hi=1.0):
    return min(hi, max(lo, x))


def _ease(x):
    x = _clamp(x)
    return x * x * (3.0 - 2.0 * x)


def align_tokens(words, a, b, transcript, line_index=None):
    """Return measured ``(start, end)`` pairs in canonical glyph order.

    ``transcript`` can be the original list of segments or a flat word list.
    The end-boundary epsilon is deliberate: float noise used to pull the next
    line's first word into the previous line's alignment candidate list.
    """
    words = [str(w) for w in words]
    if line_index is None:
        candidate = min(range(len(LINE_STARTS)), key=lambda i: abs(a - LINE_STARTS[i]))
        line_index = candidate if abs(a - LINE_STARTS[candidate]) < 0.08 else -1
    flat = []
    for item in transcript:
        flat.extend(item['words'] if 'words' in item else [item])
    raw = [w for w in flat if a - .001 <= float(w['start']) < b - .0001]
    spans = _ASR_SPANS.get(line_index)
    if spans is not None and len(spans) == len(words) and raw and max(s[1] for s in spans) < len(raw):
        times = [(float(raw[lo]['start']), float(raw[hi]['end'])) for lo, hi in spans]
        # Whisper segmented the held final /z/ of BLUES as a separate "us".
        if line_index == 26:
            times[-1] = (times[-1][0], min(b, float(raw[-1]['end'])))
    else:
        matches = {}
        sm = difflib.SequenceMatcher(None, [norm(w) for w in words],
                                     [norm(w['word']) for w in raw], autojunk=False)
        for block in sm.get_matching_blocks():
            for k in range(block.size):
                rw = raw[block.b + k]
                matches[block.a + k] = (float(rw['start']), float(rw['end']))
        # Allocate each unmatched run once, using surrounding measured anchors.
        # Do not let newly invented timestamps become anchors for later words.
        times = [matches.get(i) for i in range(len(words))]
        j = 0
        while j < len(words):
            if times[j] is not None:
                j += 1
                continue
            end = j + 1
            while end < len(words) and times[end] is None:
                end += 1
            lo = times[j - 1][1] if j else a
            hi = times[end][0] if end < len(words) else b
            step = max(.045, hi - lo) / (end - j)
            for k in range(j, end):
                times[k] = (lo + (k - j) * step, lo + (k - j + 1) * step)
            j = end
    result = []
    previous = a
    for start, end in times:
        start = max(a, previous, start)
        end = max(start + .025, min(b, end))
        result.append((round(start, 6), round(end, 6)))
        previous = start
    return result


def _drive(word):
    """Semantic apparatus cue; it changes with the sung word, never in advance."""
    w = norm(word)
    if w == 'pdoom':
        return 'detonate'
    if w in {'foom', 'boom', 'nvda', 'moon', 'accelerating', '1e30'}:
        return 'expand'
    if w in {'nervous', 'servant', 'boss', 'chatgpt', 'eat', 'alive', 'trapped',
             'singularitys', 'sydney', 'free', 'gato', 'dont', 'killswitch',
             'pto', 'nowhere', 'fence'}:
        return 'clamp'
    if w in {'drop', 'loss', 'obsolete', 'left', 'turn', 'disobey', 'askew'}:
        return 'shear'
    if w in {'atoms', 'rearranging', 'paperclips', 'fuse', 'breaking', 'gpu', 'rlhf'}:
        return 'fracture'
    if w in {'loom', 'pretraining', 'recursive', 'selfupgrade', 'foretold'}:
        return 'weave'
    if w in {'eyes', 'shinigami', 'see', 'ilya', 'know', 'show'}:
        return 'observe'
    return 'trace'


def plan_tokens(words, a, b, transcript=None, starts=None, ends=None, line_index=None):
    """Score existing independent word meshes; return one dictionary per word.

    Supply the transcript for the corrected measured timing.  Alternatively
    supply aligned ``starts`` and ``ends``.  Display no scaffold for future
    groups: keep the apparatus geometry, but attach its illuminated traces to
    ``token_state()['visible']`` rather than showing a complete phrase rail.
    """
    words = [str(w) for w in words]
    if transcript is not None:
        timing = align_tokens(words, a, b, transcript, line_index)
    elif starts is not None:
        timing = [(float(s), float(ends[k]) if ends is not None else
                   float(starts[k + 1]) if k + 1 < len(starts) else b)
                  for k, s in enumerate(starts)]
    else:
        raise ValueError('plan_tokens requires transcript or measured starts')
    normalized = [norm(w) for w in words]
    groups = []
    k = 0
    while k < len(words):
        count = 1
        if k + 1 < len(words):
            w, nxt = normalized[k:k + 2]
            breath = timing[k + 1][0] - timing[k][1]
            punctuation = words[k].rstrip().endswith((',', '?', '!', '.', ';', ':'))
            pair = (w, nxt) in _COMPOUNDS or (w in _FUNCTION and nxt not in _SOLO)
            if pair and w not in _SOLO and breath < .36 and not punctuation:
                count = 2
        groups.append(list(range(k, k + count)))
        k += count
    result = [None] * len(words)
    for group_id, indices in enumerate(groups):
        first, last = indices[0], indices[-1]
        next_start = timing[groups[group_id + 1][0]][0] if group_id + 1 < len(groups) else b
        # A hard semantic handoff limits the screen to this group (1–2 words).
        # The trailing 0.12s only fills an actual vocal gap; it never overlaps
        # the next group's lexical content.
        off = min(next_start, b, timing[last][1] + .12)
        for slot, index in enumerate(indices):
            start, end = timing[index]
            result[index] = {
                'index': index, 'text': words[index], 'start': start, 'end': end,
                'group': group_id, 'group_start': timing[first][0],
                'group_end': off, 'group_size': len(indices), 'slot': slot,
                'keyword': normalized[index] in _SOLO, 'drive': _drive(words[index]),
                'entry': min(.075, max(.035, (end - start) * .20)),
                'exit': min(.105, max(.045, (off - start) * .20)),
                # Alternate architecture sides/depths, not a bottom subtitle line.
                'axis': group_id % 4, 'direction': 1 if group_id % 2 == 0 else -1,
            }
    return result


def token_state(t, token):
    """Visibility, line-trace reveal and local spatial action for one token.

    Entry comes from a rail/edge, then settles for legibility.  The final
    45–105ms collapse toward the attached structure, with no long ghost lyric.
    In a two-word group the first word can remain while the second is sung;
    the second cannot appear before its own onset.
    """
    start, off = token['start'], token['group_end']
    if t < start or t >= off:
        return {'visible': False, 'gain': 0., 'reveal': 0., 'enter': 0.,
                'leave': 0., 'x': 0., 'y': 0., 'z': 0., 'scale': 1.,
                'drive': token['drive'], 'energy': 0.}
    enter = _ease((t - start) / token['entry'])
    leave = _ease((t - (off - token['exit'])) / token['exit'])
    direction = token['direction']
    d = (1 - enter) * 1.25 + leave * 1.65
    axis = token['axis']
    x = direction * d if axis in (0, 2) else 0.
    y = direction * d * .65 if axis in (1, 3) else 0.
    z = -(1 - enter) * 2.2 + leave * 4.5
    return {
        'visible': True, 'gain': (1.45 + .55 * (1 - enter)) * (1 - .55 * leave),
        'reveal': _clamp((t - start) / min(.09, token['entry'] * 1.15)),
        'enter': enter, 'leave': leave, 'x': x, 'y': y, 'z': z,
        'scale': 1. + (1 - enter) * .08 - leave * .12,
        'drive': token['drive'], 'energy': max(1 - enter, leave * .6),
    }


def active_tokens(t, score):
    """Convenience interface and useful QA invariant: never more than 2."""
    return [(token, state) for token in score
            if (state := token_state(t, token))['visible']]
