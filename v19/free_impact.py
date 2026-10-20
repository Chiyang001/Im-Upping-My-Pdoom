"""Seven measured blows destroy a physical wire cage, without drawing a hand.

Six escalating contacts store permanent bends in the steel. The final kick
at 57.745 s breaks every bar, lock and surrounding frame into source-matched
mechanical fragments. A single dynamic GPU batch preserves those fragments'
geometry and depth, including their rotating XYZ ballistic motion.
"""
import math as _math

FREE_START = 56.20
FREE_END = 58.43
FREE_HIT = 57.745
FREE_REBOUND = 57.970
# All seven times are measured kick attacks in code3d/rhythm_v3.json.
# The moving contact patch implies the unseen attacker's repeated blows.
FREE_STRIKES = (
    (56.380, .50, -3.8, .9),
    (56.615, .62,  3.4, -.7),
    (56.840, .72, -1.9, 1.1),
    (57.070, .83,  2.6, -.5),
    (57.295, .94, -.7, .7),
    (57.525, 1.05, 1.8, .65),
    (57.745, 1.48, 1.8, .65),
)
BAR_X = tuple(-14.4 + 1.2*j for j in range(25))
_FIELD = None


def _ease(x):
    x = max(0., min(1., x))
    return x*x*(3.-2.*x)


def _impulse(t, onset, attack=.012, decay=.063):
    dt = t-onset
    if dt < 0.:
        return 0.
    return _ease(dt/attack)*_math.exp(-max(0., dt-attack)/decay)


def sample_free_impact(t):
    """Finite repeated recoil, progressive damage, and one total fracture.

    Legacy scalar keys remain usable by the camera/post director. New fields
    distinguish accumulated damage from the final break; post flashes and
    lens recoil are now triggered on every measured strike.
    """
    if not FREE_START <= t < FREE_END:
        return dict(active=False, exposure=0., strike=0., rebound=0., ring=0.,
                    opening=0., preload=0., shards=0., pressure=0.,
                    camera_local=(0.,0.,0.), target_local=(0.,0.,0.),
                    roll=0., contact=(1.8,.65,-3.), damage=0., final_strike=0.,
                    breakage=0., intact_gain=0., strike_index=-1,
                    contact_age=0., contact_strength=0.)
    pulses = [_impulse(t,onset,.011,.064)*strength
              for onset,strength,_,_ in FREE_STRIKES]
    strike = min(1.5,sum(pulses))
    final = pulses[-1]
    index = max((j for j,s in enumerate(FREE_STRIKES) if t>=s[0]),default=-1)
    current=FREE_STRIKES[max(index,0)]
    damage=sum(strength*_ease((t-onset-.006)/.09)
               for onset,strength,_,_ in FREE_STRIKES[:-1])/4.66
    ring=sum(strength*_math.exp(-(t-onset)/.095)*
             _math.sin(max(0.,t-onset)*_math.tau*14.)
             for onset,strength,_,_ in FREE_STRIKES if t>=onset)
    rebound=_impulse(t,FREE_REBOUND,.012,.071)
    breakage=_ease((t-FREE_HIT)/.046)
    advance=_ease((t-FREE_HIT-.035)/.48)
    pressure=min(1.3,sum(_impulse(t,s[0],.009,.047)*s[1]
                         for s in FREE_STRIKES))
    # A true translational kick retreats from each contact, returns, and then
    # flies through the all-over fracture. Small roll complements translation.
    side=sum(p*(-1 if j%2==0 else 1) for j,p in enumerate(pulses))
    camera=(1.15*advance+.13*side,
            -.72*advance+.08*ring+.12*rebound,
            .48*strike-5.2*advance)
    return dict(active=True,exposure=min(1.,(t-FREE_START)/.065,
                                        (FREE_END-t)/.065),
                strike=strike,rebound=rebound,ring=ring,opening=advance,
                preload=min(1.,damage),shards=breakage,
                shard_age=max(0.,t-FREE_HIT),pressure=pressure,
                camera_local=camera,
                target_local=(1.8*advance,-.35*advance,-10.3*advance),
                roll=.028*side+.012*ring,
                contact=(current[2],current[3],-3.),damage=damage,
                final_strike=final,breakage=breakage,
                intact_gain=1.-breakage,strike_index=index,
                contact_age=max(0.,t-current[0]),
                contact_strength=current[1] if index>=0 else 0.)


