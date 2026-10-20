"""Word-pair coverage for the second half, using finite semantic camera moves.

The first half already has its own phrase director.  Here the incoming words
select a specific physical camera operation: withdraw memory racks, take the
left junction, lose the operator, follow a fuse, separate the two orthogonal
axes, or inspect the strings behind the stage.  There is no free-running
oscillation or camera-relative geometry in this module.
"""

import json
from pathlib import Path


_TIMELINE = json.loads(Path(__file__).with_name('word_timeline.json').read_text(encoding='utf-8'))

# Dedicated rigs retain priority.  These are real mechanisms with several
# internal phases rather than holes in the pair coverage.
PROTECTED = ((56.20, 58.43), (62.34, 65.94), (73.87, 77.24),
             (84.78, 89.995), (109.82, 114.10), (127.90, 132.22))

# Each line has a persistent physical direction.  Its pairs are successive
# inserts along that direction, not alternating arbitrary left/right nudges.
_INTENT = {
    19: ('memory-withdrawal', 'Follow the withdrawn memory banks down and away.'),
    20: ('left-junction', 'Approach the junction, take its left branch, then depart low.'),
    22: ('tether-release', 'Inspect the three channels, tension their tether, then release it.'),
    23: ('forming-die', 'Follow material into the die and then skim its paperclip output.'),
    24: ('absent-operator', 'Drop from the unreachable switch to its absent operator and retreat.'),
    25: ('burning-trace', 'Move along the same fuse from the ignition point to its end.'),
    26: ('independent-axes', 'Ascend the ability axis, then travel across the unrelated goal axis.'),
    27: ('decoder-departure', 'Leave the decoder along its actual outgoing route.'),
    28: ('density-pressure', 'Close on the compression chamber, then depart under its barrier.'),
    29: ('feedback-tilt', 'Inspect the core, follow its feedback, and tip with the failed loop.'),
    30: ('selected-future', 'Enter the branch tree and follow its selected future.'),
    32: ('occluded-witness', 'Approach the witness aperture from below, then lose sight of its interior.'),
    33: ('backstage-strings', 'Pull aside from the frontal stage to expose its overhead strings.'),
}


def _visible_intervals(a, b):
    segments = [(a, b)]
    for pa, pb in PROTECTED:
        next_segments = []
        for left, right in segments:
            if right <= pa or left >= pb:
                next_segments.append((left, right))
            else:
                if left < pa:
                    next_segments.append((left, pa))
                if right > pb:
                    next_segments.append((pb, right))
        segments = next_segments
    return [(left, right) for left, right in segments if right-left >= .12]


PAIR_CUTS = []
for line_index, row in enumerate(_TIMELINE):
    if line_index not in _INTENT:
        continue
    groups = sorted({word['group'] for word in row})
    for ordinal, group in enumerate(groups):
        members = [word for word in row if word['group'] == group]
        a, b = members[0]['group_start'], members[0]['group_end']
        if b <= 77.24:
            continue
        for left, right in _visible_intervals(a, b):
            role, intent = _INTENT[line_index]
            PAIR_CUTS.append(dict(start=left, end=right, lexical_start=a,
                                  line_index=line_index, group=group,
                                  ordinal=ordinal, count=len(groups),
                                  words=[word['text'] for word in members],
                                  role=role, intent=intent))
PAIR_CUTS = tuple(PAIR_CUTS)

# Instrumental breath after CDR and after the uncertain witness remains a
# deliberate camera departure rather than a static hold awaiting the words.
SILENT_PAIR_CUTS = (
    dict(start=135.80, end=136.35, line_index=32, group=90, ordinal=6, count=8,
         words=[], role='occluded-witness', intent='Lose the closed aperture behind the lens.'),
    dict(start=136.35, end=136.90, line_index=33, group=91, ordinal=0, count=5,
         words=[], role='backstage-strings', intent='Slip into the space above the stage.'),
    dict(start=140.60, end=141.20, line_index=33, group=92, ordinal=4, count=5,
         words=[], role='backstage-strings', intent='Leave the visible stage by its overhead rigging.'),
)


def pair_state(t):
    for cue in PAIR_CUTS + SILENT_PAIR_CUTS:
        if cue['start'] <= t < cue['end']:
            return dict(cue, active=True,
                        u=(t-cue['start'])/(cue['end']-cue['start']))
    return dict(active=False)


