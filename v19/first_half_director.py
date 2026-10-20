"""Word-motivated, finite mechanisms mounted along the existing camera route."""
from first_half_score import first_half_state, phrase_state
from first_half_geometry import optimization_path


def draw_first_half(t,vp,hit,g):
    score=first_half_state(t)
    if not score['active']:return
    ctx,gl=g['ctx'],g['gl'];np,math=g['np'],g['math']
    tr,rot,sc=g['tr'],g['rot'],g['sc'];ease=g['ease'];host=g['semantic_host']
    name=score['name'];u=score['u'];amp=score['exposure']
    base=host('first-'+name,score['reference'],t,score['distance'],score['scale'])
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE);g['ms'].depth_mask=False;ctx.line_width=1.3
    def part(key,matrix=None,gain=1.,reveal=1.,collection='FIRST_HALF'):
        g[collection][key].draw(base if matrix is None else matrix,vp,t,0,0,-1,gain=gain*amp,reveal=reveal)
    def organic(key,matrix=None,gain=1.,reveal=1.):part(key,matrix,gain,reveal,'ORGANIC')
    def orbital(key,matrix=None,gain=1.,reveal=1.):part(key,matrix,gain,reveal,'ORBITAL')
    def extra(key,matrix=None,gain=1.,reveal=1.):part(key,matrix,gain,reveal,'EXTRA_MET')
    if name=='circuits':
        part('circuit_cables',gain=.75);part('circuit_synapses',gain=.95)
        # The same terminated conductors strain under a finite nervous pulse.
        nervous=float(ease((t-6.9)/.12))*(1.-float(ease((t-8.3)/.5)))
        pulse=(.5+.5*math.sin((t-6.9)*math.tau*5.6))*nervous
        part('circuit_contacts',gain=.88+.45*pulse,reveal=.18+.82*float(ease((t-6.)/1.55)))
    elif name=='control':
        transfer=float(ease((t-14.4)/1.3))
        part('control_gantry',gain=.8);part('control_reins',gain=.85)
        part('control_terminal',base@tr(0,-transfer*2.,0)@rot(-transfer*.12,0),gain=1.05)
        part('control_gripper',base@tr(0,transfer*1.8,0),gain=1.1)
    elif name=='dialogue':
        part('dialogue_housing',gain=.6);part('dialogue_cards',gain=.75)
        transit=float(ease((t-17.1)/2.9))
        part('dialogue_shuttle',base@tr(-11+22*transit,1.8,-2),gain=1.05)
        bite=float(ease((t-20.22)/.46));escape=float(ease((t-21.28)/.75))
        part('dialogue_latch',base@np.diag([1-bite*.24+escape*.36,1,1,1]),gain=.8)
    elif name=='risk':
        pressure=float(ease((t-22.19)/1.43));after=float(ease((t-23.62)/.30))
        m=base@np.diag([1-pressure*.2+after*.8,1-pressure*.13+after*.65,1,1])
        part('risk_iris',m,gain=.95*(1-after));part('risk_filaments',m,gain=1.3*(1-after),reveal=.12+.88*pressure)
    elif name=='foom':
        for j,ref in enumerate([24.68,25.57]):
            b=host('foom-forge-'+str(j),ref,t,22.,1.05+j*.22)
            growth=float(ease((t-(24.14+j*.48))/(1.-j*.18)))
            part('evolution_forge',b,gain=.68,reveal=.3+.7*growth)
            part('evolution_arms',b,gain=.95,reveal=.3+.7*growth)
            part('evolution_child',b@tr(0,growth*1.7,0),gain=1.15,reveal=growth)
    elif name=='shrooms':
        # The bag is cargo in the exit bay, in FRONT of the post-word-pass lens.
        b=base@tr(6.0,2.4,2.)
        cargo=b@tr(0,0,-4.*float(ease((t-27.8)/1.5)))
        organic('organic_mount',cargo,gain=1.05);organic('shroom_bag',cargo,gain=1.5)
        organic('shroom_stems',cargo,gain=.95);organic('shroom_caps',cargo,gain=.80)
        organic('shroom_gills',cargo,gain=.85+.15*float(ease((t-29.0)/.3)))
        organic('shroom_mycelium',cargo,gain=.45,reveal=.35+.65*float(ease((t-28.2)/.8)))
        part('exit_sorter',b,gain=.9)
        part('exit_mycelium',b,gain=.8,reveal=.2+.8*float(ease((t-28.1)/.9)))
        part('exit_canopy',b,gain=.7,reveal=.2+.8*float(ease((t-28.2)/.9)))
    elif name=='stable':
        part('training_bench',gain=.75);part('training_steps',gain=.95)
        # Three reproducible strokes, rather than an inert laboratory tableau.
        cycle=max(0.,min(3.,(t-38.76)/.72))
        down=.5-.5*math.cos(cycle*math.tau)
        part('training_piston',base@tr(0,-down*2.2,0),gain=.95)
    elif name=='singularity':
        for j,ref in enumerate([42.48,43.72]):
            b=host('singularity-forge-'+str(j),ref,t,21.,1.05+j*.20)
            phase=float(ease((t-(41.5+j*.6))/(1.5-j*.3)))
            part('evolution_forge',b,gain=.65);part('evolution_arms',b,gain=1.0)
            part('evolution_child',b@tr(0,phase*1.5,-phase*3),gain=1.1,reveal=.15+.85*phase)
    elif name=='optimization':
        b=base
        if t>=47.44:b=host('optimization-exit',48.1,t,22.,1.15)
        part('optimization_land',b,gain=.8);part('optimization_track',b,gain=1.0)
        p=float(ease((t-45.5)/3.));point=optimization_path(p)
        part('optimization_cart',b@tr(*point)@rot(p*4,1),gain=1.45)
    elif name=='atoms':
        b=base
        if t<49.4:b=host('atoms-entry',49.1,t,23.,1.05)
        part('atom_assembler',b,gain=.75);part('atom_lattice',b,gain=.9)
        progress=float(ease((t-50.16)/1.9))
        for j in range(2):
            x=-9+18*progress;yy=3.3 if j==0 else -4.4;zz=-4-j*5
            part('atom_cluster',b@tr(x,yy,zz)@rot(progress*math.pi*.5,1),gain=1.3)
        extra('arm',b@tr(-1,0,-1)@sc(.9),gain=.85)
    elif name=='sydney':
        b=base if t>=53.885 else host('sydney-entry',53.6,t,21.,1.1)
        part('dialogue_housing',b,gain=.7);part('dialogue_cards',b,gain=.95)
        # One turn-taking reply reaches the latch; the release opens once.
        reply=float(ease((t-54.0)/2.2));opened=float(ease((t-57.56)/.74))
        part('dialogue_shuttle',b@tr(-11+21*reply,-2.5,-3-reply*7),gain=1.0)

        if t<56.20:part('dialogue_latch',b@np.diag([1+opened*.65,1,1,1]),gain=.85)
    elif name=='basilisk':
        b=base@tr(-6.0,-1.7,0.)
        organic('basilisk_anchors',b,gain=.9);organic('basilisk_body',b,gain=1.55)
        organic('basilisk_head',b,gain=1.85)
        snap=float(ease((t-61.84)/.35))
        organic('basilisk_jaw',b@tr(0,-snap*.32,0),gain=1.65)
    elif name=='orbital':
        base=base@tr(3.,.8,2.)
        orbital('orbital_mount',gain=.65);orbital('orbital_rail',gain=.9)
        orbital('market_ascent',gain=1.0);orbital('wafer_dies',gain=1.05)
        orbital('moon_surface',gain=.50);orbital('moon_craters',gain=1.05);orbital('moon_rim',gain=.85)
        # A payload follows the same rising rail once; the Moon stays fixed.
        lift=float(ease((t-62.4)/1.5))
        knots=np.array([[-17.,-8.6,1.1],[-16.,-4.7,-5.3],[-14.2,.2,-12.5],[-10.5,6.,-20.2],[-5.8,8.65,-23.],[.1,9.25,-22.4],[5.4,8.65,-19.],[6.3,7.75,-15.6]])
        index=min(6,int(lift*7));blend=min(1.,lift*7-index)
        point=knots[index]*(1-blend)+knots[index+1]*blend
        b=base@tr(*(point+[0,.55,0]))
        part('orbital_sled',b,gain=.9)
        g['COHESIVE']['gpu_core'].draw(b@tr(0,.45,0)@sc(.42)@tr(-10.75,-.5,.8),vp,t,0,0,-1,gain=amp*.85)
    elif name=='inspection':
        part('inspection_jig',gain=.95)
        approval=float(ease((t-70.08)/.62));strain=float(ease((t-71.08)/.65))
        m=base@tr(-10.5,-1.3-.55*approval,1.)@rot(strain*.17,2)@tr(10.5,1.3,-1.)
        part('inspection_sample',m,gain=1.0)
        part('inspection_plant',gain=.65,reveal=.4+.6*float(ease((t-68.8)/2.2)))
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True


