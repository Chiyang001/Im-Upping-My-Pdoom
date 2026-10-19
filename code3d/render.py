import math,json,pathlib,subprocess,sys,random,re,difflib
import numpy as np
import moderngl as gl
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
import mapbox_earcut as ear
import imageio_ffmpeg
W,H=1920,1080;FPS=30;DUR=156.667
C=np.array([.70,.97,.77]);WHITE=np.array([.86,.91,.94]);PURPLE=np.array([.40,.38,.95]);DARK=np.array([.09,.16,.18])
def unit(v):v=np.array(v,dtype=float);return v/max(1e-9,np.linalg.norm(v))
def tr(x=0,y=0,z=0):m=np.eye(4);m[:3,3]=[x,y,z];return m
def sc(x):return np.diag([x,x,x,1.])
def rot(a,axis=1):
 c,s=math.cos(a),math.sin(a);m=np.eye(4);i,j=[(1,2),(2,0),(0,1)][axis];m[i,i]=m[j,j]=c;m[i,j]=-s;m[j,i]=s;return m

def perspective(fov,aspect,near=.1,far=150):
 f=1/math.tan(fov/2);return np.array([[f/aspect,0,0,0],[0,f,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]])
def look(eye,target):
 f=unit(np.array(target)-eye);s=unit(np.cross(f,[0,1,0]));u=np.cross(s,f);m=np.eye(4);m[:3,:3]=[s,u,-f];m[:3,3]=-m[:3,:3]@eye;return m
class Mesh:
 def __init__(self):self.v=[];self.l=[]
 def tri(self,a,b,c,color=WHITE):
  n=unit(np.cross(np.array(b)-a,np.array(c)-a))
  for p in [a,b,c]:self.v.append([*p,*n,*color])
 def line(self,pts,color=C,closed=False):
  p=np.array(pts)
  if closed:p=np.vstack([p,p[0]])
  for a,b in zip(p[:-1],p[1:]):self.l.extend([[*a,*color],[*b,*color]])
 def add(self,other,m=None):
  m=np.eye(4) if m is None else m
  if other.v:
   a=np.array(other.v).copy();a[:,:3]=(np.c_[a[:,:3],np.ones(len(a))]@m.T)[:,:3];a[:,3:6]=a[:,3:6]@m[:3,:3].T;a[:,3:6]/=np.maximum(np.linalg.norm(a[:,3:6],axis=1)[:,None],1e-8);self.v.extend(a.tolist())
  if other.l:
   a=np.array(other.l).copy();a[:,:3]=(np.c_[a[:,:3],np.ones(len(a))]@m.T)[:,:3];self.l.extend(a.tolist())
 def circle(self,r=1,pos=(0,0,0),axis=2,color=C,n=160):
  pts=[]
  for t in np.linspace(0,math.tau,n):
   a=[r*math.cos(t),r*math.sin(t),0];a=np.roll(a,axis-2);pts.append(np.array(a)+pos)
  self.line(pts,color)
 def sphere(self,r=1,pos=(0,0,0),color=C,rings=12):
  for a in np.linspace(-1.45,1.45,rings):self.circle(r*math.cos(a),(pos[0],pos[1]+r*math.sin(a),pos[2]),1,color,100)
  for a in np.linspace(0,math.pi,rings):
   self.line([np.array(pos)+[r*math.cos(t)*math.cos(a),r*math.sin(t),r*math.cos(t)*math.sin(a)] for t in np.linspace(0,math.tau,100)],color)
 def box(self,pos,size,color=C):
  p=np.array(pos);s=np.array(size)/2;vs=[p+s*np.array([x,y,z]) for x in [-1,1] for y in [-1,1] for z in [-1,1]]
  for i,a in enumerate(vs):
   for j,b in enumerate(vs):
    if j>i and sum(a!=b)==1:self.line([a,b],color)
 def tube(self,pts,r=.04,color=C,sides=6):
  pts=np.array(pts);rings=[]
  for i,p in enumerate(pts):
   tangent=unit(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]);u=unit(np.cross(tangent,[0,1,0] if abs(tangent[1])<.9 else [1,0,0]));v=np.cross(tangent,u);rings.append([p+r*(math.cos(t)*u+math.sin(t)*v) for t in np.linspace(0,math.tau,sides,endpoint=False)])
  for a,b in zip(rings[:-1],rings[1:]):
   for j in range(sides):k=(j+1)%sides;self.tri(a[j],b[j],b[k],color);self.tri(a[j],b[k],a[k],color)
