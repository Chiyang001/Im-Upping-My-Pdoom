"""Semantic parts fabricated as deep machine assemblies, rather than icons."""

def build_integrated(Mesh,np,math,C,WHITE,ACC):
    from semantic_geometry import build_semantics
    old=build_semantics(Mesh,np,math,C,WHITE,ACC)
    keep=('loss_curve','omega_threads','omega_focus','fuse_cord','fuse_spark','show_backstage')
    out={k:old[k] for k in keep}
    def mesh(key):
        m=Mesh();out[key]=m;return m
    def line(m,p,c=C,closed=False):m.line(p,c,closed)
    def ring(m,p,r,c=C,axis=2,n=36):m.circle(r,p,axis,c,n)
    def pipe(m,pts,r=.055,c=C):
        pts=np.asarray(pts,float)
        for k in range(5):
            a=k*math.tau/5;off=np.array([0,r*math.cos(a),r*math.sin(a)])
            line(m,pts+off,c*(1 if k==0 else .45))
    def case(m,p,w=3.8,h=2.1,d=1.7,c=C):
        p=np.asarray(p,float)
        shape=np.array([[-w*.5,-h*.35],[-w*.36,-h*.5],[w*.43,-h*.5],[w*.5,-h*.3],[w*.5,h*.3],[w*.35,h*.5],[-w*.5,h*.5]])
        for z in [-d*.5,d*.5]:line(m,np.c_[shape,np.full(len(shape),z)]+p,c,True)
        for q in shape:line(m,[p+[q[0],q[1],-d*.5],p+[q[0],q[1],d*.5]],c*.5)
        for x in [-w*.35,w*.35]:
            for y in [-h*.28,h*.28]:ring(m,p+[x,y,d*.5+.04],.07,WHITE*.5,n=12)
        for j in range(7):
            xx=-w*.32+j*w*.105;line(m,[p+[xx,-h*.25,d*.5+.06],p+[xx,h*.25,d*.5+.06]],c*.3)

    m=mesh('loss_mount')
    for side in [-1,1]:
        pipe(m,[[side*14,7,-4],[side*14,-7,-4],[side*14,-7,-19]],.10,C*.55)
        for j in range(16):
            z=-5-j*.8;line(m,[[side*14,-6,z],[side*11,-6,z],[side*11,-5.8,z-.4]],C*.25)

    m=mesh('cdr_cells')
    for j in range(5):
        p=np.array([-11+j*5.2,3.8+.35*math.sin(j),-3-j*2.4]);case(m,p,c=C*.8)
        pipe(m,[p+[0,-1,-.6],p+[0,-5,-1],p+[0,-9,-4]],.08,C*.45)
        for z in np.linspace(-.6,.6,5):line(m,[p+[0,-.9,z],p+[0,.9,z]],WHITE*.45)
        case(m,p+[-.85,-6.9,-2.4],1.8,1.25,.9,C*.45)
    m=mesh('cdr_links')
    for j in range(4):
        a=np.array([-10+j*5.2,3.8+.35*math.sin(j),-2.1-j*2.4]);b=np.array([-13.3+(j+1)*5.2,3.8+.35*math.sin(j+1),-2.1-(j+1)*2.4])
        pipe(m,[a,a+[1.2,0,-1],b+[-.5,0,.4],b],.07,WHITE*.65)
        ring(m,a,.19,C*.65,n=24)
    m=mesh('cdr_head');case(m,[0,0,0],1.55,1.5,1.,WHITE*.7)
    m=mesh('cdr_rest')
    for j in range(1,5):
        p=np.array([-11+j*5.2,3.8+.35*math.sin(j),-3-j*2.4])
        pipe(m,[p+[-1.2,-.8,1],p+[1.2,-.8,1]],.05,WHITE*.6)

    m=mesh('memory_banks')
    for side in [-1,1]:
        for j in range(11):
            p=np.array([side*10.5,-5.7+j*1.15,-5-j*.28]);case(m,p,4.2,.8,2.2,C*.6)
            pipe(m,[p+[side*2.1,0,0],p+[side*3.,0,-3],p+[side*3.,0,-12]],.035,C*.4)
    m=mesh('memory_bus')
    for side in [-1,1]:
        for j in range(9):pipe(m,[[side*10.5,-5.7+j*1.15,-5-j*.28],[side*6.5,-5.7+j*1.15,-7],[side*6.5,-6+j*.16,-13]],.04,C*.6)

    m=mesh('gato_channels')
    for lane in range(3):
        y=-5.4+lane*5.4
        for j in range(5):
            off=(j-2)*.14;pipe(m,[[-16,y+off,1],[-10,y+off,-3],[-7,y*.9+off,-9],[7,y*.6+off,-17],[13,2+off,-23]],.025,C*(.6 if j==2 else .27))
        for z in [0,-4,-9,-15]:
            x=-14+(abs(z)/15)*19
            case(m,[x,y,-3+z],1.25,.65,1.,C*.42)

    m=mesh('mask_tokens');missing=mesh('mask_missing');filled=mesh('mask_filled')
    for side in [-1,1]:
        for j in range(11):
            p=np.array([-14+j*2.8,side*(4.8+.25*math.sin(j*.7)),-4-j*.38])
            case(m,p,2.2,1.4,1.7,C*.43)
            pipe(m,[p+[0,side*.8,-.8],p+[0,side*2.,-3],p+[0,side*2.,-12]],.035,C*.27)
            if j%4==1:
                for k in range(4):ring(missing,p+[0,0,1.02-k*.13],.25,WHITE*.35,n=24)
                case(filled,p+[0,0,.15],1.65,.9,.9,WHITE*.7)
            else:
                for k in range(4):line(m,[p+[-.5,-.3+k*.2,.91],p+[.6,-.3+k*.2,.91]],C*.5)

    m=mesh('loom_branches');active=mesh('loom_selected');ports=mesh('loom_ports')
    for side in [-1,1]:
        prev=[np.array([0,side*6.,3.])]
        for level in range(1,5):
            count=2**level;current=[]
            for j in range(count):
                x=(j-(count-1)/2)*28/count;y=side*(5.7+.8*math.sin(j*1.9+level));z=3.-level*6.5
                p=np.array([x,y,z]);parent=prev[j//2];current.append(p)
                mid=parent*.55+p*.45+np.array([0,side*.6,0]);path=[parent,mid,p]
                pipe(m,path,.075,C*.55)
                if j==count//2:pipe(active,path,.075,WHITE*.7)
                for offset in [-.25,0,.25]:ring(ports,p+[0,0,offset],.3+level*.02,C*.55,n=28)
                line(m,[p+[0,-.5,0],p+[0,-.5,-3]],C*.25)
            prev=current
        # Last forks are tied into the same long load-bearing rails.
        for p in prev:pipe(m,[p,[p[0],side*8,-27]],.035,C*.23)
    return out
