"""Read-only numerical QA of the authored continuous ending path."""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qa_outro', ROOT/'v13/outro_flight.py')
o = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o)
times = np.arange(o.START, o.FREEZE_TIME+1.e-7, 1/240)
frames = [o.sample_outro_flight(float(t)) for t in times]
eyes = np.array([f['camera_eye'] for f in frames])
step = np.linalg.norm(np.diff(eyes, axis=0), axis=1)
depth = np.array([f['distance'] for f in frames])
beats = []
for i, bt in enumerate(o.BEATS):
    if bt < o.START:
        continue
    attack = o.sample_outro_flight(bt+.067)
    before = o.sample_outro_flight(max(o.START, bt-.030))
    after = o.sample_outro_flight(min(o.FREEZE_TIME, bt+.150))
    beats.append(dict(beat=i, t=bt, distance=o.distance_at(bt),
                      peak_thrust=attack['speed'], preceding_speed=before['speed'],
                      distance_in_180ms=after['distance']-before['distance'],
                      pulse_on_attack=o.sample_outro_flight(bt)['pulse']))
rooms = []
for i, (beat, stage, name, story) in enumerate(o.SCENES):
    t = o.BEATS[beat]
    center = o.route_point(o.distance_at(t))
    eye = o.sample_outro_flight(t)['camera_eye']
    rooms.append(dict(scene=i, beat=beat, t=t, name=name, story=story,
                      eye_to_room_center=math.dist(eye, center),
                      center=list(center)))
reference = o.sample_outro_flight(o.FREEZE_TIME)
frozen = all(o.sample_outro_flight(t) == reference for t in [154.7, 155., 156., 156.667])
report = dict(forward_distance=float(depth[-1]-depth[0]),
              total_path_units=float(step.sum()),
              x_range=float(np.ptp(eyes[:, 0])), y_range=float(np.ptp(eyes[:, 1])),
              monotone_depth=bool(np.all(np.diff(depth)>=-1.e-9)),
              monotone_world_z=bool(np.all(np.diff(eyes[:, 2])<=1.e-9)),
              maximum_240fps_step=float(step.max()),
              maximum_step_acceleration=float(abs(np.diff(step)*240).max()),
              no_invalid_values=bool(np.isfinite(eyes).all()),
              minimum_target_distance=min(math.dist(f['camera_eye'], f['camera_target']) for f in frames),
              nine_distinct_rooms=len({x['name'] for x in rooms}) == 9,
              every_room_crossed=all(x['eye_to_room_center'] < 1.e-5 for x in rooms),
              final_state_frozen=frozen, final_camera=reference['camera_eye'],
              final_target=reference['camera_target'], final_fov=reference['fov'],
              beats=beats, rooms=rooms)
path = ROOT/'v13/qa_outro_continuity.json'
path.write_text(json.dumps(report, indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['beats','rooms']}, indent=2))
print(path)
