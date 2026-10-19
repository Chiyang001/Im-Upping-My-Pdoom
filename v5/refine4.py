from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8')
# Make the language room into a passage occupying the lens, not a distant sign.
s=s.replace("S[6]=[('Trapped in the',18,0,4,-8,0,0,0),('Chinese room',18,-4,1,-8,.6,0,0),('with a bag of shrooms',21,4,-3,-10,-.6,0,0)]", "S[6]=[('Trapped in the',24,0,4,-3,0,0,0),('Chinese room',25,-3,1,.5,.35,0,0),('with a bag of shrooms',28,2,-3,.8,-.25,0,0)]")
s=s.replace("('PTO',11,-8,-2,-1,.6,0,0)","('PTO',9,-10,-2,-2,.4,0,0)").replace("('left to go',19,5,-3,-5,-.3,0,0)","('left to go',18,6,-4,-5,-.2,0,0)")
# Paperclip production becomes the architecture of the factory chapter.
pos=s.index('ANCHOR=[]')
s=s[:pos]+'''factory=Mesh();rng=np.random.default_rng(505)
clippts=[]
for a0 in np.linspace(0,math.pi,20):clippts.append([.45*math.cos(a0),1.1+.45*math.sin(a0),0])
clippts.append([-.45,-1.1,0])
for a0 in np.linspace(math.pi,2*math.pi,20):clippts.append([.45*math.cos(a0),-1.1+.45*math.sin(a0),0])
clippts.append([.45,.8,0])
for a0 in np.linspace(0,math.pi,20):clippts.append([.23*math.cos(a0),.8+.23*math.sin(a0),0])
clippts.append([-.23,-.9,0]);singleclip=Mesh();singleclip.line(clippts,WHITE*.65)
for lane in [-12,-8,-4.8,4.8,8,12]:
 for zz in np.arange(-65,16,3.2):
  yy=2.4*math.sin(zz*.18+lane);matrix=tr(lane,yy,zz)@rot(lane*.07+zz*.04,1)@rot(.7*math.sin(zz*.1),2)
  factory.add(singleclip,matrix);factory.line([[lane,yy-1.1,zz],[lane,2.4*math.sin((zz-3.2)*.18+lane)+1.1,zz-3.2]],C*.4)
 for y0 in [-5.5,5.5]:
  factory.line([[lane,y0,z0] for z0 in np.linspace(-65,16,240)],WHITE*.35)
factory=GPU(factory)
''' +s[pos:]
# Continuing shape bridges pass the camera instead of disappearing at a lyric index boundary.
s=s.replace("return tr(xx,yy,travel-an)","delta=t-lines[i][1];carry=0\n if i in [4,5,22,23,28,29,31] and delta>0:carry=18*ease(delta/1.4)\n return tr(xx,yy,travel-an+carry)")
s=s.replace("return node_matrix(i,t)@GLYPH_SCALE@sc(factor)@tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((i,j),0),0)","""model=node_matrix(i,t)@GLYPH_SCALE@sc(factor)@tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((i,j),0),0)
 if i==4:
  hinge=ease((t-21.1)/1.0);model=model@rot((-.45 if j==0 else .4 if j==2 else 0)*hinge,0)
 if i==22 and j==0:
  tension=ease((t-92.05)/.7);model=model@np.diag([1,1+tension*.65,1,1])
 if i==22 and t>94.86:model=model@rot(ease((t-94.86)/.8)*.8,2)
 return model""")
s=s.replace("age=t-wt;reveal=float(np.clip((age+.035)/.22,0,1))", "age=t-wt;reveal=float(np.clip((age+.035)/.22,0,1));rowend=rows[i][j+1][0][0][2] if j+1<len(rows[i]) else lines[i][1];dim=1-.78*ease((t-rowend-.25)/.75)")
s=s.replace("else:level=(.36 if age<-.035 else 1.35+max(0,1-age/.22)*.6)*gain", "else:level=((.62 if i in [5,14,23,30] and j==1 else .36) if age<-.035 else 1.35+max(0,1-age/.22)*.6)*gain*dim")
# Each chapter's own apparatus replaces the common square corridor when it is the story actor.
s=s.replace("worldM=np.diag([sx*", "maskMaw=ease((t-16)/.7)*(1-ease((t-26.0)/.7));maskRoom=ease((t-26)/.6)*(1-ease((t-30.0)/.6));maskFactory=ease((t-89.5)/.7)*(1-ease((t-109.2)/.7))\n wi*=1-.95*max(maskMaw,maskRoom,maskFactory);wc*=1-.95*max(maskMaw,maskFactory);ws*=1-.7*max(maskMaw,maskRoom,maskFactory)\n worldM=np.diag([sx*")
s=s.replace("STORY['road'].draw(np.eye(4)","STORY['road'].draw(np.eye(4)")
s=s.replace("motion=38,gain=1.0)","motion=38,gain=1.0)")
s=s.replace("STORY['road'].draw(worldM,vp,travel,hit,0,38,gain=1.0)","STORY['road'].draw(worldM,vp,travel,hit,0,38,gain=1.0-.78*max(maskMaw,maskRoom,maskFactory))")
s=s.replace("STORY['memory'].draw(worldM,vp,travel,hit,0,38,gain=.65*growth*wm)","STORY['memory'].draw(worldM,vp,travel,hit,0,38,gain=.65*growth*wm*(1-.6*maskFactory))\n factory.draw(np.eye(4),vp,travel,hit,0,38,gain=1.1*maskFactory)")
s=s.replace("em=node_matrix(ni,t)@sc(1.3)","envsize={4:2.35,5:1.7,6:1.8,7:1.5,8:1.6,13:1.6,14:1.6,16:1.7,22:1.9,23:2.0,24:1.7,27:1.5,28:1.6,29:1.6,30:1.7,31:1.6,32:1.8,33:1.8}.get(ni,1.3)\n  em=node_matrix(ni,t)@sc(envsize)")
s=s.replace("if ni<idx and t<141.2:draw_words(ni,t,vp,hit,gain=weight*.22,ghost=True)","if ni<idx and t<141.2:draw_words(ni,t,vp,hit,gain=weight*(1.3 if ni in [4,5,22,23,28,29,31] else .22),ghost=True)")
p.write_text(s,encoding='utf-8')
