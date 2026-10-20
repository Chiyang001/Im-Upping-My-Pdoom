"""A physical infinity accelerator, followed by a moving return through its iris.

The whole sculpture lives in fixed world coordinates.  Its two lobes cross at
different depths and its engraved ribbon has a twisted rectangular section;
it is not a stack of flat infinity outlines.  The final camera follows the
same red witness that flew through the preceding rooms, banks around the
right lobe, passes through the crossover, and continues into the return iris.
There is no inscription, title plane, freeze, or time clamp in this module.

Renderer connection:
    INFINITY = {key: GPU(mesh) for key, mesh in
                build_infinity(Mesh, np, math, C, WHITE, ACC).items()}
    ending = sample_finale(t)
    # Blend the original long-outro eye/target/roll/fov by ending['camera_mix'].
    # Replace the old infinity and epilogue/title drawing from START onward:
    draw_finale(t, vp, hit, globals())

Keep the existing long-outro rooms until approximately 153.4 and then attenuate
them by ending['old_world_gain'].  Do not clamp render time or post processing
at 154.6: the last two seconds are actual forward flight.  sample_finale is
pure Python and can be tested without an OpenGL context or numpy.
"""

import math
from bisect import bisect_right

START = 152.5
END = 156.667
BEATS = (152.505, 152.960, 153.415, 153.870, 154.325)


def _clamp(x, lo=0., hi=1.):
    return max(lo, min(hi, float(x)))


def _ease(x):
    x = _clamp(x)
    return x*x*(3.-2.*x)


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _mul(a, s):
    return tuple(x*s for x in a)


def _unit(a):
    return _mul(a, 1./max(1.e-12, math.sqrt(sum(x*x for x in a))))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def ribbon_point(theta):
    """Two recognizable lobes, with 6.4 units of clearance at the crossover."""
    return (17.5*math.sin(theta), 7.2*math.sin(2.*theta),
            3.2*math.cos(theta))


def ribbon_frame(theta):
    tangent = _unit((17.5*math.cos(theta), 14.4*math.cos(2.*theta),
                     -3.2*math.sin(theta)))
    side = _unit(_cross(tangent, (0., 0., 1.)))
    normal = _unit(_cross(tangent, side))
    twist = theta*.5+.20*math.sin(2.*theta)
    u = _add(_mul(side, math.cos(twist)), _mul(normal, math.sin(twist)))
    v = _add(_mul(side, -math.sin(twist)), _mul(normal, math.cos(twist)))
    return ribbon_point(theta), tangent, u, v


# Nonuniform cubic Hermite interpolation gives the photographed mechanism
# real parallax.  The last endpoint deliberately has a nonzero tangent.
_POSES = (
    (152.500, (0., 2., 72.),       (0., 0., 0.),       -.03, 88.),
    (152.960, (-2., 1.6, 46.),    (0., 0., 0.),        .04, 72.),
    (153.415, (0., 1., 30.),      (1., 1., 0.),       -.05, 58.),
    (153.870, (11.5, 6.5, 17.),   (15., 4., 0.),      -.25, 67.),
    (154.325, (18., -1., 7.),     (13., -5., -1.5),     .28, 83.),
    (154.780, (10., -6.5, 2.),    (2., -3., -4.),       .58, 89.),
    (155.150, (0., -.8, 0.),      (-1., 1., -15.),     -.12, 96.),
    (155.600, (-2., .5, -12.),    (0., 0., -36.),       .16, 89.),
    (156.050, (1.2, -.4, -24.),   (0., 0., -50.),     -.05, 81.),
    (156.667, (0., .05, -39.),    (0., 0., -64.),       .03, 80.),
)
_TIMES = tuple(row[0] for row in _POSES)


def _values(row):
    return (*row[1], *row[2], row[3], row[4])


def _slope(i, axis):
    if i == 0:
        a, b = 0, 1
    elif i == len(_POSES)-1:
        a, b = i-1, i
    else:
        a, b = i-1, i+1
    return (_values(_POSES[b])[axis]-_values(_POSES[a])[axis])/(
        _TIMES[b]-_TIMES[a])


