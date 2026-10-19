"""Authored camera coverage for the vocal, independent of the travel rig.

The 32 shots have the exact cut boundaries of ``edit_director_v9.EDITS``.
``camera_eye`` and ``camera_target`` are ABSOLUTE renderer-local coordinates;
they replace the old base-rig-plus-small-offset camera, rather than adding to
it.  World travel and the edit director's transition shutter remain intact.

``word_anchor`` is a fixed, shot-local host position.  The renderer can add its
existing node translation, but should not add the old large phrase offsets.
The recommended transform is T(anchor) @ RY(ry) @ RX(rx) @ RZ(rz) @ S(scale).
``word_plane_rotation`` is (rx, ry, rz), radians; it is constant for the entire
shot.  These are authored walls, hanging plates and floors, never a per-frame
billboard.  ``word_scale`` multiplies the v9 token-group scale.  Keep relative
token slots small (suggested factor .32) around the host.  Static framing
calibration is allowed to reduce word_scale / adjust the lens per shot.

The camera follows a directed track inside every shot: there is no circular
orbit or recurring return to the frontal stage.  At 141.2 seconds ``active``
is False; the existing beat-cut outro and the end-title freeze take ownership.
This module uses only the Python standard library.
"""

from bisect import bisect_right
from dataclasses import dataclass, replace
import math


VOCAL_END = 141.2
CUT_TIMES = (
    5.700, 9.100, 12.990, 17.070, 22.190, 25.685, 31.830,
    38.190, 42.050, 44.790, 48.645, 53.885, 58.430, 65.920,
    68.185, 73.870, 77.240, 82.050, 84.780, 89.995, 95.910,
    98.845, 104.330, 109.330, 116.595, 118.645, 123.870,
    127.960, 133.430, 136.830, 141.140,
)


@dataclass(frozen=True)
class Shot:
    kind: str
    lens: str
    description: str
    eye_in: tuple
    eye_out: tuple
    target_in: tuple
    target_out: tuple
    roll: tuple
    fov: tuple
    word_anchor: tuple
    word_plane_rotation: tuple
    word_scale: float
    surface: str
    focal_node: int
    bow: tuple = (0., 0., 0.)


