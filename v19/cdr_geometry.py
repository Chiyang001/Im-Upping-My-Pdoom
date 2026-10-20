"""One curved, bolted cons-list machine; no detached pictogram rows.

CDR is Lisp's tail operation, as confirmed by the lyric author.  Four paired
cons sockets share a curved keel.  The head socket, tail loom and moving
selector are literal spatial relationships, while the neural bypass is an
artistic metaphor for the lyric's old-symbolic-AI allusion.
All meshes contain GL_LINES only, in the established cyan/white metal style.
"""

CDR_START, CDR_END = 84.78, 89.995


def cdr_path(u, np, math):
    """An asymmetric continuous tail, in local world-machine coordinates."""
    u = min(1., max(0., float(u)))
    return np.array([-13.+27.*u, 3.6-10.7*math.sin(u*math.pi*.79),
                     -1.8-24.5*u])


def build_cdr(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = [np.asarray(x, float) for x in (C, WHITE, ACC)]
    out = {k: Mesh() for k in ('keel', 'cons', 'links', 'tail', 'selector',
                               'head', 'bypass', 'seed')}

    def line(m, pts, col=C, closed=False):
        m.line(np.asarray(pts, float), col, closed=closed)

    def ring(m, p, radius, col, axis=2, n=32):
        m.circle(radius, pos=p, axis=axis, color=col, n=n)

    def tube(m, pts, radius=.12, col=C, strands=6):
        pts = np.asarray(pts, float)
        for j, a in enumerate(np.linspace(0, math.tau, strands, endpoint=False)):
            off = np.array([0., math.cos(a), math.sin(a)])*radius
            line(m, pts+off, col*(1. if j == 0 else .44))

    def beam(m, a, b, radius=.12, col=C):
        a, b = np.asarray(a, float), np.asarray(b, float)
        axis = b-a; axis /= max(1e-9, np.linalg.norm(axis))
        ref = np.array([0., 1., 0.]) if abs(axis[1]) < .9 else np.array([1., 0., 0.])
        p = np.cross(axis, ref); p /= np.linalg.norm(p)
        q = np.cross(axis, p)
        offsets = [radius*(i*p+j*q) for i,j in ((1,1),(-1,1),(-1,-1),(1,-1))]
        for off in offsets:
            line(m, [a+off,b+off], col)
        for u in np.linspace(0,1,7):
            center = a+(b-a)*u
            line(m, [center+x for x in offsets], col*.45, True)

    keel, cons, links = (out[k] for k in ('keel','cons','links'))
    path = np.array([cdr_path(u,np,math) for u in np.linspace(0,1,160)])
    # All four sockets are fixed to this SINGLE fabricated backbone, rather
    # than a collection of copies that float independently above the lyrics.
    for off in [np.array([0.,-1.75,-1.8]),np.array([0.,-2.45,-1.8]),np.array([0.,-2.1,-3.3])]:
        tube(keel,path+off,.11,C*.74)
    for j,u in enumerate(np.linspace(0,1,38)):
        p=cdr_path(u,np,math)
        beam(keel,p+[0,-1.75,-1.8],p+[0,-2.45,-1.8],.055,C*.4)
        beam(keel,p+[0,-2.45,-1.8],p+[0,-2.1,-3.3],.05,C*.3)
        if j%2 == 0:
            beam(keel,p+[0,-1.75,-1.8],p+[0,-.6,-.4],.065,C*.4)
    # Long diagonal return and two structural roots tie it into architecture.
    beam(keel,[-14,3,-5],[-11,-10,-20],.22,C*.37)
    beam(keel,[-11,-10,-20],[15,-8,-31],.22,C*.37)
    beam(keel,[14,-4,-29],[15,-8,-31],.16,C*.42)
    for j,u in enumerate([.035,.34,.66,.96]):
        p=cdr_path(u,np,math)
        # One asymmetric open Y-yoke: the angular CAR atom cradle and the
        # circular CDR pipe have different silhouettes.  No rectangular body,
        # no two-eyed/cassette face, no boxes aligned as an overlay row.
        for z in [-.7,-.3,.15]:
            line(cons,[p+[-2.15,.65,z],p+[-2.15,-.7,z],
                       p+[0,-1.3,z],p+[2.15,-.7,z],p+[2.15,.65,z]],C*.62)
            line(cons,[p+[0,-1.3,z],p+[0,-2.0,-1.8]],C*.58)
        for dx in [-.8,.8]:
            beam(cons,p+[dx,-.95,-.7],p+[dx,-1.8,-1.8],.065,C*.6)
        # CAR occupies an open triangular cradle, and CDR a deep socket.
        for z in [-.35,.1,.55,.9]:
            line(cons,[p+[-1.15,.83,z],p+[-1.91,-.55,z],
                       p+[-.39,-.55,z]],C*.61,True)
        for z,r in [(-.25,.82),(.0,.82),(.35,.76),(.7,.69),(.95,.57)]:
            ring(cons,p+[1.15,0,z],r,C*.65 if z<.7 else WHITE*.6)
        for a in np.linspace(0,math.tau,16,endpoint=False):
            q=np.array([math.cos(a),math.sin(a),0.])
            line(cons,[p+[1.15,0,-.25]+q*.82,p+[1.15,0,.95]+q*.57],C*.42)
        for x,y in [(-2.15,-.7),(0,-1.3),(2.15,-.7)]:
            ring(cons,p+[x,y,.2],.085,WHITE*.65,n=12)
        # The symbolic atom is a tetrahedral wire insert in the CAR cradle.
        a=p+[-1.15,0,.95]
        tetra=np.array([[0,.34,0],[-.3,-.2,.12],[.3,-.2,.12],[0,0,-.32]])+a
        for aa in range(4):
            for bb in range(aa+1,4):line(cons,[tetra[aa],tetra[bb]],WHITE*.5)
        if j<3:
            nextp=cdr_path([.34,.66,.96][j],np,math)
            pp=[p+[1.15,0,.95],p+[3.3,-.2,1.1],nextp+[-3.,.6,1.3],nextp+[-2.3,0,.8]]
            tube(links,pp,.075,WHITE*.62)
            # Actual tail pointer arrow at the recipient socket.
            q=nextp+[-2.45,0,.85]
            line(links,[q+[-.45,.24,0],q,q+[-.45,-.24,0]],WHITE*.7)
    # Tail conductor is continuous but intentionally skips the first head.
    tailpath=np.array([cdr_path(u,np,math)+[1.15,0.,1.] for u in np.linspace(.035,.96,150)])
    tube(out['tail'],tailpath,.035,WHITE*.65,strands=3)
    # A moving fork selector fits mechanically OVER the tail conductor.
    for z in [-.2,.2]:
        line(out['selector'],[[-.65,-.4,z],[-.65,.4,z],[.65,.4,z],[.65,-.4,z]],WHITE*.85)
        line(out['selector'],[[-.3,.4,z],[-.3,.75,z],[.3,.75,z],[.3,.4,z]],C*.7)
    for x in [-.65,.65]:
        line(out['selector'],[[x,-.4,-.2],[x,-.4,.2]],C*.7)
    ring(out['head'],[0,0,0],.5,WHITE*.55)
    line(out['head'],[[-.24,-.24,0],[.24,.24,0],[-.24,.24,0],[.24,-.24,0]],C*.6)
    # Neural route bridges over the cons structure.  It is bolted at both
    # ends, with many fine threads in one loom, never a detached red ribbon.
    bypass=[]
    for u in np.linspace(0,1,160):
        bypass.append([-16+34*u,5.1+1.1*math.sin(u*math.pi),1.8-29*u])
    for k in range(13):
        shift=np.array([0.,(k-6)*.045,.07*math.sin(k)])
        line(out['bypass'],np.array(bypass)+shift,C*(.53 if k==6 else .18))
    for u in [.02,.12,.88,.98]:
        p=np.array([-16+34*u,5.1+1.1*math.sin(u*math.pi),1.8-29*u])
        beam(keel,p,p+[0,-3,-2],.075,C*.35)
    for axis in range(3):ring(out['seed'],[0,0,0],.18,WHITE*.85,axis=axis,n=24)
    return out


def draw_cdr(t, vp, hit, g):
    if not CDR_START <= t < CDR_END:
        return
    np,math,tr,rot=g['np'],g['math'],g['tr'],g['rot']
    ease=g['ease'];base=g['semantic_host']('cdr',87.1,t,20.,1.12)
    amp=min(1.,(t-CDR_START)/.075,(CDR_END-t)/.075)
    def draw(key,model=base,gain=1.,reveal=1.):
        g['CDR'][key].draw(model,vp,t,0,0,-1,gain=gain*amp,reveal=reveal)
    draw('keel',gain=.72);draw('cons',gain=.85);draw('links',gain=.8)
    progress=float(ease((t-86.16)/2.20))
    draw('tail',gain=.45+.30*progress,reveal=.06+.94*progress)
    p=cdr_path(.035+.925*progress,np,math)+[1.15,0,1.08]
    draw('selector',base@tr(*p)@rot(-.22,1),gain=.8)
    head=cdr_path(.035,np,math)+[-1.15,0,1.12]
    withdraw=float(ease((t-85.7)/.6))
    draw('head',base@tr(*(head+[0,withdraw*2.2,withdraw*-.5])),gain=.58*(1-withdraw*.75))
    bypass=float(ease((t-85.38)/1.08))
    draw('bypass',gain=.78,reveal=.05+.95*bypass)
    u=float(ease((t-86.40)/2.8))
    p=np.array([-16+34*u,5.1+1.1*math.sin(u*math.pi),1.8-29*u])
    draw('seed',base@tr(*p),gain=.8)
