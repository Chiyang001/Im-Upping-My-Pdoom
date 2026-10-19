from pathlib import Path
p=Path('v4/render.py');s=p.read_text(encoding='utf-8')
s=s.replace('m.line(p2,color*.55,closed=True)','m.line(p2,color*.20,closed=True)').replace('m.line(pp,color*.25,closed=True)','m.line(pp,color*.12,closed=True)').replace('m.line([p[k],p2[k]],color*.55)','m.line([p[k],p2[k]],color*.23)')
s=s.replace('void main(){vec3 p=pos;float seed=data.y;', 'void main(){vec3 p=pos;float seed=data.y;\n if(motion==0){p.y*=1.-energy*.13;p.z+=sin(p.x*9.+clock*8.)*energy*.08;}')
s=s.replace(' vec4 world=model*vec4(p,1);', ' if(motion==34){p.x*=1.+action*2.2;p.y+=sin(p.x*.9+clock*2.)*action*.5;p.z-=action*abs(p.x)*.3;}\n vec4 world=model*vec4(p,1);')
s=s.replace('uniform float gain;uniform float reveal;uniform float tracer;', 'uniform float gain;uniform float reveal;uniform float tracer;uniform float text_role;uniform vec4 clearBox;')
s=s.replace('frag=vec4(C*gain*tip*exp(-max(0.,dist-18.)*.008),1);','vec2 screen=gl_FragCoord.xy/vec2(1920.,1080.)*2.-1.;float zone=length((screen-clearBox.xy)/max(clearBox.zw,vec2(.02)));float room=mix(.30,1.,smoothstep(.55,1.5,zone));room=mix(room,1.,text_role);frag=vec4(C*gain*tip*exp(-max(0.,dist-18.)*.008)*room,1);')
s=s.replace('def __init__(self,m):\n  a=np.array', 'def __init__(self,m,role=0):\n  self.role=role\n  a=np.array')
s=s.replace("for key,val in [('clock'", "prog['text_role'].value=float(self.role)\n  for key,val in [('clock'")
s=s.replace('words.append((GPU(wm),wx,timing[wi],ww))','words.append((GPU(wm,1),wx,timing[wi],ww))')
s=s.replace("def stroke_title(s,size,col):return GPU(textmesh(s,size,col)[0])", "def stroke_title(s,size,col):return GPU(textmesh(s,size,col)[0],1)")
pos=s.index('# Per-scene semantic timing markers')
s=s[:pos]+'''endnetwork=Mesh()
base,_=textmesh('P(doom)',3.5,C,depth=1.2)
for j in range(32):endnetwork.add(base,tr(0,0,-j*.65)@sc(1+j*.035))
endnetwork=GPU(endnetwork)
infinity=Mesh()
for j in range(18):
 zz=(j-9)*.045
 infinity.line([[10*math.cos(a)/(1+math.sin(a)**2),7*math.sin(a)*math.cos(a)/(1+math.sin(a)**2),zz] for a in np.linspace(0,math.tau,500)],C*(.45 if j else 1.))
infinity=GPU(infinity,1)
endformula=stroke_title('P(doom) = '+chr(8734),1.0,WHITE)
''' +s[pos:]
needle="ms.use();ms.clear(.002,.005,.009,1,depth=1);ctx.enable"
s=s.replace(needle,"""# Dim only the immediately sung word's neighborhood; all geometry remains in the same depth-tested scene.
 widx=0
 for kk,word in enumerate(rows[idx][active][0]):
  if t>=word[2]-.04:widx=kk
 wg=rows[idx][active][0][widx][0];sr=rows[idx][active][2];_,_,sx,sy,sz,sry,srz,_=sr
 bm=tr(sx,sy,sz)@rot(sry,1)@rot(srz,2)@rot(RX.get((idx,active),0),0)
 wc=[]
 for xx in [wg.bmin[0],wg.bmax[0]]:
  for yy in [wg.bmin[1],wg.bmax[1]]:
   for zz in [wg.bmin[2],wg.bmax[2]]:wc.append(bm@np.array([xx,yy,zz,1]))
 wclip=np.array(wc)@vp.T;wndc=wclip[:,:2]/wclip[:,3:4];mn=wndc.min(axis=0);mx=wndc.max(axis=0)
 prog['clearBox'].value=(*(mn+mx)*.5,*np.maximum((mx-mn)*.65,.04))
 ms.use();ms.clear(.002,.005,.009,1,depth=1);ctx.enable""")
start=s.index(' if t>141.2:\n  ms.clear');end=s.index(' ctx.copy_framebuffer',start)
s=s[:start]+''' if t>141.2:
  ms.clear(.002,.005,.009,1,depth=1);prog['clearBox'].value=(3.,3.,.01,.01)
  outro=t-141.2;ending=ease((outro-3)/6)
  oe=np.array([-6+outro*.8,2+math.sin(outro*.18)*2,25-outro*.4]);ot=np.array([0.,0.,-7.]);vp=perspective(math.radians(53+ending*6),W/H)@look(oe,ot)
  if t<154.2:
   endnetwork.draw(tr(0,0,-3),vp,t,hit,ending,34,gain=.42+hit*.2)
   environments[30].draw(tr(0,-1,-4)@sc(1.3+ending*.6),vp,t,hit,ending,30,gain=.42)
   endtitle.draw(tr(0,.7,2)@rot(ending*.6,1),vp,t,hit,ending,34,gain=1.3,reveal=min(1,outro/.65))
   if outro<4:endclaim.draw(tr(0,-3.5,2),vp,t,hit,gain=1.0)
  else:
   final=t-154.2;vp=perspective(math.radians(48),W/H)@look(np.array([0.,0.,24.]),[0,0,0])
   infinity.draw(tr(0,.5,0)@rot((1-ease(final/.5))*.3,1),vp,t,hit,gain=1.4*min(1,(DUR-t)/.45),reveal=min(1,final/.45))
   endformula.draw(tr(0,-3.2,1),vp,t,hit,gain=1.1*min(1,(DUR-t)/.45))
   endname.draw(tr(0,-5.4,1),vp,t,hit,gain=.9*min(1,(DUR-t)/.45))
''' +s[end:]
p.write_text(s,encoding='utf-8')
