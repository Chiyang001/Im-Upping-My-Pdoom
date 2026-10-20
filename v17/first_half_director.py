"""Word-motivated, finite mechanisms mounted along the existing camera route."""
from first_half_score import first_half_state
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
        part('circuit_contacts',gain=.95,reveal=.18+.82*float(ease((t-6.)/1.55)))
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
        organic('organic_mount',b,gain=1.05);organic('shroom_bag',b,gain=1.5)
        organic('shroom_stems',b,gain=.95);organic('shroom_caps',b,gain=.80)
        organic('shroom_gills',b,gain=.85+.15*float(ease((t-29.0)/.3)))
        organic('shroom_mycelium',b,gain=.45,reveal=.35+.65*float(ease((t-28.2)/.8)))
        part('exit_sorter',b,gain=.9)
        part('exit_mycelium',b,gain=.8,reveal=.2+.8*float(ease((t-28.1)/.9)))
        part('exit_canopy',b,gain=.7,reveal=.2+.8*float(ease((t-28.2)/.9)))
    elif name=='stable':
        part('training_bench',gain=.75);part('training_steps',gain=.95)
        down=.5-.5*math.cos(float(ease((t-38.9)/1.8))*math.tau)
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
        part('dialogue_latch',b@np.diag([1+opened*.65,1,1,1]),gain=.85)
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
        part('inspection_jig',gain=.95);part('inspection_sample',gain=1.0)
        part('inspection_plant',gain=.65,reveal=.4+.6*float(ease((t-68.8)/2.2)))
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True
