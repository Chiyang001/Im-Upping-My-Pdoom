"""Procedural fractured plates and near-field trusses; every face is an edge."""
def build_ruptures(Mesh,np,math,C,WHITE,ACC):
    rng=np.random.default_rng(110319)
    ribs=Mesh();plates=Mesh()
    for z in np.linspace(-36,25,16):
        for side in [-1,1]:
            x=side*(8.2+rng.uniform(0,3.2));y=rng.uniform(-2,2)
            pts=np.array([[x,-8+y,z],[x,-4+y,z+1.4],[x+side*3.5,y,z-2],[x,5+y,z+1.8],[x,9+y,z]])
            for off in [0,.12,.27]:
                ribs.line(pts+[side*off,0,-off],WHITE*.65 if off==0 else C*.35)
            for j in range(4):
                a=pts[j];b=pts[j+1]
                for p in np.linspace(.1,.9,5):
                    q=a*(1-p)+b*p;ribs.line([q,q+[side*.38,.14,-.16]],ACC*.75)
        for side in [-1,1]:
            ribs.line([[-13,side*9,z],[0,side*6,z-4],[13,side*9,z]],C*.7)
    for j in range(86):
        a=j*math.tau/86+rng.uniform(-.025,.025)
        radial=np.array([math.cos(a),math.sin(a)*.72,0.])
        tangent=np.array([-math.sin(a),math.cos(a)*.72,0.])
        inner=radial*rng.uniform(3.3,6.5)+[0,0,rng.uniform(-2,2)]
        outer=radial*rng.uniform(14,24)+[0,0,rng.uniform(-9,12)]
        p=np.array([inner,outer+tangent*rng.uniform(.15,1.7),outer-tangent*rng.uniform(.1,.6)])
        plates.line(p,WHITE*(1.1 if j%5==0 else .6),closed=True)
        for k in range(1,5):
            q=p*(1-k*.065)+p.mean(axis=0)*k*.065
            plates.line(q,C*.28 if j%3 else ACC*.36,closed=True)
        plates.line([p[0],p[0]+[0,0,.42],p[1]+[0,0,.42],p[1]],ACC*.8)
    return {'ribs':ribs,'faults':plates}
