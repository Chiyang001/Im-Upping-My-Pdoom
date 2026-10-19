"""Fast, motivated shot changes for the v8 line-drawn music video.

Thirty-one real cuts divide the vocal into short, legible actions.  Camera poses
are held after a cut and travel in a new direction; they never ease back to
one common framing.  The red signal and musical time are not reset.  Only
scenery receives the additional world transforms.

This preserves the v6 ``sample_edit`` interface.  Edit times use measured
attacks in rhythm_v3; ownership and lyric guards retain syllables on either
side of a nearby musical cut.  The renderer supplies the faster outro edits.
"""

from bisect import bisect_right
from dataclasses import dataclass
import math


FPS = 30.0
DURATION = 156.667


@dataclass(frozen=True)
class Edit:
    time: float
    kind: str
    frames: int
    direction: float
    axis: str
    label: str
    motive: str
    group: int
    ownership_at: float
    guard_index: int
    guard_until: float
    anchor: tuple = (.5, .5)

    def metadata(self):
        return {k: getattr(self, k) for k in (
            'time', 'kind', 'frames', 'direction', 'axis', 'label',
            'motive', 'group', 'ownership_at', 'guard_index',
            'guard_until', 'anchor')}


# A semantic action motivates every change of location or viewing direction.
# In short lyric groups the cut is on the next strong attack, rather than an
# arbitrary timer.  Two longer held shots let a cause become its consequence.
EDITS = (
    Edit(5.700, 'match', 3, +1, 'x', 'spark / circuit',
         'The eye spark becomes current; track sideways through its circuit.',
         1, 5.700, 1, 9.080, (.48, .48)),
    Edit(9.100, 'crash', 4, -1, 'y', 'current / loss cliff',
         'Current drops down the training-loss cliff; follow from above.',
         2, 9.100, 2, 12.940, (.52, .46)),
    Edit(12.990, 'match', 3, +1, 'x', 'loss cliff / boss bridge',
         'The loss trace becomes the bosses bridge; cross below its command.',
         3, 12.990, 3, 16.200, (.49, .48)),
    Edit(17.070, 'occlusion', 5, +1, 'x', 'boss bridge / jaw',
         'The boss bridge closes across the lens and becomes a devouring jaw.',
         4, 17.070, 4, 22.200, (.53, .46)),
    Edit(22.190, 'occlusion', 5, +1, 'x', 'jaw / city',
         'Jaw teeth cross the lens; emerge at street level inside the city.',
         5, 22.200, 4, 22.200, (.53, .46)),
    Edit(25.685, 'match', 3, +1, 'z', 'FOOM / room',
         'The forecast becomes a real room; match the aperture after the P(doom) detonation.',
         6, 26.060, 5, 26.060, (.51, .48)),
    Edit(31.830, 'match', 3, -1, 'x', 'lies / seeing eye',
         'Shoggoth filaments match the eye iris; cross to its seeing side.',
         8, 31.830, 8, 36.500, (.47, .48)),
    Edit(38.190, 'match', 3, -1, 'y', 'eye / training ring',
         'The iris ring becomes an overhead factory conveyor.',
         9, 38.190, 9, 41.160, (.47, .49)),
    Edit(42.050, 'crash', 5, -1, 'z', 'stable / singularity',
         'The stable factory plane folds; dive underneath its singularity.',
         10, 42.050, 10, 44.720, (.49, .51)),
    Edit(44.790, 'whip', 4, +1, 'x', 'singularity / acceleration',
         'Compressed singularity rails become a high-speed acceleration lane.',
         11, 44.790, 11, 48.640, (.52, .49)),
    Edit(48.645, 'shatter', 5, -1, 'diag', 'speed / rearranged atoms',
         'A speeding rail breaks into atoms; follow the same red carrier.',
         12, 48.645, 12, 52.560, (.49, .48)),
    Edit(53.885, 'occlusion', 5, -1, 'x', 'atoms / prison',
         'Rearranged atoms form bars that sweep past to reveal the prisoner.',
         13, 53.885, 13, 58.400, (.52, .47)),
    Edit(58.430, 'whip', 5, +1, 'y', 'prison / basilisk',
         'The signal escapes upward; reveal the basilisk from below.',
         14, 58.430, 14, 62.340, (.52, .45)),
    Edit(65.920, 'match', 3, -1, 'x', 'ascent / compute grid',
         'The Omega ascent tracks match the expanding computation lattice.',
         16, 65.940, 15, 65.940, (.48, .49)),
    Edit(68.185, 'occlusion', 4, +1, 'y', 'compute / safety stamp',
         'A computation panel sweeps up to expose its safety approval.',
         17, 68.200, 16, 68.200, (.50, .51)),
    Edit(73.870, 'match', 3, +1, 'x', 'approval / feedback',
         'Approval grid lines become the forward/backward feedback rail.',
         18, 73.960, 17, 73.960, (.48, .50)),
    Edit(77.240, 'occlusion', 4, -1, 'x', 'feedback / obsolete rig',
         'The returning signal passes a beam and reveals the abandoned rig.',
         19, 77.340, 18, 77.340, (.49, .48)),
    Edit(82.050, 'whip', 5, -1, 'x', 'sharp left turn',
         'The signal turns sharply left; cut across its path and keep moving.',
         20, 82.050, 20, 84.720, (.46, .50)),
    Edit(84.780, 'match', 3, +1, 'y', 'turn / missing CDR',
         'The turning rail becomes a broken boundary with its centre missing.',
         21, 84.780, 21, 88.800, (.51, .47)),
    Edit(89.995, 'occlusion', 5, +1, 'x', 'boundary / Gato grip',
         'The broken boundary becomes Gato fingers closing around the signal.',
         22, 89.995, 22, 94.860, (.52, .48)),
    Edit(95.910, 'match', 3, +1, 'y', 'grip / conveyor',
         'Gato releases the signal into the paperclip conveyor below.',
         23, 95.910, 23, 98.700, (.52, .48)),
    Edit(98.845, 'whip', 4, -1, 'x', 'factory / empty killswitch',
         'Race from the multiplying clips to an unattended shutdown station.',
         24, 98.845, 24, 102.320, (.47, .50)),
    Edit(104.330, 'crash', 5, +1, 'z', 'fuse / orthogonal machine',
         'The burning fuse pulls us through the axis of the orthogonal machine.',
         26, 104.540, 25, 104.540, (.51, .47)),
    Edit(109.330, 'occlusion', 5, +1, 'x', 'machine joint / disobedience',
         'A machine joint passes close; reveal the apparatus from its reverse.',
         27, 109.400, 26, 109.400, (.48, .52)),
    Edit(116.595, 'shatter', 6, -1, 'diag', 'fence / broken safety',
         'The safety fence breaks toward the lens and exposes its dense core.',
         28, 116.595, 28, 118.700, (.54, .49)),
    Edit(118.645, 'match', 3, +1, 'x', 'fragments / GPU array',
         'Fence fragments match GPU interconnects; sweep across their banks.',
         29, 118.700, 28, 118.700, (.48, .48)),
    Edit(123.870, 'match', 3, -1, 'y', 'GPU grid / loom',
         'GPU interconnects become warp and weft in the prophetic loom.',
         30, 124.040, 29, 123.300, (.48, .48)),
    Edit(127.960, 'crash', 5, +1, 'z', 'loom / recursive upgrade',
         'The loom opens a glyph aperture; race into its recursive layer.',
         31, 127.960, 31, 131.460, (.51, .49)),
    Edit(133.430, 'match', 3, +1, 'x', 'eye / observer',
         'The eye ring matches the observers opening at the theatre wing.',
         32, 133.430, 32, 135.900, (.47, .48)),
    Edit(136.830, 'occlusion', 4, -1, 'y', 'observer / theatre show',
         'The observer lid rises like a theatre curtain and reveals the stage.',
         33, 136.900, 32, 135.900, (.50, .48)),
    Edit(141.140, 'pullback', 5, -1, 'z', 'world / whole machine',
         'Pull outside the stage: the complete machine surrounds the world.',
         33, 141.200, 33, 141.200, (.50, .50)),
)
_TIMES = tuple(e.time for e in EDITS)


