"""One physical pursuit: compute payload -> lunar relief -> Omega focus.

The supplied models are the actual scene models, anchored from the unmodified
authored camera.  No geometry is attached to this camera and no preceding frame
is needed.  Call ``pursuit_camera`` after the ordinary camera has been sampled.
The returned ``surface_matrix`` is an optional physical lyric attachment, not a
billboard: its orientation is inherited from the appropriate machine model.

The camera reaches the real rising sled, side-skims the fixed lunar terrain,
then crosses the intervening world space toward the independent Omega body.
An entry blend occupies 160 ms; the 160 ms lunar/Omega lash lands on the word
Omega.  The existing 60.245 P(doom) crossing is outside this module's interval.
"""

import math


START = 62.34
END = 65.94
MOON_LASH = (64.06, 64.22)
RAIL_KNOTS = (
    (-17., -8.6, 1.1), (-16., -4.7, -5.3), (-14.2, .2, -12.5),
    (-10.5, 6., -20.2), (-5.8, 8.65, -23.), (.1, 9.25, -22.4),
    (5.4, 8.65, -19.), (6.3, 7.75, -15.6),
)
MOON_CENTER = (11.7, 4.25, -16.6)


def _ease(v):
    v = max(0., min(1., float(v)))
    return v * v * (3. - 2. * v)


def _point(model, point, np):
    return (np.asarray(model, float) @ np.r_[point, 1.])[:3]


def _vector(model, vector, np):
    return np.asarray(model, float)[:3, :3] @ np.asarray(vector, float)


def _surface(model, point, np, yaw=0.):
    """A genuine object-local surface; independent of viewing direction."""
    m = np.asarray(model, float).copy()
    m[:3, 3] = _point(model, point, np)
    if yaw:
        c, s = math.cos(yaw), math.sin(yaw)
        r = np.eye(4)
        r[:3, :3] = ((c, 0., s), (0., 1., 0.), (-s, 0., c))
        m = m @ r
    return m


def sled_point(t, np):
    """Match the drawn trolley exactly, including its 0.55-unit deck offset."""
    lift = _ease((t - 62.4) / 1.5)
    knots = np.asarray(RAIL_KNOTS, float)
    index = min(6, int(lift * 7.))
    blend = min(1., lift * 7. - index)
    return knots[index] * (1. - blend) + knots[index + 1] * blend + [0., .55, 0.]


def _curve(t, knots, np):
    """Continuous position/velocity at authored, unequal-time path knots."""
    if t <= knots[0][0]:
        return np.asarray(knots[0][1], float)
    if t >= knots[-1][0]:
        return np.asarray(knots[-1][1], float)
    j = next(i for i in range(len(knots) - 1) if knots[i][0] <= t < knots[i + 1][0])
    ta, pa = knots[j]
    tb, pb = knots[j + 1]
    pa, pb = np.asarray(pa, float), np.asarray(pb, float)
    a = max(0, j - 1)
    b = min(len(knots) - 1, j + 2)
    va = (np.asarray(knots[j + 1][1], float) - np.asarray(knots[a][1], float)) / (knots[j + 1][0] - knots[a][0])
    vb = (np.asarray(knots[b][1], float) - np.asarray(knots[j][1], float)) / (knots[b][0] - knots[j][0])
    u = (t - ta) / (tb - ta)
    return ((2*u**3-3*u*u+1)*pa + (u**3-2*u*u+u)*(tb-ta)*va
            + (-2*u**3+3*u*u)*pb + (u**3-u*u)*(tb-ta)*vb)


def pursuit_landmarks(t, orbit_model, omega_model, *, np):
    """Actual actor centres plus stable, object-oriented lyric surfaces."""
    sled = sled_point(t, np)
    moon = np.asarray(MOON_CENTER, float)
    omega = np.asarray((0., 0., -16.))
    u = max(0., min(1., (t - 64.22) / (65.94 - 64.22)))
    radius = .65 * (3. + 8.5 * u)
    return {
        'sled_local': sled,
        'sled': _point(orbit_model, sled, np),
        'moon': _point(orbit_model, moon, np),
        'omega': _point(omega_model, omega, np),
        'nvda_surface': _surface(orbit_model, sled + [0., 2.6, .5], np),
        'moon_surface': _surface(orbit_model, moon + [-.3, 1.7, 6.55], np, -.12),
        'omega_surface': _surface(omega_model, omega + [0., 1.5, radius + 1.4], np),
        'omega_local_radius': radius,
    }


def _sled_pose(t, orbit_model, np):
    p = sled_point(t, np)
    u = _ease((t - 62.34) / .94)
    offset = np.array([6.4 - 2.4*u, 3.4 + 1.2*u, 15.8 - 2.2*u])
    eye = _point(orbit_model, p + offset, np)
    # Gaze leads the physical payload slightly; no camera-relative actor.
    lead = sled_point(t + .045, np)
    target = _point(orbit_model, p*.68 + lead*.32 + [.25, .9, 0.], np)
    return eye, target, -.06 - .11*u, 64. - 2.*u


