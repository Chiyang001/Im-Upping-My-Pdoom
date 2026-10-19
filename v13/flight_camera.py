"""One-way FPV passes through a fixed, physical word plane.

This replaces the v11 impact orbit.  The four P(doom) words are approached
from their readable side, crossed on their last sung frames, and then left
behind the camera.  There is no return envelope: a flight stays in its new
corridor until the next accepted cut.  The renderer keeps glyphs fixed.

Recommended integration, before projection and instead of impact_camera:

    cue = sample_flight_camera(t)
    # Freeze these at cue['start_time'], using the ordinary shot camera:
    entry_eye, entry_target, entry_roll, entry_fov, entry_focus = ...
    move = apply_flight_camera(t, eye, target, roll, fov, focus, normal,
        event=cue['name'], entry_eye=entry_eye, entry_target=entry_target,
        entry_roll=entry_roll, entry_fov=entry_fov, entry_focus=entry_focus)

focus is the event word's world position carried by world travel; normal is
the same fixed word's +Z surface normal.  entry_focus is that world position
at start_time.  Explicit frozen entry values avoid a moving base shot bending
the trajectory.  The fallback current pose is useful for numerical previews.

After crossing, later words in this cut must be placed along the returned
continuation corridor, facing its incoming direction.  Leave the event word
at its physical host; do not billboard it, slide it toward the lens, aim the
camera backwards, or invoke the old whole-word FOV fit during an intentional
pass.  `allow_word_clipping` and `has_crossed` expose that distinction.

All positions are world units, angles radians, FOV degrees and speed units/s.
Only Python's standard library is required.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Flight:
    time: float
    name: str
    handoff: float
    read_end: float
    cross_age: float
    side: float
    rise: float
    bank: float
    pre: float = .08
    crosses: bool = True


# read_end is an absolute lexical time, independent of the visual shock.
# FUSE remains on its readable side: the following real cut occurs while
# that word is still sung, so a fast tangential skim supplies the flight.
FLIGHTS = (
    Flight(23.620, 'PDOOM 1', 25.685, 24.040, .365, +1., -.65, -24.),
    Flight(42.050, 'SINGULARITY', 44.790, 44.020, 2.025, -.8, -1., +19., 0.),
    Flight(49.785, 'ATOMS', 53.885, 49.900, .420, +.9, +.8, -18.),
    Flight(59.985, 'PDOOM 2', 65.920, 60.300, .260, -1., +1.0, +27.),
    Flight(96.335, 'PDOOM 3', 98.845, 96.680, .290, +.8, -.9, -22.),
    Flight(103.870, 'FUSE', 104.330, 104.540, 9., -1., +.7, +15., .06, False),
    Flight(117.505, 'SAFETY FENCE', 118.645, 117.620, .420, -.8, +1., +23.),
    Flight(125.460, 'PDOOM 4', 127.960, 125.860, .345, -1., -.75, +25.),
    Flight(131.140, 'SELF UPGRADE', 133.430, 131.460, .375, +.9, +.8, -20.),
)
# Additional word-driven flights are independent of the explosion score.
FLIGHTS=tuple(sorted(FLIGHTS+(
    Flight(10.520,'LOSS DROP',12.990,10.980,.405,+1.,-1.,-27.,.20),
    Flight(47.440,'ACCELERATING',48.645,48.640,1.140,+.6,+.5,+28.,.20),
    Flight(76.420,'FEEDBACK REPEAT',77.240,77.340,.760,-1.,+.7,+31.,.12),
    Flight(94.300,'GO DISASTER',95.910,94.860,.500,-1.,-.8,-34.,.240),
    Flight(114.220,'DISOBEY',116.595,115.000,.720,-1.,+.65,-30.,.12),
    Flight(121.760,'ASKEW',123.870,122.540,.725,+1.,-.6,+32.,.12),
    Flight(139.580,'SHOW EXIT',141.140,140.480,.845,-.7,+.8,-24.,.15),
),key=lambda f:f.time))
_BY_NAME = {f.name: f for f in FLIGHTS}


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


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a, fallback=(0., 0., -1.)):
    length = _norm(a)
    return _mul(a, 1./length) if length > 1.e-9 else tuple(fallback)


def _mix(a, b, p):
    return _add(_mul(a, 1.-p), _mul(b, p))


def _event(event):
    name = event if isinstance(event, str) else (
        event.get('name') if isinstance(event, dict) else event.name)
    return _BY_NAME.get(name)


def sample_flight_camera(t, event=None, handoff_time=None, *, allow_after_handoff=False):
    """Return the active cue, persisting through the next authored cut.

    handoff_time may select a newly authored occlusion/cut, but is never an
    easing-back deadline.  It must follow the planned word crossing.
    `allow_after_handoff=True`, with an explicit event, exposes the exact
    same path's linear continuation for positioning a fixed future word
    gate.  Ordinary rendering leaves it False and releases at the real cut.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('Flight camera requires a finite time')
    if allow_after_handoff and event is None:
        raise ValueError('Future path queries require an explicit event')
    candidates = (_event(event),) if event is not None else FLIGHTS
    for f in candidates:
        if f is None:
            continue
        end = float(f.handoff if handoff_time is None else handoff_time)
        if f.crosses and end <= f.time+f.cross_age:
            raise ValueError('A flight handoff must follow the word crossing')
        if f.time-f.pre <= t and (t < end or allow_after_handoff):
            age = t-f.time
            return dict(active=True, name=f.name, start_time=f.time-f.pre,
                        event_time=f.time, handoff_time=end, age=age,
                        duration=end-f.time, read_until=f.read_end,
                        crossing_time=f.time+f.cross_age if f.crosses else None,
                        crosses=f.crosses, side=f.side, rise=f.rise,
                        after_handoff=t >= end,
                        bank_degrees=f.bank, pre=f.pre,
                        phase=('load' if age < .06 else 'approach'
                               if not f.crosses or age < f.cross_age-.07
                               else 'plane_pass' if age < f.cross_age+.13
                               else 'forward_corridor'),
                        allow_word_clipping=f.crosses and t >= f.read_end-.145,
                        has_crossed=f.crosses and age >= f.cross_age)
    return dict(active=False, name=None, phase='shot', allow_word_clipping=False,
                has_crossed=False, crosses=False, age=None)


