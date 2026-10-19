from pathlib import Path
s=Path('v4/render.py').read_text(encoding='utf-8');s=s[:s.index('def drawframe(t):')]
s=s.replace("sys.path.insert(0,'v4');sys.path.insert(0,'code3d')", "sys.path.insert(0,'v4');sys.path.insert(0,'code3d');sys.path.insert(0,'v5')")
s=s.replace('from scenes_early import build as early','from scenes_early import build as early\nfrom camera_path import camera_state\nfrom world_layers import build_world\nfrom story_geometry import build_story,road_point')
# Give a few narrative nouns a larger physical role; no per-word auto-focus will remain.
s=s.replace("S[2]=[", "S[0][1]=('AGI',18,0,-1.,0,0,0,0)\nS[2]=[")
s=s.replace("S[3]=[(\"Now I'm your servant\",21,-1,-3.8,-1,-.25,0,0),(\"and you're my boss\",29,0,3.3,-3,.15,0,0)]", "S[3]=[(\"Now I'm your servant\",24,-3,-3.8,-1,-.15,0,0),(\"and you're my\",18,4,3.5,-2,.15,0,0),('boss',18,4,-.2,-2,.1,0,0)]")
s=s.replace("S[20]=[('Sharp left turn',25,0,1,0,0,0,0),('and there you are',25,0,-.5,0,1.570796,0,0)]", "S[20]=[('Sharp left turn',25,-2,2,-1,.22,-.1,0),('and there you are',25,3,-2,-3,-.25,.08,0)]")
s=s.replace("('blues',19,5,-3,-4,-1.570796,0,0)","('blues',19,5,-3,-4,-.4,.2,0)")
s=s.replace("RX={(2,0):-.75,(2,2):-1.05,(6,2):-.15,(13,1):-.8,(18,0):-.75,(18,1):.75,(21,0):-.18,(26,0):-.35,(30,1):-.55,(31,0):-.1}", "RX={(2,0):-.3,(2,2):-.4,(6,2):-.15,(13,1):-.3,(18,0):-.35,(18,1):.35,(21,0):-.18,(26,0):-.2,(30,1):-.3,(31,0):-.1}")
s=s.replace('if(motion==34)', '''if(motion==35){p.z=mod(p.z+clock+70.,100.)-70.;}
 if(motion==36){p.z=mod(p.z+clock+48.,82.)-48.;p.x+=sin(p.z*.12+clock*.01)*.3;p.y+=cos(p.z*.08-clock*.015)*.18;}
 if(motion==37){p.z=mod(p.z+clock+55.,90.)-55.;p.x+=sin(clock*.03+p.y*.6)*.4;}
 if(motion==34)''')
