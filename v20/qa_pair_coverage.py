"""Diagnose actual camera changes for every recorded one/two-word group.

This imports the production renderer and samples its final ``frame_view`` at
the delivery frame rate. Common world travel is removed before measuring
translation. A director label, a time counter, a flash, and ordinary straight
corridor travel are never accepted as evidence of a meaningful camera change.

The numerical thresholds below are REVIEW FLAGS, not a proof of beauty or of
semantic scene action. Rendered contact sheets and the separate spatial-word
audit remain necessary. Run this in a fresh Python process per version.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load_renderer(version):
    folder = ROOT / version
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location('pair_qa_renderer', folder / 'render.py')
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    r.prepare_compositions()
    return r


def groups_from_renderer(r):
    groups = []
    for line, score in enumerate(r.TOKEN_SCORES):
        for group in sorted({token['group'] for token in score}):
            members = [token for token in score if token['group'] == group]
            groups.append(dict(line=line, group=group,
                               words=[token['text'] for token in members],
                               start=min(token['group_start'] for token in members),
                               end=max(token['group_end'] for token in members)))
    return groups


def angle_degrees(a, b):
    return math.degrees(math.acos(float(np.clip(np.dot(a, b), -1., 1.))))


def pose_at(r, t):
    # Use the exact final camera. hit=0 deliberately excludes music-driven
    # high-frequency shake, while all authored scene/director motion remains.
    state, eye, target, vp = r.frame_view(float(t), 0)
    eye, target, vp = np.asarray(eye), np.asarray(target), np.asarray(vp)
    travel = float(r.camera_state(float(t), np, math)['travel'])
    common = np.array([0., 0., travel])
    direction = target-eye
    length = float(np.linalg.norm(direction))
    finite = bool(np.isfinite(np.r_[eye, target, vp.ravel()]).all())
    determinant = float(np.linalg.det(vp)) if finite else float('nan')
    return dict(t=float(t), eye=eye-common, target=target-common,
                direction=direction/max(1.e-12, length),
                roll=float(state['roll']), lens=float(state['lens']),
                finite=finite, determinant=determinant,
                valid=finite and length > 1.e-6 and abs(determinant) > 1.e-12,
                # These labels are context only. They never establish coverage.
                context={key: str(state[key]) for key in
                         ('meaning_camera', 'pair_camera', 'pair_kinetics',
                          'upgrade_camera', 'object_pursuit', 'actor_follow')
                         if key in state and state[key] is not None})


def summarize(r, group, fps):
    a, b = group['start'], group['end']
    times = [f/fps for f in range(math.ceil(a*fps), math.ceil(b*fps))]
    # Very short groups are still observed, even if they have only one
    # delivered frame. Boundary motion is recorded separately below.
    if not times:
        times = [(a+b)/2.]
    poses = [pose_at(r, t) for t in times]
    eye = np.array([p['eye'] for p in poses])
    target = np.array([p['target'] for p in poses])
    eye_net = float(np.linalg.norm(eye[-1]-eye[0]))
    eye_path = float(np.linalg.norm(np.diff(eye, axis=0), axis=1).sum())
    target_net = float(np.linalg.norm(target[-1]-target[0]))
    eye_spread = float(max(np.linalg.norm(e-eye[0]) for e in eye))
    direction = max(angle_degrees(poses[0]['direction'], p['direction']) for p in poses)
    roll = math.degrees(float(np.ptp(np.unwrap([p['roll'] for p in poses]))))
    fov = float(np.ptp([p['lens'] for p in poses]))
    before = pose_at(r, max(0., a-1./fps))
    after = pose_at(r, a+min(.025, max(.001, (b-a)*.12)))
    boundary_eye = float(np.linalg.norm(after['eye']-before['eye']))
    boundary_direction = angle_degrees(before['direction'], after['direction'])
    boundary_roll = abs(math.degrees(after['roll']-before['roll']))
    boundary_fov = abs(after['lens']-before['lens'])
    efficiency = eye_net/max(1.e-9, eye_path)
    # A reversible authored flight may have low net travel. Retain its range
    # only if the path is coherent enough not to be dominated by tiny jitter.
    reasons = []
    if eye_net >= 1.25: reasons.append('local_translation')
    elif eye_spread >= 2. and efficiency >= .2: reasons.append('coherent_local_excursion')
    if direction >= 3.: reasons.append('direction_change')
    if roll >= 2.2: reasons.append('bank_change')
    if fov >= 3.5: reasons.append('lens_change')
    if boundary_eye >= 1.4 or boundary_direction >= 4. or boundary_roll >= 3. or boundary_fov >= 4.:
        reasons.append('pair_boundary_change')
    invalid = [p['t'] for p in [before, *poses, after] if not p['valid']]
    contexts = sorted({json.dumps(p['context'], sort_keys=True) for p in poses if p['context']})
    return dict(**group, samples=len(poses),
                local_eye_net=eye_net, local_eye_path=eye_path,
                local_eye_spread=eye_spread, eye_path_efficiency=efficiency,
                local_target_net=target_net,
                direction_span_degrees=direction, bank_span_degrees=roll, fov_span_degrees=fov,
                boundary_eye_delta=boundary_eye,
                boundary_direction_degrees=boundary_direction,
                boundary_bank_degrees=boundary_roll, boundary_fov_degrees=boundary_fov,
                numerical_review_flags=reasons, camera_change_observed=bool(reasons),
                requires_scene_action_or_visual_review=not bool(reasons),
                invalid_pose_times=invalid,
                first=dict(t=poses[0]['t'], eye=eye[0].tolist(), target=target[0].tolist()),
                last=dict(t=poses[-1]['t'], eye=eye[-1].tolist(), target=target[-1].tolist()),
                contexts_for_debug_only=contexts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='v20')
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    r = load_renderer(args.version)
    groups = [summarize(r, group, args.fps) for group in groups_from_renderer(r)]
    low = [{k: row[k] for k in ('line', 'group', 'words', 'start', 'end',
                                'local_eye_net', 'direction_span_degrees', 'fov_span_degrees')}
           for row in groups if row['requires_scene_action_or_visual_review']]
    runs = []
    pending = []
    for row in groups:
        if row['requires_scene_action_or_visual_review']:
            if pending and (row['line'] != pending[-1]['line'] or row['start']-pending[-1]['end'] > .3):
                runs.append(pending)
                pending = []
            pending.append(row)
        elif pending:
            runs.append(pending)
            pending = []
    if pending:
        runs.append(pending)
    runs = [dict(line=run[0]['line'], start=run[0]['start'], end=run[-1]['end'],
                 words=[word for row in run for word in row['words']]) for run in runs]
    invalid = [dict(line=row['line'], group=row['group'], times=row['invalid_pose_times'])
               for row in groups if row['invalid_pose_times']]
    folder = ROOT/args.version
    report = dict(version=args.version, fps=args.fps,
                  method='Actual final frame_view, hit=0, common Z world travel removed; labels do not establish coverage.',
                  limitation='Numerical change does not prove semantic clarity or aesthetic quality. Review rendered shots and spatial-word QA separately.',
                  words=sum(len(row['words']) for row in groups), groups=len(groups),
                  camera_change_observed=sum(row['camera_change_observed'] for row in groups),
                  maximum_consecutive_words_needing_scene_action=max((len(run['words']) for run in runs), default=0),
                  camera_only_runs_exceeding_two_words=[run for run in runs if len(run['words']) > 2],
                  scene_action_or_visual_review_required=low, invalid_poses=invalid,
                  render_sha256=hashlib.sha256((folder/'render.py').read_bytes()).hexdigest(),
                  rows=groups)
    output = args.output or folder/'qa_pair_coverage.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'rows'}, indent=2))
    print(output)


if __name__ == '__main__':
    main()