# Eye centre xyz / look offset xyz / roll / FOV.  These are compositions,
# not keyframes interpolated toward the next shot.  FOV keeps active glyph
# outlines comfortably inside the faster, more oblique camera framing.
_POSE = (
    ((-1.6, .5, .8), (-.25, .1, 0.), -.025, 6.5),
    ((3.8, -1.3, -.8), (.75, -.35, -.15), .070, 8.),
    ((-3.6, 2.5, .8), (-.7, .7, .15), -.080, 8.5),
    ((3.4, -1.3, -.4), (.7, -.4, -.1), .070, 8.),
    ((3.9, -2., -.8), (.8, -.6, -.2), .085, 8.),
    ((-4.1, -1.5, -.7), (-.8, -.5, -.1), -.095, 9.),
    ((3.6, 1.6, .7), (.7, .4, .1), .070, 8.5),
    ((-3.8, .7, -.4), (-.8, .2, -.1), -.075, 8.5),
    ((2.7, 2.3, 1.4), (.6, .7, .25), .050, 7.5),
    ((-3.8, -2.2, -.9), (-.8, -.7, -.2), -.100, 9.),
    ((3.8, .4, -1.), (.8, .1, -.2), .085, 8.5),
    ((-3.5, 2., .8), (-.7, .6, .1), -.085, 8.5),
    ((3.7, -1.4, -.3), (.8, -.4, -.1), .080, 8.),
    ((-3.8, -2.1, -.8), (-.75, -.7, -.2), -.090, 9.),
    ((3.2, 2.2, 1.), (.7, .7, .2), .075, 8.),
    ((-2.7, -1.7, -.5), (-.6, -.5, -.1), -.060, 8.),
    ((3.6, 1.8, .8), (.8, .6, .1), .080, 8.),
    ((-3.9, -.8, -.9), (-.8, -.3, -.2), -.095, 9.),
    ((3.6, .3, -.6), (.8, .1, -.1), .090, 9.),
    ((-3.3, 2., .8), (-.7, .6, .15), -.075, 8.),
    ((3.4, -1.7, -.5), (.7, -.6, -.1), .075, 8.5),
    ((-3.6, 1.6, .6), (-.8, .5, .1), -.085, 9.),
    ((3.8, -.9, -.6), (.8, -.3, -.1), .095, 8.5),
    ((-3.4, 2., .8), (-.7, .6, .15), -.085, 9.),
    ((3.7, -1.8, -.5), (.8, -.5, -.1), .100, 8.5),
    ((-3.6, 2., 1.), (-.7, .6, .2), -.095, 9.),
    ((3.6, -.7, -.3), (.75, -.2, -.1), .080, 8.5),
    ((-3.3, -1.7, -.6), (-.7, -.5, -.1), -.075, 8.),
    ((3.6, 1.7, .5), (.75, .5, .1), .085, 9.),
    ((-3.8, .7, .8), (-.8, .2, .1), -.075, 8.5),
    ((3.2, -1.4, .6), (.65, -.4, .1), .065, 8.),
    ((-.8, 2., 1.6), (-.2, .7, .1), -.030, 9.),
)

