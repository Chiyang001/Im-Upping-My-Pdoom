"""Additional line sculptures and a finite semantic exposure score."""
def metaphor_state(t):
    cues=(('chinese',26.06,29.68,6),('shoggoth',29.68,31.83,7),
          ('sharpturn',80.68,84.78,20),('paperclip',95.91,98.845,23),
          ('orthogonal',104.54,109.4,26),('chinchilla',115.,116.88,28),
          ('feedback',120.18,122.54,29),('recursive',127.96,131.46,31),
          ('unknown',132.22,135.68,32))
    for name,a,b,i in cues:
        if a<=t<b:
            u=(t-a)/(b-a)
            return dict(active=True,name=name,start=a,end=b,index=i,u=u,
                        exposure=min(1.,(t-a)/.10,(b-t)/.10))
    return dict(active=False,name=None,u=0.,exposure=0.)

def build_extra(Mesh,np,math,C,WHITE,ACC):
    out={n:Mesh() for n in ['constraint','capability','hollow','data','dense',
                           'robot','arm','offspring','window']}
    m=out['constraint']
    for z in np.linspace(-11,6,13):
        m.box((0,0,z),(14,10,.16),C*.65)
        for x in [-7,7]:
            for y in np.linspace(-5,5,21):m.line([[x,y,z],[x*1.04,y,z-.8]],C*.38)
    for x in [-7,7]:
        for y in [-5,5]:m.line([[x,y,7],[x,y,-14]],WHITE*.45)
    m=out['capability']
    for j in range(8):
        z=4-j*2.1
        for k in range(12):
            a=k*math.tau/12;p=np.array([2.5*math.cos(a),2.5*math.sin(a),z])
            m.sphere(.10,p,ACC,rings=3)
            for kk in [-1,1]:
                aa=a+kk*.32;q=[2.9*math.cos(aa),2.9*math.sin(aa),z-2.1];m.line([p,q],ACC*.65)
    m=out['hollow']
    for side in [-1,1]:
        for j in range(15):
            m.box((-8,0,-2-j*.18),(8+j*.06,8+j*.06,.04),WHITE*.35)
            for y in [-4,4]:m.line([[-12,y,-2-j*.18],[-4,y,-2-j*.18]],C*.6)
    m=out['data']
    for river in range(4):
        angle=river*math.pi/2
        for j in range(26):
            z=5-j*.8;r=10-(j/26)*5
            p=[6+r*math.cos(angle),r*math.sin(angle),z]
            m.box(p,(.45,.3,.08),C*.75)
            m.line([p,np.array(p)+[-.3,.16,-.3]],ACC*.5)
    m=out['dense']
    for x in range(-3,4):
        for y in range(-3,4):
            for z in range(-3,4):
                p=np.array([6+x*.5,y*.5,-3+z*.5]);m.box(p,(.22,.22,.22),WHITE*.5)
                if x<3:m.line([p,p+[.5,0,0]],C*.45)
                if y<3:m.line([p,p+[0,.5,0]],C*.45)
    m=out['robot']
    for z in [2,0,-3]:
        m.box((0,0,z),(15,10,.5),C*.45)
        for side in [-1,1]:
            m.box((side*7.5,-3,z),(1.1,4,2),WHITE*.7)
    for x in [-8,8]:
        for yy in np.linspace(-5,5,28):m.line([[x,yy,3],[x+.8,yy,3],[x+.8,yy,-8]],C*.4)
    m=out['arm']
    joints=[np.array([-8,-3,2]),np.array([-5,3,-2]),np.array([-2,2,-8])]
    for a,b in zip(joints,joints[1:]):
        for off in [[.12,0,0],[-.12,0,0],[0,.12,0],[0,-.12,0]]:m.line([a+off,b+off],WHITE)
        for p in np.linspace(0,1,16):m.circle(.24,a*(1-p)+b*p,2,C*.6,24)
    for p in joints:m.sphere(.5,p,C*.7,rings=7)
    for side in [-1,1]:m.line([joints[-1],[-2+side*.6,1.5,-9],[-2+side*.2,1.2,-10]],ACC)
    m=out['offspring']
    for j in range(3):
        z=-j*3;rad=5.0+.25*j
        for k in range(7):
            r=rad+k*.065;m.line([[r*math.cos(a),r*.7*math.sin(a),z] for a in np.linspace(0,math.tau,140)],C*.7 if k%3 else WHITE*.8,closed=True)
        for a in np.linspace(0,math.tau,18):
            m.line([[rad*math.cos(a),rad*.7*math.sin(a),z],[(rad+.8)*math.cos(a),(rad+.8)*.7*math.sin(a),z-2]],ACC*.6)
    m=out['window']
    for j in range(12):m.box((0,0,-j*.15),(16+j*.08,9+j*.08,.05),C*.5)
    # Empty dark centre: the observer is never shown a claimed secret image.
    for side in [-1,1]:
        for j in range(36):
            y=side*(.3+j*.14);m.line([[-8,y,0],[8,y,0],[8,y,-.4],[-8,y,-.4]],WHITE*.55)
    return out
