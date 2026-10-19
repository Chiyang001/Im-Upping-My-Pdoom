"""A beat-edited epilogue for the all-line MV (no renderer dependencies).

The 30 main attacks below are measured attacks from rhythm_v3, not a fresh
regular grid.  Each advances one consequence of the same escaping signal:
replication -> planetary capture -> collapse -> the closed infinity loop.

``sample_outro(t)`` returns ordinary Python scalars, tuples, and dictionaries.
The ``eye``/``target`` values are offsets from a neutral eye=(0,0,28),
target=(0,0,0); ``camera_eye``/``camera_target`` are their absolute equivalents.
Do not add both.  FOV is absolute degrees; rotations are radians.  The final
camera, geometry clock, and action values stop at FREEZE_TIME.  Keep the
credit visible and the image fixed through the end; do not fade it away.

Render ``motif`` as the current action, with ``motif_progress`` as its local
0..1 motion.  Retain the signal and established network across these cuts.
``stage`` 0..3 selects the broad geometry family; each beat's named motif is
an action within it, not a replacement of the whole story with random art.
``pulse`` is the main attack; ``secondary`` is a smaller subdivision attack.
Only actual shot changes have a transition packet.  Avoid full-frame flashes
on every beat: ``blast`` has deliberate peaks and the rest use local motion.
"""

from bisect import bisect_right
from dataclasses import dataclass
import math


START = 141.2
FREEZE_TIME = 154.6
DURATION = 156.667
CREDIT = "Made by Chiyang001"

# First attack launches in the last SHOW cut; the remaining attacks belong to
# the instrumental ending.  The tail after 154.6 has no meaningful main beat.
OUTRO_BEATS = (
    141.140, 141.595, 142.050, 142.505, 142.960, 143.415,
    143.870, 144.320, 144.775, 145.230, 145.685, 146.140,
    146.595, 147.060, 147.505, 147.970, 148.415, 148.880,
    149.320, 149.775, 150.230, 150.700, 151.140, 151.595,
    152.050, 152.505, 152.960, 153.415, 153.870, 154.325,
)
_STRENGTHS = (
    1., .7258, 1., .7699, .9904, .7126, 1., .9183, 1., .9193,
    1., .8402, 1., .9529, 1., .8842, 1., .9087, 1., .7736,
    1., .9487, 1., .8115, 1., .7302, .4301, .409, .4036, .4019,
)
# Measured subdivisions. They tug only a local thread, latch, fragment or
# graph packet, leaving the main visual meter legible.
_SUB_HITS = (
    142.735, 145.000, 145.915, 146.370, 147.730, 151.370,
)


@dataclass(frozen=True)
class BeatAction:
    stage: int
    motif: str
    story: str
    tension: float
    blast: float = 0.0
    direction: float = 1.0


ACTIONS = (
    BeatAction(0, "escape", "The red witness tears free of the theatre.", .25, .75),
    BeatAction(0, "wake", "The escaping point leaves a bright physical wake.", .35, .0, -1),
    BeatAction(0, "bifurcate", "Its wake forks into two conductive branches.", .45, .25),
    BeatAction(0, "lock", "Both branches snap onto the same machine rhythm.", .65, .0, -1),
    BeatAction(0, "replicate", "The first packet copies into a bank of nodes.", .45, .8),
    BeatAction(0, "cascade", "Replication races across adjacent node banks.", .6, .0, -1),
    BeatAction(0, "spine", "The banks connect into one growing nervous spine.", .7, .35),
    BeatAction(0, "network", "The spine opens out into the whole machine.", .85, .0, -1),
    BeatAction(1, "world_reveal", "Pull back: the machine is wrapped around a world.", .45, 1.),
    BeatAction(1, "orbit_clamp", "One orbital jaw closes around its equator.", .65, .0, -1),
    BeatAction(1, "meridian", "A second cage closes through the poles.", .8, .35),
    BeatAction(1, "eye_gate", "The opening eye aligns with the captive world.", .95, .0, -1),
    BeatAction(1, "seize", "The jaws seize; the world and network share one pulse.", 1., 1.),
    BeatAction(1, "world_plates", "The surface separates into wired plates.", .8, .0, -1),
    BeatAction(1, "feed", "Those plates are pulled toward the machine throat.", .95, .35),
    BeatAction(1, "sever", "The last independent route snaps under load.", 1., .65, -1),
    BeatAction(2, "buckle", "The overloaded structure buckles inward.", 1., .8),
    BeatAction(2, "bundle", "Every remaining strand stretches toward the core.", 1., .0, -1),
    BeatAction(2, "implode", "The tense core implodes into one red point.", 1., 1.),
    BeatAction(2, "fracture", "Its shell breaks and ejects the stored energy.", .85, .85, -1),
    BeatAction(2, "aftershock", "A shard wave carries the same signal outward.", .7, .75),
    BeatAction(2, "invert", "The wave folds the machine grid back on itself.", .8, .0, -1),
    BeatAction(2, "recursive", "The folded grid nests inside another copy.", .95, .6),
    BeatAction(2, "pinch", "All copies pinch into the crossing of a loop.", 1., .0, -1),
    BeatAction(3, "infinity_trace", "The red point draws the two infinity lobes.", .65, .8),
    BeatAction(3, "infinity_clasp", "The lobes lock around the surviving network.", .8, .0, -1),
    BeatAction(3, "return", "The witness returns to its starting point.", .5, .35),
    BeatAction(3, "settle", "Its wake becomes the last permanent contour.", .3, .0, -1),
    BeatAction(3, "engrave", "A final pullback exposes the maker's engraving.", .15),
    BeatAction(3, "seal", "The engraving and infinite machine seal into one held frame.", .0, .25, -1),
)


