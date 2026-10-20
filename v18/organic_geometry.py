"""Three physical mushrooms and a pillar-bound mechanical Basilisk.

Only GL_LINES are produced.  All objects have true depth, with restrained
mint/white construction detail and tiny accent seams.  Nothing is a screen
icon or a replacement for the film's principal eye.  Semantic host envelope:
x +/-18, y +/-10, z -23..3.  The central lyric passage is kept empty.

The first five layers belong together at the Chinese-room conveyor.  Reveal
the stems before caps/gills or raise the entire attached assembly once.  The
four Basilisk layers form one creature: keep anchors fixed while applying
small motions to body/jaw.  Avoid separate orbiting head and body rotations.
"""


def build_organic(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = (np.asarray(c, float) for c in (C, WHITE, ACC))
    names = ('shroom_caps', 'shroom_gills', 'shroom_stems',
             'shroom_mycelium', 'shroom_bag', 'organic_mount', 'basilisk_body',
             'basilisk_head', 'basilisk_jaw', 'basilisk_anchors')
    out = {name: Mesh() for name in names}

    def line(m, points, color=C, closed=False):
        m.line(points, color, closed=closed)

    def unit(a):
        a = np.asarray(a, float)
        return a/max(1.e-9, float(np.linalg.norm(a)))

    def frame(tangent):
        tangent = unit(tangent)
        u = unit(np.cross(tangent, [0., 1., 0.] if abs(tangent[1]) < .9
                          else [1., 0., 0.]))
        return u, np.cross(tangent, u)

    def circle(m, center, radius, color, u=None, v=None, n=32,
               ratio=1.):
        center = np.asarray(center, float)
        u = np.array([1., 0., 0.]) if u is None else np.asarray(u, float)
        v = np.array([0., 1., 0.]) if v is None else np.asarray(v, float)
        line(m, [center+radius*(u*math.cos(a)+ratio*v*math.sin(a))
                 for a in np.linspace(0., math.tau, n, endpoint=False)],
             color, True)

    def bezier(points, n=50):
        p = np.asarray(points, float)
        return np.asarray([(1-t)**3*p[0]+3*(1-t)**2*t*p[1]
                           +3*(1-t)*t*t*p[2]+t**3*p[3]
                           for t in np.linspace(0., 1., n)])

    def beam(m, a, b, width, color=C, ribs=5):
        a, b = np.asarray(a, float), np.asarray(b, float)
        u, v = frame(b-a)
        offsets = [width*(u+v), width*(-u+v),
                   width*(-u-v), width*(u-v)]
        for d in offsets:
            line(m, [a+d, b+d], color)
        for j in range(ribs+1):
            p = a+(b-a)*j/ribs
            line(m, [p+d for d in offsets], color*.5, True)
            if j < ribs:
                q = a+(b-a)*(j+1)/ribs
                line(m, [p+offsets[j%4], q+offsets[(j+1)%4]], color*.4)

    caps, gills, stems = [out[k] for k in
                          ('shroom_caps', 'shroom_gills', 'shroom_stems')]
    # Each record is ground point, crooked neck, cap radius, cap height and
    # small world tilt.  Neighbouring mushrooms differ in stage and profile.
    mushrooms = [
        ((-12.5, -8.8, -4.3), (-11.7, -4.6, -3.7), 2.75, 1.48, -.13, .08),
        ((-8.6, -8.65, -8.7), (-8.2, -5.6, -8.2), 1.82, 1.28, .16, -.12),
        ((-15.3, -8.7, -10.9), (-14.6, -5.2, -11.3), 2.0, 1.12, -.19, -.08),
    ]
    for mi, (foot, neck, radius, height, tilt_z, tilt_x) in enumerate(mushrooms):
        foot, neck = np.asarray(foot), np.asarray(neck)
        cs, sn = math.cos(tilt_z), math.sin(tilt_z)
        cx, sx = math.cos(tilt_x), math.sin(tilt_x)
        rz = np.array([[cs, -sn, 0], [sn, cs, 0], [0, 0, 1.]])
        rx = np.array([[1., 0, 0], [0, cx, -sx], [0, sx, cx]])
        orientation = rz@rx

        def cap_point(r, angle, y):
            # Slight asymmetric expansion stops the mesh reading as a
            # perfect machine hemisphere, while the ribs retain precision.
            asym = 1.+.035*math.sin(angle*3+mi)+.018*math.cos(angle*7)
            return neck+orientation@np.array([r*asym*math.cos(angle), y,
                                              r*.84*asym*math.sin(angle)])

        # Latitudes and meridians contour the umbrella's actual dome.  An
        # explicit rolled rim makes the familiar cap silhouette unmistakable.
        for j, theta in enumerate(np.linspace(.11, math.pi/2, 12)):
            r = radius*math.sin(theta)
            yy = height*max(0., math.cos(theta))**.88
            line(caps, [cap_point(r, a, yy)
                        for a in np.linspace(0., math.tau, 100, endpoint=False)],
                 C*(.43 if j%3 else .65), True)
        for ai, angle in enumerate(np.linspace(0., math.tau, 42, endpoint=False)):
            line(caps, [cap_point(radius*math.sin(theta), angle,
                                 height*max(0., math.cos(theta))**.88)
                        for theta in np.linspace(0., math.pi/2, 27)],
                 WHITE*(.37 if ai%4 else .58))
        for r, yy in [(radius, .0), (radius*.985, -.09), (radius*.94, -.12)]:
            line(caps, [cap_point(r, a, yy)
                        for a in np.linspace(0., math.tau, 100, endpoint=False)],
                 WHITE*.67, True)
        # Shallow irregular flecks follow the dome, never flat circles stuck
        # to a sprite.  Their sparse grouping gives each specimen a face.
        for k in range(15):
            angle = k*2.39996+mi*.3
            rr = radius*(.25+.52*((k*7)%15)/14)
            theta = math.asin(rr/radius)
            yy = height*math.cos(theta)**.88+.018
            a0, a1 = angle-.055, angle+.065
            pts = [cap_point(rr*.98, a0, yy),
                   cap_point(rr*1.03, angle, yy+.03),
                   cap_point(rr*.99, a1, yy)]
            line(caps, pts, WHITE*.38)

        # The underside has genuinely radiating gill surfaces.  Alternate
        # shorter secondary gills join midway, as on a physical mushroom.
        for gi, angle in enumerate(np.linspace(0., math.tau, 66, endpoint=False)):
            r0 = radius*(.17 if gi%2 == 0 else .48)
            radii = np.linspace(r0, radius*.945, 22)
            upper, lower = [], []
            for r in radii:
                t = r/radius
                yy = -.07-.10*math.sin(t*math.pi)
                upper.append(cap_point(r, angle, yy))
                lower.append(cap_point(r, angle+.008,
                                       yy-(.10+.12*math.sin(t*math.pi))))
            line(gills, upper, C*.58)
            line(gills, lower, WHITE*.40)
            line(gills, [upper[-1], lower[-1]], WHITE*.5)

        # A bent, subtly tapered organic stem with thirteen longitudinal
        # fibres.  Transverse scars are uneven and do not become screw coils.
        bend = np.array([(-1 if mi%2 else 1)*.72, .0, .24])
        path = bezier([foot, foot+[.2, 1.9, -.15]+bend,
                       neck+[.35, -1.2, -.15]-bend*.25, neck], 52)
        stem_r = .28+radius*.052
        stem_frames = []
        for j, p in enumerate(path):
            tangent = path[min(j+1, len(path)-1)]-path[max(0, j-1)]
            u, v = frame(tangent)
            stem_frames.append((u, v))
        for fi, angle in enumerate(np.linspace(0., math.tau, 13, endpoint=False)):
            pts = []
            for j, p in enumerate(path):
                f = j/(len(path)-1)
                r = stem_r*(1.13-.24*f+.09*math.sin(f*math.pi*2+mi))
                u, v = stem_frames[j]
                pts.append(p+r*(math.cos(angle)*u+math.sin(angle)*v))
            line(stems, pts, C*(.6 if fi%3 else .85))
        for j in [3, 13, 27, 37, 46]:
            u, v = stem_frames[j]
            circle(stems, path[j], stem_r*(1.12-j*.003), WHITE*.28,
                   u=u, v=v, n=24)
        # A thin torn veil under two mature caps adds a recognisable neck.
        if mi in (0, 3):
            u, v = stem_frames[-8]
            collar_y = path[-8]
            line(stems, [collar_y+stem_r*(1.5+.25*math.sin(a*5))*
                         (math.cos(a)*u+math.sin(a)*v)
                         for a in np.linspace(0., math.tau, 36, endpoint=False)],
                 WHITE*.55, True)

    mycelium = out['shroom_mycelium']
    # Low, flattened mats connect roots to the conveyor, not random sparks.
    for mi, record in enumerate(mushrooms):
        foot = np.asarray(record[0], float)
        for k in range(11):
            angle = (k+.2*mi)*math.tau/11
            length = .8+1.25*((k*3+mi)%8)/7
            direction = np.array([math.cos(angle), 0., math.sin(angle)])
            end = foot+direction*length
            path = bezier([foot, foot+direction*.5+[0, -.12, .1],
                           end-direction*.2+[.1, .09, 0], end], 18)
            line(mycelium, path, C*.35)
            for branch in (8, 13):
                p = path[branch]
                sideways = np.array([-direction[2], 0., direction[0]])
                q = p+direction*.35+sideways*(.23 if branch%2 else -.3)
                line(mycelium, [p, q, q+direction*.23], WHITE*.25)
        # A grounded thin foot socket belongs to the same conveyor build.
        for zoff in [-.48, .48]:
            line(mycelium, [foot+[-.75, -.12, zoff],
                           foot+[.75, -.12, zoff]], C*.32)

    bag = out['shroom_bag']
    # A tall, open, folded sack encloses the three LEFT specimens.  Its
    # uneven octagonal mouth reaches the crooked necks, unlike a low ring
    # around their feet.  The four clearly lit corner folds establish a soft
    # upright container, and sparse dim interior creases leave stems visible.
    rim = np.array([[-16.8, -5.20, -3.40], [-15.8, -4.80, -2.50],
                    [-11.3, -5.02, -2.80], [-7.0, -4.60, -3.80],
                    [-6.7, -4.90, -8.40], [-8.0, -4.70, -12.80],
                    [-15.3, -4.90, -14.00], [-17.0, -5.40, -11.80]])
    base = np.array([[-15.7, -9.10, -4.10], [-14.9, -9.20, -3.80],
                     [-11.2, -9.22, -3.90], [-7.9, -9.10, -4.60],
                     [-7.7, -9.10, -8.80], [-8.5, -9.20, -12.10],
                     [-14.8, -9.14, -12.70], [-16.0, -9.10, -11.00]])
    line(bag, rim, WHITE*.88, True)
    # Folded-over mouth has material thickness and a dark inner lip.
    lip = rim.copy(); lip[:, 1] -= .20
    lip[:, 0] += np.where(lip[:, 0] < -11.5, .12, -.12)
    line(bag, lip, C*.67, True)
    for j, (p, q) in enumerate(zip(rim, lip)):
        line(bag, [p, q], WHITE*.55)
    line(bag, base, WHITE*.60, True)
    for j, (bottom, top) in enumerate(zip(base, rim)):
        side = -1 if j in (0, 1, 6, 7) else 1
        bulge = np.array([side*.20, .0, -.10])
        path = bezier([bottom, bottom+[0., 1.15, 0.]+bulge,
                       top+[0., -1.0, 0.]+bulge, top], 24)
        line(bag, path, WHITE*(.76 if j in (0, 3, 5, 7) else .48))
        # Long narrow pleats, with one asymmetric turn near the base.
        fold = bezier([bottom+[.20, .05, -.03],
                       bottom+[side*.4, 1.1, .15],
                       top+[-side*.27, -.9, -.08], top], 18)
        line(bag, fold, C*.32)
    for j in range(len(rim)):
        k = (j+1)%len(rim)
        # Only two interior folds per panel, well below the brighter contour.
        for f in [.31, .70]:
            low = base[j]*(1-f)+base[k]*f
            high = rim[j]*(1-f)+rim[k]*f
            center = (low+high)*.5
            center += [(.12 if j%2 else -.12), -.1, .11]
            line(bag, bezier([low, low+[.10, .75, .05],
                              center, high], 17), C*.21)
    # An attached broad gusset folds across the front at the bottom, rather
    # than a cylindrical circumference around the mushrooms.
    line(bag, [base[0], [-15.0, -8.25, -3.65],
               [-11.3, -8.75, -3.4], [-7.9, -8.15, -4.45], base[3]],
         C*.46)
    # Two soft, narrow handles rise from the same folded mouth.  Their unequal
    # heights and paired stitched contours read as bag straps, not eye rings.
    for start, finish, top_y in [([-16.4, -5.04, -3.25],
                                  [-14.8, -4.85, -2.57], -2.85),
                                 ([-8.2, -4.67, -3.55],
                                  [-6.95, -4.73, -5.65], -2.58)]:
        start, finish = np.array(start), np.array(finish)
        controls = [start, start+[.0, top_y-start[1]+.6, -.1],
                    finish+[.0, top_y-finish[1]+.6, .1], finish]
        strap = bezier(controls, 36)
        line(bag, strap, WHITE*.83)
        line(bag, strap+[.13, .0, -.045], C*.54)
        for p in [start, finish]:
            line(bag, [p+[-.16, -.24, .0], p+[.2, -.24, .0],
                       p+[.2, .10, .0], p+[-.16, .10, .0]], WHITE*.53, True)
    # The right two specimens remain restrained environmental cargo.  Their
    # small folded sack has angular shoulders, not repeated circular bands.

    mount = out['organic_mount']
    # The primary sack containing THREE mushrooms is delivered on one
    # manufactured carrier.  This entire assembly can be placed at the exit
    # of the Chinese-room flight, instead of remaining in the abandoned room.
    # A chamfered low platform gives the bag one clear, coherent silhouette.
    tray = np.array([[-16.9, -9.48, -2.2], [-6.0, -9.48, -2.2],
                     [-5.7, -9.48, -3.4], [-6.2, -9.48, -11.6],
                     [-7.4, -9.48, -13.1], [-16.3, -9.48, -13.1],
                     [-17.4, -9.48, -11.9], [-17.4, -9.48, -3.4]])
    line(mount, tray, WHITE*.80, True)
    line(mount, tray+[0., -.26, .0], C*.65, True)
    for a in tray:
        line(mount, [a, a+[0., -.26, 0.]], WHITE*.65)
    # A visible raised front lip seats the sack on the delivery tray.  The
    # side chamfers and inset seam communicate a fabricated part at a glance.
    line(mount, [[-16.6, -8.95, -2.15], [-15.8, -8.65, -2.15],
                 [-7.0, -8.65, -2.15], [-6.3, -8.98, -2.15]], WHITE*.75)
    line(mount, [[-16.6, -8.95, -2.15], [-16.6, -9.48, -2.15],
                 [-6.3, -9.48, -2.15], [-6.3, -8.98, -2.15]], C*.65)
    line(mount, [[-15.8, -9.06, -2.10], [-7.0, -9.06, -2.10]], WHITE*.45)
    # Carrier skids have unevenly grouped braces, not another rectangular
    # tunnel.  They continue into the exit machinery behind the mushrooms.
    for x in [-16.2, -7.0]:
        beam(mount, [x, -9.58, .9], [x+.3, -9.58, -20.5],
             .13, C*.52, ribs=14)
    for j in range(11):
        z = -2.5-j*.93
        line(mount, [[-16.7, -9.43, z], [-6.3, -9.43, z-.15]], C*.28)
    # A rear folded chute points toward the sack.  Its two sides and floor
    # have continuous thickness, made from the same mint/white line material.
    chute_left = [[-15.7, -3.8, -20.7], [-15.7, -5.4, -18.4],
                  [-14.6, -7.7, -14.0], [-14.1, -8.7, -12.5]]
    chute_right = [[-10.3, -3.8, -20.7], [-10.3, -5.4, -18.4],
                   [-9.4, -7.7, -14.0], [-9.2, -8.7, -12.5]]
    for edge in (chute_left, chute_right):
        line(mount, edge, WHITE*.65)
        line(mount, np.asarray(edge)+[0., .30, 0.], C*.45)
        for p in edge:
            line(mount, [p, np.asarray(p)+[0., .3, .0]], C*.35)
    for j in range(len(chute_left)):
        line(mount, [chute_left[j], chute_right[j]], C*.30)
    for f in np.linspace(.12, .86, 7):
        l = np.asarray(chute_left[1])*(1-f)+np.asarray(chute_left[2])*f
        r = np.asarray(chute_right[1])*(1-f)+np.asarray(chute_right[2])*f
        line(mount, [l, r], C*.21)
    # Two low fingers hold the delivery sack by its bottom folds.  They end
    # below the bag opening and never obstruct its recognisable cap profiles.
    for x in [-15.8, -7.2]:
        beam(mount, [x, -9.4, -5.2], [x, -7.8, -5.2], .075, C*.60, 4)
        line(mount, [[x, -7.8, -5.2], [x+(.45 if x < -10 else -.45), -7.6, -5.0]],
             WHITE*.67)

    body = out['basilisk_body']
    head = out['basilisk_head']
    jaw = out['basilisk_jaw']
    anchors = out['basilisk_anchors']

    # One creature winds around a real left pillar and crosses above the
    # lyric plane into an upper-right skull.  These are anatomical sections,
    # not independent sine waves and not concentric rings around the camera.
    segments = [
        [(-14.1, -6.4, -22.1), (-16.3, -5.5, -20.0),
         (-15.7, -2.0, -17.0), (-12.6, -2.2, -15.6)],
        [(-12.6, -2.2, -15.6), (-8.9, -2.4, -14.3),
         (-8.6, 1.4, -12.0), (-11.2, 2.8, -10.4)],
        [(-11.2, 2.8, -10.4), (-14.7, 4.6, -8.9),
         (-11.1, 7.6, -7.2), (-7.6, 7.6, -6.5)],
        [(-7.6, 7.6, -6.5), (-2.1, 7.5, -6.0),
         (1.8, 5.3, -9.4), (5.2, 6.0, -7.9)],
        [(5.2, 6.0, -7.9), (8.4, 6.6, -6.6),
         (13.8, 8.1, -6.0), (12.3, 6.1, -3.4)],
    ]
    spine = np.concatenate([bezier(p, 40)[:-1] for p in segments]
                           +[np.asarray([segments[-1][-1]], float)])
    frames, radii = [], []
    for j, p in enumerate(spine):
        t = j/(len(spine)-1)
        tangent = spine[min(j+1, len(spine)-1)]-spine[max(0, j-1)]
        u, v = frame(tangent)
        frames.append((u, v))
        radii.append(.19+1.02*math.sin(t*math.pi*.61)**.75)
    # Longitudinal ridges and individually seated belly plates reveal the
    # S silhouette while the many vertebrae encode real depth progression.
    for k, angle in enumerate(np.linspace(0., math.tau, 12, endpoint=False)):
        pts = [p+radii[j]*(math.cos(angle)*frames[j][0]
                          +.88*math.sin(angle)*frames[j][1])
               for j, p in enumerate(spine)]
        line(body, pts, C*(.34 if k%3 else .65))
    for j in range(3, len(spine)-2, 3):
        p, (u, v), r = spine[j], frames[j], radii[j]
        # Slightly pointed dorsal part of each rib makes a scale armour
        # silhouette, rather than a smooth corrugated hose.
        ring = []
        for a in np.linspace(0., math.tau, 20, endpoint=False):
            bulge = 1.+.16*max(0., math.sin(a))**7
            ring.append(p+r*bulge*(math.cos(a)*u+.88*math.sin(a)*v))
        line(body, ring, WHITE*(.55 if j%9 == 0 else .30), True)
        if j+3 < len(spine):
            pn, (un, vn), rn = spine[j+3], frames[j+3], radii[j+3]
            for angle in [.25, 1.1, 2.0, 3.2, 4.15, 5.25]:
                a = p+r*(math.cos(angle)*u+.88*math.sin(angle)*v)
                b = pn+rn*(math.cos(angle+.18)*un+.88*math.sin(angle+.18)*vn)
                mid = (a+b)*.5+.08*(u+v)
                line(body, [a, mid, b], C*.48)
        # A few integral mechanical seams, deliberately far from red sweeps.
        if j%18 == 0:
            point = p+r*u
            line(body, [point-.12*v, point+.12*v], ACC*.30)

    # Angular skull with two depths, bevel rim and internal mechanical
    # sutures.  It is a side-profile head facing left, visibly serpent-like.
    skull_xy = [(6.5, 4.55), (8.0, 4.4), (11.7, 4.55), (13.55, 5.5),
                (13.8, 6.55), (12.65, 7.5), (10.45, 7.8), (8.8, 6.8),
                (7.1, 5.55)]
    front = np.array([[x, y, .9] for x, y in skull_xy], float)
    back = np.array([[x+.3, y+.15, -2.7] for x, y in skull_xy], float)
    line(head, front, WHITE*.84, True)
    line(head, back, C*.57, True)
    for j, (a, b) in enumerate(zip(front, back)):
        line(head, [a, b], C*.52)
        if j not in (0, 1, 7, 8):
            mid = (a+b)*.5
            line(head, [mid, mid+[-.4, .1, -.2], back[(j+1)%len(back)]], C*.30)
    # Long cranial rails meet the neck; no floating jaw ornament.
    for p in [[13.3, 5.5, -.7], [12.9, 7.1, -1.2], [11.7, 7.5, -1.5]]:
        beam(head, p, [12.3, 6.1, -3.4], .10, C*.5, 4)
    for j in range(6):
        z = .65-j*.54
        line(head, [[7.15, 5.15, z], [9.0, 5.6, z],
                    [10.8, 7.2, z], [12.4, 7.15, z]], C*.30)
    line(head, [[6.8, 4.9, 1.0], [8.1, 5.0, 1.02], [8.9, 5.6, 1.02]], WHITE*.63)
    # Exactly one eye on the visible flank.  Its slit is anatomical, never
    # a duplicate of the film's spherical principal-eye set piece.
    eye_center = np.array([10.25, 6.27, 1.04])
    for radius, ratio, col in [(.80, .70, C*.74), (.66, .70, WHITE*.83),
                               (.39, .83, C*.59)]:
        circle(head, eye_center, radius, col, ratio=ratio, n=48)
    line(head, [eye_center+[0., -.28, .025], eye_center+[.055, .0, .025],
                eye_center+[0., .28, .025], eye_center+[-.055, .0, .025]],
         WHITE*.9, True)
    # Raised brow and long nasal seam make this read as a skull, not an eye
    # icon placed next to an abstract tube.
    line(head, [[8.85, 6.55, 1.10], [9.6, 7.02, 1.14],
                [10.8, 7.08, 1.14], [11.52, 6.62, 1.10]], C*.88)
    for x in [7.12, 7.38]:
        line(head, [[x, 5.06, 1.02], [x+.12, 5.17, 1.05]], WHITE*.65)

    # A lower jaw with a deep articulated rear hinge and attached teeth.
    lower_xy = [(6.62, 4.22), (8.2, 3.65), (11.55, 3.74),
                (13.37, 4.65), (13.5, 5.18), (11.65, 4.25), (8.0, 4.1)]
    lower_front = np.array([[x, y, .93] for x, y in lower_xy], float)
    lower_back = lower_front.copy(); lower_back[:, 2] = -1.95
    line(jaw, lower_front, WHITE*.72, True)
    line(jaw, lower_back, C*.42, True)
    for a, b in zip(lower_front, lower_back):
        line(jaw, [a, b], C*.42)
    for j in range(9):
        x = 7.1+j*.48
        tooth_y = 4.47+(x-7.1)*.02
        h = .23+(.18 if j in (1, 6) else .0)
        line(jaw, [[x, tooth_y, .95], [x+.1, tooth_y-h, 1.02],
                   [x+.2, tooth_y, .95]], WHITE*.70)
    # The two fangs are part of this one mouth and attach to its upper rim.
    for x in [8.1, 11.2]:
        line(jaw, [[x, 4.49, .93], [x+.08, 3.98, 1.04],
                   [x+.23, 4.5, .93]], WHITE*.84)
    for z in [.95, .75, -.4, -1.95]:
        circle(jaw, [12.8, 5.12, z], .40, C*.56, ratio=1., n=28)
        circle(jaw, [12.8, 5.12, z+.02], .19, WHITE*.48, n=24)
    # A short forked tongue stays above the text corridor and ends in depth.
    line(jaw, [[6.8, 4.32, .2], [6.25, 4.12, .8], [5.65, 4.1, 1.2],
               [5.25, 4.25, 1.4]], C*.50)
    line(jaw, [[5.65, 4.1, 1.2], [5.2, 3.95, 1.4]], C*.50)

    # Physical supports follow the film's fabricated architecture.  Body
    # wraps around one inclined column instead of floating near a HUD.
    beam(anchors, [-12.3, -8.6, -18.9], [-11.9, 8.4, -7.4],
         .23, C*.39, ribs=18)
    beam(anchors, [-12.0, 7.9, -7.9], [13.5, 8.6, -6.5],
         .16, WHITE*.30, ribs=18)
    for p, q in [([-12.4, -5.9, -18.4], [-15.3, -4.6, -19.3]),
                 ([-12.1, 2.0, -11.4], [-11.3, 3.2, -10.4]),
                 ([-7.6, 8.3, -7.5], [-7.6, 7.6, -6.5]),
                 ([5.2, 8.3, -7.0], [5.2, 6.0, -7.9]),
                 ([12.7, 8.5, -6.6], [12.3, 7.0, -4.7])]:
        beam(anchors, p, q, .10, C*.41, ribs=4)
    for j in [27, 65, 116, 159, 181]:
        p, (u, v), r = spine[j], frames[j], radii[j]
        circle(anchors, p, r*1.17, WHITE*.45, u=u, v=v, n=28, ratio=.88)
        circle(anchors, p+.08*unit(np.cross(u, v)), r*1.22,
               C*.32, u=u, v=v, n=28, ratio=.88)
    # Two low asymmetric braces physically ground the pillar into a base.
    for side in [-1, 1]:
        beam(anchors, [-12.3, -7.4, -18.2],
             [-12.3+side*2.1, -9.0, -20.5], .15, C*.35, ribs=5)

    return out
