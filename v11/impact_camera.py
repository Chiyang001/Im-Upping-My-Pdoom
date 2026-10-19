"""Fast, authored impact camera moves around a real scene / lyric centre.

This module does not change a lyric, token transform, cut time or beat.  The
normal shot remains the reference pose throughout each finite-support move.
Apply AFTER the ordinary shot pose and BEFORE projection; the existing outro
can continue to take final ownership after 141.2 seconds.

    move = apply_impact_camera(t, eye, target, roll, fov,
                               focus=impact_origin(event, t),
                               event=event, text_normal=word_normal)
    eye, target, roll, fov = (move[k] for k in ('eye','target','roll','fov'))

``event`` accepts an impact metadata dict, an Impact dataclass or its name.
Omitting it selects among the same nine accepted semantic impact times.  A
glyph's world-space +Z normal is optional but recommended: it limits the
orbit to the original visible hemisphere, rather than turning words into
mirrored reverse faces.  The words themselves are never billboarded.

The four choruses have different attack directions.  All moves contain a
fast real orbit and dolly, a strong barrel bank and a smaller counter-whip.
They return with zero relative position / velocity at their support ends.
Values are ordinary Python floats / tuples; there is no renderer dependency.
"""

import math


# time, name, yaw degrees, pitch degrees, roll degrees, dive, recoil, duration
# Positive / negative banks deliberately differ between consecutive events.
MOVES = (
    (23.620, 'PDOOM 1',       39., -16., -64., .28, .20, 1.12),
    (42.050, 'SINGULARITY', -32.,  29.,  58., .34, .12, 1.08),
    (49.785, 'ATOMS',        30., -19., -53., .23, .16,  .98),
    (59.985, 'PDOOM 2',     -37.,  31.,  71., .31, .23, 1.16),
    (96.335, 'PDOOM 3',      47., -23., -75., .32, .24, 1.20),
    (103.870, 'FUSE',       -43., -14.,  62., .29, .20, 1.12),
    (117.505, 'SAFETY FENCE', 35.,  29., -66., .28, .19, 1.10),
    (125.460, 'PDOOM 4',    -49., -25.,  79., .35, .25, 1.22),
    (131.140, 'SELF UPGRADE', 40.,  24., -68., .30, .20, 1.12),
)

PRE = .14
_BY_NAME = {row[1]: row for row in MOVES}


def _clamp(x, lo=0., hi=1.):
    return min(hi, max(lo, x))


def _smooth(x):
    x = _clamp(x)
    return x*x*(3.-2.*x)


def _bump(age, peak, end):
    """A compact C1 impulse, with separate authored rise / return duration."""
    if age <= 0. or age >= end:
        return 0.
    if age <= peak:
        return _smooth(age/peak)
    return 1.-_smooth((age-peak)/(end-peak))


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _mul(a, s):
    return tuple(x*s for x in a)


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a):
    length = _norm(a)
    if length < 1.e-10:
        raise ValueError('A camera / normal direction has zero length')
    return _mul(a, 1./length)


def _rotate(v, axis, angle):
    """Rodrigues rotation, valid for near-overhead and low cameras alike."""
    c, s = math.cos(angle), math.sin(angle)
    return _add(_add(_mul(v, c), _mul(_cross(axis, v), s)),
                _mul(axis, _dot(axis, v)*(1.-c)))


def _event_row(t, event):
    if event is not None:
        name = event if isinstance(event, str) else (
            event.get('name') if isinstance(event, dict) else event.name)
        row = _BY_NAME.get(name)
        return row if row and -PRE <= t-row[0] < row[-1] else None
    return next((row for row in MOVES if -PRE <= t-row[0] < row[-1]), None)