def _pose(t):
    i = max(0, min(len(_POSES)-2, bisect_right(_TIMES, t)-1))
    a, b = _POSES[i], _POSES[i+1]
    dt = b[0]-a[0]
    u = (t-a[0])/dt
    h00, h10 = 2*u*u*u-3*u*u+1., u*u*u-2*u*u+u
    h01, h11 = -2*u*u*u+3*u*u, u*u*u-u*u
    va, vb = _values(a), _values(b)
    value = tuple(h00*va[k]+h10*dt*_slope(i,k)+h01*vb[k]+
                  h11*dt*_slope(i+1,k) for k in range(8))
    return value[:3], value[3:6], value[6], value[7]


def _theta(t):
    # One journey, not a periodically repeated scan: the last drum attacks
    # expose successive physical portions of the same continuous conductor.
    knots = ((152.5, -.60), (152.96, -.22), (153.415, .15),
             (153.87, .85), (154.325, 1.80), (154.78, 2.75),
             (155.15, math.pi+.025))
    ts = tuple(row[0] for row in knots)
    i = max(0, min(len(knots)-2, bisect_right(ts, t)-1))
    u = _clamp((t-knots[i][0])/(knots[i+1][0]-knots[i][0]))
    # Linear angle with a gentle monotonic acceleration within each interval.
    u = u+.045*math.sin(math.tau*u)
    return knots[i][1]+(knots[i+1][1]-knots[i][1])*u


def witness_point(t):
    if t <= 155.15:
        return ribbon_point(_theta(t))
    p = _clamp((t-155.15)/(END-155.15))
    start = ribbon_point(math.pi+.025)
    # A departing single spark becomes the pupil of the next view.  Its
    # lateral excursions decay, so the camera actually enters the deep iris.
    return (start[0]*(1-p)+1.1*math.sin(p*math.tau)*(1-p),
            start[1]*(1-p)+.65*math.sin(p*math.pi)*(1-p),
            start[2]-67.*p)


def sample_finale(t):
    """Fixed-world camera plan and material envelope; no frozen terminal pose."""
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('finale time must be finite')
    if t<START:return dict(active=False,old_world_gain=1.,camera_mix=0.)
    eye, target, roll, fov = _pose(t)
    pulse = sum(math.exp(-(t-b)/.075)*s for b,s in
                zip(BEATS, (.82,.74,.74,.62,.62)) if t >= b)
    pulse = min(1., pulse)
    # A small positive velocity surge on attacks returns to the authored
    # trajectory smoothly; the route itself supplies the large displacement.
    camera_mix = _ease((t-START)/.70)
    # The complete outline is visible for the approach before its rails pass
    # either side of the lens.  No huge scene fade occurs at the crossing.
    exposure = _ease((t-START)/.32)
    iris_gain = .55+.45*_ease((t-154.55)/.75)
    return dict(active=t>=START, camera_eye=eye, camera_target=target,
                eye=eye, target=target, roll=roll, fov=fov,
                camera_mix=camera_mix, pulse=pulse,
                stage=('infinity_approach' if t<153.415 else
                       'witness_chase' if t<155.15 else 'iris_return'),
                exposure=exposure, old_world_gain=1.-_ease((t-153.40)/.85),
                iris_gain=iris_gain, witness=witness_point(t),
                witness_path=tuple(witness_point(t-.22+.22*i/25.)
                                   for i in range(26)),
                chromatic=.0007*pulse, quake=.002*pulse,
                freeze=False, render_time=t)


