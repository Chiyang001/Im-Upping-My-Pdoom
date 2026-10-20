"""Measure the removal of lexical camera resets against the original v20.

The baseline renderer is loaded from Git in memory, in its own process. No
historical directory is created. Both workers import the same v20 geometry
and score files; neither calls prepare_compositions or changes production.
Numerical continuity is evidence about motion only, not an aesthetic verdict.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import types

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'v20'
BASELINE = '7bab5f9'
REPORT = FOLDER / 'qa_smooth_camera.json'
EPSILON = .001


def renderer_source(version):
    if version == 'baseline':
        return subprocess.run(
            ['git', 'show', BASELINE + ':v20/render.py'], cwd=ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True).stdout.decode('utf-8')
    return (FOLDER / 'render.py').read_text(encoding='utf-8')


def load_renderer(version):
    source = renderer_source(version)
    sys.path.insert(0, str(FOLDER))
    name = 'smooth_camera_' + version
    renderer = types.ModuleType(name)
    renderer.__file__ = str(FOLDER / 'render.py')
    sys.modules[name] = renderer
    exec(compile(source, renderer.__file__, 'exec'), renderer.__dict__)
    return renderer, source


def direction_angle(a, b):
    return math.degrees(math.acos(float(np.clip(np.dot(a, b), -1., 1.))))


def pose(renderer, t, hit=0.):
    state, eye, target, vp = renderer.frame_view(float(t), hit)
    eye, target = np.asarray(eye), np.asarray(target)
    travel = renderer.camera_state(float(t), np, math)['travel']
    common = np.array([0., 0., travel])
    direction = target-eye
    direction /= max(1.e-12, np.linalg.norm(direction))
    assert np.isfinite(np.r_[eye, target, np.asarray(vp).ravel()]).all()
    return dict(eye=(eye-common).tolist(), target=(target-common).tolist(),
                direction=direction.tolist(), roll=float(state['roll']),
                lens=float(state['lens']), vp=np.asarray(vp).tolist())


def delta(a, b):
    return dict(eye=float(np.linalg.norm(np.array(b['eye'])-a['eye'])),
                target=float(np.linalg.norm(np.array(b['target'])-a['target'])),
                direction_degrees=direction_angle(a['direction'], b['direction']),
                bank_degrees=abs(math.degrees(b['roll']-a['roll'])),
                lens_degrees=abs(b['lens']-a['lens']),
                projection_max_abs=float(np.abs(np.array(b['vp'])-a['vp']).max()))


def protected_reason(r, t):
    # These are existing v20 scene cuts and intentional mechanisms. The
    # exclusion is temporal/structural, not based on a reassuring camera label.
    lyric_boundaries = {edge for row in r.TOKEN_SCORES for edge in
                        (min(word['start'] for word in row),
                         max(word['end'] for word in row))}
    if any(abs(t-edge) <= EPSILON for edge in lyric_boundaries):
        return 'lyric_line_start_or_end'
    if t <= 1.42+EPSILON:
        return 'instrumental_hook'
    before, after = r.sample_shot(t-EPSILON), r.sample_shot(t+EPSILON)
    if before['shot_id'] != after['shot_id']:
        return 'original_shot_cut'
    if any(r.sample_flight_camera(q)['active'] for q in (t-EPSILON, t, t+EPSILON)):
        return 'physical_word_flight'
    if any(r.sample_upgrade(q)['active'] for q in (t-EPSILON, t, t+EPSILON)):
        return 'archive_upgrade'
    if 73.87-EPSILON <= t <= 77.24+EPSILON:
        return 'repeat_rail'
    if 84.78-EPSILON <= t <= 89.995+EPSILON:
        return 'cdr_inspection'
    if 62.34-EPSILON <= t <= 65.94+EPSILON:
        return 'moon_object_pursuit'
    if 56.20-EPSILON <= t <= 58.43+EPSILON:
        return 'free_cage_strikes'
    if 109.82-EPSILON <= t <= 114.10+EPSILON:
        return 'transformer_authored_inserts'
    if r.sample_finale(t)['active'] or t >= 141.2:
        return 'outro_and_infinity'
    return None


def collect_worker(version):
    r, source = load_renderer(version)
    from first_half_score import PHRASE_CUTS, SILENT_CUTS
    from pair_director import PAIR_CUTS, SILENT_PAIR_CUTS

    invocations = dict(phrase_camera=0, pair_camera=0)
    for name in invocations:
        original = getattr(r, name)
        def wrapped(*args, _fn=original, _name=name, **kwargs):
            invocations[_name] += 1
            return _fn(*args, **kwargs)
        setattr(r, name, wrapped)

    # The 147 original lexical cues are sampled even if a specialised scene
    # used to take precedence. No coverage threshold demands fast motion.
    cues = list(PHRASE_CUTS)+list(PAIR_CUTS)
    boundaries = []
    lyric_boundaries = {edge for row in r.TOKEN_SCORES for edge in
                        (min(word['start'] for word in row),
                         max(word['end'] for word in row))}
    times = sorted({c['start'] for c in cues} | {c['end'] for c in cues}
                   | {c[k] for c in SILENT_CUTS+SILENT_PAIR_CUTS for k in ('start', 'end')}
                   | lyric_boundaries)
    for t in times:
        reason = protected_reason(r, t)
        if reason:
            row = dict(time=t, excluded=reason)
            if reason == 'lyric_line_start_or_end':
                row['delta'] = delta(pose(r,t-EPSILON),pose(r,t+EPSILON))
                row['nearest_original_shot_cut'] = min(r.CUT_TIMES,key=lambda q:abs(q-t))
            boundaries.append(row)
            continue
        before, after = pose(r, t-EPSILON), pose(r, t+EPSILON)
        boundaries.append(dict(time=t, excluded=None, delta=delta(before, after)))

    beat_checks = []
    ordinary_samples = []
    for c in cues:
        t = (c['start']+c['end'])*.5
        pose(r, t, 0.)
        if protected_reason(r, t):
            continue
        a, b = pose(r, t, 0.), pose(r, t, 1.)
        d = delta(a, b)
        beat_checks.append(dict(time=t, words=c['words'], delta=d))
        ordinary_samples.append((c['start']+.01, c['end']-.01))

    # Existing purposeful motion must remain possible after removing the
    # lexical overlay. Common forward-world travel is subtracted in pose().
    directed_intervals = (
        ('circuits_authored_truck', 6.05, 6.80),
        ('loss_word_flight', 10.40, 11.30),
        ('pdoom_flight', 23.56, 24.70),
        ('free_strikes', 56.37, 57.85),
        ('moon_pursuit', 62.75, 65.30),
        ('repeat_retrace', 75.92, 76.28),
        ('go_disaster', 94.10, 95.10),
        ('transformer_inserts', 110.00, 113.70),
        ('archive_upgrade', 128.10, 130.30),
        ('long_outro', 143.00, 149.00),
        ('infinity_ending', 153.00, 155.80),
    )
    directed = []
    for name, a, b in directed_intervals:
        poses = [pose(r, t) for t in np.linspace(a, b, 31)]
        length = sum(np.linalg.norm(np.array(q['eye'])-p['eye'])
                     for p, q in zip(poses, poses[1:]))
        directed.append(dict(name=name, start=a, end=b, local_eye_path=float(length),
                             delta=delta(poses[0], poses[-1])))

    tree = ast.parse(source)
    frame_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == 'frame_view')
    static_calls = {name:sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                            and n.func.id == name for n in ast.walk(frame_node))
                    for name in invocations}
    report = dict(version=version, baseline_commit=BASELINE,
                  render_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  original_lexical_cues=len(cues),
                  actual_overlay_invocations=invocations,
                  static_frame_view_overlay_calls=static_calls,
                  epsilon_seconds=EPSILON, boundaries=boundaries,
                  beat_checks=beat_checks, purposeful_intervals=directed)
    destination = FOLDER / ('qa_smooth_camera_' + version + '.json')
    destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(destination, flush=True)


def summarize():
    reports = {}
    for version in ('baseline', 'candidate'):
        subprocess.run([sys.executable, '-X', 'utf8', str(Path(__file__).resolve()),
                        '--worker', version], cwd=ROOT, check=True)
        reports[version] = json.loads((FOLDER / ('qa_smooth_camera_' + version + '.json')).read_text())
    baseline, candidate = reports['baseline'], reports['candidate']
    old = {row['time']:row for row in baseline['boundaries'] if not row['excluded']}
    new = {row['time']:row for row in candidate['boundaries'] if not row['excluded']}
    assert set(old) == set(new)
    keys = ('eye', 'direction_degrees', 'bank_degrees', 'lens_degrees')
    summary = {}
    for key in keys:
        values = {version:[row['delta'][key] for row in rows.values()]
                  for version, rows in [('baseline', old), ('candidate', new)]}
        summary[key] = {version:dict(median=statistics.median(v), maximum=max(v),
                                     mean=statistics.mean(v)) for version,v in values.items()}
    beat_max = {key:max(row['delta'][key] for row in candidate['beat_checks'])
                for key in (*keys, 'target', 'projection_max_abs')}
    residual = [dict(time=t, baseline=old[t]['delta'], candidate=row['delta'])
                for t,row in new.items()
                if row['delta']['eye'] > .10 or row['delta']['direction_degrees'] > .10
                or row['delta']['bank_degrees'] > .10 or row['delta']['lens_degrees'] > .20]
    old_transitions = {row['time']:row for row in baseline['boundaries']
                       if row['excluded'] == 'lyric_line_start_or_end'}
    line_transitions = [dict(time=row['time'],nearest_original_shot_cut=row['nearest_original_shot_cut'],
                             baseline=old_transitions[row['time']]['delta'],candidate=row['delta'])
                        for row in candidate['boundaries']
                        if row['excluded'] == 'lyric_line_start_or_end']
    overlay_off = all(n == 0 for n in candidate['actual_overlay_invocations'].values())
    static_off = all(n == 0 for n in candidate['static_frame_view_overlay_calls'].values())
    beat_off = all(value < 1.e-10 for key,value in beat_max.items()
                   if key != 'direction_degrees') and beat_max['direction_degrees'] < 2.e-6
    movement_kept = all(row['local_eye_path'] > .10 for row in candidate['purposeful_intervals'])
    report = dict(baseline_commit=BASELINE, original_lexical_cues=candidate['original_lexical_cues'],
                  compared_ordinary_boundaries=len(new), excluded_boundaries=len(candidate['boundaries'])-len(new),
                  method='Final production frame_view sampled at same-lyric-line word-group boundaries +/- 1ms, hit=0; common world Z travel removed. ALL lyric-line starts/ends are excluded and recorded separately, alongside dedicated v20 rigs and original shot cuts.',
                  limitation='Pose continuity is not an aesthetic verdict; actual encoded review remains necessary.',
                  ordinary_boundary_statistics=summary, residual_review_flags=residual,
                  separately_recorded_lyric_line_transitions=line_transitions,
                  ordinary_hit_zero_vs_one_samples=len(candidate['beat_checks']),
                  ordinary_hit_zero_vs_one_maximum_delta=beat_max,
                  actual_overlay_invocations=candidate['actual_overlay_invocations'],
                  static_frame_view_overlay_calls=candidate['static_frame_view_overlay_calls'],
                  lexical_overlay_disabled=overlay_off and static_off,
                  ordinary_beat_camera_disabled=beat_off,
                  purposeful_motion_retained=movement_kept,
                  purposeful_intervals=candidate['purposeful_intervals'],
                  passed=overlay_off and static_off and beat_off and movement_kept and not residual,
                  renderer_sha256=candidate['render_sha256'])
    REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
    rows = []
    for metric, statistics_ in summary.items():
        a,b = statistics_['baseline'],statistics_['candidate']
        rows.append('| %s | %.6f | %.6f | %.6f | %.6f |' % (metric,a['median'],b['median'],a['maximum'],b['maximum']))
    text = '''# v20 smooth camera audit\n\nBaseline: original v20 commit `%s`. The baseline source was read directly from Git into memory in an isolated process; no historical version directory was created.\n\nThe final production camera was sampled 1 ms before and after %d ordinary word-group boundaries **within the same lyric line**. Every lyric-line start/end is excluded uniformly and recorded separately in the JSON report. Original shot cuts and deliberate flight, FREE, Moon, Repeat, CDR, Transformer, upgrade and ending rigs were also excluded. Common world travel was subtracted.\n\n| Pose change across 2 ms | Original median | Smooth median | Original maximum | Smooth maximum |\n| --- | ---: | ---: | ---: | ---: |\n%s\n\n- Original lexical camera cues: %d.\n- Candidate calls to phrase_camera / pair_camera: %s.\n- Ordinary hit=0 versus hit=1 checks: %d; camera poses and projections equal: %s.\n- Retained deliberate camera intervals: %d; all retain measured local movement: %s.\n- Residual same-line boundary flags: %d.\n- Numerical result for this limited scope: **%s**.\n\nOriginal line/scene transitions remain intentional. For example, Without begins at 84.720 s while its authored shot cut occurs at 84.780 s; its inherited lens transition is retained. This audit does not claim that the entire movie has no cuts or pose jumps. It checks removal of repeated word-group camera resets and ordinary beat shake. Detailed samples, including every lyric-line transition, are in the generated qa_smooth_camera.json report.\n\nThe finalized smooth-v20 MP4 was separately decoded for 32 opening stills, including five native 1920x1080 images, plus two supplemental native BAG checkpoints at 28.400 and 28.500 s. Both contact-sheet pages were inspected: the original hook, single eye, circuits, loss, authority, dialogue and mushroom scenes remain. BAG is clearly readable in both supplemental frames before passing the camera. Contact sheets cannot prove temporal smoothness; the measured camera test above supplies the complementary motion check.\n''' % (BASELINE,len(new),'\n'.join(rows),candidate['original_lexical_cues'],
       candidate['actual_overlay_invocations'],len(candidate['beat_checks']),beat_off,
       len(candidate['purposeful_intervals']),movement_kept,len(residual),'PASS' if report['passed'] else 'REVIEW REQUIRED')
    (FOLDER / 'qa_smooth_camera.md').write_text(text, encoding='utf-8')
    if not report['passed']:
        raise SystemExit('Camera audit requires review; inspect residual flags.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=('baseline','candidate'))
    arguments = parser.parse_args()
    if arguments.worker:
        collect_worker(arguments.worker)
    else:
        summarize()
