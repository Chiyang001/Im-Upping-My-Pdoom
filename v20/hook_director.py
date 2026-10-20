"""Four 1.42-second cold-open microshots of one fabricated ignition machine.

Everything is line geometry. The seed travels on the same rail in all four
cuts, energises the induction collar and passes into the iris. There is no
fade from black and no displayed text before the first sung word.
"""
import math as _math

HOOK_END = 1.42
HOOK_CUTS = (.24, .69, 1.14, HOOK_END)


def _ease(u):
    u=max(0.,min(1.,u));return u*u*(3.-2.*u)


def seed_point(t):
    u=_ease(t/1.12)
    return (-8.*(1.-u)**2, 1.7*_math.sin(_math.pi*u), -6.-18.5*u)


def sample_hook(t):
    if not 0. <= t < HOOK_END:return dict(active=False)
    shot=0 if t<.24 else 1 if t<.69 else 2 if t<1.14 else 3
    starts=(0.,.24,.69,1.14);ends=(.24,.69,1.14,HOOK_END)
    u=(t-starts[shot])/(ends[shot]-starts[shot])
    return dict(active=True,shot=shot,u=u,seed=seed_point(t),
                energised=_ease((t-.22)/.70),opening=_ease((t-.91)/.36),
                # Frame zero is already a luminous close shot.
                exposure=1.,flash=max(0.,1.-abs(t-.918)/.045)*.12)


def hook_camera(t,*,np):
    s=sample_hook(t)
    if not s['active']:return None
    u=s['u'];p=np.array(s['seed']);shot=s['shot']
    def mix(a,b):return np.array(a,float)*(1-u)+np.array(b,float)*u
    if shot==0:
        # Macro: bearings, rail teeth and the charged capsule fill the frame.
        eye=p+mix((1.8,.8,2.5),(1.2,.38,2.1));target=p+np.array([0.,0.,-.38])
        roll=-.10+.16*u;fov=52.-3.*u
    elif shot==1:
        # A lateral truck makes the rail, seed and rear fixtures shear apart.
        eye=p+mix((-5.5,3.4,5.0),(-3.7,1.5,3.0));target=p+np.array([1.,-.2,-2.0])
        roll=.11-.16*u;fov=65.+3.*u
    elif shot==2:
        # Low reverse angle watches the real seed overtake the induction collar.
        eye=mix((4.8,-3.7,-15.0),(2.8,-1.8,-19.8))
        target=p+np.array([0.,.1,-2.0]);roll=-.16+.12*u;fov=68.+3.*u
    else:
        # The last shot enters the iris on axis and matches the sung-eye cut.
        # End at the lip: crossing the front blade here puts every nearby
        # etched ring behind the lens for the last pre-vocal frame. The
        # match cut to the sung iris supplies the next physical depth step.
        eye=mix((1.8,.65,-19.0),(.12,.05,-24.0))
        target=np.array([0.,0.,-31.0]);roll=.13*(1.-u);fov=76.-8.*u
    return dict(eye=eye,target=target,roll=roll,fov=fov,phase='hook_'+str(shot))