def _pose(cue):
    """Local start/end eye positions, target pan, bank and lens adjustment."""
    role = cue['role']
    j = cue['ordinal']
    u = cue['u']
    # Fast motion is carried by a departure acceleration, not impact shake.
    p = .66*u + .34*u*u
    if role == 'memory-withdrawal':
        positions = (((-2.8, 1.0, -.8), (-.9, -.9, 1.5)),
                     ((2.7, .6, -.7), (.5, -1.7, 1.9)),
                     ((1.0, 2.0, -.9), (-1.3, -2.0, 2.3)))
        a, b = positions[min(j, 2)]; pan = (.1, -.25, 0); bank = -.045; zoom = 1.
    elif role == 'left-junction':
        positions = (((1.8, 1.1, -1.2), (.1, -.2, 1.8)),
                     ((2.7, .6, -.8), (-2.4, .25, 2.0)),
                     ((-2.3, .7, -.4), (-.5, -1.3, 2.1)),
                     ((1.1, -1.7, -.4), (-2.2, .4, 2.0)))
        a, b = positions[min(j, 3)]; pan = (-.4, -.05, 0); bank = -.065; zoom = 2.
    elif role == 'tether-release':
        positions = (((-2.8, 1.3, -.9), (-.2, -.2, 2.0)),
                     ((2.5, -.9, -.7), (-1.6, .8, 2.5)),
                     ((-2.4, -1.2, -.6), (1.7, .5, 2.3)),
                     ((.4, 1.9, -.4), (1.0, -1.7, 2.4)))
        a, b = positions[min(j, 3)]; pan = (.05, -.05, 0); bank = .05; zoom = 1.
    elif role == 'forming-die':
        a = (-2.5+.30*j, 1.1-.10*j, -.8)
        b = (1.5+.15*j, -.9+.09*j, 2.0)
        pan = (.25, -.1, 0); bank = -.045; zoom = 1.
    elif role == 'absent-operator':
        # Switch high / operator low / escape corridor shut: successive
        # inserts follow the actual causal order instead of circling a point.
        positions = (((-2.4, 2., -.6), (1.7, .1, 2.1)),
                     ((2.2, 1., -.7), (.6, -2., 1.7)),
                     ((-1.8, -1.8, -.8), (2.1, -.8, 1.8)),
                     ((2.3, -1.5, -.7), (-1.8, 1., 2.2)),
                     ((-2.2, -1.6, -.9), (1.7, .2, 2.7)),
                     ((1.8, 1.2, -.8), (-2.4, -.6, 2.3)),
                     ((-2.3, .3, -.8), (.8, 1.8, 2.2)),
                     ((1.7, 1.6, -1.), (-1.7, -1.2, 2.4)))
        a, b = positions[min(j, 7)]
        pan = (.15, -.3 if j < 4 else .1, 0); bank = -.045; zoom = 2.
    elif role == 'burning-trace':
        a = (-2.6+.25*j, -1.3, -.8)
        b = (1.9+.15*j, .65, 2.2)
        pan = (.35, -.1, 0); bank = .04; zoom = 1.
    elif role == 'independent-axes':
        positions = (((-1.1, -2.5, -.8), (1.2, 2.1, 2.4)),
                     ((-2.8, 1.2, -.5), (2.3, 1.0, 1.8)),
                     ((2.5, 1.3, -.9), (-1.8, -1.5, 2.5)))
        a, b = positions[min(j, 2)]; pan = (.1, .1, 0); bank = .08 if j == 1 else -.055; zoom = 1.
    elif role == 'density-pressure':
        positions = (((2.7, 1.5, -1.2), (-1.7, .2, 2.4)),
                     ((-2.2, -1.5, -.6), (1.2, .8, 2.7)),
                     ((1.8, 1.8, -.7), (-1.5, -1.1, 2.4)))
        a, b = positions[min(j, 2)]; pan = (.1, -.15, 0); bank = .05; zoom = 2.
    elif role == 'feedback-tilt':
        positions = (((-2.9, 1.3, -.8), (1.9, -.7, 2.1)),
                     ((2.5, -.9, -.7), (-1.8, .7, 2.4)),
                     ((-2.6, -.9, -.7), (1.7, 1.3, 2.1)),
                     ((1.4, 1.8, -.9), (-2.0, -1.1, 2.2)))
        a, b = positions[min(j, 3)]; pan = (.1, .12, 0); bank = -.075 if j >= 2 else .04; zoom = 1.
    elif role == 'selected-future':
        a = (-2.5+.15*j, 1.6-.12*j, -.8)
        b = (1.6+.10*j, -.8+.13*j, 2.2)
        pan = (.25, .05, 0); bank = .045; zoom = 2.
    elif role == 'occluded-witness':
        positions = (((-2.2, -1.8, -.7), (1.5, .3, 1.9)),
                     ((2.5, .8, -.8), (-1.5, -1.0, 2.0)),
                     ((-2.1, -1.0, -.7), (1.8, 1.0, 2.2)),
                     ((2.1, 1.4, -.8), (-1.7, -.4, 2.4)),
                     ((-2.6, .4, -.5), (.8, -1.3, 2.3)),
                     ((1.6, 1.8, -.7), (-2.1, -.7, 2.4)),
                     ((-2.0, -1.2, -.5), (1.4, .9, 2.5)))
        a, b = positions[min(j, 6)]; pan = (-.1, .05, 0); bank = -.055; zoom = 1.
    elif role == 'backstage-strings':
        positions = (((-2.7, -1.2, -.8), (1.5, 1.8, 2.0)),
                     ((2.6, .5, -.8), (-1.6, 1.6, 2.2)),
                     ((-2.4, 1.5, -.7), (1.9, -.5, 2.3)),
                     ((1.3, 2.0, -.9), (-2., -1.2, 2.5)),
                     ((-1.9, -1.2, -.6), (1.8, 1.7, 2.6)))
        a, b = positions[min(j, 4)]; pan = (.1, .25, 0); bank = .055; zoom = 2.
    else:
        a, b = ((-2.1, 1.2, -.8), (1.7, -.8, 2.1))
        pan = (.1, .1, 0); bank = .04; zoom = 1.
    return dict(start=a, end=b, offset=tuple(a[k]*(1.-p)+b[k]*p for k in range(3)),
                pan=pan, bank=bank*(.8-.4*u), zoom=zoom+1.2*u,
                phase='lexical_%s_%s_%s' % (cue['line_index'], cue['group'], role))