def _deform(points,t,np):
    """Permanent dents plus fast compression/rebound on each actual blow."""
    p=np.array(points,dtype=float,copy=True)
    front=np.exp(-((p[:,2]+3.)/6.0)**2)
    # Frame corners move too: the impact is transmitted through the complete
    # structure, not a single detachable centre panel.
    edge=.30+.70*np.maximum(0.,1.-(np.abs(p[:,0])/19.)**1.3)
    z=np.zeros(len(p));shear=np.zeros(len(p));vertical=np.zeros(len(p))
    for j,(onset,power,x,y) in enumerate(FREE_STRIKES[:-1]):
        if t<onset:continue
        age=t-onset
        footprint=np.exp(-((p[:,0]-x)/9.8)**2-((p[:,1]-y)/9.0)**2)
        impulse=_impulse(t,onset,.011,.064)
        plastic=_ease((age-.005)/.09)
        vibrate=_math.sin(age*_math.tau*14.)*_math.exp(-age/.095)
        z-=power*front*edge*(.31*plastic+3.80*impulse*footprint+.22*vibrate)
        shear+=power*footprint*(.12*plastic+.47*impulse)*(1 if j%2 else -1)
        vertical+=power*footprint*.13*vibrate
    p[:,2]+=z;p[:,0]+=shear;p[:,1]+=vertical
    return p


