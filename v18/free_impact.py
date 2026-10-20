"""A finite, scene-bound invisible blow opens Sydney's containment bars.

The hand is inferred from the cage's contact patch and transferred momentum;
there is no fist, hand icon, screen overlay, or continuously looping effect.
The primary blow is on the recorded kick at 57.745 s. The 57.970 s kick is
the failed lock's rebound. Geometry stays attached to actual hinge locations.
"""
import math as _math

FREE_START = 56.20
FREE_END = 58.43
FREE_HIT = 57.745
FREE_REBOUND = 57.970
BAR_X = tuple(-14.4 + 1.2*j for j in range(25))


def _ease(x):
    x = max(0., min(1., x))
    return x*x*(3.-2.*x)


def _impulse(t, onset, attack=.020, decay=.10):
    dt = t-onset
    if dt < 0.:
        return 0.
    return _ease(dt/attack)*_math.exp(-max(0., dt-attack)/decay)


def sample_free_impact(t):
    """Pure scalar motion score, including a host-local XYZ camera shove.

    ``camera_local`` uses the free-wall host's axes: -Z flies into the cage,
    +X follows the off-centre contact, and -Y drops through the torn opening.
    It is a finite translation, not a screen-shake substitute. A camera
    director may scale the displacement to preserve the sung word's frame.
    ``target_local`` follows the broken lock into the opening.
    """
    if not FREE_START <= t < FREE_END:
        return dict(active=False, exposure=0., strike=0., rebound=0., ring=0.,
                    opening=0., preload=0., shards=0., pressure=0.,
                    camera_local=(0.,0.,0.), target_local=(0.,0.,0.),
                    roll=0., contact=(1.8,.65,-3.0))
    dt = t-FREE_HIT
    strike = _impulse(t,FREE_HIT,.017,.095)
    rebound = _impulse(t,FREE_REBOUND,.014,.075)
    # The wall stores energy before the main kick, then fails once.
    preload = _ease((t-57.56)/.16)*(1.-_ease(dt/.035))
    opening = _ease((t-FREE_HIT-.014)/.43)
    ring = (0. if dt < 0. else _math.exp(-dt/0.30)*
            _math.sin(max(0.,dt)*_math.tau*13.5))
    shard_age = max(0.,t-FREE_HIT-.025)
    shards = _ease(shard_age/.034)*(1.-_ease((t-58.22)/.21))
    pressure = _impulse(t,FREE_HIT,.012,.068)
    # Forward parallax grows as the aperture opens; the impact briefly pushes
    # the lens back before the camera surges through the failed lock.
    advance = _ease((t-FREE_HIT-.035)/.48)
    camera = (1.15*advance+.28*strike, -.72*advance+.18*rebound,
              .65*strike-5.2*advance)
    return dict(active=True, exposure=min(1.,(t-FREE_START)/.10,
                                        (FREE_END-t)/.065),
                strike=strike,rebound=rebound,ring=ring,opening=opening,
                preload=preload,shards=shards,shard_age=shard_age,
                pressure=pressure,contact=(1.8,.65,-3.),
                camera_local=camera,target_local=(1.8,-.35,-3.-7.3*advance),
                roll=-.075*strike+.027*ring)