def build_hook(Mesh,np,math,C,WHITE,ACC):
    """Machined rail, coil and iris; eight bounded line-only GPU batches."""
    out={}
    def part(name):m=Mesh();out[name]=m;return m
    def line(m,p,c=C,closed=False):m.line(p,c,closed)
    def ring(m,p,r,c=C,n=64):m.circle(r,p,2,c,n)
    def box(m,p,size,c=C):m.box(p,size,c)
    def cable(m,p,r=.06,c=C,n=4):
        p=np.array(p,float)
        for k in range(n):
            a=k*math.tau/n;off=np.array([math.cos(a)*r,math.sin(a)*r,0.])
            line(m,p+off,c*(1. if k==0 else .45))
    rail=part('rail');chamber=part('chamber');collar=part('collar')
    iris=part('iris');seed=part('seed');current=part('current')
    blade=part('blade');sparks=part('sparks')
    # Two curved rails share the actual capsule path, with teeth and tie rods.
    path=[np.array(seed_point(1.12*j/95)) for j in range(96)]
    for side in [-1,1]:
        for y in [-.6,.6]:
            cable(rail,[p+[side*1.15,y,0] for p in path],.055,C*.8)
        for j in range(0,96,3):
            p=path[j];box(rail,p+[side*1.25,-.2,0],(.32,1.75,.18),WHITE*.45)
            line(rail,[p+[side*1.25,.75,.1],p+[side*2.5,.75,.1],p+[side*2.5,-2.9,.1]],C*.35)
    # Foreground members are finite machine housing, not decorative world fog.
    for z in np.linspace(1.,-35.,17):
        box(chamber,(0,0,z),(26,17,.22),C*.19)
        for side in [-1,1]:
            box(chamber,(side*10.9,-6.8,z),(.6,1.8,.8),C*.36)
            for y in [-5.,5.]:ring(chamber,(side*10.9,y,z+.2),.19,WHITE*.38,n=12)
    for x in [-13.,-11.2,11.2,13.]:
        for y in [-8.5,8.5]:cable(chamber,[[x,y,2],[x,y,-36]],.08,C*.26)
    # Deeply layered induction coil at the end of the rail.
    for z,r in [(-18.0,6.0),(-18.5,6.3),(-19.0,6.0),(-21.4,6.0),(-22.0,6.3)]:
        for d in [0.,.16]:ring(collar,(0,0,z),r+d,C*.55)
    for a in np.linspace(0,math.tau,36,endpoint=False):
        c,s=math.cos(a),math.sin(a)
        for r in [5.9,6.35]:line(collar,[[r*c,r*s,-18.],[r*c,r*s,-22.]],C*.48)
        box(collar,(6.7*c,6.7*s,-20.),(.42,.42,2.8),WHITE*.35)
    for j in range(10):
        z=-25.-j*.64;r=6.2-j*.27
        ring(iris,(0,0,z),r,WHITE*(.67-j*.038))
        ring(iris,(0,0,z+.1),r+.13,C*.28)
        for a in np.linspace(0,math.tau,24,endpoint=False):
            p=np.array([r*math.cos(a),r*math.sin(a),z])
            line(iris,[p,p+[.08*math.cos(a),.08*math.sin(a),-.64]],C*.35)
    # One local iris blade is instanced twelve times around real bearings.
    for r in [2.35,2.5,5.4,5.65]:
        line(blade,[[r*math.cos(a),r*math.sin(a),0.] for a in np.linspace(-.08,.38,24)],WHITE*.55)
    for a in [-.08,.12,.38]:
        line(blade,[[r*math.cos(a),r*math.sin(a),0.] for r in np.linspace(2.35,5.65,12)],C*.52)
    for j in range(10):
        a=-.06+j*.043
        line(blade,[[r*math.cos(a),r*math.sin(a),.04] for r in np.linspace(3.,5.5,14)],C*.22)
    # Capsule: longitudinal shell, etched seams, internal three-axis seed.
    for z,r in [(-.8,.44),(-.5,.65),(.5,.65),(.8,.44)]:ring(seed,(0,0,z),r,WHITE*.9,n=36)
    for a in np.linspace(0,math.tau,12,endpoint=False):
        line(seed,[[.44*math.cos(a),.44*math.sin(a),-.8],[.65*math.cos(a),.65*math.sin(a),-.5],
                   [.65*math.cos(a),.65*math.sin(a),.5],[.44*math.cos(a),.44*math.sin(a),.8]],WHITE*.7)
    for r in [.18,.28]:ring(seed,(0,0,.83),r,ACC*.72,n=28)
    for a in np.linspace(0,math.tau,9,endpoint=False):
        line(seed,[[.33*math.cos(a),.33*math.sin(a),-.8],[.33*math.cos(a),.33*math.sin(a),.8]],C*.65)
    # Fine turned seams and captive sockets make the opening macro hold up
    # at native 1080p; all details belong to the capsule's machined shell.
    for z in np.linspace(-.46,.46,15):ring(seed,(0,0,z),.651,C*.30,n=48)
    for a in np.linspace(0,math.tau,24,endpoint=False):
        line(seed,[[.653*math.cos(a),.653*math.sin(a),-.43],
                   [.653*math.cos(a),.653*math.sin(a),.43]],C*.26)
        for z in [-.53,.53]:
            p=np.array([.627*math.cos(a),.627*math.sin(a),z])
            line(seed,[p+[.025,0,0],p+[0,.025,0],p+[-.025,0,0],p+[0,-.025,0]],WHITE*.48,True)
    # Energised wire is a fixed physical winding, not a travelling red overlay.
    line(current,[[6.02*math.cos(a),6.02*math.sin(a),-18.-4*j/719]
                  for j,a in enumerate(np.linspace(0,math.tau*10,720))],WHITE*.8)
    for j in range(24):
        a=j*math.tau/24;r=2.2+(j%4)*.8
        line(sparks,[[r*math.cos(a),r*math.sin(a),-25.],[(r+.45)*math.cos(a),(r+.45)*math.sin(a),-26.3]],WHITE*.75)
    return out


def draw_hook(t,vp,hit,g):
    s=sample_hook(t)
    if not s['active']:return
    ctx,gl=g['ctx'],g['gl'];np=g['np'];tr,rot=g['tr'],g['rot']
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE);g['ms'].depth_mask=False
    ctx.line_width=1.25;identity=np.eye(4)
    def part(key,m=identity,gain=1.):g['HOOK'][key].draw(m,vp,t,0,0,-1,gain=gain)
    part('chamber');part('rail',gain=1.05);part('collar',gain=1.05);part('iris',gain=1.1)
    part('seed',tr(*s['seed'])@rot(t*1.8,2),gain=1.9)
    part('current',gain=.16+1.0*s['energised'])
    opening=s['opening']
    for j in range(12):
        a=j*_math.tau/12
        # Blades move about their own fixed bearing to reveal the deep throat.
        m=tr(0,0,-24.9)@rot(a,2)@tr(5.3,0,0)@rot(-opening*.62,2)@tr(-5.3,0,0)
        part('blade',m,gain=.95)
    part('sparks',gain=.15+.7*s['energised'])
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True
