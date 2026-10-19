from pathlib import Path
p=Path('v4/render.py');s=p.read_text(encoding='utf-8-sig')
# Make glyphs deeply structural and engrave controlled parallel hatches inside the outlines.
s=s.replace("m.line(p2,color*.42,closed=True)","m.line(p2,color*.55,closed=True)\n   if depth>.55:\n    for zz in np.linspace(0,depth,max(3,int(depth*5)))[1:-1]:\n     pp=p.copy();pp[:,2]=zz;m.line(pp,color*.25,closed=True)")
# Curved and multi-plane sentence-specific layouts replace the five shared row styles.
pos=s.index('def norm(x):')
s=s[:pos]+'''# Semantic placement edits are intentionally explicit, one score per sentence.
S[2]=[('There was a sudden',25,-1,2,-5,.12,-.18,0),('drop',12,5,-.5,0,.1,-.48,0),('in your training loss',24,0,-3,-4,.1,0,0)]
S[3]=[("Now I'm your servant",21,-1,-3.8,-1,-.25,0,0),("and you're my boss",29,0,3.3,-3,.15,0,0)]
S[6]=[('Trapped in the',20,0,4,-6,0,0,0),('Chinese room',25,-7,-.7,-5,1.05,0,0),('with a bag of shrooms',27,6,-2,-6,-1.05,0,0)]
S[7]=[('See through the',19,-6,4.4,0,.2,-.08,0),("shoggoth's",25,0,.4,-3,.2,0,8),('lies',12,5,-3,1,-.2,0,0)]
S[10]=[("But now the",17,-7,4,1,.12,-.08,0),("singularity's",29,0,0,-4,0,0,8.5),('begun',14,0,-3,-5,0,0,0)]
S[13]=[('Sydney,',23,0,1,-4,0,0,0),('please let me free',28,0,-4,-5,0,0,0)]
S[14]=[("I'm upping my",18,-7,4,0,.4,-.17,0),('P(doom)',25,-2,.2,-3,.55,.15,0),('I hear the basilisk boom',29,0,-3.5,-2,-.25,.08,18)]
S[15]=[('NVDA to the moon',28,-1,1,-3,-.1,0,0),("the Omega Point's",21,5,4,-8,-.35,0,0),('coming soon',19,7,-2,-6,-.4,0,0)]
S[17]=[('"That was safe enough"',25,0,2,-2,0,0,10),('we reckoned',19,0,-2.5,0,-.15,0,0)]
S[18]=[('Forward MLP,',24,0,4,-3,0,0,0),('backward, repeat',26,0,-4,-3,.12,0,0)]
S[20]=[('Sharp left turn',25,0,1,0,0,0,0),('and there you are',25,0,-.5,0,1.570796,0,0)]
S[21]=[('Without a single',28,0,3,-2,0,0,0),('CDR',21,0,-4,-1,0,0,0)]
S[24]=[('Killswitch guys on',27,-1,3,0,.2,0,0),('PTO',11,-8,-2,-1,.6,0,0),("now there's nowhere",29,0,1,-8,0,0,0),('left to go',19,5,-3,-5,-.3,0,0)]
S[26]=[('Orthogonality',25,0,1,-3,0,0,0),('thesis',15,-5,-1,-2,0,1.570796,0),('blues',19,5,-3,-4,-1.570796,0,0)]
S[30]=[("I'm upping my",19,-7,4,-1,.35,-.1,0),('P(doom)',26,0,0,-4,0,0,0),('just as foretold by Loom',29,0,-3,-2,-.25,.08,0)]
S[31]=[('From masked',18,-5,4,-2,.15,0,0),('pre-training days',24,0,1,-6,-.1,0,0),('to recursive self-upgrade',27,0,-2.7,-10,.15,0,0)]
RX={(2,0):-.75,(2,2):-1.05,(6,2):-.15,(13,1):-.8,(18,0):-.75,(18,1):.75,(21,0):-.18,(26,0):-.35,(30,1):-.55,(31,0):-.1}
DEPTH={0:.5,1:.65,2:.5,3:2.2,4:1.7,5:2.8,6:1.4,7:.5,8:.5,9:.75,10:1.8,11:1.2,12:.6,13:3.3,14:1.5,15:1.4,16:4.0,17:1.2,18:1.5,19:3.5,20:2.8,21:3.7,22:.7,23:2.6,24:3.3,25:.7,26:.8,27:3.5,28:2.4,29:2.,30:.7,31:4.,32:1.3,33:4.2}
''' +s[pos:]
s=s.replace('for sr in spec:\n  phrase,width,x,y,z,ry,rz,rad=sr;', 'for rowid,sr in enumerate(spec):\n  phrase,width,x,y,z,ry,rz,rad=sr;')
s=s.replace('depth=.2+.04*size)', 'depth=DEPTH[idx])')
s=s.replace("wx=cx+ww/2;cx+=ww+contour(' ')[1]*size;words.append((GPU(wm),wx,timing[wi],ww));wi+=1", """wx=cx+ww/2;cx+=ww+contour(' ')[1]*size
   # Bend every vertex, not just each word's origin, so the letter strokes form a real spatial surface.
   for v in wm.l:
    gx=v[0]+wx
    if rad:v[0]=rad*math.sin(gx/rad);v[2]+=rad*(1-math.cos(gx/rad))
    else:v[0]=gx
    if idx==15 and rowid==0:v[1]+=.023*(gx+11)**2-3;v[2]+=-.25*(gx+11)-3
    if idx==30 and rowid==1:v[2]+=.35*math.sin(gx*.75+v[1]*1.4)
   # The letter's own strokes become columns/rails, not a separate title floating in front.
   if idx in [1,3,6,13,16,19,21,23,24,27,28,29,31,33]:
    for vv in wm.l[::max(4,len(wm.l)//16)]:
     pp=np.array(vv[:3]);qq=pp.copy();qq[2]-=DEPTH[idx]*1.6;wm.line([pp,qq],C*.27)
   words.append((GPU(wm),wx,timing[wi],ww));wi+=1""")