class Pen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.contours=[];self.p=[]
 def _moveTo(self,p):self.p=[p]
 def _lineTo(self,p):self.p.append(p)
 def _curveToOne(self,p1,p2,p3):
  p0=self.p[-1]
  for t in np.linspace(0,1,9)[1:]:self.p.append(tuple((1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3)))
 def _qCurveToOne(self,p1,p2):
  p0=self.p[-1]
  for t in np.linspace(0,1,7)[1:]:self.p.append(tuple((1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t*t*np.array(p2)))
 def _closePath(self):
  if len(self.p)>2:self.contours.append(self.p)
  self.p=[]
 def _endPath(self):self._closePath()
font=TTFont('C:/Windows/Fonts/arialbd.ttf');gs=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm;cache={}
def glyph(ch):
 if ch in cache:return cache[ch]
 name=cmap.get(ord(ch),'question');pen=Pen(gs);gs[name].draw(pen);geo=None
 for contour in pen.contours:
  poly=Polygon(np.array(contour)/upm)
  if not poly.is_valid:poly=poly.buffer(0)
  geo=poly if geo is None else geo.symmetric_difference(poly)
 out=Mesh();dep=.24
 if geo is not None:
  polys=[geo] if geo.geom_type=='Polygon' else list(geo.geoms)
  for poly in polys:
   rings=[np.array(poly.exterior.coords)[:-1]]+[np.array(x.coords)[:-1] for x in poly.interiors];vertices=np.concatenate(rings);ends=np.cumsum([len(x) for x in rings]).astype(np.uint32);ids=ear.triangulate_float64(vertices,ends)
   for i in range(0,len(ids),3):
    abc=[[*vertices[k],dep] for k in ids[i:i+3]];out.tri(*abc);out.tri(*[[*vertices[k],0] for k in reversed(ids[i:i+3])])
   for ring in rings:
    for a,b in zip(ring,np.roll(ring,-1,axis=0)):
     out.tri([*a,0],[*b,0],[*b,dep]);out.tri([*a,0],[*b,dep],[*a,dep])
 cache[ch]=(out,font['hmtx'][name][0]/upm);return cache[ch]
def text(s,size=1,color=WHITE,center=True):
 out=Mesh();width=sum(glyph(c)[1] for c in s)*size;x=-width/2 if center else 0
 for ch in s:
  g,adv=glyph(ch);temp=Mesh();temp.add(g,tr(x,0,0)@sc(size))
  for v in temp.v:v[6:9]=color
  out.add(temp);x+=adv*size
 return out,width

def clipmesh():
 m=Mesh();pts=[]
 # open continuous folded paperclip path
 for t in np.linspace(0,math.pi,20):pts.append([.5*math.cos(t),1.2+.5*math.sin(t),0])
 pts.extend([[-.5,-1.2,0]])
 for t in np.linspace(math.pi,2*math.pi,20):pts.append([.5*math.cos(t),-1.2+.5*math.sin(t),0])
 pts.append([.5,.85,0])
 for t in np.linspace(0,math.pi,20):pts.append([.25*math.cos(t),.85+.25*math.sin(t),0])
 pts.append([-.25,-.9,0]);m.tube(pts,.045,WHITE);return m
clip=clipmesh()

def objectmesh(kind):
 m=Mesh();rng=np.random.default_rng(55+kind)
 if kind==0: # precision eye, curved iris and eyelid contours
  for k in range(28):
   r=1.0+k*.065;m.circle(r,axis=2,color=C if k%4==0 else DARK)
  for k in range(160):
   a=k*math.tau/160;pts=[]
   for r in np.linspace(1.1,2.8,25):pts.append([r*math.cos(a+.06*math.sin(r*8+k)),r*math.sin(a+.06*math.sin(r*8+k)),.10*math.sin(r*5+k)])
   m.line(pts,WHITE*.7)
  for k in range(16):
   z=-.8+k*.1
   m.line([[x,1.9*math.sin(math.pi*(x+4.3)/8.6),z] for x in np.linspace(-4.3,4.3,150)],C)
   m.line([[x,-1.9*math.sin(math.pi*(x+4.3)/8.6),z] for x in np.linspace(-4.3,4.3,150)],C)
  m.sphere(.85,color=PURPLE,rings=12)
 elif kind==1: # circuits / neural architecture
  for j in range(7):
   z=(j-3)*1.0
   for k in range(8):
    x=(k-3.5)*1.1;y=.35*math.sin(k+j);m.box((x,y,z),(.6,.6,.6),C)
    m.line([[x,y,z],[x,y+1.3,z],[x+.5,y+1.3,z],[x+.5,y+1.3,z+1]],WHITE*.6)
  for j in range(12):m.line([[x,math.sin(x*2+j)*.15-2+j*.12,(j-6)*.15] for x in np.linspace(-6,6,180)],PURPLE)
 elif kind==2: # loss manifold
  for z in np.linspace(-5,5,65):m.line([[x,2*math.exp(-x*.32)*.3*math.sin(z*.8)+.12*x*x-2,z] for x in np.linspace(-5,5,100)],C if int(z*10)%4==0 else DARK*2)
  for x in np.linspace(-5,5,50):m.line([[x,2*math.exp(-x*.32)*.3*math.sin(z*.8)+.12*x*x-2,z] for z in np.linspace(-5,5,90)],WHITE*.32)
  m.tube([[x,.12*x*x-1.9+.6*math.sin(x*.8),0] for x in np.linspace(-5,5,100)],.035,PURPLE)
 elif kind==3: # impossible room
  for j in range(20):
   z=-j*.8;m.box((0,0,z),(10,7,.03),C if j%4==0 else DARK*2)
   for k in range(5):m.line([[-5+k*2,-3.5,z],[-5+k*2,3.5,z]],DARK)
  for j in range(12):
   x,y,z=rng.uniform([-4,-2,-12],[4,2,1]);m.box((x,y,z),(1,2,.1),WHITE)
 elif kind==4: # organic shoggoth made entirely of evolving curves
  for j in range(120):
   a=j*math.tau/120;pts=[]
   for t in np.linspace(0,1,100):
    r=2.2+1.7*t+math.sin(t*12+a*5)*.3;pts.append([r*math.cos(a+t*2),r*math.sin(a+t*2)*.7,math.sin(a*4+t*10)*t*1.4])
   m.line(pts,C if j%5 else WHITE)
  m.sphere(1.1,color=PURPLE)
 elif kind==5: # atom / singularity
  m.sphere(.65,color=WHITE)
  for j in range(15):
   a=j*math.pi/15;temp=Mesh();temp.circle(2.4+j*.06,axis=1,color=C if j%3 else PURPLE);m.add(temp,rot(a,0)@rot(a*.7,2))
  for j in range(30):m.sphere(.035,pos=rng.normal(0,2.2,3),color=WHITE,rings=3)
 elif kind==6: # basilisk / a logarithmic helical serpent
  for j in range(40):
   pts=[]
   for t in np.linspace(-math.pi*2,math.pi*2,400):
    rr=2.1+.45*math.cos(t*.7);a=j*math.tau/40;pts.append([(rr+.35*math.cos(a))*math.cos(t),t*.43+.35*math.sin(a),(rr+.35*math.cos(a))*math.sin(t)])
   m.line(pts,C if j%4 else WHITE)
  m.circle(3.8,axis=2,color=PURPLE)
 elif kind==7: # paperclip cathedral
  for j in range(85):
   x,y,z=rng.uniform([-6,-3,-8],[6,4,2]);m.add(clip,tr(x,y,z)@rot(rng.uniform(-1,1),2)@rot(rng.uniform(-1,1),1)@sc(rng.uniform(.2,.65)))
 elif kind==8: # compute lattice
  for x in range(-4,5):
   for y in range(-3,4):
    for z in range(-2,3):m.box((x*.95,y*.9,z*.95),(.5,.5,.5),C if (x+y+z)%4==0 else DARK*2.5)
  for j in range(20):m.circle(4.8+j*.02,axis=1,color=PURPLE*.7,n=150)
 elif kind==9: # neural layers
  for i in range(5):
   for j in range(7):
    pos=[(i-2)*2,(j-3)*.8,0];m.circle(.18,pos,2,WHITE,32)
    if i<4:
     for k in range(7):m.line([pos,[(i-1)*2,(k-3)*.8,0]],DARK*2)
  for i in range(5):m.box(((i-2)*2,0,-.3),(.04,6,3),C)
 elif kind==10: # fuse / orthogonal axes
  for j in range(24):m.line([[x,math.sin(x*1.3+j*.13)*.2,math.cos(x*1.3+j*.13)*.2] for x in np.linspace(-6,6,240)],C)
  for k in range(3):
   v=np.zeros(3);v[k]=5;m.line([-v,v],WHITE)
  m.circle(2.8,axis=2,color=PURPLE)
 return m
ctx=gl.create_standalone_context(require=330);print(ctx.info['GL_RENDERER'],flush=True)
vs='''#version 330
in vec3 pos;in vec3 normal;in vec3 color;uniform mat4 model;uniform mat4 vp;out vec3 N;out vec3 P;out vec3 C;void main(){vec4 p=model*vec4(pos,1);P=p.xyz;N=mat3(model)*normal;C=color;gl_Position=vp*p;}'''
fs='''#version 330
in vec3 N;in vec3 P;in vec3 C;out vec4 frag;uniform vec3 eye;uniform float pulse;uniform float gain;void main(){vec3 n=normalize(N);if(!gl_FrontFacing)n=-n;vec3 l=normalize(vec3(-.5,1,1));vec3 v=normalize(eye-P);float diff=max(dot(n,l),0);float rim=pow(1-max(dot(n,v),0),3);float spec=pow(max(dot(n,normalize(l+v)),0),50);vec3 col=C*(.28+.72*diff)+vec3(.55,.72,.8)*spec*.7+C*rim*.25;float fog=exp(-length(eye-P)*.009);frag=vec4(col*fog*gain,1);}'''
lvs='''#version 330
in vec3 pos;in vec3 color;uniform mat4 model;uniform mat4 vp;out vec3 C;out float dist;uniform vec3 eye;void main(){vec4 p=model*vec4(pos,1);dist=length(eye-p.xyz);C=color;gl_Position=vp*p;}'''
lfs='''#version 330
in vec3 C;in float dist;uniform float pulse;uniform float gain;out vec4 frag;void main(){frag=vec4(C*(1.1+pulse*.35)*exp(-dist*.010)*gain,1);}'''
prog=ctx.program(vertex_shader=vs,fragment_shader=fs);lp=ctx.program(vertex_shader=lvs,fragment_shader=lfs)
class GPU:
 def __init__(self,m):
  self.vao=None;self.line=None
  if m.v:self.buf=ctx.buffer(np.array(m.v,'f4').tobytes());self.vao=ctx.vertex_array(prog,[(self.buf,'3f 3f 3f','pos','normal','color')])
  if m.l:self.lb=ctx.buffer(np.array(m.l,'f4').tobytes());self.line=ctx.vertex_array(lp,[(self.lb,'3f 3f','pos','color')])
 def draw(self,model,vp,eye,pulse=0,gain=1):
  for p in [prog,lp]:
   p['model'].write(np.array(model.T,'f4').tobytes());p['vp'].write(np.array(vp.T,'f4').tobytes());p['eye'].value=tuple(eye)
   if 'pulse' in p:p['pulse'].value=pulse
   if 'gain' in p:p['gain'].value=gain
  if self.vao:self.vao.render(gl.TRIANGLES)
  if self.line:self.line.render(gl.LINES)
objects=[GPU(objectmesh(k)) for k in range(11)]
marker=Mesh();marker.sphere(.11,color=C,rings=5);marker=GPU(marker)
burst=Mesh();rng=np.random.default_rng(16)
for j in range(140):
 v=unit(rng.normal(size=3));burst.line([v*1.2,v*(1.8+rng.random()*2.5)],C if j%4 else WHITE)
burst=GPU(burst)
# A precisely ruled spatial stage, drawn as geometry, with no background image.
stage=Mesh()
for x in np.linspace(-20,20,61):stage.line([[x,-4,-22],[x,-4,12]],DARK*.65)
for z in np.linspace(-22,12,54):stage.line([[-20,-4,z],[20,-4,z]],DARK*.65)
for j in range(3):stage.circle(6+j*.06,(0,-3.98,-1),1,C*.4)
stage=GPU(stage)
lines=json.load(open('work/lyrics.json'));beats=np.array(json.load(open('work/beats.json')))
# Letterforms are tessellated outlines, extruded into solid meshes. No text textures.
layouts=[]
trans=json.load(open('work/transcript.json'))
def norm(x):return re.sub('[^a-z0-9]','',x.lower())
for i,r in enumerate(lines):
 a,b,asset,lyric,key=r;parts=lyric.split('|');chunks=[]
 for phrase in parts:
  if len(phrase)>45:
   words=phrase.split();k=len(words)//2;chunks.extend([' '.join(words[:k]),' '.join(words[k:])])
  else:chunks.append(phrase)
 allwords=' '.join(chunks).split();ws=[w for z in trans for w in z['words'] if a-.1<=w['start']<b]
 matcher=difflib.SequenceMatcher(None,[norm(x) for x in allwords],[norm(w['word']) for w in ws],autojunk=False);timing={}
 for block in matcher.get_matching_blocks():
  for j in range(block.size):timing[block.a+j]=ws[block.b+j]['start']
 for j in range(len(allwords)):
  if j not in timing:
   lo=max([k for k in timing if k<j],default=-1);hi=min([k for k in timing if k>j],default=len(allwords));timing[j]=timing.get(lo,a)+(timing.get(hi,b-.2)-timing.get(lo,a))*(j-lo)/(hi-lo)
 rows=[];wordindex=0
 for j,phrase in enumerate(chunks):
  raw,width=text(phrase,1);size=min(1.7,20/max(width,1));width*=size;x=-width/2;words=[]
  for word in phrase.split():
   color=C if j==0 and i in [5,14,23,30] else WHITE
   mesh,ww=text(word,size,color);wordx=x+ww/2;x+=ww+glyph(' ')[1]*size
   words.append((GPU(mesh),wordx,timing[wordindex]));wordindex+=1
  rail=Mesh();radius=24 if i%2 else -25
  rail.line([[x,-.22,radius*(1-math.cos(x/radius))] for x in np.linspace(-width/2-.3,width/2+.3,150)],C*.6)
  for x in np.linspace(-width/2,width/2,int(width*4)):
   z=radius*(1-math.cos(x/radius));rail.line([[x,-.25,z],[x,-.33,z]],WHITE*.6)
  rows.append((words,width,size,GPU(rail),radius))
 layouts.append(rows)
# Etched concentric instruments, ticks, construction rails and physical micro labels.
precision=Mesh()
for rr in [3.8,3.84,4.15,4.2,5.0,5.02]:precision.circle(rr,axis=2,color=C*.55)
for k in range(180):
 a=k*math.tau/180;r0=4.2;r1=r0+(.22 if k%5==0 else .08)
 precision.line([[r0*math.cos(a),r0*math.sin(a),0],[r1*math.cos(a),r1*math.sin(a),0]],WHITE*.7)
for k in range(12):
 a=k*math.tau/12;rr=5.2;small,_=text(f'{k*30:03}',.19,C);precision.add(small,tr(rr*math.cos(a),rr*math.sin(a),0)@rot(a,2))
precision=GPU(precision)
labels=[]
for i,r in enumerate(lines):
 m=Mesh();kind=kindmap[i] if 'kindmap' in globals() else i
 for j,word in enumerate(['SPECIMEN '+str(i+1).zfill(3),'P / UNCERTAINTY','PHASE '+str(i//9+1).zfill(2)]):
  tx,_=text(word,.22,C);m.add(tx,tr(-6.4+j*6.4,4.8,-2));m.line([[-6.4+j*6.4,4.5,-2],[-6.4+j*6.4,3.3,-2],[-4+j*4,2.8,-1]],C*.5)
 labels.append(GPU(m))
title=GPU(text('P(doom)',3.2,C)[0]);closing=GPU(text('THE SHOW CONTINUES',1.2,WHITE)[0]);credit=GPU(text('CHIYANG001',.6,C)[0])
# MSAA resolves into an HDR color target, then a restrained optical halo.
ms=ctx.framebuffer(color_attachments=[ctx.renderbuffer((W,H),components=4,samples=4,dtype='f2')],depth_attachment=ctx.depth_renderbuffer((W,H),samples=4))
tex=ctx.texture((W,H),4,dtype='f2');resolved=ctx.framebuffer([tex]);output=ctx.simple_framebuffer((W,H),components=3)
post=ctx.program(vertex_shader='''#version 330
in vec2 p;out vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0,1);}''',fragment_shader='''#version 330
in vec2 uv;uniform sampler2D source;uniform vec2 px;out vec4 f;void main(){vec3 c=texture(source,uv).rgb;vec3 g=vec3(0);for(int i=0;i<12;i++){float a=float(i)*.523599;vec2 d=vec2(cos(a),sin(a));for(int r=1;r<=3;r++){vec3 s=texture(source,uv+d*px*float(r)*2).rgb;g+=max(s-.48,0)/36.;}}c+=g*.23;c=pow(c,vec3(.93));float v=1-.16*dot(uv-.5,uv-.5);f=vec4(c*v,1);}''')
quad=ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],'f4').tobytes());qvao=ctx.vertex_array(post,[(quad,'2f','p')]);post['source']=0;post['px']=(1/W,1/H)
kindmap=[0,1,2,1,0,5,3,4,0,9,5,6,5,3,6,5,8,9,9,8,2,3,4,7,3,10,10,9,8,1,7,8,0,3]

def renderframe(t):
 idx=next((i for i,r in enumerate(lines) if r[0]<=t<r[1]),-1);past=beats[beats<=t];pulse=max(0,1-(t-past[-1])/.18) if len(past) else 0
 if idx>=0:a,b,*_=lines[idx];u=(t-a)/(b-a);kind=kindmap[idx];mode=idx%5
 else:a=t//4*4;u=(t-a)/4;kind=7 if t>141 else 5;mode=0
 local=t-a
 # Small but visible orbit creates parallax across independent depth planes.
 yaw=.22*math.sin(local*.38+idx*.8);eye=np.array([math.sin(yaw)*21,2.0+math.sin(local*.3)*.6,math.cos(yaw)*21]);target=np.array([0,0,-1.2]);vp=perspective(math.radians(43),W/H)@look(eye,target)
 ms.use();ms.clear(.004,.008,.014,1,depth=1);ctx.enable(gl.DEPTH_TEST);ctx.disable(gl.BLEND);ctx.line_width=1.15
 stage.draw(np.eye(4),vp,eye,pulse)
 if idx>=0:
  # Each composition locates type within a different part of the apparatus.
  objpos=[(0,1,-3),(3,1,-3),(0,1,-3),(-2,1,-4),(0,0,-3)][mode]
  model=tr(*objpos)@rot(.12*local+idx*.5,1)@rot(.06*math.sin(t),2)@sc(1.65)
  if kind in [2,3,9]:model=tr(*objpos)@rot(.18*math.sin(local*.4),1)@sc(1.55)
  if kind==7:model=model@sc(.75+u*.65)
  objects[kind].draw(model,vp,eye,pulse,1.15)
  # Moving electrical impulses follow the physical structure.
  for k in range(6):
   aa=t*(.7+k*.03)+k*math.tau/6
   marker.draw(tr(3.9*math.cos(aa),1+3.9*math.sin(aa),-3+.35*math.sin(t+k)),vp,eye,pulse,1.5)
  if idx in [5,14,23,30]:
   phase=max(0,local-1.5);scale=.2+phase*1.8
   if phase>0:burst.draw(tr(0,1,-3)@sc(scale),vp,eye,pulse,max(.15,1-phase*.35))
  if kind==10:
   marker.draw(tr(-6+12*u,.1,-2),vp,eye,pulse,3)

  precision.draw(tr(0,1,-4)@rot(.16*math.sin(t*.4),1)@rot(local*.045,2),vp,eye,pulse)
  labels[idx].draw(np.eye(4),vp,eye,pulse)
  rows=layouts[idx];n=len(rows)
  for j,(words,width,size,rail,radius) in enumerate(rows):
   # typography is suspended at different depths, physically extruded and lit
   entrance=max(0,1-min(1,local/0.48));ease=entrance**3
   if mode==0:x=0;y=-1.3-j*1.75;z=2.0+j*.35;ang=-.26
   elif mode==1:x=-1.5;y=2.1-j*2.1;z=2+j*.5;ang=.28
   elif mode==2:x=0;y=2.5-j*2.;z=1.0+j*.65;ang=-.29
   elif mode==3:x=1;y=-.8-j*2;z=2.5-j*.55;ang=.24
   else:x=0;y=2.4-j*2;z=2+j*.6;ang=-.30
   model=tr(x+ease*2,y-ease*1.8,z-ease*7)@rot(ang,1)@rot(.025*math.sin(local*.5+j),0)
   rail.draw(model,vp,eye,pulse)
   for gpu,wx,wt in words:
    arcx=radius*math.sin(wx/radius);arcz=radius*(1-math.cos(wx/radius));since=t-wt
    lift=max(0,1-min(1,max(0,since)/.24))*.3 if since>=0 else .3
    wm=model@tr(arcx,lift,arcz)@rot(-wx/radius,1)
    gain=.40 if since<0 else 1.0+max(0,1-since/.35)*.35
    gpu.draw(wm,vp,eye,pulse,gain)
  # semantic foreground elements intersect and occlude the typography at the edges
  if kind in [0,5,6,7]:
   small=tr(-8+1.0*math.sin(local*.4),-.5,4.5)@rot(t*.17,1)@sc(.28)
   objects[kind].draw(small,vp,eye,pulse)
 else:
  objects[kind].draw(tr(0,.3,-3)@rot(t*.18,1)@sc(1.8),vp,eye,pulse)
  precision.draw(tr(0,.5,-3)@rot(t*.05,2),vp,eye,pulse)
  title.draw(tr(0,1.1,2)@rot(.15*math.sin(t*.3),1),vp,eye,pulse)
  if t>141:
   closing.draw(tr(0,-1.4,2)@rot(-.12,1),vp,eye,pulse)
   if t>152:credit.draw(tr(0,-3.0,3),vp,eye)
 ctx.copy_framebuffer(resolved,ms);output.use();ctx.disable(gl.DEPTH_TEST);tex.use(0);qvao.render(gl.TRIANGLE_STRIP)
 data=output.read(components=3,alignment=1)
 return data

def main():
 if '--preview' in sys.argv:
  times=[3,7,11,15,19,24,28,31,34,40,43,46,50,55,60,64,67,70,76,79,82,87,92,96,100,103,107,112,117,121,126,129,133,139,146,155]
  sheet=Image.new('RGB',(1920,math.ceil(len(times)/4)*270))
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),renderframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'code3d/preview-{t}.jpg');sheet.paste(im.resize((480,270)),((j%4)*480,j//4*270))
  sheet.save('code3d/storyboard.jpg');print('previews done',flush=True);return
 ff=imageio_ffmpeg.get_ffmpeg_exe();src=str(next(pathlib.Path('.').glob('*.mp4')))
 cmd=[ff,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-i',src,'-map','0:v','-map','1:a','-vf','vflip','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-t',str(DUR),'-movflags','+faststart','output3d/Pdoom_Code_Sculpture_1080p.mp4']
 with open('code3d/render.log','w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for i in range(round(DUR*FPS)):
   p.stdin.write(renderframe(i/FPS))
   if i%300==0:print(f'{i/FPS:.0f} / {DUR:.0f} seconds',flush=True)
  p.stdin.close();p.wait();assert p.returncode==0
if __name__=='__main__':main()
