"""Integrated line sculptures for the v17 mechanical visual language.

The processor is an embedded physical part of a complete computing chassis,
not a chip pictogram.  Fixed fasteners, cooling folds, cable looms and angled
load-bearing members carry detail through real depth.  All geometry consists
of GL_LINES; the renderer owns all transforms, motion and visibility.

Local envelope: x -16..16, y -9..9, z -24..3.  The foreground lyric corridor
(abs(x)<5, abs(y)<2) stays open.  Suggested gains: chassis/rear .45--.7,
fins .65--.9, bus .7--1, core 1--1.3, packets .7--1.  The three 'mount_*'
layers attach unrelated semantic mechanisms to the same fabricated world.
"""


def build_cohesive(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = (np.asarray(c, float) for c in (C, WHITE, ACC))
    names = ('gpu_chassis', 'gpu_fins', 'gpu_bus', 'gpu_core', 'gpu_rear',
             'gpu_packets', 'mount_keel', 'mount_arms', 'mount_harness')
    out = {name: Mesh() for name in names}

    def line(m, points, color=C, closed=False):
        m.line(points, color, closed=closed)

    def basis(a, b):
        direction = np.asarray(b, float)-np.asarray(a, float)
        direction /= max(1.e-9, float(np.linalg.norm(direction)))
        u = np.cross(direction, [0., 1., 0.] if abs(direction[1]) < .9
                     else [1., 0., 0.])
        u /= max(1.e-9, float(np.linalg.norm(u)))
        return u, np.cross(direction, u)

    def polygon_prism(m, profile, z0, z1, color=C, inner=.0):
        """Unequal bevels and real thickness, never a billboard rectangle."""
        p0 = np.asarray([[x, y, z0] for x, y in profile], float)
        p1 = p0.copy(); p1[:, 2] = z1
        line(m, p0, color, True); line(m, p1, color*.67, True)
        for a, b in zip(p0, p1):
            line(m, [a, b], color*.72)
        if inner:
            centre = p0[:, :2].mean(axis=0)
            inset = p0.copy()
            inset[:, :2] = centre+(inset[:, :2]-centre)*(1.-inner)
            inset[:, 2] += .035
            line(m, inset, color*.40, True)

    def plate(m, center, width, height, depth, color=C, bevel=.2):
        x, y, z = center
        w, h = width*.5, height*.5
        b = min(bevel, w*.6, h*.6)
        polygon_prism(m, [(x-w+b, y-h), (x+w-b, y-h),
                         (x+w, y-h+b), (x+w, y+h-b),
                         (x+w-b, y+h), (x-w+b, y+h),
                         (x-w, y+h-b), (x-w, y-h+b)],
                      z, z-depth, color, inner=.06)

    def beam(m, a, b, width, color=C, ribs=4):
        a, b = np.asarray(a, float), np.asarray(b, float)
        u, v = basis(a, b)
        offsets = [width*(u+v), width*(-u+v),
                   width*(-u-v), width*(u-v)]
        for d in offsets:
            line(m, [a+d, b+d], color)
        for j in range(ribs+1):
            p = a+(b-a)*j/ribs
            line(m, [p+d for d in offsets], color*.5, True)
            if j < ribs:
                q = a+(b-a)*(j+1)/ribs
                line(m, [p+offsets[j%4], q+offsets[(j+1)%4]], color*.45)

    def collar(m, center, u, v, radius, color, n=16):
        p = np.asarray(center, float)
        line(m, [p+radius*(u*math.cos(a)+v*math.sin(a))
                 for a in np.linspace(0., math.tau, n, endpoint=False)],
             color, True)

    def loom(m, points, radius=.12, color=C, strands=6, fittings=4):
        points = np.asarray(points, float)
        u, v = basis(points[0], points[-1])
        for a in np.linspace(0., math.tau, strands, endpoint=False):
            shift = radius*(u*math.cos(a)+v*math.sin(a))
            line(m, points+shift, color)
        for j in np.linspace(1, len(points)-2, fittings).astype(int):
            collar(m, points[j], u, v, radius*1.38, color*.72, n=10)

    def fastener(m, point, radius=.085, color=WHITE):
        p = np.asarray(point, float)
        collar(m, p, np.array([1., 0., 0.]), np.array([0., 1., 0.]),
               radius, color, n=10)
        line(m, [p+[-radius*.5, 0., .005], p+[radius*.5, 0., .005]],
             color*.68)

    def curve(points, count=48):
        """Cubic Bezier with explicit points, deterministic manufactured run."""
        p = np.asarray(points, float)
        return np.asarray([(1-t)**3*p[0]+3*(1-t)**2*t*p[1]
                           +3*(1-t)*t*t*p[2]+t**3*p[3]
                           for t in np.linspace(0., 1., count)])

    # A load-bearing machine cradle.  The diagonal lower keel, right housing
    # and left upper counterweight are a single assembly with unequal masses.
    chassis = out['gpu_chassis']
    right_profile = [(6.5, -5.6), (13.5, -6.7), (15.5, -4.4),
                     (15.4, 6.0), (13.7, 8.2), (9.1, 7.7),
                     (6.8, 4.7)]
    polygon_prism(chassis, right_profile, -1.3, -19.3, WHITE*.56, inner=.055)
    polygon_prism(chassis, [(7.2, -5.1), (13.1, -5.9), (14.6, -3.7),
                           (14.6, 5.5), (13.3, 7.2), (9.4, 6.9),
                           (7.4, 4.1)], -1.1, -2.4, C*.62, inner=.035)
    left_profile = [(-15.6, 2.6), (-13.4, 1.8), (-8.0, 4.2),
                    (-6.5, 6.4), (-8.3, 8.2), (-14.0, 7.2), (-15.8, 5.1)]
    polygon_prism(chassis, left_profile, 1.8, -15.0, C*.46, inner=.06)
    for a, b, r in [((-14.6, -7.5, 2.0), (13.7, -7.8, -21.8), .26),
                    ((7.0, -5.6, -.9), (8.1, -8.1, -7.0), .19),
                    ((13.8, -5.9, -17.2), (13.7, -7.8, -21.8), .20),
                    ((-14.8, 2.7, 1.2), (-13.1, -7.4, -1.1), .17),
                    ((-9.0, 7.3, -13.5), (9.4, 8.5, -19.0), .15),
                    ((-13.2, -7.4, -1.1), (-9.0, 1.9, -9.8), .15)]:
        beam(chassis, a, b, r, C*.47, ribs=9)
    for k, (x, y) in enumerate(right_profile):
        for z in [-1.24, -5.2, -12.5, -19.25]:
            fastener(chassis, [x*.99, y*.99, z], .09, WHITE*.55)
    # Engraved seam runs are structural, with sparse depth breakpoints.
    for j in range(6):
        x = 8.1+j*.94
        line(chassis, [[x, -5.75+(x-8.1)*-.1, -2.7],
                       [x, -5.75+(x-8.1)*-.1, -15.4],
                       [x+.4, -5.5, -18.4]], C*.24)

    # Folded heat exchangers grow out of the actual case.  Different heights,
    # oblique ends and unevenly grouped spacing avoid floating equal panels.
    fins = out['gpu_fins']
    for side in (0, 1):
        for j in range(37 if side == 0 else 28):
            z = -2.8-j*(.415 if side == 0 else .46)
            if side == 0:
                profile = [(9.0, 5.2), (13.7, 5.4), (14.45, 6.2),
                           (13.65, 7.15), (10.05, 6.8), (8.3, 5.9)]
            else:
                profile = [(7.35, -3.4), (14.4, -3.2), (14.3, -4.7),
                           (13.15, -5.6), (7.9, -4.85)]
            # Every fifth full-depth separator connects the fin bank to a
            # side wall; the others carry a fine folded double edge.
            col = WHITE*(.42 if j%5 == 0 else .25)
            polygon_prism(fins, profile, z, z-.065, col)
            if j%5 == 0:
                line(fins, [[14.4, -4.2 if side else 6.2, z],
                            [15.0, -3.9 if side else 5.9, z],
                            [15.0, 2.2, z]], C*.24)
    # Narrow heat pipes feed the exchangers from the processor seat.
    for j in range(9):
        x = 8.1+j*.67
        path = [[x, 3.4, -2.7], [x, 4.3, -3.2],
                [x+.18, 5.2, -4.1], [x+.18, 5.45, -15.8]]
        loom(fins, path, .055, C*.35, strands=4, fittings=5)
    for j in range(23):
        z = .8-j*.61
        line(fins, [[-15.0, 3.5, z], [-13.2, 3.1, z],
                    [-8.1, 5.3, z], [-7.9, 6.6, z],
                    [-9.0, 7.2, z], [-14.3, 6.5, z]], WHITE*.26, True)

    # One embedded accelerator package: chamfered ceramic seat, stacked die
    # and contact combs.  Local rectangles are recessed parts, not hero icons.
    core = out['gpu_core']
    plate(core, [10.75, .5, -.8], 5.8, 6.4, .85, C*.65, .55)
    plate(core, [10.55, .65, -.64], 3.35, 3.0, .2, WHITE*.75, .3)
    for z in [-.60, -.47, -.34]:
        plate(core, [10.55, .65, z], 2.6, 2.2, .035, WHITE*.55, .25)
    # Unequal inner functional blocks with fine interconnects, under the
    # cooling cover; the chip is not multiplied in the scene.
    for row in range(6):
        for col in range(7):
            x = 9.45+col*.34
            y = -.18+row*.31
            if (row+col)%5 == 0:
                line(core, [[x, y, -.28], [x+.2, y, -.28],
                            [x+.2, y+.19, -.28], [x, y+.19, -.28]], C*.4, True)
            else:
                line(core, [[x, y, -.28], [x+.2, y, -.28]], WHITE*.32)
    for side in (-1, 1):
        for j in range(22):
            y = -1.93+j*.231
            line(core, [[10.75+side*2.08, y, -.59],
                        [10.75+side*2.66, y, -.86],
                        [10.75+side*2.66, y, -1.63]], C*.55)
        for j in range(16):
            x = 8.97+j*.237
            line(core, [[x, .5+side*2.45, -.59],
                        [x, .5+side*2.97, -.94],
                        [x, .5+side*2.97, -1.64]], WHITE*.4)
    for x, y in [(8.35, -2.15), (13.1, -2.15), (8.35, 3.15), (13.1, 3.15)]:
        fastener(core, [x, y, -.5], .14, WHITE*.72)
    # Coolant manifold is offset above, with actual depth and mounting feet.
    for j in range(7):
        x = 8.45+j*.69
        loom(core, [[x, 3.4, -.8], [x, 3.8, -.8],
                    [x+.1, 4.1, -2.8], [x+.1, 4.1, -7.7]],
             .08, C*.52, strands=5, fittings=3)

    bus = out['gpu_bus']; packets = out['gpu_packets']
    # Curved ribbon bundles connect the masses over the top and under the
    # words.  No bundle runs through the central lyric plane.
    bus_paths = []
    for j in range(12):
        f = j/11
        bus_paths.append(curve([[-12.9+f*4.5, 3.2+f*1.5, -.1],
                                [-9.0, 8.0-f*.8, -5.0],
                                [4.4, 8.2-f*.7, -13.0],
                                [8.2+f*4.6, 6.3, -17.0]], 44))
    for j in range(11):
        f = j/10
        bus_paths.append(curve([[-14.1, 2.8+f*2.7, -7.5],
                                [-15.2, -6.2+f*.2, -11.0],
                                [3.0, -8.4+f*.55, -14.8],
                                [7.3+f*.23, -2.8+f*.3, -16.8]], 48))
    for j, path in enumerate(bus_paths):
        loom(bus, path, .045, C*(.33 if j%3 else .5), strands=3, fittings=3)
        # Tiny white contact segments are physical stations, not a sweeping
        # red curve.  Renderer can reveal the layer once, without cycling.
        k = 17+(j*7)%19
        line(packets, path[k:k+3], WHITE*(.6 if j%3 else .8))
        if j in (2, 9, 15, 21):
            p = path[-2]
            collar(packets, p, np.array([1., 0., 0.]),
                   np.array([0., 1., 0.]), .12, ACC*.38, n=8)
    # The contacts physically enter the processor seat, in deep side traces.
    for j in range(18):
        y = -2.3+j*.31
        line(bus, [[7.4, y, -1.9], [6.9, y, -2.5],
                   [6.9, y, -5.0-j*.47], [7.35, y, -5.4-j*.47]], C*.4)

    rear = out['gpu_rear']
    polygon_prism(rear, [(7.0, -5.0), (13.0, -6.0), (14.7, -3.7),
                         (14.8, 5.5), (13.4, 7.1), (9.3, 6.6),
                         (7.2, 4.2)], -19.4, -23.3, C*.35, inner=.05)
    for j in range(21):
        y = -3.7+j*.43
        line(rear, [[8.1, y, -19.35], [13.8, y+.15, -19.35]], WHITE*.25)
    # Three unequal connector wells recessed into the back, with pin combs.
    for x, y, w, h in [(9.0, -3.2, 1.9, 1.4), (11.8, .2, 3.0, 2.2),
                        (10.0, 4.3, 2.7, 1.3)]:
        plate(rear, [x, y, -23.3], w, h, .35, C*.48, .18)
        for j in range(max(4, int(w/.19))):
            xx = x-w*.38+j*w*.76/max(1, int(w/.19)-1)
            line(rear, [[xx, y-h*.28, -23.67],
                        [xx, y+h*.28, -23.67]], WHITE*.33)
    for j in range(8):
        y = -5.3+j*1.6
        loom(rear, [[14.8, y, -5.5], [15.4, y+.3, -9.7],
                    [15.4, y+.3, -20.1], [14.2, y, -22.5]],
             .075, C*.23, strands=4, fittings=4)

    # Cohesion adapters: fabricated pieces the renderer can put under token
    # paths / decision branches / linked lists.  No rectangular tunnel.
    keel = out['mount_keel']
    for offset in [-.42, .42]:
        path = curve([[-15.2, -7.5+offset, 2.1],
                      [-10.0, -8.2+offset, -3.8],
                      [8.3, -7.2+offset, -14.0],
                      [15.1, -5.7+offset, -23.5]], 54)
        loom(keel, path, .12, C*.35, strands=4, fittings=9)
    for j in range(15):
        f = j/14
        x, z = -14.6+29.0*f, 1.7-24.5*f
        y = -7.7+1.8*f*f
        line(keel, [[x-.45, y-.45, z], [x+.45, y+.45, z],
                    [x+.7, y+.5, z-.7]], WHITE*.3)
        if j%3 == 0:
            beam(keel, [x, y, z], [x+.4, y+1.2, z-.8], .1, C*.4, 3)

    arms = out['mount_arms']
    for side, front, back in [(-1, 2., -19.), (1, -1.5, -23.)]:
        # An offset lifting fork which can support a semantic object above
        # the caption passage without visually surrounding it with a frame.
        pts = [[side*15.3, -6.2, front], [side*14.4, -2.4, front-2.],
               [side*13.1, 4.5, back+3.], [side*8.0, 7.7, back]]
        for a, b in zip(pts[:-1], pts[1:]):
            beam(arms, a, b, .17, WHITE*.33, 6)
        for p in pts[1:-1]:
            collar(arms, p, np.array([1., 0., 0.]),
                   np.array([0., 1., 0.]), .37, C*.46, 20)
            collar(arms, p, np.array([1., 0., 0.]),
                   np.array([0., 1., 0.]), .22, WHITE*.4, 16)
        beam(arms, pts[-1], [side*6.8, 7.9, back-.1], .12, C*.45, 4)

    harness = out['mount_harness']
    for side in (-1, 1):
        for j in range(7):
            f = j/6
            path = curve([[side*(7.2+f*1.2), 6.0, 1.2-f*.15],
                          [side*14.6, 6.8-f*.4, -3.2],
                          [side*15.0, -4.5+f*.6, -14.],
                          [side*(7.5+f*.8), -5.5, -23.1]], 55)
            loom(harness, path, .045, C*.28, strands=3, fittings=5)
            # A stitched cable support in the machine's own restrained
            # palette anchors the small device to its environment.
            for k in [8, 26, 43]:
                p = path[k]
                line(harness, [p+[0., -.22, .1], p+[0., .22, .1]], WHITE*.35)

    return out