def build_infinity(Mesh, np, math, C, WHITE, ACC):
    """Precisely fabricated ribbon, supported crossover, and deep return iris."""
    C, WHITE, ACC = (np.asarray(c, float) for c in (C, WHITE, ACC))
    names = ('ribbon_body', 'ribbon_edges', 'ribbon_ribs', 'ribbon_engraving',
             'crossover', 'return_iris', 'return_throat', 'return_rim', 'seed')
    out = {key: Mesh() for key in names}

    def line(key, points, color, closed=False):
        out[key].line(points, color, closed=closed)

    def point(theta, width=0., depth=0.):
        p, _, u, v = ribbon_frame(theta)
        return np.asarray(p)+np.asarray(u)*width+np.asarray(v)*depth

    theta = np.linspace(0., math.tau, 641)
    # Nine conductors on either face define the changing surface normals.
    # The crossover's front and back never occupy the same plane.
    for depth in (-.24, .24):
        for width in np.linspace(-1.13,1.13,9):
            color = C*(.27 if depth<0 else .48)
            line('ribbon_body', [point(a,width,depth) for a in theta], color)
    for width in (-1.2,1.2):
        for depth in (-.31,.31):
            line('ribbon_edges', [point(a,width,depth) for a in theta],
                 WHITE*(.68 if depth>0 else .37))
    line('ribbon_engraving', [point(a,0.,.345) for a in theta], WHITE*.46)
    # Manufactured ribs cross the full depth, with narrow recessed grooves
    # and a contrasting screw at each second rib, never repeated red bars.
    for j,a in enumerate(np.linspace(0.,math.tau,144,endpoint=False)):
        corners = [point(a,w,d) for w,d in
                   ((-1.2,-.31),(1.2,-.31),(1.2,.31),(-1.2,.31))]
        line('ribbon_ribs',corners,C*(.54 if j%3 else .75),True)
        if j%2==0:
            p,tangent,u,v = ribbon_frame(a)
            p=np.asarray(p);tangent=np.asarray(tangent);u=np.asarray(u);v=np.asarray(v)
            for side in (-1,1):
                centre=p+u*(side*.93)+v*.33
                line('ribbon_engraving',[centre+.065*(u*math.cos(q)+tangent*math.sin(q))
                     for q in np.linspace(0.,math.tau,9,endpoint=False)],WHITE*.56,True)
        if j%6==0:
            line('ribbon_engraving',[point(a-.008,-.73,.35),
                 point(a+.008,-.73,.35),point(a+.008,.73,.35)],C*.33)
    # Structural bridges below the separate crossover layers explain why
    # the thin ribbon can support itself, without filling its passable gaps.
    for a0 in (.0,math.pi):
        _,_,u,v=ribbon_frame(a0)
        for side in (-1,1):
            pts=[point(a0+d,side*1.45,-.60) for d in np.linspace(-.20,.20,35)]
            line('crossover',pts,C*.47)
        for d in (-.20,.20):
            line('crossover',[point(a0+d,-1.45,-.60),
                 point(a0+d,1.45,-.60)],WHITE*.43)

    # A single iris aperture feeds a continuous, deep braided throat.  This
    # is not a row of copied circular portals and no flat eye symbol is used.
    for j in range(64):
        angle=math.tau*j/64.
        blade=[]
        for q in np.linspace(0.,1.,23):
            r=2.7+8.1*q
            a=angle+.24*(1-q)**1.2
            z=-34.+6.*q+(.12 if j%2 else -.12)
            blade.append([r*math.cos(a),r*math.sin(a),z])
        line('return_iris',blade,C*(.44 if j%2 else .72))
        line('return_iris',[[p[0]*1.012,p[1]*1.012,p[2]-.13]
                          for p in blade],WHITE*.22)
    for r,z,gain in ((10.8,-28.,.64),(11.15,-28.4,.32),
                      (10.85,-29.1,.25),(2.7,-34.,.48)):
        line('return_rim',[[r*math.cos(a),r*math.sin(a),z]
             for a in np.linspace(0.,math.tau,193)],WHITE*gain)
    for j in range(64):
        a=math.tau*j/64.
        pts=[]
        for q in np.linspace(0.,1.,145):
            z=-34.-44.*q
            r=2.7+3.5*q+1.6*math.sin(q*math.pi)
            th=a+1.15*q+.10*math.sin(q*math.tau)
            pts.append([r*math.cos(th),r*math.sin(th),z])
        line('return_throat',pts,(C if j%4 else WHITE)*(.40 if j%2 else .58))
    # Sparse cross ties make the iris read as one tapering mechanical depth
    # surface.  They are not repeated self-standing portal silhouettes.
    for q in np.linspace(.025,.975,24):
        r=2.7+3.5*q+1.6*math.sin(q*math.pi)
        z=-34.-44.*q
        for side in range(8):
            a0=side*math.tau/8.+1.15*q+.10*math.sin(q*math.tau)
            line('return_throat',[[r*math.cos(a),r*math.sin(a),z]
                 for a in np.linspace(a0,a0+.23,10)],C*.22)
    # A small three-dimensional needle rides the rail; only it uses ACC.
    for axis in range(3):
        points=[]
        for a in np.linspace(0.,math.tau,33):
            if axis==0:p=(.18*math.cos(a),.18*math.sin(a),0.)
            elif axis==1:p=(.18*math.cos(a),0.,.4*math.sin(a))
            else:p=(0.,.18*math.cos(a),.4*math.sin(a))
            points.append(p)
        line('seed',points,ACC*.85 if axis<2 else WHITE*.85)
    line('seed',[(-.32,0.,0.),(.32,0.,0.)],WHITE)
    line('seed',[(0.,-.32,0.),(0.,.32,0.)],WHITE)
    return out


