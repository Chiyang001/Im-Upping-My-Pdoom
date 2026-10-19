from pathlib import Path
p=Path('v4/render.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('def textmesh(s,size=1,color=WHITE,depth=.22):','def textmesh(s,size=1,color=WHITE,depth=.22,style=-1):')
s=s.replace("  x+=adv*size\n return m,width", """  # True woven glyphs and paperclip link glyphs use the font outline as geometry, not as a texture.
  if style==30 and cs:
   for vertical in [False,True]:
    coords=np.concatenate(cs)*size+[x,0];lo=coords[:,int(not vertical)].min();hi=coords[:,int(not vertical)].max()
    for scan in np.arange(lo,hi,max(.08,size*.055)):
     crossings=[]
     for cc in cs:
      cc=cc*size+[x,0]
      if vertical:cc=cc[:,::-1]
      for aa,bb in zip(cc,np.roll(cc,-1,axis=0)):
       if (aa[1]<=scan<bb[1]) or (bb[1]<=scan<aa[1]):crossings.append(aa[0]+(scan-aa[1])*(bb[0]-aa[0])/(bb[1]-aa[1]))
     crossings.sort()
     for aa,bb in zip(crossings[::2],crossings[1::2]):
      pts=[[aa,scan,depth+.02],[bb,scan,depth+.02]]
      if vertical:pts=[[q[1],q[0],depth+.035] for q in pts]
      m.line(pts,C*.8 if vertical else WHITE*.7)
  if style==23:
   for cc in cs:
    cc=cc*size+[x,0]
    for j in range(0,len(cc),max(2,len(cc)//15)):
     aa=cc[j];bb=cc[(j+1)%len(cc)];v=bb-aa;ln=np.linalg.norm(v)
     if ln<1e-5:continue
     v=v/ln;nn=np.array([-v[1],v[0]]);pts=[]
     for th in np.linspace(0,math.tau*1.8,20):
      pp=aa+v*(.14*math.cos(th))+nn*(.06*math.sin(th));pts.append([*pp,depth+.04])
     m.line(pts,C*.9)
  x+=adv*size
 return m,width""")
s=s.replace('depth=DEPTH[idx])','depth=DEPTH[idx],style=idx if rowid==1 and idx in [23,30] else -1)')
s=s.replace('5:2.8','5:6.5').replace('14:1.5','14:3.0').replace('23:2.6','23:4.5')
# Fix the active word's tracing response so the first stroke pops at the exact attack.
s=s.replace("gain=.48 if since<-.04 else 1.25+max(0,1-since/.28)*.7", "gain=.48 if since<-.04 else 1.30+max(0,1-since/.20)*1.0")
# A hard, rhythm-derived alternate shot has a deliberately different vantage.
s=s.replace("(-1)**idx*1.8*alt,.65*alt,-1.0*alt", "(-1)**idx*3.7*alt,1.1*alt,-2.2*alt")
s=s.replace("sharp*.3,math.cos(t*61)*sharp*.22,-sharp*.6", "sharp*.4,math.cos(t*61)*sharp*.3,-sharp*.9")
# Individual dramatic scale changes. Readable holds surround every short macro shot.
s=s.replace("rr=roll*math.sin(u*math.pi)+sharp*.008*(-1)**idx", """macro=0.
 if idx in [0,4,5,7,10,11,14,16,23,28,30,31]:
  age=t-EVENT[idx]
  macro=max(0,1-abs(age-.18)/.26)*(.15 if idx in [4,7] else .23)
  eye=target+(eye-target)*(1-macro)
 if idx==5:
  blast=ease((t-25.40)/.22);eye=target+(eye-target)*(1+blast*.28)
 if idx==14:eye[0]+=math.sin(local*1.8)*action*1.5
 if idx==23:eye[2]+=action*3.0
 if idx==28:eye[2]-=action*2.0
 if idx==32:eye[2]-=ease(u)*1.5
 rr=roll*math.sin(u*math.pi)+sharp*.015*(-1)**idx""")
s=s.replace("environments[idx].draw(envmodel,vp,t,hit,action,idx,gain=.94)", """if idx==5:
  blast=ease((t-25.40)/.2);envmodel=envmodel@sc(1+blast*1.6)
 if idx==4:
  close=.22*(math.exp(-abs(t-18.885)/.12)+math.exp(-abs(t-20.235)/.12));envmodel=envmodel@np.diag([1,1-close,1,1])
 if idx==7:envmodel=tr(action*2.5,0,0)@envmodel
 if idx==14:envmodel=tr(action*3-2,0,0)@envmodel
 if idx==17:envmodel=envmodel@rot(action*.25,2)
 if idx==23:envmodel=envmodel@sc(1+action*.5)
 if idx==28:envmodel=tr(0,0,action*4)@envmodel
 if idx==29:envmodel=envmodel@rot(action*.2,2)
 if idx==30:envmodel=envmodel@np.diag([1,1+hit*.12,1,1])
 environments[idx].draw(envmodel,vp,t,hit*1.7,action,idx,gain=1.05)""")
s=s.replace("elif idx==5 and j==1:typemodel=typemodel@sc(1+sharp*.07)", """elif idx==5:
   if j==1:typemodel=typemodel@sc(1+sharp*.08)
   if t>25.4:
    blast=ease((t-25.4)/.22);typemodel=tr((-1)**j*blast*(j+1)*.5,blast*(1-j)*.3,-blast*j*.7)@typemodel
   if j==3:typemodel=typemodel@sc(1+max(0,1-abs(t-25.53)/.2)*.35)""")
s=s.replace("elif idx==14:typemodel=tr(math.sin(local*3+j)*hit*.2,0,0)@typemodel", "elif idx==14:typemodel=tr(math.sin(local*2+j)*hit*.55,0,math.sin(local+j)*action*.4)@typemodel")
s=s.replace("elif idx==30:typemodel=tr(0,math.sin(local*6+j)*hit*.15,0)@typemodel", "elif idx==30:typemodel=tr(0,math.sin(local*6+j)*hit*.35,0)@typemodel")
s=s.replace("phase=t-EVENT[idx]\n  if 0<phase<.7", "phase=t-(25.4 if idx==5 else EVENT[idx])\n  if 0<phase<.7")
s=s.replace("impact*.012", "impact*.024")
s=s.replace("paper=1. if idx in [9,17,18,21,26]", "paper=1. if idx in [9,17,18,21,26]")
# Boost colored structural engraving on the light technical scenes while keeping black letter outlines.
s=s.replace("vec3 p=vec3(.94,.95,.925)-c*.89", "vec3 p=vec3(.94,.95,.925)-min(vec3(1.05),c*1.65)*.89")
p.write_text(s,encoding='utf-8')