def build_free_impact(Mesh,np,math,C,WHITE,ACC):
    """Return line-only machined cage pieces with no unmounted symbols.

    BAR_X and the two local half-bar meshes are animated about their top and
    bottom frame pivots by draw_free_impact. The frame shares the original
    linework's pale metal and muted green. Red is limited to tiny fracture
    details at the one physical failure, never a travelling scan.
    """
    result={}
    def part(name):
        m=Mesh();result[name]=m;return m
    def line(m,p,c=C,closed=False):m.line(p,c,closed)
    def ring(m,p,r,c=C,axis=2,n=24):m.circle(r,p,axis,c,n)
    def rod(m,a,b,r,c=C,n=6):
        a=np.array(a,float);b=np.array(b,float);d=b-a
        d/=max(1.e-9,np.linalg.norm(d))
        v=np.cross(d,[0,1,0] if abs(d[1])<.9 else [1,0,0])
        v/=max(1.e-9,np.linalg.norm(v));w=np.cross(d,v)
        for q in np.linspace(0,math.tau,n,endpoint=False):
            off=r*(math.cos(q)*v+math.sin(q)*w)
            line(m,[a+off,b+off],c*(1. if q<.1 else .54))
        for p in [a,b]:
            line(m,[p+r*(math.cos(q)*v+math.sin(q)*w)
                    for q in np.linspace(0,math.tau,n,endpoint=False)],c*.8,True)
    def sleeve(m,p,axis=1):
        for k in [-.19,0.,.19]:
            q=np.array(p,float);q[axis]+=k
            ring(m,q,.23,WHITE*.60,axis,12)
        for a in np.linspace(0,math.tau,6,endpoint=False):
            if axis==1:
                line(m,[[p[0]+.23*math.cos(a),p[1]-.22,p[2]+.23*math.sin(a)],
                        [p[0]+.23*math.cos(a),p[1]+.22,p[2]+.23*math.sin(a)]],C*.55)

    frame=part('cage_frame')
    # Deep side rails and their cross braces place the gate inside the room.
    for side in [-1,1]:
        for z in [-3.,-10.,-18.]:
            rod(frame,[side*15.8,-8.4,z],[side*15.8,8.4,z],.22,C*.58)
            for y in [-8.4,8.4]:
                rod(frame,[side*14.7,y,z],[side*16.8,y,z],.13,WHITE*.45)
                if z>-18:
                    rod(frame,[side*15.8,y,z],[side*15.8,y,z-7],.14,C*.43)
        for y in [-8.4,8.4]:
            rod(frame,[side*15.8,y,-3],[side*15.8,-y,-10],.075,C*.29)
        for z in [-3,-10,-18]:
            for y in [-6.5,0,6.5]:
                ring(frame,[side*15.8,y,z+.23],.19,WHITE*.5,n=12)
    for y in [-8.15,8.15]:
        for z in [-3.25,-3.,-2.75]:
            rod(frame,[-15.8,y,z],[15.8,y,z],.12,C*.63)
        for x in BAR_X:
            m=frame
            # Hinge beds are fixed even after the rods have torn out.
            for off in [-.25,.25]:ring(m,[x,y+off,-2.74],.12,WHITE*.55,n=12)
            line(m,[[x-.32,y-.34,-3],[x+.32,y-.34,-3],
                    [x+.32,y+.34,-3],[x-.32,y+.34,-3]],C*.46,True)

    for key,sgn in [('bar_upper',-1),('bar_lower',1)]:
        m=part(key)
        # End-to-end ribs and four rings are fine line geometry, not surfaces.
        rod(m,[0,0,0],[0,sgn*7.9,0],.095,C*.78)
        for y in [0,sgn*1.1,sgn*4.9,sgn*7.65]:sleeve(m,[0,y,0])
        for j in range(3):
            zz=.045*(j-1)
            line(m,[[.105,sgn*7.0,zz],[.14,sgn*7.47,zz],
                    [.06,sgn*7.9,zz]],WHITE*.47)

    locks=part('cage_locks')
    for side in [-1,1]:
        # Two lock rods terminate in frame bearings, not floating padlocks.
        rod(locks,[side*15.8,-2.9,-3.1],[side*4.8,-2.9,-3.1],.13,C*.7)
        rod(locks,[side*15.8,2.9,-3.1],[side*4.8,2.9,-3.1],.13,C*.7)
        for y in [-2.9,2.9]:
            for x in [side*5.0,side*8.,side*11.5,side*15.]:
                ring(locks,[x,y,-2.9],.23,WHITE*.6,n=18)

    bolt=part('released_bolt')
    for z in [-.12,.12]:ring(bolt,[0,0,z],.17,WHITE*.85,n=6)
    for a in np.linspace(0,math.tau,6,endpoint=False):
        p=[.17*math.cos(a),.17*math.sin(a)]
        line(bolt,[[*p,-.12],[*p,.12]],C*.72)
    ring(bolt,[0,0,.125],.075,C*.7,n=6)
    rod(bolt,[0,0,-.10],[0,0,-.38],.07,C*.68)

    chip=part('metal_chip')
    line(chip,[[-.11,0,0],[.08,-.025,.05],[.16,.08,.13]],WHITE*.85)
    line(chip,[[.08,-.025,.05],[.04,-.13,-.04]],C*.7)
    contact=part('contact_faults')
    # Short stress seams are attached to fractures on rods. They are never
    # rendered as a recognisable hand contour or as a screen-sized graphic.
    for j in range(7):
        a=j*2.399963
        rr=.32+j*.18
        p=np.array([rr*math.cos(a),rr*.65*math.sin(a),0.])
        line(contact,[p,p+[.17*math.cos(a+.7),.12*math.sin(a+.7),-.1],
                      p+[.38*math.cos(a),.28*math.sin(a),-.32]],
             WHITE*.8 if j%3 else ACC*.46)
    pressure=part('pressure_rim')
    # Broken shallow arcs catch on bars for one kick and dissipate outward.
    for a in [0.2,1.8,3.6,5.0]:
        line(pressure,[[math.cos(q),.72*math.sin(q),.11*math.sin(q*3)]
                       for q in np.linspace(a,a+.43,18)],C*.72)
    return result