@dataclass(frozen=True)
class Shot:
    beat: int
    eye: tuple
    target: tuple
    drift: tuple
    roll: float
    fov: float
    kind: str
    frames: int
    axis: str
    direction: float


# Actual cuts retain their new viewpoint. There is no return to an orbiting
# centre stage after the fast transition gesture has finished.
SHOTS = (
    Shot(0, (+7., -4., -4.), (+1., -.6, -2.), (-3., +1., -3.), -.09, 65., "pullback", 5, "z", -1),
    Shot(4, (-10., +3., -5.), (-1.5, +.6, -3.), (+4., -2., +2.), +.12, 67., "whip", 4, "x", 1),
    Shot(8, (+4., +10., +12.), (0., +1., -3.), (-4., -3., +5.), -.045, 62., "match", 3, "y", -1),
    Shot(12, (-9., -6., -4.), (-1., -1., -2.), (+3., +2., -2.), +.10, 69., "crash", 5, "z", 1),
    Shot(16, (+10., +5., -2.), (+1., +.5, -3.), (-5., -3., -4.), -.12, 68., "occlusion", 4, "x", -1),
    Shot(20, (-5., +8., +5.), (-.5, +1., -2.), (+4., -4., +5.), +.07, 72., "shatter", 5, "diag", 1),
    Shot(24, (+7., -2., +7.), (+.5, 0., -1.), (-4., +2., -1.), -.055, 61., "match", 3, "x", -1),
    Shot(26, (-5., +3., +4.), (-.5, +.2, -.5), (+3., -2., +1.), +.035, 60., "whip", 4, "y", 1),
    Shot(28, (0., +1., +7.), (0., 0., 0.), (0., 0., 0.), 0., 58., "pullback", 4, "z", -1),
)
_SHOT_TIMES = tuple(OUTRO_BEATS[s.beat] for s in SHOTS)
STAGE_NAMES = ("signal becomes machine", "machine captures world", "machine collapses", "infinite return")


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _ease(x):
    x = _clamp(x)
    return x * x * (3.0 - 2.0 * x)


def _ramp(t, start, end):
    return _ease((t - start) / (end - start))