def build_free_impact(Mesh,np,math,C,WHITE,ACC):
    """Build machined cage and fracture cells, with no triangle surfaces.

    Long rod outlines are cut into <=1.35-unit segments before being grouped
    into small physical cells. Therefore the complete 32-unit frame cannot
    accidentally survive as one intact giant piece after the final blow.
    """
    global _FIELD
    result={}
    cage=Mesh()
    def line(m,p,c=C,closed=False):m.line(p,c,closed)
    def ring(m,p,r,c=C,axis=2,n=16):m.circle(r,p,axis,c,n)
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
    def sleeve(m,p):
        for k in [-.19,0.,.19]:
            ring(m,[p[0],p[1]+k,p[2]],.23,WHITE*.60,1,12)
        for a in np.linspace(0,math.tau,6,endpoint=False):
            line(m,[[p[0]+.23*math.cos(a),p[1]-.22,p[2]+.23*math.sin(a)],
                    [p[0]+.23*math.cos(a),p[1]+.22,p[2]+.23*math.sin(a)]],C*.55)
    for side in [-1,1]:
        for z in [-3.,-10.,-18.]:
            rod(cage,[side*15.8,-8.4,z],[side*15.8,8.4,z],.22,C*.58)
            for y in [-8.4,8.4]:
                rod(cage,[side*14.7,y,z],[side*16.8,y,z],.13,WHITE*.45)
                if z>-18:
                    rod(cage,[side*15.8,y,z],[side*15.8,y,z-7],.14,C*.43)
        for y in [-8.4,8.4]:
            rod(cage,[side*15.8,y,-3],[side*15.8,-y,-10],.075,C*.29)
        for z in [-3,-10,-18]:
            for y in [-6.5,0,6.5]:
                ring(cage,[side*15.8,y,z+.23],.19,WHITE*.5,n=12)
    for y in [-8.15,8.15]:
        for z in [-3.25,-3.,-2.75]:
            rod(cage,[-15.8,y,z],[15.8,y,z],.12,C*.63)
        for x in BAR_X:
            for off in [-.25,.25]:
                ring(cage,[x,y+off,-2.74],.12,WHITE*.55,n=12)
            line(cage,[[x-.32,y-.34,-3],[x+.32,y-.34,-3],
                       [x+.32,y+.34,-3],[x-.32,y+.34,-3]],C*.46,True)
    for x in BAR_X:
        rod(cage,[x,-8.15,-3],[x,8.15,-3],.095,C*.78)
        for y in [-7.9,-4.9,-1.1,0.,1.1,4.9,7.9]:
            sleeve(cage,[x,y,-3.])
        # Three short longitudinal scores add the identity of bent steel.
        for off in [-.045,0,.045]:
            line(cage,[[x+.105,-7.,-3+off],[x+.14,0.,-2.97+off],
                       [x+.105,7.,-3+off]],WHITE*.24)
    for side in [-1,1]:
        for y in [-2.9,2.9]:
            rod(cage,[side*15.8,y,-3.1],[side*4.8,y,-3.1],.13,C*.7)
            for x in [side*5.,side*8.,side*11.5,side*15.]:
                ring(cage,[x,y,-2.9],.23,WHITE*.6,n=18)
                # Small hexagonal lock heads share their bearing's fracture.
                ring(cage,[x,y,-2.75],.105,WHITE*.74,n=7)
                rod(cage,[x,y,-2.7],[x,y,-3.28],.055,C*.54)
    # Split every long line, then bind nearby vertices into a real spatial
    # fragment. Cells preserve rings and tube sides; none are arbitrary dots.
    cells={}
    for aa,bb in np.asarray(cage.l,float).reshape(-1,2,6):
        count=max(1,int(math.ceil(np.linalg.norm(bb[:3]-aa[:3])/1.35)))
        for j in range(count):
            a=aa+(bb-aa)*(j/count);b=aa+(bb-aa)*((j+1)/count)
            mid=(a[:3]+b[:3])*.5
            key=tuple(np.floor((mid+[.13,.07,.19])/[1.8,1.55,2.0]).astype(int))
            cells.setdefault(key,[]).extend([a,b])
    field=Mesh();centres=[];chunk_ids=[];sizes=[]
    for idx,(key,verts) in enumerate(sorted(cells.items())):
        a=np.asarray(verts);center=(a[:,:3].min(0)+a[:,:3].max(0))*.5
        field.l.extend(a.tolist());centres.extend([center]*len(a))
        chunk_ids.extend([idx]*len(a));sizes.append(a[:,:3].max(0)-a[:,:3].min(0))
    source=np.asarray(field.l,float);centre=np.asarray(centres)
    ids=np.asarray(chunk_ids,float)
    # Fixed deterministic per-cell velocity/axis; adjacent line endpoints
    # rotate together so the debris retains its physical mechanical shape.
    angle=ids*2.399963;dx=centre[:,0]-1.8;dy=centre[:,1]-.65
    norm=np.maximum(1.,np.sqrt(dx*dx+dy*dy))
    near=np.exp(-((centre[:,2]+3)/7.)**2)
    velocity=np.column_stack((dx/norm*(12.+5.*np.sin(angle)**2),
                              dy/norm*(10.+5.*np.cos(angle)**2)+3.,
                              8.+15.*near+5.*np.sin(angle*1.7)))
    # Wire pieces in the background diverge in depth as well as sideways.
    velocity[:,2]-=(1.-near)*18.
    axis=np.column_stack((np.sin(angle*.77),np.cos(angle*1.13),
                          np.sin(angle*.51)+.2))
    axis/=np.maximum(1.e-9,np.linalg.norm(axis,axis=1))[:,None]
    speed=8.+12.*np.mod(ids*.6180339,1.)
    _FIELD=dict(source=source,centres=centre,ids=ids,velocity=velocity,
                axis=axis,speed=speed,chunk_count=len(cells),
                max_chunk_span=float(np.max(sizes)),
                break_source=_deform(source[:,:3],FREE_HIT-1.e-5,np),
                break_centres=_deform(centre,FREE_HIT-1.e-5,np),
                phase=np.repeat(np.arange(len(source)//2)/max(1,len(source)//2-1),2),
                seed=np.repeat(np.mod(np.arange(len(source)//2)*.6180339,1),2))
    result['cage_field']=field
    contact=Mesh()
    for j in range(9):
        a=j*2.399963;rr=.32+j*.14
        p=np.array([rr*math.cos(a),rr*.65*math.sin(a),0.])
        line(contact,[p,p+[.17*math.cos(a+.7),.12*math.sin(a+.7),-.1],
                      p+[.38*math.cos(a),.28*math.sin(a),-.32]],
             WHITE*.8 if j%4 else ACC*.25)
    result['contact_faults']=contact
    pressure=Mesh()
    for a in [.2,1.8,3.6,5.0]:
        line(pressure,[[math.cos(q),.72*math.sin(q),.11*math.sin(q*3)]
                       for q in np.linspace(a,a+.43,18)],WHITE*.66)
    result['pressure_rim']=pressure
    return result


def _field_vertices(t,np):
    """Return posed source vertices; before impact, every cell is connected."""
    f=_FIELD
    if f is None:raise RuntimeError('build_free_impact must precede posing')
    if t<FREE_HIT:
        return _deform(f['source'][:,:3],t,np)
    # A sub-frame fracture wave breaks the farthest steel within 26 ms.
    c=f['break_centres'];p=f['break_source']
    delay=np.minimum(.026,np.linalg.norm((c-[1.8,.65,-3.])*[.7,.8,.45],axis=1)*.0013)
    age=np.maximum(0.,t-FREE_HIT-delay)
    angle=f['speed']*age
    local=p-c;axis=f['axis'];co=np.cos(angle)[:,None];si=np.sin(angle)[:,None]
    spin=local*co+np.cross(axis,local)*si+axis*np.sum(axis*local,axis=1)[:,None]*(1.-co)
    # Accelerated transfer over the first 45 ms avoids a frame of teleporting
    # debris. The final opening is made by physical fragments leaving it.
    fly=np.maximum(0.,age-.016*(1.-np.exp(-age/.016)))
    posed=c+spin+f['velocity']*fly[:,None]
    posed[:,1]-=10.5*age*age
    return posed


def draw_free_impact(t,vp,hit,g):
    """One uploaded line batch for every intact/fractured cage component."""
    state=sample_free_impact(t)
    if not state['active']:return
    np,math=g['np'],g['math'];tr,sc=g['tr'],g['sc']
    ctx,gl=g['ctx'],g['gl'];field=g['FREE_IMPACT']['cage_field']
    base=g['semantic_host']('free-wall',57.9,t,18.,1.2)
    posed=_field_vertices(t,np);f=_FIELD
    data=np.column_stack((posed,f['source'][:,3:],f['phase'],f['seed'])).astype('f4')
    field.buf.write(data.tobytes())
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
    g['ms'].depth_mask=False;ctx.line_width=1.35
    # No intact fallback is ever drawn after the final blow: the same entire
    # mesh becomes individually rotating steel pieces in this one GPU draw.
    gain=state['exposure']*(.80+.14*min(1.,state['strike']))
    if t>=FREE_HIT:gain*=1.-.34*_ease((t-FREE_HIT-.36)/.33)
    field.draw(base,vp,t,0,0,-1,gain=gain)
    for onset,power,x,y in FREE_STRIKES:
        age=t-onset;pulse=_impulse(t,onset,.009,.060)*power
        if pulse<.012:continue
        if age<.14:
            g['FREE_IMPACT']['contact_faults'].draw(
                base@tr(x,y,-3.-min(2.5,age*20)),vp,t,0,0,-1,
                gain=state['exposure']*pulse*.72)
        # The pressure ring is born exactly at the successive bar contacts,
        # staying in that wall's coordinates rather than following the lens.
        g['FREE_IMPACT']['pressure_rim'].draw(
            base@tr(x,y,-3.-age*6)@sc(1.1+age*(43 if onset==FREE_HIT else 29)),
            vp,t,0,0,-1,gain=state['exposure']*pulse*.65)
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True
