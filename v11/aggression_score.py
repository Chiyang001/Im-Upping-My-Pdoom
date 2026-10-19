"""Six authored non-explosion accelerations for the line-drawn MV.

``sample_aggression(t)`` is stateless and uses only the standard library.
Apply its camera pose BEFORE the independent explosion-camera rig:

    eye += right * camera_local[0] + up * camera_local[1]
    eye += forward * camera_local[2]
    target += right * target_local[0] + up * target_local[1]
    target += forward * target_local[2]

Here forward = normalized(target - eye), right = normalized(cross(forward,
world_up)), up = cross(right, forward); calculate this basis before changing
the eye. Positive camera z therefore moves INTO the scene. Roll is radians,
fov is extra degrees. These are a few directed actions, not drum-camera noise.

Every action begins and ends at zero with zero first derivative, including
its structural force. ``world_speed`` is an extra forward world-travel PHASE
in world units, despite its inherited field name; do not multiply the absolute
clock by it. It can be added to the background travel phase. Its recovery is
slow enough to avoid an obvious reversal of the already travelling scenery.

``scene_force`` values are normalized scalar amounts for the six structural
actions. Suggested shader integration is documented in SHADER_ACTIONS below.
All forces must apply to structural role 0 only, never glyph positions.
The four P(doom) attacks, other explosions, instrumental outro and final
hold are intentionally outside this module's remit.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Action:
    label: str
    start: float
    peak: float
    end: float
    camera_local: tuple
    target_local: tuple
    roll: float
    fov: float
    world_speed: float
    razor_gain: float
    force: str
    force_amount: float = 1.0


# Amplitudes keep the word host on its authored physical plane. Lens opening
# compensates the forward plunge; it is not a substitute for the plunge.
# Fast attacks are followed by a longer continuation / recovery. Most of each
# shot remains governed by its own camera track, so these six actions retain
# musical contrast and do not compete with the four P(doom) detonations.
ACTIONS = (
    Action(
        'loss cliff: descend on DROP',
        10.02, 10.80, 12.28,
        (1.35, -1.40, 3.40), (.22, -.25, .24),
        -.30, 8.5, .65, .68, 'loss_drop', 1.0,
    ),
    Action(
        'jaw: enter the gap, teeth scrape past the lens',
        19.98, 20.80, 22.17,
        (1.45, -.45, 3.65), (.26, -.08, .22),
        -.28, 9.0, .55, .95, 'jaw_bite', 1.0,
    ),
    Action(
        'acceleration: punch through the lane fins',
        46.92, 47.78, 48.63,
        (.52, .28, 3.20), (.06, .03, .26),
        .16, 10.0, .45, 1.0, 'accel_lane', 1.0,
    ),
    Action(
        'sharp left: counterbank across the outer rail',
        81.62, 82.39, 84.72,
        (-2.25, .48, 2.15), (-.32, .05, .18),
        .33, 7.0, .70, .90, 'left_turn', 1.0,
    ),
    Action(
        'disobey: scrape across a shearing machine joint',
        113.58, 114.62, 116.54,
        (-2.05, -.65, 2.90), (-.28, -.08, .20),
        .32, 8.5, .75, 1.0, 'disobey_shear', 1.0,
    ),
    Action(
        'RLHF askew: bank across interconnect layers',
        121.45, 122.13, 123.80,
        (1.45, .72, 2.20), (.19, .08, .17),
        -.29, 7.0, .65, .80, 'rack_askew', 1.0,
    ),
)


# Four concrete renderer integrations cover all six semantic actions. They
# are metadata, so importing this module never needs numpy or an OpenGL ctx.
SHADER_ACTIONS = (
    {
        'motion': 2,
        'force': 'loss_drop',
        'parameter': 'extra cliff displacement, local y',
        'amplitude': -4.2,
        'suggestion':
            'p.y -= 4.2 * force * smoothstep(-1., 2., p.x); '
            'p.z += force * .8 * sin(p.x * .7);',
        'purpose': 'Training-loss contours buckle into a cliff on DROP.',
    },
    {
        'motion': 4,
        'force': 'jaw_bite',
        'parameter': 'alternating teeth advance and inner compression',
        'amplitude': 3.6,
        'suggestion':
            'float tooth = floor((p.x + 20.) / 1.4); '
            'float alt = mod(tooth, 2.); '
            'p.z += force * (alt * 2. - 1.) * 3.6; '
            'p.y *= 1. - force * .22;',
        'purpose':
            'Teeth pass at different depths instead of shrinking uniformly.',
        'caution':
            'If tooth lines share vertices across bins, derive alt from a '
            'per-tooth mesh seed rather than floor(pos.x).',
    },
    {
        'motion': '11 / world near-field trusses',
        'force': 'accel_lane / left_turn',
        'parameter': 'extra z phase plus near-lens crossing rails',
        'amplitude': 7.0,
        'suggestion':
            'For ni11, add +7.0 * accel_lane to the already wrapped local z '
            'phase, wrapping before projection. Place 4-6 near-field trusses '
            'at peripheral x/y, not across the central lyric clearance. '
            'For turn, yaw the incoming rail by -.5 * left_turn and translate '
            'it laterally 2.0 * left_turn along the outer bend.',
        'purpose':
            'Foreground parallax makes acceleration and the left turn visible.',
    },
    {
        'motion': '27 / 29',
        'force': 'disobey_shear / rack_askew',
        'parameter': 'opposed joint fracture and stepped rack shear',
        'amplitude': 2.5,
        'suggestion':
            'For ni27: p.z += sign(p.x) * disobey_shear * 2.5; '
            'p.x += p.y * disobey_shear * .45; '
            'For ni29: p.x += clamp(floor(p.y * .7), -3., 3.) '
            '* rack_askew * .75; '
            'p.z += sign(p.y) * rack_askew * 1.2;',
        'purpose':
            'The machine disobeys by separating; GPU rows then lose alignment.',
        'caution':
            'Use per-part seeds for rigid pieces if available; leave word '
            'role 1 untouched and keep the foreground word-clearance pocket.',
    },
)


def _smooth(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3.0 - 2.0 * value)


def _envelope(t, action):
    if t <= action.start or t >= action.end:
        return 0.0
    if t <= action.peak:
        return _smooth((t - action.start) / (action.peak - action.start))
    return 1.0 - _smooth((t - action.peak) / (action.end - action.peak))


def sample_aggression(t):
    """Sample a C1 local camera / semantic-geometry action at musical time.

    Return keys are always present. ``events`` carries the active cue's
    finite support and amplitude for logging; pose values are ready to add
    once, without a second multiplication by ``amount``. ``scene_force``
    likewise already includes its cue envelope. No lyric timing is changed.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('sample_aggression requires finite time')
    forces = {action.force: 0.0 for action in ACTIONS}
    out = {
        'active': False,
        'label': None,
        'start': None,
        'peak': None,
        'end': None,
        'duration': 0.0,
        'amount': 0.0,
        'camera_local': (0.0, 0.0, 0.0),
        'target_local': (0.0, 0.0, 0.0),
        'roll': 0.0,
        'fov': 0.0,
        'world_speed': 0.0,
        'razor_gain': 0.0,
        'scene_force': forces,
        'events': [],
    }
    camera = [0.0, 0.0, 0.0]
    target = [0.0, 0.0, 0.0]
    for action in ACTIONS:
        amount = _envelope(t, action)
        if amount <= 0.0:
            continue
        out['active'] = True
        for k in range(3):
            camera[k] += action.camera_local[k] * amount
            target[k] += action.target_local[k] * amount
        for key in ('roll', 'fov', 'world_speed', 'razor_gain'):
            out[key] += getattr(action, key) * amount
        forces[action.force] += action.force_amount * amount
        row = {
            'label': action.label,
            'start': action.start,
            'peak': action.peak,
            'end': action.end,
            'duration': action.end - action.start,
            'amount': amount,
            'force': action.force,
        }
        out['events'].append(row)
        if amount >= out['amount']:
            for key in ('label', 'start', 'peak', 'end', 'duration', 'amount'):
                out[key] = row[key]
    out['camera_local'] = tuple(camera)
    out['target_local'] = tuple(target)
    return out


def validate_score():
    """Small CPU-only invariants for envelopes and stage ownership."""
    supports = []
    epsilon = 1.0e-6
    for action in ACTIONS:
        assert 0.0 < action.start < action.peak < action.end < 141.14
        for boundary in (action.start, action.end):
            assert _envelope(boundary, action) == 0.0
            # A finite-difference derivative approaches zero from either side.
            derivative = (_envelope(boundary + epsilon, action)
                          - _envelope(boundary - epsilon, action)) / (2 * epsilon)
            assert abs(derivative) < 1.0e-4
        assert _envelope(action.peak, action) == 1.0
        peak = sample_aggression(action.peak)
        assert peak['active'] and peak['label'] == action.label
        assert peak['world_speed'] >= 0.0
        supports.append((action.label, action.start, action.end))
    for t in (0.0, 23.620, 42.050, 49.785, 59.985, 96.335,
              103.870, 117.505, 125.460, 131.140, 141.2, 154.6):
        assert not sample_aggression(t)['active']
    return {'actions': len(ACTIONS), 'C1_boundaries': True,
            'explosion_and_outro_windows_clear': True, 'supports': supports}


if __name__ == '__main__':
    import json
    print(json.dumps(validate_score(), indent=2))