# Each row owns the scene action and a different physical viewing position.
# Floor rotations intentionally differ from wall / instrument rotations.
SHOTS = (
    Shot('iris_macro', 'close / 48-51 degrees',
         'Skim the etched iris at sensor distance, then pull across its rim.',
         (4., 2., 8.), (-1., 1., 13.), (0., 0., -3.), (-.8, .2, -3.5),
         (-.035, .015), (48., 51.), (0., .15, -2.7), (-.12, .12, 0.),
         .42, 'engraved iris inspection plate', 0, (0., .25, -.3)),
    Shot('circuit_lateral', 'close / 46-51 degrees',
         'Run sideways along the circuit traces; the chips cross foreground.',
         (-14., 2.7, 10.), (-4., .8, 8.), (-2., .2, -5.), (1., -.2, -6.),
         (-.045, .025), (46., 51.), (-.8, -.35, -4.), (-.08, -.55, -.015),
         .48, 'side-facing circuit carrier', 1, (0., .45, -.2)),
    Shot('loss_overhead', 'high angle / 52-57 degrees',
         'Read the loss cliff from overhead while sliding diagonally downhill.',
         (5., 25., 6.), (-4., 19., -2.), (0., -1., -4.), (-1., -2., -7.),
         (.015, -.035), (52., 57.), (0., -.4, -3.8), (-1.30, .08, 0.),
         .65, 'training-loss contour floor', 2, (.5, 0., .45)),
    Shot('command_worm_eye', 'very low angle / 56-60 degrees',
         'Pass underneath the command rig and look up at its hanging authority.',
         (-5., -9., 12.), (3., -6., 17.), (0., 2., -5.), (.6, 2.3, -5.),
         (.025, -.025), (56., 60.), (0., 1.2, -4.2), (.50, -.12, .015),
         .63, 'hanging command beam', 3, (0., -.35, -.5)),
    Shot('jaw_pov', 'aperture POV / 62-69 degrees',
         'Enter between the teeth at eye height; jaw blades scrape the lens.',
         (1.7, .3, 7.), (-1.5, -1., 11.), (.2, 0., -9.), (-.5, -.5, -11.),
         (-.025, .04), (62., 69.), (0., -.4, -4.), (.05, .03, 0.),
         .53, 'inner jaw membrane', 4, (.35, -.1, -.9)),
    Shot('detonation_low_wide', 'low wide / 64-72 degrees',
         'A low pressure-vessel view expands into the first P(doom) detonation.',
         (8., -9., 23.), (-4., -4., 31.), (0., 0., -6.), (0., 1., -8.),
         (.045, -.025), (64., 72.), (0., .1, -4.5), (.22, .12, 0.),
         .80, 'pressure-vessel cross member', 5, (0., -.7, -1.4)),
    Shot('room_over_shoulder', 'oblique medium / 55-60 degrees',
         'Cross the doorpost from the shoulder and see the room extend away.',
         (10., 3., 10.), (7., 1., 4.), (-2., -1., -11.), (-3., -.6, -14.),
         (-.035, .025), (55., 60.), (.7, -.8, -6.3), (-.08, .43, -.015),
         .53, 'inner room wall / incoming filament', 6, (-.6, .25, 0.)),
    Shot('seeing_eye_close', 'eye close-up / 40-44 degrees',
         'Cut directly to one Shinigami iris, not another whole-machine vista.',
         (-4.4, .8, 7.), (-7.4, 1.3, 10.), (-5., 0., -3.), (-5., .2, -3.4),
         (.02, -.02), (40., 44.), (-4.8, -.35, -2.5), (-.08, -.07, .015),
         .39, 'left ocular rim engraving', 8, (.2, .25, -.3)),
    Shot('stable_top_track', 'top view / 51-55 degrees',
         'Track over the stable oscilloscope deck as if it were a real table.',
         (-7., 21., 8.), (7., 17., 0.), (-1., -1., -4.), (1., -1., -6.),
         (-.025, .035), (51., 55.), (0., -.6, -4.5), (-1.28, 0., -.025),
         .64, 'horizontal oscilloscope deck', 9, (0., 0., .7)),
    Shot('singularity_undercut', 'low oblique / 56-61 degrees',
         'Drop below the folded funnel and inspect the space turning inside out.',
         (13., -6., 7.), (8., -11., 10.), (0., -1., -6.), (-.5, -2., -8.),
         (.065, -.035), (56., 61.), (.1, -1.5, -4.8), (.62, .53, .025),
         .57, 'underside of singularity shell', 10, (.4, -.35, -.4)),
    Shot('acceleration_pov', 'forward POV / 70-76 degrees',
         'Race inside the lanes with foreground fins overtaking the lens.',
         (1., -1., 10.), (-1.3, .5, 4.8), (0., 0., -20.), (-.6, .3, -27.),
         (-.035, .035), (70., 76.), (0., .15, -6.), (.035, -.015, 0.),
         .57, 'forward acceleration gate', 11, (.4, .3, -.7)),
    Shot('atom_specimen_macro', 'instrument macro / 35-40 degrees',
         'Inspect the atoms from a close probe; bonds cross each other in depth.',
         (5., 2., 9.), (-3., -1., 12.), (.3, 0., -4.), (-.7, -.4, -5.),
         (.025, -.025), (35., 40.), (0., -.15, -3.6), (-.06, .12, 0.),
         .35, 'atomic specimen carrier', 12, (0., .6, -.4)),
    Shot('prison_side_low', 'side tracking / 51-57 degrees',
         'Pass the bars from below and to one side, rather than face the cage.',
         (-16., -5., 10.), (-8., -3., 7.), (0., -1., -7.), (1., 0., -9.),
         (-.04, .025), (51., 57.), (-.7, -.2, -5.5), (.24, -.65, -.02),
         .55, 'inside prison-bar cross plate', 13, (0., -.35, -.2)),
    Shot('basilisk_low_reveal', 'hero low angle / 62-67 degrees',
         'Look up the basilisk spine and climb across its enormous lower coils.',
         (8., -11., 18.), (-3., -6., 23.), (0., 2., -6.), (-1., 3., -7.),
         (.04, -.03), (62., 67.), (0., .3, -5.), (.37, .13, .01),
         .73, 'lower basilisk coil', 14, (.6, -.5, -.8)),
    Shot('compute_rack_side', 'rack medium / 49-55 degrees',
         'Descend beside one compute bank with modules filling a near edge.',
         (15., 7., 8.), (11., -2., 12.), (3., 0., -9.), (2., -1., -11.),
         (.025, -.025), (49., 55.), (2.4, -.5, -6.7), (-.16, .61, .015),
         .55, 'compute-bank side face', 16, (.2, 0., -.4)),
    Shot('approval_instrument', 'close inspection / 38-43 degrees',
         'Tilt past the safety shell to inspect its fragile approval surface.',
         (0., 7., 8.), (5., 3., 11.), (0., -1., -4.), (1., -.8, -5.),
         (-.02, .025), (38., 43.), (.1, -.25, -3.8), (-.48, .13, 0.),
         .37, 'tilted safety-inspection plate', 17, (-.2, .3, -.3)),
    Shot('feedback_birdseye', 'birdseye / 51-56 degrees',
         'Expose the forward/backward mechanism from above and cross its loop.',
         (2., 23., 3.), (-7., 20., -5.), (0., -1., -6.), (-1., -1., -9.),
         (.025, -.025), (51., 56.), (0., -.6, -4.7), (-1.31, -.05, .02),
         .65, 'feedback-machine top surface', 18, (.5, 0., .4)),
    Shot('obsolete_over_shoulder', 'shoulder medium-close / 43-49 degrees',
         'See the abandoned mechanism past its large foreground shoulder.',
         (-12., 6., 12.), (-7., 2., 9.), (0., -1., -7.), (.6, -.5, -9.),
         (-.025, .02), (43., 49.), (-.5, -.4, -5.2), (-.21, -.49, -.015),
         .50, 'abandoned machine reverse plate', 19, (0., .4, -.3)),
    Shot('left_turn_cross_track', 'extreme side / 58-64 degrees',
         'Cut across the sharp left turn and sprint sideways through its path.',
         (18., 1., 8.), (9., 1.8, -5.), (0., 0., -9.), (-2., .2, -15.),
         (.035, -.035), (58., 64.), (.5, -.2, -6.), (-.05, .97, 0.),
         .57, 'outer face of turning rail', 20, (.5, .4, 0.)),
    Shot('boundary_negative_space', 'oblique medium / 49-55 degrees',
         'Slip up the broken boundary and let its missing centre reveal depth.',
         (-14., 1., 12.), (-8., 5., 8.), (0., 0., -7.), (1., .5, -9.),
         (-.025, .03), (49., 55.), (-.7, .2, -5.6), (-.18, -.57, .02),
         .55, 'remaining boundary wall', 21, (0., .3, -.4)),
    Shot('gato_claw_pov', 'low close / 53-59 degrees',
         'Look up between the gripping fingers and follow the stretched tether.',
         (3., -9., 10.), (-2., -5., 7.), (0., 2., -4.), (-.5, 2., -6.),
         (.025, -.03), (53., 59.), (0., -.3, -3.8), (.59, .06, 0.),
         .52, 'underside of Gato finger bridge', 22, (.25, -.4, -.5)),
    Shot('paperclip_factory_top', 'overhead production / 53-59 degrees',
         'See clips multiply across a true overhead conveyor composition.',
         (-4., 24., 4.), (6., 18., -4.), (0., -3., -6.), (1., -3., -8.),
         (-.025, .035), (53., 59.), (0., -1.9, -5.), (-1.34, .02, -.02),
         .68, 'paperclip-conveyor deck', 23, (.5, 0., .5)),
    Shot('killswitch_macro', 'switch macro / 39-45 degrees',
         'Inspect the unattended shutdown station at reach distance.',
         (8., 3., 9.), (3., -2., 7.), (0., -1., -5.), (-.5, -.8, -6.),
         (.025, -.02), (39., 45.), (0., -.8, -4.2), (-.09, .32, .01),
         .36, 'vacant killswitch console', 24, (.25, .3, -.3)),
    Shot('orthogonal_reverse', 'reverse side / 53-60 degrees',
         'Pass behind the orthogonal axes and see their incompatible directions.',
         (-15., -4., 7.), (-8., 3., -1.), (0., 0., -9.), (1., 1., -12.),
         (-.04, .035), (53., 60.), (-.5, .1, -6.8), (.09, -.72, .015),
         .53, 'reverse orthogonal-axis truss', 26, (0., -.4, .3)),
    Shot('machine_reverse_shoulder', 'reverse shoulder / 50-56 degrees',
         'Approach disobedience from the back of a joint, beneath moving arms.',
         (14., 5., 9.), (7., -1., 3.), (0., 0., -8.), (-1., -.3, -11.),
         (.03, -.035), (50., 56.), (.6, .25, -6.2), (-.11, .61, -.015),
         .54, 'reverse transformer-joint web', 27, (.3, .4, -.2)),
    Shot('safety_fence_worm_eye', 'ground-level wide / 63-69 degrees',
         'Watch the fence burst overhead; fragments clear the low camera.',
         (-2., -11., 10.), (4., -6., 6.), (0., 1., -7.), (.5, 2., -10.),
         (-.03, .035), (63., 69.), (0., -.7, -5.3), (.63, .05, 0.),
         .60, 'underside of breached fence', 28, (.3, -.5, -.3)),
    Shot('gpu_interconnect_macro', 'chip macro / 36-42 degrees',
         'Skim a single bank of GPU interconnects while far racks shear past.',
         (-9., 3., 6.), (-3., 1., 9.), (0., 0., -6.), (.5, -.2, -7.),
         (-.025, .02), (36., 42.), (-.2, -.25, -4.6), (-.13, -.43, -.015),
         .36, 'GPU interconnect substrate', 29, (0., .35, -.3)),
    Shot('loom_overhead', 'overhead weave / 49-55 degrees',
         'Look down onto the prophecy loom and cross warp against weft.',
         (5., 22., 4.), (-5., 18., -3.), (0., -2., -6.), (-1., -2., -9.),
         (.025, -.03), (49., 55.), (0., -1.2, -4.9), (-1.30, .03, .025),
         .64, 'horizontal loom bed', 30, (.6, 0., .4)),
    Shot('recursive_aperture_pov', 'aperture POV / 64-72 degrees',
         'Drive through successive recursive glyph apertures at their centre.',
         (.5, .2, 11.), (-1., .5, 3.), (0., 0., -21.), (-.6, .2, -29.),
         (-.035, .035), (64., 72.), (0., .1, -6.5), (-.025, -.025, 0.),
         .57, 'recursive-upgrade aperture', 31, (.4, -.3, -.8)),
    Shot('observer_shoulder', 'observer shoulder / 44-50 degrees',
         'Reveal the observer through the opening eye from its theatre wing.',
         (15., 5., 15.), (8., 2., 11.), (0., 0., -6.), (-.5, .5, -8.),
         (.025, -.025), (44., 50.), (.4, .15, -4.8), (-.15, .48, -.015),
         .54, 'observer aperture inner wall', 32, (.3, .35, -.4)),
    Shot('theatre_wide_reveal', 'wide reveal / 55-64 degrees',
         'Escape the theatre wing into the full machine before the beat outro.',
         (-17., 5., 20.), (-2., 8., 32.), (0., 0., -8.), (0., 1., -10.),
         (-.035, .015), (55., 64.), (0., .2, -5.2), (-.15, -.20, 0.),
         .82, 'theatre proscenium cross beam', 33, (0., 1., -.6)),
    Shot('whole_machine_handoff', 'wide / 65 degrees',
         'Hand the whole-machine reveal directly to the existing beat outro.',
         (-2., 8., 32.), (-1.7, 8.1, 32.3), (0., 1., -10.), (0., 1., -10.2),
         (.015, .015), (64., 65.), (0., .2, -5.2), (-.15, -.20, 0.),
         .82, 'theatre proscenium cross beam', 33),
)


