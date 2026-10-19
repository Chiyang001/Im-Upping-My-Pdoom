"""Legible, fabricated line sculptures for the song's four central metaphors.

Only Mesh.line is used.  No surfaces, pictures, labels or implied human brain.
The six layers of each concept are deliberately separate so the renderer can
animate an actual cause and result instead of rotating one static ornament.

Integration suggestions (local times are measured from the lyric onset):
  Chinese room, 26.06--29.68: advance input cards, tick the rules, then output;
    keep the chair still.  Matching symbols are produced without understanding.
  Shoggoth, 29.68--31.78: mask and split are LEFT/RIGHT halves of the smile;
    translate them apart by 1.2--3 units to reveal organs and tendrils behind.
  Paperclips, 96.7--98.7: sources/planet feed the conveyor, shredder shears,
    forming glows, swarm fills the room.  Sources and planet can shrink away.
  Orthogonality, 104.54--109.4: ability/ascent move vertically and grow; goal
    and clips stay locked.  Independent red goal remains a paperclip at every
    capacity level.  Frame includes the precise right-angle bracket.

All coordinates are local, x +/-18, y +/-10, z -15..8.  A central word corridor
of roughly x +/-7 and y +/-2 is kept free of foreground mechanical clutter.
Suggested rendering: low-gain shell/frame, 0.8--1.3 active mechanism, 1.6 red
signal packets; a flight should pass BETWEEN the two side mechanisms.
"""


