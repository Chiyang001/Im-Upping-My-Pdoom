"""Fixed, open 3D apparatus that makes translation through a word readable.

All vertices are authored in the word host's local frame.  +Z is the approach
side, Z=0 is the word, and -Z is the space exposed after the camera crosses it.
Attach these meshes to the SAME frozen host used to plan an impact flight;
never attach them to the eye or to the next active token.  No faces, textures,
extra writing, or screen-space streaks are used.

Usage: {key: GPU(mesh) for key, mesh in build_flight_geometry(...).items()}.
Choose the impact kind, then draw it once with motion=-1 (fixed geometry)
and action=0.  A host model with unit right/up/normal basis, centered on
the isolated word, is appropriate.  Geometry already has world-sized units:
the central word aperture is roughly 20 x 10, and the apparatus spans Z +20
through -80.  If scaling is needed, use a uniform factor around .7--1.2 rather
than the glyph's baked character scale.
"""


def build_flight_geometry(Mesh, np, math, C, WHITE, ACC):
    rng = np.random.default_rng(120418)
    stages = (20., 14., 8., 2., -4., -11., -20., -31., -45., -61., -80.)
    meshes = {}

    def line(mesh, points, color):
        mesh.line(np.asarray(points, dtype=float), color)

    def rail(mesh, a, b, color, width=.09):
        """Two real edges plus short depth cross braces, not a luminous stripe."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        v = b - a
        side = np.cross(v, [0., 0., 1.])
        if np.linalg.norm(side) < 1e-6:
            side = np.array([1., 0., 0.])
        side /= np.linalg.norm(side)
        line(mesh, [a + side * width, b + side * width], color)
        line(mesh, [a - side * width, b - side * width], color * .44)
        for f in (.15, .38, .62, .85):
            p = a + v * f
            line(mesh, [p - side * width, p + side * width], color * .45)

    def collar(mesh, polygon, n, color):
        """An open-center extruded rib, with real front/back depth."""
        p = np.asarray(polygon, float)
        q = p.copy(); q[:, 2] -= .28
        mesh.line(p, color, closed=True)
        mesh.line(q, color * .30, closed=True)
        for k in range(0, len(p), n):
            line(mesh, [p[k], q[k]], color * .70)

    def pin(mesh, p, outward, color, length=.7):
        p = np.asarray(p, float); d = np.asarray(outward, float)
        q = p + d * length
        line(mesh, [p, q, q + [0, 0, -.55]], color)
        line(mesh, [q + [0, -.13, 0], q + [0, .13, 0]], color * .45)

    # Split radial iris: successive polygonal throats turn in depth, while the
    # depth rails remain continuous.  It expands after the word into a large
    # engine bore, so flying past the letter is followed by a fresh reveal.
    mesh = Mesh(); stations = []
    for j, z in enumerate(stages):
        u = max(0., -z) / 80.
        center = np.array([2.3 * math.sin(u * 1.65), -1.5 * u * u, z])
        rx = 11.7 + 1.7 * u; ry = 6.9 + 2.6 * u
        angle = .045 * j
        points = []
        for k in range(12):
            a = math.tau * k / 12 + angle
            points.append(center + [rx * math.cos(a), ry * math.sin(a), 0])
        stations.append(np.asarray(points))
        collar(mesh, points, 2, WHITE * (.72 if j % 3 == 0 else .40))
        for k in range(12):
            p = points[k]
            outward = (p - center) * [1. / rx, 1. / ry, 0.]
            pin(mesh, p, outward, ACC * .72 if (k + j) % 4 == 0 else C * .48,
                length=.65 + .18 * (k % 3))
            if k % 2 == 0:
                q = center + (p - center) * 1.11
                q[2] -= .8
                line(mesh, [p, q, q + [0, 0, -1.2]], C * .42)
    for j in range(len(stations) - 1):
        for k in range(12):
            rail(mesh, stations[j][k], stations[j + 1][k],
                 WHITE * .40 if k % 3 == 0 else C * .34)
            if (j + k) % 2 == 0:
                line(mesh, [stations[j][k], stations[j + 1][(k + 1) % 12]], C * .20)
    meshes['radial'] = mesh

    # A lift shaft that becomes a tall canyon behind the word.  Tall side masts
    # and staggered floors give the up/down component a strong physical scale.
    mesh = Mesh(); stations = []
    for j, z in enumerate(stages):
        u = max(0., -z) / 80.
        cx = -1.2 * u; cy = 6.2 * u * u
        rx = 11.4 - 1.1 * u; ry = 6.7 + 6.5 * u
        p = np.array([[cx-rx, cy-ry, z], [cx+rx, cy-ry, z],
                      [cx+rx, cy+ry, z], [cx-rx, cy+ry, z]])
        stations.append(p)
        collar(mesh, p, 1, WHITE * .53)
        for side in (-1, 1):
            # Side banks project outward, leaving the center entirely open.
            x = cx + side * rx
            for yy in np.linspace(cy-ry, cy+ry, 11):
                p0 = np.array([x, yy, z])
                pin(mesh, p0, [side, 0, 0], C * .53, .75 if j % 2 else 1.5)
            for dy in (-ry, ry):
                line(mesh, [[x, cy+dy, z], [x+side*2.2, cy+dy, z-1.6],
                            [x+side*2.2, cy+dy+math.copysign(1.8, dy), z-1.6]], ACC * .46)
        # Distinct broken platform on alternate sides, never a center crossbar.
        side = -1 if j % 2 else 1
        x = cx + side * rx
        line(mesh, [[x, cy-ry, z], [x+side*4.2, cy-ry, z],
                    [x+side*4.2, cy-ry+.7, z-2.2], [x, cy-ry+.7, z-2.2]], C * .43)
    for j in range(len(stations)-1):
        for k in range(4):
            rail(mesh, stations[j][k], stations[j+1][k], WHITE * .43, width=.15)
            a, b = stations[j][k], stations[j+1][k]
            side = -1 if k in (0, 3) else 1
            line(mesh, [a+[side*1.2, 0, 0], b+[side*1.2, 0, 0]], C * .31)
            if k in (0, 1):
                line(mesh, [a, b+[side*1.2, 0, 0], b], C * .24)
    meshes['vertical'] = mesh

    # Sheared bulkheads: off-axis frames are structurally connected, then open
    # onto side galleries.  Three dimensional shards stay OUTSIDE the aperture.
    mesh = Mesh(); stations = []
    for j, z in enumerate(stages):
        u = max(0., -z) / 80.
        cx = -4.3 * u * u; cy = 1.8 * math.sin(u * 2.3)
        rx = 11.7 + .7 * math.sin(j * .6); ry = 7.0 + 1.4 * u
        shear = .7 * math.sin(j * .7)
        p = np.array([[cx-rx+shear,cy-ry,z], [cx+rx+shear,cy-ry,z-.65],
                      [cx+rx-shear,cy+ry,z], [cx-rx-shear,cy+ry,z+.65]])
        stations.append(p)
        for k in range(4):
            a, b = p[k], p[(k+1)%4]
            # Deliberate gap at each corner: a cracked, open bulkhead.
            aa = a*.93+b*.07; bb = a*.07+b*.93
            line(mesh, [aa, bb], WHITE * .58)
            line(mesh, [aa+[0,0,-.28], bb+[0,0,-.28]], C * .30)
            outward = (aa-np.array([cx,cy,z])) * [1./rx,1./ry,0]
            q = aa + outward * (1.7 + .3*(j % 3)) + [0,0,-1.2]
            line(mesh, [aa, q, q+[0,0,-2.1], bb], ACC * .40 if k == j%4 else C * .30)
        for side in (-1, 1):
            x = cx+side*(rx+1.4)
            for h in (-1, 1):
                y = cy+h*(ry+.8)
                shard=np.array([[x,y,z], [x+side*rng.uniform(1.8,3.5),y+h*.6,z-3.2],
                                [x+side*.8,y+h*1.6,z-4.1]])
                mesh.line(shard, WHITE*.43, closed=True)
                line(mesh, [shard[0], shard[2]+[0,0,-1.2]], ACC*.52)
    for j in range(len(stations)-1):
        for k in range(4):
            rail(mesh, stations[j][k], stations[j+1][k], C*.50, .14)
            if k % 2 == j % 2:
                a,b=stations[j][k],stations[j+1][k]
                direction=np.array([-1 if k in (0,3) else 1, -1 if k<2 else 1, 0.])
                q=(a+b)*.5+direction*2.4
                line(mesh,[a,q,b],WHITE*.35)
    meshes['fracture']=mesh

    # Recursive chambers: square -> clipped octagon -> square, each with its
    # own offset and little nested load braces.  This reads as an actual chain
    # of rooms rather than repeated 2D scaled frames.
    mesh=Mesh();stations=[]
    for j,z in enumerate(stages):
        u=max(0.,-z)/80.
        cx=2.4*math.sin(u*3.2);cy=1.6*math.sin(u*4.3)
        rx=11.9+1.7*u;ry=6.8+1.3*u
        cut=1.2+(j%3)*.4
        p=np.array([[cx-rx+cut,cy-ry,z],[cx+rx-cut,cy-ry,z],
                    [cx+rx,cy-ry+cut,z],[cx+rx,cy+ry-cut,z],
                    [cx+rx-cut,cy+ry,z],[cx-rx+cut,cy+ry,z],
                    [cx-rx,cy+ry-cut,z],[cx-rx,cy-ry+cut,z]])
        stations.append(p)
        collar(mesh,p,1,WHITE*(.66 if j%3==0 else .41))
        for k in (0,2,4,6):
            a=p[k];b=p[(k+1)%8]
            d=(a-np.array([cx,cy,z]))*[1./rx,1./ry,0]
            # Outer nested corner has real backwards extrusion and no center
            # interference, so the lens can pass close to one of its edges.
            for repeat in (1,2,3):
                q=a+d*(repeat*.52)+[0,0,-repeat*.33]
                r=b+d*(repeat*.52)+[0,0,-repeat*.33]
                line(mesh,[a,q,r,b],C*(.42-repeat*.055))
            pin(mesh,(a+b)*.5,d,ACC*.62,.9)
    for j in range(len(stations)-1):
        for k in range(8):
            rail(mesh,stations[j][k],stations[j+1][k],C*.36 if k%2 else WHITE*.44)
        for k in (1,3,5,7):
            a=stations[j][k];b=stations[j+1][k]
            side=np.sign(a[:2]);side=np.r_[side,0.]
            line(mesh,[a,a+side*.65+[0,0,-1.2],b+side*.65+[0,0,1.2],b],ACC*.31)
    meshes['recursive']=mesh

    def dress_corridor(mesh, kind):
        """Continuous, deeply engraved walls remain visible after the gate.

        The word aperture stays clear.  Every detail lies on a physical side,
        floor, or ceiling, and successive panels are connected in depth.  Two
        shells accommodate the authored lateral/upward flights: the inner
        banks provide a near miss, while the taller outer walls remain ahead
        of a camera that has risen through one of the broken ceiling ribs.
        """
        mode = ('radial', 'vertical', 'fracture', 'recursive').index(kind)
        depths = np.linspace(20., -80., 29)

        def frame(z):
            u=max(0.,-z)/80.
            if kind=='radial':
                return np.array([1.25*math.sin(u*1.65),-.7*u*u,z])
            if kind=='vertical':
                return np.array([-.6*u,2.6*u*u,z])
            if kind=='fracture':
                return np.array([-1.8*u*u,.8*math.sin(u*2.3),z])
            return np.array([1.1*math.sin(u*3.2),.7*math.sin(u*4.3),z])

        def panel(p, normal, j, cell, wall):
            p=np.asarray(p,float);normal=np.asarray(normal,float)
            center=p.mean(0)
            bright=(j+cell+wall+mode)%5==0
            edge=WHITE*(.62 if bright else .36)
            mesh.line(p,edge,closed=True)
            # Recessed, inset engraved edges are actual different Z / wall
            # depth.  They have parallax under a sideways or vertical pass.
            inset=p*.82+center*.18+normal*.24
            mesh.line(inset,C*(.38 if bright else .24),closed=True)
            k=(j+cell+mode)%4
            if k<2:
                line(mesh,[inset[k],inset[(k+2)%4]],C*.28)
            else:
                q0=inset[0]*.70+inset[1]*.30
                q1=inset[3]*.70+inset[2]*.30
                line(mesh,[q0,q1],C*.29)
            # Small exposed hinge and offset contact on each physical plate.
            p0=p[0]*.75+p[1]*.25;p1=p[0]*.45+p[1]*.55
            line(mesh,[p0,p0-normal*.26,p1-normal*.26,p1],ACC*.59 if bright else WHITE*.31)
            if bright:
                q0=p[1]*.15+p[2]*.85;q1=p[1]*.85+p[2]*.15
                line(mesh,[q0-normal*.12,q1-normal*.12],ACC*.92)

        for j,(za,zb) in enumerate(zip(depths[:-1],depths[1:])):
            a,b=frame(za),frame(zb)
            # Slightly sheared bays in the fracture room, regular modules in
            # the recursive chamber, rounded conduit banks in the engine.
            rx=13.35+(.45*math.sin(j*.6) if mode!=3 else .2*(j%3))
            ry=12.6+(.9*max(0.,-za)/80. if kind=='vertical' else 0.)
            for side in (-1,1):
                for cell in range(9):
                    y0=-15.+cell*(30./9.);y1=y0+30./9.
                    p=[a+[side*rx,y0,0],a+[side*rx,y1,0],
                       b+[side*rx,y1,0],b+[side*rx,y0,0]]
                    panel(p,[side,0,0],j,cell,0 if side<0 else 1)
                for cell in range(8):
                    x0=-19.+cell*4.75;x1=x0+4.75
                    p=[a+[x0,side*ry,0],a+[x1,side*ry,0],
                       b+[x1,side*ry,0],b+[x0,side*ry,0]]
                    panel(p,[0,side,0],j,cell,2 if side<0 else 3)

            # Bright continuous edge conduits, alternating physical offsets
            # and depth jumps give the lateral flight a visible speed scale.
            for side in (-1,1):
                for yy in (-14.5,-8.3,-4.8,4.8,8.3,14.5):
                    off=np.array([side*(rx-.18),yy,0.])
                    rail(mesh,a+off,b+off,ACC*.60 if abs(yy)==8.3 else C*.48,.065)
                for xx in (-17.,-11.,-5.5,5.5,11.,17.):
                    off=np.array([xx,side*(ry-.18),0.])
                    line(mesh,[a+off,b+off],WHITE*.37 if abs(xx)==11. else C*.30)
                # A rail outside each room, visible after a vertical escape.
                for yy in (-17.8,17.8):
                    off=np.array([side*20.5,yy,0.])
                    line(mesh,[a+off,b+off],C*.43)
                    if j%2==0:
                        line(mesh,[a+off,a+[side*rx,math.copysign(ry,yy),0]],WHITE*.34)

        # Curving long hydraulic bundles keep an uninterrupted depth reference
        # even where one bulkhead has broken away; these are world-fixed.
        for side in (-1,1):
            for cable in range(12):
                pts=[]
                for z in np.linspace(20.,-80.,112):
                    c=frame(z);u=(20.-z)/100.
                    x=side*(14.7+.16*cable+.24*math.sin(u*9.+cable*.35))
                    y=-10.8+cable*1.95+.30*math.sin(u*12.+cable*.2+mode)
                    pts.append(c+[x,y,0.])
                line(mesh,pts,ACC*.62 if cable in (2,9) else C*.35)
        # Recessed outer side galleries remain when the camera skims beyond
        # an inner wall. Their ribs are intentionally staggered from it.
        for j,z in enumerate(np.linspace(18.,-78.,25)):
            c=frame(z)
            for side in (-1,1):
                for yy in (-17.8,17.8):
                    line(mesh,[c+[side*12.4,yy,0],c+[side*20.5,yy,0],
                               c+[side*20.5,yy,-1.4]],WHITE*.40)
                for yy in np.linspace(-16.,16.,9):
                    p=c+[side*20.5,yy,0]
                    line(mesh,[p,p+[side*.45,.3,-1.0],p+[0,.7,-1.7]],C*.35)

    for key,mesh in meshes.items():
        dress_corridor(mesh,key)
    return meshes