def _moon_pose(t, orbit_model, np):
    centre = np.asarray(MOON_CENTER, float)
    # A translating oblique near-side pass.  The camera does not circle the
    # lunar centre: X advances throughout while Y and Z change separately.
    offset = _curve(t, (
        (63.26, (-5.8, 6.7, 10.6)),
        (63.48, (-3.7, 5.1, 9.4)),
        (63.78, (3.4, 1.6, 9.0)),
        (64.06, (7.7, -2.0, 7.5)),
    ), np)
    focus = _curve(t, (
        (63.26, (-1.2, 1.8, 4.6)),
        (63.48, (-.9, 1.5, 4.8)),
        (63.78, (1.3, .35, 4.9)),
        (64.06, (3.0, -1.1, 4.3)),
    ), np)
    u = _ease((t - 63.28) / .78)
    return (_point(orbit_model, centre + offset, np),
            _point(orbit_model, centre + focus, np),
            -.17 + .32*u, 62. + 4.*u)


def _omega_pose(t, omega_model, np):
    centre = np.asarray((0., 0., -16.))
    offset = _curve(t, (
        (64.22, (-12., 6., 29.)),
        (64.72, (-7., 2.1, 23.)),
        (65.34, (1.0, -2.8, 17.3)),
        (65.94, (4.5, .4, 13.8)),
    ), np)
    u = _ease((t - 64.22) / 1.72)
    return (_point(omega_model, centre + offset, np),
            _point(omega_model, centre + [0., .7*(1.-u), 0.], np),
            .16 - .26*u, 66. + 5.*u)


def _mix_pose(a, b, u):
    return tuple(x * (1. - u) + y * u for x, y in zip(a, b))


def pursuit_camera(t, eye, target, roll, fov, *, orbit_model, omega_model, np):
    """Return an object-follow pose dict, or None outside [62.34, 65.94)."""
    if not START <= t < END:
        return None
    landmarks = pursuit_landmarks(t, orbit_model, omega_model, np=np)
    sled = _sled_pose(t, orbit_model, np)
    moon = _moon_pose(t, orbit_model, np)
    omega = _omega_pose(t, omega_model, np)
    if t < 63.26:
        pose = sled
        phase, subject, surface = 'payload_chase', 'NVDA', 'nvda_surface'
    elif t < MOON_LASH[0]:
        handoff = _ease((t - 63.26) / .19)
        pose = _mix_pose(sled, moon, handoff)
        phase, subject, surface = 'lunar_relief_skim', 'moon', 'moon_surface'
    elif t < MOON_LASH[1]:
        handoff = _ease((t - MOON_LASH[0]) / (MOON_LASH[1] - MOON_LASH[0]))
        pose = _mix_pose(moon, omega, handoff)
        # An upward whip banks through the actual intervening space.  This
        # single finite displacement is unrelated to rhythmic screen shake.
        lift = math.sin(math.pi * handoff)
        pose = (pose[0] + _vector(orbit_model, [0., 2.8*lift, 0.], np),
                pose[1], pose[2] - .20*lift, 66. + 8.*lift)
        phase, subject, surface = 'moon_to_omega_lash', 'moon', 'moon_surface'
    else:
        pose = omega
        phase, subject, surface = 'omega_convergence', 'Omega', 'omega_surface'
    entry = _ease((t - START) / .16)
    original = (np.asarray(eye, float), np.asarray(target, float), float(roll), float(fov))
    pose = _mix_pose(original, pose, entry)
    return {
        'active': True, 'eye': pose[0], 'target': pose[1],
        'roll': float(pose[2]), 'fov': float(pose[3]),
        'phase': phase, 'subject': subject, 'entry_blend': entry,
        'subject_position': landmarks[{'NVDA': 'sled', 'moon': 'moon', 'Omega': 'omega'}[subject]],
        'surface_matrix': landmarks[surface], 'landmarks': landmarks,
        'cut_out': END,
    }


if __name__ == '__main__':
    import json
    import numpy as np

    orbital = np.eye(4)
    omega = np.eye(4)
    omega[:3, 3] = [38., 4., -52.]
    samples = []
    for t in np.linspace(START, END-1.e-5, 721):
        pose = pursuit_camera(t, [0., 0., 20.], [0., 0., 0.], 0., 65.,
                              orbit_model=orbital, omega_model=omega, np=np)
        assert np.isfinite(pose['eye']).all() and np.isfinite(pose['target']).all()
        assert np.linalg.norm(pose['target'] - pose['eye']) > .1
        samples.append((float(t), pose))
    eye = np.asarray([p['eye'] for _, p in samples])
    report = {
        'finite_samples': len(samples),
        'three_axis_translation': np.ptp(eye, axis=0).tolist(),
        'path_distance': float(np.linalg.norm(np.diff(eye, axis=0), axis=1).sum()),
        'entry_matches_authored': bool(np.array_equal(samples[0][1]['eye'], [0., 0., 20.])),
        'moon_min_local_radius': min(float(np.linalg.norm(_moon_pose(t, orbital, np)[0]-np.array(MOON_CENTER)))
                                     for t in np.linspace(63.26, 64.06, 200)),
        'omega_end_clearance': float(np.linalg.norm(_omega_pose(END, omega, np)[0]-_point(omega, [0.,0.,-16.],np))
                                     - .65*(3.+8.5)),
        'phases': list(dict.fromkeys(p['phase'] for _, p in samples)),
    }
    assert report['entry_matches_authored']
    assert report['moon_min_local_radius'] > 6.2
    assert report['omega_end_clearance'] > 2.
    assert min(report['three_axis_translation']) > 15.
    print(json.dumps(report, indent=2))
