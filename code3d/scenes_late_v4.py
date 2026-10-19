"""Detailed, independent line constructions for P(doom), shots 17--33.

Only vector geometry is returned.  There are no bitmap assets, text planes,
shared floor grids, or generic HUD ornaments.  All coordinates are world space.
"""


def build_late(idx, Mesh, np, math, C, WHITE, ACCENT):
    m = Mesh()
    C = np.asarray(C, dtype=float)
    WHITE = np.asarray(WHITE, dtype=float)
    ACCENT = np.asarray(ACCENT, dtype=float)
    tau = math.tau
    rng = np.random.default_rng(4300 + idx * 119)
    faint = C * .19
    dark = C * .32
    steel = WHITE * .48

    def line(p, col=steel, close=False):
        m.line(p, col, closed=close)

    def ring(center, r, axis=2, col=steel, n=80):
        m.circle(r, tuple(center), axis, col, n)

    def box(center, size, col=steel):
        m.box(tuple(center), tuple(size), col)

    def unit(a):
        a = np.asarray(a, dtype=float)
        return a / max(float(np.linalg.norm(a)), 1e-9)

    def wire(points, radius=.10, strands=8, col=steel, rib_every=0):
        """A swept, open wire bundle with longitudinal and transverse detail."""
        pts = np.asarray(points, dtype=float)
        tangent = np.gradient(pts, axis=0)
        tangent /= np.maximum(np.linalg.norm(tangent, axis=1)[:, None], 1e-9)
        fixed = np.tile([0., 1., 0.], (len(pts), 1))
        fixed[np.abs(tangent[:, 1]) > .92] = [1., 0., 0.]
        u = np.cross(tangent, fixed)
        u /= np.maximum(np.linalg.norm(u, axis=1)[:, None], 1e-9)
        v = np.cross(tangent, u)
        rails = []
        for j in range(strands):
            a = j * tau / strands
            p = pts + radius * (math.cos(a) * u + math.sin(a) * v)
            line(p, col * (.52 + .48 * (j % 4 == 0)))
            rails.append(p)
        if rib_every:
            for k in range(0, len(pts), rib_every):
                line([p[k] for p in rails], col * .55, True)

    def frame(z, w, h, col=steel, x=0., y=0., chamfer=0.):
        if chamfer:
            q = chamfer
            line([[x-w/2+q,y-h/2,z],[x+w/2-q,y-h/2,z],
                  [x+w/2,y-h/2+q,z],[x+w/2,y+h/2-q,z],
                  [x+w/2-q,y+h/2,z],[x-w/2+q,y+h/2,z],
                  [x-w/2,y+h/2-q,z],[x-w/2,y-h/2+q,z]], col, True)
        else:
            line([[x-w/2,y-h/2,z],[x+w/2,y-h/2,z],
                  [x+w/2,y+h/2,z],[x-w/2,y+h/2,z]], col, True)

    def beam(a, b, width=.10, col=steel, segments=16):
        p = np.linspace(a, b, segments)
        wire(p, width, 6, col, 4)

    def clip(center, scale=1., angle=0., depth=.1, col=steel, strands=5):
        p = []
        for a in np.linspace(0, math.pi, 25):
            p.append([.50*math.cos(a),1.15+.50*math.sin(a),0])
        p.append([-.50,-1.15,0])
        for a in np.linspace(math.pi, tau, 25):
            p.append([.50*math.cos(a),-1.15+.50*math.sin(a),0])
        p.append([.50,.72,0])
        for a in np.linspace(0, math.pi, 25):
            p.append([.26*math.cos(a),.72+.26*math.sin(a),0])
        p.append([-.26,-.86,0])
        p = np.asarray(p) * scale
        xx = p[:,0].copy()
        p[:,0] = xx*math.cos(angle)-p[:,1]*math.sin(angle)
        p[:,1] = xx*math.sin(angle)+p[:,1]*math.cos(angle)
        p[:,2] = np.sin(np.linspace(0, math.pi, len(p))) * depth
        p += np.asarray(center)
        wire(p, .026*scale, strands, col, 11)

    def subdiv_box(center, size, steps=8, col=dark):
        x,y,z = center
        w,h,d = size
        box(center,size,col*1.6)
        for a in np.linspace(-.5,.5,steps):
            for zz in [-d/2,d/2]:
                line([[x+a*w,y-h/2,z+zz],[x+a*w,y+h/2,z+zz]],col)
                line([[x-w/2,y+a*h,z+zz],[x+w/2,y+a*h,z+zz]],col)
            for xx in [-w/2,w/2]:
                line([[x+xx,y-h/2,z+a*d],[x+xx,y+h/2,z+a*d]],col)
                line([[x+xx,y+a*h,z-d/2],[x+xx,y+a*h,z+d/2]],col)

    if idx == 17:
        # A fragile lenticular safety shell, surrounding an empty observation bay.
        for j, a in enumerate(np.linspace(0,tau,140,endpoint=False)):
            pts=[]
            for t in np.linspace(0,math.pi,105):
                x=11.6*math.sin(t)*math.cos(a)
                y=6.0*math.sin(t)*math.sin(a)
                z=-4.0+4.6*math.cos(t)
                # Slits and clipped seams betray the shell's structural weakness.
                q=.16*math.sin(t*11+a*7)
                pts.append([x,y,z+q])
            line(pts, C*(.23 if j%5 else .68))
        for t in np.linspace(.17,math.pi-.17,30):
            line([[11.6*math.sin(t)*math.cos(a),6*math.sin(t)*math.sin(a),
                   -4+4.6*math.cos(t)] for a in np.linspace(0,tau,140)],steel*.65)
        # Corner rivet seams and fractured inspection ribs, no floating labels.
        for side in [-1,1]:
            for j in range(15):
                x=side*(8.0+.17*j); z=-7+.45*j
                beam([x,-4.4,z],[x,4.4,z],.028,C*.38,22)
                for y in np.linspace(-4,4,13):
                    box([x,y,z],[.11,.08,.07],WHITE*.65)
        for j in range(40):
            x,y=rng.uniform([-9,-5],[9,5]); z=-3.5-rng.random()*3
            p=np.asarray([x,y,z])
            line([p,p+[.4,.25,.05],p+[.6,-.10,.1],p+[1.0,.30,.18]],ACCENT*.65)

    elif idx == 18:
        # A vertically folded forward/backward machine, with open space at its heart.
        layers=[-11,-7,-3,1,5]
        nodes=[]
        for k,z in enumerate(layers):
            row=[]
            for j in range(9):
                x=(j-4)*2.9; y=4.7 if k%2==0 else -4.7
                p=np.array([x,y,z]); row.append(p)
                for rr in [.15,.21,.34,.40]:
                    ring(p,rr,2,C if rr==.34 else dark,48)
                for off in [-.11,.11]:
                    ring(p+[0,0,off],.40,2,steel,40)
                box(p,[.92,.92,.32],steel*.75)
            nodes.append(row)
        for k in range(4):
            for j,a in enumerate(nodes[k]):
                for q in range(9):
                    b=nodes[k+1][q]
                    bend=(a+b)/2+np.array([0,0,.3*math.sin(j+q)])
                    pts=[(1-t)**2*a+2*(1-t)*t*bend+t*t*b for t in np.linspace(0,1,28)]
                    line(pts,C*(.16 if (j+q)%3 else .44))
        for side in [-1,1]:
            p=[]
            for t in np.linspace(0,tau,260):
                p.append([side*(12+.5*math.cos(t)),5.8*math.sin(t),-3+8.2*math.cos(t)])
            wire(p,.16,14,ACCENT*.65,8)

    elif idx == 19:
        # An obsolete computer hall: tilted card cages and a broken central bus.
        for side in [-1,1]:
            for k in range(7):
                z=5-k*2.5; x=side*(8.2+.16*k)
                subdiv_box([x,-.4,z],[5.0,10.4,1.8],12,dark)
                for slot in range(18):
                    y=-5.1+slot*.56
                    box([x,y,z+.95],[4.5,.34,.25],steel*.65)
                    for v in range(7):
                        line([[x-1.9+v*.6,y-.09,z+1.1],
                              [x-1.9+v*.6,y+.09,z+1.1]],C*.62)
                for q in range(9):
                    # Half-withdrawn logic blades become a cascading cemetery.
                    xx=x-side*(.2+.11*q)
                    line([[xx,-3+q*.6,z+1],[xx-side*3,-2.6+q*.6,z+1.3],
                          [xx-side*3,-2.35+q*.6,z+1.3],[xx,-2.75+q*.6,z+1]],steel*.45,True)
        for j in range(48):
            a=j*tau/48
            p=[]
            for t in np.linspace(0,1,80):
                p.append([4.8*math.cos(a)*(1-t),-5.5+5*t-3*t*t,
                          -10+18*t+math.sin(a*3)*.25])
            line(p,ACCENT*.40 if j%8==0 else faint)
        for j in range(180):
            x,y,z=rng.uniform([-6,-6,-11],[6,-3,7])
            box([x,y,z],rng.uniform(.08,.52,3),steel*.55)

    elif idx == 20:
        # A true L-shaped corridor; the elbow sits to the upper left of the frame.
        route=[]
        route.extend([[0,0,z] for z in np.linspace(8,-5,65)])
        route.extend([[-v,0,-5] for v in np.linspace(0,13,65)[1:]])
        for n,p in enumerate(route):
            p=np.array(p)
            if n<65:
                points=[[p[0]-6,-5.8,p[2]],[p[0]+6,-5.8,p[2]],
                        [p[0]+6,5.8,p[2]],[p[0]-6,5.8,p[2]]]
            else:
                points=[[p[0],-5.8,-11],[p[0],-5.8,1],
                        [p[0],5.8,1],[p[0],5.8,-11]]
            line(points,C*(.7 if n%8==0 else .22),True)
        for a in np.linspace(-5.8,5.8,52):
            for side in [-1,1]:
                line([[side*6,a,z] for z in np.linspace(8,-5,80)],steel*.28)
                line([[x,a,-5+side*6] for x in np.linspace(0,-13,80)],steel*.28)
        for a in np.linspace(-6,6,42):
            for y in [-5.8,5.8]:
                line([[a,y,z] for z in np.linspace(8,-5,60)],dark)
                line([[x,y,-5+a] for x in np.linspace(0,-13,60)],dark)
        for z in np.linspace(-4.8,7.8,26):
            for side in [-1,1]:
                x=side*5.7
                line([[x,-4.8,z],[x,-4.4,z-.3],[x,-4.0,z]],ACCENT*.72)

    elif idx == 21:
        # A suspended bridge whose middle third has no support at all.
        for side in [-1,1]:
            for rail in range(18):
                x=side*(4.6+rail*.06)
                for za,zb in [(8,0),(-4,-12)]:
                    line([[x,1.1+.018*(z+2)**2,z] for z in np.linspace(za,zb,90)],C*.58)
            for z in np.linspace(-12,8,70):
                if -4<z<0:continue
                beam([side*4.6,-4.5,z],[side*4.6,1.1+.018*(z+2)**2,z],.035,steel*.6,12)
                line([[side*4.6,-4.5,z],[side*4.6,-2,z-.5],
                      [side*4.6,-4.5,z-1]],dark)
            for k in range(12):
                x=side*(4.9+k*.13)
                for za,zb in [(8,0),(-4,-12)]:
                    line([[x,-5.2,z] for z in np.linspace(za,zb,65)],faint)
        for z in np.linspace(-12,8,160):
            if -4<z<0:continue
            line([[-4.6,-4.4,z],[4.6,-4.4,z]],steel*.4)
            if int(z*8)%8==0:
                line([[-4.6,-4.4,z],[4.6,-4.4,z-.8]],dark)
        # Snapped tendons stop at the missing bearing, sharply exposing negative space.
        for j in range(54):
            x=-4.5+j*9/53
            p=[]
            for t in np.linspace(0,1,85):
                p.append([x+.12*math.sin(t*4+j),-4.4-1.8*t*t,0-1.0*t])
            line(p,C*.35)
        for x in [-10,-7,7,10]:
            beam([x,-6,-11],[x,6,-11],.16,steel*.5,24)

    elif idx == 22:
        # Tension cat. Contour sections, ribs, whiskers, and an enormous tail rail.
        def catcontour(t,z):
            # Angular ears are integrated into the otherwise soft head sections.
            x=3.2*math.cos(t)
            y=2.65*math.sin(t)+.55
            ear=math.exp(-((t-.85)/.22)**2)+math.exp(-((t-2.30)/.22)**2)
            return [x*(1+.10*ear),y+2.1*ear,z]
        for j,z in enumerate(np.linspace(-6,-1.8,42)):
            line([catcontour(t,z) for t in np.linspace(0,tau,170)],C*(.22 if j%5 else .7),True)
        for a in np.linspace(0,tau,90,endpoint=False):
            line([catcontour(a,z) for z in np.linspace(-6,-1.8,40)],steel*.4)
        for side in [-1,1]:
            for j in range(12):
                p=[]
                for t in np.linspace(0,1,85):
                    p.append([side*(1.8+10*t),-.4+(j-5.5)*.13+(j-5.5)*.13*t,
                              -1.5-4*t*t+.09*math.sin(t*5+j)])
                line(p,WHITE*(.35 if j%3 else .75))
            for j in range(24):
                p=[]
                for t in np.linspace(0,1,90):
                    p.append([side*(2+8*t),3.7+1.8*t-.11*j,-4.0-5*t])
                line(p,faint)
            for z in [-1.7,-1.5]:
                line([[side*(.4+1.65*t),1.25+.45*math.sin(t*math.pi),z]
                      for t in np.linspace(0,1,70)],ACCENT*.85)
        p=[]
        for t in np.linspace(0,1,320):
            a=t*math.pi*2.2
            p.append([6*math.sin(a),-3.8+1.8*math.cos(a),-10+17*t])
        wire(p,.21,16,C*.48,8)

    elif idx == 23:
        # A forward-moving paperclip cathedral; near clips are deliberately enormous.
        for j in range(96):
            z=rng.uniform(-12,7)
            a=rng.uniform(0,tau)
            rr=rng.uniform(5.1,12.8)
            center=[rr*math.cos(a),.40*rr*math.sin(a),z]
            clip(center,rng.uniform(.35,1.35),a+.5, rng.uniform(.04,.3),
                 C*.62 if j%4 else WHITE*.7,4)
        for side in [-1,1]:
            for j in range(12):
                clip([side*(8+j*.13),0,6-j*.32],2.7,side*.17,.38,
                     ACCENT*.40 if j%4==0 else faint,4)
        for k in range(24):
            a=k*tau/24
            line([[(7+.12*math.sin(t*8+a))*math.cos(a),
                   (4.3+.1*math.cos(t*8+a))*math.sin(a),t]
                  for t in np.linspace(-12,8,120)],C*.28)

    elif idx == 24:
        # Empty operator stations surrounded by a dead-ended switch maze.
        for side in [-1,1]:
            for j in range(6):
                x=side*(7.6+j*.42); z=5-j*2.7
                subdiv_box([x,-3.8,z],[3.2,2.4,1.7],7,dark)
                frame(z-.15,2.2,1.3,steel,x=x,y=-1.3,chamfer=.15)
                for v in range(18):
                    line([[x-1+v*.12,-1.9,z-.16],[x-1+v*.12,-.7,z-.16]],faint)
                # Wire chairs with empty seats, not human silhouettes.
                box([x,-4.9,z+1.7],[1.3,.18,1.2],WHITE*.45)
                beam([x,-4.8,z+2.3],[x,-2.9,z+2.3],.08,steel*.6,12)
                for xx in [-.5,.5]:
                    beam([x+xx,-6,z+1.3],[x+xx,-4.9,z+1.3],.04,dark,12)
        for j in range(70):
            a=j*tau/70
            p=[]
            radius=6.4+.025*j
            for t in np.linspace(0,1,150):
                # Repeated hard corners make every route fold back to the core.
                x=radius*math.cos(a)
                y=4.6*math.sin(a)
                z=-11+18*t
                if .35<t<.70:x+=math.sin(a)*2
                p.append([x,y,z])
            line(p,C*(.21 if j%5 else .62))
        # A monumental switch whose contacts never meet.
        for side in [-1,1]:
            for j in range(25):
                x=side*(3.4+j*.035)
                line([[x,-6,3],[x,-3,3],[side*.8,-1.2,-.3]],ACCENT*.42)
        for j in range(35):
            frame(-8-j*.04,8.8,10.5,dark,y=.1,chamfer=.35)

    elif idx == 25:
        # A braided fuse spans the whole picture, coiling through real depth.
        p=[]
        for t in np.linspace(0,1,600):
            x=-13+26*t
            y=-3.5+1.9*math.sin(t*tau)+1.0*math.sin(t*tau*2)
            z=-7+10*t+1.2*math.sin(t*math.pi*3)
            p.append([x,y,z])
        wire(p,.23,24,C*.72,5)
        for j in range(28):
            phase=j*tau/28
            line([[p[k][0],p[k][1]+.24*math.cos(k*.17+phase),
                   p[k][2]+.24*math.sin(k*.17+phase)]
                  for k in range(0,len(p),2)],WHITE*.27)
        for k in range(15,590,30):
            pt=np.asarray(p[k]); bottom=pt+[0,-2.2,.25]; bottom[1]=max(-6.25,bottom[1])
            beam(pt+[0,-.24,0],bottom,.035,dark,12)
            box(bottom+[0,-.1,0],[.8,.16,.8],C*.38)
        tip=np.array([10.6,-3.3,2.3])
        for j in range(180):
            d=unit(rng.normal(size=3)); length=rng.uniform(.3,2.2)
            line([tip+d*.15,tip+d*length],ACCENT*(.35+rng.random()*.6))

    elif idx == 26:
        # Three mutually orthogonal music staves; no generic Cartesian floor.
        for axis in range(3):
            for stave in range(5):
                p=[]
                for t in np.linspace(-12,12,360):
                    wave=.20*math.sin(t*1.4+axis*.8)
                    if axis==0:p.append([t,-2.3+stave*.36+wave,-4])
                    elif axis==1:p.append([-7,-5.4+stave*.36,t*.72-2])
                    else:p.append([6.4+stave*.36,t*.53,-5+wave])
                wire(p,.028,3,C*.55,0)
            for j in range(30):
                t=-11.5+j*.79
                if axis==0:a=[t,-2.5,-4];b=[t,-.65,-4]
                elif axis==1:a=[-7,-5.6,t*.72-2];b=[-7,-3.65,t*.72-2]
                else:a=[6.2,t*.53,-5];b=[8.05,t*.53,-5]
                line([a,b],steel*.45)
        for j in range(60):
            x=rng.uniform(-11,11); y=-2.0+rng.integers(0,5)*.34
            z=-3.8
            for d in np.linspace(0,.12,4):
                line([[x+.23*math.cos(a),y+.13*math.sin(a),z+d]
                      for a in np.linspace(0,tau,38)],WHITE*.55,True)
            beam([x+.22,y,z],[x+.22,y+1.35,z],.018,ACCENT*.65,8)
        for j in range(26):
            line([[x,4.6+.22*math.sin(x*.8+j*.09),-9+j*.10]
                  for x in np.linspace(-13,13,180)],C*.26)

    elif idx == 27:
        # A close, asymmetric articulated machine. No nested gates or central tunnel.
        # The main bearing occupies the right foreground. Long guides run toward a
        # physical meeting point outside the left edge, rather than the image center.
        def articulated_arm(start, end, hw, hh, twist, col):
            a=np.asarray(start,dtype=float); b=np.asarray(end,dtype=float)
            tangent=unit(b-a)
            u=unit(np.cross(tangent,[0,1,0]))
            v=np.cross(tangent,u)
            # Chamfered structural extrusion: eight discrete corner rails, many ribs,
            # and separate helical service cables in the open central channel.
            section=np.array([[-1,-.70],[-.70,-1],[.70,-1],[1,-.70],
                              [1,.70],[.70,1],[-.70,1],[-1,.70]])
            stations=np.linspace(0,1,105)
            paths=[[] for _ in range(8)]
            for t in stations:
                ang=twist*t
                uu=math.cos(ang)*u+math.sin(ang)*v
                vv=-math.sin(ang)*u+math.cos(ang)*v
                center=a+(b-a)*t+v*(.10*math.sin(t*math.pi))
                for j,(sx,sy) in enumerate(section):
                    paths[j].append(center+uu*sx*hw+vv*sy*hh)
            for j,p in enumerate(paths):
                line(p,col*(.9 if j%2==0 else .5))
            for k in range(0,len(stations),3):
                line([p[k] for p in paths],col*.55,True)
                if k+3<len(stations):
                    for side in [0,2,4,6]:
                        line([paths[side][k],paths[(side+2)%8][k+3]],col*.28)
            for j in range(6):
                phase=j*tau/6
                p=[]
                for t in stations:
                    p.append(a+(b-a)*t+u*(hw*.40*math.cos(phase+t*7))+
                             v*(hh*.40*math.sin(phase+t*7)))
                line(p,ACCENT*.34 if j==0 else C*.32)
            # End flanges are short, attached parts of the arm, not another portal.
            for endk in [0,-1]:
                for j in range(8):
                    p=np.asarray(paths[j][endk])
                    line([p,p+tangent*.28,p+tangent*.28+u*.08],WHITE*.52)

        def mechanical_joint(center,radius,depth,detail):
            p=np.asarray(center,dtype=float)
            radii=[radius*.36,radius*.44,radius*.70,radius*.77,radius*.94,radius]
            for z in np.linspace(-depth/2,depth/2,detail):
                for j,r in enumerate(radii):
                    ring(p+[0,0,z],r,2,C*.64 if j==4 else steel*.60,72)
            for a in np.linspace(0,tau,36,endpoint=False):
                ca,sa=math.cos(a),math.sin(a)
                for z in [-depth/2,depth/2]:
                    line([p+[radius*.45*ca,radius*.45*sa,z],
                          p+[radius*.71*ca,radius*.71*sa,z]],steel*.56)
                    line([p+[radius*.80*ca,radius*.80*sa,z],
                          p+[radius*.94*ca,radius*.94*sa,z]],ACCENT*.48 if int(a*36/tau)%6==0 else dark)
                # Thick casing teeth and through-bolts reveal real axial depth.
                q=p+np.array([radius*.93*ca,radius*.93*sa,0])
                line([q+[0,0,-depth/2],q+[0,0,depth/2]],C*.55)
                rr=radius*.075
                for z in [-depth*.51,depth*.51]:
                    line([q+[rr*math.cos(b),rr*math.sin(b),z]
                          for b in np.linspace(0,tau,7)],WHITE*.55,True)

        articulated_arm([8,-3,4],[-5,1.2,-5],.69,.40,.18,C*.68)
        articulated_arm([-5,1.2,-5],[-14,5,-11],.42,.62,-.28,steel*.68)
        articulated_arm([8,-3,4],[16,1.4,7],.73,.37,-.10,C*.61)
        # Two broken segments enter from outside the composition, with an obvious gap.
        articulated_arm([3.0,4.2,-3.6],[15.5,7.2,5.7],.45,.32,.32,steel*.64)
        articulated_arm([-16,-5.7,1.8],[-2.2,-3.8,-7.0],.36,.51,-.16,C*.48)
        mechanical_joint([8,-3,4],1.85,.98,5)
        mechanical_joint([-5,1.2,-5],1.13,.69,3)
        mechanical_joint([-12.1,4.0,-9.7],.62,.44,3)
        # Frayed hydraulic braids bridge only part of the gap; each has a distinct
        # slack curve, making the failure readable even in a static close-up.
        for j in range(18):
            a=np.array([2.65+(j%3)*.10,3.9+(j//3)*.07,-3.8])
            b=np.array([-.8+(j%3)*.13,2.4+(j//3)*.09,-6.2])
            p=[]
            for t in np.linspace(0,1,74):
                q=a*(1-t)+b*t
                q[1]-=(.35+j*.018)*math.sin(t*math.pi)
                q[2]+=.11*math.sin(t*9+j*.38)
                p.append(q)
            line(p,ACCENT*.63 if j%6==0 else C*.32)
        vanishing=np.array([-18.8,2.0,-15.8])
        for j in range(18):
            # Unevenly spaced rails are all subordinate to a single off-screen axis.
            start=np.array([14.5,-6.1+j*.16,7.2])
            finish=vanishing+np.array([0,j*.035,j*.055])
            pts=[]
            for t in np.linspace(0,.90,78):
                q=start*(1-t)+finish*t
                q[1]+=.07*math.sin(t*16+j*.5)
                pts.append(q)
            line(pts,C*(.42 if j%5==0 else .15))
        # Detached cut ends, retaining the precise rectangular steel cross section.
        for j in range(14):
            a=np.array([1.8+j*.095,3.3+(j%4)*.10,-4.5])
            b=a+np.array([-.5-rng.random()*.7,-.8-rng.random()*.5,-.6])
            beam(a,b,.025,WHITE*.58,9)

    elif idx == 28:
        # Sequential safety fences, each one already fractured in a different way.
        for layer in range(10):
            z=7-layer*1.9
            opening=1.0+layer*.17
            for row,y in enumerate(np.linspace(-6,6,32)):
                for col,x in enumerate(np.linspace(-13,13,58)):
                    if abs(x)<3.0+opening and abs(y)<2.3+opening*.3:continue
                    shift=.15*math.sin(col*.7+row*.9+layer)
                    p=np.array([x,y,z])
                    # Diamond mesh rather than the former rectangular ground grid.
                    line([p,p+[.23,.20,shift],p+[.46,0,0],p+[.23,-.20,-shift],p],
                         C*(.21 if (col+row)%6 else .49))
            for side in [-1,1]:
                beam([side*12,-6,z],[side*12,6,z],.11,steel*.7,24)
                beam([side*(3+opening),-2.3-opening*.3,z],
                     [side*(4.2+opening),-4.4,z+.9],.04,ACCENT*.7,12)
            for j in range(18):
                a=j*tau/18
                p=np.array([(4+opening)*math.cos(a),(2.5+opening*.4)*math.sin(a),z])
                d=unit([p[0],p[1],.7])
                line([p,p+d*rng.uniform(.4,1.6)],WHITE*.75)

    elif idx == 29:
        # A sheared GPU honeycomb. Center is an aperture; edges are computational mass.
        for layer in range(6):
            z=6-layer*3.1
            for row in range(13):
                y=-6+row*.97
                shear=(row-6)*.058*layer
                for col in range(19):
                    x=-11.6+col*1.26+(row%2)*.63+shear
                    if abs(x)<5.3 and abs(y)<2.9:continue
                    center=np.array([x,y,z])
                    for d in [-.28,0,.28]:
                        line([center+[.59*math.cos(a),.47*math.sin(a),d]
                              for a in np.linspace(0,tau,7)],
                             C*.43 if (col+row)%5 else WHITE*.6,True)
                    for a in np.linspace(0,tau,6,endpoint=False):
                        o=np.array([.59*math.cos(a),.47*math.sin(a),0])
                        line([center+o+[0,0,-.28],center+o+[0,0,.28]],dark)
                    box(center,[.40,.31,.18],ACCENT*.42 if col%9==0 else faint)
        for k in range(36):
            y=-6+k*.34
            line([[x,y+.17*math.sin(x*.5+k*.2),-11.5]
                  for x in np.linspace(-14,14,140)],C*.25)

    elif idx == 30:
        # Loom: taut warp threads, curved weft, tension pulleys, and a traveling shuttle.
        for j in range(130):
            x=-13+26*j/129
            p=[]
            for t in np.linspace(0,1,130):
                z=-12+20*t
                y=-3.8+.45*math.sin(t*tau*2+j*.10)*(1-t)+.025*j
                p.append([x,y,z])
            line(p,C*(.24 if j%6 else .62))
        for k in range(85):
            z=-11.5+k*.22
            p=[]
            for x in np.linspace(-13,13,140):
                p.append([x,-2.2+.20*math.sin(x*4.8+k*math.pi),z])
            line(p,WHITE*.29 if k%5 else ACCENT*.55)
        for side in [-1,1]:
            for z in [-10.8,6.8]:
                beam([side*12,-6,z],[side*12,6,z],.19,steel*.6,35)
                for j in range(8):
                    ring([side*12,3.5,z+j*.08],1.15,2,C*.55,100)
                for a in np.linspace(0,tau,20,endpoint=False):
                    line([[side*12,3.5,z],[side*12+1.1*math.cos(a),3.5+1.1*math.sin(a),z]],steel*.55)
        p=[]
        for t in np.linspace(0,1,180):
            p.append([-13+26*t,1.7+1.9*math.sin(t*math.pi),-5.0])
        wire(p,.14,12,ACCENT*.55,8)

    elif idx == 31:
        # Recursive gates alternate their aspect, offset and physical construction.
        for layer in range(23):
            z=7.5-layer*.85
            ang=.095*math.sin(layer*.55)
            w=21-layer*.35; h=11.3-layer*.13
            x=.9*math.sin(layer*.55); y=.6*math.cos(layer*.48)
            for inset in range(8):
                ww=w-inset*.065; hh=h-inset*.065
                pts=[]
                for px,py in [(-ww/2,-hh/2),(ww/2,-hh/2),(ww/2,hh/2),(-ww/2,hh/2)]:
                    pts.append([x+px*math.cos(ang)-py*math.sin(ang),
                                y+px*math.sin(ang)+py*math.cos(ang),z-inset*.025])
                line(pts,C*(.64 if inset==0 else .23),True)
            for edge in range(4):
                for j in range(90):
                    t=j/89
                    if edge==0:px=-w/2+w*t;py=-h/2
                    elif edge==1:px=w/2;py=-h/2+h*t
                    elif edge==2:px=w/2-w*t;py=h/2
                    else:px=-w/2;py=h/2-h*t
                    q=np.array([x+px*math.cos(ang)-py*math.sin(ang),y+px*math.sin(ang)+py*math.cos(ang),z])
                    line([q,q+[0,0,-.60]],WHITE*.37)
            if layer%3==0:
                for side in [-1,1]:
                    line([[side*(w/2+.1),-h/2,z],[side*(w/2+.6),-h/2-.5,z-.5],
                          [side*(w/2+.6),h/2+.5,z-.5],[side*(w/2+.1),h/2,z]],ACCENT*.50)
        for j in range(80):
            a=j*tau/80
            line([[(11-.24*k)*math.cos(a+.08*k),
                   (5.8-.10*k)*math.sin(a+.08*k),7.5-k*.85] for k in range(23)],dark)

    elif idx == 32:
        # An occluding observation aperture assembled from long, staggered slats.
        for side in [-1,1]:
            for j in range(100):
                x=side*(2.7+j*.112)
                z=3.6+.35*math.sin(j*.24)
                y0=-6.7; y1=6.7
                line([[x,y0,z],[x,y1,z]],C*(.23 if j%5 else .64))
                line([[x+.035,y0,z-.25],[x+.035,y1,z-.25]],steel*.32)
                for k in range(20):
                    y=-6.4+k*.67
                    line([[x,y,z],[x+.055,y,z-.35]],dark)
        for j in range(58):
            rr=2.1+j*.023
            p=[]
            for a in np.linspace(0,tau,160):
                # An almond eye-hole, not another decorative circular instrument.
                x=rr*math.cos(a)
                y=1.32*math.sin(a)*abs(math.sin(a))**.32
                p.append([x,y,-1.0-j*.065])
            line(p,C*(.22 if j%6 else .65),True)
        for k in range(60):
            a=k*tau/60
            line([[2.5*math.cos(a)*(1+t*.55),1.7*math.sin(a)*(1+t*.55),-2-10*t]
                  for t in np.linspace(0,1,95)],faint)
        for j in range(100):
            p=rng.uniform([-8,-5,-12],[8,5,-8])
            q=p+rng.normal(0,.22,3)
            line([p,q],ACCENT*.42)

    elif idx == 33:
        # A real wire theater, including fly tower, rigging, wings, seats and a trap.
        for z in np.linspace(-10,3.5,38):
            frame(z,22.5,12,C*.38,y=.1,chamfer=.25)
            for x in np.linspace(-11,11,32):
                line([[x,6,z],[x,6.55,z-.22]],steel*.4)
        # Curtain fabric uses paired ruled curves, not an opaque textured backdrop.
        for side in [-1,1]:
            for j in range(82):
                x=side*(6+j*.078)
                p=[]
                for y in np.linspace(-6,6,125):
                    p.append([x+side*.28*math.sin(y*.5+j*.17),y,
                              1.6+.22*math.sin(j*.41)+.05*y*y])
                line(p,C*(.22 if j%7 else .64))
            for k in range(12):
                z=-10+k*1.0
                for xx in [side*6.2,side*10.8]:
                    beam([xx,-6,z],[xx,6,z],.055,steel*.35,20)
                line([[side*6.2,6,z],[side*10.8,6,z],[side*10.8,-6,z]],dark)
        for x in np.linspace(-10.5,10.5,40):
            line([[x,6.2,z] for z in np.linspace(-11,6,80)],C*.23)
        for j in range(40):
            x=-9.7+j*.5
            line([[x,6.3,-8],[x,2.7+.8*math.sin(j*.4),-4],[x,6.3,1]],steel*.38)
        for row in range(6):
            z=3+row*.8
            for seat in range(20):
                x=-10+seat*1.05
                y=-5.6-row*.12
                box([x,y,z],[.76,.18,.65],dark)
                line([[x-.38,y,z+.34],[x-.38,y+1.0,z+.34],
                      [x+.38,y+1.0,z+.34],[x+.38,y,z+.34]],steel*.5)
        for inset in range(12):
            frame(-4.5-inset*.12,4.8-inset*.11,7.2-inset*.11,
                  ACCENT*(.26 if inset else .7),y=-.8)

    return m