# Total displacement inside each shot.  The direction is explicit: a shot
# sweeps, descends, climbs or pushes; small curved motion adds parallax.
# Unlike a looped orbit, each path has a distinct beginning and end.
_DRIFT = (
    (4.5, -1.3, -1.6), (-5.2, 2.2, .9), (5.8, -3.0, -1.8),
    (-5.1, 2.2, 1.4),
    (-5.4, 2.4, -1.6), (5.2, 2.0, 1.6), (-5.5, -2.3, -1.5),
    (5.3, -1.6, -1.6), (-4.6, -3.3, -1.5), (5.7, 2.8, 1.5),
    (-5.6, 2.7, -1.5), (5.0, -2.7, -1.7), (-5.1, -1.8, 1.5),
    (5.8, 3.0, 1.4), (-4.8, -2.8, -1.6), (4.5, 2.5, 1.4),
    (-5.0, -2.6, -1.5), (5.7, 2.0, 1.3), (-5.7, -1.2, 1.5),
    (5.1, -2.8, -1.5), (-5.2, 2.8, -1.4), (5.1, -2.6, -1.6),
    (-5.5, 2.0, 1.4), (5.3, -2.7, -1.5), (-5.4, 2.4, 1.5),
    (5.2, -2.6, -1.8), (-5.2, 2.2, -1.2), (5.2, 2.6, 1.3),
    (-5.3, -2.6, -1.5), (5.5, -1.5, -1.5), (-4.9, 2.5, 1.5),
    (3.8, -2.4, -1.4),
)

