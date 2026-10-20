"""Concrete lyric referents, built only from line segments; no texture/text."""

def build_semantics(Mesh,np,math,C,WHITE,ACC):
    out={}
    def mesh(name):
        m=Mesh();out[name]=m;return m
    def line(m,p,c=C):m.line(p,c)
    def ring(m,p,r,c=C,sy=1.,n=64):
        line(m,[np.array(p)+[r*math.cos(a),r*sy*math.sin(a),0] for a in np.linspace(0,math.tau,n)],c)
    def beam(m,a,b,w=.08,c=C):
        a=np.array(a,float);b=np.array(b,float);v=b-a;v/=max(1e-8,np.linalg.norm(v));u=np.cross(v,[0,0,1.])
        if np.linalg.norm(u)<.01:u=np.cross(v,[0,1.,0])
        u/=np.linalg.norm(u);q=np.cross(v,u)
        for off in [u*w,-u*w,q*w,-q*w]:line(m,[a+off,b+off],c)
        for s in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/1.5))):
            p=a+(b-a)*s;line(m,[p+u*w,p+q*w,p-u*w,p-q*w,p+u*w],c*.6)
    def card(m,p,w=1,h=.7,c=C):
        m.box(p,(w,h,.13),c)
        for j in range(3):line(m,[np.array(p)+[-w*.34,-h*.25+j*h*.23,.08],np.array(p)+[w*.25,-h*.25+j*h*.23,.08]],c*.55)
    def chip(m,p,size=3.,c=C):
        p=np.array(p,float);m.box(p,(size,size,.45),c);m.box(p+[0,0,.26],(size*.7,size*.7,.05),WHITE*.65)
        for side in [-1,1]:
            for a in np.linspace(-size*.4,size*.4,11):
                line(m,[p+[a,side*size*.5,0],p+[a,side*(size*.5+.45),0]],c)
                line(m,[p+[side*size*.5,a,0],p+[side*(size*.5+.45),a,0]],c)
        for j in range(6):line(m,[p+[-size*.28,-size*.28+j*size*.11,.32],p+[size*.28,-size*.28+j*size*.11,.32]],c*.5)

    m=mesh('risk_face')
    for r in [6.5,6.7,7.1,7.2]:ring(m,[0,0,-2],r,WHITE*.5,sy=.82,n=120)
    for k in range(70):
        a=math.pi*.18+k*math.pi*1.64/69
        line(m,[[r*math.cos(a),r*.82*math.sin(a),-1.8] for r in [6.,6.5]],ACC*.8 if k>44 else C*.75)
    for x in [-12,12]:
        for y in [-5,5]:beam(m,[x,y,2],[x*.62,y*.62,-3],.1,C*.55)
    m=mesh('risk_needle');beam(m,[0,0,-1.5],[5.65,0,-1.5],.09,ACC);ring(m,[0,0,-1.4],.45,WHITE)

    m=mesh('eye_shell')
    for side in [-1,1]:
        for j in range(8):
            line(m,[[side*(7.0+7.5*math.cos(a)),(3.8+j*.035)*math.sin(a),-3-j*.15] for a in np.linspace(0,math.tau,140)],C*(.7-j*.06))
        for r in [1.5,2.,2.6,2.8]:ring(m,[side*7,0,-2.8],r,WHITE*.7,n=90)
        for a in np.linspace(0,math.tau,42):line(m,[[side*7+2*math.cos(a),2*math.sin(a),-2.7],[side*7+2.7*math.cos(a),2.7*math.sin(a),-3.6]],ACC*.65)
    m=mesh('eye_life')
    for side in [-1,1]:
        p=np.array([side*10.,5.8,-5]);ring(m,p,2.,WHITE*.8)
        for k in range(24):
            a=k*math.tau/24;line(m,[p+[1.6*math.cos(a),1.6*math.sin(a),0],p+[1.9*math.cos(a),1.9*math.sin(a),0]],C)
        for j in range(9):line(m,[[side*(5+j*.9),-6.,-4],[side*(5+j*.9),-4.5+.5*math.sin(j),-4]],ACC*.6)
    m=mesh('eye_trade')
    for k in range(40):
        a=math.pi/2+k*math.pi/40;line(m,[[2.*math.cos(a),2.*math.sin(a),0],[1.6*math.cos(a),1.6*math.sin(a),0]],ACC)
    beam(m,[0,0,0],[0,1.7,0],.04,WHITE)

    m=mesh('circuit_board')
    for x in [-11,-5.5,5.5,11]:
        for y in [-5.5,5.5]:chip(m,[x,y,-4],2.2)
    for k in range(20):
        y=-7.8+k*.82;s=-1 if k%2 else 1
        line(m,[[s*18,y,-6],[s*13,y,-6],[s*10,y*.72,-4],[s*5.8,y*.72,-4],[s*4,y*.35,-1]],C*.4)
        ring(m,[s*13,y,-5.9],.10,WHITE*.6,n=12)
    m=mesh('circuit_synapse')
    for k in range(16):
        a=k*math.tau/16
        line(m,[[r*math.cos(a+.3*math.sin(r)),r*.7*math.sin(a+.3*math.sin(r)),-3+.15*r] for r in np.linspace(2,13,40)],ACC*.6)
    m=mesh('loss_axes')
    for j in range(16):line(m,[[-13,-6+j*.8,-5],[14,-6+j*.8,-5]],C*.16)
    for j in range(28):line(m,[[-13+j,-6,-5],[-13+j,6,-5]],C*.15)
    beam(m,[-13,7,-4],[-13,-6,-4],.08,WHITE);beam(m,[-13,-6,-4],[15,-6,-4],.08,WHITE)
    m=mesh('loss_curve')
    for z in [-4,-4.2,-4.4]:line(m,[[x,5.8-8.5/(1+math.exp(-(x-1.5)*1.1))+.2*math.sin(x*6),z] for x in np.linspace(-12,14,190)],ACC*.8)
    m=mesh('loss_layers')
    for side in [-1,1]:
        for z in range(5):
            chip(m,[side*11,-3,-6-z*2.5],2.2,C*.5)
            for y in [-6,0]:beam(m,[side*11,y,-6],[side*11,y,-17],.04,C*.4)

    m=mesh('hierarchy')
    for x,y,s in [(-10,-4,1.3),(9,4,3.6)]:
        chip(m,[x,y,-5],s)
        for j in range(10):line(m,[[x,y+s*.65,-5],[x+(j-4.5)*.45,y+s+1.,-7]],C*.5)
    m=mesh('hierarchy_tether')
    for j in range(6):line(m,[[-10,-2+j*.2,-5],[-6,1,-5],[3,1,-5],[9,2-j*.2,-5]],ACC*.5)

    m=mesh('sydney_bubbles')
    for side in [-1,1]:
        for z in range(7):
            xx=side*(7.7+.06*z);yy=side*2.8
            line(m,[[xx-4,yy-1.7,-z*.25-4],[xx+4,yy-1.7,-z*.25-4],[xx+4,yy+1.7,-z*.25-4],[xx-4,yy+1.7,-z*.25-4],[xx-4,yy-1.7,-z*.25-4],[xx-2,yy-2.4,-z*.25-4],[xx-1,yy-1.7,-z*.25-4]],WHITE*.4)
        for k in range(3):ring(m,[side*7.7+(k-1)*1.6,side*2.8,-3.8],.2,ACC,n=24)
    m=mesh('sydney_bars')
    for side in [-1,1]:
        for j in range(8):beam(m,[side*(4+j),-7,0],[side*(4+j),7,0],.07,C*.7)
        beam(m,[side*4,-7,0],[side*12,-7,0],.12,WHITE)
        beam(m,[side*4,7,0],[side*12,7,0],.12,WHITE)
    m=mesh('sydney_latch');m.box([0,0,0],(2.2,3.,.8),WHITE);ring(m,[0,0,.5],.5,ACC)
    for k in range(8):line(m,[[-1,1.3-k*.36,.6],[1,1.3-k*.36,.6]],C*.5)

    m=mesh('basilisk_coil')
    for strand in range(8):
        line(m,[[(10+.3*math.cos(strand))*math.cos(a),6.4*math.sin(a),-7+a*.45+.3*math.sin(strand)] for a in np.linspace(0,math.tau*2.5,350)],C*.55)
    for a in np.linspace(0,math.tau*2.5,100):
        p=np.array([10*math.cos(a),6.4*math.sin(a),-7+a*.45]);ring(m,p,.42,ACC*.5,sy=.7,n=18)
    m=mesh('basilisk_eye')
    for x in [-4.5,4.5]:
        for rr in [1.,1.3,1.5]:ring(m,[x,4.2,-1],rr,ACC*.8,sy=.5)
        beam(m,[x,3.7,-.9],[x,4.7,-.9],.06,WHITE)
    m=mesh('basilisk_reverse')
    for j in range(8):
        line(m,[[x,math.sin(x*.45+j)*.5-5.5,-6-j*.3] for x in np.linspace(-15,15,100)],ACC*.3)
        x=12-j*3;line(m,[[x,-4.8,-4],[x-.7,-5.5,-4],[x,-6.2,-4]],WHITE*.8)

    m=mesh('moon_chip');chip(m,[0,0,0],4.2)
    for side in [-1,1]:
        beam(m,[side*2,-2,0],[side*3.8,-4,0],.12,WHITE)
        for j in range(12):line(m,[[side*.4,-2,-.2],[side*(1+j*.15),-4-j*.24,-2]],ACC*.6)
    m=mesh('moon_market')
    for j in range(35):
        x=-15+j*.85;y=-5+j*.19+.8*math.sin(j*.8);h=.3+.6*abs(math.sin(j*2))
        m.box([x,y,-6],(.36,h,.17),C*.7 if j%3 else ACC*.7)
        line(m,[[x,y-h,-6],[x,y+h,-6]],WHITE*.5)
    m=mesh('moon_terrain')
    p=np.array([10,5,-10]);m.sphere(3.4,p,WHITE*.3,rings=9)
    for x,y,r in [(9,5,.6),(11,6,.4),(10,3.5,.45)]:ring(m,[x,y,-6.7],r,C*.7,sy=.5)
    m=mesh('omega_threads')
    for k in range(36):
        a=k*math.tau/36
        line(m,[[r*math.cos(a),r*.55*math.sin(a),-4-(17-r)*.8] for r in np.linspace(17,.4,90)],C*.5 if k%3 else ACC*.5)
    m=mesh('omega_focus');m.sphere(.65,[0,0,-16],WHITE*.7,rings=7)

    m=mesh('flops_towers')
    for side in [-1,1]:
        for z in range(6):
            for y in range(8):
                p=[side*(7.5+z*.8),-6+y*1.55,-3-z*2.5];chip(m,p,.9,C*.55)
    m=mesh('flops_gates')
    for j in range(30):
        a=j*math.tau/30;p=[12*math.cos(a),7*math.sin(a),-8]
        ring(m,p,.35,WHITE*.7,n=24)
        line(m,[p,[p[0]*.82,p[1]*.82,-15]],ACC*.4)

    m=mesh('safe_frame')
    for s in range(4):m.box([0,0,-4-s*.4],(27+s*.25,14+s*.25,.15),C*.5)
    for side in [-1,1]:
        for j in range(12):line(m,[[side*13,-6+j,-3.9],[side*11.5,-5.5+j,-3.9]],WHITE*.5)
    m=mesh('safe_stamp')
    for j in range(7):ring(m,[8,4,-2-j*.16],2.,ACC*.8)
    line(m,[[6.8,4,-1.9],[7.7,3.2,-1.9],[9.4,5.2,-1.9]],WHITE)
    m=mesh('safe_cracks')
    for side in [-1,1]:
        line(m,[[side*12,-7,-3],[side*10,-4,-2.9],[side*11,-2,-3],[side*7,1,-2.9],[side*8,3,-3],[side*4,7,-2.9]],ACC*.9)
        for j in range(8):line(m,[[side*(10-j*.7),-3+j,-3],[side*(12-j*.6),-4+j,-3]],ACC*.5)

    m=mesh('vonneumann_memory')
    for side in [-1,1]:
        for j in range(14):card(m,[side*10,-6.5+j,-6],5,.65,WHITE*.55)
    m=mesh('vonneumann_cpu');chip(m,[0,-4.8,-4],4.2)
    m=mesh('vonneumann_bus')
    for side in [-1,1]:
        for j in range(12):line(m,[[side*10,-6.5+j,-5.8],[side*6,-6.5+j,-5.8],[side*6,-4.8+j*.08,-3.5],[side*2.5,-4.8+j*.08,-3.5]],C*.65)
    m=mesh('neural_replacement')
    for k in range(10):
        x=-12+k*2.6
        for y in [-5.5,5.5]:
            ring(m,[x,y,-5],.35,ACC*.7,n=22)
            for j in [-2,0,2]:line(m,[[x,y,-5],[x+j,-y,-8]],ACC*.35)

    m=mesh('cdr_cells')
    for j in range(5):
        x=-11+j*5.2;m.box([x,4,-5],(3.8,2.2,.6),WHITE*.7)
        line(m,[[x,2.9,-4.65],[x,5.1,-4.65]],C*.8)
        ring(m,[x+1,4,-4.6],.18,ACC,n=22)
        line(m,[[x+1,4,-4.6],[x+3.3,4,-4.6],[x+2.8,4.4,-4.6]],ACC*.7)
        line(m,[[x-1,3.4,-4.6],[x-1,-3,-5]],C*.5)
        card(m,[x-1,-4,-5],2.,1.8,C*.75)
    m=mesh('cdr_head');ring(m,[-11,4,-4.5],2.1,ACC,sy=.7)
    beam(m,[-12.8,4,-4.4],[-9,4,-4.4],.04,WHITE)
    m=mesh('cdr_pointer')
    line(m,[[-15,-6,-3],[-7,-6,-3],[-7,1,-3],[-5.8,4,-4.3]],WHITE)
    line(m,[[-6.7,3.7,-4.3],[-5.8,4,-4.3],[-6.1,3.1,-4.3]],ACC)
    m=mesh('cdr_rest')
    for j in range(4):
        x=-5.8+j*5.2
        for k in range(5):line(m,[[x-2.1,5.4+k*.12,-5],[x+2.1,5.4+k*.12,-5]],ACC*.55)

    m=mesh('gato_lanes')
    for lane in range(4):
        y=-6+lane*4.
        for j in range(24):card(m,[-16+j*1.3,y,-7],.8,.5,C*.45)
        line(m,[[-17,y,-7],[9,y,-7],[13,0,-10]],ACC*.35)
    m=mesh('gato_lens')
    for r in [1,1.3,2.,2.2]:ring(m,[-10,5,-3],r,WHITE*.65)
    m=mesh('gato_hand')
    for j in range(4):
        x=5.5+j*1.6;beam(m,[x,-4,-4],[x,-1,-3],.2,WHITE*.7);beam(m,[x,-1,-3],[x-.4,1,-5],.14,C*.7)
    m.box([8,-5,-4],(7,2,1),C*.7)
    m=mesh('gato_pad')
    for r in [1.,1.2]:ring(m,[-10,-5,-3],r,C*.7)
    beam(m,[-11,-5,-2.8],[-9,-5,-2.8],.09,WHITE);beam(m,[-10,-6,-2.8],[-10,-4,-2.8],.09,WHITE)

    m=mesh('kill_desk')
    m.box([-7,-3,-5],(12,.5,5),WHITE*.65)
    for x in [-12,-2]:
        for z in [-7,-3]:beam(m,[x,-3,z],[x,-8,z],.1,C*.65)
    for j in range(9):line(m,[[4+j*.8,-7,-4],[4+j*.8,7,-4]],C*.5)
    m=mesh('kill_switch')
    for r in [1.8,2.,2.25]:ring(m,[-7,-2,-3],r,ACC,sy=.5)
    m.box([-7,-1.9,-3.2],(3.3,.7,1.5),ACC*.6)
    for k in range(14):line(m,[[-10,-4-k*.2,-4],[-4,-4-k*.2,-4]],C*.3)
    m=mesh('kill_vacation')
    for j in range(12):
        a=j*math.pi/11;line(m,[[8+4*math.cos(a),3+3*math.sin(a),-3],[8,3,-3]],WHITE*.65)
    beam(m,[8,3,-3],[8,-5,-3],.05,ACC)
    line(m,[[4,-6,-3],[6,-3,-3],[10,-5,-3],[11,-6,-3]],C*.8)
    m=mesh('fuse_cord')
    for k in range(4):line(m,[[x,-4+.8*math.sin(x*.5)+.08*math.cos(k),-3+.08*math.sin(k)] for x in np.linspace(-16,16,180)],C*.8)
    m=mesh('fuse_spark')
    for k in range(35):
        a=k*2.4;r=.6+(k%5)*.22;line(m,[[0,0,0],[r*math.cos(a),r*math.sin(a),(k%3-1)*.6]],ACC)

    m=mesh('mask_tokens')
    for row in [-1,1]:
        for j in range(13):
            if j%4!=1:card(m,[-15+j*2.5,row*5,-5],1.8,1.2,C*.6)
    m=mesh('mask_missing')
    for row in [-1,1]:
        for j in [1,5,9]:
            m.box([-15+j*2.5,row*5,-5],(1.9,1.3,.2),ACC*.55)
            for k in range(3):ring(m,[-15+j*2.5+(k-1)*.4,row*5,-4.8],.09,WHITE,n=12)
    m=mesh('mask_filled')
    for row in [-1,1]:
        for j in [1,5,9]:card(m,[-15+j*2.5,row*5,-4.8],1.7,1.1,WHITE*.8)

    m=mesh('loom_choice')
    card(m,[0,0,0],2.3,1.5,WHITE*.8)
    for side in [-1,1]:
        line(m,[[0,0,-.2],[side*2,side*1.8,-1.5],[side*4,side*3,-3]],ACC*.85)
        card(m,[side*4,side*3,-3],1.7,.9,C*.8)
    m=mesh('loom_tree')
    for side in [-1,1]:
        for level in range(5):
            count=2**level
            for j in range(count):
                x=side*(4+level*2.6);y=(j-(count-1)/2)*12/max(1,count)
                px=side*(4+(level-1)*2.6);py=((j//2)-((count//2)-1)/2)*12/max(1,count//2)
                if level:line(m,[[px,py,-3-(level-1)*2],[x,y,-3-level*2]],C*.55)
                card(m,[x,y,-3-level*2],1.,.45,WHITE*.55)
    m=mesh('loom_futures')
    for side in [-1,1]:
        for k in range(6):
            line(m,[[side*(4+j*2.6),3*math.sin((k+j)*1.7),-3-j*2] for j in range(5)],ACC*(.8 if k==2 else .2))

    m=mesh('show_frame')
    for side in [-1,1]:
        for j in range(22):line(m,[[side*(6+j*.45),-8,0],[side*(6+j*.45),8,0],[side*(6+j*.45),8,-3]],C*.45)
    beam(m,[-17,8,0],[17,8,0],.2,WHITE*.7)
    m=mesh('show_backstage')
    for side in [-1,1]:
        for j in range(8):
            x=side*(6+j*1.35)
            line(m,[[x,-8,-4],[x,5,-12],[x,8,-4]],ACC*.45)
            ring(m,[x,6,-6],.6,WHITE*.7,n=32)
        for j in range(8):beam(m,[side*8,-6+j*1.4,-10],[side*17,6-j*.7,-14],.05,C*.4)
    return out
