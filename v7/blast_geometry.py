"""Line-only impact apparatus for the v7 music-video renderer.

All coordinates are local to an impact origin.  ``+z`` points towards a camera
looking down -z.  Layers have deliberately different silhouettes and may be
drawn separately.  No bitmap assets, filled faces, or text are used.

Suggested animation (seconds after a hit):
    pressure: 0.12 s BEFORE hit, contract 1.4 -> 0.25, disappear on hit.
    shockwaves: first 0.45 s, scale 0.08 -> 2.6, fade late, not constant spin.
    shards: 0.04..0.9 s, scale 0.2 -> 2.0, travel +z and fall in y.
    plates: 0.0..0.7 s, scale .45 -> 1.8 with an oblique rotation.
    streaks: first .12..35 s, translate +z 0 -> 18 (lens fly-by).
    arcs: .15..1.0 s, irregular on/off gain, scale .9 -> 1.3.

Base bounds are roughly x +/- 18, y +/- 12, z -12..16.  Each group is a
normal Mesh so the caller can use independent model/sc/action uniforms.
"""


def build_blast(Mesh, np, math, C, WHITE, ACC):
    rng = np.random.default_rng(740813)
    groups = {key: Mesh() for key in
              ('pressure', 'shockwaves', 'shards', 'plates', 'streaks', 'arcs')}
    C, WHITE, ACC = (np.asarray(v, dtype=float) for v in (C, WHITE, ACC))
    tau = math.tau

    def norm(v):
        v = np.asarray(v, dtype=float)
        return v / max(float(np.linalg.norm(v)), 1.e-9)

    def basis(n):
        u = norm(np.cross(n, [0, 0, 1] if abs(n[2]) < .85 else [0, 1, 0]))
        return u, norm(np.cross(n, u))

    def mix(a, b, w):
        return a * (1 - w) + b * w

    # 1. The held breath: a pinched, asymmetric cage.  It reads as machinery
    # being pulled taut, rather than an already exploded particle sphere.
    m = groups['pressure']
    for side in (-1, 1):
        for i in range(28):
            a = (i + .25) / 28 * tau
            outer = np.array([16 * math.cos(a), 10 * math.sin(a), -6 + 2 * math.sin(a*3)])
            tip = np.array([1.7 * math.cos(a), 1.1 * math.sin(a), side * .8])
            pts = []
            for t in np.linspace(0, 1, 30):
                p = outer * (1-t) + tip * t
                p[2] += side * math.sin(t * math.pi) * (2.5 + .6 * math.sin(a*5))
                pts.append(p)
            m.line(pts, mix(C, WHITE, .3))
            # Small tension-ladder rungs stay perspective coherent.
            for t in (.16, .31, .48, .67):
                p = outer*(1-t)+tip*t
                d = np.array([-math.sin(a), math.cos(a), .15*side]) * (.32 + .8*(1-t))
                m.line([p-d, p+d], ACC * .8)
    for j in range(8):
        r = .7 + j * .17
        m.line([[r*math.cos(a), r*.65*math.sin(a), (j-4)*.28]
                for a in np.linspace(0, tau, 100)], WHITE)

    # 2. Impact fronts: interrupted, nested elliptical ribbons, with shallow
    # 3D buckling and uneven thickness.  Five different fronts cannot resolve
    # into a single turning ball even at the peak frame.
    m = groups['shockwaves']
    for layer in range(5):
        base = 2.4 + layer * 1.8
        tilt = -.32 + layer*.17
        for sector in range(9):
            start = sector*tau/9 + .04*math.sin(layer+sector)
            stop = start + tau/9 * (.64 + .26*rng.random())
            for band in range(3):
                width = (band-1)*(.055 + .11*math.sin(sector*1.7+layer)**2)
                pts = []
                for a in np.linspace(start, stop, 48):
                    ripple = 1 + .035*math.sin(13*a+layer) + .014*math.sin(37*a)
                    x = (base+width)*1.55*math.cos(a)*ripple
                    y = (base+width)*.76*math.sin(a)*ripple
                    z = math.sin(a*3+layer)*(.2+layer*.06) + x*tilt + (layer-2)*.48
                    pts.append([x, y, z])
                m.line(pts, mix(WHITE, ACC, layer/7) * (1.05 if band == 1 else .65))
            # Finite cross-links reveal a thin fractured sheet, not a HUD.
            for a in (start, stop):
                x = base*1.55*math.cos(a); y = base*.76*math.sin(a)
                z = math.sin(a*3+layer)*(.2+layer*.06)+x*tilt+(layer-2)*.48
                m.line([[x*.975,y*.975,z-.15], [x*1.025,y*1.025,z+.15]], WHITE)

    # 3. Directional splinters: long irregular tetrahedral wire fragments,
    # biased along three pressure axes instead of uniform spherical dust.
    m = groups['shards']
    axes = [norm([1,.23,.55]), norm([-1,-.38,.8]), norm([.22,1,.26])]
    for i in range(540):
        axis = axes[i % 3] * (-1 if i % 7 == 0 else 1)
        direction = norm(axis + rng.normal(0,.38,3))
        u, v = basis(direction)
        radius = rng.uniform(2.2, 11.5)
        center = direction * radius
        center[0] *= 1.25
        center[1] *= .76
        length = rng.uniform(.45,2.1) * (1.7 if i % 11 == 0 else 1)
        width = rng.uniform(.035,.17)
        tail = center-direction*length*.55
        tip = center+direction*length*.65
        vertices = [tail-u*width-v*width*.4, tail+u*width-v*width*.5,
                    tail+v*width, tip]
        color = mix(WHITE, ACC, rng.uniform(.05,.8))
        for a,b in ((0,1),(1,2),(2,0),(0,3),(1,3),(2,3)):
            m.line([vertices[a],vertices[b]], color)
        # Intermittent split trails are stretched behind the individual shard.
        for k in range(3):
            begin = center-direction*(length*.6+k*.55)
            end = begin-direction*(.22+k*.16)
            m.line([begin+u*width*(k-1),end+u*width*(k-1)], color*.55)
        if i % 3 == 0:
            for k in range(3):
                d = (k+1)/4
                m.line([vertices[0]*(1-d)+tip*d,vertices[1]*(1-d)+tip*d], C*.8)

    # 4. A structure visibly breaking: skew plates, torn diagonals, hatching,
    # and disconnected support struts.  These large edges sell the scale.
    m = groups['plates']
    for i in range(86):
        a = i*2.399963229728653
        radius = 4 + (i % 9)*.83
        center = np.array([math.cos(a)*radius*1.3, math.sin(a)*radius*.7,
                           rng.uniform(-7,5)])
        normal = norm([math.cos(a)*.7,math.sin(a)*.45,rng.uniform(.45,1.25)])
        u,v = basis(normal)
        w,h = rng.uniform(.45,1.5), rng.uniform(.35,1.3)
        corners = [center+u*w*x+v*h*y+normal*rng.uniform(-.12,.12)
                   for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        m.line(corners, mix(C,WHITE,.4), closed=True)
        # Second fractured rim and cross-structure establish actual volume.
        rear = [p-normal*.17 for p in corners]
        m.line(rear, C*.6, closed=True)
        for p,q in zip(corners,rear):m.line([p,q],WHITE*.65)
        split = center + u*w*rng.uniform(-.5,.5)
        m.line([corners[0], split-v*h*.15, split+v*h*.4, corners[2]], ACC)
        m.line([corners[1],center+normal*.15,corners[3]],WHITE*.65)
        for k in range(1,12):
            f = k/12
            left = corners[0]*(1-f)+corners[3]*f
            right = corners[1]*(1-f)+corners[2]*f
            # A real gap follows the tear instead of a complete grid face.
            m.line([left, left*.55+right*.45-u*.05], C*.55)
            m.line([left*.38+right*.62+u*.05, right], C*.55)
        # The supporting truss breaks apart at the same seam.
        foot = center-normal*1.1-v*.25
        m.line([corners[0],foot,corners[1]],ACC*.8)
        m.line([foot,foot-normal*.7+u*.2],WHITE*.65)

    # 5. Near-lens pieces.  They start outside the clear central lyric area
    # and occupy a broad 16:9 field.  Move +z for extremely fast edge fly-bys.
    m = groups['streaks']
    for i in range(660):
        a = rng.uniform(0,tau)
        r = rng.uniform(.68,1.35)
        p = np.array([math.cos(a)*r*16,math.sin(a)*r*9,rng.uniform(-12,9)])
        d = norm([p[0]*.2,p[1]*.18,1.7])
        length = rng.uniform(.65,3.8)
        u,v = basis(d)
        for lane in range(2 if i%3 else 3):
            q = p+u*(lane-1)*.045
            pts=[]
            for t in np.linspace(0,1,7):
                pts.append(q+d*length*t+v*.025*math.sin(t*math.pi))
            m.line(pts,mix(C,WHITE,rng.uniform(.3,1))*(.6 if lane else 1.0))

    # 6. Aftershock whips: angular filament arcs joining displaced fragments,
    # with short forks.  Each is a spatial broken path rather than a ring.
    m = groups['arcs']
    for i in range(114):
        a = rng.uniform(0,tau)
        r = rng.uniform(4,13)
        start = np.array([math.cos(a)*r, math.sin(a)*r*.72,rng.uniform(-5,4)])
        b = a+rng.uniform(.3,1.05)*(-1 if i%2 else 1)
        end = np.array([math.cos(b)*r*1.13, math.sin(b)*r*.72,rng.uniform(-4,5)])
        d = end-start; u,v = basis(norm(d))
        points=[]
        for k,t in enumerate(np.linspace(0,1,42)):
            envelope=math.sin(t*math.pi)
            jag = .14*math.sin(k*2.3+i)+.22*math.sin(k*.71+i*.7)
            points.append(start+d*t+u*jag*envelope+v*.38*math.sin(t*math.pi*2+i)*envelope)
        m.line(points,mix(WHITE,ACC,.16 if i%3 else .65))
        for at in (10,23,32):
            p=points[at]
            branch=[p]
            for k in range(1,8):
                branch.append(p+u*k*.11+v*math.sin(k*1.7+i)*.11+norm(d)*k*.07)
            m.line(branch,C*.8)
    return groups