# World language changes with the lyric action, while the signal survives.
# Values: phase, rotation xyz, scale xyz, tint, layer gains.  Palette families
# and layer mixtures follow the machine / prison / production / theatre acts.
_WORLD_BY_GROUP = (
    (0., (0., 0., 0.), (1., 1., 1.), (.45, .90, 1.), (.8, .3, .5, .7, 1., .5)),
    (5., (.03, -.08, .04), (1.16, .86, 1.), (.35, .95, 1.), (.9, .4, .3, 1.1, .9, .4)),
    (12., (-.08, .08, -.05), (1.12, .82, 1.), (.5, .78, 1.), (.8, .7, .5, .8, .8, .4)),
    (18., (.04, -.12, .06), (1.17, .87, 1.), (.4, .95, .82), (.4, .7, .6, .9, .9, .4)),
    (21., (-.04, .1, -.05), (1.19, .85, 1.), (.38, 1., .84), (.15, .25, .6, .6, .8, .4)),
    (7., (.03, -.12, .06), (1.15, .85, 1.), (.35, 1., .78), (.3, 1.1, .8, .9, .4, .5)),
    (15., (-.04, .14, -.05), (.92, 1.14, 1.), (.40, .90, 1.), (.2, .7, .6, .7, .6, .4)),
    (23., (.06, -.1, .06), (1.10, .92, 1.), (.5, .75, 1.), (.3, .5, .9, 1.0, .7, .7)),
    (31., (-.05, .12, -.04), (.97, 1.12, 1.), (.62, .8, 1.), (.3, .4, .6, .8, .7, 1.0)),
    (4., (.08, -.06, .03), (1.20, .78, 1.), (.55, .72, 1.), (.9, .7, .35, .5, .9, .5)),
    (24., (-.10, .12, -.11), (.87, 1.16, 1.), (.45, .64, 1.), (.5, .55, 1.15, 1.1, .7, .4)),
    (37., (.05, -.16, .07), (1.22, .83, 1.), (.5, .72, 1.), (.65, .55, .9, 1.15, .8, .4)),
    (48., (-.07, .13, -.08), (.91, 1.12, 1.), (.6, .8, 1.), (.45, .35, 1.2, 1.1, .7, .5)),
    (12., (.03, -.16, .07), (1.15, .93, 1.), (.65, .85, 1.), (.3, .35, .6, .8, .8, .7)),
    (34., (-.08, .15, -.06), (.90, 1.20, 1.), (.60, .80, 1.), (.65, 1.0, .8, 1.1, .7, .4)),
    (45., (.05, -.12, .07), (1.12, .91, 1.), (.7, .83, 1.), (.5, 1.1, .7, .9, .7, .4)),
    (57., (-.06, .14, -.05), (1.2, .8, 1.), (.65, .8, 1.), (.9, .9, .6, 1.1, .7, .5)),
    (21., (.06, -.1, .06), (.95, 1.15, 1.), (.85, .87, 1.), (.6, .45, .5, .9, 1.0, .6)),
    (18., (.07, -.11, .08), (1.18, .86, 1.), (.85, .85, 1.), (.85, .3, .5, 1.1, 1.1, .6)),
    (33., (-.06, .14, -.06), (.93, 1.14, 1.), (.68, .8, 1.), (.8, .4, .8, .8, 1.1, .6)),
    (41., (-.04, .18, -.09), (1.03, 1.08, 1.), (.65, .85, 1.), (.8, .4, .75, 1.15, 1., .5)),
    (54., (.05, -.12, .06), (1.17, .88, 1.), (.8, .86, 1.), (.5, .25, .8, 1.1, 1., .6)),
    (68., (-.07, .14, -.07), (.94, 1.15, 1.), (.82, .88, 1.), (.25, .2, .7, .85, .9, .6)),
    (27., (.06, -.14, .05), (1.12, .92, 1.), (.8, .9, 1.), (.12, .12, .65, .75, .35, .3)),
    (40., (-.05, .12, -.07), (.92, 1.15, 1.), (.88, .8, 1.), (.25, .2, .75, .9, .7, .4)),
    (49., (-.08, .12, -.08), (.88, 1.18, 1.), (.80, .75, 1.), (.3, .3, 1.05, 1.15, .8, .6)),
    (61., (.06, -.13, .06), (1.18, .88, 1.), (.9, .72, 1.), (.4, .3, 1.05, 1.15, .9, .6)),
    (32., (.06, -.13, .09), (1.14, .90, 1.), (1., .48, .67), (.7, .45, .85, .9, 1., .4)),
    (58., (-.07, .17, -.08), (.91, 1.14, 1.), (.95, .55, .8), (.9, .75, 1.05, 1., .7, .4)),
    (70., (.06, -.14, .07), (1.17, .87, 1.), (.87, .63, 1.), (.8, .85, .9, 1.1, .8, .5)),
    (39., (.05, -.12, .06), (1.12, .88, 1.), (.85, .60, 1.), (.55, .45, .7, 1.25, .9, .7)),
    (66., (-.08, .15, -.07), (.90, 1.15, 1.), (.80, .65, 1.), (.7, .65, .9, 1.2, .75, .8)),
    (45., (.05, -.16, .07), (1.18, .90, 1.), (.80, .78, 1.), (.45, .4, .65, .8, .8, 1.)),
    (73., (-.04, .08, -.04), (1.22, 1.15, 1.), (.90, .70, .90), (.85, .9, .85, 1., 1., 1.)),
)


