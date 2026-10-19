"""A continuous, beat-thrust FPV ending through nine physical story rooms.

No renderer, numpy, or geometry dependency is required.  The camera moves
through *fixed* world-space instances; never parent these instances to the
camera.  This is the difference between flight and an object held on stage.

Integration:
    old = sample_outro(t)
    flight = sample_outro_flight(t)
    if flight['active']:
        old.update({k: flight[k] for k in
                    ('camera_eye', 'camera_target', 'roll', 'fov')})
    for scene in flight['geometry_instances']:
        for draw in scene['draws']:
            EPILOGUE[draw['mesh']].draw(np.array(draw['model']), vp, ...)

``draw.model`` is an ordinary row-major 4x4 object-to-world transform.  Pass
it straight to the renderer's GPU.draw, which already uploads transposes.
Use draw.gain/reveal/action/motion as the corresponding draw parameters;
keep the original time and measured drum pulse.  Existing signal/trail can
use witness_path and the local point witness.  The nine rooms overlap in
depth, so the next consequence is visible before the camera leaves one.

Retain the accepted infinity in its existing world coordinates from 152.5;
this is the distant destination of the final passage.  Reveal its existing
title/credit assembly from 153.95 onward. The flight ends at (0,1,35), then
settles to the title camera, target (0,0,0), FOV58.  Freeze all rendering at
154.6 as before.  Title reveal can run 153.95->154.35 and credit
154.08->154.45.  This prevents a giant title being seen edge-on in transit.
"""

from bisect import bisect_right
import math

START = 141.2
FLIGHT_END = 153.95
FREEZE_TIME = 154.6
START_Z = 620.0
END_Z = 35.0
TOTAL_DISTANCE = START_Z - END_Z

BEATS = (
    141.140, 141.595, 142.050, 142.505, 142.960, 143.415,
    143.870, 144.320, 144.775, 145.230, 145.685, 146.140,
    146.595, 147.060, 147.505, 147.970, 148.415, 148.880,
    149.320, 149.775, 150.230, 150.700, 151.140, 151.595,
    152.050, 152.505, 152.960, 153.415, 153.870, 154.325,
)
STRENGTHS = (
    1., .7258, 1., .7699, .9904, .7126, 1., .9183, 1., .9193,
    1., .8402, 1., .9529, 1., .8842, 1., .9087, 1., .7736,
    1., .9487, 1., .8115, 1., .7302, .4301, .409, .4036, .4019,
)


def _clamp(x, lo=0., hi=1.):
    return min(hi, max(lo, x))


def _ease(x):
    x = _clamp(x)
    return x*x*(3.-2.*x)


def _mix(a, b, p):
    return tuple(x+(y-x)*p for x, y in zip(a, b))


def _unit(v):
    d = math.sqrt(sum(x*x for x in v))
    return tuple(x/max(1.e-12, d) for x in v)


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _speed(t):
    # Positive speed is integrated.  A drum attack adds thrust rather than
    # moving the eye forward and then snapping it back to the previous pose.
    speed = 35.
    for bt, strength in zip(BEATS, STRENGTHS):
        x = (t-bt)/.067
        if 0. <= x < 9.:
            speed += 124.*strength*x*math.exp(-x)
    # Coast into the final engraving; no reversal or camera teleport.
    return speed*(1.-_ease((t-153.16)/.79))


_DT = 1./1200.
_N = math.ceil((FLIGHT_END-START)/_DT)
_TIMES = tuple(START+(FLIGHT_END-START)*i/_N for i in range(_N+1))
_RAW = [0.]
for _i in range(_N):
    _RAW.append(_RAW[-1]+(_speed(_TIMES[_i])+_speed(_TIMES[_i+1]))*
                (_TIMES[_i+1]-_TIMES[_i])*.5)
_NORMALIZER = TOTAL_DISTANCE/_RAW[-1]
_DISTANCES = tuple(v*_NORMALIZER for v in _RAW)


def distance_at(t):
    """Monotonically increasing travelled distance, in world units."""
    if t <= START:
        return 0.
    if t >= FLIGHT_END:
        return TOTAL_DISTANCE
    i = min(_N-1, bisect_right(_TIMES, t)-1)
    p = (t-_TIMES[i])/(_TIMES[i+1]-_TIMES[i])
    return _DISTANCES[i]+(_DISTANCES[i+1]-_DISTANCES[i])*p


