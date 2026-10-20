"""Scene-bound parts and finite actions; no looping foreground scan lines."""

from cdr_geometry import draw_cdr
from pair_director import pair_part_matrix

def draw_integrated(t,vp,hit,g):
    score=g['semantic_state'](t)
    if not score['active']:return
    np,math=g['np'],g['math'];ctx,gl=g['ctx'],g['gl'];tr,sc,rot=g['tr'],g['sc'],g['rot'];ease=g['ease']
    name=score['name'];u=score['u'];amp=score['exposure'];host=g['semantic_host']
    base=host(name,score['reference'],t,score['distance'],score['scale'])
    ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE);g['ms'].depth_mask=False;ctx.line_width=1.3
    def part(key,matrix=None,gain=1.,reveal=1.,collection='SEMANTIC'):
        model=pair_part_matrix(name,key,base if matrix is None else matrix,t,g=g)
        g[collection][key].draw(model,vp,t,0,0,-1,gain=gain*amp,reveal=reveal)
    def tf(key,matrix=None,gain=1.,reveal=1.):part(key,matrix,gain,reveal,'TRANSFORMER')
    def metal(key,matrix=None,gain=1.,reveal=1.):part(key,matrix,gain,reveal,'COHESIVE')
    def mounts(matrix=None,gain=.5):
        metal('mount_keel',matrix,gain);metal('mount_arms',matrix,gain*.8);metal('mount_harness',matrix,gain*.55)
    if name=='loss':
        for j,ref in enumerate([10.2,11.85]):
            b=base if j==0 else host('loss-fall',ref,t,18.,1.2)
            gain=1. if j==0 else float(ease((t-10.65)/.5))
            part('loss_mount',b,gain=.8*gain)
            part('loss_curve',b,gain=.70*gain,reveal=min(1.,.15+(t-9.08)/2.8))
    elif name=='omega':
        part('omega_threads',gain=1.15,reveal=.4+.6*u)
        part('omega_focus',base@tr(0,0,-16)@sc(3+u*8.5)@tr(0,0,16),gain=1.65)
    elif name in ['compute','gpu']:
        # One body, embedded cores and deep cooling parts share their supports.
        b=base@rot(-.26 if name=='gpu' else .18,1)
        metal('gpu_chassis',b,.72);metal('gpu_fins',b,1.0)
        metal('gpu_bus',b,.95);metal('gpu_core',b,1.3)
        metal('gpu_rear',b,.65);metal('gpu_packets',b,.62,reveal=.25+.75*float(ease(u/.7)))
        if name=='compute':
            metal('gpu_rear',b@tr(0,0,-21)@sc(1.15),.6)
            metal('gpu_bus',b@tr(0,0,-21)@sc(1.15),.5)
    elif name=='mlp':
        mounts(gain=.45);tf('nn_layers',gain=1.0);tf('nn_connections',gain=.60)
        # One forward pass, one reverse pass, then one repeat: no phase wrap.
        forward=float(ease((t-73.96)/1.8));back=float(ease((t-75.9)/.52));repeat=float(ease((t-76.42)/.82))
        tf('nn_forward',gain=.65 if t<75.9 else .25+.45*repeat,reveal=forward)
        tf('nn_backward',gain=.6 if t<76.42 else .28,reveal=back)
        # A retraced physical rail, not a second copy of the whole network.
        # The camera follows these SAME banks forward, backward and again.
        if t>76.42:tf('nn_forward',gain=.85,reveal=repeat)
    elif name=='vonneumann':
        old=float(ease((t-79.8)/.7));mounts(gain=.45)
        part('memory_banks',gain=.95*(1-old*.48));part('memory_bus',gain=.8*(1-old*.65))
        metal('gpu_rear',gain=.5);metal('gpu_bus',gain=.55,reveal=.15+.85*old)
        metal('gpu_core',gain=.7,reveal=.2+.8*old)
    elif name=='cdr':
        draw_cdr(t,vp,hit,g)
    elif name=='gato':
        mounts(gain=.5);part('gato_channels',gain=.9,reveal=.4+.6*float(ease((t-89.995)/1.8)))
    elif name=='killswitch':
        # Retain the original switch and its physical empty chair.  Its clip
        # factory closes the retreat, rather than displaying a holiday icon.
        shut=float(ease((t-100.16)/1.7))
        g['METAPHOR']['paperclip_swarm'].draw(base@tr(0,0,-24+shut*8)@sc(.9),vp,t,0,0,-1,gain=amp*.65,reveal=.05+.95*shut)
    elif name=='fuse':
        part('fuse_cord',gain=.95);x=-16+32*u;y=-4+.8*math.sin(x*.5)
        part('fuse_spark',base@tr(x,y,-2.9)@sc(.65+hit*.35),gain=1.1)
    elif name=='transformer':
        stage=min(4,max(0,np.searchsorted([110.4,111.15,112.42,113.26],t)))
        mounts(gain=.43);tf('tf_structure',gain=.7)
        tf('tf_token_belt',gain=1.0 if stage==0 else .55);tf('tf_positions',gain=.9 if stage==0 else .4)
        for j,key in enumerate(['tf_q_branch','tf_k_branch','tf_v_branch']):
            tf(key,gain=1.0 if stage==1 else .55,reveal=float(ease((t-110.35-j*.12)/.25)))
        tf('tf_attention_heads',gain=1.0 if stage==2 else .65)
        tf('tf_attention_weights',gain=1.1 if stage==2 else .45,reveal=float(ease((t-110.8)/.65)))
        tf('tf_concat',gain=1.1 if stage==3 else .45,reveal=float(ease((t-111.6)/.7)))
        tf('tf_residual',gain=.9 if stage>=3 else .35)
        tf('tf_mlp',gain=1.0 if stage==3 else .45,reveal=float(ease((t-112.1)/.65)))
        tf('tf_decoder',gain=.6 if stage<4 else 1.,reveal=.25+.75*float(ease((t-112.42)/.7)))
        tf('tf_output',gain=.9,reveal=float(ease((t-112.6)/.5)))
        if t>=113.26:
            b=host('decoder-exit',114.75,t,19.,1.45)
            tf('tf_decoder',b,.95);tf('tf_output',b,.9)
    elif name in ['loom','branch_seed']:
        mounts(gain=.5);part('loom_branches',gain=1.05,reveal=.35+.65*u)
        part('loom_ports',gain=.75,reveal=.35+.65*u)
        part('loom_selected',gain=.95,reveal=float(ease(u/.75)))
    elif name=='masked':
        b=host('masked-rack',128.5,t,18.,1.25)
        mounts(b,.5);part('mask_tokens',b,.85)
        part('mask_missing',b,.6*(1-u));part('mask_filled',b,.85,reveal=float(ease((t-128.4)/.8)))
    elif name=='unknown':
        if t<133.43:base=host('unknown-pass',133.1,t,20.,1.5)
        close=float(ease((t-134.2)/1.5));mounts(gain=.4)
        for j in range(2):
            b=base@tr(-j*3.,j*.6,-j*9.)@rot(j*.22,1)
            g['EXTRA_MET']['window'].draw(b,vp,t,0,close,53,gain=amp*(.8-j*.3))
    elif name=='show':
        reveal=float(ease((t-138.)/1.7));part('show_backstage',gain=.85,reveal=.1+.9*reveal)
        if t>139.43:part('show_backstage',host('show-flight',140.65,t,20.,1.45),.9)
    ctx.line_width=1.2;ctx.disable(gl.BLEND);g['ms'].depth_mask=True
