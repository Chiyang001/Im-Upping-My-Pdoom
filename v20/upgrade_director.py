"""Fast, word-motivated archive -> masking -> self-fabrication direction."""
import math

START, CAMERA_END, END = 127.90, 130.56, 132.22
WORD_CUES = (127.90,128.08,128.56,129.18,129.60,129.98,130.56)


def ease(u):
    u=max(0.,min(1.,float(u)))
    return u*u*(3.-2.*u)


def sample_upgrade(t):
    if not START <= t < END:
        return {'active':False,'camera_active':False}
    phase = ('archive_feed' if t<128.08 else 'mask_release' if t<128.56
             else 'training_comb' if t<129.18 else 'days_index'
             if t<129.60 else 'vertical_extraction' if t<129.98
             else 'recursive_fabrication' if t<130.56 else 'successor_cascade')
    return dict(active=True,camera_active=t<CAMERA_END,phase=phase,
                mask=ease((t-128.08)/.34),training=ease((t-128.56)/.50),
                days=ease((t-129.18)/.35),extract=ease((t-129.60)/.34),
                recursive=ease((t-129.98)/.50),upgrade=ease((t-130.56)/.65))


def upgrade_host(t,g):
    return g['semantic_host']('upgrade-fabricator',129.18,t,21.,1.18)


def upgrade_token_surface(index,t,*,g):
    """Fixed machine-mounted planes; root fits the original word geometry.

    Returns None for SELF-UPGRADE, whose authored one-way word crossing is
    retained.  No plane depends on the current camera pose.
    """
    np,tr,rot=g['np'],g['tr'],g['rot']
    gid=0 if index<=1 else 1 if index<=3 else 2 if index==4 else 3
    if index>=6:return None
    p,yaw=([[-6.,0.,4.],-.22] if gid==0 else [[8.,2.,-8.],.18]
           if gid==1 else [[5.,8.,-17.],-.16] if gid==2 else [[-4.,6.,-24.],-.20])
    return dict(matrix=upgrade_host(t,g)@tr(*p)@rot(yaw,1),
                width=[12.,16.,5.3,13.][gid],group=gid)


def upgrade_camera(t,eye,target,roll,fov,*,g):
    if not START<=t<CAMERA_END:return None
    np=g['np'];base=upgrade_host(t,g)
    # Each phrase has a different physical job and velocity direction.  Cuts
    # at PRE-TRAINING and TO retain the feed/print direction on screen.
    shots=(
      (127.90,128.56,(-16.,6.,20.),(-8.,2.,16.),(-6.,0.,2.),(-6.,0.,2.),-.12,.10,66.),
      (128.56,129.60,(5.,6.,10.),(14.,-.5,6.),(8.,2.,-8.),(8.,2.,-8.),.12,-.12,70.),
      (129.60,129.98,(11.,12.,1.),(7.,15.,-4.),(5.,8.,-17.),(5.,8.,-17.),-.1,.17,68.),
      (129.98,130.56,(1.,10.,-8.),(-10.,4.,-9.),(-4.,6.,-24.),(-4.,6.,-24.),.18,-.15,70.),
    )
    shot=next(s for s in shots if s[0]<=t<s[1]);a,b,p0,p1,q0,q1,r0,r1,lens=shot
    u=(t-a)/(b-a)
    # Linear travel is deliberate: smoothstep alone would park on every word.
    p=np.array(p0)*(1-u)+np.array(p1)*u
    q=np.array(q0)*(1-u)+np.array(q1)*u
    # DAYS triggers an accelerating side shear in the same continuous shot.
    if 129.18<=t<129.60:
        kick=ease((t-129.18)/.42);p += np.array([3.1*kick,-1.8*kick,-2.2*kick])
    def point(v):return (base@np.r_[v,1.])[:3]
    return dict(eye=point(p).tolist(),target=point(q).tolist(),
                roll=r0*(1-u)+r1*u,fov=lens,phase=sample_upgrade(t)['phase'])


