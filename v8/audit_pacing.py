"""Check the authored edit density and continuous camera speed."""

import json
import math
from pathlib import Path
import sys
import numpy as np

for folder in ('v5', 'v6', 'v7', 'v8'):
    sys.path.insert(0, folder)
from camera_path import camera_state as base_camera
from camera_path_v8 import camera_state as fast_camera
from edit_director import sample_edit as old_edit
from edit_director_v8 import sample_edit, EDITS

lines = json.loads(Path('work/lyrics.json').read_text())
edges = [0.] + [e.time for e in EDITS if e.time < 141.2] + [141.2]
shots = []
for i, (a, b) in enumerate(zip(edges, edges[1:])):
    content = [j for j, row in enumerate(lines)
               if min(b, row[1]) - max(a, row[0]) >= .35]
    shots.append({'shot': i, 'start': a, 'end': b, 'seconds': b-a,
                  'lyric_groups': content, 'group_count': len(content)})

def speed_stats(edit, camera):
    times = np.arange(1.5, 141.1, 1/60)
    eyes = np.array([camera(float(t), np, math)['eye']
                     + np.asarray(edit(float(t))['eye']) for t in times])
    velocity = np.linalg.norm(np.diff(eyes, axis=0), axis=1) * 60
    valid = []
    for t in times[1:]:
        s = edit(float(t))
        valid.append(not s['transition']['active']
                     and t-s['shot_start'] > .2
                     and s['shot_end']-t > .2)
    return dict(zip(('p10', 'median', 'p90'),
                    map(float, np.quantile(velocity[np.asarray(valid)], [.1,.5,.9]))))

durations = np.array([s['seconds'] for s in shots])
report = {
    'vocal_shots': len(shots), 'vocal_cuts': len(shots)-1,
    'shot_duration_median': float(np.median(durations)),
    'shot_duration_max': float(durations.max()),
    'shots_with_at_most_two_lyric_groups': sum(s['group_count'] <= 2 for s in shots),
    'max_lyric_groups': max(s['group_count'] for s in shots),
    'v7_camera_speed_units_per_second': speed_stats(old_edit, base_camera),
    'v8_camera_speed_units_per_second': speed_stats(sample_edit, fast_camera),
    'travel_gain': 1.65, 'shots': shots,
}
assert report['max_lyric_groups'] <= 4, 'too many lyrics without a cut'
assert report['shot_duration_max'] <= 8.05, 'unintended long shot'
Path('v8/pacing_audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'shots'}, indent=2))
