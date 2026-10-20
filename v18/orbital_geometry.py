"""A lunar destination and rising compute plant, authored as physical lines.

API: build_orbital(Mesh, np, math, C, WHITE, ACC) -> dict[str, Mesh].
Suggested use at 62.34--65.94: all seven layers share ONE fixed semantic_host.
Keep the moon present through the upward pass; reveal the ascending machine
and rail once, never wrap phase or rotate this sculpture as a whole.  Layer
gains around .75--1.15 preserve the crater silhouette at thumbnail size.

The right-hand Moon is a displaced icosphere with irregular bowl / rim
topography, not a circle, eye, astronomical interface or stock-market icon.
Three unequal computing stations climb from the near lower left to a deep
upper berth; their cooler folds, processor trays and structural rail belong
to one fabricated machine.  No logo, letters, texture, face or filled triangle
is used.  Local envelope: x +/-20, y +/-11, z -27..3.  The full central lyric
corridor abs(x)<5 and abs(y)<2 is empty at every depth.

Run this module directly for a CPU-only static audit.  It builds a small
compatible line collector and never imports ModernGL or opens a GL context.
"""


def build_orbital(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = [np.asarray(c, dtype=float) for c in (C, WHITE, ACC)]
    names = ('moon_surface', 'moon_craters', 'moon_rim', 'market_ascent',
             'orbital_rail', 'wafer_dies', 'orbital_mount')
    out = {name: Mesh() for name in names}

    def line(m, points, color=C, closed=False):
        m.line(np.asarray(points, dtype=float), color, closed=closed)

    def unit(v):
        v = np.asarray(v, dtype=float)
        return v / max(1.e-9, float(np.linalg.norm(v)))

    def basis(direction):
        n = unit(direction)
        u = unit(np.cross(n, [0., 1., 0.] if abs(n[1]) < .9 else [1., 0., 0.]))
        return u, np.cross(n, u)

    def beam(m, a, b, radius=.08, color=C, ribs=6):
        a, b = np.asarray(a, float), np.asarray(b, float)
        u, v = basis(b-a)
        corners = [radius*(u*sx+v*sy) for sx, sy in
                   ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for off in corners:
            line(m, [a+off, b+off], color)
        for j in range(ribs+1):
            p = a+(b-a)*j/ribs
            line(m, [p+off for off in corners], color*.63, True)
            if j < ribs:
                q = a+(b-a)*(j+1)/ribs
                line(m, [p+corners[j % 4], q+corners[(j+1) % 4]], color*.45)

    def plate(m, p, width, height, depth, color=C, bevel=.15):
        x, y, z = p
        w, h = width*.5, height*.5
        b = min(bevel, w*.45, h*.45)
        profile = np.asarray([[x-w+b, y-h], [x+w-b, y-h],
                              [x+w, y-h+b], [x+w, y+h-b],
                              [x+w-b, y+h], [x-w+b, y+h],
                              [x-w, y+h-b], [x-w, y-h+b]])
        front = np.c_[profile, np.full(8, z)]
        back = front.copy(); back[:, 2] -= depth
        line(m, front, color, True); line(m, back, color*.7, True)
        for a, b in zip(front, back):
            line(m, [a, b], color*.66)

    def collar(m, p, n, radius, color=C, segments=20):
        p = np.asarray(p, float); u, v = basis(n)
        line(m, [p+radius*(u*math.cos(a)+v*math.sin(a))
                 for a in np.linspace(0, math.tau, segments, endpoint=False)], color, True)

    def cable(m, points, radius=.07, color=C, strands=4):
        points = np.asarray(points, float)
        u, v = basis(points[-1]-points[0])
        for a in np.linspace(0, math.tau, strands, endpoint=False):
            off = radius*(u*math.cos(a)+v*math.sin(a))
            line(m, points+off, color)
        for j in range(1, len(points)-1):
            collar(m, points[j], points[j+1]-points[j-1], radius*1.7, WHITE*.52, 10)

    # Lunar terrain: geodesic edges avoid a latitude/longitude globe graphic.
    # Pits and their raised ejecta deform the actual 3D radius, including the
    # coarse surface beneath separately engraved high-resolution crater rims.
    centre = np.array([11.7, 4.25, -16.6]); radius = 5.95
    crater_directions, crater_sizes = [], []
    golden = math.pi*(3.-math.sqrt(5.))
    for k in range(57):
        z = .045+.93*(k+.5)/57
        rr = math.sqrt(max(0., 1-z*z)); a = k*golden+.42
        crater_directions.append([rr*math.cos(a), rr*math.sin(a), z])
        crater_sizes.append(.060+.147*((k*17) % 23)/22)
    # Four broad basins interrupt the small-crater texture at unequal angles.
    for d, size in [([-.55, .43, .72], .275), ([.45, -.42, .79], .235),
                    ([.32, .67, .65], .19), ([-.30, -.68, .66], .17)]:
        crater_directions.append(unit(d)); crater_sizes.append(size)
    crater_directions = np.asarray(crater_directions, float)
    crater_sizes = np.asarray(crater_sizes, float)

    def terrain(normals):
        n = np.atleast_2d(normals).astype(float)
        n /= np.linalg.norm(n, axis=1)[:, None]
        x, y, z = n.T
        rough = (.047*np.sin(x*31+y*17)*np.cos(z*29-y*11)
                 +.028*np.sin(y*63-z*37+x*19))
        # Chordal separation gives a smooth spherical bowl without an axis.
        chord = np.sqrt(np.maximum(0., 2.-2.*(n@crater_directions.T)))
        q = chord/crater_sizes[None, :]
        bowls = -.20*np.exp(-(q/.72)**4)
        raised = .095*np.exp(-((q-1.02)/.14)**2)
        rough += ((bowls+raised)*np.minimum(1.35, crater_sizes/.12)[None, :]).sum(axis=1)
        return centre+n*(radius+rough)[:, None]

    phi = (1+math.sqrt(5))/2
    vertices = [unit(v) for v in [(-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
                                (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
                                (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)]]
    faces = [(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),
             (1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),
             (3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),
             (4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
    for _ in range(4):
        mids = {}
        def midpoint(i, j):
            key = tuple(sorted((i, j)))
            if key not in mids:
                mids[key] = len(vertices); vertices.append(unit(vertices[i]+vertices[j]))
            return mids[key]
        refined = []
        for a, b, c in faces:
            ab, bc, ca = midpoint(a,b), midpoint(b,c), midpoint(c,a)
            refined.extend([(a,ab,ca),(b,bc,ab),(c,ca,bc),(ab,bc,ca)])
        faces = refined
    normals = np.asarray(vertices); points = terrain(normals)
    edges = {tuple(sorted(pair)) for a,b,c in faces for pair in ((a,b),(b,c),(c,a))}
    for a, b in sorted(edges):
        front = max(0., float((normals[a,2]+normals[b,2])*.5))
        col = C*(.22+.28*front)
        # A few pale mineral seams give relief without a second grid.
        if abs(float(normals[a,0]+normals[a,1]*.7)) < .055 and front > .25:
            col = WHITE*.46
        line(out['moon_surface'], [points[a],points[b]], col)

    for k, (n, size) in enumerate(zip(crater_directions, crater_sizes)):
        u, v = basis(n)
        irregular = .022+.008*(k % 3)
        for frac, brightness in ((.48,.43),(.78,.58),(1.02,.86)):
            samples = []
            for a in np.linspace(0, math.tau, 49, endpoint=False):
                r = size*frac*(1+irregular*math.sin(a*5+k)+.018*math.sin(a*9-k))
                samples.append(unit(n*math.cos(r)+(u*math.cos(a)+v*math.sin(a))*math.sin(r)))
            line(out['moon_craters'], terrain(samples)+n*.018, WHITE*brightness, True)
        # Unequal radial fractures descend into the floor, visibly curved in Z.
        for j in range(5+(k % 4)):
            a = j*math.tau/(5+k % 4)+k*.13
            ns = [unit(n*math.cos(size*f)+(u*math.cos(a)+v*math.sin(a))*math.sin(size*f))
                  for f in np.linspace(.44,1.19,6)]
            line(out['moon_craters'], terrain(ns)+n*.014, C*.53)
    # The outer limb follows a displaced sphere. Short second-depth arcs
    # expose thickness around the sphere rather than drawing concentric eyes.
    limb_n = unit([.16,.08,1.]); u, v = basis(limb_n)
    for offset, start, stop, col in [(0.,0.,math.tau,WHITE*.85),
                                    (-.13,.35,2.15,C*.65),(.12,3.7,5.3,C*.55)]:
        ns = [unit(u*math.cos(a)+v*math.sin(a)+limb_n*offset)
              for a in np.linspace(start,stop,180)]
        line(out['moon_rim'], terrain(ns), col)

    # Three nonidentical complete stations climb away from the viewer.
    # Their short upper radiator columns recall rising financial candles,
    # but remain functional manufactured objects instead of a stock chart.
    stations = [(-15.1,-5.5,-2.4,4.8,3.4,4.5),
                (-12.8,-.8,-10.8,4.7,3.9,5.5),
                (-8.9,5.0,-18.0,4.65,4.45,6.0)]
    for k, (x,y,z,w,h,d) in enumerate(stations):
        machine = out['market_ascent']
        plate(machine,[x,y,z],w,h,d,WHITE*.68,.30)
        plate(machine,[x+.16,y+.12,z+.10],w*.78,h*.72,.25,C*.78,.2)
        # Angled maintenance seam and an open cooler throat have true depth.
        line(machine,[[x-w*.43,y-h*.23,z+.13],[x+w*.20,y-h*.23,z+.13],
                      [x+w*.39,y+.15,z+.13],[x+w*.39,y+h*.32,z+.13]],C*.55)
        for j in range(14+k*3):
            zz = z-.35-j*(d-.7)/(13+k*3)
            # Folded fins project from the right upper shoulder of the case.
            yy = y+h*.22+.08*math.sin(j*.6+k)
            line(machine,[[x-w*.32,yy,zz],[x-w*.28,yy+.52,zz],
                          [x+w*.30,yy+.59,zz],[x+w*.41,yy+.2,zz],
                          [x+w*.39,yy+.03,zz]],WHITE*(.66 if j % 5 == 0 else .4))
            line(machine,[[x-w*.32,yy,zz-.05],[x-w*.28,yy+.52,zz-.05],
                          [x+w*.30,yy+.59,zz-.05]],C*.37)
        for j in range(4):
            xx = x+(j-1.5)*.88
            height = .34+.3*j+.16*k
            beam(machine,[xx,y+h*.51,z-d*.72],
                 [xx,y+h*.51+height,z-d*.72],.10,C*.65,3)
            collar(machine,[xx,y+h*.51+height,z-d*.72],[0,1,0],.16,WHITE*.7,12)
        for side in (-1,1):
            cable(machine,[[x+side*w*.36,y-h*.18,z-.3],
                           [x+side*w*.40,y-h*.32,z-d*.5],
                           [x+side*w*.34,y-h*.36,z-d+.2]],.055,C*.62)
        # Processor tray: nested housings, heat pipes and embedded die pads.
        die = out['wafer_dies']
        plate(die,[x-.15,y-.25,z+.19],w*.48,h*.40,.32,WHITE*.9,.17)
        for row in range(3):
            for col in range(5):
                px, py = x-w*.17+col*w*.078, y-h*.19+row*h*.10
                plate(die,[px,py,z+.23],w*.061,h*.071,.10,C*.79,.025)
        for lane in range(6):
            yy = y-h*.31+lane*.083
            line(die,[[x-w*.23,yy,z+.2],[x-w*.35,yy,z+.2],
                      [x-w*.38,yy+.4,z-.8],[x-w*.38,yy+.4,z-d*.7]],WHITE*.57)
        for side in (-1,1):
            for sy in (-1,1):
                collar(die,[x+side*w*.40,y+sy*h*.38,z+.04],[0,0,1],.075,WHITE*.76,10)
        # Very sparse red-orange electrical contacts, never red support legs.
        for side in (-1,1):
            line(die,[[x+side*w*.42,y-.04,z+.15],
                      [x+side*w*.42,y+.07,z+.15]],ACC*.7)

    # One silicon wafer sits obliquely in the first station's fabrication tray.
    # Multiple rim depths and clipped diced cells distinguish it from a disc UI.
    p = np.array([-15.55,-3.57,-4.2]); u = unit([1.,0.,.10]); v = unit([-.03,.54,.84])
    n = unit(np.cross(u,v)); wafer = out['wafer_dies']; wr = 1.72
    for off,col in ((0.,WHITE*.82),(-.12,C*.65),(-.20,C*.44)):
        samples = []
        for a in np.linspace(.10,math.tau-.10,110):
            samples.append(p+wr*(u*math.cos(a)+v*math.sin(a))+n*off)
        line(wafer,samples,col)
        line(wafer,[samples[0],samples[-1]],col*.8)
    for ix in range(-4,5):
        for iy in range(-4,5):
            xx,yy=ix*.34,iy*.34
            if (abs(xx)+.145)**2+(abs(yy)+.145)**2 > (wr*.91)**2:continue
            corners = [p+u*(xx+sx*.142)+v*(yy+sy*.142)+n*.018
                       for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
            line(wafer,corners,C*.72,True)
            line(wafer,[p+u*(xx-.09)+v*yy+n*.026,
                        p+u*(xx+.09)+v*yy+n*.026],WHITE*.51)

    # Fixed, rising double rail: connected computation becomes an orbital
    # launch route. The top span passes over the sung words, not through them.
    knots = np.asarray([[-17.0,-8.6,1.1],[-16.,-4.7,-5.3],[-14.2,.2,-12.5],
                        [-10.5,6.0,-20.2],[-5.8,8.65,-23.0],
                        [.1,9.25,-22.4],[5.4,8.65,-19.0],[6.3,7.75,-15.6]])
    rail = out['orbital_rail']
    for lane in (-1,1):
        shift = np.array([0.,lane*.22,lane*.38])
        for a,b in zip(knots[:-1]+shift,knots[1:]+shift):
            beam(rail,a,b,.105,WHITE*.70,8)
    for a,b in zip(knots[:-1],knots[1:]):
        for s in np.linspace(0.,1.,8,endpoint=False):
            pp = a+(b-a)*s
            beam(rail,pp+[0.,-.33,-.48],pp+[0.,.33,.48],.044,C*.66,2)
    cable(rail,knots+[0.,-.41,-.64],.065,C*.68,5)
    # Staggered fixed contact strips can reveal once along this actual route.
    for j,p in enumerate(knots[1:-1]):
        collar(rail,p,[1.,.15,-.4],.24,WHITE*.74,16)

    mount=out['orbital_mount']
    for k,(x,y,z,w,h,d) in enumerate(stations):
        # A single side keel joins the lower-left machinery to the same rail.
        a=np.array([x-w*.40,y-h*.47,z-d*.6]); b=knots[min(k+1,len(knots)-1)]
        beam(mount,a,b,.16,C*.59,7)
        for sy in (-1,1):
            cable(mount,[[x-w*.43,y+sy*h*.34,z],
                         [x-w*.50,y+sy*h*.34,z-d*.52],a,b],.06,C*.48)
        beam(mount,[x-w*.55,y-h*.57,z-.2],
             [x+w*.53,y-h*.57,z-d+.05],.17,WHITE*.53,8)
    # The lunar berth's three struts terminate at separated surface contacts.
    berth=np.array([6.3,7.75,-15.6])
    contacts=[np.array([6.35,6.5,-15.2]),np.array([6.7,7.4,-17.0]),
              np.array([7.45,8.1,-14.9])]
    for contact in contacts:
        beam(mount,berth,contact,.085,WHITE*.72,5)
        collar(mount,contact,contact-centre,.20,C*.7,16)
    return out


def audit_orbital(meshes, np):
    """Static line, palette, envelope and open-corridor diagnostics."""
    by_layer={name:len(mesh.l) for name,mesh in meshes.items()}
    data=np.asarray([p for mesh in meshes.values() for p in mesh.l],dtype=float)
    xyz,colors=data[:,:3],data[:,3:6]
    # Count actual red-dominant vertices, including scaled ACC variants.
    accent=(colors[:,0]>colors[:,1]*1.4)&(colors[:,0]>colors[:,2]*1.2)
    corridor=(np.abs(xyz[:,0])<5)&(np.abs(xyz[:,1])<2)
    # Endpoint-only checks can miss a beam crossing the empty lyric centre.
    a,b=xyz[::2],xyz[1::2];delta=b-a
    enter=np.zeros(len(a));leave=np.ones(len(a));possible=np.ones(len(a),dtype=bool)
    for axis,limit in ((0,5.),(1,2.)):
        static=np.abs(delta[:,axis])<1.e-12
        possible &= ~(static & (np.abs(a[:,axis])>=limit))
        denom=np.where(static,1.,delta[:,axis])
        lo=(-limit-a[:,axis])/denom;hi=(limit-a[:,axis])/denom
        enter=np.maximum(enter,np.where(static,-np.inf,np.minimum(lo,hi)))
        leave=np.minimum(leave,np.where(static,np.inf,np.maximum(lo,hi)))
    crossings=possible & (enter<leave-1.e-10)
    triangles=sum(len(getattr(mesh,'v',[]))//3 for mesh in meshes.values())
    bounds=bool((np.abs(xyz[:,0])<=20).all() and (np.abs(xyz[:,1])<=11).all()
                and (xyz[:,2]>=-27).all() and (xyz[:,2]<=3).all())
    finite=bool(np.isfinite(data).all())
    return dict(layers=len(meshes),line_vertices=len(data),triangles=triangles,
                by_layer=by_layer,minimum=xyz.min(axis=0).tolist(),
                maximum=xyz.max(axis=0).tolist(),accent_vertex_fraction=float(accent.mean()),
                corridor_vertices=int(corridor.sum()),corridor_crossing_segments=int(crossings.sum()),
                inside_envelope=bounds,
                finite=finite,line_only=triangles==0,
                passed=bool(bounds and finite and triangles==0 and not corridor.any() and not crossings.any()
                            and accent.mean()<=.05 and len(data)<250000))


if __name__=='__main__':
    import json
    import math
    from pathlib import Path
    import numpy as np

    class Lines:
        def __init__(self):self.l=[];self.v=[]
        def line(self,points,color,closed=False):
            pairs=list(zip(points,points[1:]))
            if closed and len(points)>1:pairs.append((points[-1],points[0]))
            for a,b in pairs:
                self.l.extend([list(a)+list(color),list(b)+list(color)])

    meshes=build_orbital(Lines,np,math,[.2,.93,.8],[.89,.95,1.],[1.,.22,.4])
    report=audit_orbital(meshes,np)
    target=Path(__file__).with_name('orbital_geometry_audit.json')
    target.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2));print(target)
    assert report['passed'],'Orbital line geometry failed static audit'