def draw_free_impact(t,vp,hit,g):
    """Draw using g['FREE_IMPACT'], the existing GPU line mesh collection."""
    state=sample_free_impact(t)
    if not state['active']:return
    np,math=g['np'],g['math'];tr,rot,sc=g['tr'],g['rot'],g['sc']
    ctx,gl=g['ctx'],g['gl']
    base=g['semantic_host']('free-wall',57.9,t,18.,1.2)
    mesh=g['FREE_IMPACT'];amp=state['exposure']
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
    g['ms'].depth_mask=False;ctx.line_width=1.35
    def draw(key,matrix=base,gain=1.):
        mesh[key].draw(matrix,vp,t,0,0,-1,gain=amp*gain)
    draw('cage_frame',gain=.83)
    # Each half bends about a real fixed bearing at the frame. The contact
    # footprint reaches nearby rods first, with a 13 ms radius propagation.
    for j,x in enumerate(BAR_X):
        radius=abs(x-1.8)
        local=sample_free_impact(t-min(.043,radius*.0031))
        force=math.exp(-((x-1.8)/8.0)**2)
        side=1 if x>=1.8 else -1
        opened=local['opening'];strike=local['strike'];ring=local['ring']
        recoil=local['rebound']
        bend=force*(.055*local['preload']+.63*strike+
                    .92*opened+.085*ring+.15*recoil)
        spread=force*(.36*opened+.16*strike)
        # Outer bars retain their original alignment and carry the wave.
        tiny=ring*.025*(.25+.75*force)
        gain=.62 if abs(x)<4.8 else .88
        for upper in [True,False]:
            sgn=1 if upper else -1
            pivot=base@tr(x,sgn*8.15,-3.)
            matrix=pivot@rot(sgn*bend,0)@rot(sgn*side*spread,2)
            matrix=matrix@rot(tiny*side,1)
            draw('bar_upper' if upper else 'bar_lower',matrix,gain)
        if force>.35 and state['pressure']>.006:
            draw('contact_faults',base@tr(x,.45+math.sin(j)*.35,-3.-force*strike*2.),
                 gain=force*state['pressure']*.7)
    # Locking crossbars retract/peel off only once instead of scanning across
    # the word. Their centre remains open for the readable FREE letterform.
    lock_open=state['opening']
    draw('cage_locks',base@tr(0,-.4*lock_open,-4.*lock_open)@
         np.diag([1.+.15*lock_open,1.+.36*lock_open,1.,1.]),
         gain=.82*(1.-lock_open*.82))
    if state['pressure']>.006:
        age=max(0.,t-FREE_HIT)
        draw('pressure_rim',base@tr(1.8,.65,-3.-age*8.)@
             sc(1.5+age*40.),gain=state['pressure']*.75)
    if state['shards']>.001:
        age=state['shard_age']
        # Bolts leave known hinge/lock contacts; there are no arbitrary stars.
        for j in range(12):
            side=-1 if j%2 else 1
            source=np.array([side*(4.8+(j//4)*2.4),(-1 if j%4<2 else 1)*2.9,-3.])
            speed=np.array([side*(5.+j*.19),(-1 if j%4<2 else 1)*(3.+j*.13),-13.-j*.7])
            p=source+speed*age+np.array([0,-7.*age*age,0])
            draw('released_bolt',base@tr(*p)@rot(age*(12+j),j%3),
                 gain=.75*state['shards'])
        for j in range(32):
            a=j*2.399963;force=.65+(j%5)*.12
            source=np.array([1.8+5.*math.cos(a),.65+2.6*math.sin(a),-3.])
            speed=np.array([math.cos(a)*(9.+j%4),math.sin(a)*8.,-14.-j%7])
            p=source+speed*age+np.array([0,-9.*age*age,0])
            draw('metal_chip',base@tr(*p)@rot(age*(15+j)*force,j%3),
                 gain=.58*state['shards'])
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True