s=s.replace('exp(-max(0.,dist-18.)*.008)', 'exp(-max(0.,dist-16.)*mix(.018,.006,text_role))')
# All old drawing and camera-centering logic is replaced below.
s+='''
WORLD={key:GPU(mesh) for key,mesh in build_world(Mesh,np,math,C,WHITE,ACC).items()}
STORY={key:GPU(mesh) for key,mesh in build_story(Mesh,np,math,C,WHITE,ACC).items()}
ANCHOR=[]
for i,r in enumerate(lines):
 at=(r[0]+r[1])*.5;travel=camera_state(at,np,math)['travel'];ANCHOR.append((travel,2.0*math.sin(at*.055),.9*math.sin(at*.07)))
GLYPH_SCALE=np.diag([1.14,1.02,.62,1.])
# A luminous signal and its wake are the moving witness that connects the whole journey.
signal=Mesh()
for j in range(3):signal.circle(.12+j*.025,axis=j,color=ACC,n=30)
signal.line([[0,0,.55],[0,0,-.55]],WHITE);signal=GPU(signal,1)
trailbuf=ctx.buffer(reserve=128*8*4)
trailvao=ctx.vertex_array(prog,[(trailbuf,'3f 3f 2f','pos','color','data')])

def node_matrix(i,t):
 travel=camera_state(t,np,math)['travel'];an,xx,yy=ANCHOR[i]
 return tr(xx,yy,travel-an)
def frame_view(t,hit=0):
 state=camera_state(t,np,math);eye=np.array(state['eye'],float);target=np.array(state['target'],float)
 # Impacts affect the physical trip briefly; there is no word-centering or verse reset.
 eye+=np.array([math.sin(t*79)*hit*.10,math.cos(t*67)*hit*.08,-hit*.22])
 roll=state['roll']+hit*math.sin(t*29)*.005
 vp=perspective(math.radians(state['fov']-hit*.5),W/H,far=220)@(rot(roll,2)@look(eye,target))
 return state,eye,target,vp

def word_matrix(i,j,t):
 phrase,width,x,y,z,ry,rz,rad=rows[i][j][2]
 return node_matrix(i,t)@GLYPH_SCALE@tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((i,j),0),0)

def draw_words(i,t,vp,hit,gain=1.,ghost=False):
 for j,(words,scaffold,sr) in enumerate(rows[i]):
  model=word_matrix(i,j,t)
  scaffold.draw(model,vp,t,hit,gain=.6*gain)
  for k,(gpu,wx,wt,ww) in enumerate(words):
   age=t-wt;reveal=float(np.clip((age+.035)/.22,0,1))
   if ghost:level=.23*gain
   else:level=(.36 if age<-.035 else 1.35+max(0,1-age/.22)*.6)*gain
   # Letter strokes continue into architecture; a word may disassemble only after it was readable.
   wm=model
   if i==12 and age>.5:
    move=math.sin(ease((age-.5)/1.25)*math.pi)*.5;wm=wm@tr(math.sin(k*7+j)*move,math.cos(k*4+j)*move,math.sin(k*3)*move)
   if i==29 and age>.7:wm=wm@tr(math.sin(k+j*2)*hit*.18,0,0)
   ctx.line_width=1.75 if age>=0 and age<.4 else 1.45
   if not ghost and -.035<=age<.22:
    ctx.depth_func='<=';gpu.draw(wm,vp,t,hit,gain=.45*gain);gpu.draw(wm,vp,t,hit,gain=level,reveal=reveal);ctx.depth_func='<'
   else:gpu.draw(wm,vp,t,hit,gain=level)
 ctx.line_width=1.2

def signal_position(t,travel):
 ahead=2.4+.5*math.sin(t*.5);zz=((ahead-travel+70)%100)-70
 x,y,z=road_point(zz,-1)
 return np.array([x,y,((z+travel+70)%100)-70])

def drawframe(t):
 global last_camera_stats
 idx=next((i for i,r in enumerate(lines) if r[0]<=t<r[1]),-1)
 if idx<0:idx=max(0,min(33,np.searchsorted([r[0] for r in lines],t,'right')-1))
 a,b,*_=lines[idx];u=float(np.clip((t-a)/(b-a),0,1));sharp,hit=beatstate(t);state,eye,target,vp=frame_view(t,hit);travel=state['travel'];section=state['section']
 # Camera audit records the actual autonomous path. It never modifies eye or target.
 current=0
 for j,(words,_,_) in enumerate(rows[idx]):
  if t>=words[0][2]-.05:current=j
 points=[]
 for gpu,wx,wt,ww in rows[idx][current][0]:
  for xx in [gpu.bmin[0],gpu.bmax[0]]:
   for yy in [gpu.bmin[1],gpu.bmax[1]]:
    for zz in [gpu.bmin[2],gpu.bmax[2]]:points.append(word_matrix(idx,current,t)@np.array([xx,yy,zz,1]))
 clip=np.array(points)@vp.T;ndc=clip[:,:2]/clip[:,3:4]
 last_camera_stats={'t':float(t),'idx':int(idx),'row':int(current),'xmin':float(ndc[:,0].min()),'xmax':float(ndc[:,0].max()),'ymin':float(ndc[:,1].min()),'ymax':float(ndc[:,1].max()),'travel':float(travel)}
 # A soft local illumination pocket gives the sung line contrast, while preserving moving foreground edges.
 mn=ndc.min(axis=0);mx=ndc.max(axis=0);prog['clearBox'].value=(*(mn+mx)*.5,*np.maximum((mx-mn)*.65,.08))
 ms.use();ms.clear(.002,.006,.011,1,depth=1);ctx.enable(gl.DEPTH_TEST);ctx.disable(gl.BLEND);ctx.line_width=1.15
 growth=.55+.45*ease(t/18);tension=.7+.3*ease((t-38)/80)
 # Persistent layers remain in the world across all lyric boundaries.
 WORLD['infrastructure'].draw(np.eye(4),vp,travel*.78,hit,0,36,gain=1.25*growth)
 WORLD['city'].draw(tr(0,-.5,0),vp,travel,hit,0,36,gain=1.15*growth*tension)
 WORLD['debris'].draw(np.eye(4),vp,travel*1.3,hit,0,37,gain=.85*growth)
 WORLD['data_ribbons'].draw(np.eye(4),vp,travel*.86,hit,0,35,gain=1.1*growth)
 STORY['road'].draw(np.eye(4),vp,travel,hit,0,35,gain=1.0)
 STORY['signals'].draw(np.eye(4),vp,travel,hit,0,35,gain=1.0+hit*.6)
 STORY['machine_skeleton'].draw(np.eye(4),vp,travel,hit,0,35,gain=.8*growth)
 STORY['memory'].draw(np.eye(4),vp,travel,hit,0,35,gain=.65*growth)
 # Previous forms physically remain behind us; future forms are visible farther along the road.
 for ni in [idx-1,idx,idx+1]:
  if not 0<=ni<34:continue
  if ni==idx:weight=.85;clock=t;action=ease((t-EVENT[ni])/.7)
  elif ni<idx:weight=.36*(1-ease((t-a)/4.0));clock=t;action=1
  else:weight=.14+.17*ease(u);clock=t;action=0
  if weight<.02:continue
  em=node_matrix(ni,t)@sc(1.3)
  if ni==7:em=em@tr(3,0,-1)@rot(-.2,2)
  if ni==14:em=em@tr(-2,-1,-2)@rot(.55,2)@rot(.3,1)
  if ni==10:em=em@rot(-.2,0)
  if ni==27:em=em@tr(2,0,0)
  if ni==29:em=em@rot(action*.2,2)
  if ni==5 and t>25.685:em=em@sc(1+ease((t-25.685)/.25)*1.2)
  environments[ni].draw(em,vp,clock,hit*1.3,action,ni,gain=weight)
  if ni!=idx:draw_words(ni,t,vp,hit,gain=weight*.6,ghost=True)
 # The living red signal carries impact energy forward along the actual connected road.
 pos=signal_position(t,travel);signal.draw(tr(*pos)@sc(1+hit*.3),vp,t,hit,gain=2.4)
 tail=[]
 for q0 in np.linspace(0,.9,45):
  tt=max(0,t-q0);pasttravel=camera_state(tt,np,math)['travel'];pp=signal_position(tt,pasttravel);pp[2]+=travel-pasttravel;tail.append(pp)
 arr=[]
 for j in range(len(tail)-1):
  for pp in [tail[j],tail[j+1]]:arr.append([*pp,*(ACC*(1-j/len(tail))),j/len(tail),0])
 trailbuf.write(np.array(arr,'f4').tobytes());prog['model'].write(np.eye(4,dtype='f4').tobytes());prog['vp'].write(np.array(vp.T,'f4').tobytes());prog['clock']=t;prog['energy']=hit;prog['action']=0;prog['motion']=-1;prog['gain']=1.7;prog['reveal']=1;prog['tracer']=0;prog['text_role']=1
 trailvao.render(gl.LINES,vertices=len(arr))
 draw_words(idx,t,vp,hit)
 # Burst fragments become part of the next environment instead of resetting the world.
 if idx in [5,7,10,14,16,20,23,25,27,28,29,30,31]:
  phase=t-(25.685 if idx==5 else EVENT[idx])
  if 0<phase<1.0:shards.draw(node_matrix(idx,t)@tr(0,0,2)@sc(.3+phase*10),vp,t,hit,gain=(1-phase)*.75)
 if t>141.2:
  outro=t-141.2;ending=ease((outro-2)/7)
  # Last scene remains: the city, theatre and eye become one machine around the retreating camera.
  prog['clearBox'].value=(3,3,.01,.01)
  if t<154.6:
   endnetwork.draw(tr(0,0,-4),vp,t,hit,ending,34,gain=.45+hit*.2)
   endtitle.draw(tr(0,1,1)@rot(ending*.45,1),vp,t,hit,ending*.65,34,gain=1.1,reveal=min(1,outro/.6))
   if outro>9:endclaim.draw(tr(0,-3,1),vp,t,hit,gain=.8)
  else:
   final=t-154.6;fade=min(1,(DUR-t)/.4)
   infinity.draw(tr(0,0,0),vp,t,hit,gain=1.2*fade,reveal=min(1,final/.45))
   endformula.draw(tr(0,-3.3,1),vp,t,hit,gain=fade)
   endname.draw(tr(0,-5.2,1),vp,t,hit,gain=.8*fade)
 ctx.copy_framebuffer(resolve,ms);output.use();ctx.disable(gl.DEPTH_TEST);tex.use(0)
 paper=ease((t-68.2)/.5)*(1-ease((t-73.5)/.6))*.85
 if t>104:paper=max(paper,ease((t-104.6)/.5)*(1-ease((t-109.0)/.5))*.75)
 post['paper']=paper;post['impact']=sharp*.6;post['flash']=sharp*.12;q.render(gl.TRIANGLE_STRIP)
 return output.read(components=3,alignment=1)

def main():
 if '--audit' in sys.argv:
  audit=[]
  for t in np.arange(1.5,141,.25):drawframe(float(t));audit.append(last_camera_stats)
  json.dump(audit,open('v5/framing_audit.json','w'),indent=2);print('audit saved',flush=True);return
 if '--preview' in sys.argv:
  times=[(r[0]+r[1])*.5 for r in lines]+[146,155];sheet=Image.new('RGB',(1920,9*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v5/preview-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{j:02} / {t:.2f}s',fill='white')
  sheet.save('v5/storyboard.jpg');print('preview saved',flush=True);return
 ff=imageio_ffmpeg.get_ffmpeg_exe();src=str(next(pathlib.Path('.').glob('*.mp4')));dest='output_v5/Pdoom_Living_Machine_1080p.mp4'
 if '--sample' in sys.argv:start=float(sys.argv[sys.argv.index('--sample')+1]);duration=12;dest=f'v5/sample-{int(start)}.mp4'
 else:start=0;duration=DUR
 cmd=[ff,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-ss',str(start),'-i',src,'-map','0:v','-map','1:a','-vf','vflip','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-t',str(duration),'-movflags','+faststart',dest]
 with open('v5/render.log','w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for i in range(round(duration*FPS)):
   p.stdin.write(drawframe(start+i/FPS))
   if i%300==0:print(f'{start+i/FPS:.0f} seconds rendered',flush=True)
  p.stdin.close();p.wait();assert p.returncode==0
 print(dest,flush=True)
if __name__=='__main__':main()
'''
Path('v5/render.py').write_text(s,encoding='utf-8')