def phrase_camera(t,eye,target,roll,fov,*,g):
    """Hard coverage cuts at real two-word groups, with directed XYZ trucks.

    Camera offsets use the authored view's axes; all geometry hosts remain
    frozen to authored_frame_view. This is real parallax, never moving a
    prop with the current camera. The renderer keeps its lexical FOV guard.
    The actual approach and crossing of existing word flights remain exact.
    Post-crossing cuts are tangential to the physical word plane, preserving
    its signed camera depth and the one-way crossing. FREE and lunar chase
    have their own specialised camera directors.
    """
    cue=phrase_state(t)
    if not cue['active']:return None
    flight=g['sample_flight_camera'](t) if g.get('sample_flight_camera') else dict(active=False)
    if flight['active']:
        crossing=flight.get('crossing_time')
        if not crossing or not flight.get('has_crossed') or cue['start']<crossing+.18:return None
    np=g['np'];math=g['math'];u=cue['u'];serial=cue['serial']
    eye=np.array(eye,float);target=np.array(target,float)
    forward=target-eye;forward/=max(1e-9,np.linalg.norm(forward))
    right=np.cross(forward,[0.,1.,0.]);right/=max(1e-9,np.linalg.norm(right))
    up=np.cross(right,forward);basis=np.array([right,up,forward]).T
    name=cue.get('name') if cue.get('silent') else first_half_state(t).get('name')
    side=1. if serial%2==0 else -1.
    # Each noun receives its own camera grammar: see circuit depth laterally,
    # authority from below, a jaw from its shoulder, stability from overhead.
    if name in ['iris_rim','iris_exit']:
        a=(side*2.4,1.0,1.0);b=(-side*1.8,-1.2,3.8);bank=.065*side;zoom=-3.
    elif name in ['approval_seam','approval_exit']:
        a=(side*2.7,-1.8,1.1);b=(-side*2.1,.8,3.2);bank=-.060*side;zoom=-2.
    elif 1.42<=t<5.7 or 31.83<=t<38.19:
        a=(side*1.8,.7,-.6);b=(-side*1.4,-.6,1.1);bank=.030*side;zoom=.5
    elif name=='circuits':
        a=(side*3.6,1.2,-.6);b=(-side*2.2,-.8,1.7);bank=.045*side;zoom=-1.
    elif name=='control':
        a=(side*2.5,-2.4,-.5);b=(-side*1.7,.2,2.2);bank=-.035*side;zoom=2.
    elif name=='dialogue':
        a=(side*3.1,1.2,-.5);b=(-side*2.5,-1.0,2.7);bank=.045*side;zoom=1.
    elif name=='risk':
        a=(side*2.7,-2.2,-1.0);b=(side*.5,-.3,2.2);bank=.025*side;zoom=3.
    elif name=='stable':
        a=(side*3.0,.4,-1.2);b=(-side*2.1,-1.4,1.2);bank=-.040*side;zoom=1.
    elif name=='optimization':
        a=(side*3.2,-1.4,-.5);b=(-side*1.7,.6,2.1);bank=.040*side;zoom=2.
    elif name=='inspection':
        a=(side*2.8,2.1,-1.0);b=(-side*1.8,-.7,1.2);bank=-.035*side;zoom=-1.
    else:
        a=(side*2.6,1.4,-.8);b=(-side*1.8,-.8,1.8);bank=.035*side;zoom=1.
    # Constant motion with a short acceleration departure. Cuts alternate a
    # foreground edge instead of returning to a camera-centred orbit.
    p=u*.72+u*u*.28;offset=np.array(a)*(1-p)+np.array(b)*p
    if flight['active'] and g.get('flight_pose'):
        pose=g['flight_pose'](t)
        # No translation along the crossed plane's normal: the 17 original
        # word passes retain exactly their old signed depth after crossing.
        tangent=np.array(pose['right'])*offset[0]+np.array(pose['up'])*offset[1]
        eye+=tangent;target+=tangent
    else:
        eye+=basis@offset
        target+=basis@np.array([offset[0]*.07,offset[1]*.06,0.])
    return dict(eye=eye,target=target,roll=roll+bank*(1.-.5*u),
                fov=min(102.,max(38.,fov+zoom+2.2*u)),
                phase='pair_'+str(cue['line_index'])+'_'+str(cue['group']),
                words=cue['words'],cut=cue['start'])