def draw_finale(t,vp,hit,g):
    """Draw the fixed sculpture with the production renderer's existing GPU API."""
    score=sample_finale(t)
    if not score['active']:return
    ctx,gl=g['ctx'],g['gl']
    np=g['np'];tr,sc,rot=g['tr'],g['sc'],g['rot']
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
    g['ms'].depth_mask=False;ctx.line_width=1.2
    g['prog']['clearBox'].value=(3.,3.,.01,.01)
    meshes=g['INFINITY'];identity=np.eye(4);amp=score['exposure'];pulse=score['pulse']
    for key,gain in (('ribbon_body',.82),('ribbon_edges',1.12),
                     ('ribbon_ribs',.88),('ribbon_engraving',.88),
                     ('crossover',.80)):
        meshes[key].draw(identity,vp,t,0.,0.,-1,gain=amp*(gain+pulse*.16))
    iris_amp=amp*score['iris_gain']
    for key,gain in (('return_iris',.88),('return_rim',.98),('return_throat',.88)):
        meshes[key].draw(identity,vp,t,0.,0.,-1,gain=iris_amp*(gain+pulse*.10))
    # A short tail is one finite physical journey; it never resets or scans
    # across the screen.  It also crosses the camera's depth plane naturally.
    g['draw_red_path']([np.asarray(p) for p in score['witness_path']],vp,1.0+pulse*.35)
    meshes['seed'].draw(tr(*score['witness'])@sc(.9+pulse*.2),vp,t,0.,0.,-1,
                        gain=2.0+pulse*.8)
    ctx.disable(gl.BLEND);g['ms'].depth_mask=True


if __name__=='__main__':
    # Meaningful geometry-independent checks: no camera freeze, no vanishing
    # view vector, finite values, and continuous movement through the last frame.
    previous=None
    maximum_step=0.
    for frame in range(round((END-START)*240)+1):
        t=START+frame/240.
        value=sample_finale(t)
        assert all(math.isfinite(v) for v in (*value['eye'],*value['target'],
                                             value['roll'],value['fov']))
        assert math.dist(value['eye'],value['target'])>6.
        if previous is not None:
            maximum_step=max(maximum_step,math.dist(value['eye'],previous['eye']))
        previous=value
    assert math.dist(sample_finale(156.60)['eye'],sample_finale(END)['eye'])>1.
    assert math.dist(ribbon_point(0.),ribbon_point(math.pi))>6.
    assert not sample_finale(END)['freeze']
    print('Moving infinity finale: fixed 3D ribbon, separated crossover, 39-unit final iris flight.')
    print('Maximum camera step at 240fps:',round(maximum_step,5))
