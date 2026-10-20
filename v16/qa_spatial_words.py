"""Read-only spatial and timing diagnostics for the actual v13 word matrices.

Run from the project root.  This never calls drawframe or changes production
sources.  It deliberately distinguishes trace completion from readable,
front-facing, fully framed letters before an intentional camera crossing.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VERSION = sys.argv[1] if len(sys.argv) > 1 else 'v16'
spec = importlib.util.spec_from_file_location('qa_renderer', ROOT / VERSION / 'render.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
composition = ROOT / VERSION / 'compositions.json'
if composition.exists():
    for key, value in json.loads(composition.read_text()).get('word_scale_guard', {}).items():
        r.WORD_SCALE_GUARD[int(key)] = value


def inspect_word(i, j, t, pose=None):
    token = r.TOKEN_SCORES[i][j]
    ts = r.token_state(t, token)
    if pose is None:
        pose = r.frame_view(t)
    state, eye, target, vp = pose
    matrix = r.token_matrix(i, j, t)
    gpu = r.TOKEN_DATA[i][j][0]
    points = np.array([matrix @ np.array([x, y, z, 1.])
                       for x in [gpu.bmin[0], gpu.bmax[0]]
                       for y in [gpu.bmin[1], gpu.bmax[1]]
                       for z in [gpu.bmin[2], gpu.bmax[2]]])
    clip = points @ vp.T
    ndc = clip[:, :2] / np.maximum(clip[:, 3:4], 1.e-9)
    center = (matrix @ np.r_[r.TOKEN_GROUPS[i][token['group']]['center'], 1.])[:3]
    normal = np.cross(matrix[:3, 0], matrix[:3, 1])
    normal /= np.linalg.norm(normal)
    cosine = float(normal @ ((eye-center) / max(1.e-9, np.linalg.norm(eye-center))))
    height = float(np.ptp(ndc[:, 1]) * r.H/2)
    reach = float(abs(ndc).max())
    complete = ts['visible'] and ts['reveal'] >= .99 and ts['gain'] >= .6
    readable = complete and clip[:, 3].min() > 0 and reach <= 1.02 and cosine > .35 and height >= 28
    return dict(t=round(t, 6), complete=bool(complete), readable=bool(readable),
                reach=reach, face_cosine=cosine, height_px=height,
                min_clip_w=float(clip[:, 3].min()),
                eye=[float(v) for v in eye], center=[float(v) for v in center],
                normal=[float(v) for v in normal])


rows = []
for i, score in enumerate(r.TOKEN_SCORES):
    for j, token in enumerate(score):
        samples = [inspect_word(i, j, frame/30)
                   for frame in range(math.ceil(token['start']*30), math.ceil(token['end']*30))]
        complete = [s for s in samples if s['complete']]
        readable = [s for s in samples if s['readable']]
        # Prefer a fully traced front view, then the least clipped frame.
        best = min(complete or samples, key=lambda s: (s['reach'] > 1.02, -s['face_cosine'], s['reach'])) if samples else None
        rows.append(dict(line=i, word=j, text=token['text'], start=token['start'], end=token['end'],
                         complete_frames=[s['t'] for s in complete],
                         readable_frames=[s['t'] for s in readable], best=best))

maximum = 0
early = []
for frame in range(math.ceil(141.2*30)):
    t = frame/30
    active = [(i, j) for i, score in enumerate(r.TOKEN_SCORES)
              for j, token in enumerate(score) if r.token_state(t, token)['visible']]
    maximum = max(maximum, len(active))
    for i, j in active:
        if t < r.TOKEN_SCORES[i][j]['start']:
            early.append([i, j, t])
canonical = json.loads((ROOT/'work/lyrics.json').read_text())
expected = [r.token_norm(w) for line in canonical for w in line[3].replace('|', ' ').split()]
actual = [r.token_norm(token['text']) for score in r.TOKEN_SCORES for token in score]
report = dict(version=VERSION, tokens=len(rows), canonical_order=actual == expected,
              max_simultaneous=maximum, early_words=early,
              never_complete=[dict(line=x['line'], word=x['word'], text=x['text']) for x in rows if not x['complete_frames']],
              never_spatially_readable=[dict(line=x['line'], word=x['word'], text=x['text'], best=x['best']) for x in rows if not x['readable_frames']],
              words=rows)
path = ROOT/VERSION/f'qa_spatial_words_{VERSION}.json'
path.write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'words'}, indent=2))
print(path)