# Each control is physical lateral/vertical displacement at a route distance.
# Cubic Hermite tangent interpolation keeps the entire take C1-continuous.
# The last controls align the route with the engraving's unmodified camera.
_ROUTE = (
    (0., -4., -1.), (.085, -21., 8.), (.175, 12., -12.),
    (.285, 25., 16.), (.385, -17., 25.), (.490, -28., -10.),
    (.590, 20., -22.), (.690, 29., 12.), (.790, -21., 19.),
    (.875, -14., -8.), (.935, 0., 1.), (.975, 0., 1.),
    (1., 0., 1.),
)
_ROUTE_Q = tuple(v[0] for v in _ROUTE)


def _slope(i, axis):
    if i == 0:
        return (_ROUTE[1][axis]-_ROUTE[0][axis])/(_ROUTE[1][0]-_ROUTE[0][0])
    if i >= len(_ROUTE)-1:
        return 0.
    return ((_ROUTE[i+1][axis]-_ROUTE[i-1][axis])/
            (_ROUTE[i+1][0]-_ROUTE[i-1][0]))


def route_point(distance):
    """World-space route centre.  Increasing distance always decreases z."""
    q = _clamp(distance/TOTAL_DISTANCE)
    i = min(len(_ROUTE)-2, max(0, bisect_right(_ROUTE_Q, q)-1))
    a, b = _ROUTE[i], _ROUTE[i+1]
    width = b[0]-a[0]
    u = _clamp((q-a[0])/width)
    h00, h10 = 2*u**3-3*u*u+1, u**3-2*u*u+u
    h01, h11 = -2*u**3+3*u*u, u**3-u*u
    xy = tuple(h00*a[axis]+h10*width*_slope(i, axis)+
               h01*b[axis]+h11*width*_slope(i+1, axis)
               for axis in (1, 2))
    return (*xy, START_Z-distance)


def route_frame(distance):
    """Local +z faces backwards; local -z follows the physical flight path."""
    p = route_point(distance)
    pa = route_point(distance-1.)
    pb = route_point(distance+1.)
    forward = _unit(tuple(b-a for a, b in zip(pa, pb)))
    right = _unit(_cross(forward, (0., 1., 0.)))
    up = _unit(_cross(right, forward))
    return (
        (right[0], up[0], -forward[0], p[0]),
        (right[1], up[1], -forward[1], p[1]),
        (right[2], up[2], -forward[2], p[2]),
        (0., 0., 0., 1.),
    )


def _mm(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(4))
                       for j in range(4)) for i in range(4))


def _model(position=(0., 0., 0.), rotation=(0., 0., 0.), scale=(1., 1., 1.)):
    rx, ry, rz = rotation
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    ax = ((1.,0.,0.,0.),(0.,cx,-sx,0.),(0.,sx,cx,0.),(0.,0.,0.,1.))
    ay = ((cy,0.,sy,0.),(0.,1.,0.,0.),(-sy,0.,cy,0.),(0.,0.,0.,1.))
    az = ((cz,-sz,0.,0.),(sz,cz,0.,0.),(0.,0.,1.,0.),(0.,0.,0.,1.))
    tr = ((1.,0.,0.,position[0]),(0.,1.,0.,position[1]),
          (0.,0.,1.,position[2]),(0.,0.,0.,1.))
    sc = ((scale[0],0.,0.,0.),(0.,scale[1],0.,0.),
          (0.,0.,scale[2],0.),(0.,0.,0.,1.))
    return _mm(tr, _mm(ay, _mm(ax, _mm(az, sc))))


# Centres are consecutive measured attacks.  Stage order remains causal:
# replication -> captured world -> fractured machine -> infinite return.
SCENES = (
    (1, 0, 'synapse_cut', 'The witness enters the conductive nerve.'),
    (4, 0, 'replication_banks', 'The same route copies into flanking banks.'),
    (7, 0, 'nervous_spine', 'The banks join one long machine spine.'),
    (10, 1, 'orbital_jaws', 'The spine pierces the captive world cage.'),
    (13, 1, 'severed_plates', 'World plates tear into the machine intake.'),
    (16, 2, 'buckling_ribs', 'The overloaded ribs crush around the route.'),
    (19, 2, 'shard_inversion', 'The shell fractures behind the witness.'),
    (22, 2, 'recursive_rooms', 'The broken rooms propagate into nested copies.'),
    (25, 3, 'infinite_exit', 'The nested route opens into the final loop.'),
)
_CENTRES = tuple(distance_at(BEATS[b]) for b, *_ in SCENES)


