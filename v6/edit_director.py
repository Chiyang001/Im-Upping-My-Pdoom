"""Beat-led editing for the line-drawn MV; independent of the renderer.

``sample_edit(t)`` augments the existing continuous camera.  It does not
replace musical time, lyric time, or the travelling red signal.  There are
sixteen real cuts: each begins a different held pose and a new local drift.
Only the 3--8 frames surrounding a cut contain a fast transition gesture.

All vector values are ordinary tuples.  Camera rotations are radians, FOV
offsets are degrees, world_phase is an additional world-travel distance.
World transforms belong to scenery, never to the sung glyphs or signal.
``scene_group`` is a suggested lower bound for scenery ownership.  A renderer
must always retain the currently sung lyric even during a cut.  In particular
FOOM owns the 25.685 cut until 26.06, and the final SHOW line owns 141.14.
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
    anchor: tuple = (0.5, 0.5)

    def metadata(self):
        return {
            "time": self.time, "kind": self.kind, "frames": self.frames,
            "direction": self.direction, "axis": self.axis,
            "label": self.label, "motive": self.motive,
            "group": self.group, "ownership_at": self.ownership_at,
            "guard_index": self.guard_index, "guard_until": self.guard_until,
            "anchor": self.anchor,
        }


# Values use measured attacks.  A cut can occur inside a phrase when the
# action itself motivates it; it never substitutes the next lyric early.
EDITS = (
    Edit(22.190, "occlusion", 6, +1, "x", "jaw / city",
         "Jaw crosses the lens; emerge below the machine city.",
         5, 22.200, 4, 22.200, (.53, .46)),
    Edit(25.685, "crash", 6, +1, "z", "FOOM / room",
         "FOOM expands the machine; pass through its opening into the room.",
         6, 26.060, 5, 26.060, (.51, .48)),
    Edit(38.190, "match", 3, -1, "y", "eye / training ring",
         "The eye ring becomes an overhead training conveyor.",
         9, 38.190, 9, 41.160, (.47, .49)),
    Edit(42.050, "crash", 7, -1, "z", "stable / singularity",
         "The stable plane collapses; cut underneath the singularity.",
         10, 42.050, 10, 44.720, (.49, .51)),
    Edit(53.885, "occlusion", 6, -1, "x", "atoms / prison",
         "Rearranged atom bars pass close to reveal the prison side.",
         13, 53.885, 13, 58.400, (.52, .47)),
    Edit(58.430, "whip", 7, +1, "y", "prison / basilisk",
         "The signal escapes upward; reveal the basilisk from below.",
         14, 58.430, 14, 62.340, (.52, .45)),
    Edit(73.870, "match", 3, +1, "x", "approval / feedback",
         "Approval grid lines match to the feedback rail.",
         18, 73.960, 17, 73.960, (.48, .50)),
    Edit(82.050, "whip", 6, -1, "x", "sharp left turn",
         "The red signal takes a sharp left; change viewpoint across its path.",
         20, 82.050, 20, 84.720, (.46, .50)),
    Edit(95.910, "match", 4, +1, "y", "grip / conveyor",
         "Gato releases the same signal into the paperclip conveyor.",
         23, 95.910, 23, 98.700, (.52, .48)),
    Edit(103.420, "crash", 6, +1, "z", "fuse / orthogonal machine",
         "Race along the burning fuse into the orthogonal machine.",
         25, 103.420, 25, 104.540, (.51, .47)),
    Edit(109.330, "occlusion", 6, +1, "x", "machine joint / disobedience",
         "A mechanical joint sweeps past; see the apparatus from its reverse.",
         27, 109.400, 26, 109.400, (.48, .52)),
    Edit(116.595, "shatter", 7, -1, "diag", "fence / GPU field",
         "The fence breaks across the lens and exposes the dense GPU field.",
         28, 116.595, 28, 118.700, (.54, .49)),
    Edit(123.870, "match", 4, -1, "y", "GPU grid / loom",
         "GPU interconnects match to the loom's warp and weft.",
         30, 124.040, 30, 127.900, (.48, .48)),
    Edit(129.325, "crash", 6, +1, "z", "recursive aperture",
         "Go through a glyph aperture into the next recursive layer.",
         31, 129.325, 31, 131.460, (.51, .49)),
    Edit(133.430, "match", 3, +1, "x", "eye / observer",
         "The eye ring matches the observer's opening at the theatre wing.",
         32, 133.430, 32, 135.900, (.47, .48)),
    Edit(141.140, "pullback", 5, -1, "z", "world / whole machine",
         "Cut back in scale to reveal the complete machine around the world.",
         32, 141.200, 33, 141.200, (.50, .50)),
)
_TIMES = tuple(e.time for e in EDITS)

# eye xyz, target xyz, roll, FOV.  Distinct post-cut poses are held until the
# next shot; there is no ease back to a single default stage or camera.
_POSE = (
    ((-1.2, +.5, +.6), (-.2, +.1, 0.), -.018, 4.0),
    ((+3.8, -2.0, -1.6), (+.7, -.7, -.4), +.095, 7.0),
    ((-3.2, +1.6, +.7), (-.6, +.4, +.2), -.070, 7.0),
    ((+2.1, +3.0, +1.8), (+.4, +1.0, +.3), +.035, 5.0),
    ((-4.1, -2.4, -1.5), (-.8, -.8, -.3), -.110, 8.0),
    ((+3.9, +1.5, +.5), (+.8, +.3, +.1), +.080, 6.0),
    ((-3.8, -2.2, -1.1), (-.7, -.7, -.2), -.095, 8.0),
    ((+3.5, +2.2, +1.0), (+.7, +.7, +.2), +.080, 6.0),
    ((-4.5, +.1, -1.2), (-.9, +.1, -.2), -.120, 8.0),
    ((+3.5, -2.2, -.8), (+.6, -.8, -.1), +.070, 7.0),
    ((-3.8, +2.0, +1.3), (-.8, +.6, +.2), -.090, 8.0),
    ((+3.8, -1.7, -.6), (+.8, -.5, -.1), +.110, 7.0),
    ((-3.5, +2.4, +1.4), (-.7, +.7, +.2), -.105, 8.0),
    ((+3.0, -2.1, -.9), (+.7, -.7, -.1), +.075, 6.0),
    ((-3.5, +1.8, +.8), (-.7, +.6, +.1), -.095, 8.0),
    ((+4.3, +.8, +1.3), (+.9, +.4, +.2), +.065, 6.0),
    ((-.9, +2.5, +2.1), (-.2, +.8, +.1), -.030, 8.0),
)

# Local movement is deliberately unequal: side track, descend, climb, cross,
# and reveal.  The drift is not a slow interpolation to the following shot.
_DRIFT = (
    (+1.5, -.5, -.8), (-1.6, +.8, +.8), (+1.6, -1.1, -.7),
    (-1.6, -1.4, -.6), (+1.5, +1.2, +.7), (-1.4, -.8, -.7),
    (+1.6, +1.2, +.6), (-1.5, -1.2, -.9), (+1.8, +.8, +.8),
    (-1.4, +1.1, -.7), (+1.4, -.9, -.6), (-1.5, +.9, +.7),
    (+1.4, -1.1, -.8), (-1.5, +1.0, +.5), (+1.5, -.9, -.7),
    (-1.8, +.9, -.9), (+1.3, -1.4, -.6),
)

# phase, rotation xyz in radians, scale xyz, tint, semantic layer gains
# Layers: infrastructure, city, debris, data_ribbons, skeleton, memory.
_WORLD = (
    (0., (0., 0., 0.), (1., 1., 1.), (.45, .90, 1.), (.8, .3, .5, .7, 1., .5)),
    (7., (.03, -.12, .06), (1.15, .85, 1.), (.35, 1., .78), (.3, 1.1, .8, .9, .4, .5)),
    (15., (-.04, .14, -.05), (.92, 1.14, 1.), (.40, .90, 1.), (.2, .7, .6, .7, .6, .4)),
    (4., (.08, -.06, .03), (1.20, .78, 1.), (.55, .72, 1.), (.9, .7, .35, .5, .9, .5)),
    (24., (-.10, .12, -.11), (.87, 1.16, 1.), (.45, .64, 1.), (.5, .55, 1.15, 1.1, .7, .4)),
    (12., (.03, -.16, .07), (1.15, .93, 1.), (.65, .85, 1.), (.3, .35, .6, .8, .8, .7)),
    (34., (-.08, .15, -.06), (.90, 1.20, 1.), (.60, .80, 1.), (.65, 1.0, .8, 1.1, .7, .4)),
    (18., (.07, -.11, .08), (1.18, .86, 1.), (.85, .85, 1.), (.85, .3, .5, 1.1, 1.1, .6)),
    (41., (-.04, .18, -.09), (1.03, 1.08, 1.), (.65, .85, 1.), (.8, .4, .75, 1.15, 1., .5)),
    (27., (.06, -.14, .05), (1.12, .92, 1.), (.8, .9, 1.), (.12, .12, .65, .75, .35, .3)),
    (49., (-.08, .12, -.08), (.88, 1.18, 1.), (.80, .75, 1.), (.3, .3, 1.05, 1.15, .8, .6)),
    (32., (.06, -.13, .09), (1.14, .90, 1.), (1., .48, .67), (.7, .45, .85, .9, 1., .4)),
    (58., (-.07, .17, -.08), (.91, 1.14, 1.), (.95, .55, .8), (.9, .75, 1.05, 1., .7, .4)),
    (39., (.05, -.12, .06), (1.12, .88, 1.), (.85, .60, 1.), (.55, .45, .7, 1.25, .9, .7)),
    (66., (-.08, .15, -.07), (.90, 1.15, 1.), (.80, .65, 1.), (.7, .65, .9, 1.2, .75, .8)),
    (45., (.05, -.16, .07), (1.18, .90, 1.), (.80, .78, 1.), (.45, .4, .65, .8, .8, 1.)),
    (73., (-.04, .08, -.04), (1.22, 1.15, 1.), (.90, .70, .90), (.85, .9, .85, 1., 1., 1.)),
)


def _clamp(value, low, high):
    return max(low, min(high, value))


def sample_edit(t):
    """Return shot pose, scenery ownership and the optional fast gesture.

    Required integration:
      camera.eye += result['eye']; camera.target += result['target']
      camera.roll += result['roll']; camera.fov += result['fov']

    ``transition`` always exists.  Outside the brief edit window its active
    flag and strength are false/zero.  At the exact cut phase is zero and the
    held pose has already switched.  ``event`` is the active-window metadata,
    otherwise the most recent cut (None for the opening shot).

    ``world_weights`` and ``world_tint`` are held per shot, not a slow blend.
    Apply the world transform only to scenery.  ``lyric_guard`` explicitly
    identifies a sung line that must survive a semantic scene ownership cut.
    """
    t = _clamp(float(t), 0., DURATION)
    shot = bisect_right(_TIMES, t)
    start = 0. if shot == 0 else EDITS[shot - 1].time
    end = EDITS[shot].time if shot < len(EDITS) else DURATION
    u = _clamp((t - start) / max(.001, end - start), 0., 1.)
    # Linear track plus a gentle arch gives continuous movement inside the
    # shot, without stopping at the middle or aiming at each sung word.
    eye0, target0, roll0, fov0 = _POSE[shot]
    drift = _DRIFT[shot]
    arch = math.sin(math.pi * u)
    eye = [eye0[j] + drift[j] * u for j in range(3)]
    eye[1] += .16 * arch * (-1 if shot % 2 else 1)
    target = [target0[j] + drift[j] * u * (.20 if j < 2 else .08)
              for j in range(3)]
    roll = roll0 + drift[0] * .009 * u
    fov = fov0 + .5 * u

    active = None
    phase = 0.
    for event in EDITS:
        half_window = event.frames / FPS * .5
        if event.time - half_window <= t <= event.time + half_window:
            active = event
            phase = _clamp((t - event.time) / half_window, -1., 1.)
            break
    transition = {
        "active": active is not None, "kind": None, "phase": 0.,
        "strength": 0., "direction": 0., "axis": None,
        "anchor": (.5, .5), "frames": 0, "cut_time": None,
        "motion_blur": 0., "radial_zoom": 0., "line_sweep": 0.,
    }
    if active is not None:
        # Compact support: no effect leaks into the rest of the shot.
        pulse = math.cos(phase * math.pi * .5) ** 2
        swing = math.sin(phase * math.pi) * pulse
        direction = active.direction
        kind = active.kind
        transition.update({
            "kind": kind, "phase": phase, "strength": pulse,
            "direction": direction, "axis": active.axis,
            "anchor": active.anchor, "frames": active.frames,
            "cut_time": active.time,
        })
        if kind == "whip":
            channel = 1 if active.axis == "y" else 0
            eye[channel] += direction * swing * (1.55 if channel == 0 else .55)
            target[channel] += direction * swing * .30
            roll += direction * swing * .055
            fov += 1.2 * pulse
            transition["motion_blur"] = pulse
        elif kind == "crash":
            eye[2] += (-1.15 if phase < 0 else .65) * pulse
            fov += 1.0 * pulse
            transition["radial_zoom"] = direction * pulse
            transition["motion_blur"] = .65 * pulse
        elif kind == "occlusion":
            eye[0] += direction * swing * .65
            roll += direction * swing * .022
            transition["line_sweep"] = pulse
            transition["motion_blur"] = .35 * pulse
        elif kind == "shatter":
            eye[0] += direction * swing * .65
            eye[1] += swing * .28
            roll += direction * swing * .035
            transition["line_sweep"] = pulse
            transition["motion_blur"] = .55 * pulse
        elif kind == "pullback":
            eye[2] += .55 * pulse
            fov += .75 * pulse
            transition["radial_zoom"] = -.65 * pulse
        # A match cut keeps its anchor quiet; its actual discontinuity is the
        # new held camera and scenery pose, rather than a transition overlay.

    # Ownership is switched at the lyric-safe moment, which may trail the
    # visual edit by a few frames.  Never remove current sung glyphs here.
    group = 0
    for event in EDITS:
        if t >= event.ownership_at:
            group = event.group
    guard = None
    guard_event = active or (EDITS[shot - 1] if shot else None)
    if guard_event is not None and t < guard_event.guard_until:
        guard = {"index": guard_event.guard_index,
                 "until": guard_event.guard_until}
    world_phase, rotation, scale, tint, gains = _WORLD[shot]
    latest = active or (EDITS[shot - 1] if shot else None)
    return {
        "shot": shot, "shot_start": start, "shot_end": end,
        "shot_progress": u, "event": latest.metadata() if latest else None,
        "eye": tuple(_clamp(v, -7., 7.) if j == 0 else
                     _clamp(v, -3.5, 3.5) if j == 1 else
                     _clamp(v, -3., 3.) for j, v in enumerate(eye)),
        "target": tuple(_clamp(v, -1.5, 1.5) for v in target),
        "roll": roll, "fov": _clamp(fov, 4., 9.5),
        "world_phase": world_phase + (t - start) * .06,
        "world_rotation": rotation, "world_scale": scale,
        "world_tint": tint,
        "world_weights": dict(zip(("infrastructure", "city", "debris",
                                   "data_ribbons", "skeleton", "memory"), gains)),
        "scene_group": group, "lyric_guard": guard,
        "outro": t >= 141.2, "transition": transition,
    }


if __name__ == "__main__":
    assert len(EDITS) == 16 and len(_POSE) == len(_DRIFT) == len(_WORLD) == 17
    assert all(a.time < b.time for a, b in zip(EDITS, EDITS[1:]))
    jumps = []
    for e in EDITS:
        left, right = sample_edit(e.time - 1e-6), sample_edit(e.time + 1e-6)
        jumps.append(math.sqrt(sum((a-b)**2 for a, b in zip(left['eye'], right['eye']))))
        assert right['shot'] == left['shot'] + 1
        assert e.frames in range(3, 9)
    for frame in range(math.ceil(DURATION * FPS)):
        state = sample_edit(frame / FPS)
        assert all(math.isfinite(x) for key in ('eye', 'target') for x in state[key])
        assert abs(state['eye'][0]) <= 7 and abs(state['eye'][1]) <= 3.5 and abs(state['eye'][2]) <= 3
        assert 4 <= state['fov'] <= 9.5
    assert sample_edit(25.9)['scene_group'] == 5
    assert sample_edit(26.1)['scene_group'] == 6
    assert sample_edit(141.17)['lyric_guard']['index'] == 33
    print('edit director passed: 16 cuts, 17 moving shots, 3--7-frame gestures')
    print('held eye jumps:', ', '.join(f'{j:.2f}' for j in jumps))
    print('kinds:', ', '.join(sorted(set(e.kind for e in EDITS))))
