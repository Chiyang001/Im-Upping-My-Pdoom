"""Connected line sculpture for a continuous journey through the machine.

The red signal's two rails are a single physical object.  Ribs, fingers,
inspection circuits and the machine's memories all attach to those rails.
Only Mesh.line is used: no faces, lettering, pictures or GPU dependency.
"""


def road_point(z, side, lane=0., upper=False):
    """Carrier coordinate as a plain tuple, usable by a camera or signal.

    This public helper uses only Python's standard math module.  The
    default lane is precisely the red conductor, not an approximation.
    """
    import math
    bend = .54*math.sin(.092*z+.7) + .24*math.sin(.227*z)
    width = 3.52 + .62*math.sin(.064*z+1.1)
    x = bend + side*(width + lane*.125)
    y = -3.12 + .48*math.sin(.135*z+.8)
    if upper:
        x += side*.62
        y = 1.24 + .50*math.sin(.101*z+1.5)
    else:
        y += .075*lane + .13*math.cos(.18*z+lane*.16)
    return (x, y, z)


_carrier_coordinate = road_point


def build_story(Mesh, np, math, C, WHITE, ACC):
    """Return road, signals, machine_skeleton and memory as static Meshes.

    The journey runs from z=12 to z=-70.  The active lane stays clear; the
    carrier lives mostly at x +/- 2..6 and y=-4..2.  Large shells continue
    beyond the field of view, so they read as a place entered by the lens.
    All random-looking variation is deterministic.
    """
    C, WHITE, ACC = [np.asarray(v, dtype=float) for v in (C, WHITE, ACC)]
    road, signals, skeleton, memory = [Mesh() for _ in range(4)]

    def line(mesh, pts, col, closed=False):
        mesh.line(pts, np.asarray(col), closed=closed)

    def unit(v):
        a = np.asarray(v, dtype=float)
        return a / max(float(np.linalg.norm(a)), 1.e-9)

    def road_point(z, side, lane=0., upper=False):
        # The shared carrier, deliberately asymmetric but never a center
        # ornament.  Every later machine organ terminates on this spline.
        return np.asarray(_carrier_coordinate(z, side, lane, upper))

    def circle_pts(center, u, v, radius, n=20, squash=1.):
        center, u, v = map(np.asarray, (center, u, v))
        return [center+radius*(math.cos(a)*u+squash*math.sin(a)*v)
                for a in np.linspace(0., math.tau, n, endpoint=False)]

    def basis(a, b):
        tangent = unit(np.asarray(b)-np.asarray(a))
        u = unit(np.cross(tangent, [0., 1., 0.] if abs(tangent[1]) < .9
                          else [1., 0., 0.]))
        return u, np.cross(tangent, u)

    def beam(mesh, a, b, radius, col, steps=10, sides=4):
        # A rectangular hollow truss with real cross braces, not a wire
        # box placed behind the action.  Joint centers are exact shared
        # coordinates with rails, shell ribs or the next beam.
        a, b = np.asarray(a), np.asarray(b)
        u, v = basis(a, b)
        offsets = [radius*(math.cos(q)*u+math.sin(q)*v)
                   for q in np.linspace(math.pi/4, math.tau+math.pi/4,
                                        sides, endpoint=False)]
        for d in offsets:
            line(mesh, [a+d, b+d], col)
        for j in range(steps+1):
            p = a+(b-a)*j/steps
            line(mesh, [p+d for d in offsets], col*.65, True)
            if j < steps:
                q = a+(b-a)*(j+1)/steps
                for k in range(sides):
                    line(mesh, [p+offsets[k], q+offsets[(k+1)%sides]],
                         col*(.56 if k%2 else .83))
        for j in range(1, steps, 3):
            p = a+(b-a)*j/steps
            line(mesh, [p+d*.72 for d in offsets], col*.35, True)

    def cable(mesh, points, radius, col, strands=4):
        # Continuous longitudinal strokes with a restrained radial twist.
        p = np.asarray(points)
        for k in range(strands):
            a = math.tau*k/strands
            offset = np.c_[np.cos(np.arange(len(p))*.07+a),
                            np.sin(np.arange(len(p))*.07+a),
                            np.zeros(len(p))]*radius
            line(mesh, p+offset, col*(1. if k == 0 else .55))

    zrail = np.linspace(12., -70., 401)
    for side in (-1, 1):
        # The single bright red conductor is flanked by fabricated layers
        # of fine green/white rail edges and return cables.
        for lane in range(-6, 7):
            p = [road_point(float(z), side, lane) for z in zrail]
            col = ACC*.88 if lane == 0 else C*(.22+.04*(lane%4))
            if lane in (-6, 6):
                col = WHITE*.43
            line(road, p, col)
        for lane in (-3, -1, 1, 3):
            p = [road_point(float(z), side, lane, True) for z in zrail]
            line(road, p, C*(.33 if lane%3 else .47))
        # Close paired rail banks into a recognisable fabricated object.
        for j, z in enumerate(np.linspace(11.8, -69.8, 165)):
            lo, hi = road_point(z, side, -6), road_point(z, side, 6)
            line(road, [lo, hi], C*.5)
            for dz in (-.07, .07):
                p = road_point(z+dz, side)
                line(road, [p+[-.91, -.30, 0.], p+[.91, -.30, 0.],
                            p+[.91, .31, 0.], p+[-.91, .31, 0.]],
                     C*.18, True)
            if j % 3 == 0:
                # The upper cable is causally fed by the lower carrier.
                p, q = road_point(z, side), road_point(z, side, 0, True)
                mid = np.array([p[0]+side*.42, q[1]-.46, z-.45])
                line(road, [p, p+[side*.42, .52, -.22], mid, q], C*.3)
                line(road, [p+[.05, 0., 0.], mid+[.05, 0., 0.],
                            q+[.05, 0., 0.]], WHITE*.15)
        # Hairline service returns run underneath, joining both banks.
        for lane in range(4):
            p = [road_point(float(z), side, -5+lane*2)
                 +[side*.17, -.62-lane*.10, 0.] for z in zrail]
            line(road, p, C*(.13+.025*lane))

    # Underfloor transoms leave the centre open above y=-4.  These are
    # shared physical supports for both sides, not crossing decorations.
    for j, z in enumerate(np.linspace(10.8, -69., 58)):
        a, b = road_point(z, -1), road_point(z, 1)
        a[1] -= .8
        b[1] -= .8
        line(road, [a, b], C*.19)
        line(road, [a+[0., -.17, 0.], b+[0., -.17, 0.]], C*.12)
        for side, p in ((-1, a), (1, b)):
            q = road_point(z, side)
            line(road, [q, p], WHITE*.29)
            line(road, [p, road_point(z-.72, side)+[0., -.8, 0.]], C*.17)

    # The signal is an explicit dense, sequential spatial score.  Moving
    # this layer in z reads as flowing pulses rather than random stars.
    for j, z in enumerate(np.linspace(11.85, -69.85, 620)):
        side = -1 if j%2 else 1
        lane = (j%7-3)*1.5
        a = road_point(z, side, lane)
        b = road_point(z-.043-(j%4)*.015, side, lane)
        line(signals, [a+[0., .095, 0.], b+[0., .095, 0.]],
             ACC*(.52 if j%5 else 1.))
        # Paired brackets and a contact return give every pulse direction.
        radius = .055+.014*(j%3)
        if j%2 == 0:
            u, v = [1., 0., 0.], [0., 1., 0.]
            line(signals, circle_pts(a+[0., .11, 0.], u, v,
                                    radius, 7), C*.42, True)
        if j%5 == 0:
            q = road_point(z, side, 0, True)
            line(signals, [a, a+[side*.23, .36, -.08],
                           q+[side*.12, -.22, 0.], q], ACC*.39)
            for k in range(3):
                dz = -.11*k
                p = road_point(z+dz, side, 0, True)
                line(signals, [p, p+[side*.11, .08, -.12]], WHITE*.51)

    # Every shell rib is wired into a carrier joint.  The shell extends
    # offscreen rather than enclosing a small central, complete object.
    ribs = [10.5, 4., -3., -11., -19., -28., -38., -49., -59., -68.]
    rib_controls = []
    for ri, z in enumerate(ribs):
        width = 13.5+2.4*math.sin(ri*.8)
        top = 8.8+1.8*math.cos(ri*.7)
        bottom = -10.5-.6*math.sin(ri)
        bend = .8*math.sin(ri*.9)
        # An off-axis, six-sided machine cross-section.
        corners = [np.array([-width, bottom, z]),
                   np.array([-width-2., 1.9+bend, z-1.2]),
                   np.array([-width*.53, top, z-.2]),
                   np.array([width*.59, top-1.2, z+.4]),
                   np.array([width+1.7, -.8+bend, z-1.]),
                   np.array([width*.87, bottom-.4, z])]
        rib_controls.append(corners)
        for k in range(6):
            beam(skeleton, corners[k], corners[(k+1)%6],
                 .16+.035*(ri%3), C*(.21+.02*(k%3)),
                 steps=7+(k%3), sides=4)
        for side, ci in ((-1, 0), (1, 5)):
            anchor = road_point(z, side)
            root = corners[ci]
            knee = root*.55+anchor*.45
            knee[1] -= .8
            beam(skeleton, root, knee, .17, WHITE*.27, 6)
            beam(skeleton, knee, anchor, .10, C*.48, 5)
            line(skeleton, [root+[0., .28, -.16], knee+[0., .28, -.16],
                            anchor], ACC*.36)
            upper = road_point(z, side, 0, True)
            topjoint = corners[2 if side == -1 else 3]
            route = [upper, upper+[side*1.4, 1.8, -.25],
                     topjoint+[0., -.45, 0.], topjoint]
            cable(skeleton, route, .055, C*.32, 3)
        # Fabrication detail on the outer skin: carefully bounded, no
        # random spray filling the active centre with disconnected noise.
        for side, ci in ((-1, 1), (1, 4)):
            p = corners[ci]
            for k in range(11):
                yy = -5.9+k*1.04
                x = p[0]+side*(.38+.07*(k%3))
                pts = [[x, yy, z-.5], [x-side*.55, yy, z-.5],
                       [x-side*.55, yy+.34, z-.76],
                       [x-side*1.05, yy+.34, z-.76]]
                line(skeleton, pts, C*(.14+.03*(k%3)))
                line(skeleton, [[x, yy+.12, z-.52],
                                [x-side*.33, yy+.12, z-.52]], WHITE*.2)

    # Longitudinal outside beams attach ribs, proving the entire movie
    # takes place inside one machine rather than ten unrelated tunnels.
    for i in range(len(ribs)-1):
        for ci in (0, 1, 2, 3, 4, 5):
            a, b = rib_controls[i][ci], rib_controls[i+1][ci]
            beam(skeleton, a, b, .115, C*.18, steps=6)

    # Three clamp hands are positioned on the sides of the route.  Their
    # wrist, palm, knuckles and terminal fingertip are physically joined.
    for hi, (z, side) in enumerate(((5., -1), (-25., 1), (-54., -1))):
        carrier = road_point(z, side)
        wrist = np.array([side*(12.6+hi*.7), -1.7+hi*.55, z-1.3])
        palm = np.array([side*8.4, -1.2, z])
        beam(skeleton, wrist, palm, .46, WHITE*.40, 9)
        for finger in range(4):
            dz = (finger-1.5)*.74
            root = palm+[0., (finger%2)*.24, dz]
            knuckle = np.array([side*6.2, .95+(finger%2)*.35, z+dz-.2])
            joint = np.array([side*4.85, .65, z+dz-.1])
            tip = road_point(z+dz, side, finger-1.5)
            # Articulated ribs and finger tendons meet at each pivot.
            beam(skeleton, root, knuckle, .19, C*.44, 6)
            beam(skeleton, knuckle, joint, .15, WHITE*.38, 5)
            beam(skeleton, joint, tip, .105, C*.55, 6)
            for k in (-1, 1):
                line(skeleton, [root+[0., k*.10, 0.],
                                knuckle+[0., k*.15, 0.],
                                joint+[0., k*.12, 0.], tip], ACC*.3)
            for jointpoint in (root, knuckle, joint):
                for depth in (-.12, .12):
                    line(skeleton, circle_pts(jointpoint+[0., 0., depth],
                                             [1., 0., 0.], [0., 1., 0.],
                                             .27, 18), WHITE*.28, True)
        cable(skeleton, [wrist, palm, carrier], .11, ACC*.46, 4)

    # One eye is remembered at multiple scales along the same connected
    # spine.  The lateral centres keep the principal narrative lane open.
    def eye(center, sx, sy, seed):
        cx, cy, cz = center
        lid = []
        for k in range(8):
            t = np.linspace(0., math.tau, 65)
            a = sx*(1.-.045*k)
            b = sy*(1.-.062*k)
            p = [np.array([cx+a*math.cos(q), cy+b*math.sin(q)*
                           (.83+.17*abs(math.cos(q))), cz+.075*k+
                           .26*math.cos(q*2)]) for q in t]
            line(memory, p, (WHITE if k == 0 else C)*(.5 if k == 0 else .17))
            lid.append(p)
        for k in range(20):
            q = math.tau*k/20
            a = np.array([cx+sx*.93*math.cos(q),
                          cy+sy*.93*math.sin(q), cz+.08])
            b = np.array([cx+sx*.77*math.cos(q),
                          cy+sy*.66*math.sin(q), cz+.52])
            line(memory, [a, b], C*.22)
        rad = sy*.7
        for k in range(6):
            rr = rad*(.35+k*.12)
            line(memory, circle_pts([cx, cy, cz+.42+k*.035],
                                    [1., 0., 0.], [0., 1., 0.], rr, 49),
                 ACC*(.45 if k in (0, 5) else .22), True)
        for k in range(76):
            a = math.tau*k/76
            r0, r1 = rad*.43, rad*(.85+.13*math.sin(k*1.77+seed))
            line(memory, [[cx+r0*math.cos(a), cy+r0*math.sin(a), cz+.72],
                          [cx+r1*math.cos(a+.025),
                           cy+r1*math.sin(a+.025), cz+.58]], C*.26)
        return np.array([cx, cy-sy, cz])

    eye_specs = [((-9.2, 2.1, -15.), 4.1, 2.2, -1),
                 ((10.1, 3.0, -37.), 5.0, 2.55, 1),
                 ((-7.5, 3.7, -63.), 3.5, 1.9, -1)]
    for k, (center, sx, sy, side) in enumerate(eye_specs):
        anchor = eye(center, sx, sy, k)
        carrier = road_point(center[2]+1., side, 0, True)
        cable(memory, [anchor, anchor+[side*-.8, -1.0, .2],
                       carrier+[side*.7, .5, .1], carrier],
              .065, C*.35, 4)

    # Neural inspection boards are further down the corridor, physically
    # fed from the eye/carrier rather than floating in an unrelated void.
    for ni, (z, side) in enumerate(((-24., -1), (-46., 1), (-67., -1))):
        cx, cy = side*10.1, -.25
        nodes = []
        for layer in range(5):
            count = (4, 7, 8, 6, 3)[layer]
            layernodes = []
            for n in range(count):
                p = np.array([cx+side*(layer-2)*.86,
                              cy+(n-(count-1)/2)*.74, z-layer*.17])
                layernodes.append(p)
                line(memory, circle_pts(p, [1., 0., 0.], [0., 1., 0.],
                                        .12+(n%2)*.018, 10),
                     WHITE*.36, True)
            nodes.append(layernodes)
        for layer in range(4):
            for a in nodes[layer]:
                for bi, b in enumerate(nodes[layer+1]):
                    # Wiring is deterministic and selective enough to
                    # retain fine fabrication instead of a solid patch.
                    if bi%2 == layer%2 or layer == 3:
                        line(memory, [a, b], C*(.1+.035*(bi%3)))
        carrier = road_point(z, side, 0, True)
        terminal = nodes[0][1]
        cable(memory, [carrier, carrier+[side*1.2, .45, -.1],
                       terminal+[side*-.3, -.45, 0.], terminal],
              .06, ACC*.32, 4)
        # A shallow board edge receives every last-layer output.
        for a in nodes[-1]:
            q = np.array([cx+side*3.1, a[1], z-1.1])
            line(memory, [a, q, q+[0., -.35, -.15]], C*.27)
        line(memory, [[cx-side*2.3, -3.5, z],
                      [cx+side*3.2, -3.5, z-1.1],
                      [cx+side*3.2, 3.3, z-1.1],
                      [cx-side*2.3, 3.3, z]], WHITE*.15, True)

    def clip_points(cx, cy, z, scale, angle):
        # One genuinely continuous bent wire with recognisable nested
        # semicircular ends; the open end connects to the next clip.
        p = []
        for t in np.linspace(0., math.pi, 18):
            p.append([.62*math.cos(t), 1.03+.62*math.sin(t)])
        p.append([-.62, -1.03])
        for t in np.linspace(math.pi, math.tau, 18):
            p.append([.62*math.cos(t), -1.03+.62*math.sin(t)])
        p.append([.62, .93])
        for t in np.linspace(0., math.pi, 16):
            p.append([.35*math.cos(t)+.27, .93+.35*math.sin(t)])
        p.append([-.08, -.93])
        for t in np.linspace(math.pi, math.tau, 16):
            p.append([.35*math.cos(t)+.27, -.93+.35*math.sin(t)])
        p.append([.62, .50])
        ca, sa = math.cos(angle), math.sin(angle)
        return [np.array([cx+scale*(a*ca-b*sa),
                          cy+scale*(a*sa+b*ca), z+.07*a]) for a, b in p]

    # The same carrier becomes a paperclip manufacturing chain: connected
    # at ends, climbing away from the corridor into the outer skeleton.
    for side in (-1, 1):
        previous = None
        for j, z in enumerate(np.linspace(-31., -69., 30)):
            anchor = road_point(z, side)
            cx = anchor[0]+side*(2.15+.35*math.sin(j*.6))
            cy = anchor[1]+1.9+.25*math.cos(j*.5)
            p = clip_points(cx, cy, z, .67+.04*(j%3), side*.22)
            for depth, gain in ((-.035, .35), (.035, .55)):
                line(memory, [q+[0., 0., depth] for q in p], C*gain)
            line(memory, [anchor, anchor+[side*.4, .6, -.1], p[-1]],
                 ACC*.3)
            if previous is not None:
                line(memory, [previous, p[0]], WHITE*.24)
            previous = p[-1]

    # A distant loom is the endpoint of all earlier carriers.  Its frame
    # sits below and beside the active lane; strings still spread out of
    # frame and create large-scale perspective, not a small flat emblem.
    loom_z = -64.
    left, right = road_point(loom_z, -1), road_point(loom_z, 1)
    loom_corners = [np.array([-12., -8., loom_z-2.]),
                    np.array([12., -8., loom_z-2.]),
                    np.array([12., 4.6, loom_z-7.]),
                    np.array([-12., 4.6, loom_z-7.])]
    for k in range(4):
        beam(memory, loom_corners[k], loom_corners[(k+1)%4],
             .2, WHITE*.27, 15)
    for side, a in ((-1, left), (1, right)):
        p = loom_corners[0 if side == -1 else 1]
        cable(memory, [a, a+[side*1.4, -1.7, -1.], p], .09, ACC*.45, 4)
    for j in range(83):
        f = j/82
        x = -11.7+23.4*f
        pts = []
        for k, z in enumerate(np.linspace(loom_z-1.8, -70., 37)):
            y = -7.7+(.35*math.sin(k*.52+j*.19))
            pts.append([x+.13*math.sin(k*.31+j*.4), y, z])
        line(memory, pts, C*(.18 if j%4 else .38))
        if j%3 == 0:
            line(memory, [[x, -7.7, loom_z-2.],
                          [x, 4.3, loom_z-7.]], C*.13)
    for k, z in enumerate(np.linspace(loom_z-2., -70., 31)):
        p = [[x, -7.7+.25*math.sin(x*.72+k*.41), z]
             for x in np.linspace(-11.7, 11.7, 70)]
        line(memory, p, (ACC if k%7 == 0 else WHITE)*.19)

    return {'road': road, 'signals': signals,
            'machine_skeleton': skeleton, 'memory': memory}