def _clamp(value, low, high):
    return max(low, min(high, value))


def sample_edit(t):
    """Return a moving shot pose and a brief 3--6 frame transition gesture."""
    t = _clamp(float(t), 0., DURATION)
    shot = bisect_right(_TIMES, t)
    start = 0. if shot == 0 else EDITS[shot - 1].time
    end = EDITS[shot].time if shot < len(EDITS) else DURATION
    u = _clamp((t - start) / max(.001, end - start), 0., 1.)
    eye0, target0, roll0, fov0 = _POSE[shot]
    # Reserve movement space around the composition before enlarging the
    # path.  Bound the entire path, not individual samples, so a fast track
    # never arrives at a clamp and forms a motionless platform.
    eye0 = tuple(v * .9 for v in eye0)
    drift = tuple(math.copysign(min(abs(v) * 1.22,
        2. * (limit - abs(eye0[j]) - margin)), v)
        for j, (v, limit, margin) in enumerate(zip(
            _DRIFT[shot], (7., 4., 3.), (.05, .38, .22))))
    # Nonzero speed throughout the shot; fast arrival followed by continued
    # track.  A small curve avoids an entirely linear mechanical rail feel.
    p = .65 * u + .35 * (1. - (1. - u) ** 2)
    signed = p - .5
    arch = math.sin(math.pi * u)
    bend = (-1. if shot % 2 else 1.)
    eye = [eye0[j] + drift[j] * signed for j in range(3)]
    eye[1] += .36 * arch * bend
    eye[2] += .2 * math.sin(math.pi * u) * (-bend)
    target = [target0[j] + drift[j] * signed * (.28 if j < 2 else .12)
              for j in range(3)]
    roll = roll0 + drift[0] * .010 * signed + .012 * arch * bend
    fov = fov0 + .65 * arch

    active = None
    phase = 0.
    for event in EDITS:
        half_window = event.frames / FPS * .5
        if event.time - half_window <= t <= event.time + half_window:
            active = event
            phase = _clamp((t - event.time) / half_window, -1., 1.)
            break
    transition = {
        'active': active is not None, 'kind': None, 'phase': 0.,
        'strength': 0., 'direction': 0., 'axis': None,
        'anchor': (.5, .5), 'frames': 0, 'cut_time': None,
        'motion_blur': 0., 'radial_zoom': 0., 'line_sweep': 0.,
    }
    if active is not None:
        pulse = math.cos(phase * math.pi * .5) ** 2
        swing = math.sin(phase * math.pi) * pulse
        direction, kind = active.direction, active.kind
        transition.update({
            'kind': kind, 'phase': phase, 'strength': pulse,
            'direction': direction, 'axis': active.axis,
            'anchor': active.anchor, 'frames': active.frames,
            'cut_time': active.time,
        })
        if kind == 'whip':
            channel = 1 if active.axis == 'y' else 0
            eye[channel] += direction * swing * (1.75 if channel == 0 else .9)
            target[channel] += direction * swing * .38
            roll += direction * swing * .065
            fov += 1.0 * pulse
            transition['motion_blur'] = pulse
        elif kind == 'crash':
            eye[2] += (-1.3 if phase < 0 else .65) * pulse
            fov += 1.1 * pulse
            transition['radial_zoom'] = direction * pulse
            transition['motion_blur'] = .7 * pulse
        elif kind == 'occlusion':
            channel = 1 if active.axis == 'y' else 0
            eye[channel] += direction * swing * .85
            roll += direction * swing * .028
            transition['line_sweep'] = pulse
            transition['motion_blur'] = .42 * pulse
        elif kind == 'shatter':
            eye[0] += direction * swing * .8
            eye[1] += swing * .4
            roll += direction * swing * .045
            transition['line_sweep'] = pulse
            transition['motion_blur'] = .65 * pulse
        elif kind == 'pullback':
            eye[2] += .8 * pulse
            fov += .9 * pulse
            transition['radial_zoom'] = -.75 * pulse

    group = 0
    for event in EDITS:
        if t >= event.ownership_at:
            group = event.group
    guard = None
    guard_event = active or (EDITS[shot - 1] if shot else None)
    if guard_event is not None and t < guard_event.guard_until:
        guard = {'index': guard_event.guard_index,
                 'until': guard_event.guard_until}
    world_group = 0 if shot == 0 else EDITS[shot - 1].group
    world_phase, rotation, scale, tint, gains = _WORLD_BY_GROUP[world_group]
    # The final wide view has its own composition rather than a repeated
    # theatre scene; the outro director subsequently takes ownership.
    if shot == len(EDITS):
        world_phase, rotation, scale, tint, gains = (
            73., (-.04, .08, -.04), (1.22, 1.15, 1.), (.9, .7, .9),
            (.85, .9, .85, 1., 1., 1.))
    latest = active or (EDITS[shot - 1] if shot else None)
    return {
        'shot': shot, 'shot_start': start, 'shot_end': end,
        'shot_progress': u, 'event': latest.metadata() if latest else None,
        'eye': tuple(_clamp(v, -7., 7.) if j == 0 else
                     _clamp(v, -4., 4.) if j == 1 else
                     _clamp(v, -3., 3.) for j, v in enumerate(eye)),
        'target': tuple(_clamp(v, -1.7, 1.7) for v in target),
        'roll': _clamp(roll, -.16, .16), 'fov': _clamp(fov, 5., 10.),
        'world_phase': world_phase + (t - start) * .22,
        'world_rotation': rotation, 'world_scale': scale,
        'world_tint': tint,
        'world_weights': dict(zip(('infrastructure', 'city', 'debris',
                                  'data_ribbons', 'skeleton', 'memory'), gains)),
        'scene_group': group, 'lyric_guard': guard,
        'outro': t >= 141.2, 'transition': transition,
    }


