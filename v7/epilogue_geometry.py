"""Distinct line-built actors for the instrumental epilogue.

``build_epilogue`` returns ordinary Mesh objects.  The coordinate origin is
the dramatic focus, +z faces the lens.  All objects are deterministic and all
segments are unfilled.  The network is emitted in seven complete route
batches, so reveal values n/7 produce a visible seven-stage propagation.

Suggested roles: network propagates; world is the acquired planet; clamps
compress it; shell bursts out; recursive partitions overtake the debris;
spine carries the final signal laterally into the creator's last frame.
These objects intentionally have different silhouettes and principal axes.
"""


def build_epilogue(Mesh, np, math, C, WHITE, ACC):
    rng = np.random.default_rng(145703)
    C, WHITE, ACC = (np.asarray(v, dtype=float) for v in (C, WHITE, ACC))
    parts = {name: Mesh() for name in
             ('network', 'world', 'clamps', 'shell', 'recursive', 'spine')}
    tau = math.tau

    def unit(v):
        v = np.asarray(v, dtype=float)
        return v / max(float(np.linalg.norm(v)), 1.e-9)

    def basis(v):
        v = unit(v)
        u = unit(np.cross(v, [0,0,1] if abs(v[2]) < .85 else [0,1,0]))
        return u, unit(np.cross(v,u))

    def mix(a,b,t):return a*(1-t)+b*t

    def octa(m,p,r,color):
        p=np.asarray(p)
        top=p+[0,r,0]; bot=p-[0,r,0]
        ring=[p+q for q in ([r,0,0],[0,0,r],[-r,0,0],[0,0,-r])]
        m.line(ring,color,closed=True)
        for q in ring:m.line([top,q,bot],color)

    def beam(m,a,b,width,color,rungs=6):
        a,b=np.asarray(a),np.asarray(b)
        u,v=basis(b-a)
        corners=[u*width+v*width,-u*width+v*width,
                 -u*width-v*width,u*width-v*width]
        for p in (a,b):m.line([p+d for d in corners],color,closed=True)
        for d in corners:m.line([a+d,b+d],color)
        for k in range(rungs):
            t=k/rungs; tt=(k+1)/rungs
            for side in range(2):
                lo=corners[side];hi=corners[side+1]
                m.line([a*(1-t)+b*t+lo,a*(1-tt)+b*tt+hi],color*.72)
                m.line([a*(1-t)+b*t+hi,a*(1-tt)+b*tt+lo],color*.4)

    # Seven independent, irregular vascular highways.  Each has a backbone,
    # service lines, branching relays, and arrow-like broken signal packets.
    m=parts['network']
    for route in range(7):
        pts=[]
        for k in range(83):
            f=k/82; x=-17+34*f
            y=(route-3)*1.65+1.1*math.sin(f*tau+route*.9)+.36*math.sin(f*19+route)
            z=-1.5+2.8*math.sin(f*4.5+route*.72)+.4*math.sin(f*13)
            pts.append(np.array([x,y,z]))
        color=mix(C,WHITE,.12+route*.085)
        for offset in (-.13,0,.13):
            m.line([p+[0,offset,offset*.6] for p in pts],color*(1 if offset==0 else .5))
        for k in range(4,80,4):
            p=pts[k];q=pts[k+1];d=unit(q-p)
            u,v=basis(d)
            octa(m,p,.13+(.07 if k%12==0 else 0),WHITE if k%12==0 else C)
            if k%8==0:
                # Relay branches deliberately depart above and below the lane.
                side=1 if (k//8+route)%2 else -1
                branch=[p,p+[.22,side*.35,.2],p+[.75,side*.75,.6],
                        p+[1.2,side*(1.25+.1*route),1.05]]
                m.line(branch,ACC*.75)
                octa(m,branch[-1],.17,ACC)
                for j in range(3):
                    end=branch[-1]+np.array([.35+j*.15,side*(.3+j*.17),-.2+j*.2])
                    m.line([branch[-1],end],C*.65)
            # Direction is communicated geometrically, not by flashing dots.
            if k%12==0:
                for shift in (0,.2,.4):
                    c=p+d*shift
                    m.line([c-d*.18+u*.16,c,c-d*.18-u*.16],ACC)
        # A route-specific terminal gate with a different slant on each lane.
        p=pts[-1];u,v=basis(pts[-1]-pts[-2])
        for size in (.33,.55):
            m.line([p+u*size+v*size,p-u*size+v*size,
                    p-u*size-v*size,p+u*size-v*size],WHITE,closed=True)
        # Append regular branch structures last within each route batch.
        for k in range(7,79,6):
            a,b=pts[k],pts[min(k+3,82)]
            m.line([a,b+[0,.25,.28]],C*.5)

    # The world is a shell of broken faceted geographic plates.  Every plate
    # has its own separated boundary; there is no unbroken latitude circle.
    m=parts['world']
    radius=6.4
    def globe(lat,lon,r=radius):
        return np.array([r*math.cos(lat)*math.cos(lon),r*math.sin(lat),r*math.cos(lat)*math.sin(lon)])
    for row in range(13):
        lat0=-1.48+row*2.96/13
        lat1=-1.48+(row+1)*2.96/13
        shift=.32*math.sin(row*1.7)
        for col in range(30):
            lon0=(col+shift)*tau/30;lon1=(col+1+shift)*tau/30
            # A small gap and torn outer edge break the perfect grid.
            lo=lat0+.012;hi=lat1-.012
            left=lon0+.008;right=lon1-.008
            p=[globe(lo,left),globe(lo,right),globe(hi,right),globe(hi,left)]
            center=sum(p)/4;n=unit(center)
            fracture=(row*17+col*7)%19
            # Incomplete/raised plates form an identifiable rupture meridian.
            lift=.3 if fracture<3 else 0
            p=[q+n*lift for q in p]
            color=mix(C,WHITE,.2 if fracture>4 else .65)
            if fracture!=0:m.line(p,color,closed=True)
            if (col+row)%2:m.line([p[0],p[2]],color*.55)
            else:m.line([p[1],p[3]],color*.55)
            if fracture<7:
                inner=[q-n*.17 for q in p]
                m.line(inner,C*.38,closed=True)
                for q,r in zip(p,inner):m.line([q,r],WHITE*.5)
            if fracture<3:
                q=center+n*(.5+row*.012)
                m.line([p[0],q,p[2]],ACC*.8)
                octa(m,q,.08,ACC)
    # A few coherent irregular continental ridges; none close into a ring.
    for branch in range(21):
        lat=rng.uniform(-1.2,1.2);lon=rng.uniform(0,tau)
        path=[]
        for k in range(14):
            path.append(globe(lat+math.sin(k*.7+branch)*.028+k*.006,
                              lon+k*.018+math.sin(k*.9)*.011,radius+.06))
        m.line(path,WHITE*.8)

    # Open opposing mechanical hands.  Palms sit out wide and finger chains
    # curl towards the world but leave a central opening.  Layered struts and
    # offset pads make them read as joints rather than disconnected chevrons.
    m=parts['clamps']
    for side in (-1,1):
        root=np.array([side*17.,-.8,-3.8])
        wrist=np.array([side*10.6,.2,-1.3])
        palm=np.array([side*8.3,.5,.2])
        beam(m,root,wrist,.52,C,12)
        beam(m,wrist,palm,.65,WHITE*.7,8)
        # Telescoping piston on each outside edge.
        for yy in (-.65,.65):
            beam(m,root+[0,yy,.35],wrist+[0,yy,.35],.13,ACC*.65,5)
        for j in range(4):
            y=(j-1.5)*1.85+.5
            z=(j%2-.5)*1.2+.3
            p0=np.array([side*8.7,y,z])
            p1=np.array([side*(7.1-.12*j),y*1.10,z+1.3])
            p2=np.array([side*(5.95-.08*j),y*.83,z+2.35])
            p3=np.array([side*(5.15+.08*j),y*.64,z+1.7])
            beam(m,palm,p0,.31,C,3)
            for k,(a,b) in enumerate(zip((p0,p1,p2),(p1,p2,p3))):
                beam(m,a,b,.23-k*.045,WHITE*.75,4)
                # Axis pins: faceted not smooth donut bearings.
                u,v=basis(b-a)
                for depth in (-.25,.25):
                    octa(m,a+unit(b-a)*depth,.34-k*.04,ACC*.85)
                center=(a+b)/2
                for tick in range(4):
                    f=(tick+1)/5
                    q=a*(1-f)+b*f
                    m.line([q+u*.28-v*.13,q+u*.28+v*.13],C*.9)
            # A visibly serrated contact pad faces the unclosed central gap.
            for tooth in range(7):
                yy=p3[1]+(tooth-3)*.105
                m.line([[p3[0],yy,p3[2]],[p3[0]-side*.35,yy+.04,p3[2]-.12],
                        [p3[0],yy+.08,p3[2]-.18]],ACC)

    # World crust after the rupture: large separate triangular frame plates
    # and retained scaffolding.  Seed-based motion can eject these as shards.
    m=parts['shell']
    for i in range(122):
        lat=math.asin(rng.uniform(-.9,.9));lon=i*2.399963229728653
        n=unit(globe(lat,lon,1));u,v=basis(n)
        center=n*rng.uniform(6.4,9.4)
        size=rng.uniform(.55,1.45)
        p=[center+u*size*math.cos(a)+v*size*math.sin(a)
           for a in (0,2.05,4.33)]
        back=[q-n*.28 for q in p]
        m.line(p,WHITE*.8,closed=True);m.line(back,C*.55,closed=True)
        for a,b in zip(p,back):m.line([a,b],ACC*.75)
        c=sum(p)/3
        for a in p:m.line([a,c-n*.35],C*.7)
        for j in range(1,7):
            f=j/7
            m.line([p[0]*(1-f)+p[1]*f,p[0]*(1-f)+p[2]*f],C*.4)
        # A detached claw of support steel trails behind each large piece.
        m.line([c-n*.35,c-n*.9+u*.18,c-n*1.5+u*.35],ACC*.7)
        m.line([c-n*.35,c-n*1.25-v*.25],WHITE*.65)

    # A sheared, branching array of recursive machine rooms.  Mixed polygons
    # and off-axis centers avoid the repeated central rectangular tunnel.
    m=parts['recursive']
    for bank in range(5):
        base=np.array([(bank-2)*5.3,math.sin(bank*1.9)*2.1,(bank%2)*-3.5])
        for level in range(7):
            s=2.7*(.76**level)
            center=base+np.array([level*.28*(-1 if bank%2 else 1),
                                  level*.23*math.sin(bank+1),-level*.83])
            angle=.12*bank+.055*level
            n=3 if (bank+level)%3==0 else 4
            pts=[]
            for j in range(n):
                a=angle+tau*j/n+(math.pi/4 if n==4 else math.pi/2)
                pts.append(center+[math.cos(a)*s*1.32,math.sin(a)*s,0])
            rear=[q+[.13,-.12,-.38] for q in pts]
            m.line(pts,WHITE*.8,closed=True);m.line(rear,C*.6,closed=True)
            for a,b in zip(pts,rear):m.line([a,b],C*.8)
            for a,b in zip(pts,pts[1:]+pts[:1]):
                for k in range(1,7):
                    f=k/7; q=a*(1-f)+b*f
                    out=unit(q-center)
                    m.line([q,q+out*.16,q+out*.16+[0,0,-.35]],ACC*.7)
            # Hard-wired sub-room link carries the recursive operation onward.
            if level:
                prev=base+np.array([(level-1)*.28*(-1 if bank%2 else 1),
                                    (level-1)*.23*math.sin(bank+1),-(level-1)*.83])
                m.line([prev+[0,s,0],center+[.28,s,0],center+[.28,0,0]],ACC)
        # A transverse backbone visibly connects the five separate bays.
        if bank:
            prior=np.array([(bank-3)*5.3,math.sin((bank-1)*1.9)*2.1,((bank-1)%2)*-3.5])
            beam(m,prior+[0,-3,-1],base+[0,-3,-1],.12,C*.75,8)

    # Wide neural spine: a horizontal creature/machine with asymmetric ribs,
    # signal buses and angular vertebrae.  This final object moves across the
    # screen and cannot be mistaken for a ring or a floating centered icon.
    m=parts['spine']
    centers=[]
    for i in range(69):
        x=-20+i*40/68
        centers.append(np.array([x,.8*math.sin(x*.21),1.1*math.sin(x*.16+.7)]))
    for offset in (-.28,0,.28):
        m.line([q+[0,offset,offset*.4] for q in centers],WHITE if offset==0 else C*.6)
    for i,p in enumerate(centers):
        if i%2:continue
        octa(m,p,.32,ACC if i%8==0 else WHITE*.7)
        for side in (-1,1):
            span=2.2+1.7*math.sin(i*.16+.3)**2
            rib=[]
            for k in range(15):
                t=k/14
                rib.append(p+[math.sin(t*math.pi)*(.75+side*.22),
                              side*span*t,math.sin(t*math.pi)*1.4-t*.6])
            m.line(rib,C*.85)
            m.line([q+[.12,0,.12] for q in rib],C*.38)
            for k in range(2,14,2):m.line([rib[k],rib[k]+[.12,0,.12]],WHITE*.6)
            end=rib[-1]
            octa(m,end,.15,ACC*.85)
            for branch in (-1,1):
                m.line([end,end+[.6*branch,side*.3,.2],end+[1.*branch,side*.45,-.1]],WHITE*.65)
        if i+2<len(centers):
            beam(m,p+[0,-.6,-.45],centers[i+2]+[0,-.6,-.45],.1,C*.5,2)
    # Six long partly broken signal buses follow the full width of the spine.
    for lane in range(6):
        yy=(lane-2.5)*.42
        for k in range(0,64,4):
            pts=[q+[0,yy,-1.1] for q in centers[k:k+4]]
            m.line(pts,ACC*.65 if lane==2 else C*.6)
    return parts