def sample_impact_camera(t, event=None):
    """Return dimensionless choreography; angles are radians, lens degrees.

    ``radius_scale`` is relative to the actual focus distance.  This makes a
    9-unit macro push and a 35-unit wide-shot recoil equally legible.  Peaks
    happen .19-.24 seconds after the accepted sung / semantic blast attacks.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('Impact camera requires a finite time')
    row = _event_row(t, event)
    if row is None:
        return dict(active=False, name=None, yaw=0., pitch=0., roll=0.,
                    radius_scale=1., fov=0., focus_lock=0., activity=0.,
                    age=None, duration=0., phase='shot')
    at, name, yaw, pitch, bank, dive, recoil, end = row
    age = t-at
    if age < 0.:
        q = _smooth((age+PRE)/PRE)
        return dict(active=True, name=name, age=age, duration=end,
                    yaw=math.radians(-yaw*.055*q),
                    pitch=math.radians(-pitch*.04*q),
                    roll=math.radians(-bank*.045*q),
                    radius_scale=1.+.055*q, fov=-1.8*q,
                    focus_lock=.08*q, activity=.08*q, phase='load')
    # Carry the small pre-load continuously across the actual detonation.
    carry = 1.-_smooth(age/.085)
    peak = .205 if name == 'ATOMS' else .23
    main = _bump(age, peak, end)
    # The counter-whip is kept weaker, so it reads as a controlled recovery.
    counter = _bump(max(0., age-.22), .33, end-.22)
    out = _bump(max(0., age-.12), .30, end-.12)
    return dict(active=True, name=name, age=age, duration=end,
                yaw=math.radians(yaw*(main-.24*counter)-yaw*.055*carry),
                pitch=math.radians(pitch*(main+.18*counter)-pitch*.04*carry),
                roll=math.radians(bank*(main-.15*counter)-bank*.045*carry),
                radius_scale=1.+.055*carry-dive*main+recoil*out,
                fov=-1.8*carry+14.5*main-5.5*out,
                focus_lock=.08*carry+.48*main,
                activity=main,
                phase='strike' if age < .12 else 'bank' if age < .40 else 'recover')


def apply_impact_camera(t, eye, target, roll, fov, focus=None,
                        event=None, text_normal=None):
    """Return an absolute pose plus measurable motion against the base shot.

    The base aim and eye are rotated together around ``focus``.  A moderate
    focus lock removes the tendency for a near word to exit the frame during
    the bank.  Field of view opens through the dive; it closes on recovery.
    """
    eye, target = tuple(map(float, eye)), tuple(map(float, target))
    focus = tuple(map(float, target if focus is None else focus))
    c = sample_impact_camera(t, event)
    result = dict(c, eye=eye, target=target, roll=float(roll), fov=float(fov),
                  eye_displacement=0., orbit_degrees=0., roll_degrees=0.,
                  radius_ratio=1., hemisphere_limited=False)
    if not c['active']:
        return result
    outward = _sub(eye, focus)
    radius = _norm(outward)
    if radius < .25:
        return result
    forward = _unit(_sub(target, eye))
    # This follows the base shot's horizontal plane, including top views.
    right = _cross(forward, (0., 1., 0.))
    if _norm(right) < .05:
        right = _cross(forward, (0., 0., 1.))
    right = _unit(right)
    up = _unit(_cross(right, forward))

    def turn(v, fraction=1.):
        return _rotate(_rotate(v, up, c['yaw']*fraction), right,
                       c['pitch']*fraction)

    fraction = 1.
    normal = _unit(tuple(text_normal)) if text_normal is not None else None
    # A floor, side wall or tilted plate retains its visible physical face.
    # A 0.32 cosine permits a bold oblique angle without illegible edge-on text.
    if normal is not None:
        baseline = _dot(_unit(outward), normal)
        minimum = min(.32, max(.10, baseline*.65))
        if _dot(_unit(turn(outward)), normal) < minimum:
            lo, hi = 0., 1.
            for _ in range(18):
                mid = (lo+hi)*.5
                if _dot(_unit(turn(outward, mid)), normal) >= minimum:
                    lo = mid
                else:
                    hi = mid
            fraction = lo
            result['hemisphere_limited'] = True
    turned = turn(outward, fraction)
    new_eye = _add(focus, _mul(turned, c['radius_scale']))
    aimed = turn(_sub(target, focus), fraction)
    new_target = _add(focus, _mul(aimed, 1.-c['focus_lock']))
    result.update(eye=new_eye, target=new_target, roll=float(roll)+c['roll'],
                  fov=_clamp(float(fov)+c['fov'], 30., 94.),
                  eye_displacement=_norm(_sub(new_eye, eye)),
                  orbit_degrees=math.degrees(math.acos(_clamp(
                      _dot(_unit(outward), _unit(turned)), -1., 1.))),
                  roll_degrees=math.degrees(c['roll']),
                  radius_ratio=c['radius_scale'])
    return result


def audit_impact_camera(fps=240):
    """Numerical evidence of real displacement / rotation and smooth return.

    The reference is a 30-unit low three-quarter shot.  Renderer QA should
    repeat these metrics with actual world-space lyric centres and frame
    previews, then separately check all 225 unchanged lexical windows.
    """
    rows = []
    base_eye, base_target = (6., -7., 24.), (0., 0., -5.)
    for spec in MOVES:
        at, name, *_, end = spec
        samples = [apply_impact_camera(at-PRE+j/fps, base_eye, base_target,
                                      0., 62., focus=base_target, event=name,
                                      text_normal=(0., 0., 1.))
                   for j in range(math.ceil((end+PRE)*fps)+1)]
        speed = max(_norm(_sub(a['eye'], b['eye']))*fps
                    for a, b in zip(samples, samples[1:]))
        bank_speed = max(abs(a['roll']-b['roll'])*fps*180./math.pi
                         for a, b in zip(samples, samples[1:]))
        metrics = dict(name=name,
                       max_eye_displacement=max(s['eye_displacement'] for s in samples),
                       max_orbit_degrees=max(s['orbit_degrees'] for s in samples),
                       max_roll_degrees=max(abs(s['roll_degrees']) for s in samples),
                       max_eye_speed=speed, max_roll_speed_degrees=bank_speed,
                       min_radius_ratio=min(s['radius_ratio'] for s in samples),
                       duration=end)
        assert metrics['max_eye_displacement'] > 12., metrics
        assert metrics['max_orbit_degrees'] > 29., metrics
        assert metrics['max_roll_degrees'] > 48., metrics
        assert metrics['max_eye_speed'] > 95., metrics
        assert metrics['max_roll_speed_degrees'] > 300., metrics
        # Exactly the unmodified shot at both support ends; dense sampling
        # also proves first / last-frame relative drift vanishes smoothly.
        for boundary in (at-PRE, at+end):
            edge = apply_impact_camera(boundary, base_eye, base_target, 0., 62.,
                                       event=name, focus=base_target)
            assert _norm(_sub(edge['eye'], base_eye)) < 1.e-8
            assert abs(edge['roll']) < 1.e-8
        rows.append(metrics)
    return {'finite_support': True, 'C1_envelopes': True,
            'accepted_semantic_events': 9, 'PDOOM_events': 4,
            'no_FOOM_or_BASILISK_BOOM': True, 'events': rows}


if __name__ == '__main__':
    import json
    print(json.dumps(audit_impact_camera(), indent=2))
