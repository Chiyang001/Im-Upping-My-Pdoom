import sys,math,json,re,difflib,time,pathlib,subprocess
import numpy as np
import moderngl as gl
import imageio_ffmpeg
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
sys.path.insert(0,'v4');sys.path.insert(0,'code3d')
from engine import Mesh,Pen,tr,sc,rot,perspective,look,unit
from scenes_early import build as early
W,H=1920,1080;FPS=30;DUR=156.667
C=np.array([.2,.93,.8]);WHITE=np.array([.89,.95,1]);ACC=np.array([1,.22,.4]);DARK=C*.2
font=TTFont('C:/Windows/Fonts/arialbd.ttf');gs=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm;cache={}
def contour(ch):
 if ch not in cache:
  name=cmap.get(ord(ch),'question');p=Pen(gs);gs[name].draw(p);cache[ch]=([np.array(c)/upm for c in p.contours],font['hmtx'][name][0]/upm)
 return cache[ch]
def textmesh(s,size=1,color=WHITE,depth=.22,style=-1):
 m=Mesh();width=sum(contour(ch)[1] for ch in s)*size;x=-width/2
 for ch in s:
  cs,adv=contour(ch)
  for c in cs:
   p=np.c_[c*size+[x,0],np.full(len(c),depth)]
   # contour and a second engraved edge, never filled letter faces
   m.line(p,color,closed=True);p2=p.copy();p2[:,2]=0;m.line(p2,color*.20,closed=True)
   if depth>.55:
    for zz in np.linspace(0,depth,max(3,int(depth*5)))[1:-1]:
     pp=p.copy();pp[:,2]=zz;m.line(pp,color*.12,closed=True)
   for k in range(0,len(c),max(2,len(c)//9)):
    m.line([p[k],p2[k]],color*.23)
  # True woven glyphs and paperclip link glyphs use the font outline as geometry, not as a texture.
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
 return m,width
ctx=gl.create_standalone_context(require=330)
print('GPU:',ctx.info['GL_RENDERER'],flush=True)
vs='''#version 330
in vec3 pos;in vec3 color;in vec2 data;uniform mat4 model;uniform mat4 vp;uniform float clock;uniform float energy;uniform float action;uniform int motion;out vec3 C;out float phase;out float dist;
void main(){vec3 p=pos;float seed=data.y;
 if(motion==0){p.y*=1.-energy*.13;p.z+=sin(p.x*9.+clock*8.)*energy*.08;}
 if(motion==1){p.z+=sin(p.x*1.9+clock*7+p.y)*energy*.18;}
 if(motion==2){p.y-=action*3.*smoothstep(-1.,2.,p.x);p.x+=sin(p.z*.8+clock*4)*energy*.1;}
 if(motion==3){p.y+=sign(p.y)*energy*.22;p.x+=sin(p.y+clock*3)*action*.5;}
 if(motion==4){p.y*=1.-action*.25;p.y+=sign(p.y)*energy*.3;}
 if(motion==5){p.xy*=1.+action*.65;p.z-=action*length(p.xy)*.3;p.xy+=vec2(sin(seed*91.),cos(seed*53.))*energy*.7;}
 if(motion==6){p.z=mod(p.z+clock*(6.+energy*8.)+28.,36.)-28.;p.x+=sin(p.z*.4)*action;}
 if(motion==7){p.x+=sign(p.x)*action*4.;p.y+=sin(p.x*.8+clock*2)*.4;}
 if(motion==8){p.z+=sin(p.x*.5+clock*3)*energy*.5;}
 if(motion==9){p.y+=sin(p.x*2.-clock*8)*energy*.45;}
 if(motion==10){float a=action*.5+energy*.05;mat2 r=mat2(cos(a),-sin(a),sin(a),cos(a));p.xy=r*p.xy;p.xy*=1.-action*.35;p.z-=action*2.;}
 if(motion==11){p.z=mod(p.z+clock*(18.+action*20.)+42.,52.)-42.;p.xy*=1.+energy*.05;}
 if(motion==12){p+=vec3(sin(seed*53.),cos(seed*37.),sin(seed*21.))*action*3.;p.z+=sin(clock*3.+seed*9.)*energy;}
 if(motion==13){p.x+=sign(p.x)*(action*3.-energy*.3);}
 if(motion==14){p.x+=sin(p.y*.7-clock*3.)*action*1.7;p.z+=sin(p.y*.5+clock*2)*.7;}
 if(motion==15){p.y+=action*.2*p.x;p.z+=sin(clock*4.+p.x)*energy*.2;}
 if(motion==16){p.y+=sin(clock*8.+p.z)*energy*.24;p.z=mod(p.z+clock*8.+25.,35.)-25.;}
 if(motion==17){p.x+=sign(p.x)*action*2.;p.y-=action*abs(p.x)*.18;}
 if(motion==18){p.x+=sin(clock*7.+p.y)*energy*.22;p.z+=action*sin(p.x)*.5;}
 if(motion==19){p.y-=action*action*(1.+smoothstep(-14.,14.,p.x))*4.;p.x+=sin(seed*20.)*action;}
 if(motion==20){p.z+=energy*.6;}
 if(motion==21){p.y-=action*abs(p.x)*.2;p.z+=energy*.4;}
 if(motion==22){p.y+=sin(p.x*.6-clock*3.)*(.25+energy*.4);p.x*=1.+action*.12;}
 if(motion==23){p.xy*=1.-action*.25;p.z=mod(p.z+clock*(6.+action*8.)+20.,30.)-20.;}
 if(motion==24){p.x*=1.-action*.25;p.y+=energy*.2*sin(p.x);}
 if(motion==25){p.y+=sin(p.x*3.-clock*10.)*energy*.15;}
 if(motion==26){p.y+=sin(p.x*1.5+clock*5.)*(.2+energy*.4);p.z+=sin(p.x*1.7-clock*3)*.15;}
 if(motion==27){p.x+=action*sin(p.y*.6)*4.;p.z+=action*cos(p.x*.4)*3.;}
 if(motion==28){p+=vec3(sign(p.x)*3.,sign(p.y)*2.,sin(seed*30.)*3.)*action;}
 if(motion==29){p.x+=sin(floor(p.y)*.8+clock*4.)*action*4.5;p.z+=energy*.7;}
 if(motion==30){p.z+=sin(p.x*.6+clock*3.)*action*1.5;p.y+=sin(p.x*1.2+p.z*.7-clock*4.)*energy*.2;}
 if(motion==31){p.z=mod(p.z+clock*(5.+action*8.)+24.,32.)-24.;p.xy*=1.+sin(clock*2.+p.z)*energy*.08;}
 if(motion==32){p.z-=action*2.;}
 if(motion==33){p.z+=action*p.x*.5;p.y-=action*abs(p.x)*.15;}
 if(motion==34){p.x*=1.+action*2.2;p.y+=sin(p.x*.9+clock*2.)*action*.5;p.z-=action*abs(p.x)*.3;}
 vec4 world=model*vec4(p,1);gl_Position=vp*world;C=color;phase=data.x;dist=gl_Position.w;}
'''
fs='''#version 330
in vec3 C;in float phase;in float dist;uniform float gain;uniform float reveal;uniform float tracer;uniform float text_role;uniform vec4 clearBox;out vec4 frag;
void main(){if(phase>reveal)discard;float tip=1.+2.*exp(-abs(phase-reveal)*80.)*tracer;vec2 screen=gl_FragCoord.xy/vec2(1920.,1080.)*2.-1.;float zone=length((screen-clearBox.xy)/max(clearBox.zw,vec2(.02)));float room=mix(.30,1.,smoothstep(.55,1.5,zone));room=mix(room,1.,text_role);frag=vec4(C*gain*tip*exp(-max(0.,dist-18.)*.008)*room,1);}'''
prog=ctx.program(vertex_shader=vs,fragment_shader=fs)
class GPU:
 def __init__(self,m,role=0):
  self.role=role
  a=np.array(m.l,'f4');self.count=len(a)
  self.bmin=a[:,:3].min(axis=0) if len(a) else np.zeros(3);self.bmax=a[:,:3].max(axis=0) if len(a) else np.ones(3)
  if self.count==0:self.vao=None;return
  n=len(a)//2;phase=np.repeat(np.arange(n)/max(1,n-1),2);seed=np.repeat(np.mod(np.arange(n)*.6180339,1),2)
  a=np.c_[a,phase,seed].astype('f4');self.buf=ctx.buffer(a.tobytes());self.vao=ctx.vertex_array(prog,[(self.buf,'3f 3f 2f','pos','color','data')])
 def draw(self,model,vp,clock=0,energy=0,action=0,motion=-1,gain=1,reveal=1):
  if not self.vao:return
  prog['model'].write(np.array(model.T,'f4').tobytes());prog['vp'].write(np.array(vp.T,'f4').tobytes())
  prog['text_role'].value=float(self.role)
  for key,val in [('clock',clock),('energy',energy),('action',action),('motion',motion),('gain',gain),('reveal',reveal),('tracer',1. if reveal<1 else 0.)]:prog[key].value=val
  self.vao.render(gl.LINES)
lines=json.load(open('work/lyrics.json'));trans=json.load(open('work/transcript.json'));rhythm=json.load(open('code3d/rhythm_v3.json'))
hits=np.array([x['t'] for x in rhythm['impacts']]);strength=np.array([x['strength'] for x in rhythm['impacts']]);htypes=[x['type'] for x in rhythm['impacts']]
# Every sentence has a separate spatial typographic score. Rows specify width, position and axis rotation.
# text, width, x, y, z, rotationY, rotationZ, curve radius
S=[
 [('I see sparks of',17,0,3.8,1,0,0,12),('AGI',11,0,-.1,1,0,0,0),('in your eyes',17,0,-3.3,1,0,0,-13)],
 [('Your circuits make me',24,-1,3.2,1,.2,-.06,0),('nervous',21,0,-.2,2,-.12,.06,0),("that's no surprise",22,1,-3.2,1,.12,0,0)],
 [('There was a sudden',24,-2,4,1,.2,0,0),('drop',9,6,.0,3,.25,-.15,0),('in your training loss',23,-1,-3,3,.25,0,25)],
 [("Now I'm your servant",21,-1,-3,1,-.2,0,0),("and you're my boss",26,0,3,0,.1,0,0)],
 [('ChatGPT,',23,0,3.6,0,.05,0,18),("please don't",18,0,.2,2,0,0,0),('eat me alive',24,0,-3.4,2,-.05,0,-18)],
 [("I'm upping my",18,-2,4.6,0,.12,0,0),('P(doom)',24,0,.2,2,-.1,0,20),("'cause the future goes",24,-1,-2.8,2,-.1,0,0),('foom',11,8,-5,4,-.1,0,0)],
 [('Trapped in the',19,-3,4,2,.25,0,0),('Chinese room',25,0,.5,1,0,0,0),('with a bag of shrooms',25,0,-3.2,3,-.2,0,0)],
 [('See through the',19,-4,4,2,.18,-.04,0),("shoggoth's",24,1,.1,1,-.1,.02,0),('lies',10,7,-3.6,5,-.2,0,0)],
 [('With your',15,-7,4.3,3,.2,0,0),('Shinigami eyes',30,0,-.7,2,0,0,32)],
 [('We had a stable',24,-1,3.3,2,0,0,0),('training run',25,0,-1,2,0,0,0)],
 [("But now the",18,-6,4,2,.2,-.05,0),("singularity's begun",27,0,-.2,3,-.15,0,16)],
 [("And you're",15,-8,4.5,2,.3,0,0),('optimizing,',22,-1,1,3,.2,.08,0),('accelerating',28,0,-3.4,4,-.2,-.05,0)],
 [('I feel my',16,-7,4,2,.25,0,0),('atoms',14,1,.3,2,0,0,0),('rearranging',26,0,-3.4,2,-.2,0,0)],
 [('Sydney,',20,-3,4,2,.25,0,0),('please let me free',28,0,-1,2,-.15,0,0)],
 [("I'm upping my",20,-4,4.3,2,.2,0,0),('P(doom)',23,-2,.6,3,.2,0,0),('I hear the basilisk boom',28,0,-3.5,3,-.2,0,24)],
 [('NVDA to the moon',27,0,2.7,2,-.1,.08,0),("the Omega Point's",24,-1,-1,3,.1,.06,0),('coming soon',19,3,-3.7,3,.1,.08,0)],
 [('1e30',23,-3,2,2,.3,0,0),('flops a second',26,0,-2.7,3,-.2,0,0)],
 [('"That was safe enough"',28,0,2,2,.12,0,20),('we reckoned',21,0,-2.5,3,-.15,0,0)],
 [('Forward MLP,',25,0,3,2,.12,0,0),('backward, repeat',27,0,-2.2,3,-.12,0,0)],
 [("Now von Neumann's",28,0,3.3,2,.16,0,0),('obsolete',25,0,-1.6,3,-.16,0,0)],
 [('Sharp left turn',26,0,1,3,0,0,0),('and there you are',26,3,-1,0,math.pi/2,0,0)],
 [('Without a single',26,0,3.3,2,.16,0,0),('CDR',18,0,-1.5,3,-.1,0,0)],
 [('Gato,',17,-5,4,1,.3,-.07,0),("please don't",22,0,.3,2,0,0,20),('let me go',22,3,-3.4,3,-.3,.06,0)],
 [("I'm upping my",19,-5,4,2,.2,0,0),('P(doom)',25,0,.2,3,0,0,20),('as paperclips fill the room',30,0,-3.6,2,-.14,0,0)],
 [('Killswitch guys on PTO',29,0,3.3,2,.15,0,0),("now there's nowhere",27,0,-.5,2,-.1,0,0),('left to go',20,5,-3.6,4,-.1,0,0)],
 [('Too late now,',23,-2,3.5,2,.2,0,18),('we lit the fuse',28,0,-1.5,3,-.15,0,-25)],
 [('Orthogonality',29,0,3,2,.1,.04,0),('thesis',16,-5,-.7,3,.4,-.05,0),('blues',17,6,-3.4,3,-.3,.05,0)],
 [('"Just transformers',29,0,4,2,.2,0,0),('all the way"',21,-4,.2,2,.1,0,0),("'til you learned to disobey",30,0,-3.6,3,-.2,0,0)],
 [('Post-Chinchilla,',26,0,3.5,2,.1,0,0),('super-dense,',24,-2,.2,3,-.1,0,0),('breaking through each safety fence',32,0,-3.5,3,-.1,0,0)],
 [('Hundred thousand GPU',30,0,3.1,2,.12,0,0),('RLHF goes askew',29,0,-1.9,3,-.2,.06,0)],
 [("I'm upping my",20,-5,4,2,.2,0,0),('P(doom)',26,0,.2,3,0,0,20),('just as foretold by Loom',30,0,-3.7,3,-.2,0,0)],
 [('From masked pre-training days',32,0,3,2,.1,0,0),('to recursive self-upgrade',31,0,-1.7,3,-.1,0,0)],
 [('What did Ilya see?',28,0,2.5,2,.14,0,15),("We'll never know",27,0,-2.2,3,-.14,0,-16)],
 [('Was it all',23,-3,3,2,.12,0,0),('for show?',26,1,-1.8,3,-.1,0,0)]
]
# Semantic placement edits are intentionally explicit, one score per sentence.
S[2]=[('There was a sudden',25,-1,2,-5,.12,-.18,0),('drop',12,5,-.5,0,.1,-.48,0),('in your training loss',24,0,-3,-4,.1,0,0)]
S[3]=[("Now I'm your servant",21,-1,-3.8,-1,-.25,0,0),("and you're my boss",29,0,3.3,-3,.15,0,0)]
S[6]=[('Trapped in the',18,0,4,-8,0,0,0),('Chinese room',18,-4,1,-8,.6,0,0),('with a bag of shrooms',21,4,-3,-10,-.6,0,0)]
S[7]=[('See through the',19,-6,4.4,0,.2,-.08,0),("shoggoth's",25,0,.4,-3,.2,0,22),('lies',12,5,-3,1,-.2,0,0)]
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
DEPTH={0:.5,1:.65,2:.5,3:2.2,4:1.7,5:6.5,6:1.4,7:.5,8:.5,9:.75,10:1.8,11:1.2,12:.6,13:3.3,14:3.0,15:1.4,16:4.0,17:1.2,18:1.5,19:3.5,20:2.8,21:3.7,22:.7,23:4.5,24:3.3,25:.7,26:.8,27:3.5,28:2.4,29:2.,30:.7,31:4.,32:1.3,33:4.2}
def norm(x):return re.sub('[^a-z0-9]','',x.lower())
rows=[]
for idx,(r,spec) in enumerate(zip(lines,S)):
 a,b,_,lyric,key=r;allwords=[w for sr in spec for w in sr[0].split()];ws=[w for q in trans for w in q['words'] if a-.12<=w['start']<b];m=difflib.SequenceMatcher(None,[norm(x) for x in allwords],[norm(x['word']) for x in ws],autojunk=False);timing={}
 for bl in m.get_matching_blocks():
  for k in range(bl.size):timing[bl.a+k]=ws[bl.b+k]['start']
 for j in range(len(allwords)):
  if j not in timing:
   lo=max([k for k in timing if k<j],default=-1);hi=min([k for k in timing if k>j],default=len(allwords));timing[j]=timing.get(lo,a)+(timing.get(hi,b-.2)-timing.get(lo,a))*(j-lo)/(hi-lo)
 out=[];wi=0
 for rowid,sr in enumerate(spec):
  phrase,width,x,y,z,ry,rz,rad=sr;raw=sum(contour(c)[1] for c in phrase.upper());size=width/max(.1,raw);cx=-width/2;words=[]
  for word in phrase.upper().split():
   wm,ww=textmesh(word,size,C if 'P(DOOM)' in word else ACC if word in ['AGI','1E30','CDR','LIES','ASKEW','FOOM'] else WHITE,depth=DEPTH[idx],style=idx if rowid==1 and idx in [23,30] else -1)
   wx=cx+ww/2;cx+=ww+contour(' ')[1]*size
   # Bend every vertex, not just each word's origin, so the letter strokes form a real spatial surface.
   for v in wm.l:
    gx=v[0]+wx
    if rad:v[0]=rad*math.sin(gx/rad);v[2]+=rad*(1-math.cos(gx/rad))
    else:v[0]=gx
    if idx==10 and rowid==1:
     th=gx/20+math.pi/2;rr=9+v[1];v[0]=rr*math.cos(th);v[1]=rr*math.sin(th)-6;v[2]=v[2]*.3
    if idx==15 and rowid==0:v[1]+=.023*(gx+11)**2-3;v[2]+=-.25*(gx+11)-3
    if idx==30 and rowid==1:v[2]+=.35*math.sin(gx*.75+v[1]*1.4)
   # The letter's own strokes become columns/rails, not a separate title floating in front.
   if idx in [1,3,6,13,16,19,21,23,24,27,28,29,31,33]:
    for vv in wm.l[::max(4,len(wm.l)//16)]:
     pp=np.array(vv[:3]);qq=pp.copy();qq[2]-=DEPTH[idx]*1.6;wm.line([pp,qq],C*.27)
   words.append((GPU(wm,1),wx,timing[wi],ww));wi+=1
  # Actual structural traces attach to the glyphs, with a distinct geometry in every sentence.
  scaffold=Mesh()
  for j,(_,wx,wt,ww) in enumerate(words):
   if idx in [0,4,8,10,14,30]:
    for k in range(5):scaffold.line([[wx,-.12,k*.035],[wx,-.6,k*.035],[wx+(-1)**j*1.2,-1.2,-1.5],[wx*1.2,-2.0,-4]],C*.4)
   elif idx in [1,3,9,13,16,18,19,21,24,27,28,29,31]:
    for k in range(4):scaffold.line([[wx+ww*.3,-.1,k*.04],[wx+ww*.3,-.55,k*.04],[wx-ww*.3,-.55,k*.04],[wx-ww*.3,-.9,-.5]],C*.6)
   else:
    scaffold.line([[wx,-.15,0],[wx,-.65,0],[wx+ww*.45,-.65,-.3]],ACC*.6)
  out.append((words,GPU(scaffold),sr))
 rows.append(out)
print('outline typography built',flush=True)
# Temporal samples do not require the old renderer or any bitmap asset.
try:
 from scenes_late_v4 import build_late
except ImportError:build_late=None
environments=[]
for i in range(34):
 m=early(i) if i<17 else build_late(i,Mesh,np,math,C,WHITE,ACC) if build_late else Mesh()
 environments.append(GPU(m));print('scene',i,'segments',len(m.l)//2,flush=True)
# Impact material: anisotropic shards and high-speed streaks, not an ornament in the middle.
shards=Mesh();rng=np.random.default_rng(14)
for j in range(380):
 v=unit(rng.normal(size=3));r=rng.uniform(1,10);shards.line([v*r,v*(r+rng.uniform(.3,4))],ACC if j%6==0 else C*.7)
shards=GPU(shards)
# Custom cameras: start eye / end eye / target / roll / lens. No shared orbit rig.
CAM=[
 ([3,2,19],[-3,1,22],[0,0,-2],-.07,44),
 ([-7,4,23],[6,1,22],[0,0,-2],.05,43),
 ([6,7,24],[0,1,22],[0,0,-1],-.10,48),
 ([-5,-3,23],[3,4,24],[0,0,-2],.06,46),
 ([0,1,23],[2,0,26],[0,0,-3],0,46),
 ([-4,2,24],[4,-1,27],[0,0,-3],-.06,48),
 ([5,3,24],[-4,0,23],[0,0,-3],.08,48),
 ([-5,3,24],[3,-1,24],[0,0,-2],-.08,47),
 ([0,-1,25],[0,2,28],[0,0,-3],.03,46),
 ([-4,2,24],[4,2,24],[0,0,-3],0,44),
 ([5,7,25],[-3,1,23],[0,0,-5],-.12,48),
 ([-3,-1,24],[3,2,24],[0,0,-6],.07,48),
 ([4,2,25],[-4,4,23],[0,0,-2],-.05,47),
 ([-5,1,24],[5,1,24],[0,0,-4],.04,48),
 ([6,-2,26],[-3,4,25],[0,0,-3],-.10,48),
 ([-5,-1,26],[4,5,25],[0,0,-4],-.06,48),
 ([5,-3,25],[-3,4,24],[0,0,-4],.04,48),
 ([-2,4,24],[4,-1,24],[0,0,-4],-.06,47),
 ([-6,2,26],[6,-1,25],[0,0,-4],.05,47),
 ([4,-3,25],[-3,3,26],[0,0,-4],-.03,48),
 ([0,1,25],[25,1,0],[0,0,0],0,48),
 ([-5,3,25],[4,-2,25],[0,0,-4],.08,48),
 ([-5,2,25],[5,-1,25],[0,0,-3],-.06,48),
 ([3,0,26],[-2,2,29],[0,0,-4],.04,48),
 ([-6,-2,26],[5,2,25],[0,0,-4],-.05,48),
 ([-4,3,25],[5,-1,25],[0,0,-3],.06,48),
 ([6,6,27],[-4,-1,25],[0,0,-3],-.07,48),
 ([-4,3,26],[4,-2,25],[0,0,-3],.05,48),
 ([2,-2,26],[-3,3,26],[0,0,-5],-.05,49),
 ([-5,5,27],[4,1,25],[0,0,-3],.08,48),
 ([5,3,27],[-5,-1,26],[0,0,-4],-.08,48),
 ([-3,1,27],[3,3,25],[0,0,-5],.05,48),
 ([2,2,26],[0,1,24],[0,0,-4],-.02,47),
 ([0,1,26],[6,3,25],[0,0,-4],.06,48)]
CAM[0]=([5,3,18],[-5,1,23],[0,0,-3],-.12,52)
CAM[1]=([-12,5,22],[9,-1,20],[0,0,-4],.14,53)
CAM[2]=([11,11,22],[3,4,20],[0,-1,-4],-.16,56)
CAM[3]=([-8,-8,24],[7,7,24],[0,0,-3],.12,57)
CAM[4]=([0,1,21],[3,-1,29],[0,0,-4],.04,55)
CAM[5]=([-11,3,24],[9,-2,26],[0,0,-5],-.14,58)
CAM[6]=([0,1,18],[2,0,14],[0,0,-12],.08,66)
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
# Wide coverage / MSAA resolve / bloom / brief directional kick distortion.
ms=ctx.framebuffer([ctx.renderbuffer((W,H),components=4,samples=4,dtype='f2')],ctx.depth_renderbuffer((W,H),samples=4));tex=ctx.texture((W,H),4,dtype='f2');resolve=ctx.framebuffer([tex]);output=ctx.simple_framebuffer((W,H),components=3)
post=ctx.program(vertex_shader='''#version 330
in vec2 p;out vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0,1);}''',fragment_shader='''#version 330
in vec2 uv;uniform sampler2D source;uniform vec2 px;uniform float impact;uniform float flash;uniform float paper;out vec4 frag;
void main(){vec2 q=(uv-.5)*(1.-impact*.024)+.5;vec3 c=texture(source,q).rgb;vec3 glow=vec3(0);for(int j=0;j<8;j++){float a=float(j)*.785398;for(int k=1;k<=3;k++){vec2 v=vec2(cos(a),sin(a))*px*float(k)*2.;glow+=max(texture(source,q+v).rgb-.35,0)/24.;}}c+=glow*.85;c+=vec3(.06,.15,.13)*flash;vec3 p=vec3(.94,.95,.925)-min(vec3(1.05),c*1.65)*.89;c=mix(c,p,paper);frag=vec4(pow(max(c,0),vec3(.91)),1);}''')
qb=ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],'f4').tobytes());q=ctx.vertex_array(post,[(qb,'2f','p')]);post['source']=0;post['px']=(1/W,1/H)
def ease(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def stroke_title(s,size,col):return GPU(textmesh(s,size,col)[0],1)
endtitle=stroke_title('P(doom)',4.5,C);endclaim=stroke_title('PROBABILITY / UNBOUNDED',.8,WHITE);endname=stroke_title('CHIYANG001',.5,C)
SHOT=[]
for ii,rrs in enumerate(rows):
 data=[]
 for jj,(words,scaffold,sr) in enumerate(rrs):
  phrase,width,x,y,z,ry,rz,rad=sr;bm=tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((ii,jj),0),0)
  points=[]
  for gpu,wx,wt,ww in words:
   for xx in [gpu.bmin[0],gpu.bmax[0]]:
    for yy in [gpu.bmin[1],gpu.bmax[1]]:
     for zz in [gpu.bmin[2],gpu.bmax[2]]:points.append((bm@np.array([xx,yy,zz,1]))[:3])
  pp=np.array(points);center=(pp.min(axis=0)+pp.max(axis=0))*.5;normal=unit(bm[:3,:3]@np.array([0.,0.,1.]))
  tt=words[0][2];near=hits[np.argmin(abs(hits-tt))];tt=float(near) if abs(near-tt)<.16 else tt
  data.append((tt,center,pp,normal))
 SHOT.append(data)
endnetwork=Mesh()
base,_=textmesh('P(doom)',3.5,C,depth=1.2)
for j in range(32):endnetwork.add(base,tr(0,0,-j*.65)@sc(1+j*.035))
endnetwork=GPU(endnetwork)
infinity=Mesh()
for j in range(18):
 zz=(j-9)*.045
 infinity.line([[10*math.cos(a)/(1+math.sin(a)**2),7*math.sin(a)*math.cos(a)/(1+math.sin(a)**2),zz] for a in np.linspace(0,math.tau,500)],C*(.45 if j else 1.))
infinity=GPU(infinity,1)
endformula=stroke_title('P(doom) = '+chr(8734),1.0,WHITE)
# Per-scene semantic timing markers: measured drum hits nearest the lyric's event.
EVENT=[2.055,5.70,10.235,14.56,18.885,23.18,27.28,30.23,34.79,38.19,42.05,45.69,49.785,53.885,58.43,62.96,66.595,70.23,75.69,79.32,81.96,86.59,92.05,96.59,100.23,103.41,107.05,113.41,116.59,121.14,125.69,129.32,133.41,139.32]
def beatstate(t):
 k=np.searchsorted(hits,t,'right')-1
 if k<0:return 0,0
 age=t-hits[k];return float(strength[k]*math.exp(-age/.075)),float(strength[k]*math.exp(-age/.18))
def drawframe(t):
 global last_camera_stats
 idx=next((i for i,r in enumerate(lines) if r[0]<=t<r[1]),-1)
 # In instrumental gaps, continue the preceding physical scene instead of inserting a reused idle loop.
 if idx<0:
  idx=max(0,min(33,np.searchsorted([r[0] for r in lines],t,'right')-1))
 a,b,*_=lines[idx];u=np.clip((t-a)/(b-a),0,1);local=t-a;sharp,hit=beatstate(t);event=EVENT[idx];action=ease((t-event)/.65)
 ce,cf,ct,roll,fov=CAM[idx];ce=np.array(ce,float);cf=np.array(cf,float);target=np.array(ct,float)
 if idx==20:
  ang=ease((t-81.96)/.28)*math.pi/2;eye=np.array([25*math.sin(ang),1,25*math.cos(ang)])
 else:eye=ce*(1-ease(u))+cf*ease(u)
 # Two material shots per line: a short physical dolly impact and an alternate off-axis cut.
 alt=1 if t>CUTS[idx] and idx not in [0,9,20,32] else 0
 eye+=np.array([(-1)**idx*3.7*alt,1.1*alt,-2.2*alt])
 eye+=np.array([math.sin(t*73)*sharp*.4,math.cos(t*61)*sharp*.3,-sharp*.9])
 # In the last phrase the sideward move reveals the letters as separate depth planes.
 macro=0.
 if idx in [0,4,5,7,10,11,14,16,23,28,30,31]:
  age=t-EVENT[idx]
  macro=max(0,1-abs(age-.18)/.26)*(.15 if idx in [4,7] else .23)
  eye=target+(eye-target)*(1-macro)
 if idx==5:
  blast=ease((t-25.685)/.22);eye=target+(eye-target)*(1+blast*.28)
 if idx==14:eye[0]+=math.sin(local*1.8)*action*1.5
 if idx==23:eye[2]+=action*3.0
 if idx==28:eye[2]-=action*2.0
 if idx==32:eye[2]-=ease(u)*1.5
 # Match the active word-bearing structure to a readable hero shot. Other words remain real scenery around it.
 active=0
 for jj,info in enumerate(SHOT[idx]):
  if t>=info[0]-.04:active=jj
 st,focus,pp,normdir=SHOT[idx][active];plan=unit(eye-target)
 direction=unit(plan*.55+normdir*.45)
 if idx in [6,18,26]:direction=unit(plan*.3+normdir*.7)
 right=unit(np.cross([0,1,0],direction));up=unit(np.cross(direction,right));rel=pp-focus
 hw=max(abs(rel@right));hh=max(abs(rel@up));hz=max(abs(rel@direction))
 theta=math.tan(math.radians(fov)/2)
 distance=max(hw/(theta*(W/H)*.80),hh/(theta*.70))+hz*.55
 distance=max(10.5,min(35.,distance))
 # Brief macros happen after an established readable contour, and give way to a new held angle.
 distance*=1-macro*.5
 eye=focus+direction*distance;target=focus
 if idx==5 and t>25.685:eye=target+(eye-target)*(1+ease((t-25.685)/.20)*.3)
 if idx==20 and active==1:eye=target+unit([1,.12,.03])*distance
 rr=roll*math.sin(u*math.pi)*.65+sharp*.01*(-1)**idx
 view=rot(rr,2)@look(eye,target);vp=perspective(math.radians(fov-hit*1.8),W/H,far=180)@view
 # Protect the sung structure, while already-read foreground strokes may pass outside the lens.
 for attempt in range(4):
  ck=np.c_[pp,np.ones(len(pp))]@vp.T;nn=ck[:,:3]/ck[:,3:4];edge=max(abs(nn[:,:2]).max(),.01)
  if edge<=.945:break
  eye=target+(eye-target)*(edge/.93);view=rot(rr,2)@look(eye,target);vp=perspective(math.radians(fov+hit*.35),W/H,far=180)@view
 clip=np.c_[pp,np.ones(len(pp))]@vp.T;ndc=clip[:,:3]/clip[:,3:4]
 last_camera_stats={'t':float(t),'idx':int(idx),'row':int(active),'xmin':float(ndc[:,0].min()),'xmax':float(ndc[:,0].max()),'ymin':float(ndc[:,1].min()),'ymax':float(ndc[:,1].max())}
 # Dim only the immediately sung word's neighborhood; all geometry remains in the same depth-tested scene.
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
 ms.use();ms.clear(.002,.005,.009,1,depth=1);ctx.enable(gl.DEPTH_TEST);ctx.disable(gl.BLEND);ctx.line_width=1.2
 # Semantic deformation is in the line geometry itself, independent of the camera.
 envmodel=np.eye(4)
 if idx==0:envmodel=tr(0,0,-1)@sc(1.3)
 elif idx==7:envmodel=tr(3,0,-1)@rot(-.24,2)@sc(1.15)
 elif idx==8:envmodel=sc(1.35)
 elif idx==14:envmodel=tr(-3,-1,-3)@rot(.58,2)@rot(.5,1)@sc(1.1)
 elif idx==10:envmodel=rot(-.22,0)@sc(1.15)
 elif idx==5:envmodel=tr(1,0,-2)@rot(.22,1)@sc(1.2)
 if idx==5:
  blast=ease((t-25.685)/.2);envmodel=envmodel@sc(1+blast*1.6)
 if idx==4:
  close=.22*(math.exp(-abs(t-18.885)/.12)+math.exp(-abs(t-20.235)/.12));envmodel=envmodel@np.diag([1,1-close*1.8,1,1])
 if idx==7:envmodel=tr(action*2.5,0,0)@envmodel
 if idx==14:envmodel=tr(action*3-2,0,0)@envmodel
 if idx==17:envmodel=envmodel@rot(action*.25,2)
 if idx==23:envmodel=envmodel@sc(1+action*.5)
 if idx==28:envmodel=tr(0,0,action*4)@envmodel
 if idx==29:envmodel=envmodel@rot(action*.2,2)
 if idx==30:envmodel=envmodel@np.diag([1,1+hit*.12,1,1])
 environments[idx].draw(envmodel,vp,t,hit*1.7,action,idx,gain=1.05)
 for j,(words,scaffold,sr) in enumerate(rows[idx]):
  phrase,width,x,y,z,ry,rz,rad=sr;typemodel=tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((idx,j),0),0)
  if idx==2:
   typemodel=tr(0,-action*(2 if j==1 else .5),0)@typemodel
  elif idx==3:
   typemodel=tr(0,hit*(.15 if j else -.12),0)@typemodel
  elif idx==4:typemodel=tr(0,(-1)**j*hit*.15,-action*j*.3)@typemodel
  elif idx==5:
   if j==1:typemodel=typemodel@sc(1+sharp*.08)
   if t>25.685:
    blast=ease((t-25.685)/.22);typemodel=tr((-1)**j*blast*(j+1)*.5,blast*(1-j)*.3,-blast*j*.7)@typemodel
   if j==3:typemodel=typemodel@sc(1+max(0,1-abs(t-25.53)/.2)*.35)
  elif idx==11:typemodel=tr(sharp*(-1)**j*.4,0,0)@typemodel
  elif idx==12:typemodel=tr(math.sin(j*3)*action*.35,math.cos(j*3)*action*.25,0)@typemodel
  elif idx==14:typemodel=tr(math.sin(local*2+j)*hit*.55,0,math.sin(local+j)*action*.4)@typemodel
  elif idx==18 and j==1:typemodel=tr(-math.sin(local*5)*hit*.5,0,0)@typemodel
  elif idx==19:typemodel=tr(0,-action*max(0,u-.4)*2,0)@typemodel
  elif idx==21 and j==1:typemodel=tr(math.sin(local*20)*hit*.1,-action*.4,0)@typemodel
  elif idx==26:typemodel=tr(0,math.sin(local*6+j)*hit*.2,0)@typemodel
  elif idx==27:typemodel=tr(action*math.sin(j*2)*.7,0,action*j*.15)@typemodel
  elif idx==29:typemodel=tr(math.sin(t*8+j)*action*.3,0,0)@typemodel
  elif idx==30:typemodel=tr(0,math.sin(local*6+j)*hit*.35,0)@typemodel
  elif idx==33:typemodel=tr(0,0,-action*j*.7)@typemodel
  scaffold.draw(typemodel,vp,t,hit,gain=.7)
  for k,(gpu,wx,wt,ww) in enumerate(words):
   since=t-wt;reveal=float(np.clip((since+.04)/.22,0,1));gain=.48 if since<-.04 else 1.30+max(0,1-since/.20)*1.0
   wm=typemodel
   # Hand-traced letters connect into the apparatus; semantic breaks happen after legibility window.
   if idx==12 and since>.5:
    amt=math.sin(ease((since-.5)/1.)*math.pi)*.8;wm=wm@tr(math.sin(k*7+j)*amt,math.cos(k*5+j)*amt,math.sin(k*3)*amt)
   if idx==28 and since>.7:wm=wm@tr(math.sin(k*5)*hit*.25,math.cos(k*7)*hit*.2,0)
   if idx==23:wm=wm@tr(0,0,-sharp*.12)
   ctx.line_width=1.9 if since<.4 and since>=0 else 1.55
   if since>=-.04 and reveal<1:
    ctx.depth_func='<=';gpu.draw(wm,vp,t,hit,0,-1,.50,1);gpu.draw(wm,vp,t,hit,0,-1,gain,reveal);ctx.depth_func='<'
   else:gpu.draw(wm,vp,t,hit,0,-1,gain,1)
  ctx.line_width=1.2
 # Percussive events generate actual moving fragments across the lens.
 if idx in [5,7,10,14,16,20,23,25,27,28,29,30,31]:
  phase=t-(25.685 if idx==5 else EVENT[idx])
  if 0<phase<.7:shards.draw(tr(0,0,2)@sc(.3+phase*12),vp,t,hit,gain=(1-phase/.7)*1.4)
 if t>141.2:
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
 ctx.copy_framebuffer(resolve,ms);output.use();ctx.disable(gl.DEPTH_TEST);tex.use(0)
 paper=1. if idx in [9,17,18,21,26] and t<141 else 0.
 post['paper']=paper;post['impact']=sharp;post['flash']=sharp*.2;q.render(gl.TRIANGLE_STRIP)
 return output.read(components=3,alignment=1)
def main():
 if '--audit' in sys.argv:
  audit=[]
  for t in np.arange(1.5,141,.25):drawframe(float(t));audit.append(last_camera_stats)
  json.dump(audit,open('v4/framing_audit.json','w'),indent=2);print('audit samples',len(audit),flush=True);return
 if '--preview' in sys.argv:
  times=[(r[0]+r[1])*.5 for r in lines]+[146,155];sheet=Image.new('RGB',(1920,9*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v4/preview-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{j:02} / {t:.2f}s',fill='white')
  sheet.save('v4/storyboard.jpg');print('preview saved',flush=True);return
 ff=imageio_ffmpeg.get_ffmpeg_exe();src=str(next(pathlib.Path('.').glob('*.mp4')));dest='output_v4/Pdoom_Line_Architecture_1080p.mp4'
 if '--sample' in sys.argv:
  start=float(sys.argv[sys.argv.index('--sample')+1]);duration=8;dest=f'v4/sample-{int(start)}.mp4'
 else:start=0;duration=DUR
 cmd=[ff,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-ss',str(start),'-i',src,'-map','0:v','-map','1:a','-vf','vflip','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-t',str(duration),'-movflags','+faststart',dest]
 with open('v4/render.log','w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for i in range(round(duration*FPS)):
   p.stdin.write(drawframe(start+i/FPS))
   if i%300==0:print(f'{start+i/FPS:.0f} seconds rendered',flush=True)
  p.stdin.close();p.wait();assert p.returncode==0
 print(dest,flush=True)
if __name__=='__main__':main()