def _local_draws(scene_id, local_progress, pulse):
    """Distinct open structures, not nine copies of a rectangular portal."""
    out = []
    def add(mesh, pos=(0.,0.,0.), rot=(0.,0.,0.), scale=(1.,1.,1.),
            gain=1., reveal=1., action=0., motion=-1):
        out.append(dict(mesh=mesh, local_model=_model(pos, rot, scale),
                        gain=gain, reveal=reveal, action=action, motion=motion))
    p = _clamp(local_progress)
    if scene_id == 0:
        # Lateral vascular highways are rotated into the flight direction.
        for side in (-1, 1):
            add('network', (side*10., side*1.5, 0.), (0., math.pi/2, side*.28),
                (1.6,.78,1.), .82+pulse*.35)
        add('spine', (0.,-7.,-6.), (0.,math.pi/2,0.), (1.4,1.,1.), .8)
    elif scene_id == 1:
        for lane in (-1,0,1):
            add('recursive', (lane*15., lane*3., -lane*5.), (0.,0.,lane*.18),
                (.72,.85,1.5), .78+pulse*.35, min(1.,.35+p))
        add('network', (0.,-8.,0.), (0.,math.pi/2,0.), (1.3,.65,1.), .7)
    elif scene_id == 2:
        for side in (-1,1):
            add('spine', (side*9.,0.,0.), (0.,math.pi/2,side*.4),
                (1.7,1.0,1.), .9+pulse*.4)
        add('clamps', (0.,0.,-7.), (.2,0.,.4), (1.0,1.35,1.5), 1.)
    elif scene_id == 3:
        add('world', (0.,0.,-4.), (0.,.4,0.), (2.0,2.0,2.0), .8+pulse*.4)
        add('clamps', (0.,0.,0.), (0.,0.,.32), (1.45,1.8,1.6), 1.1)
        add('clamps', (0.,0.,-12.), (0.,0.,1.7), (1.65,1.5,1.4), .82)
    elif scene_id == 4:
        add('shell', (0.,0.,0.), (.18,.25,.28), (1.8,1.8,1.9), .9+pulse*.4,
            action=.2+p*.45, motion=42)
        for side in (-1,1):
            add('network', (side*12.,0.,-5.), (0.,math.pi/2,side*.35),
                (1.1,.8,1.), .7)
        add('clamps', (0.,0.,-13.), (0.,0.,-.6), (1.05,1.3,1.), .85)
    elif scene_id == 5:
        for j in range(3):
            add('clamps', (0.,0.,7.-j*12.), (0.,0.,j*.52),
                (1.15-p*.2,1.8-p*.35,1.0), .92+pulse*.35)
        add('spine', (0.,-9.,0.), (0.,math.pi/2,0.), (1.9,.9,1.), .75)
    elif scene_id == 6:
        add('shell', (0.,0.,0.), (.35,1.,-.25), (2.,2.,2.), 1.05+pulse*.4,
            action=.35+p*.4, motion=41)
        add('network', (0.,-7.,-10.), (0.,math.pi/2,.2), (1.2,.8,1.), .64)
    elif scene_id == 7:
        for j in range(4):
            add('recursive', (math.sin(j*1.3)*3., math.cos(j*.9)*2., 14.-j*13.),
                (.08*j,0.,(-1 if j%2 else 1)*.23),
                (1.15-j*.1,1.15-j*.06,1.), .9/(1+j*.12)+pulse*.2)
    else:
        # The last branching array gives way to an open two-lobed route;
        # root renders the accepted infinity and inscription after passage.
        for side in (-1,1):
            add('recursive', (side*12.,side*2.,-4.), (0.,side*.25,side*.45),
                (.75,1.15,1.), .52+pulse*.2)
        add('spine', (0.,-8.,-8.), (0.,math.pi/2,0.), (1.2,.65,1.), .55)
        for side in (-1,1):
            add('network', (side*10.,side*3.,-31.),
                (0.,math.pi/2,side*.4), (.9,.6,.8), .45)
    return out


def geometry_instances(t, distance=None, pulse=0.):
    """Return only nearby fixed scene instances; world positions never chase eye."""
    d = distance_at(t) if distance is None else distance
    result = []
    for i, ((beat, stage, name, story), centre) in enumerate(zip(SCENES, _CENTRES)):
        ahead = centre-d
        if not -80. <= ahead <= 176.:
            continue
        frame = route_frame(centre)
        local = _clamp((t-(BEATS[beat]-.65))/1.25)
        draws = []
        for draw in _local_draws(i, local, pulse):
            draw = dict(draw)
            draw['model'] = _mm(frame, draw.pop('local_model'))
            draws.append(draw)
        result.append(dict(scene=i, stage=stage, name=name, story=story,
                           arrival_time=BEATS[beat], distance=centre,
                           ahead=ahead, position=route_point(centre), matrix=frame,
                           progress=local, draws=draws))
    return result