def pair_camera(t, eye, target, roll, fov, *, g):
    cue = pair_state(t)
    if not cue['active']:
        return None
    np = g['np']
    flight = g['sample_flight_camera'](t)
    if flight['active']:
        crossing = flight.get('crossing_time')
        # The approach, exact crossing, and a settling interval retain their
        # physical trajectory.  That flight is itself the pair's fast action.
        if not crossing or not flight.get('has_crossed') or cue['start'] < crossing+.14:
            return None
    eye = np.array(eye, float)
    target = np.array(target, float)
    pose = _pose(cue)
    offset = np.asarray(pose['offset'], float)
    if flight['active']:
        aircraft = g['flight_pose'](t)
        right, up = np.array(aircraft['right']), np.array(aircraft['up'])
        move = right*offset[0]+up*offset[1]
        # Exact equal displacement preserves eye-target direction and signed
        # normal depth.  No re-crossing, no aftershock camera reversal.
        eye += move
        target += move
    else:
        forward = target-eye
        forward /= max(1.e-9, np.linalg.norm(forward))
        right = np.cross(forward, [0., 1., 0.])
        right /= max(1.e-9, np.linalg.norm(right))
        up = np.cross(right, forward)
        basis = np.array([right, up, forward]).T
        eye += basis@offset
        pan = np.asarray(pose['pan'])*(cue['u']*.7+.3)
        target += basis@np.array([offset[0]*.09+pan[0], offset[1]*.08+pan[1], pan[2]])
    return dict(eye=eye, target=target, roll=roll+pose['bank'],
                fov=min(104., max(38., fov+pose['zoom'])),
                phase=pose['phase'], words=cue['words'], cut=cue['start'],
                intent=cue['intent'], motion=pose['end'])


def _smooth(x):
    x = min(1., max(0., x))
    return x*x*(3.-2.*x)


def pair_part_matrix(name, key, matrix, t, *, g):
    """Finite actions of existing assembly parts, never new floating icons.

    Called from semantic_director's part() before the draw.  Hosts remain
    anchored to authored_frame_view.  Moving a rack or tightening a channel
    therefore has visible parallax independently of the actual current lens.
    """
    tr, rot, np = g['tr'], g['rot'], g['np']
    if name == 'vonneumann' and key in ('memory_banks', 'memory_bus'):
        # Mechanical retirement: racks and their attached harness withdraw
        # down their common support, then tip into the decommissioned bay.
        q = _smooth((t-79.80)/.80)
        return matrix@tr(0., -3.8*q, -2.7*q)@rot(-.09*q, 0)
    if name == 'gato' and key == 'gato_channels':
        # Shared multimodal channels stretch against one tether.  The small
        # YZ release is cumulative and tied to the words, with no phase wrap.
        q = _smooth((t-90.50)/1.0)
        pull = _smooth((t-92.84)/.92)
        return matrix@tr(0., -.65*q-1.0*pull, -1.6*pull)@np.diag([1.+.035*pull, 1.+.045*q, 1., 1.])
    if name in ('compute', 'gpu') and key == 'gpu_packets':
        # Packets have a finite transit into the chassis, not an endless scan.
        a, b = (65.94, 68.20) if name == 'compute' else (118.70, 120.18)
        return matrix@tr(0., 0., -3.2*_smooth((t-a)/(b-a)))
    if name == 'show' and key == 'show_backstage':
        # The rig's lift exposes the stage's supporting strings from below.
        lift = _smooth((t-138.06)/1.30)
        return matrix@tr(0., 1.4*lift, -.7*lift)
    return matrix


def pair_action_state(t):
    """Inspectable production actions; useful alongside actual camera QA."""
    if 79.80 <= t < 80.68:
        return dict(active=True, part='memory-rack-retirement', value=_smooth((t-79.80)/.80))
    if 90.50 <= t < 94.06:
        return dict(active=True, part='channel-tether', value=_smooth((t-90.50)/1.)+_smooth((t-92.84)/.92))
    if 138.06 <= t < 139.58:
        return dict(active=True, part='stage-rig-lift', value=_smooth((t-138.06)/1.3))
    return dict(active=False)


def coverage_plan():
    return dict(lexical_groups=len(PAIR_CUTS), silent_groups=len(SILENT_PAIR_CUTS),
                lines=sorted({cue['line_index'] for cue in PAIR_CUTS}),
                cuts=[dict(cue) for cue in PAIR_CUTS], protected=list(PROTECTED))