s=s.replace("for i in range(34):", "for i in range(34):")
# Camera rigs vary in elevation, azimuth, lens and shot distance. Topology turns use their own camera.
pos=s.index('# Wide coverage')
s=s[:pos]+'''CAM[0]=([5,3,18],[-5,1,23],[0,0,-3],-.12,52)
CAM[1]=([-12,5,22],[9,-1,20],[0,0,-4],.14,53)
CAM[2]=([11,11,22],[3,4,20],[0,-1,-4],-.16,56)
CAM[3]=([-8,-8,24],[7,7,24],[0,0,-3],.12,57)
CAM[4]=([0,1,21],[3,-1,29],[0,0,-4],.04,55)
CAM[5]=([-11,3,24],[9,-2,26],[0,0,-5],-.14,58)
CAM[6]=([0,1,16],[2,0,10],[0,0,-12],.08,66)
CAM[7]=([-11,4,23],[8,-2,23],[1,0,-3],-.18,55)
CAM[8]=([0,-1,23],[0,3,29],[0,0,-5],.02,52)
CAM[9]=([-8,3,25],[8,3,25],[0,0,-4],0,49)
CAM[10]=([9,12,23],[0,3,19],[0,0,-6],-.17,58)
CAM[11]=([-7,-3,24],[5,4,21],[0,0,-8],.16,57)
CAM[12]=([9,4,25],[-7,5,21],[0,0,-3],-.1,55)
CAM[13]=([-10,2,24],[8,1,23],[0,0,-6],.12,58)
CAM[14]=([11,-5,25],[-8,7,24],[-2,0,-5],-.17,58)
CAM[15]=([-12,3,24],[9,10,23],[1,1,-5],-.1,58)
CAM[16]=([8,-7,25],[-7,8,24],[0,0,-5],.1,58)
CAM[17]=([-3,11,24],[6,0,23],[0,0,-4],-.12,56)
CAM[18]=([-8,9,24],[8,-7,23],[0,0,-4],.1,56)
CAM[19]=([9,-7,26],[-6,6,25],[0,0,-5],-.08,57)
CAM[21]=([8,-4,24],[-5,4,23],[0,0,-4],.13,56)
CAM[22]=([-10,3,24],[9,-2,24],[0,0,-5],-.14,57)
CAM[23]=([9,-1,26],[-7,5,29],[0,0,-5],.12,58)
CAM[24]=([-11,-5,25],[9,4,24],[0,0,-6],-.12,59)
CAM[25]=([-10,5,24],[10,-3,24],[0,0,-4],.14,56)
CAM[26]=([1,6,25],[16,8,18],[0,0,-4],-.08,57)
CAM[27]=([-9,6,25],[8,-4,24],[0,0,-4],.13,58)
CAM[28]=([5,-5,26],[-7,7,24],[0,0,-7],-.12,59)
CAM[29]=([-10,10,27],[9,2,24],[0,0,-5],.16,57)
CAM[30]=([11,6,27],[-10,-2,25],[0,0,-5],-.14,58)
CAM[31]=([-4,1,25],[4,4,19],[0,0,-9],.1,60)
CAM[33]=([0,1,27],[12,6,24],[0,0,-5],.12,57)
CUTS=[]
for i,r in enumerate(lines):
 aa,bb=r[:2];cand=[x for x in rhythm['impacts'] if aa+(bb-aa)*.42<x['t']<aa+(bb-aa)*.72]
 CUTS.append(max(cand,key=lambda x:x['strength'])['t'] if cand else (aa+bb)*.5)
''' +s[pos:]
s=s.replace('alt=1 if u>.59 and idx not in [9,20,32] else 0','alt=1 if t>CUTS[idx] and idx not in [0,9,20,32] else 0')
s=s.replace("eye+=np.array([(-1)**idx*.75*alt,.35*alt,-.5*alt])", "eye+=np.array([(-1)**idx*1.8*alt,.65*alt,-1.0*alt])")
s=s.replace("sharp*.15,math.cos(t*61)*sharp*.12,-sharp*.3", "sharp*.3,math.cos(t*61)*sharp*.22,-sharp*.6")
s=s.replace("fov+hit*.35", "fov-hit*1.8")
s=s.replace("typemodel=tr(x,y,z)@rot(ry,1)@rot(rz,2)", "typemodel=tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((idx,j),0),0)")
s=s.replace("arx=wx if not rad else rad*math.sin(wx/rad);arz=0 if not rad else rad*(1-math.cos(wx/rad));anga=0 if not rad else -wx/rad\n   wm=typemodel@tr(arx,0,arz)@rot(anga,1)", "wm=typemodel")
s=s.replace("since=t-wt;reveal=float(np.clip((since+.04)/.32,0,1));gain=.15 if since<-.04 else 1.25+max(0,1-since/.28)*.7", "since=t-wt;reveal=float(np.clip((since+.04)/.22,0,1));gain=.34 if since<-.04 else 1.25+max(0,1-since/.28)*.7")
s=s.replace("gpu.draw(wm,vp,t,hit,0,-1,gain,reveal if since>=-.04 else 1)", """if since>=-.04 and reveal<1:
    ctx.depth_func='<=';gpu.draw(wm,vp,t,hit,0,-1,.44,1);gpu.draw(wm,vp,t,hit,0,-1,gain,reveal);ctx.depth_func='<'
   else:gpu.draw(wm,vp,t,hit,0,-1,gain,1)""")
s=s.replace("if t>141.2:\n  outro=", "if t>141.2:\n  ms.clear(.002,.005,.009,1,depth=1)\n  outro=")
s=s.replace("c+=glow*.7", "c+=glow*.85")
s=s.replace("c=mix(c,p,paper)", "c=mix(c,p,paper)")
# Preserve the continuous lyric text while future words serve as visible structural guides.
p.write_text(s,encoding='utf-8')