def sample_outro_flight(t):
    """Absolute FPV pose plus fixed scene models and beat-local shock values."""
    if not math.isfinite(t):
        raise ValueError('outro time must be finite')
    active = t >= START
    q = min(FREEZE_TIME, max(START, float(t)))
    d = distance_at(q)
    beat = min(len(BEATS)-1, max(0, bisect_right(BEATS, q)-1))
    age = max(0., q-BEATS[beat])
    pulse = STRENGTHS[beat]*math.exp(-age/.085)
    thrust = _speed(min(q, FLIGHT_END))*_NORMALIZER
    eye = route_point(d)
    # Look ahead follows actual future route.  Yaw and pitch express changes
    # of direction; banking is a supporting consequence of these movements.
    look_distance = 24.+pulse*5.
    target = route_point(d+look_distance)
    a = route_point(d-5.)
    b = route_point(d+5.)
    c = route_point(d+15.)
    lateral_bend = (c[0]-b[0])-(b[0]-a[0])
    roll = _clamp(-lateral_bend*.12, -.92, .92)
    roll += math.sin((q-START)*1.4)*.075
    fov = 88.+pulse*8.+min(6., thrust*.045)
    # Vanishing direction aligns in advance.  The final 0.65 s is a smooth
    # lens/attitude settle at the exact existing title camera, not a cut.
    finish = _ease((q-153.415)/(FREEZE_TIME-153.415))
    target = _mix(target, (0.,0.,0.), finish)
    roll *= 1.-finish
    fov += (58.-fov)*finish
    if q >= FLIGHT_END:
        eye = (0.,1.,35.)
    if q >= FREEZE_TIME:
        eye, target, roll, fov = (0.,1.,35.), (0.,0.,0.), 0., 58.
        pulse, thrust = 0., 0.
    scene_id = min(len(SCENES)-1, max(0, bisect_right(_CENTRES, d)-1))
    stage = SCENES[scene_id][1]
    # A red physical route remains ahead of the lens, linking all nine rooms.
    witness = route_point(min(TOTAL_DISTANCE+10., d+30.))
    witness_path = tuple(route_point(d+u) for u in range(-12, 77, 2))
    return dict(
        active=active, freeze=t>=FREEZE_TIME, render_time=q,
        camera_eye=eye, camera_target=target, eye=eye, target=target,
        roll=roll, fov=fov, up=(0.,1.,0.),
        distance=d, total_distance=TOTAL_DISTANCE, speed=thrust,
        beat_index=beat, beat_time=BEATS[beat], beat_elapsed=age, pulse=pulse,
        scene=scene_id, stage=stage, scene_name=SCENES[scene_id][2],
        geometry_instances=geometry_instances(q, d, pulse) if q<FLIGHT_END else [],
        witness=witness, witness_path=witness_path,
        flight_gain=1.-_ease((q-153.415)/.535), settle=finish,
        # Use a restrained short post impulse; motion is provided by geometry.
        chromatic=.0015*pulse*(1.-finish), quake=.010*pulse*(1.-finish),
        transition=dict(active=False, kind='none', phase=1., strength=0.,
                        frames=0, axis='z', direction=1., anchor=(.5,.5)),
    )


if __name__ == '__main__':
    prev = sample_outro_flight(START)
    highest_step = 0.
    for frame in range(1, math.ceil((FREEZE_TIME-START)*120)+1):
        t = min(FREEZE_TIME, START+frame/120.)
        now = sample_outro_flight(t)
        assert now['distance'] >= prev['distance']-1.e-9
        assert now['camera_eye'][2] <= prev['camera_eye'][2]+1.e-9
        step = math.dist(now['camera_eye'], prev['camera_eye'])
        highest_step = max(highest_step, step)
        assert all(math.isfinite(v) for v in (*now['camera_eye'], *now['camera_target']))
        assert math.dist(now['camera_eye'], now['camera_target'])>2.
        prev = now
    end = sample_outro_flight(FREEZE_TIME)
    for t in (154.7,155.,156.,156.667):
        assert sample_outro_flight(t)==end
    assert end['camera_eye']==(0.,1.,35.) and end['fov']==58.
    assert len(SCENES)==9 and len({s[2] for s in SCENES})==9
    print('continuous outro FPV: 585 forward world units, 9 fixed physical scenes, 30 measured beats')
    print('maximum 120 fps eye step:', round(highest_step,4))
    print('final camera and entire state hold exactly from154.6 through156.667')
