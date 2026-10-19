"""The last GO becomes a one-way plunge through an earthquake fault.

Pure standard library; all coordinates are world units and angles radians.
GO is sung at 94.060--94.860.  Its physical plane stays fixed, is completely
readable before the final rush, and is crossed at 94.800.  The camera keeps
going through a fracture gate, falling arch and rising fault until the real
95.910 cut.  No return-to-entry envelope is used and no P(doom) is triggered.

Use sample_disaster(t) for post effects, seismic structure displacement and
timed gate metadata.  apply_disaster_camera has the same frozen-entry inputs
as v12's apply_flight_camera and returns absolute camera eye/target, a stable
world basis, velocity and the usual continuation corridor keys.  Pass focus
as the GO glyph centre carried by world travel, normal as its fixed plane
normal, and cache entry_eye/target/focus/roll/fov at START.  Do not transform
the GO glyph with the camera shake or with quake_displacement.

If the renderer reuses its own existing flight path, GO_FLIGHT_SPEC can be
turned into its Flight dataclass instead; sample_disaster is still useful
for earthquake geometry and chromatic separation.  Use one camera path,
not both.  Never apply post effects at or beyond HANDOFF.
"""

import math

START = 94.060
GO_READ_UNTIL = 94.660
GO_CROSSING = 94.800
GO_END = 94.860
HANDOFF = 95.910
GO_LYRIC_INDEX = 22
GO_TOKEN_INDEX = 5

# Compatible keyword arguments for v12 Flight(**GO_FLIGHT_SPEC).
GO_FLIGHT_SPEC = dict(time=94.300, name='GO DISASTER', handoff=HANDOFF,
                      read_end=GO_END, cross_age=.500, side=-1., rise=-.8,
                      bank=-34., pre=.240, crosses=True)

# Three genuinely different physical structures in one continuous corridor.
# These are placement times on the path, not cuts or whole-screen flashes.
GATES = (
    dict(time=94.800, name='GO', kind='glyph_plane', distance=0.,
         half_size=(8.5, 5.2), rotation=(0., 0., 0.)),
    dict(time=95.230, name='fault throat', kind='fracture', distance=44.,
         half_size=(11., 8.), rotation=(.08, -.12, -.19)),
    dict(time=95.435, name='falling arch', kind='collapse', distance=69.,
         half_size=(10., 7.), rotation=(-.17, .14, .38)),
    dict(time=95.680, name='rising fault', kind='vertical', distance=99.,
         half_size=(12., 9.), rotation=(.23, -.10, -.28)),
)

# Detected snare/onset attacks in rhythm_v3, plus the authored GO plane pass.
ATTACKS = ((94.300, .80), (94.800, 1.), (95.230, .64),
           (95.435, .90), (95.680, .58))


def _clamp(x, lo=0., hi=1.):
    return min(hi, max(lo, x))


def _smooth(x):
    x = _clamp(x)
    return x*x*(3.-2.*x)


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _mul(a, s):
    return tuple(x*s for x in a)


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a, fallback=(0., 0., -1.)):
    n = _norm(a)
    return _mul(a, 1./n) if n > 1.e-9 else tuple(fallback)


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _mix(a, b, p):
    return _add(_mul(a, 1.-p), _mul(b, p))