# These inserts inspect a specific part, rather than the empty centre of a
# large apparatus. Coordinates include the renderer's semantic mesh scale.
_detail_overrides = {
    1: dict(eye_in=(-17., 1., 3.), eye_out=(-11., 2., -3.),
            target_in=(0., 0., -10.), target_out=(0., .2, -11.),
            fov=(51., 55.), word_anchor=(-.5, -.4, -6.),
            word_plane_rotation=(-.05, -.97, -.01), word_scale=.45),
    11: dict(eye_in=(3.8, 3., 8.8), eye_out=(.3, 1.2, 7.4),
             target_in=(-3.664, .434, -.486), target_out=(-4.15, .6, -1.8),
             fov=(40., 44.), word_anchor=(-3.4, .25, -1.8),
             word_plane_rotation=(-.10, .60, 0.), word_scale=.30),
    15: dict(eye_in=(-10., 7., 10.), eye_out=(-5., 3., 10.),
             target_in=(-8., 0., -4.), target_out=(-6., 0., -5.),
             word_anchor=(-7., -.25, -2.8), word_plane_rotation=(-.40, -.15, 0.)),
    17: dict(eye_in=(-22., 6., 17.), eye_out=(-16., 3., 11.),
             target_in=(-11., 0., 2.), target_out=(-10., 0., 2.),
             word_anchor=(-10., .1, 3.), word_plane_rotation=(-.20, -.60, -.015),
             word_scale=.43),
    26: dict(eye_in=(-20., 8., 16.), eye_out=(-16., 5., 13.),
             target_in=(-12., 2., 1.), target_out=(-11., 2., 0.),
             word_anchor=(-11.5, 1.8, 3.), word_plane_rotation=(-.30, -.40, -.015),
             word_scale=.33),
    27: dict(eye_in=(5., 14., 4.), eye_out=(-4., 10., -1.),
             target_in=(0., -3.8, -8.5), target_out=(-1., -3.8, -9.),
             word_anchor=(0., -3.2, -7.8), word_plane_rotation=(-1.23, .03, .025),
             word_scale=.48),
    29: dict(eye_in=(4.7, 1.6, 3.2), eye_out=(1.4, .6, -6.8),
             target_in=(-1.754, -.060, -15.2), target_out=(-1.754, -.060, -28.1),
             fov=(43., 47.), word_anchor=(-.8, -1.1, -13.8),
             word_plane_rotation=(-.05, .18, 0.), word_scale=.32),
}
SHOTS=tuple(replace(s, **_detail_overrides.get(i, {})) for i,s in enumerate(SHOTS))


