"""Fabricated foreground mechanisms for the first two verses.

No labels, image planes, free-standing pictograms or arbitrary scan paths.
Every visible lead terminates at a socket, bearing, fixture or moving part.
"""

def optimization_path(u):
    import math
    return [-14+28*u, -4.7+.65*math.cos(u*math.tau), 2-21*u]


def build_first_half(Mesh,np,math,C,WHITE,ACC):
    out={}
    def mesh(key):
        m=Mesh();out[key]=m;return m
    def line(m,pts,c=C,closed=False):m.line(pts,c,closed)
    def ring(m,p,r,c=C,axis=2,n=40):m.circle(r,p,axis,c,n)
    def basis(a,b):
        d=np.array(b,float)-np.array(a,float);d/=max(1e-9,np.linalg.norm(d))
        v=np.cross(d,[0,1,0] if abs(d[1])<.9 else [1,0,0]);v/=max(1e-9,np.linalg.norm(v))
        return v,np.cross(d,v)
    def tube(m,pts,r=.09,c=C,n=6,collars=0):
        p=np.array(pts,float)
        for j in range(len(p)-1):
            a,b=p[j:j+2];v,w=basis(a,b)
            for q in np.linspace(0,math.tau,n,endpoint=False):
                d=r*(math.cos(q)*v+math.sin(q)*w);line(m,[a+d,b+d],c*(1 if q==0 else .48))
            for t in np.linspace(0,1,collars+2):
                line(m,[a+(b-a)*t+r*(math.cos(q)*v+math.sin(q)*w) for q in np.linspace(0,math.tau,n,endpoint=False)],c*.5,True)
    def box(m,p,size,c=C,detail=False):
        p=np.array(p,float);h=np.array(size,float)*.5
        vertices=[p+h*[x,y,z] for x in [-1,1] for y in [-1,1] for z in [-1,1]]
        for i,a in enumerate(vertices):
            for b in vertices[i+1:]:
                if np.count_nonzero(abs(a-b)>1e-7)==1:line(m,[a,b],c)
        if detail:
            for sx in [-1,1]:
                for sy in [-1,1]:ring(m,p+[sx*h[0]*.8,sy*h[1]*.8,h[2]+.03],.07,WHITE*.45,n=12)
            for j in range(7):
                x=-h[0]*.7+j*h[0]*1.4/6
                line(m,[p+[x,-h[1]*.6,h[2]+.02],p+[x,h[1]*.6,h[2]+.02]],c*.32)
    def sphere(m,p,r,c=WHITE,n=36,rings=7):
        p=np.array(p,float)
        for a in np.linspace(-math.pi/2+.15,math.pi/2-.15,rings):
            rr=r*math.cos(a);yy=r*math.sin(a)
            line(m,[p+[rr*math.cos(q),yy,rr*math.sin(q)] for q in np.linspace(0,math.tau,n,endpoint=False)],c*.6,True)
        for q in np.linspace(0,math.tau,12,endpoint=False):
            line(m,[p+[r*math.cos(a)*math.cos(q),r*math.sin(a),r*math.cos(a)*math.sin(q)] for a in np.linspace(-math.pi/2,math.pi/2,n)],c*.7)
    def floor(m,y=-7.,depth=-24.,c=C*.28):
        for x in [-17,-8,8,17]:tube(m,[[x,y,4],[x,y,depth]],.10,c,collars=9)
        for z in np.linspace(3,depth,12):
            for side in [-1,1]:tube(m,[[side*8,y,z],[side*17,y,z]],.055,c)

    # Three braids have depth and physical terminations, not PCB squares.
    shell=mesh('circuit_cables');cores=mesh('circuit_synapses');current=mesh('circuit_contacts')
    floor(shell)
    for side in [-1,1]:
        for lane in range(3):
            y=-4.9+lane*4.8;x=side*(10.3+lane*.7)
            pts=[]
            for u in np.linspace(0,1,50):pts.append([x+side*2.1*math.sin(u*math.pi),y+.9*math.sin(u*math.tau),3-u*27])
            tube(shell,pts,.19,C*.55,n=6)
            for j,u in enumerate([.08,.30,.55,.82]):
                p=np.array(pts[round(u*49)])
                sphere(cores,p,.38,WHITE*.62,n=20,rings=4)
                box(cores,p+[side*1.5,0,-.8],(1.2,.8,1.8),C*.5,True)
                tube(shell,[p,p+[side*1.5,0,-.8],p+[side*2,0,-3]],.055,C*.45)
                ring(current,p+[0,0,.4],.21,WHITE*.85,n=18)

    # Counterweighted control rig: control changes hands through actual ropes.
    frame=mesh('control_gantry');terminal=mesh('control_terminal');hand=mesh('control_gripper');reins=mesh('control_reins')
    floor(frame)
    for side in [-1,1]:
        tube(frame,[[side*13,-7,2],[side*13,8,2],[side*13,8,-15]],.22,C*.65,collars=12)
        for z in [1,-5,-11]:
            ring(frame,[side*13,7,z],.85,WHITE*.65,axis=0)
            ring(frame,[side*13,7,z],.55,C*.55,axis=0)
    tube(frame,[[-13,8,-3],[13,8,-3]],.25,C*.65,collars=12)
    box(terminal,[-10,-4,1],(4.8,2.4,3.7),C*.8,True)
    for k in range(3):ring(terminal,[-11.4+k*1.4,-3.8,2.9],.28,WHITE*.8,n=24)
    for side in [-1,1]:
        tube(hand,[[9,4,-3],[9+side*1.5,3.5,-1],[9+side*1.6,1,-.5],[9+side*.7,.1,0]],.18,WHITE*.78,collars=4)
    box(hand,[9,4.3,-3],(4,1,2.2),C*.65,True)
    for k in range(6):
        yy=6.0+k*.12
        tube(reins,[[-10+k*.17,-2.8,1],[-13,yy,1],[-13,yy,-3],[13,yy,-3],[9+(k-2.5)*.3,3.7,-3]],.025,C*.6)

    # Dialogue is a pair of opposing mechanical card/turn-taking chambers.
    body=mesh('dialogue_housing');shelves=mesh('dialogue_cards');shuttle=mesh('dialogue_shuttle');jaws=mesh('dialogue_latch')
    floor(body,-7,-28)
    for side in [-1,1]:
        for z in [1,-8,-17]:
            x=side*12
            box(body,[x,0,z],(6,12,2.2),C*.5,True)
            for y in [-5,5]:tube(body,[[side*8.5,y,z+1.3],[side*15,y,z+1.3],[side*15,y,z-5]],.10,WHITE*.48)
            for k in range(9):
                yy=-4.3+k*.98
                # Folded reply sheets sit inside slots, including a real lip.
                line(shelves,[[x-2.2,yy,z+1.5],[x+2.0,yy,z+1.5],[x+2.2,yy+.25,z+1.35],[x+2.2,yy+.5,z+.8],[x-2.2,yy+.5,z+.8]],C*.65,True)
                for v in range(3):line(shelves,[[x-1.8,yy+.10+v*.09,z+1.51],[x+.6+(k%3)*.3,yy+.10+v*.09,z+1.51]],WHITE*.35)
        for x in [side*7.8,side*16]:tube(body,[[x,-6,3],[x,-6,-27]],.14,C*.5,collars=14)
    for j in range(4):
        z=1-j*1.5;box(shuttle,[0,0,z],(3.2,2,.13),WHITE*.65)
        line(shuttle,[[-1.2,-.45,z+.09],[.8,-.45,z+.09],[.8,.5,z+.09]],C*.6)
    for side in [-1,1]:
        tube(jaws,[[side*8,-6,1],[side*8,6,1]],.3,WHITE*.65,collars=12)
        for j in range(8):
            y=-5.2+j*1.5
            tube(jaws,[[side*8,y,1],[side*6.6,y,.6],[side*6.3,y+.3,-1.6]],.095,C*.75)

    # Four independent stressed shutters make a threshold tangible, no dial.
    gate=mesh('risk_iris');fuse=mesh('risk_filaments')
    for side in [-1,1]:
        for y in [-5.8,5.8]:
            p=np.array([side*10,y,-3.])
            box(gate,p,(4,2.8,5),C*.6,True)
            tube(gate,[p+[0,0,2],p+[-side*2.5,-y*.22,2],p+[-side*3.2,-y*.32,-4]],.15,WHITE*.8,collars=8)
            for j in range(7):tube(fuse,[p+[side*.3,-.6+j*.2,2.7],p+[-side*2.5,-.6+j*.2,2.7]],.023,WHITE*.65)

    # A Chinese-room exit sorter stays on the same delivery rail. The bag's
    # mycelium becomes a vaulted gill ceiling: a finite spatial hallucination.
    sorter=mesh('exit_sorter');canopy=mesh('exit_canopy');growth=mesh('exit_mycelium')
    for z in [-10,-20]:
        for x in [1.5,8.5]:tube(sorter,[[x,-7,z],[x,3,z],[x,3,z-2]],.17,C*.6,collars=8)
        tube(sorter,[[1.5,3,z],[8.5,3,z]],.16,WHITE*.6,collars=7)
    for x in [2,8]:tube(sorter,[[x,-5,-7],[x,-5,-24]],.16,C*.7,collars=12)
    for j,z in enumerate(np.linspace(-8,-23,12)):
        tube(sorter,[[2,-4.6,z],[8,-4.6,z]],.16,WHITE*.55,n=8)
        if j%2==0:
            box(sorter,[5,-4.1,z],(3.6,.18,1.4),WHITE*.6)
            # Folded symbol strips pass beneath the real stamp crosshead.
            for k in range(3):line(sorter,[[3.6+k*.9,-3.97,z-.3],[3.9+k*.9,-3.97,z+.3],[4.2+k*.9,-3.97,z-.3]],C*.65)
    box(sorter,[5,1,-14],(5,1.6,4),C*.6,True)
    for x in [3,7]:tube(sorter,[[x,1,-14],[x,-3,-14]],.21,WHITE*.7,collars=10)
    box(sorter,[5,-3.3,-14],(5.5,.6,3.5),C*.7,True)
    tube(sorter,[[-9,-8.8,-12],[-9,-8.8,-20],[2,-8.8,-20],[2,-5,-20]],.17,C*.6,collars=9)
    # A large asymmetrical umbrella has true underside curvature and ribs;
    # its stems attach to the cargo-side column, not to the camera.
    center=np.array([-3.7,4.4,-17.0]);radius=12.4
    for angle in np.linspace(0,math.tau,68,endpoint=False):
        pts=[]
        for rr in np.linspace(.35,radius,48):
            f=rr/radius;pts.append(center+[rr*math.cos(angle),-2.2*f*f+.18*math.sin(f*math.pi),rr*.66*math.sin(angle)])
        line(canopy,pts,WHITE*(.35 if int(angle*17)%3 else .5))
        line(canopy,np.array(pts)+[0,-.17,0],C*.32)
    for rr in np.linspace(2,radius,10):
        f=rr/radius;line(canopy,[center+[rr*math.cos(a),-2.2*f*f,rr*.66*math.sin(a)] for a in np.linspace(0,math.tau,120,endpoint=False)],C*.35,True)
    for j in range(8):
        off=(j-3.5)*.12
        tube(growth,[[-11+off,-8.8,-12],[-15+off,-5,-15],[-15+off,1,-18],[-9+off,4,-19],[-3.7+off,4.4,-17]],.035,C*.5)
    for x in [-14,7]:
        tube(sorter,[[x,-7,-22],[x,2,-22],[x,2,-24]],.13,C*.4,collars=12)

    # Repeatable training cells, with a balanced mechanical registrar.
    bench=mesh('training_bench');steps=mesh('training_steps');piston=mesh('training_piston')
    floor(bench)
    for side in [-1,1]:
        for j in range(9):
            x=side*(9.8+.35*math.sin(j));z=2-j*2.7
            box(steps,[x,-3.6,z],(3.8,1.9,1.5),C*.6,True)
            for off in [-.65,.65]:tube(bench,[[x+off,-4.4,z],[x+off,-7,z],[x+off,-7,z-2]],.075,C*.5)
            for k in range(3):ring(steps,[x-.8+k*.8,-3.4,z+.8],.18,WHITE*.5,n=16)
        tube(bench,[[side*13,-7,3],[side*13,6,3],[side*13,6,-24]],.16,C*.5,collars=10)
        tube(piston,[[side*10,-1,0],[side*10,4.5,0]],.27,WHITE*.8,collars=13)
        box(piston,[side*10,-1,0],(3.2,.8,2.4),C*.65,True)

    # Actual fabrication benches at three scales, not a cosmic black-hole icon.
    forge=mesh('evolution_forge');arms=mesh('evolution_arms');child=mesh('evolution_child')
    floor(forge)
    for side in [-1,1]:
        box(forge,[side*11,-5.5,-3],(8,2.8,13),C*.55,True)
        for y in [-4,5]:tube(forge,[[side*7,y,3],[side*7,y,-19],[side*16,y,-19]],.16,C*.5,collars=12)
        pts=[[side*15,-4,0],[side*15,4,-1],[side*10,6,-5],[side*9,0,-8]]
        for a,b in zip(pts,pts[1:]):tube(arms,[a,b],.24,WHITE*.8,collars=8)
        for p in pts:sphere(arms,p,.55,C*.8,n=24,rings=5)
        for k in [-1,1]:tube(arms,[pts[-1],[side*9+k*.9,-.3,-8],[side*9+k*.4,-1.3,-8]],.10,C*.8)
        box(child,[side*10,-3,-8],(3,3,4.5),WHITE*.6,True)
        for d in range(6):line(child,[[side*8.7,-4.3+d*.5,-5.7],[side*11.3,-4.3+d*.5,-5.7]],C*.5)

    land=mesh('optimization_land');track=mesh('optimization_track');cart=mesh('optimization_cart')
    floor(land,-8,-28)
    def h(x,z):return min(3.8,-7.3+.018*(x+z*.8)**2+.35*math.sin(z*.65+x*.25))
    for x in np.linspace(-17,17,45):
        if abs(x)<5:continue
        line(land,[[x,h(x,z),z] for z in np.linspace(3,-25,65)],C*.35)
    for z in np.linspace(3,-25,31):
        for side in [-1,1]:line(land,[[x,h(x,z),z] for x in np.linspace(side*5,side*17,28)],C*.4)
    path=np.array([optimization_path(u) for u in np.linspace(0,1,90)])
    for offset in [-.5,.5]:tube(track,path+[0,offset,0],.09,WHITE*.8,n=6)
    for i,p in enumerate(path[::4]):
        tube(land,[p+[0,-.6,0],p+[0,-2,0],p+[0,-2,-1]],.055,C*.5)
        line(track,[p+[0,-.55,0],p+[0,.55,0]],C*.55)
    sphere(cart,[0,0,0],.58,WHITE*.85,n=40,rings=9)
    ring(cart,[0,0,0],.82,C*.8,axis=0);ring(cart,[0,0,0],.75,C*.65,axis=1)

    lattice=mesh('atom_lattice');cluster=mesh('atom_cluster');assembler=mesh('atom_assembler')
    floor(assembler,-7,-26)
    for side in [-1,1]:
        for x in range(4):
            for y in range(5):
                for z in range(5):
                    p=np.array([side*(7.8+x*1.7),-4.3+y*1.8,-1-z*2.3])
                    sphere(lattice,p,.17,WHITE*.65,n=12,rings=3)
                    for d in [[side*1.7,0,0],[0,1.8,0],[0,0,-2.3]]:
                        if (d[0] and x<3) or (d[1] and y<4) or (d[2] and z<4):line(lattice,[p,p+d],C*.48)
        for z in [1,-11]:tube(assembler,[[side*16,-7,z],[side*16,7,z],[side*6,7,z]],.17,C*.5,collars=10)
    for x in range(3):
        for y in range(3):
            for z in range(3):
                p=np.array([(x-1)*.9,(y-1)*.9,(z-1)*.9]);sphere(cluster,p,.17,WHITE*.75,n=12,rings=3)
                for d,ok in [([.9,0,0],x<2),([0,.9,0],y<2),([0,0,.9],z<2)]:
                    if ok:line(cluster,[p,p+d],C*.7)

    # The small inspection jig cannot encompass the plant beyond its scope.
    jig=mesh('inspection_jig');sample=mesh('inspection_sample');plant=mesh('inspection_plant')
    box(jig,[-10.5,-3.8,1],(6.2,1.1,6),C*.75,True)
    for side in [-1,1]:
        tube(jig,[[-10.5+side*2.6,-3.2,2],[-10.5+side*2.6,2.5,2],[-10.5+side*1.9,3.3,2]],.18,WHITE*.7,collars=6)
        tube(jig,[[-10.5+side*2.6,-3.2,-1],[-10.5+side*2.6,-7,-1]],.17,C*.55)
    box(sample,[-10.5,-1.3,1],(2.7,3.2,2.8),WHITE*.75,True)
    for side in [-1,1]:
        for j in range(6):
            x=side*(9+j*.7);z=-9-j*3.7
            box(plant,[x,-1,z],(5+j*.5,10+j,1.7),C*.5,True)
            for k in range(6):
                y=-4+k*1.4
                tube(plant,[[x-2,y,z+1],[x+2,y,z+1],[x+2,y,z-2]],.055,WHITE*.42)
    sled=mesh('orbital_sled')
    box(sled,[0,0,0],(3.4,.6,2.6),C*.7,True)
    for side in [-1,1]:
        for z in [-.85,.85]:
            tube(sled,[[side*1.5,-.15,z],[side*1.7,-.8,z],[side*.7,-.8,z]],.09,C*.7)
            ring(sled,[side*1.5,-.55,z],.30,WHITE*.7,axis=2,n=24)
    return out