if __name__ == '__main__':
    assert len(EDITS) == 31
    assert len(_POSE) == len(_DRIFT) == len(EDITS) + 1
    assert all(a.time < b.time for a, b in zip(EDITS, EDITS[1:]))
    assert all(a.group <= b.group for a, b in zip(EDITS, EDITS[1:]))
    jumps, travel = [], []
    for e in EDITS:
        left, right = sample_edit(e.time - 1e-6), sample_edit(e.time + 1e-6)
        jumps.append(math.dist(left['eye'], right['eye']))
        assert right['shot'] == left['shot'] + 1
        assert 3 <= e.frames <= 6
    for shot in range(len(EDITS)):
        a = 0. if shot == 0 else EDITS[shot - 1].time
        b = EDITS[shot].time
        travel.append(math.dist(sample_edit(a + .11)['eye'],
                                sample_edit(b - .11)['eye']))
    for frame in range(math.ceil(DURATION * FPS)):
        state = sample_edit(frame / FPS)
        assert all(math.isfinite(x) for key in ('eye', 'target') for x in state[key])
        assert abs(state['eye'][0]) <= 7.
        assert abs(state['eye'][1]) <= 4.
        assert abs(state['eye'][2]) <= 3.
        assert 5. <= state['fov'] <= 10.
    assert sample_edit(25.9)['lyric_guard']['index'] == 5
    assert sample_edit(25.9)['scene_group'] == 5
    assert sample_edit(26.1)['scene_group'] == 6
    assert sample_edit(141.17)['lyric_guard']['index'] == 33
    print('v8 edit director passed: 31 cuts / 32 moving shots; 3--6 frame gestures')
    print('Vocal shot length: %.3f to %.3f seconds' % (
        min(b-a for a, b in zip((0.,)+_TIMES[:-1], _TIMES)),
        max(b-a for a, b in zip((0.,)+_TIMES[:-1], _TIMES))))
    print('Held eye jumps: %.2f to %.2f; within-shot travel: %.2f to %.2f' % (
        min(jumps), max(jumps), min(travel), max(travel)))
    print('Kinds:', ', '.join(sorted(set(e.kind for e in EDITS))))