def _mix(a, b, p):
    return tuple(x + (y - x) * p for x, y in zip(a, b))


def sample_shot(t):
    """Return a directed shot, a stable word host and editorial metadata.

    The camera is intentionally discontinuous at the existing 31 motivated
    cuts; each side has its own direction, angle and lens.  Its directed path
    has non-zero end speed, avoiding slow ease-in / ease-out at every lyric.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('sample_shot requires finite time')
    tc = max(0., min(VOCAL_END, t))
    shot_id = min(len(SHOTS) - 1, bisect_right(CUT_TIMES, tc))
    shot = SHOTS[shot_id]
    start = 0. if shot_id == 0 else CUT_TIMES[shot_id - 1]
    end = CUT_TIMES[shot_id] if shot_id < len(CUT_TIMES) else VOCAL_END
    u = min(1., max(0., (tc - start) / max(.001, end - start)))
    # Nonzero monotonic travel with a brisk arrival and a continuing exit.
    p = .80 * u + .20 * (1. - (1. - u) ** 2)
    arch = math.sin(math.pi * u)
    eye = tuple(v + shot.bow[i] * arch
                for i, v in enumerate(_mix(shot.eye_in, shot.eye_out, p)))
    target = _mix(shot.target_in, shot.target_out, p)
    return {
        'active': 0. <= t < VOCAL_END,
        'shot': shot_id,
        'shot_id': shot_id,
        'shot_start': start,
        'shot_end': end,
        'shot_progress': u,
        'camera_eye': eye,
        'camera_target': target,
        'roll': shot.roll[0] + (shot.roll[1] - shot.roll[0]) * p,
        'fov': shot.fov[0] + (shot.fov[1] - shot.fov[0]) * p,
        'kind': shot.kind,
        'lens': shot.lens,
        'description': shot.description,
        'word_anchor': shot.word_anchor,
        'word_plane_rotation': shot.word_plane_rotation,
        'word_scale': shot.word_scale,
        'word_slot_scale': .32,
        'word_surface': shot.surface,
        'focal_node': shot.focal_node,
    }


if __name__ == '__main__':
    assert len(SHOTS) == len(CUT_TIMES) + 1 == 32
    assert all(a < b for a, b in zip(CUT_TIMES, CUT_TIMES[1:]))
    paths = []
    for i, shot in enumerate(SHOTS):
        a = 0. if i == 0 else CUT_TIMES[i - 1]
        b = CUT_TIMES[i] if i < len(CUT_TIMES) else VOCAL_END
        paths.append(math.dist(shot.eye_in, shot.eye_out))
        for j in range(31):
            state = sample_shot(a + (b-a) * (j + .01) / 31.)
            numbers = (*state['camera_eye'], *state['camera_target'],
                       *state['word_anchor'], *state['word_plane_rotation'],
                       state['fov'], state['roll'], state['word_scale'])
            assert all(math.isfinite(v) for v in numbers)
            assert state['shot_id'] == i
            assert math.dist(state['camera_eye'], state['camera_target']) > 4.
            assert 30. <= state['fov'] <= 78.
            assert .20 <= state['word_scale'] <= .90
        assert math.dist(shot.eye_in, shot.eye_out) > .1
    assert not sample_shot(141.2)['active']
    assert not sample_shot(155.)['active']
    assert sample_shot(23.18)['focal_node'] == 5
    assert sample_shot(60.)['focal_node'] == 14
    assert sample_shot(97.)['focal_node'] == 23
    assert sample_shot(125.7)['focal_node'] == 30
    print('Shot grammar passed: 32 authored compositions; seven angle families')
    print('Vocal eye z %.1f..%.1f; eye y %.1f..%.1f; FOV %.1f..%.1f' % (
        min(min(s.eye_in[2], s.eye_out[2]) for s in SHOTS),
        max(max(s.eye_in[2], s.eye_out[2]) for s in SHOTS),
        min(min(s.eye_in[1], s.eye_out[1]) for s in SHOTS),
        max(max(s.eye_in[1], s.eye_out[1]) for s in SHOTS),
        min(s.fov[0] for s in SHOTS), max(s.fov[1] for s in SHOTS)))
    print('Directed camera displacement %.2f..%.2f units per shot' % (
        min(paths[:-1]), max(paths[:-1])))