def _pchip(times, values, at):
    """C1 cubic interpolation with sign-preserving scalar derivatives.

    In particular, the plane-depth coordinate cannot reverse between keys.
    """
    n = len(times)
    slope = [(values[k+1]-values[k])/(times[k+1]-times[k])
             for k in range(n-1)]
    tangent = [0.]*n
    tangent[-1] = slope[-1]
    for k in range(1, n-1):
        if slope[k-1]*slope[k] > 0.:
            h0, h1 = times[k]-times[k-1], times[k+1]-times[k]
            w0, w1 = 2*h1+h0, h1+2*h0
            tangent[k] = (w0+w1)/(w0/slope[k-1]+w1/slope[k])
    if at <= times[0]:
        return values[0], 0.
    k = min(n-2, next((j for j in range(n-1) if at <= times[j+1]), n-2))
    h = times[k+1]-times[k]
    u = _clamp((at-times[k])/h)
    a, b, ma, mb = values[k], values[k+1], tangent[k], tangent[k+1]
    value = ((2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*h*ma
             +(-2*u**3+3*u*u)*b+(u**3-u*u)*h*mb)
    velocity = ((6*u*u-6*u)*a+(3*u*u-4*u+1)*h*ma
                +(-6*u*u+6*u)*b+(3*u*u-2*u)*h*mb)/h
    return value, velocity


def _local_track(c, depth, lateral, vertical):
    age, side, rise = c['age'], c['side'], c['rise']
    if age > c['duration']:
        edge = dict(c, age=c['duration'])
        position, velocity = _local_track(edge, depth, lateral, vertical)
        return _add(position, _mul(velocity, age-c['duration'])), velocity
    if not c['crosses']:
        q = max(0., age-.035)
        ramp = _smooth(q/.14)
        return ((lateral+side*46.*q*ramp,
                 vertical+rise*22.*q*ramp, depth-11.*q*ramp),
                (side*46.*ramp, rise*22.*ramp, -11.*ramp))
    cross = c['crossing_time']-c['event_time']
    duration = c['duration']
    tail = min(cross+.76, duration-.025)
    # A fast push dominates the movement; side/up keys create real parallax.
    # Both tangent coordinates hit zero at the plane: the lens actually
    # passes through the word's centre rather than circling around its face.
    times = [-c['pre'], .055, min(.20, cross-.13), cross-.07,
             cross, cross+.13, tail, duration]
    # Singularities retain their long readable word while the approach
    # translates laterally/downward.  Their final plane pass is still fast.
    tail_depth = -min(36., 12.+(tail-cross-.13)*40.)
    final_depth = max(-98., tail_depth-max(.05, (duration-tail)*15.))
    xs = [lateral, lateral, lateral*.56+side*1.2, side*.20,
          0., side*1.7, side*3.6, side*(3.6+(duration-tail)*.45)]
    ys = [vertical, vertical, vertical*.56+rise*.85, rise*.16,
          0., rise*1.3, rise*3.0, rise*(3.0+(duration-tail)*.45)]
    vals = [_pchip(times, values, age) for values in (xs, ys)]

    def hermite(a, b, va, vb, da, db):
        h = b-a
        u = _clamp((age-a)/h)
        value = ((2*u**3-3*u*u+1)*va+(u**3-2*u*u+u)*h*da
                 +(-2*u**3+3*u*u)*vb+(u**3-u*u)*h*db)
        velocity = ((6*u*u-6*u)*va+(3*u*u-4*u+1)*h*da
                    +(-6*u*u+6*u)*vb+(3*u*u-2*u)*h*db)/h
        return value, velocity
    crossing_speed = _clamp(depth/(cross+c['pre'])*1.15, 65., 115.)
    if cross > 1. and age <= cross-.35:
        normal_track = hermite(-c['pre'], cross-.35, depth,
                               min(23., depth*.72), 0., -6.)
    elif cross > 1. and age <= cross:
        normal_track = hermite(cross-.35, cross, min(23., depth*.72),
                               0., -6., -crossing_speed)
    elif age <= cross:
        normal_track = hermite(-c['pre'], cross, depth, 0., 0., -crossing_speed)
    elif age <= cross+.13:
        normal_track = hermite(cross, cross+.13, 0., -12., -crossing_speed, -85.)
    elif age <= tail:
        normal_track = hermite(cross+.13, tail, -12., tail_depth, -85., -15.)
    else:
        terminal_speed = (final_depth-tail_depth)/(duration-tail)
        normal_track = hermite(tail, duration, tail_depth, final_depth,
                               -15., terminal_speed)
    vals.append(normal_track)
    return tuple(v[0] for v in vals), tuple(v[1] for v in vals)


def apply_flight_camera(t, eye, target, roll, fov, focus=None, normal=None,
                        event=None, *, text_normal=None, entry_eye=None,
                        entry_target=None, entry_roll=None, entry_fov=None,
                        entry_focus=None, handoff_time=None,
                        allow_after_handoff=False):
    """Return an absolute pose, world velocity, and a future-word corridor.

    `eye`/`target` are only the unmodified fallback outside a flight.  Supply
    all five entry values for a stable render; they are ordinary tuples and
    floats and can be cached by cue name.  The initial face side is selected
    once from entry_eye, allowing overhead / floor words to work naturally.
    """
    eye, target = tuple(map(float, eye)), tuple(map(float, target))
    c = sample_flight_camera(t, event, handoff_time,
                            allow_after_handoff=allow_after_handoff)
    result = dict(c, eye=eye, target=target, roll=float(roll), fov=float(fov),
                  eye_displacement=0., speed=0., plane_depth=None,
                  signed_plane_depth=None, velocity=(0., 0., 0.),
                  flight_forward=_unit(_sub(target, eye)),
                  intentionally_crosses_word=False)
    if not c['active']:
        return result
    focus = tuple(map(float, target if focus is None else focus))
    entry_eye = tuple(map(float, eye if entry_eye is None else entry_eye))
    entry_target = tuple(map(float, target if entry_target is None else entry_target))
    entry_focus = tuple(map(float, focus if entry_focus is None else entry_focus))
    entry_roll = float(roll if entry_roll is None else entry_roll)
    entry_fov = float(fov if entry_fov is None else entry_fov)
    n = _unit(tuple(normal if normal is not None else text_normal
                    if text_normal is not None else (0., 0., 1.)))
    outward = _sub(entry_eye, entry_focus)
    if _dot(outward, n) < 0.:
        n = _mul(n, -1.)
    incoming = _unit(_sub(entry_target, entry_eye))
    right = _cross(incoming, (0., 1., 0.))
    right = _sub(right, _mul(n, _dot(right, n)))
    if _norm(right) < .025:
        right = _cross((0., 0., 1.), n)
    if _norm(right) < .025:
        right = _cross((0., 1., 0.), n)
    right = _unit(right)
    up = _unit(_cross(n, right))
    depth = max(8., _dot(outward, n))
    lateral, vertical = _dot(outward, right), _dot(outward, up)
    local, derivative = _local_track(c, depth, lateral, vertical)
    def world(v):
        return _add(_add(_mul(right, v[0]), _mul(up, v[1])), _mul(n, v[2]))
    new_eye = _add(focus, world(local))
    velocity = world(derivative)
    travel_forward = _unit(velocity, _mul(n, -1.))
    # Early aim is the original shot; at the word it is the flight tangent.
    # Past the plane the camera never turns around to watch the back face.
    aim_mix = _smooth((c['age']-.055)/max(.12,
        (c['crossing_time']-c['event_time']-.09) if c['crosses'] else .18))
    forward = _unit(_mix(incoming, travel_forward, aim_mix), travel_forward)
    new_target = _add(new_eye, _mul(forward, 24.))
    banking = _smooth((c['age']-.10)/.25)
    release_bank = 1.-.65*_smooth((c['age']-.8)/.65)
    bank = math.radians(c['bank_degrees'])*banking*release_bank
    aperture = 12.*_smooth((c['age']-.10)/.24)
    result.update(eye=new_eye, target=new_target, roll=entry_roll+bank,
                  fov=_clamp(entry_fov+aperture, 42., 98.),
                  eye_displacement=_norm(_sub(new_eye,
                      _add(entry_eye, _sub(focus, entry_focus)))),
                  speed=_norm(velocity), velocity=velocity,
                  plane_depth=local[2], signed_plane_depth=local[2],
                  flight_forward=forward, forward=forward,
                  right=right, up=up, word_plane_normal=n,
                  continuation_origin=_add(new_eye, _mul(forward, 19.)),
                  continuation_word_normal=_mul(forward, -1.),
                  intentionally_crosses_word=c['crosses'],
                  no_return_to_entry=True,
                  maximum_word_fit_disabled=c['allow_word_clipping'])
    return result


def audit_flight_camera(fps=240):
    """Numerical audit: signed crossing, forward velocity, no reverse exit."""
    rows = []
    for f in FLIGHTS:
        common = dict(eye=(8., -6., 28.), target=(0., 0., -7.), roll=0.,
                      fov=62., focus=(0., 0., -4.), normal=(0., 0., 1.),
                      event=f.name, entry_eye=(8., -6., 28.),
                      entry_target=(0., 0., -7.), entry_focus=(0., 0., -4.))
        count = math.ceil((f.handoff-f.time+f.pre)*fps)
        moves = [apply_flight_camera(f.time-f.pre+j/fps, **common)
                 for j in range(count) if f.time-f.pre+j/fps < f.handoff]
        depths = [x['plane_depth'] for x in moves]
        assert all(b <= a+1.e-8 for a, b in zip(depths, depths[1:])), f.name
        max_speed = max(x['speed'] for x in moves)
        displacement = max(x['eye_displacement'] for x in moves)
        assert max_speed > 45., (f.name, max_speed)
        if f.crosses:
            at_plane = apply_flight_camera(f.time+f.cross_age, **common)
            assert abs(at_plane['plane_depth']) < 1.e-7, f.name
            narrative=f.name in {'LOSS DROP','ACCELERATING','FEEDBACK REPEAT','GO DISASTER','DISOBEY','ASKEW','SHOW EXIT'}
            if f.name.startswith('PDOOM'):assert f.read_end-.07 <= f.time+f.cross_age <= f.read_end-.035, f.name
            elif narrative:assert f.time < f.time+f.cross_age < f.read_end, f.name
            else:assert f.time+f.cross_age >= f.read_end+.04, f.name
            assert depths[0] > 0. and depths[-1] < (-1. if narrative else -10.), f.name
            assert _dot(at_plane['flight_forward'], (0., 0., -1.)) > .85, f.name
            # Once behind the word, look and velocity remain into the new
            # scene, not back at the text to simulate a circular flyaround.
            assert all(_dot(x['flight_forward'], (0., 0., -1.)) > .45
                       for x in moves if x['has_crossed']), f.name
        rows.append(dict(name=f.name, crosses_word=f.crosses,
                         crossing_time=f.time+f.cross_age if f.crosses else None,
                         word_read_end=f.read_end, handoff=f.handoff,
                         initial_plane_depth=depths[0], final_plane_depth=depths[-1],
                         peak_speed=max_speed, maximum_displacement=displacement,
                         monotone_forward=True))
    return dict(events=rows, pdoom_crossings=4,
                one_way_until_real_cut=True, word_billboarding=False,
                old_orbit_or_recoil=False)


if __name__ == '__main__':
    import json
    print(json.dumps(audit_flight_camera(), indent=2))