def draw_upgrade(t,vp,hit,g):
    s=sample_upgrade(t)
    if not s['active']:return
    np,math,tr,rot,sc=g['np'],g['math'],g['tr'],g['rot'],g['sc']
    ctx,gl=g['ctx'],g['gl'];base=upgrade_host(t,g)
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE);g['ms'].depth_mask=False;ctx.line_width=1.35
    # The final bridge remains fully exposed through the cut.  A fade here
    # made the fast camera outrun the apparatus into a near-black frame.
    amp=1.
    archive_gain=(1.-ease((t-130.56)/.38))
    def draw(key,matrix=None,gain=1.,reveal=1.):
        g['UPGRADE'][key].draw(base if matrix is None else matrix,vp,t,0,0,-1,
                               gain=gain*amp,reveal=max(0.,min(1.,reveal)))
    draw('archive',gain=1.08*archive_gain)
    # Ordered conveyor feed: the same samples enter the masking/training slit.
    for j in range(11):
        travel=(t-START)*9.
        z=12.-j*5.2-travel
        draw('leaf',base@tr(-7.+j*.72,-1.2+.15*(j%2),z)@rot(-.22,1),
             gain=1.05*archive_gain)
    maskbase=base@tr(-6,0,-2)
    draw('mask_slit',maskbase,gain=.86*archive_gain)
    for key,sign in [('mask_left',-1),('mask_right',1)]:
        draw(key,maskbase@tr(sign*4.2*s['mask'],0,-.5*s['mask']),gain=.92*archive_gain)
    trainbase=base@tr(8,1,-11)
    draw('trainer',trainbase,gain=1.20*archive_gain)
    sweep=ease((t-128.56)/1.04)
    draw('training_comb',trainbase@tr(0,-2.7+5.4*sweep,-3.-6*sweep),gain=1.2*archive_gain)
    for j in range(7):
        q=max(0.,min(1.,(t-128.56-j*.045)/.62))
        draw('training_seed',trainbase@tr(-5.4+j*1.8,-2.4+4.8*q,-3.-6*q),gain=1.5*archive_gain)
    draw('day_chain',trainbase@tr(-7.5,-4.4,-1.)@rot(-.12,2),gain=.95*archive_gain,reveal=.04+.96*s['days'])
    if 129.18<=t<130.08:
        route=np.array([[8.,-1.7,-20.],[8.,-1.7,-22.],
                        [5.,-1.7,-24.],[5.,-1.7,-29.],[-4.,-1.7,-34.]])
        run=4.*ease((t-129.18)/.80);j=min(3,int(run));f=min(1.,run-j)
        p=route[j]*(1-f)+route[j+1]*f
        draw('training_seed',base@tr(*p),gain=1.7*archive_gain)
    extbase=base@tr(5,1,-24)
    draw('extractor',extbase,gain=.82*archive_gain)
    draw('extractor_head',extbase@tr(0,-3.+13.*s['extract'],0),gain=1.05*archive_gain)
    draw('leaf',extbase@tr(0,-5.+13.*s['extract'],1.2)@sc(1.5),gain=1.2*archive_gain)
    fabbase=base@tr(-4,1,-34)
    draw('fabricator',fabbase,gain=.90*archive_gain)
    for side in [-1,1]:
        draw('fold_arm',fabbase@tr(side*5.6,1,0)@rot(side*(.55-.85*s['recursive']),2),gain=1.05*archive_gain)
    # A successor is printed on the seed's output rail before the camera
    # enters the existing word flight.  The next, larger topology appears
    # farther along THAT flight, creating causal spatial progression.
    draw('successor_a',fabbase@tr(0,0,-15),gain=.95*archive_gain,
         reveal=.02+.98*s['recursive'])
    for index in [0,2,4,5]:
        surf=upgrade_token_surface(index,t,g=g)
        draw('surface_'+str(surf['group']),surf['matrix']@tr(0,0,-.2),gain=.65*archive_gain)
    # World-stationed cascade, aligned to the actual authored self-upgrade
    # flight.  Its open centre lets the lyric plane pass through the lens.
    flybase=g['metaphor_station']('SELF UPGRADE',131.48,t,9.)
    cascade=ease((t-130.30)/.26)
    draw('cascade_rail',flybase,gain=.82*cascade)
    for j,key in enumerate(['successor_a','successor_b','successor_c']):
        grow=ease((t-(130.46+j*.20))/.33)
        matrix=flybase@tr((j-1)*1.8,j*1.6,-j*24.)@rot((j-1)*.085,2)
        draw(key,matrix,gain=(.94+j*.12)*cascade,reveal=.025+.975*grow)
        if grow>0:
            draw('fold_arm',matrix@tr(-8-j*3.,3,1)@rot(-.45+grow*.8,2),gain=cascade)
            draw('fold_arm',matrix@tr(8+j*3.,-3,-2)@rot(math.pi+.35-grow*.65,2),gain=cascade)
    # A fixed future fabrication bridge catches the continuing WHAT flight.
    # Placement is sampled once at an authored reference, not from the live
    # camera, so rails and wing boards retain real parallax as it passes.
    if t>=131.46:
        exitbase=g['metaphor_station']('SELF UPGRADE',132.16,t,13.)
        emergence=ease((t-131.46)/.24)
        draw('cascade_rail',exitbase,gain=.95*emergence)
        draw('successor_c',exitbase@rot(-.16,2),gain=1.24*emergence)
        draw('successor_b',exitbase@tr(4.,-3.,-31.)@rot(.12,2),gain=1.06*emergence)
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True
