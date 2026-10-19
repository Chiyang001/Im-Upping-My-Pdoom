"""Continuous, hand-built line architecture for the P(doom) film.

All surfaces are bundles of actual 3-D strokes.  No image, font, texture,
shader, or scene dependency is needed by this module.  The caller owns
the four layers' transforms, travel speed, visibility, and beat envelope.
"""


def build_world(Mesh, np, math, C, WHITE, ACC):
    """Return four independent, deterministic line-only Mesh instances.

    Their principal volume is x +/- 25, y +/- 14, z -45..12.  The middle
    foreground is intentionally porous: dense physical detail lives along
    the edges, above/below the camera, and behind the lyric architecture.
    """
    rng = np.random.default_rng(510731)
    C, WHITE, ACC = (np.asarray(v, dtype=float) for v in (C, WHITE, ACC))
    layers = {name: Mesh() for name in
              ('infrastructure', 'city', 'debris', 'data_ribbons')}

    def stroke(mesh, pts, col):
        mesh.line(pts, col)

    def basis(tangent):
        tangent = np.asarray(tangent, dtype=float)
        tangent /= max(float(np.linalg.norm(tangent)), 1e-8)
        up = [0., 1., 0.] if abs(tangent[1]) < .88 else [1., 0., 0.]
        u = np.cross(tangent, up)
        u /= max(float(np.linalg.norm(u)), 1e-8)
        return u, np.cross(tangent, u)

    def cylinder(mesh, a, b, radius, col, sides=8, collars=0):
        """An open, straight pipe, drawn with rails and collar stitches."""
        a, b = np.asarray(a), np.asarray(b)
        u, v = basis(b - a)
        ring = [radius * (math.cos(t) * u + math.sin(t) * v)
                for t in np.linspace(0., math.tau, sides, endpoint=False)]
        for delta in ring:
            stroke(mesh, [a + delta, b + delta], col)
        for q in np.linspace(0., 1., collars + 2):
            center = a * (1. - q) + b * q
            mesh.line([center + delta for delta in ring], col * .8, closed=True)

    def truss(mesh, a, b, width, col, count=14):
        """Asymmetric square bridge, with diagonal load-bearing wires."""
        a, b = np.asarray(a), np.asarray(b)
        u, v = basis(b - a)
        offsets = [width * (x * u + y * v) for x, y in
                   [(-1, -1), (-1, 1), (1, 1), (1, -1)]]
        for off in offsets:
            stroke(mesh, [a + off, b + off], col)
        for j in range(count):
            p, q = a + (b-a)*j/count, a + (b-a)*(j+1)/count
            mesh.line([p + off for off in offsets], col * .7, closed=True)
            for k in range(4):
                stroke(mesh, [p + offsets[k], q + offsets[(k+1)%4]], col * .8)
            # A narrow secondary seam makes the frames read as fabricated.
            if j % 3 == 0:
                inset = (p + q) / 2
                mesh.line([inset + off*.83 for off in offsets], col*.35, closed=True)

    # ------------------------------------------------------------------
    # Continuous service infrastructure.  The ceiling and two sides have
    # distinct geometries; no radial repetition and no concentric tunnel.
    # ------------------------------------------------------------------
    infra = layers['infrastructure']
    zsamples = np.linspace(-45., 12., 65)
    banks = [(-21.4, 8.2, .10), (-17.2, -10.3, .60),
             (21.3, 5.3, 1.90), (17.7, -11.7, 2.60),
             (-5.8, 12.1, 3.10), (10.6, 11.5, 4.20),
             (-24., -2.0, 4.80), (23.1, -4.7, 5.50)]
    for bi, (cx, cy, phase) in enumerate(banks):
        for cable in range(7 + bi % 3):
            lane = cable - (6 + bi % 3) / 2
            radius = .14 + .035 * (cable % 3)
            bend = .7 + .16 * bi
            centers = []
            for zz in zsamples:
                xx = cx + .25*lane + bend*math.sin(.078*zz+phase)
                yy = cy + .22*math.sin(.21*zz+phase+.14*lane)
                yy += .16*lane + .24*math.sin(.045*zz+phase*2)
                centers.append(np.array([xx, yy, zz]))
            col = (C if cable % 4 else WHITE) * (.19 + .035*(cable%4))
            # Four parallel contours read as a drawn pipe rather than a
            # single random curve.  Different fittings identify the runs.
            for ang in [0., math.pi/2, math.pi, math.pi*1.5]:
                delta = np.array([radius*math.cos(ang), radius*math.sin(ang), 0.])
                stroke(infra, [p+delta for p in centers], col)
            for j in range(5 + cable % 3, len(centers)-1, 11 + cable%3):
                p = centers[j]
                infra.circle(radius*1.32, p, 2, col*1.25, 9)
                stroke(infra, [p+[-.24,0,0],p+[.24,0,0]], col*.7)

    # Unequal overhead crane structures, left-wall spine, and a low right
    # rail provide foreground occlusions when the camera advances.
    for k, z in enumerate(np.arange(-43., 12., 5.9)):
        truss(infra, [-24., 10.8, z], [25., 12.4-.15*(k%3), z+2.7],
              .23, WHITE*.20, 24)
        if k % 2 == 0:
            truss(infra, [-21.7,-13.,z-1.7],[-21.7,11.7,z+1.],
                  .32,C*.26,15)
        else:
            truss(infra, [22.8,-12.7,z-1.], [22.8,8.7,z+1.9],
                  .24,C*.23,12)
        truss(infra, [-24.,-11.8,z],[-10.3,-10.5,z+4.],.18,C*.22,9)
        # Offset ceiling control crates with vents and suspension stems.
        for j in range(3):
            px=-16.+j*13.2+(k%2)*2.3
            infra.box([px,10.2,z+.8],[3.8,.9,1.2],C*.22)
            for v in np.arange(-1.7,1.71,.21):
                stroke(infra,[[px+v,9.74,z+.23],[px+v,9.74,z+1.34]],WHITE*.11)
            stroke(infra,[[px-1.2,10.7,z+.7],[px-1.2,12.5,z+.7]],C*.30)

    # Long wall ladder/rack.  These small repeatable cues give actual
    # distance and speed information rather than orbiting a center object.
    for side in [-1,1]:
        x=side*24.4
        for y in [-9.2,-8.6,2.5,3.1,8.7]:
            stroke(infra,[[x,y,-45],[x,y,12]],C*.22)
        for k,z in enumerate(np.arange(-44.6,12.,.56)):
            stroke(infra,[[x,-9.2,z],[x,-8.6,z]],C*.23)
            if k%3==0:
                stroke(infra,[[x,2.5,z],[x,3.1,z]],WHITE*.18)
                stroke(infra,[[x-1.2*side,8.7,z],[x,8.7,z]],C*.20)

    # ------------------------------------------------------------------
    # Machine city / rack canyon.  The canyon's vanishing path wanders
    # off-center; blocks have stacked service bays, stair traces, circuits,
    # heat exchangers, pylons and top antennae, not blank wire boxes.
    # ------------------------------------------------------------------
    city = layers['city']
    for zi,z in enumerate(np.arange(-44.,12.,3.55)):
        center=-1.8+1.1*math.sin(zi*.29)
        for side in [-1,1]:
            for lane in range(4):
                px=center+side*(10.3+lane*3.75)+rng.uniform(-.33,.33)
                width=rng.uniform(2.2,3.25)
                depth=rng.uniform(2.2,3.0)
                height=rng.uniform(3.4,11.5)*(1.+lane*.035)
                py=-13.+height/2
                col=(C if (lane+zi)%4 else WHITE)*(.24 if lane<2 else .15)
                city.box([px,py,z],[width,height,depth],col)
                front=z+depth/2+.025
                # Inset face, multiple floor plates, and exact rack vents.
                city.box([px,py,front+.015],[width*.80,height*.94,.12],col*.57)
                bays=max(4,int(height/.65))
                for j in range(bays):
                    yy=-12.75+(j+.5)*(height-.5)/bays
                    stroke(city,[[px-width*.46,yy,front],[px+width*.46,yy,front]],col*.8)
                    for slot in range(4):
                        xx=px-width*.33+slot*width*.22
                        stroke(city,[[xx,yy+.13,front+.02],[xx+width*.13,yy+.13,front+.02]],col*.53)
                    if j%3==0:
                        stroke(city,[[px-width*.39,yy+.22,front+.03],[px-width*.30,yy+.22,front+.03]],ACC*.36)
                # Side circuit traces take right-angle paths with branches.
                for circuit in range(5):
                    yy=-12.6+(height-.8)*circuit/5
                    xx=px+side*width*.501
                    pz=z-depth*.41
                    stroke(city,[[xx,yy,pz],[xx,yy,z-.05],[xx,yy+.26,z-.05],
                                 [xx,yy+.26,z+depth*.40]],C*.19)
                    if circuit%2==0:
                        stroke(city,[[xx,yy,z-.05],[xx,yy+.71,z-.05]],col*.7)
                top=-13.+height
                if (lane+zi)%3==0:
                    for a in [-.5,.5]:
                        cylinder(city,[px+a,top,z],[px+a,top+.9,z],.11,C*.22,6,1)
                    stroke(city,[[px-.5,top+.9,z],[px+.5,top+.9,z]],WHITE*.26)
                if lane==0:
                    # Step-by-step service stair, not a single diagonal.
                    stairs=[]
                    for j in range(12):
                        xx=px-side*(width*.55+.09*j)
                        yy=-12.9+.23*j
                        stairs.extend([[xx,yy,z-.45],[xx-side*.09,yy,z-.45]])
                    stroke(city,stairs,C*.20)
                    stroke(city,[[px-side*width*.55,-12.1,z-.45],
                                 [px-side*(width*.55+1.08),-9.34,z-.45]],WHITE*.18)
            # Tall, thin service pylons alternate between the city blocks.
            xx=center+side*(9.1+.8*(zi%3))
            truss(city,[xx,-13.,z-1.2],[xx,3.7+(zi%4),z-1.2],
                  .19,C*.16,13)

    # Floor highway: imperfect edge routes and switches, not a tiled grid.
    for lane in range(28):
        xx=-25.+lane*1.85
        pts=[]
        for j,zz in enumerate(np.linspace(-45,12,49)):
            off=.34*math.sin(j*.19+lane*.71)
            pts.append([xx+off,-13.15+.025*(lane%3),zz])
        stroke(city,pts,C*(.12 if lane%5 else .25))
    for j,z in enumerate(np.arange(-44.,12.,1.12)):
        for side in [-1,1]:
            x=side*(7.2+(j%7)*.15)
            stroke(city,[[x,-13.08,z],[x+side*1.6,-13.08,z],
                         [x+side*1.6,-13.08,z+.38],
                         [x+side*3.1,-13.08,z+.38]],C*.17)

    # ------------------------------------------------------------------
    # Drifting fabricated pieces.  Each is constructed in a random local
    # 3-D basis: some large fragments cut the frame, small ones show depth.
    # ------------------------------------------------------------------
    debris=layers['debris']
    for i in range(194):
        p=np.array([rng.uniform(-25.,25.),rng.uniform(-13.,14.),rng.uniform(-45.,12.)])
        if abs(p[0])<9.5 and abs(p[1])<4.7 and p[2]>-15:
            p[0]+=13.5 if p[0]>=0 else -13.5
        scale=rng.uniform(.32,1.1) if i%6 else rng.uniform(1.6,3.6)
        u,v=basis(rng.normal(size=3));n=np.cross(u,v)
        col=(C if i%4 else WHITE)*rng.uniform(.16,.36)

        def local(pts):
            return [p+scale*(u*x+v*y+n*z) for x,y,z in pts]

        if i%4 in (0,1):
            # Broken machine panel with real grid engraving and ribs.
            coords=[[-1.,-.65,-.12],[.85,-.65,-.12],[1.,.3,-.12],
                    [.48,.77,-.12],[-.82,.77,-.12],[-1.,-.65,-.12]]
            stroke(debris,local(coords),col)
            stroke(debris,local([[x,y,.12] for x,y,z in coords]),col*.62)
            for x,y,z in coords[:-1]:
                stroke(debris,local([[x,y,-.12],[x,y,.12]]),col*.8)
            for a in np.linspace(-.75,.75,9):
                stroke(debris,local([[a,-.48,.13],[a,.48,.13]]),col*.5)
            for b in np.linspace(-.48,.48,7):
                stroke(debris,local([[-.75,b,.13],[.75,b,.13]]),col*.5)
            for a in [-.75,.65]:
                for b in [-.48,.48]:
                    theta=np.linspace(0,math.tau,12)
                    stroke(debris,local([[a+.06*math.cos(t),b+.06*math.sin(t),.14] for t in theta]),col)
        elif i%4==2:
            # Open six-tooth coupling, with paired rim and longitudinal
            # connectors.  These are individual bits, not scene-wide rings.
            for depth in [-.32,.32]:
                shape=[]
                for k in range(49):
                    theta=math.tau*k/48
                    r=.8 if k%4 in (1,2) else .62
                    shape.append([r*math.cos(theta),r*math.sin(theta),depth])
                stroke(debris,local(shape),col)
                stroke(debris,local([[.28*math.cos(t),.28*math.sin(t),depth]
                                    for t in np.linspace(0,math.tau,25)]),col*.7)
            for k in range(12):
                theta=math.tau*k/12
                a,b=.62*math.cos(theta),.62*math.sin(theta)
                stroke(debris,local([[a,b,-.32],[a,b,.32]]),col*.65)
        else:
            # Folded circuit spine, useful close foreground silhouettes.
            for j in range(6):
                y=-.8+j*.31
                stroke(debris,local([[-.7,y,-.2],[-.7,y,.2],[.7,y,.2],[.7,y,-.2]]),col)
                for a in np.linspace(-.6,.6,8):
                    stroke(debris,local([[a,y,.2],[a+.07,y+.17,.2],[a+.07,y+.17,-.2]]),col*.55)
            for a in [-.7,.7]:
                stroke(debris,local([[a,-.8,-.2],[a,.75,-.2]]),col*.65)

    # Slender, non-radial fragments create diagonal near-frame accents.
    for i in range(75):
        x=rng.choice([-1.,1.])*rng.uniform(12.,25.)
        a=np.array([x,rng.uniform(-13.,14.),rng.uniform(-43.,12.)])
        b=a+rng.normal(size=3)*[1.8,.8,2.3]
        truss(debris,a,b,rng.uniform(.05,.13),C*.22,5)

    # ------------------------------------------------------------------
    # Five physically woven data bands.  Their unequal paths cross the
    # picture diagonally and pass through depth, with stitches, edge teeth,
    # electrical branches, and alternate conductive traces.
    # ------------------------------------------------------------------
    ribbons=layers['data_ribbons']
    def band_point(b,t,w):
        if b==0:
            center=np.array([-24.+49.*t,8.6+2.2*math.sin(t*5.8),-42.+51.*t])
            axis=np.array([.17,1.,.14])
        elif b==1:
            center=np.array([22.-45.*t,-8.8+1.7*math.sin(t*7.+.4),-42.+53.*t])
            axis=np.array([.1,.97,-.22])
        elif b==2:
            center=np.array([-15.2+3.1*math.sin(t*7.1),-13.+27.*t,-44.+52.*t])
            axis=np.array([1.,.16,.05])
        elif b==3:
            center=np.array([17.2+3.1*math.sin(t*6.2+1.),13.-25.*t,-43.+50.*t])
            axis=np.array([1.,-.16,.18])
        else:
            center=np.array([-24.+49.*t,11.6+.7*math.sin(t*8.),-26.+9.*math.sin(t*4.9)])
            axis=np.array([.1,.20,1.])
        width=[1.45,1.7,1.8,1.35,1.6][b]*(1.+.12*math.sin(t*11.+b))
        axis=axis/np.linalg.norm(axis)
        # Longitudinal twist remains gentle enough to read the weaving.
        return center+axis*(w*width)+np.array([0.,.05*math.sin(t*36.+w*6.+b),0.])

    for b in range(5):
        steps=np.linspace(0.,1.,185)
        # 15 rails, including bright double stitched borders.
        for rail,w in enumerate(np.linspace(-1.,1.,15)):
            col=(WHITE*.26 if rail in (0,14) else C*(.17+.035*(rail%3)))
            if rail==7:col=ACC*.25
            stroke(ribbons,[band_point(b,float(t),float(w)) for t in steps],col)
        for j,t in enumerate(np.linspace(0.,1.,100)):
            # A fabric rib follows width and depth, not a flat overlay.
            stroke(ribbons,[band_point(b,float(t),float(w))
                            for w in np.linspace(-1.,1.,15)],C*(.20 if j%5 else .34))
            if j%3==0:
                for sign in [-1.,1.]:
                    p=band_point(b,float(t),sign)
                    q=band_point(b,min(1.,float(t)+.008),sign*1.17)
                    stroke(ribbons,[p,q],WHITE*.28)
            if j%5==0 and j<98:
                for w in [-.65,.27]:
                    t2=min(1.,float(t)+.014)
                    stroke(ribbons,[band_point(b,float(t),w),band_point(b,t2,w),
                                    band_point(b,t2,w+.18)],ACC*.33)

    return layers
