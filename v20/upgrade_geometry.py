"""A masked-data archive which physically fabricates its own successor.

All detail is machined GL_LINES.  The mechanism is deliberately asymmetric:
archive leaves feed a masking slit, a training comb drives a folded output
gantry, and three differently built successors open beside the actual flight.
There are no nested rings, orbiting robots, textures, or screen-space symbols.
"""


def build_upgrade(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = [np.asarray(c, float) for c in (C, WHITE, ACC)]
    out = {k: Mesh() for k in (
        'archive', 'leaf', 'mask_left', 'mask_right', 'mask_slit',
        'trainer', 'training_comb', 'training_seed', 'day_chain',
        'extractor', 'extractor_head', 'fabricator', 'fold_arm',
        'successor_a', 'successor_b', 'successor_c', 'cascade_rail',
        'arc', 'rivet', 'surface_0', 'surface_1', 'surface_2', 'surface_3')}

    def line(m, pts, col=C, closed=False):
        m.line(np.asarray(pts, float), col, closed=closed)

    def beam(m, a, b, r=.10, col=C):
        a, b = np.asarray(a, float), np.asarray(b, float)
        v = b-a; v /= max(np.linalg.norm(v), 1e-9)
        ref = np.array([0., 1., 0.]) if abs(v[1]) < .8 else np.array([1., 0., 0.])
        p = np.cross(v, ref); p /= max(1e-9, np.linalg.norm(p))
        q = np.cross(v, p)
        corners = [r*(i*p+j*q) for i,j in ((1,1),(-1,1),(-1,-1),(1,-1))]
        for o in corners: line(m, [a+o,b+o], col)
        for f in [0., .25, .5, .75, 1.]:
            line(m, [a+f*(b-a)+o for o in corners], col*.55, True)

    def plate(m, center, width, height, depth=.2, col=C):
        x,y,z=center
        m.box([x,y,z],[width,height,depth],color=col)
        for dx in [-width*.5+.22,width*.5-.22]:
            for dy in [-height*.5+.22,height*.5-.22]:
                m.circle(.07,pos=[x+dx,y+dy,z+depth*.55],color=WHITE*.52,n=8)

    # An oblique archive canopy and an open floor conveyor occupy the full
    # frame in a low tracking shot; parts have real parallax at different Z.
    m=out['archive']
    for x in [-20.,-13.,-6.,1.,8.,15.,22.]:
        beam(m,[x,-7,11],[x,-7,-40],.16,C*.38)
        beam(m,[x,-7,-40],[x,12,-40],.15,C*.42)
        beam(m,[x,12,-40],[x-4,15,12],.10,C*.3)
        for z in np.arange(-38,14,3):
            line(m,[[x,-7,z],[x+5,-7,z-2.4]],C*.28)
    for z in [9.,2.,-5.,-12.,-19.,-26.,-33.]:
        beam(m,[-20,-7,z],[-20,9,z],.14,C*.42)
        beam(m,[22,-7,z],[22,11,z],.14,C*.4)
        beam(m,[-20,9,z],[-9,12,z],.10,C*.4)
        beam(m,[22,11,z],[14,13,z],.10,C*.4)
        for j in range(9):
            x=-19+j*.75
            line(m,[[x,-5.8,z],[x,7.4,z],[x+.2,7.6,z]],C*.25)
            line(m,[[-x+2,-5.8,z],[-x+2,9.2,z]],C*.20)
    for z in np.linspace(9,-40,66):
        beam(m,[-13,-4.8,z],[13,-4.8,z],.055,C*.30)
    # One visible downstream loom connects the training output, lift cradle
    # and seed printer.  The story is a connected fabrication line, rather
    # than three unrelated apparatuses appearing at successive cuts.
    route=np.array([[8.,-1.7,-20.],[8.,-1.7,-22.],
                    [5.,-1.7,-24.],[5.,-1.7,-29.],[-4.,-1.7,-34.]])
    for j in range(11):
        off=np.array([(j-5)*.065,0.,0.])
        line(m,route+off,C*(.48 if j==5 else .23))
    for a,b in zip(route[:-1],route[1:]):
        beam(m,a+[0,-.45,0],b+[0,-.45,0],.10,C*.42)
    # One clipped-corner archive leaf, including embedded token strips.
    m=out['leaf']
    for z in [-.12,.12]:
        line(m,[[-2.4,-1.5,z],[1.85,-1.5,z],[2.4,-.95,z],
                [2.4,1.5,z],[-2.4,1.5,z]],WHITE*.67,True)
    for x in np.linspace(-2.1,1.8,14):
        for y in [-1.,-.45,.1,.65,1.1]:
            line(m,[[x,y,.14],[x+.18,y,.14]],C*.65)
    for k in range(9):
        line(m,[[-2.1,-1.3+k*.3,-.13],[-2.1+k*.14,-1.3+k*.3,-.13]],C*.35)
    # Opposed shutters cover only the data-bearing region; they withdraw on
    # MASKED, leaving the physical training sample visible behind them.
    for key,sign in [('mask_left',-1),('mask_right',1)]:
        m=out[key]
        for j in range(7):
            x=sign*(.25+j*.43)
            plate(m,[x,0,0],.38,5.7,.22,C*.76)
            for y in [-2.3,-1.1,.2,1.5,2.4]:
                line(m,[[x-.12,y,.13],[x+.12,y+.16,.13]],WHITE*.38)
        beam(m,[sign*.3,-3.25,-.15],[sign*3.3,-3.25,-.15],.12,C*.55)
        beam(m,[sign*.3,3.25,-.15],[sign*3.3,3.25,-.15],.12,C*.55)
    m=out['mask_slit']
    for x in [-3.7,3.7]:
        beam(m,[x,-4.0,-.5],[x,4.0,-.5],.18,C*.64)
        for y in np.linspace(-3.6,3.6,13):
            line(m,[[x-.35,y,-.5],[x+.35,y,-.5]],WHITE*.38)
    for y in [-4.,4.]:beam(m,[-4,y,-.5],[4,y,-.5],.16,C*.6)
    # Training is not a magic sphere: physical traces between three combs,
    # ending in a folded output board which the extractor can actually lift.
    m=out['trainer']
    for z in [-3.,-6.,-9.]:
        for x in np.linspace(-5.8,5.8,17):
            beam(m,[x,-2.8,z],[x,2.8,z],.025,C*.28)
        for y in [-3.,3.]:beam(m,[-6.5,y,z],[6.5,y,z],.13,C*.55)
    for k in range(40):
        x=-5.6+(k%10)*1.24;y=-2.4+(k//10)*1.6
        a=[x,y,-3];b=[x*.7+1.2,y*.7,-6];c=[x*.45-1.2,y*.45,-9]
        line(m,[a,b,c],C*.32)
        line(m,[[x,-2.9,-2.8],[x,2.9,-2.8]],C*.22)
    m=out['training_comb']
    beam(m,[-6.4,0,0],[6.4,0,0],.12,WHITE*.64)
    for x in np.linspace(-6,6,41):
        line(m,[[x,-.6,0],[x,.6,0]],C*.64)
        if int((x+6)*10)%3==0:
            line(m,[[x,.6,0],[x,.8,-.6]],WHITE*.7)
    m=out['training_seed']
    for j in range(6):
        z=-j*.4
        line(m,[[-.2,-.2,z],[.2,-.2,z],[.2,.2,z],[-.2,.2,z]],WHITE*.8,True)
    # The days counter is a continuous accumulating notched chain, attached
    # to the training carriage; not a floating row of pictograms.
    m=out['day_chain']
    for j in range(48):
        x=j*.32
        line(m,[[x,-.22,0],[x,.22,0],[x+.14,.22,0]],C*.65)
        if j%6==0:beam(m,[x,-.5,0],[x,.5,0],.025,WHITE*.65)
    for y in [-.4,.4]:line(m,[[0,y,0],[15.3,y,0]],C*.4)
    m=out['extractor']
    for x in [-5.,5.]:
        beam(m,[x,-7,-4],[x,13,-4],.18,C*.55)
        beam(m,[x,-7,-4],[x,-7,-15],.16,C*.4)
        for y in np.arange(-6,13,.6):
            line(m,[[x-.2,y,-4],[x+.2,y,-4]],C*.33)
    for y in [-7.,13.]:beam(m,[-5,y,-4],[5,y,-4],.18,C*.5)
    m=out['extractor_head']
    plate(m,[0,0,0],8.,.7,.6,C*.65)
    for x in [-3.5,3.5]:
        beam(m,[x,0,0],[x,-2,1],.13,WHITE*.65)
        line(m,[[x,-2,1],[x*.78,-2.5,1.2]],WHITE*.8)
    # A seed printer with an open diagonal cantilever.  Successors gain
    # truss depth, boards and extra print axes, rather than scale-only clones.
    m=out['fabricator']
    for x in [-6.,6.]:
        beam(m,[x,-4,2],[x,-4,-11],.2,C*.5)
        beam(m,[x,-4,-11],[x,6,-11],.18,C*.65)
        beam(m,[x,6,-11],[x,8,-1],.12,C*.5)
    for y,z in [(-4,2),(-4,-11),(6,-11),(8,-1)]:
        beam(m,[-6,y,z],[6,y,z],.15,C*.58)
    for z in np.linspace(-10,1,12):
        line(m,[[-6,-3.7,z],[6,-3.7,z]],C*.33)
    m=out['fold_arm']
    beam(m,[0,0,0],[0,4,-5],.18,C*.78)
    beam(m,[0,4,-5],[0,1,-10],.16,WHITE*.65)
    for d in [-.4,.4]:
        line(m,[[d,1,-10],[d,0,-11.2]],WHITE*.75)
    # The three stages intentionally have different topology/silhouettes.
    for j,key in enumerate(['successor_a','successor_b','successor_c']):
        m=out[key];w=7.+j*3.0;h=5.5+j*2.6;depth=7.+j*4.
        for side in [-1,1]:
            x=side*w
            for z in [0,-depth]:
                beam(m,[x,-h,z],[x,h,z],.16+j*.025,C*.62)
                beam(m,[x,-h,z],[side*(w+3),-h-2,z-2],.12,C*.46)
            beam(m,[x,h,0],[x,h,-depth],.16,C*.62)
            beam(m,[x,-h,0],[x,-h,-depth],.16,C*.5)
            for n in range(7+j*4):
                z=-depth*n/(6+j*4)
                line(m,[[x,-h,z],[x-side*1.3,h,z-1]],C*.30)
            # Attached folded circuit wings flank, never block, flight axis.
            for n in range(4+j*2):
                z=-depth*(n+.3)/(4+j*2)
                plate(m,[x+side*1.7,0,z],3.,h*1.5,.15,C*.48)
                for y in np.linspace(-h*.65,h*.65,12):
                    line(m,[[x+side*.4,y,z+.1],[x+side*3,y,z+.1]],C*.27)
        # Deliberately open central span; only high/low lintels bridge it.
        for y in [-h,h]:
            beam(m,[-w,y,0],[w,y,0],.15,C*.6)
            beam(m,[-w,y,-depth],[w,y,-depth],.15,C*.45)
        if j>=1:
            for s in [-1,1]:beam(m,[s*w,h,-depth],[s*(w-2),h+3,-depth*.4],.12,WHITE*.5)
        if j==2:
            for s in [-1,1]:
                for q in [-1,1]:beam(m,[s*w,q*h,-depth],[s*(w+4),q*(h+3),-depth-6],.12,C*.5)
    m=out['cascade_rail']
    for x in [-12.,12.,-19.,19.]:
        for y in [-9.,9.]:
            beam(m,[x,y,10],[x*1.5,y*1.5,-95],.11,C*.4)
    for z in np.arange(8,-95,-3):
        line(m,[[-19,-9,z],[-12,-9,z],[-12.5,-9.4,z-1]],C*.3)
        line(m,[[19,9,z],[12,9,z],[12.5,9.4,z-1]],C*.3)
    m=out['arc']
    line(m,[[-3,0,0],[-1.4,.55,-.3],[-.6,-.25,-.7],
            [.4,.4,-1.1],[1.8,-.3,-1.7],[3,0,-2]],WHITE*.75)
    out['rivet'].circle(.12,color=WHITE*.7,n=10)
    # Lyric support plates share these physical planes with the inscriptions.
    # Open corners avoid a subtitle rectangle while retaining real rivets.
    for k,(width,height) in enumerate([(13.,3.7),(17.,4.),(6.,3.),(14.,3.8)]):
        m=out['surface_'+str(k)]
        for sx in [-1,1]:
            for sy in [-1,1]:
                x,y=sx*width*.5,sy*height*.5
                line(m,[[x-sx*.9,y,0],[x,y,0],[x,y-sy*.8,0]],C*.55)
                m.circle(.07,pos=[x-sx*.25,y-sy*.25,0],color=WHITE*.6,n=8)
        for x in [-width*.5,width*.5]:
            beam(m,[x,-height*.5,-.15],[x,-height*.5-1.8,-1.],.05,C*.3)
    return out