def sample_outro(t):
    """Return the timed epilogue state. Safe to call outside the outro too.

    ``freeze`` is the renderer instruction to hold *all* geometry/camera/post
    clocks, not just the lettering. ``render_time`` is the correct frozen
    clock. ``credit_reveal`` reaches 1 before freeze and remains exactly 1.
    An optional ``transition`` packet shares v6's kind/phase/strength fields.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError("outro time must be finite")
    active = t >= START
    frozen = t >= FREEZE_TIME
    q = min(FREEZE_TIME, max(START, t))
    k = max(0, min(len(OUTRO_BEATS) - 1, bisect_right(OUTRO_BEATS, q) - 1))
    bt = OUTRO_BEATS[k]
    next_bt = OUTRO_BEATS[k + 1] if k + 1 < len(OUTRO_BEATS) else FREEZE_TIME
    elapsed = max(0., q - bt)
    phase = _clamp(elapsed / max(.001, next_bt - bt))
    beat = ACTIONS[k]
    pulse = _STRENGTHS[k] * math.exp(-elapsed / .105)
    sub_index = bisect_right(_SUB_HITS, q) - 1
    secondary = (math.exp(-(q - _SUB_HITS[sub_index]) / .055)
                 if sub_index >= 0 else 0.)
    anticipation = _clamp(1. - (next_bt - q) / .085) ** 2
    shot_index = max(0, bisect_right(_SHOT_TIMES, q) - 1)
    shot = SHOTS[shot_index]
    shot_start = _SHOT_TIMES[shot_index]
    shot_end = _SHOT_TIMES[shot_index + 1] if shot_index + 1 < len(SHOTS) else FREEZE_TIME
    shot_phase = _clamp((q - shot_start) / max(.001, shot_end - shot_start))
    # Smooth motion *inside* a shot, intentionally discontinuous across a cut.
    eye = tuple(a + b * shot_phase for a, b in zip(shot.eye, shot.drift))
    target = tuple(shot.target)
    roll = shot.roll * (1. - .25 * shot_phase)
    trans_duration = shot.frames / 30.
    trans_phase = _clamp((q - shot_start) / trans_duration)
    trans_on = active and 0. <= q - shot_start < trans_duration and not frozen
    transition = {
        "active": trans_on, "kind": shot.kind if trans_on else "none",
        "phase": trans_phase, "strength": math.sin(math.pi * trans_phase) if trans_on else 0.,
        "frames": shot.frames, "axis": shot.axis,
        "direction": shot.direction, "anchor": (.5, .5),
    }
    # Causal cumulative states: the same graph survives every camera cut.
    network = _ramp(q, 141.14, 144.32)
    capture = _ramp(q, 144.775, 147.97)
    collapse = _ramp(q, 148.415, 150.23)
    recursion = _ramp(q, 150.23, 152.05)
    infinity = _ramp(q, 152.05, 153.415)
    credit = _ramp(q, 154.325, FREEZE_TIME)
    # World hierarchy changes by chapter rather than retaining a generic
    # corridor. Values key directly into v6's persistent-world layer names.
    weights = (
        (.55, .35, .2, .8, .45, .25),
        (.25, .85, .25, .45, .8, .55),
        (.12, .12, .9, .5, .35, .2),
        (.06, .08, .18, .25, .15, .28),
    )[beat.stage]
    tint = ((.28, 1., .82), (1., .42, .22), (1., .2, .38), (.68, .88, 1.))[beat.stage]
    if frozen:
        pulse = secondary = anticipation = 0.
    return {
        "active": active, "freeze": frozen, "render_time": q,
        "freeze_time": FREEZE_TIME, "credit": CREDIT,
        "credit_reveal": credit, "credit_gain": 1.15 * credit,
        "beat_index": k, "beat_time": bt, "beat_elapsed": elapsed,
        "beat_phase": phase, "beat_strength": _STRENGTHS[k],
        "next_beat": next_bt, "pulse": pulse, "secondary": .45 * secondary,
        "anticipation": anticipation, "stage": beat.stage,
        "stage_name": STAGE_NAMES[beat.stage], "motif": beat.motif,
        "story": beat.story, "motif_progress": _ease(phase),
        "direction": beat.direction,
        "tension": beat.tension * (.55 + .45 * anticipation),
        "blast": beat.blast * pulse,
        "shot": shot_index, "shot_start": shot_start,
        "shot_progress": shot_phase, "transition": transition,
        "eye": eye, "target": target, "roll": roll, "fov": shot.fov,
        "camera_eye": (eye[0], eye[1], 28. + eye[2]),
        "camera_target": target,
        "world_weights": dict(zip(("infrastructure", "city", "debris", "data_ribbons", "skeleton", "memory"), weights)),
        "world_tint": tint,
        "world_rotation": (0., (0., .35, -.45, .1)[beat.stage], 0.),
        "world_scale": ((1., 1., 1.), (1.15, 1.15, 1.), (.8, .8, 1.25), (1., 1., 1.))[beat.stage],
        "network_growth": network, "world_capture": capture,
        "collapse": collapse, "recursion": recursion, "infinity": infinity,
        "network_reveal": _clamp((k + phase) / 7.),
        "world_phase": 250. + (q - START) * 2.2,
    }


if __name__ == "__main__":
    assert len(ACTIONS) == len(OUTRO_BEATS) == len(_STRENGTHS) == 30
    assert len({x.motif for x in ACTIONS}) == 30
    assert all(a < b for a, b in zip(OUTRO_BEATS, OUTRO_BEATS[1:]))
    assert max(b-a for a, b in zip(OUTRO_BEATS, OUTRO_BEATS[1:])) < .47
    assert len(SHOTS) == 9 and all(3 <= s.frames <= 5 for s in SHOTS)
    for i, t in enumerate(OUTRO_BEATS):
        x = sample_outro(max(START, t))
        assert x['beat_index'] == i
    for frame in range(math.ceil(DURATION * 30)):
        x = sample_outro(frame / 30.)
        assert all(math.isfinite(v) for key in ('camera_eye', 'target') for v in x[key])
        assert 0 <= x['credit_reveal'] <= 1
        assert 0 <= x['blast'] <= 1
    # Holding only the glyph would leave a moving background. Test the whole
    # public state's animated channels throughout the held final frame.
    end = sample_outro(FREEZE_TIME)
    for t in (154.7, 155., 156., DURATION):
        state = sample_outro(t)
        for key in end:
            assert state[key] == end[key], (key, state[key], end[key])
    assert end['credit'] == "Made by Chiyang001" and end['credit_reveal'] == 1.
    print('outro director passed: 30 unique beat actions, 9 shots, measured subdivision accents')
    print('held ending:', FREEZE_TIME, 'to', DURATION, 'seconds;', CREDIT)