def build_metaphors(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = [np.asarray(v, dtype=float) for v in (C, WHITE, ACC)]
    names = (
        'chinese_shell', 'chinese_input', 'chinese_rules', 'chinese_output',
        'chinese_chair', 'chinese_carriage',
        'shoggoth_mask', 'shoggoth_shell', 'shoggoth_tendrils',
        'shoggoth_puppetry', 'shoggoth_split', 'shoggoth_organs',
        'paperclip_sources', 'paperclip_conveyor', 'paperclip_shredder',
        'paperclip_forming', 'paperclip_swarm', 'paperclip_planet',
        'orthogonal_frame', 'orthogonal_ability', 'orthogonal_goal',
        'orthogonal_couplings', 'orthogonal_clips', 'orthogonal_ascent',
    )
    out = {name: Mesh() for name in names}

    def line(m, pts, col=C, close=False):
        m.line(pts, np.asarray(col), closed=close)

    def basis(a, b):
        tangent = np.asarray(b, float)-np.asarray(a, float)
        tangent /= max(1.e-9, float(np.linalg.norm(tangent)))
        u = np.cross(tangent, [0, 1, 0] if abs(tangent[1]) < .9 else [1, 0, 0])
        u /= max(1.e-9, float(np.linalg.norm(u)))
        return u, np.cross(tangent, u)

    def ring(m, center, radius, col=C, axis=2, n=64, squash=1.):
        center = np.asarray(center, float)
        u, v = ((np.array([1, 0, 0]), np.array([0, 1, 0])) if axis == 2
                else ((np.array([1, 0, 0]), np.array([0, 0, 1])) if axis == 1
                      else (np.array([0, 1, 0]), np.array([0, 0, 1]))))
        pts = [center+radius*(math.cos(q)*u+squash*math.sin(q)*v)
               for q in np.linspace(0, math.tau, n, endpoint=False)]
        line(m, pts, col, True)

    def box(m, center, size, col=C, detail=False):
        p, h = np.asarray(center, float), np.asarray(size, float)*.5
        pts = [p+h*np.array([x, y, z])
               for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        for i, a in enumerate(pts):
            for j, b in enumerate(pts):
                if j > i and np.count_nonzero(a != b) == 1:
                    line(m, [a, b], col)
        if detail:
            # Recessed seams on the front, plus four real fastener circles.
            x, y, z = p
            hx, hy, hz = h
            line(m, [[x-hx+.08, y-hy+.08, z+hz+.015],
                     [x+hx-.08, y-hy+.08, z+hz+.015],
                     [x+hx-.08, y+hy-.08, z+hz+.015],
                     [x-hx+.08, y+hy-.08, z+hz+.015]], col*.55, True)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    ring(m, p+[sx*(hx-.14), sy*(hy-.14), hz+.025],
                         .055, col*.65, n=12)

    def beam(m, a, b, r, col=C, steps=10):
        a, b = np.asarray(a, float), np.asarray(b, float)
        u, v = basis(a, b)
        offsets = [r*(u+v), r*(u-v), r*(-u-v), r*(-u+v)]
        for d in offsets:
            line(m, [a+d, b+d], col)
        for j in range(steps+1):
            p = a+(b-a)*j/steps
            line(m, [p+d for d in offsets], col*.63, True)
            if j < steps:
                q = a+(b-a)*(j+1)/steps
                for k in range(4):
                    line(m, [p+offsets[k], q+offsets[(k+1)%4]], col*.42)

    def gear(m, center, radius, col=C, axis=2, teeth=28):
        center = np.asarray(center, float)
        u, v = ((np.array([1, 0, 0]), np.array([0, 1, 0])) if axis == 2
                else ((np.array([1, 0, 0]), np.array([0, 0, 1])) if axis == 1
                      else (np.array([0, 1, 0]), np.array([0, 0, 1]))))
        normal = np.cross(u, v)
        for depth in (-.10, .10):
            pts = []
            for j in range(teeth*4):
                q = math.tau*j/(teeth*4)
                r = radius*(1. if j%4 in (1, 2) else .91)
                pts.append(center+r*(math.cos(q)*u+math.sin(q)*v)+depth*normal)
            line(m, pts, col, True)
        ring(m, center, radius*.69, col*.6, axis=axis, n=64)
        ring(m, center, radius*.18, col*.9, axis=axis, n=48)
        for q in np.linspace(0, math.tau, 12, endpoint=False):
            d = math.cos(q)*u+math.sin(q)*v
            line(m, [center+d*radius*.2, center+d*radius*.66], col*.55)

    def trace(m, pts, width=.035, col=C, strands=3):
        pts = np.asarray(pts, float)
        for j in range(strands):
            shift = np.array([0., (j-(strands-1)/2)*width, 0.])
            line(m, pts+shift, col*(1 if j == strands//2 else .43))

    def symbol(m, center, size=.6, variant=0, col=WHITE):
        # Invented syntax tiles, visibly symbols rather than natural language.
        x, y, z = center
        d = size
        motifs = [
            [(-.3, .4), (.3, .4), (.3, -.4), (-.3, -.4), (-.3, .4)],
            [(-.35, -.35), (0, .4), (.35, -.35), (-.35, -.35)],
            [(-.4, .3), (.4, .3), (0, .3), (0, -.35), (-.25, -.35)],
            [(-.3, .4), (-.3, -.4), (.3, -.4), (.3, .4), (-.3, .4)],
        ]
        pts = [[x+u*d, y+v*d, z] for u, v in motifs[variant%4]]
        trace(m, pts, .018, col, strands=2)
        if variant%3:
            line(m, [[x-d*.45, y, z], [x+d*.45, y, z]], col*.8)
        if variant%2:
            line(m, [[x, y-d*.48, z], [x, y+d*.48, z]], col*.8)

    def clip_points(center, scale=1., axis=2, angle=0.):
        # One continuous double-U wire: open small arm, inner loop, outer loop.
        raw = []
        for yy in np.linspace(-.72, .5, 9):
            raw.append([-.22, yy])
        raw += [[.03+.25*math.cos(q), .5+.25*math.sin(q)]
                for q in np.linspace(math.pi, 0, 19)]
        raw += [[.28, yy] for yy in np.linspace(.5, -.73, 9)]
        raw += [[-.08+.36*math.cos(q), -.73+.36*math.sin(q)]
                for q in np.linspace(0, -math.pi, 21)]
        raw += [[-.44, yy] for yy in np.linspace(-.73, .63, 9)]
        raw += [[.01+.45*math.cos(q), .63+.45*math.sin(q)]
                for q in np.linspace(math.pi, 0, 23)]
        raw += [[.46, yy] for yy in np.linspace(.63, -.5, 10)]
        cs, sn = math.cos(angle), math.sin(angle)
        pts = []
        for x, y in raw:
            x, y = scale*(x*cs-y*sn), scale*(x*sn+y*cs)
            p = [x, y, 0.] if axis == 2 else ([x, 0., y] if axis == 1 else [0., x, y])
            pts.append(np.asarray(center)+p)
        return np.asarray(pts)

    def clip(m, center, scale=1., col=WHITE, axis=2, angle=0., twin=False):
        pts = clip_points(center, scale, axis, angle)
        line(m, pts, col)
        if twin:
            # Real wire edge, not a filled stroke, with intermittent connectors.
            offset = np.array([.022, 0, .025])*scale
            line(m, pts+offset, col*.42)
            for j in range(0, len(pts), 8):
                line(m, [pts[j], pts[j]+offset], col*.5)

    # CLOSED SYMBOL ROOM: the doorway is a communication slot, not a mind.
    m = out['chinese_shell']
    for z in np.linspace(-13.5, 4., 13):
        for x in (-16., 16.):
            beam(m, [x, -8.5, z], [x, 8.5, z], .12, C*.32, 10)
        beam(m, [-16, 8.5, z], [16, 8.5, z], .11, C*.25, 15)
        beam(m, [-16, -8.5, z], [16, -8.5, z], .11, C*.25, 15)
    for x in np.linspace(-16, 16, 25):
        line(m, [[x, -8.5, 4], [x, -8.5, -13.5]], C*.24)
        line(m, [[x, 8.5, 4], [x, 8.5, -13.5]], C*.17)
    for side in (-1, 1):
        for yy in np.linspace(-8, 8, 17):
            trace(m, [[side*16, yy, 4], [side*16, yy, -13.5]], .04, C*.20)
        for zz in np.linspace(-13, 3.5, 10):
            box(m, [side*15.8, 5.4, zz], [.28, 2.1, 1.05], C*.35)
    # Back wall is a dense ruled ledger, deliberately empty at the lyric.
    for x in np.linspace(-15.5, 15.5, 43):
        for a, b in ((-8.4, -2.8), (2.8, 8.4)):
            line(m, [[x, a, -13.5], [x, b, -13.5]], C*.18)

    for side, key in ((-1, 'chinese_input'), (1, 'chinese_output')):
        m = out[key]
        box(m, [side*13.1, 4.9, -.8], [4.6, 3., 2.1], C*.7, True)
        for y in (4.05, 5.8):
            beam(m, [side*16.8, y, -.5], [side*7.6, y, -.5], .07, WHITE*.65, 18)
        for j in range(12):
            x = side*(8.0+j*.72)
            z = -.15-.035*j
            box(m, [x, 4.95, z], [.62, 1.22, .07], C*.46)
            for k in range(3):
                symbol(m, [x, 4.55+k*.34, z+.065], .40,
                       j+k if side < 0 else 3-j+k, WHITE*.88)
        for k in range(20):
            x = side*(8+k*.42)
            line(m, [[x, 3.85, .6], [x, 3.70, .6]], ACC*.7)
        # Different physical input/output sockets, same mechanical rule feed.
        for yy in np.linspace(3.8, 6.1, 13):
            line(m, [[side*15.3, yy, .29], [side*15.9, yy, .29]], C*.5)

    m = out['chinese_rules']
    for row in range(4):
        yy, zz = 3.7+row*.91, -5.5-row*1.9
        for j in range(14):
            x = -7.2+j*1.1
            box(m, [x, yy, zz], [.94, .72, .45], C*.32, True)
            symbol(m, [x-.23, yy, zz+.25], .40, j+row, WHITE*.7)
            symbol(m, [x+.23, yy, zz+.25], .40, j+row+2, ACC*.65)
        beam(m, [-8.1, yy-.48, zz], [8.1, yy-.48, zz], .06, C*.3, 24)
    for side in (-1, 1):
        for j in range(5):
            gear(m, [side*(8.2+j*.93), 7.3, -6.7], .44, C*.8, teeth=18)
        trace(m, [[side*13.1, 5, -.8], [side*13.1, 7.3, -2],
                  [side*8, 7.3, -6.7], [side*7, 6.45, -10.9]], .045, ACC*.7)

    m = out['chinese_chair']
    # An unmistakable EMPTY chair: back, seat, four legs, bolts, no occupant.
    chair_x, chair_y, chair_z = -10.7, -5.35, -6.5
    box(m, [chair_x, chair_y, chair_z], [2.7, .25, 2.55], WHITE*.95, True)
    for dx in (-1.15, 1.15):
        for dz in (-1.03, 1.03):
            beam(m, [chair_x+dx, chair_y-.15, chair_z+dz],
                 [chair_x+dx*1.17, -8.25, chair_z+dz*1.17], .065, C*.7, 7)
    for dx in (-1.25, 1.25):
        beam(m, [chair_x+dx, chair_y, chair_z-1],
             [chair_x+dx, chair_y+3.55, chair_z-1.3], .08, WHITE*.85, 10)
    for j in range(10):
        yy = chair_y+1.5+j*.19
        beam(m, [chair_x-1.25, yy, chair_z-1.15],
             [chair_x+1.25, yy, chair_z-1.15], .035, C*.7, 5)
    # The rule book/desk is separate from the chair and contains only syntax.
    box(m, [11.2, -3.6, -8.2], [6, .35, 3.8], WHITE*.7, True)
    for x in (8.5, 13.9):
        beam(m, [x, -3.9, -9.7], [x, -8.2, -9.7], .08, C*.55)
    for page in range(8):
        for row in range(7):
            for col in range(5):
                symbol(m, [9.2+col*.77, -3.38+page*.012, -9.4+row*.38],
                       .21, page+row+col, C*.45)

    m = out['chinese_carriage']
    beam(m, [-13.5, 7.6, .5], [13.5, 7.6, .5], .18, WHITE*.65, 45)
    for x in np.linspace(-13, 13, 47):
        box(m, [x, 7.6, .5], [.11, .55, .72], C*.55)
    box(m, [-8.1, 6.8, .5], [2.1, .9, 1.6], ACC*.8, True)
    for zz in (-.1, 1.1):
        gear(m, [-8.1, 7.65, zz], .52, C*.9, teeth=22)
    beam(m, [-8.1, 6.4, .5], [-8.1, 4.5, .2], .1, WHITE*.8, 8)
    for dx in (-.48, .48):
        trace(m, [[-8.1, 4.5, .2], [-8.1+dx, 4.2, .2],
                  [-8.1+dx, 3.6, .2], [-8.1+dx*.55, 3.45, .2]], .025, ACC*.9)

    # SMILING MASK / SHOGGOTH: polished outer interface, alien work behind.
    left, right = out['shoggoth_mask'], out['shoggoth_split']
    for sign, m in ((-1, left), (1, right)):
        for inset in (0, .13, .32):
            q0, q1 = (math.pi/2, 3*math.pi/2) if sign < 0 else (-math.pi/2, math.pi/2)
            pts = [[(9.8-inset)*math.cos(q), .5+(6.6-inset)*math.sin(q), 3.9]
                   for q in np.linspace(q0, q1, 140)]
            line(m, pts, WHITE*(.9 if inset == 0 else .30))
        # Eye sockets are above the word corridor. Crisp crescent pupils.
        eye_x = sign*4.05
        for r in (.78, .92, 1.06):
            ring(m, [eye_x, 3.08, 4.05], r, C*.9, n=72, squash=.67)
        for dx in np.linspace(-.46, .46, 11):
            line(m, [[eye_x+dx, 2.80, 4.08], [eye_x+dx, 3.35, 4.08]], C*.34)
        # Half of a single very friendly smile. Smile exposes as mask splits.
        qa, qb = (math.pi, 1.5*math.pi) if sign < 0 else (1.5*math.pi, 2*math.pi)
        for yy in (-.06, .06, .18):
            line(m, [[5.7*math.cos(q), -2.4+1.65*math.sin(q)+yy, 4.12]
                     for q in np.linspace(qa, qb, 78)], WHITE*.95)
        for yy in np.linspace(-3.3, 3.1, 20):
            xx = sign*(8.35+.38*math.cos(yy))
            line(m, [[xx, yy, 3.82], [xx-sign*.38, yy+.13, 3.82]], C*.4)
        # Thickness is constructed from contour ties, not a filled mask face.
        for q in np.linspace(q0, q1, 38):
            p = np.array([9.8*math.cos(q), .5+6.6*math.sin(q), 3.9])
            line(m, [p, p+[0, 0, -.75]], C*.38)

    m = out['shoggoth_shell']
    for k in range(18):
        q = math.tau*k/18
        pts = []
        for s in np.linspace(0, 1, 90):
            rad = 8.5+2.2*math.sin(s*math.pi)
            pts.append([rad*math.cos(q), .2+rad*.70*math.sin(q), -1.2-10.3*s])
        line(m, pts, C*.29)
    for zz in np.linspace(-2, -12.5, 15):
        ring(m, [0, .2, zz], 8.5+1.6*math.sin((zz+2)/10.5*math.pi),
             C*.22, n=116, squash=.70)

    m = out['shoggoth_tendrils']
    for sign in (-1, 1):
        for j in range(13):
            # Multistrand biological cables spill out from behind the smile.
            pts = []
            for s in np.linspace(0, 1, 92):
                x = sign*(7.5+8.2*s+.8*math.sin(s*8+j*.7)*s)
                y = (-7.3+j*1.18)*(1-.18*s)+1.1*math.sin(s*9+j*.51)*s
                z = -7.7+5.2*s+1.5*math.sin(s*5+j*.33)
                pts.append([x, y, z])
            pts = np.asarray(pts)
            for strand in range(4):
                phase = np.linspace(0, 13, len(pts))+strand*math.pi/2
                offset = np.c_[np.zeros(len(pts)), np.cos(phase), np.sin(phase)]*.11
                line(m, pts+offset, ACC*(.65 if strand == 0 else .28))
            # Small suckers make the hidden motive visibly organic.
            for k in range(9, len(pts)-5, 8):
                ring(m, pts[k]+[0, 0, .10], .12+.035*(k%3),
                     WHITE*.42, n=20, squash=.65)

    m = out['shoggoth_puppetry']
    for sign in (-1, 1):
        for j in range(12):
            yy = -5.6+j*1.03
            p = np.array([sign*(8.1+.9*math.cos(yy*.4)), yy, 3.0])
            mid = p+[sign*1.15, .4*math.sin(j), -5]
            end = np.array([sign*(11.5+(j%3)*1.1), yy*.9, -9.7])
            trace(m, [p, mid, end], .04, ACC*.54, 3)
            ring(m, p, .16, C*.9, n=24)
            box(m, end, [.42, .7, .4], C*.6, True)
    # Articulated control fingers hold the interface from behind its rim.
    for sign in (-1, 1):
        for yy in (-5.4, 5.2):
            for finger in range(4):
                x = sign*(7.2+finger*.55)
                for a, b in (([x, yy, -4], [x+sign*.38, yy+.3, -.8]),
                             ([x+sign*.38, yy+.3, -.8], [x, yy+.15, 2.6])):
                    beam(m, a, b, .065, WHITE*.55, 7)

    m = out['shoggoth_organs']
    # Multiple eyes behind the simple two-eyed interface: alien internals.
    for side in (-1, 1):
        for k in range(3):
            center = np.array([side*(2.6+k*1.35), (-1 if k%2 else 1)*(3.8+k*.24), -5.2-k*.5])
            for rr in (.35, .62, .83):
                ring(m, center, rr, ACC*.85, n=64, squash=.62)
            ring(m, center+[0,0,.09], .18, WHITE, n=38, squash=1.5)
            for q in np.linspace(0, math.tau, 18, endpoint=False):
                p=center+[.85*math.cos(q),.54*math.sin(q),0]
                line(m,[p,p+[side*.4,.6*math.sin(q*2),-1.6]],C*.6)
    for sign in (-1, 1):
        for j in range(7):
            x, y, z = sign*(8.3+(j%2)*1.6), -6.6+j*2.03, -8.2-(j%3)*1.2
            for rr in (.42, .63, .84):
                ring(m, [x, y, z], rr, ACC*.7, n=54, squash=.7)
            for q in np.linspace(0, math.tau, 18, endpoint=False):
                a = np.array([x+.86*math.cos(q), y+.6*math.sin(q), z])
                b = a+[sign*.56, .35*math.sin(q*3), -1.15]
                line(m, [a, b], C*.6)
        for lane in range(6):
            pts = [[sign*(10.6+.3*math.sin(y*.7+lane)), y, -11.8+lane*.32]
                   for y in np.linspace(-8, 8, 120)]
            line(m, pts, ACC*.22)

    # PAPERCLIP OPTIMIZER: recognizable human objects become identical wire.
    m = out['paperclip_sources']
    # Table on the input side, chair below it, open door behind: raw resources.
    box(m, [-11.6, 4.1, -5.8], [6.2, .35, 4.2], WHITE*.9, True)
    for x in (-14.3, -8.9):
        for z in (-7.5, -4.1):
            beam(m, [x, 3.9, z], [x, .5, z], .075, C*.65, 8)
    box(m, [-12.5, -3.6, -5.0], [3.0, .3, 2.7], WHITE*.85, True)
    for x in (-13.8, -11.2):
        beam(m, [x, -3.6, -6.1], [x, -.5, -6.5], .07, C*.8, 9)
        beam(m, [x, -3.8, -3.9], [x, -6.8, -3.7], .07, C*.65, 8)
        beam(m, [x, -3.8, -6.1], [x, -6.8, -6.3], .07, C*.65, 8)
    for yy in np.linspace(-2.5, -.8, 9):
        line(m, [[-13.8, yy, -6.4], [-11.2, yy, -6.4]], WHITE*.65)
    # Door at the top of the composition is visibly reduced into wire strips.
    for inset in (0, .16, .34):
        line(m, [[-2.4+inset, 2.8, -11], [-2.4+inset, 8.5-inset, -11],
                 [2.4-inset, 8.5-inset, -11], [2.4-inset, 2.8, -11]], C*.7)
    box(m, [.2, 5.55, -11.1], [3.8, 5.2, .25], WHITE*.65, True)
    ring(m, [1.38, 5.2, -10.91], .17, ACC*.9, n=32)
    for j in range(13):
        trace(m, [[-9.1+j*.11, 3.95, -5.5], [-6.6, .5-j*.16, -5.0],
                  [-5.0, -5.9, -3.0]], .022, ACC*.44)

    m = out['paperclip_conveyor']
    for z in (-.6, -3.8):
        beam(m, [-17, -6.8, z], [4, -6.8, z], .13, C*.6, 42)
    for x in np.linspace(-16.8, 3.8, 60):
        # Roller cylinders are drawn as parallel rings joined by their axle.
        for z in (-.65, -3.75):
            ring(m, [x, -6.55, z], .26, WHITE*.55, axis=2, n=24)
        line(m, [[x, -6.3, -.65], [x, -6.3, -3.75]], C*.42)
    for x in np.linspace(-16.4, 3.5, 30):
        box(m, [x, -6.1, -2.2], [.42, .25, 2.85], C*.4)
    for x in (-15.6, -10, -4.4, 2.):
        beam(m, [x, -6.9, -2.2], [x, -8.8, -2.2], .12, C*.4, 7)
    for x in np.linspace(-15.5, .5, 21):
        line(m, [[x-.22, -5.83, -2.2], [x+.23, -5.83, -2.2],
                 [x+.05, -5.70, -2.2]], ACC*.8)

    m = out['paperclip_shredder']
    for x in (-2.0, 2.0):
        beam(m, [x, -8.4, -4.8], [x, -3.3, -4.8], .19, C*.8, 13)
    beam(m, [-2, -3.3, -4.8], [2, -3.3, -4.8], .19, WHITE*.8, 10)
    for j in range(18):
        x = -1.82+j*.214
        gear(m, [x, -5.0, -3.7], .66, ACC*.8, axis=0, teeth=15)
        gear(m, [x, -5.84, -3.7], .66, C*.85, axis=0, teeth=15)
    for j in range(25):
        x = -1.8+j*.148
        line(m, [[x, -3.6, -3.15], [x+.04, -4.4, -3.2],
                 [x+.19, -5.8, -3.3], [x+.4, -7.2, -3.6]], WHITE*.45)
    for x in (-1.95, 1.95):
        box(m, [x, -4.35, -3.4], [.34, .45, 1.7], WHITE*.65, True)

    m = out['paperclip_forming']
    # Raw straight wire follows an increasingly recognizable U-shaped die.
    for k in range(16):
        x = 3.4+k*.20
        line(m, [[x, -6.0, -3.2], [x, -4.5, -3.2]], C*.45)
    for offset in (-.13, 0, .13):
        clip(m, [5.7, -5.7, -2.9+offset], 1.8, C*.8, twin=True)
    for x, y in ((4.91, -4.52), (6.53, -4.52), (5.56, -7.01)):
        for z in (-2.7, -3.3):
            gear(m, [x, y, z], .24, WHITE*.9, teeth=20)
    beam(m, [3.8, -8.7, -4.3], [7.5, -8.7, -4.3], .13, C*.7, 14)
    for xx in (4.2, 7.2):
        beam(m, [xx, -8.6, -4.3], [xx, -3.4, -4.3], .10, C*.6, 14)
    for j in range(24):
        z = -2.7-j*.1
        line(m, [[6.6, -5.9, z], [7.5, -5.9, z], [8.2, -5.1, z]], ACC*.5)

    m = out['paperclip_swarm']
    # Fill all three dimensions, preserving a passage for the current word.
    for layer in range(7):
        z = 4.2-layer*2.5
        for row in range(9):
            y = -7.9+row*1.83
            for col in range(9):
                x = -15.7+col*3.92
                if abs(x) < 7.2 and abs(y) < 2.8:
                    continue
                if x < 4 and y > -4 and layer < 2:
                    continue  # The first finished clips emerge beside the die.
                ss = .48+.10*((layer+row+col)%3)
                angle = .10*math.sin(col*1.9+row*.7+layer)
                clip(m, [x+.23*math.sin(row+layer), y, z], ss,
                     ACC*(.45+.07*(layer%3)) if col%3 == 0 else C*.55,
                     axis=2, angle=angle, twin=layer < 2)

    m = out['paperclip_planet']
    center, rad = np.array([12.35, 4.8, -8.5]), 3.15
    for lat in np.linspace(-1.4, 1.4, 21):
        ring(m, center+[0, rad*math.sin(lat), 0], rad*math.cos(lat),
             WHITE*.45, axis=1, n=120)
    for lon in np.linspace(0, math.tau, 25, endpoint=False):
        pts = [center+rad*np.array([math.cos(q)*math.cos(lon), math.sin(q),
                                   math.cos(q)*math.sin(lon)])
               for q in np.linspace(-math.pi/2, math.pi/2, 111)]
        line(m, pts, C*.55)
    # Meridians unravel and feed the same die, depicting consumption of world.
    for j in range(18):
        start = center+rad*np.array([math.cos(j*.35), -.56, math.sin(j*.35)])*.8
        end = np.array([6.4+j*.025, -4.2, -3.3])
        pts = []
        for s in np.linspace(0, 1, 80):
            p = start*(1-s)+end*s
            p[0] += math.sin(s*math.pi)*1.5
            p[2] += math.sin(s*math.pi)*(.5+j*.035)
            pts.append(p)
        line(m, pts, ACC*(.35+.02*(j%4)))

    # ORTHOGONALITY: capability and terminal goal are independent dimensions.
    m = out['orthogonal_frame']
    origin = np.array([-9., -6.8, -7.])
    ends = [np.array([16., -6.8, -7.]), np.array([-9., 8.5, -7.]),
            np.array([-9., -6.8, 5.5])]
    for k, end in enumerate(ends):
        beam(m, origin, end, .12, WHITE*.67 if k < 2 else C*.4, 30)
        u, v = basis(origin, end)
        direction = (end-origin)/np.linalg.norm(end-origin)
        for d in (u, -u, v, -v):
            line(m, [end-direction*.8+d*.4, end, end-direction*.8-d*.4],
                 WHITE*.85)
    # Exact 90-degree bracket can be read even without labels.
    line(m, [origin+[0, 1.6, 0], origin+[1.6, 1.6, 0], origin+[1.6, 0, 0]], ACC)
    for step in np.linspace(0, 24.5, 50):
        p = origin+[step, 0, 0]
        line(m, [p+[0, -.19, .22], p+[0, .19, .22]], C*.65)
    for step in np.linspace(0, 14.8, 45):
        p = origin+[0, step, 0]
        line(m, [p+[-.23, 0, .22], p+[.23, 0, .22]], C*.65)
    for y in np.linspace(-7.6, 8.6, 23):
        line(m, [[-16.4, y, -12.4], [-7.7, y, -12.4]], C*.18)
    for x in np.linspace(-16.4, -7.7, 18):
        line(m, [[x, -7.6, -12.4], [x, 8.6, -12.4]], C*.18)

    m = out['orthogonal_ability']
    for level in range(9):
        y = -5.9+level*1.61
        modules = min(7, 1+level)
        for j in range(modules):
            x = -15.45+j*.85
            box(m, [x, y, -7.4], [.66, 1.18, 1.05], C*.63, True)
            for z in (-6.83, -7.97):
                for pin in range(7):
                    line(m, [[x-.31, y-.44+pin*.145, z],
                             [x+.31, y-.44+pin*.145, z]], WHITE*.28)
        trace(m, [[-15.8, y-.53, -8.3], [-8.5, y-.53, -8.3],
                  [-8.5, y+.53, -8.3]], .025, C*.65)
    for lane in range(13):
        x, z = -16.5+lane*.115, -9.5-(lane%3)*.13
        trace(m, [[x, -7.4, z], [x, 8.9, z], [-8.7, 8.9, z]],
              .018, C*(.3+.025*(lane%3)))

    m = out['orthogonal_goal']
    target = np.array([11., 3.8, -5.5])
    for rr in (2.65, 2.89, 3.05):
        ring(m, target, rr, ACC*.68, n=140)
    ring(m, target, 3.0, C*.5, axis=1, n=140)
    ring(m, target, 3.0, C*.5, axis=0, n=140)
    clip(m, target+[0, 0, .14], 2.28, WHITE, twin=True)
    for sign in (-1, 1):
        beam(m, target+[sign*3.2, 0, 0], target+[sign*4.5, 0, 0],
             .17, ACC*.7, 8)
        box(m, target+[sign*3.15, 0, 0], [.45, .90, .70], WHITE*.65, True)
    # Locked terminal target has a latch and two ratchet pawls.
    beam(m, [11, .6, -5.5], [11, -6.4, -5.5], .15, ACC*.65, 22)
    for y in np.linspace(-5.9, .4, 22):
        line(m, [[10.83, y, -5.3], [11.23, y+.14, -5.3]], ACC*.7)
    for sign in (-1, 1):
        line(m, [[11+sign*.95, -2.1, -4.9], [11+sign*.22, -1.6, -4.9],
                 [11+sign*.22, -2.9, -4.9]], WHITE*.85)

    m = out['orthogonal_couplings']
    # Two independent axles occupy perpendicular planes; no correcting wire.
    for center, axis in (([-9, -6.8, -7], 2), ([7.3, -6.8, -7], 0)):
        for rr in (.72, 1.03, 1.24):
            ring(m, center, rr, C*.7, axis=axis, n=84)
        gear(m, center, 1.34, WHITE*.8, axis=axis, teeth=36)
    beam(m, [-9, -6.8, -6.85], [-9, -6.8, 5.5], .08, C*.6, 28)
    beam(m, [7.3, -6.8, -11.5], [7.3, -6.8, 2.0], .08, ACC*.6, 28)
    for x in np.linspace(-6.4, 5.3, 18):
        box(m, [x, -8.2, -7], [.42, .7, .95], C*.30, True)
    # Small physical caliper demonstrates right angle, without a semantic word.
    for z in (-6.7, -6.4):
        line(m, [[-8.65, -5.45, z], [-7.7, -5.45, z], [-7.7, -6.4, z]],
             WHITE*.85)

    m = out['orthogonal_clips']
    # Identical goals repeated across escalating capability: no moral drift.
    for j in range(8):
        y = -5.4+j*1.75
        clip(m, [16.15, y, -8.4], .61, ACC*.85, twin=True)
        for z in (-8.5, -9.1):
            line(m, [[14.95, y-.75, z], [17.28, y-.75, z],
                     [17.28, y+.75, z], [14.95, y+.75, z]], C*.3, True)
        line(m, [[14.8, y, -8.8], [14.25, y, -8.8]], ACC*.55)

    m = out['orthogonal_ascent']
    # A rising bank of chevrons and fine bundled conductors has a clear vector.
    for j in range(26):
        y = -7.5+j*.63
        for dx in (-.18, .0, .18):
            line(m, [[-11.5+dx, y-.35, -4.9], [-10.8+dx, y+.12, -4.9],
                     [-10.1+dx, y-.35, -4.9]], C*.8)
    for lane in range(22):
        x = -12.1+lane*.12
        pts = [[x+.04*math.sin(y*2+lane), y, -5.4-.07*(lane%4)]
               for y in np.linspace(-8.5, 9.1, 133)]
        line(m, pts, C*(.27+.03*(lane%3)))
    return out