def _pchip(times, values, at):
    """Monotone cubic for depth, smooth sign-preserving lateral motion."""
    n = len(times)
    slopes = [(values[k+1]-values[k])/(times[k+1]-times[k])
              for k in range(n-1)]
    tangent = [0.]*n
    tangent[-1] = slopes[-1]
    for k in range(1, n-1):
        if slopes[k-1]*slopes[k] > 0.:
            h0, h1 = times[k]-times[k-1], times[k+1]-times[k]
            w0, w1 = 2*h1+h0, h1+2*h0
            tangent[k] = (w0+w1)/(w0/slopes[k-1]+w1/slopes[k])
    if at <= times[0]:
        return values[0], 0.
    if at >= times[-1]:
        return values[-1]+tangent[-1]*(at-times[-1]), tangent[-1]
    k = next(j for j in range(n-1) if at <= times[j+1])
    h = times[k+1]-times[k]
    u = (at-times[k])/h
    a, b, ma, mb = values[k], values[k+1], tangent[k], tangent[k+1]
    v = ((2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*h*ma
         +(-2*u**3+3*u*u)*b+(u**3-u*u)*h*mb)
    d = ((6*u*u-6*u)*a+(3*u*u-4*u+1)*h*ma
         +(-6*u*u+6*u)*b+(3*u*u-2*u)*h*mb)/h
    return v, d


def _track(t, depth=27., lateral=0., vertical=0.):
    # A long forward displacement dominates.  The vertical dive after the
    # letter gives way to an ascending dogleg through the last fault.
    keys = (START, 94.300, 94.640, GO_CROSSING,
            95.230, 95.435, 95.680, HANDOFF)
    coordinates = (
        (lateral, lateral*.75, -.80, 0., +8., -7., -10., +7.),
        (vertical, vertical*.75, +.7, 0., -11., -5., +11., +20.),
        (depth, depth*.94, 9., 0., -44., -69., -99., -136.),
    )
    out = [_pchip(keys, values, t) for values in coordinates]
    return tuple(v for v, d in out), tuple(d for v, d in out)


def sample_disaster(t):
    """Return local pose, post effects and earthquake structure parameters.

    chromatic is a normalized screen displacement for post blastFX.w;
    shake_local offsets only the camera. quake_displacement is stronger and
    offsets physical set pieces, whose far and near layers should use
    opposite signs.  GO itself remains on its static physical host plane.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('Disaster time must be finite')
    active = START <= t < HANDOFF
    local, velocity = _track(_clamp(t, START, HANDOFF))
    age = t-START
    load = _smooth((t-94.200)/.32)
    released = _smooth((t-94.660)/.14)
    pulse = max((s*math.exp(-(t-a)/.060) for a, s in ATTACKS if t >= a), default=0.)
    # Envelope ends at a real cut; it never eases the camera back to GO.
    amplitude = (.04+.20*load+.24*released+.30*pulse) if active else 0.
    shake = tuple(amplitude*v for v in (
        math.sin(age*111.)+.28*math.sin(age*173.),
        .72*math.sin(age*137.+.8)+.24*math.sin(age*211.),
        .32*math.sin(age*97.+1.7)))
    # The physical GO crossing remains exact even while the surrounding
    # structure shakes; suppress only the lens's normal-axis tremor here.
    normal_tremor = _smooth(abs(t-GO_CROSSING)/.045)
    shake = (shake[0]*normal_tremor, shake[1]*normal_tremor,
             shake[2]*normal_tremor)
    quake = tuple(v*amplitude for v in (
        2.8*math.sin(age*73.), 3.8*math.sin(age*91.+.2),
        1.7*math.sin(age*57.+2.)))
    # Bank follows the slalom rather than replacing translation with spin.
    bank = math.radians(-34.)*released
    bank += math.radians(18.)*math.sin((t-GO_CROSSING)*5.1)*released
    fov_delta = 3.*load+17.*released+5.*pulse
    chromatic = (.0012*load+.0055*released+.016*pulse) if active else 0.
    return dict(active=active, name='GO DISASTER' if active else None,
                start_time=START, event_time=94.300, handoff_time=HANDOFF,
                crossing_time=GO_CROSSING, read_until=GO_READ_UNTIL,
                word_read_end=GO_END, age=age,
                phase=('go_read' if t < GO_READ_UNTIL else 'glyph_pass'
                       if t < 94.900 else 'seismic_corridor'),
                local_eye=local, local_velocity=velocity,
                local_target=_add(local, _mul(_unit(velocity), 24.)),
                speed=_norm(velocity), roll=bank if active else 0.,
                fov_delta=fov_delta if active else 0.,
                chromatic=chromatic, aberration=chromatic,
                shock=pulse if active else 0., flash=.10*pulse if active else 0.,
                shake_local=shake, quake_displacement=quake,
                ground_break=load if active else 0.,
                collapse=_smooth((t-94.800)/.52) if active else 0.,
                fault_offsets=((quake[0], quake[1]-.8*load, quake[2]),
                               (-quake[0], -quake[1]+1.2*load, -quake[2]),
                               (quake[2], -1.8*released, quake[0])),
                gate_index=sum(t >= g['time'] for g in GATES)-1,
                gates=GATES, has_crossed=active and t >= GO_CROSSING,
                allow_word_clipping=active and t >= GO_READ_UNTIL,
                intentionally_crosses_word=active,
                crosses=active, kind='fracture',
                keep_go_plane_fixed=True, no_return_to_entry=True,
                freeze_safe=True)


def apply_disaster_camera(t, eye, target, roll, fov, focus=None, normal=None,
                          *, entry_eye=None, entry_target=None,
                          entry_roll=None, entry_fov=None, entry_focus=None):
    """Map the local path into GO's fixed physical frame without billboarding."""
    c = sample_disaster(t)
    bank = c['roll']
    eye, target = tuple(eye), tuple(target)
    c.update(eye=eye, target=target, fov=float(fov), roll=float(roll))
    if not c['active']:
        return c
    focus = tuple(target if focus is None else focus)
    e = tuple(eye if entry_eye is None else entry_eye)
    ef = tuple(focus if entry_focus is None else entry_focus)
    et = tuple(target if entry_target is None else entry_target)
    n = _unit((0., 0., 1.) if normal is None else normal)
    if _dot(_sub(e, ef), n) < 0.:
        n = _mul(n, -1.)
    incoming = _unit(_sub(et, e))
    right = _cross(incoming, (0., 1., 0.))
    right = _sub(right, _mul(n, _dot(right, n)))
    if _norm(right) < .025:
        right = _cross((0., 0., 1.), n)
    if _norm(right) < .025:
        right = _cross((0., 1., 0.), n)
    right = _unit(right)
    up = _unit(_cross(n, right))
    outward = _sub(e, ef)
    depth = max(8., _dot(outward, n))
    local, derivative = _track(float(t), depth, _dot(outward, right), _dot(outward, up))
    def world(v):
        return _add(_add(_mul(right, v[0]), _mul(up, v[1])), _mul(n, v[2]))
    # Small tremor is added after the authored 3-axis flight. It cannot
    # reverse the corridor or become the dominant form of movement.
    new_eye = _add(focus, world(_add(local, c['shake_local'])))
    velocity = world(derivative)
    tangent = _unit(velocity, _mul(n, -1.))
    aim = _smooth((float(t)-94.300)/.38)
    forward = _unit(_mix(incoming, tangent, aim))
    new_target = _add(new_eye, _mul(forward, 24.))
    base_roll = float(roll if entry_roll is None else entry_roll)
    base_fov = float(fov if entry_fov is None else entry_fov)
    c.update(eye=new_eye, target=new_target,
             roll=base_roll+bank,
             fov=_clamp(base_fov+c['fov_delta'], 48., 99.),
             velocity=velocity, speed=_norm(velocity),
             local_eye=local, local_velocity=derivative,
             plane_depth=local[2], signed_plane_depth=local[2],
             eye_displacement=_norm(_sub(new_eye, _add(e, _sub(focus, ef)))),
             flight_forward=forward, forward=forward,
             right=right, up=up, word_plane_normal=n,
             continuation_origin=_add(new_eye, _mul(forward, 19.)),
             continuation_word_normal=_mul(forward, -1.),
             maximum_word_fit_disabled=c['allow_word_clipping'])
    return c


def audit_disaster(fps=240):
    """Numerical flight audit; no renderer or third-party imports."""
    times = [START+i/fps for i in range(math.ceil((HANDOFF-START)*fps))]
    tracks = [_track(t) for t in times]
    depths = [p[2] for p, v in tracks]
    assert all(b <= a+1.e-9 for a, b in zip(depths, depths[1:]))
    at_plane = _track(GO_CROSSING)[0]
    assert max(abs(v) for v in at_plane) < 1.e-8
    assert GO_READ_UNTIL < GO_CROSSING < GO_END
    assert HANDOFF < 96.335
    assert all(not sample_disaster(t)['active'] for t in (93., HANDOFF, 96.335, 154.6, 156.))
    peak = max(_norm(v) for p, v in tracks)
    assert peak > 160.
    assert max(p[1] for p, v in tracks)-min(p[1] for p, v in tracks) > 28.
    assert max(p[0] for p, v in tracks)-min(p[0] for p, v in tracks) > 17.
    return dict(lyric_window=[START, GO_END], complete_read_before=GO_READ_UNTIL,
                crossing=GO_CROSSING, handoff=HANDOFF, peak_speed=peak,
                forward_distance=depths[0]-depths[-1],
                actual_x_y_z_translation=True, monotone_forward=True,
                fixed_glyph=True, continuous_scene_gates=len(GATES),
                distinct_measured_attacks=len(ATTACKS), no_pdoom_overlap=True,
                final_freeze_untouched=True)


if __name__ == '__main__':
    import json
    print(json.dumps(audit_disaster(), indent=2))
