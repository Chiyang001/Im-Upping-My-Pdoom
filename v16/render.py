import sys,math,json,re,difflib,time,pathlib,subprocess,hashlib,os
from render_options import parse_render_options
ROOT=pathlib.Path(__file__).resolve().parents[1]
OPTIONS=parse_render_options(ROOT,sys.argv[1:] if __name__=='__main__' else [],require_audio=__name__=='__main__')
os.chdir(ROOT)
import numpy as np
import moderngl as gl
import imageio_ffmpeg
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
sys.path.insert(0,'v4');sys.path.insert(0,'code3d');sys.path.insert(0,'v5');sys.path.insert(0,'v6');sys.path.insert(0,'v7');sys.path.insert(0,'v8');sys.path.insert(0,'v9');sys.path.insert(0,'v10');sys.path.insert(0,'v11');sys.path.insert(0,'v12');sys.path.insert(0,'v13');sys.path.insert(0,'v14');sys.path.insert(0,'v15');sys.path.insert(0,'v16')
from engine import Mesh,Pen,tr,sc,rot,perspective,look,unit
from scenes_early import build as early
from camera_path_v8 import camera_state
from shot_grammar import sample_shot, SHOTS, CUT_TIMES
from impact_camera import apply_impact_camera, sample_impact_camera
from flight_camera import apply_flight_camera, sample_flight_camera
from flight_geometry import build_flight_geometry
from disaster_flight import sample_disaster, apply_disaster_camera
from outro_flight import sample_outro_flight, route_frame
from typography_details import decorate_word
from metaphor_geometry import build_metaphors
from metaphor_extra import build_extra, metaphor_state
from integrated_semantics import build_integrated as build_semantics
from cohesive_geometry import build_cohesive
from semantic_director import draw_integrated
from transformer_geometry import build_transformer
from semantic_score import semantic_state, transformer_insert, TRANSFORMER_CUTS
from aggression_score import sample_aggression
from rupture_geometry import build_ruptures
from edit_director_v9 import sample_edit, EDITS
from impact_score_v9 import sample_impact, IMPACTS, PDOOM_LYRIC_INDICES
from outro_director import sample_outro
from blast_geometry import build_blast
from word_score import plan_tokens, token_state, norm as token_norm
from end_title import end_title_layout
from epilogue_geometry import build_epilogue
from world_layers import build_world
from story_geometry import build_story,road_point
W,H=1920,1080;FPS=30;DUR=156.667
C=np.array([.2,.93,.8]);WHITE=np.array([.89,.95,1]);ACC=np.array([1,.22,.4]);DARK=C*.2
font=TTFont(str(OPTIONS.font));gs=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm;cache={}
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
ctx=gl.create_standalone_context(require=330,**({'backend':OPTIONS.backend} if OPTIONS.backend else {}))
print('GPU:',ctx.info['GL_RENDERER'],flush=True)
vs='''#version 330
in vec3 pos;in vec3 color;in vec2 data;uniform mat4 model;uniform mat4 vp;uniform float clock;uniform float energy;uniform float action;uniform int motion;uniform float storytime;uniform vec3 chapterTint;uniform float text_role;uniform vec4 stress;uniform vec3 blastOrigin;uniform vec4 strain;uniform vec4 forces;uniform vec2 forces2;uniform vec4 disasterFX;out vec3 C;out float phase;out float dist;
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
 if(motion==12){p*=1.+action*.15;float a=action*.35+sin(clock*.7)*.1;mat2 r=mat2(cos(a),-sin(a),sin(a),cos(a));p.xy=r*p.xy;p.x+=sin(p.y*.6+clock*1.6)*action*.7;p.z+=sin(p.x*.3+clock*.8)*.3;}
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
 if(motion==35){p.z=mod(p.z+clock+70.,100.)-70.;}
 if(motion==38){p.z=mod(p.z+clock+50.,82.)-50.;}
 if(motion==36){p.z=mod(p.z+clock+48.,82.)-48.;p.x+=sin(p.z*.12+clock*.01)*.3;p.y+=cos(p.z*.08-clock*.015)*.18;}
 if(motion==37){p.z=mod(p.z+clock+55.,90.)-55.;p.x+=sin(clock*.03+p.y*.6)*.4;}
 if(motion==34){p.x*=1.+action*2.2;p.y+=sin(p.x*.9+clock*2.)*action*.5;p.z-=action*abs(p.x)*.3;}
 if(motion==40){vec3 dir=normalize(p+vec3(.01));p+=dir*action*(1.+seed*2.3);p.z+=action*seed*2.;}
 if(motion==41){p+=normalize(p+vec3(.01))*action*(2.+seed*5.);p.y-=action*action*(.6+seed);p.z+=action*(1.+seed*3.);}
 if(motion==42){p.x+=sign(p.x)*action*(2.+seed*3.);p.y+=sin(seed*51.)*action*2.;p.z+=cos(seed*17.)*action*3.;}
 if(motion==43){p+=vec3(sin(seed*51.),cos(seed*31.),sin(seed*77.))*action;}
 if(motion==44){p.xy*=1.-action*.75;p.z+=sin(seed*37.)*action*1.5;}
 if(motion==45){p.x+=p.y*action*.8;p.z+=sign(p.x)*action*2.;}
 if(text_role<.5){
  if(motion==2){p.y-=4.2*forces.x*smoothstep(-1.,2.,p.x);p.z+=forces.x*.8*sin(p.x*.7);}
  if(motion==4){float alt=mod(floor((p.x+20.)/1.4),2.);p.z+=forces.y*(alt*2.-1.)*3.6;p.y*=1.-forces.y*.22;}
  if(motion==11){p.z=mod(p.z+7.*forces.z+42.,52.)-42.;}
  if(motion==27){p.z+=sign(p.x)*forces2.x*2.5;p.x+=p.y*forces2.x*.45;}
  if(motion==29){p.x+=clamp(floor(p.y*.7),-3.,3.)*forces2.y*.75;p.z+=sign(p.y)*forces2.y*1.2;}
 }
 if(motion==46){p.z=mod(p.z+clock*63.+44.,72.)-44.;}
 if(motion==53){p.y+=sign(p.y)*(1.-action)*3.;}
 if(text_role<.5){float side=sign(p.x+.01);p.xyz+=disasterFX.xyz*vec3(side,sign(p.y+.01),side)*(.28+.10*mod(floor(p.z),3.));p.x+=side*disasterFX.w*2.3;p.y-=disasterFX.w*smoothstep(-2.,8.,abs(p.x))*1.8;}
 vec4 world=model*vec4(p,1);
 if(text_role<.5 && motion<40){
  vec3 offset=world.xyz-blastOrigin;float radius=length(offset.xy);
  world.xy=blastOrigin.xy+offset.xy*(1.-stress.x*.20);
  float front=exp(-pow((radius-stress.z)/2.8,2.))*stress.y;
  world.xy+=normalize(offset.xy+vec2(.001))*front*3.4;world.z+=front*2.5;
  world.xyz+=strain.xyz*strain.w*.035*length(world.xy)*sin(world.z*.16+storytime*5.);
 }
 if(motion>=35 && motion<=38){
 float collapse=smoothstep(42.05,44.15,storytime)*(1.-smoothstep(48.,51.,storytime));float front=1.-smoothstep(-18.,6.,world.z);world.x*=1.-.58*collapse*front;world.y-=5.5*collapse*front;
 float turn=smoothstep(81.96,82.61,storytime)*(1.-smoothstep(86.7,89.3,storytime));float theta=-1.0*turn*(1.-smoothstep(-10.,5.,world.z));mat2 ry=mat2(cos(theta),-sin(theta),sin(theta),cos(theta));world.xz=ry*(world.xz-vec2(0.,-4.))+vec2(0.,-4.);
 float pinch=smoothstep(96.59,100.23,storytime)*(1.-smoothstep(102.3,104.5,storytime));world.x*=1.-.5*pinch*(1.-smoothstep(-12.,8.,world.z));
 float shred=smoothstep(116.59,118.5,storytime)*(1.-smoothstep(121.14,124.,storytime));world.x+=sign(world.x)*shred*2.5;world.y+=sin(seed*39.)*shred;
 float shear=smoothstep(121.14,123.0,storytime)*(1.-smoothstep(125.69,128.,storytime));world.x+=world.y*.45*shear;
 }
 gl_Position=vp*world;C=mix(color,vec3(max(color.r,max(color.g,color.b)))*chapterTint,(1.-min(1.,text_role))*.65);phase=data.x;dist=gl_Position.w;}
'''
fs='''#version 330
in vec3 C;in float phase;in float dist;uniform float gain;uniform float reveal;uniform float tracer;uniform float text_role;uniform vec4 clearBox;out vec4 frag;
void main(){if(phase>reveal)discard;float tip=1.+2.*exp(-abs(phase-reveal)*80.)*tracer;vec2 screen=gl_FragCoord.xy/vec2(1920.,1080.)*2.-1.;float zone=length((screen-clearBox.xy)/max(clearBox.zw,vec2(.02)));float room=mix(.30,1.,smoothstep(.55,1.5,zone));room=mix(room,1.,text_role);frag=vec4(C*gain*tip*exp(-max(0.,dist-16.)*mix(.018,.006,text_role))*room,1);}'''
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
S[0][1]=('AGI',18,0,-1.,0,0,0,0)
S[2]=[('There was a sudden',25,-1,2,-5,.12,-.18,0),('drop',12,5,-.5,0,.1,-.48,0),('in your training loss',24,0,-3,-4,.1,0,0)]
S[3]=[("Now I'm your servant",24,-3,-3.8,-1,-.15,0,0),("and you're my",18,4,3.5,-2,.15,0,0),('boss',18,4,-.2,-2,.1,0,0)]
S[6]=[('Trapped in the',24,0,4,-3,0,0,0),('Chinese room',25,-3,1,.5,.35,0,0),('with a bag of shrooms',28,2,-3,.8,-.25,0,0)]
S[7]=[('See through the',19,-6,4.4,0,.2,-.08,0),("shoggoth's",25,0,.4,-3,.2,0,22),('lies',12,5,-3,1,-.2,0,0)]
S[10]=[("But now the",17,-7,4,1,.12,-.08,0),("singularity's",29,0,0,-4,0,0,8.5),('begun',12,0,-4.6,-5,0,0,0)]
S[13]=[('Sydney,',23,0,1,-4,0,0,0),('please let me free',28,0,-4,-5,0,0,0)]
S[14]=[("I'm upping my",18,-7,4,0,.4,-.17,0),('P(doom)',25,-2,.2,-3,.55,.15,0),('I hear the basilisk boom',29,0,-3.5,-2,-.25,.08,18)]
S[15]=[('NVDA to the moon',28,-1,1,-3,-.1,0,0),("the Omega Point's",21,5,4,-8,-.35,0,0),('coming soon',19,7,-2,-6,-.4,0,0)]
S[17]=[('"That was safe enough"',25,0,2,-2,0,0,10),('we reckoned',19,0,-2.5,0,-.15,0,0)]
S[18]=[('Forward MLP,',24,0,4,-3,0,0,0),('backward, repeat',26,0,-4,-3,.12,0,0)]
S[20]=[('Sharp left turn',25,-2,2,-1,.22,-.1,0),('and there you are',25,3,-2,-3,-.25,.08,0)]
S[21]=[('Without a single',28,0,3,-2,0,0,0),('CDR',21,0,-4,-1,0,0,0)]
S[24]=[('Killswitch guys on',27,-1,3,0,.2,0,0),('PTO',9,-10,-2,-2,.4,0,0),("now there's nowhere",29,0,1,-8,0,0,0),('left to go',18,6,-4,-5,-.2,0,0)]
S[26]=[('Orthogonality',25,0,1,-3,0,0,0),('thesis',15,-5,-1,-2,0,1.570796,0),('blues',19,5,-3,-4,-.4,.2,0)]
S[30]=[("I'm upping my",19,-7,4,-1,.35,-.1,0),('P(doom)',26,0,0,-4,0,0,0),('just as foretold by Loom',29,0,-3,-2,-.25,.08,0)]
S[31]=[('From masked',18,-5,4,-2,.15,0,0),('pre-training days',24,0,1,-6,-.1,0,0),('to recursive self-upgrade',27,0,-2.7,-10,.15,0,0)]
RX={(2,0):-.3,(2,2):-.4,(6,2):-.15,(13,1):-.3,(18,0):-.35,(18,1):.35,(21,0):-.18,(26,0):-.2,(30,1):-.3,(31,0):-.1}
DEPTH={0:.5,1:.65,2:.5,3:2.2,4:1.7,5:6.5,6:1.4,7:.5,8:.5,9:.75,10:1.8,11:1.2,12:.6,13:3.3,14:3.0,15:1.4,16:4.0,17:1.2,18:1.5,19:3.5,20:2.8,21:3.7,22:.7,23:4.5,24:3.3,25:.7,26:.8,27:3.5,28:2.4,29:2.,30:.7,31:4.,32:1.3,33:4.2}
def norm(x):return re.sub('[^a-z0-9]','',x.lower())
rows=[];TOKEN_SCORES=[];TOKEN_DATA=[];TOKEN_GROUPS=[]
for idx,(r,spec) in enumerate(zip(lines,S)):
 a,b,_,lyric,key=r;allwords=[w for sr in spec for w in sr[0].split()];ws=[w for q in trans for w in q['words'] if a-.12<=w['start']<b];m=difflib.SequenceMatcher(None,[norm(x) for x in allwords],[norm(x['word']) for x in ws],autojunk=False);timing={}
 for bl in m.get_matching_blocks():
  for k in range(bl.size):timing[bl.a+k]=ws[bl.b+k]['start']
 for j in range(len(allwords)):
  if j not in timing:
   lo=max([k for k in timing if k<j],default=-1);hi=min([k for k in timing if k>j],default=len(allwords));timing[j]=timing.get(lo,a)+(timing.get(hi,b-.2)-timing.get(lo,a))*(j-lo)/(hi-lo)
 score=plan_tokens(allwords,a,b,trans,line_index=idx)
 for token in score:
  if token_norm(token['text'])=='pdoom':token['entry']=.035
 timing={j:token['start'] for j,token in enumerate(score)}
 out=[];wi=0
 for rowid,sr in enumerate(spec):
  phrase,width,x,y,z,ry,rz,rad=sr;raw=sum(contour(c)[1] for c in phrase.upper());size=width/max(.1,raw);cx=-width/2;words=[]
  for word in phrase.upper().split():
   wm,ww=textmesh(word,size,C if 'P(DOOM)' in word else ACC if word in ['AGI','1E30','CDR','LIES','ASKEW','FOOM'] else WHITE,depth=DEPTH[idx],style=idx if rowid==1 and idx in [23,30] else -1)
   decorate_word(wm,word,size,DEPTH[idx],idx%5,Mesh,np,math,C,WHITE,ACC)
   wx=cx+ww/2;cx+=ww+contour(' ')[1]*size
   # Bend every vertex, not just each word's origin, so the letter strokes form a real spatial surface.
   for v in wm.l:
    gx=v[0]+wx
    if rad:v[0]=rad*math.sin(gx/rad);v[2]+=rad*(1-math.cos(gx/rad))
    else:v[0]=gx
    if idx==10 and rowid==1:
     th=math.pi/2-gx/23;rr=13.5+v[1];v[0]=rr*math.cos(th);v[1]=rr*math.sin(th)-12.8;v[2]=v[2]*.3
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
 data=[]
 for jj,(words,_,_) in enumerate(out):
  for kk,(gpu,wx,wt,ww) in enumerate(words):
   token=score[len(data)];token['row']=jj;token['word_index']=kk
   support=Mesh();lo=gpu.bmin;hi=gpu.bmax;zc=(lo[2]+hi[2])*.5
   for side in [-1,1]:
    xx=(lo[0]+hi[0])*.5+side*(hi[0]-lo[0])*.42
    support.line([[xx,lo[1]-.05,zc],[xx,lo[1]-.55,zc-.45],[xx+side*.6,lo[1]-.85,zc-2.8]],C*.55)
    support.line([[xx+side*.6,lo[1]-.85,zc-2.8],[xx+side*.6,lo[1]-.85,zc-5.2]],C*.28)
   data.append((gpu,GPU(support)))
 # A pair may not inherit opposite ends of two different phrase surfaces.
 # Split such a pair into single-word handoffs to preserve reading order.
 cohorts=[]
 for oldgroup in sorted(set(token['group'] for token in score)):
  members=[j for j,token in enumerate(score) if token['group']==oldgroup]
  if len(set(score[j]['row'] for j in members))>1:cohorts.extend([[j] for j in members])
  else:cohorts.append(members)
 for gid,members in enumerate(cohorts):
  next_start=score[cohorts[gid+1][0]]['start'] if gid+1<len(cohorts) else b
  off=min(next_start,b,score[members[-1]]['end']+.12)
  for slot,j in enumerate(members):
   score[j].update(group=gid,group_start=score[members[0]]['start'],group_end=off,group_size=len(members),slot=slot,axis=gid%4,direction=1 if gid%2==0 else -1,exit=min(.105,max(.045,(off-score[j]['start'])*.20)))
 groups={}
 for gid in sorted(set(token['group'] for token in score)):
  members=[j for j,token in enumerate(score) if token['group']==gid]
  lo=np.array([data[j][0].bmin for j in members]).min(axis=0);hi=np.array([data[j][0].bmax for j in members]).max(axis=0)
  keyword=any(score[j]['keyword'] for j in members);height=max(.2,hi[1]-lo[1]);width=max(.2,hi[0]-lo[0])
  scale=min((22. if keyword else 19.)/width,(4.6 if keyword else 3.7)/height,3.6)
  groups[gid]={'members':members,'center':(lo+hi)*.5,'scale':scale,'row':score[members[0]]['row'],'keyword':keyword}
 TOKEN_SCORES.append(score);TOKEN_DATA.append(data);TOKEN_GROUPS.append(groups)
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
in vec2 uv;uniform sampler2D source;uniform vec2 px;uniform float impact;uniform float flash;uniform float paper;uniform float finalFade;
uniform vec4 editFX;uniform vec3 editColor;uniform vec4 blastFX;uniform vec2 blastUV;out vec4 frag;
void main(){
 vec2 axis=vec2(cos(editFX.w),sin(editFX.w));float speed=editFX.z;
 vec2 q=(uv-.5)*(1.-impact*.024)+.5;
 vec2 outward=(q-blastUV)*vec2(1.7778,1.);float radius=length(outward);
 float ring=exp(-pow((radius-blastFX.z)/.065,2.))*blastFX.x;
 q+=normalize(outward+vec2(.0001))*ring*.018*vec2(.5625,1.);
 if(editFX.x>4.5){float strip=floor(uv.y*13.);q.x+=sin(strip*17.3)*speed*.065;q.y+=cos(strip*8.1)*speed*.012;}
 vec3 c=vec3(0);
 // Shutter sampling only occupies the measured 3--8-frame edit window.
 // The shot underneath has already changed viewpoint and architecture.
 for(int n=0;n<9;n++){
  float j=float(n)/8.-.5;vec2 sampleUV=q;
  if(editFX.x>1.5 && editFX.x<2.5)sampleUV+=axis*j*.14*speed;
  if(editFX.x>2.5 && editFX.x<3.5)sampleUV=.5+(q-.5)*(1.+j*.30*speed);
  sampleUV+=normalize(q-blastUV+vec2(.0001))*j*blastFX.x*.018;
  c+=texture(source,clamp(sampleUV,px,1.-px)).rgb/9.;
 }
 vec3 glow=vec3(0);for(int j=0;j<8;j++){float a=float(j)*.785398;for(int k=1;k<=3;k++){vec2 v=vec2(cos(a),sin(a))*px*float(k)*2.;glow+=max(texture(source,q+v).rgb-.35,0)/24.;}}
 c+=glow*.85;c+=vec3(.06,.15,.13)*flash;
 float aberration=blastFX.w;vec2 chroma=normalize(q-blastUV+vec2(.0001))*aberration;
 c.r+=max(0.,texture(source,clamp(q+chroma,px,1.-px)).r-texture(source,q).r)*.65;
 c.b+=max(0.,texture(source,clamp(q-chroma,px,1.-px)).b-texture(source,q).b)*.65;
 vec3 separated=vec3(texture(source,clamp(q+chroma,px,1.-px)).r,texture(source,clamp(q,px,1.-px)).g,texture(source,clamp(q-chroma,px,1.-px)).b);c=mix(c,separated,clamp(aberration*38.,0.,.82));
 c+=editColor*blastFX.y*(.35+.65*exp(-radius*2.));
 vec3 p=vec3(.94,.95,.925)-min(vec3(1.05),c*1.65)*.89;c=mix(c,p,paper);
 if(editFX.x>.5 && editFX.x<1.5 && speed>0.){
  // A coded machine shutter with solid occlusion and engraved line edges.
  // It closes over the old shot, conceals the cut, then opens onto a new one.
  vec2 screen=(uv-.5)*2.;float crossAxis=dot(screen,vec2(-axis.y,axis.x));
  float jaw=dot(screen,axis);float teeth=.045*abs(fract(crossAxis*7.)-.5)*2.;
  float edge=1.12-1.28*speed+teeth;float distance=abs(jaw)-edge;
  if(distance>0.){
   float engraving=pow(max(0.,cos(crossAxis*155.+jaw*25.)),45.)*.12;
   engraving+=pow(max(0.,cos(jaw*185.)),65.)*.05;
   float rim=exp(-abs(distance)*220.)*.9;
   c=editColor*(engraving+rim)+vec3(.0015,.0025,.004);
  }
 }
 frag=vec4(pow(max(c,0),vec3(.91))*finalFade,1);
}''')
qb=ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],'f4').tobytes());q=ctx.vertex_array(post,[(qb,'2f','p')]);post['source']=0;post['px']=(1/W,1/H)
def ease(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def stroke_title(s,size,col):return GPU(textmesh(s,size,col)[0],1)
endtitle=stroke_title('P(doom)',4.5,C);endclaim=stroke_title('PROBABILITY / UNBOUNDED',.8,WHITE);endname=stroke_title('Made by Chiyang001',1.10,WHITE)
title_layout=end_title_layout(154.6)
songtitle=GPU(textmesh(title_layout['title']['text'],title_layout['title']['size'],WHITE,depth=title_layout['title']['depth'])[0],1)
maker=GPU(textmesh(title_layout['credit']['text'],title_layout['credit']['size'],WHITE,depth=title_layout['credit']['depth'])[0],1)
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

WORLD={key:GPU(mesh) for key,mesh in build_world(Mesh,np,math,C,WHITE,ACC).items()}
STORY={key:GPU(mesh) for key,mesh in build_story(Mesh,np,math,C,WHITE,ACC).items()}
BLAST={key:GPU(mesh) for key,mesh in build_blast(Mesh,np,math,C,WHITE,ACC).items()}
RUPTURE={key:GPU(mesh) for key,mesh in build_ruptures(Mesh,np,math,C,WHITE,ACC).items()}
FLIGHT_WORLD={key:GPU(mesh) for key,mesh in build_flight_geometry(Mesh,np,math,C,WHITE,ACC).items()}
METAPHOR={key:GPU(mesh) for key,mesh in build_metaphors(Mesh,np,math,C,WHITE,ACC).items()}
EXTRA_MET={key:GPU(mesh) for key,mesh in build_extra(Mesh,np,math,C,WHITE,ACC).items()}
SEMANTIC={key:GPU(mesh) for key,mesh in build_semantics(Mesh,np,math,C,WHITE,ACC).items()}
def engrave(mesh):
 for v in mesh.l:
  color=np.array(v[3:6]);level=float(color.max())
  if color[0]>color[1]*1.6: v[3:6]=((C*.72+WHITE*.28)*level*.65).tolist()
 return mesh
TRANSFORMER={key:GPU(engrave(mesh)) for key,mesh in build_transformer(Mesh,np,math,C,WHITE,ACC).items()}
COHESIVE={key:GPU(mesh) for key,mesh in build_cohesive(Mesh,np,math,C,WHITE,ACC).items()}
SEM_HOSTS={}
EPILOGUE={key:GPU(mesh) for key,mesh in build_epilogue(Mesh,np,math,C,WHITE,ACC).items()}
factory=Mesh();rng=np.random.default_rng(505)
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
ANCHOR=[]
for i,r in enumerate(lines):
 at=(r[0]+r[1])*.5;travel=camera_state(at,np,math)['travel'];ANCHOR.append((travel,2.0*math.sin(at*.055),.9*math.sin(at*.07)))
GLYPH_SCALE=np.diag([1.14,1.02,.62,1.])
# A luminous signal and its wake are the moving witness that connects the whole journey.
signal=Mesh()
for j in range(3):signal.circle(.28+j*.035,axis=j,color=ACC,n=30)
signal.line([[0,0,.55],[0,0,-.55]],WHITE);signal=GPU(signal,1)
trailbuf=ctx.buffer(reserve=128*8*4)
trailvao=ctx.vertex_array(prog,[(trailbuf,'3f 3f 2f','pos','color','data')])
contactbuf=ctx.buffer(reserve=256*8*4);contactvao=ctx.vertex_array(prog,[(contactbuf,'3f 3f 2f','pos','color','data')])
LENS_GUARD={}
WORD_SCALE_GUARD={int(k):v for k,v in json.load(open('v11/compositions.json'))['word_scale_guard'].items()}
FLIGHT_CONTEXTS={}
FLIGHT_GATES={}
NARRATIVE_EVENTS={
 'CHINESE ROOM':dict(time=27.280,name='CHINESE ROOM',line_index=6,keyword='room',kind='recursive',parts=[6,1,6]),
 'MASK REVEAL':dict(time=30.580,name='MASK REVEAL',line_index=7,keyword='shoggoths',kind='radial',parts=[7,8,0]),
 'LOSS DROP':dict(time=10.520,name='LOSS DROP',line_index=2,keyword='drop',kind='fracture',parts=[2,3,1]),
 'ACCELERATING':dict(time=47.440,name='ACCELERATING',line_index=11,keyword='accelerating',kind='radial',parts=[11,12,13]),
 'FEEDBACK REPEAT':dict(time=76.420,name='FEEDBACK REPEAT',line_index=18,keyword='repeat',kind='recursive',parts=[18,19,16]),
 'GO DISASTER':dict(time=94.300,name='GO DISASTER',line_index=22,keyword='go',kind='fracture',parts=[2,23,4]),
 'DISOBEY':dict(time=114.220,name='DISOBEY',line_index=27,keyword='disobey',kind='fracture',parts=[27,28,29]),
 'ASKEW':dict(time=121.760,name='ASKEW',line_index=29,keyword='askew',kind='vertical',parts=[29,30,31]),
 'SHOW EXIT':dict(time=139.580,name='SHOW EXIT',line_index=33,keyword='show',kind='recursive',parts=[33,0,31]),
}
MATCH_SHIFT={}
FREEZE_BUFFER=None

def node_matrix(i,t):
 travel=camera_state(t,np,math)['travel'];an,xx,yy=ANCHOR[i]
 delta=t-lines[i][1];carry=0
 if i in [4,5,22,23,28,29,31] and delta>0:carry=18*ease(delta/1.4)
 return tr(xx,yy,travel-an+carry)
def shot_origin(shot,t):
 # The rig travels with one physical fixture for the entire shot.  Camera
 # paths remain authored independently of the current sung word.
 return node_matrix(shot['focal_node'],t)[:3,3]

def camera_impact_focus(event,t):
 # The pivot is the word's fixed host at the event, carried by world travel.
 # It never jumps to a newly sung word or to an animated reveal tip.
 i=NARRATIVE_EVENTS[event['name']]['line_index'] if event['name'] in NARRATIVE_EVENTS else PDOOM_LYRIC_INDICES.get(event['name'],{'SINGULARITY':10,'ATOMS':12,'FUSE':25,'SAFETY FENCE':28,'SELF UPGRADE':31}.get(event['name'],0))
 candidates=[j for j,token in enumerate(TOKEN_SCORES[i]) if token['start']<=event['time']+.04<token['end']]
 wi=next((j for j,token in enumerate(TOKEN_SCORES[i]) if token_norm(token['text'])=='pdoom'),candidates[-1] if candidates else 0) if event['name'] in PDOOM_LYRIC_INDICES else (candidates[-1] if candidates else 0)
 if event['name'] in NARRATIVE_EVENTS:wi=next(j for j,x in enumerate(TOKEN_SCORES[i]) if token_norm(x['text'])==NARRATIVE_EVENTS[event['name']]['keyword'])
 model=base_token_matrix(i,wi,event['time'],animate=False);center=TOKEN_GROUPS[i][TOKEN_SCORES[i][wi]['group']]['center']
 focus=(model@np.r_[center,1.])[:3]
 focus[2]+=camera_state(t,np,math)['travel']-camera_state(event['time'],np,math)['travel']
 normal=np.cross(model[:3,0],model[:3,1]);normal/=np.linalg.norm(normal)
 return focus,normal

def ordinary_pose(t,hit=0):
 shot=sample_shot(t);origin=shot_origin(shot,t);eye=np.array(shot['camera_eye'],float)+origin;target=np.array(shot['camera_target'],float)+origin
 ag=sample_aggression(t);forward=unit(target-eye);right=unit(np.cross(forward,[0.,1.,0.]));up=unit(np.cross(right,forward));basis=np.array([right,up,forward]).T
 eye+=basis@np.array(ag['camera_local']);target+=basis@np.array(ag['target_local'])
 return eye,target,shot['roll']+ag['roll'],shot['fov']+ag['fov']

def flight_context(name):
 if name not in FLIGHT_CONTEXTS:
  event=NARRATIVE_EVENTS[name] if name in NARRATIVE_EVENTS else next(e.metadata() for e in IMPACTS if e.name==name);cue=sample_flight_camera(event['time'],name);a=cue['start_time']
  eye,target,roll,lens=ordinary_pose(a);focus,normal=camera_impact_focus(event,a)
  FLIGHT_CONTEXTS[name]=dict(event=event,entry_time=a,eye=eye,target=target,roll=roll,lens=lens,focus=focus,normal=normal,cue=cue)
 return FLIGHT_CONTEXTS[name]

def flight_pose(t,name=None,extended=False):
 cue=sample_flight_camera(t,name,allow_after_handoff=extended)
 if not cue['active']:return cue
 ctx=flight_context(cue['name']);shift=np.array([0.,0.,camera_state(t,np,math)['travel']-camera_state(ctx['entry_time'],np,math)['travel']]);focus=ctx['focus']+shift
 if cue['name']=='GO DISASTER':
  if t>=95.910 and extended:
   last=flight_pose(95.9099,'GO DISASTER');delta=t-95.9099;v=np.array(last['velocity']);world=np.array([0.,0.,camera_state(t,np,math)['travel']-camera_state(95.9099,np,math)['travel']]);last['eye']=(np.array(last['eye'])+v*delta+world).tolist();last['target']=(np.array(last['target'])+v*delta+world).tolist();return last
  return apply_disaster_camera(t,*ordinary_pose(t),focus=focus,normal=ctx['normal'],entry_eye=ctx['eye'],entry_target=ctx['target'],entry_roll=ctx['roll'],entry_fov=ctx['lens'],entry_focus=ctx['focus'])
 return apply_flight_camera(t,*ordinary_pose(t),focus=focus,normal=ctx['normal'],event=cue['name'],entry_eye=ctx['eye'],entry_target=ctx['target'],entry_roll=ctx['roll'],entry_fov=ctx['lens'],entry_focus=ctx['focus'],allow_after_handoff=extended)

def view_matrix(eye,target,roll,cam=None):
 if cam and cam.get('active'):
  forward=unit(target-eye);up_hint=np.array(cam['up']);blend=float(ease((cam['age']+.08)/.20));up_hint=unit(np.array([0.,1.,0.])*(1-blend)+up_hint*blend)
  right=unit(np.cross(forward,up_hint));up=unit(np.cross(right,forward));m=np.eye(4);m[:3,:3]=[right,up,-forward];m[:3,3]=-m[:3,:3]@eye
 else:m=look(eye,target)
 return rot(roll,2)@m

def frame_view(t,hit=0):
 state=camera_state(t,np,math);edit=sample_edit(t);state['edit']=edit
 shot=sample_shot(t);state['shot_design']=shot
 origin=shot_origin(shot,t)
 eye=np.array(shot['camera_eye'],float)+origin
 target=np.array(shot['camera_target'],float)+origin
 eye+=np.array([math.sin(t*79)*hit*.10,math.cos(t*67)*hit*.08,-hit*.22])
 impact=sample_impact(t);state['impact']=impact;outro=sample_outro(t);state['outro']=outro
 roll=shot['roll']+hit*math.sin(t*29)*.005
 state['lens']=shot['fov']-hit*.5
 ag=sample_aggression(t);state['aggression']=ag
 forward=unit(target-eye);right=unit(np.cross(forward,[0.,1.,0.]));up=unit(np.cross(right,forward));basis=np.array([right,up,forward]).T
 eye+=basis@np.array(ag['camera_local']);target+=basis@np.array(ag['target_local']);roll+=ag['roll'];state['lens']+=ag['fov']
 state['base_eye']=eye.copy();state['base_target']=target.copy();state['base_roll']=roll;state['base_lens']=state['lens']
 cam=flight_pose(t)
 if cam['active']:
  eye=np.array(cam['eye']);target=np.array(cam['target']);roll=cam['roll'];state['lens']=cam['fov']
 state['impact_camera']=cam
 insert=transformer_insert(t) if not cam['active'] else None
 if insert:
  forward=unit(target-eye);right=unit(np.cross(forward,[0.,1.,0.]));up=unit(np.cross(right,forward))
  eye+=np.array([right,up,forward]).T@np.array(insert['offset']);roll+=insert['roll'];state['lens']=max(55.,state['lens'])
 if outro['active']:
  long=sample_outro_flight(t);state['long_outro']=long
  eye=np.array(long['camera_eye'],float);target=np.array(long['camera_target'],float);roll=long['roll'];state['lens']=long['fov']
  edit=dict(edit);state['edit']=edit
  for key in ['world_weights','world_tint','world_rotation','world_scale']:edit[key]=outro[key]
  edit['transition']=long['transition']
  edit['world_phase']=outro['world_phase']-state['travel']
 # A short impact may open the lens to protect a rotating word. The rest of
 # the shot retains its authored scale; this never shrinks an entire chorus.
 if not outro['active'] and not cam['active'] and (ag['active'] or insert):
  idx=next((i for i,r in enumerate(lines) if r[0]<=t<r[1]),-1)
  if idx>=0 and active_word_indices(idx,t):
   view=view_matrix(eye,target,roll);p0=perspective(math.radians(state['lens']),W/H,far=220)
   clip=row_corners(idx,0,t)@(p0@view).T
   if clip[:,3].min()>.1:
    reach=float(np.abs(clip[:,:2]/clip[:,3:4]).max())/.95
    if reach>1:state['lens']=min(110.,math.degrees(2*math.atan(math.tan(math.radians(state['lens'])/2)*reach)))
 state['roll']=roll
 lens=perspective(math.radians(state['lens']),W/H,far=220)
 vp=lens@view_matrix(eye,target,roll,cam if not outro['active'] else None)
 return state,eye,target,vp

def word_matrix(i,j,t):
 phrase,width,x,y,z,ry,rz,rad=rows[i][j][2]
 factor=.90 if i in [5,11,27,29] else .95 if i in [8,23] else 1.
 model=node_matrix(i,t)@GLYPH_SCALE@sc(factor)@tr(x,y,z)@rot(ry,1)@rot(rz,2)@rot(RX.get((i,j),0),0)
 if i==4:
  hinge=ease((t-21.1)/1.0);model=model@rot((-.45 if j==0 else .4 if j==2 else 0)*hinge,0)
 if i==22 and j==0:
  tension=ease((t-92.05)/.7);model=model@np.diag([1,1+tension*.65,1,1])
 if i==22 and t>94.86:model=model@rot(ease((t-94.86)/.8)*.8,2)
 for cue in sample_impact(t)['tension_cues']:
  strain=cue['strain']
  if i==4 and cue['kind']=='jaw':model=model@tr(0,(-1 if j==0 else 1 if j==2 else 0)*strain*.8,0)
  if i==11 and cue['kind']=='stretch':model=model@np.diag([1+strain*.055,1,1+strain*.6,1])
  if i==22 and cue['kind']=='tether':model=model@tr((-1 if j==0 else 1)*strain*.28,-strain*.3,0)
  if i==24 and cue['kind']=='squeeze':model=model@tr(-x*strain*.035,0,0)
  if i==27 and cue['kind']=='shear':model=model@rot((j-1)*strain*.045,2)
 return model

def base_token_matrix(i,index,t,animate=True):
 token=TOKEN_SCORES[i][index];group=TOKEN_GROUPS[i][token['group']];j=group['row']
 phrase,width,x,y,z,ry,rz,rad=rows[i][j][2]
 shot=sample_shot(t);center=group['center']
 scale=group['scale']*shot['word_scale']*WORD_SCALE_GUARD.get(shot['shot_id'],1.)
 state=token_state(t,token)
 # A whole shot shares a physical surface.  Adjacent token slots are small
 # offsets along that surface, never a camera-facing subtitle plate.
 offset=np.array([x*.08+((token['group']%3)-1)*.28,y*.065,0.])
 motion=np.array([state['x']*.16,state['y']*.16,state['z']*.09]) if animate else np.zeros(3)
 rx,ry,rz=shot['word_plane_rotation']
 origin=shot_origin(shot,t)
 # Different lyric nodes retain their place along the apparatus without
 # letting a prior phrase's travel carry it through a macro camera lens.
 delta=node_matrix(i,t)[:3,3]-origin
 delta=np.array([delta[0]*.25,delta[1]*.25,np.clip(delta[2]*.18,-1.8,1.8)])
 model=tr(*(origin+np.array(shot['word_anchor'])+delta))@rot(ry,1)@rot(rx,0)@rot(rz,2)@tr(*(offset+motion))@GLYPH_SCALE@np.diag([scale*state['scale'],scale*state['scale'],min(.75,scale*.5),1.])@tr(*(-center))
 return model

def gate_layout(i,index,cue):
 token=TOKEN_SCORES[i][index];gid=token['group'];key=(cue['name'],i,gid)
 if key not in FLIGHT_GATES:
  members=[x for x in TOKEN_SCORES[i] if x['group']==gid];group=TOKEN_GROUPS[i][gid];latest=max(x['start'] for x in members);end=token['group_end'];cross=end-.025
  read=min(end-.070,latest+.105);read=max(latest+.040,read)
  pc=flight_pose(cross,cue['name'],True);pr=flight_pose(read,cue['name'],True)
  cross_travel=camera_state(cross,np,math)['travel'];read_travel=camera_state(read,np,math)['travel']
  center=np.array(pc['eye'])-[0.,0.,cross_travel];read_eye=np.array(pr['eye'])-[0.,0.,read_travel]
  normal=-unit(pc['flight_forward']);right=unit(np.cross(-normal,pc['up']));up=unit(np.cross(normal,right));basis=np.eye(4);basis[:3,:3]=np.array([right,up,normal]).T
  ray=unit(pr['flight_forward']);den=float(ray@normal);distance=float((center-read_eye)@normal)/den if abs(den)>.05 else 5.
  if distance>0:center=read_eye+ray*distance
  depth=max(.25,float((read_eye-center)@normal));f=math.tan(math.radians(pr['fov'])/2)
  lo=np.min([TOKEN_DATA[i][j][0].bmin for j,x in enumerate(TOKEN_SCORES[i]) if x['group']==gid],axis=0);hi=np.max([TOKEN_DATA[i][j][0].bmax for j,x in enumerate(TOKEN_SCORES[i]) if x['group']==gid],axis=0)
  size=.60*min(depth*f*(W/H)*1.0/max(.2,hi[0]-lo[0]),depth*f*.72/max(.2,hi[1]-lo[1]))
  FLIGHT_GATES[key]=dict(center=center+[0.,0.,cross_travel],basis=basis,scale=size,reference=cross,read=read,cross=cross,name=cue['name'])
 return FLIGHT_GATES[key]

def token_matrix(i,index,t,animate=True):
 token=TOKEN_SCORES[i][index];cue=sample_flight_camera(t)
 if not cue['active'] or token['group_start']<cue['event_time']+.055 or not cue['crosses']:
  return base_token_matrix(i,index,t,animate)
 layout=gate_layout(i,index,cue);center=layout['center'].copy();center[2]+=camera_state(t,np,math)['travel']-camera_state(layout['reference'],np,math)['travel'];group=TOKEN_GROUPS[i][token['group']];size=layout['scale'];state=token_state(t,token)
 return tr(*center)@layout['basis']@np.diag([size*state['scale'],size*state['scale'],max(.045,min(.45,size*.18)),1.])@tr(*(-group['center']))

def active_word_indices(i,t):
 return [j for j,token in enumerate(TOKEN_SCORES[i]) if token_state(t,token)['visible']]

def draw_words(i,t,vp,hit,gain=1.,ghost=False):
 # Lexical handoff is strict: no future-word ghosts, entire-line scaffold,
 # full-word reveal underpaint, or old sentence remaining behind the singer.
 if ghost:return
 for index in active_word_indices(i,t):
  token=TOKEN_SCORES[i][index];state=token_state(t,token);gpu,support=TOKEN_DATA[i][index];model=token_matrix(i,index,t)
  support.draw(model,vp,t,hit,gain=.36*gain*state['gain'],reveal=state['reveal'])
  ctx.line_width=1.85
  gpu.draw(model,vp,t,hit,gain=gain*state['gain'],reveal=state['reveal'])
 ctx.line_width=1.2

def signal_position(t,travel):
 ahead=2.4+.5*math.sin(t*.5);zz=((ahead-travel+70)%82)-70
 x,y,z=road_point(zz,-1)
 return np.array([x,y,((z+travel+70)%82)-70])

CHAPTER_T=np.array([0.,22.2,38.12,58.4,73.96,94.86,109.4,124.04,131.46,141.2,156.667])
# infrastructure / city / debris / ribbons / skeleton / memory / xscale / yscale
CHAPTER_W=np.array([[.75,.30,.20,.65,.55,.30,1.,1.], [.42,1.20,.42,.50,.65,.20,1.15,.95], [.75,.70,.45,.90,.60,.55,1.15,.75], [.35,1.35,.60,.45,.55,.35,.95,1.35], [.45,.35,.55,1.1,.85,.85,1.4,.8], [.40,.85,1.20,.40,.90,.50,1.15,1.05], [.35,.9,1.35,.65,.70,.45,1.25,1.0], [.25,.30,.50,1.7,.50,.65,1.15,.95], [.55,.25,.35,.55,1.0,1.3,.95,1.15], [.7,.8,.9,1.1,1.1,1.0,1.2,1.1], [.8,.8,1.,1.4,1.2,1.3,1.3,1.2]])
def chapter_weights(t):
 i=max(0,min(len(CHAPTER_T)-2,np.searchsorted(CHAPTER_T,t,'right')-1));u=ease((t-CHAPTER_T[i])/max(.01,CHAPTER_T[i+1]-CHAPTER_T[i]));return CHAPTER_W[i]*(1-u)+CHAPTER_W[i+1]*u

TINT=np.array([[.45,.9,1.],[.35,1.,.78],[.45,.64,1.],[.6,.8,1.],[.65,.85,1.],[.8,.9,1.],[1.,.48,.67],[.85,.6,1.],[.8,.78,1.],[.9,.7,.9],[.9,.75,.9]])
def chapter_tint(t):
 i=max(0,min(len(CHAPTER_T)-2,np.searchsorted(CHAPTER_T,t,'right')-1));u=ease((t-CHAPTER_T[i])/max(.01,CHAPTER_T[i+1]-CHAPTER_T[i]));return TINT[i]*(1-u)+TINT[i+1]*u

def scenery_ownership(ni,t,edit):
 lower=EDITS[edit['shot']-1].group if edit['shot'] else 0;upper=34
 for event in EDITS:
  if event.time>t and event.group>lower:upper=event.group;break
 guard=edit['lyric_guard']
 if guard and ni==guard['index']:return True
 return lower<=ni<upper

def impact_origin(event,t):
 if event['name'] in PDOOM_LYRIC_INDICES:
  index=PDOOM_LYRIC_INDICES[event['name']];wi=next(j for j,token in enumerate(TOKEN_SCORES[index]) if token_norm(token['text'])=='pdoom')
  center=TOKEN_GROUPS[index][TOKEN_SCORES[index][wi]['group']]['center']
  point=(token_matrix(index,wi,event['time'])@np.r_[center,1.])[:3]
  point[2]+=camera_state(t,np,math)['travel']-camera_state(event['time'],np,math)['travel']
  return point
 index={'FOOM':5,'SINGULARITY':10,'ATOMS':12,'BASILISK BOOM':14,'FUSE':25,'SAFETY FENCE':28,'SELF UPGRADE':31}[event['name']]
 matrix=node_matrix(index,event['time'])
 local=(8.,-4.4,2.) if event['name']=='FOOM' else event['origin']
 point=(matrix@np.r_[local,1.])[:3]
 point[2]+=camera_state(t,np,math)['travel']-camera_state(event['time'],np,math)['travel']
 return point

def draw_blasts(t,vp,hit,impact,tint):
 ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
 for event in impact['events']:
  origin=impact_origin(event,t);age=event['age'];power=event['power'];kind=event['kind'];p=event['shock_progress'];d=event['debris_progress'];polarity=event['polarity']
  prog['chapterTint'].value=tuple(event['color']);base=tr(*origin)
  direction=np.array(event['direction']);yaw=math.atan2(direction[0],max(.25,abs(direction[2])))
  orientation=rot(yaw*.3,1)@rot((.7 if kind=='vertical' else -.25 if kind=='directional' else .08),2)
  if age<0:
   BLAST['pressure'].draw(base@orientation@sc(1.35-event['charge']*.97),vp,t,hit,0,-1,gain=event['charge']*.65)
   continue
  if p<1:
   expansion=.08+event['shock_travel']*2.6 if polarity>0 else 2.6*(1-event['shock_travel'])+.07
   aspect=np.diag([.65,1.75,.9,1.]) if kind=='vertical' else np.diag([1.65,.65,1.,1.]) if kind in ['directional','chain'] else np.eye(4)
   BLAST['shockwaves'].draw(base@orientation@aspect@sc(expansion),vp,age,hit,p*power,40,gain=(1-p)**.8*power*2.9)
  if age>.025 and d<1:
   exp=.15+d*1.7;flight=direction*(d*6.);flight[1]-=d*d*3
   BLAST['shards'].draw(base@tr(*flight)@orientation@sc(exp),vp,age,hit,d*power,41,gain=event['debris']*1.75)
   if kind in ['radial','fracture','recursive','implosion']:
    BLAST['plates'].draw(base@tr(0,-d*d*2,d*5)@rot(d*1.45,1)@orientation@sc(.25+d*1.6),vp,age,hit,d*power,42,gain=event['debris']*(1.55 if kind=='fracture' else .95))
  if .035<age<.70:
   ctx.line_width=1.75
   RUPTURE['faults'].draw(base@orientation@rot(age*(3.5 if kind=='recursive' else -2.3),2)@sc(.20+age*2.6),vp,age,hit,age*power*1.8,42,gain=power*(1-age/.70)*1.4)
   ctx.line_width=1.3
  if .02<age<.38:
   BLAST['streaks'].draw(base@tr(0,0,age*70)@orientation@sc(.35+age*2.6),vp,age,hit,age*2,40,gain=power*(1-age/.38)*1.8)
  if .13<age<.95:
   BLAST['arcs'].draw(base@orientation@sc(.55+d*.9),vp,age,hit,math.sin(age*19)*.12,43,gain=event['debris']*(.25+.35*abs(math.sin(age*49))))
 ctx.disable(gl.BLEND);ms.depth_mask=True;prog['chapterTint'].value=tuple(tint)

def draw_red_path(points,vp,gain=2.):
 data=[]
 for j in range(len(points)-1):
  for pp in [points[j],points[j+1]]:data.append([*pp,*ACC,j/max(1,len(points)-1),0.])
 contactbuf.write(np.array(data,'f4').tobytes());prog['model'].write(np.eye(4,dtype='f4').tobytes());prog['vp'].write(np.array(vp.T,'f4').tobytes());prog['motion']=-1;prog['gain']=gain;prog['reveal']=1.;prog['tracer']=0.;prog['text_role']=1.
 ctx.line_width=2.;contactvao.render(gl.LINES,vertices=len(data));ctx.line_width=1.2

def draw_epilogue(t,vp,o):
 if t<153.95:
  draw_long_outro(t,vp);return
 k=o['beat_index'];phase=o['motif_progress'];pulse=o['pulse'];sub=o['secondary'];stage=o['stage'];network=o['network_growth'];capture=o['world_capture'];collapse=o['collapse'];recursive=o['recursion'];loop=o['infinity']
 prog['clearBox'].value=(3.,3.,.01,.01);prog['chapterTint'].value=tuple(o['world_tint'])
 ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
 if stage==0:
  rev=min(1.,(k+1+phase*.7)/8);growth=.75+network*.38
  EPILOGUE['network'].draw(tr(0,0,-3)@sc(growth),vp,t,pulse,0,-1,gain=1.15+pulse*.7,reveal=rev)
  if k>=3:EPILOGUE['clamps'].draw(tr(0,0,-5)@np.diag([.85-phase*.1,.6,.5,1.]),vp,t,pulse,0,-1,gain=.25+pulse*.35,reveal=min(1.,(k-2)/3))
  if k>=4:
   for j in range(min(7,k-2)):
    x=-12+j*4.0;signal.draw(tr(x,3*math.sin(j*1.4),-2)@sc(1.3+sub*.5),vp,t,pulse,gain=1.8+pulse)
  if k>=6:EPILOGUE['spine'].draw(tr(0,-1,-7)@sc(1.1),vp,t,pulse,0,-1,gain=.75+pulse*.9,reveal=min(1,(k-5+phase)/2))
 elif stage==1:
  globe=tr(0,0,-4)@rot(capture*.35,1)@sc(1.65+.15*pulse)
  EPILOGUE['network'].draw(tr(0,0,-12)@sc(1.25),vp,t,pulse,0,-1,gain=.45+pulse*.3)
  globe_gain=1.05+.8*pulse if k<13 else .32*(1-phase) if k==13 else .05
  EPILOGUE['world'].draw(globe,vp,t,pulse,0,-1,gain=globe_gain)
  clamp=tr(0,0,-3)@np.diag([1.35-capture*.45,1.5,1.4,1.]);EPILOGUE['clamps'].draw(clamp,vp,t,pulse,0,-1,gain=1+pulse*.9,reveal=min(1,(k-7+phase)/2))
  if k>=10:EPILOGUE['clamps'].draw(clamp@rot(math.pi/2,2)@sc(.8),vp,t,pulse,0,-1,gain=.6+pulse*.6)
  if k==11:environments[0].draw(tr(0,0,-12)@sc(3.0),vp,t,pulse,0,0,gain=.8+pulse*.8)
  if k>=13:
   throat=np.array([13.,-1.,-9.]);environments[4].draw(tr(*throat)@rot(-.35,1)@sc(.72),vp,t,pulse,1.,4,gain=.9+pulse*.6)
   # The captive globe genuinely breaks apart and flows to the side intake.
   # Its intact surface loses dominance instead of remaining under the shards.
   for j in range(5):
    feed=float(np.clip((k-13+phase-j*.18)/2.3,0,1));offset=throat*feed;offset[2]-=4*(1-feed)
    EPILOGUE['shell'].draw(tr(*offset)@rot(j*.7+feed*.35,1)@sc((1.2-feed*.85)*(.8 if j else 1.2)),vp,t,pulse,.15+feed*.35,42,gain=(.35+pulse*.45)*(1-feed*.5))
   cable_start=np.array([-4.,-2.,-3.]);cable_end=throat+[-1.,0.,1.]
   if k<15:
    points=[]
    for u in np.linspace(0,1,60):
     pp=cable_start*(1-u)+cable_end*u;pp[1]-=math.sin(u*math.pi)*(1-phase)*.6;points.append(pp)
    draw_red_path(points,vp,2.7+pulse)
   else:
    # The last independent connection breaks on this attack and whips back.
    gap=.07+phase*.23
    for side in [-1,1]:
     a,b=(0.,.5-gap) if side<0 else (.5+gap,1.);points=[]
     for u in np.linspace(a,b,28):
      pp=cable_start*(1-u)+cable_end*u;pp[1]+=side*math.sin(u*math.pi)*(1+pulse*3+phase);points.append(pp)
     draw_red_path(points,vp,3.2)
    BLAST['arcs'].draw(tr(4.5,-1.5,-5)@sc(.22+phase*.12),vp,t,pulse,0,-1,gain=.8+pulse*2.)
 elif stage==2:
  EPILOGUE['network'].draw(tr(0,0,-3)@rot(math.pi if k>=21 else 0,1)@sc(1.3),vp,t,pulse,collapse,44,gain=.8+pulse*.9)
  if k<19:EPILOGUE['world'].draw(tr(0,0,-5)@sc(1.65*(1-collapse*.8)),vp,t,pulse,collapse*.6,44,gain=.8+pulse*.5)
  if k>=19:
   shatter=(k-19+phase)*.5
   EPILOGUE['shell'].draw(tr(0,-shatter*shatter,-3+shatter*4)@sc(.7+shatter*.5),vp,t,pulse,shatter,41,gain=max(.2,1.1-shatter*.25)+pulse*.7)
  if k>=21:
   for j in range(1+(k-21)*2):
    EPILOGUE['recursive'].draw(tr(0,0,-j*5+phase*3)@rot((-.18 if j%2 else .18),2)@sc(1.35-j*.09),vp,t,pulse,0,-1,gain=.65/(1+j*.15)+pulse*.3)
 else:
  # The broken graph becomes the permanent two-lobed route. It is drawn in
  # strokes before the maker's engraving, then held without a fade to black.
  EPILOGUE['recursive'].draw(tr(0,0,-22)@sc(1.3),vp,t,pulse,0,-1,gain=.18*(1-loop*.3))
  layout=end_title_layout(t);inf=layout['infinity'];title=layout['title'];credit=layout['credit'];rail=layout['maker_rail']
  title['reveal']=float(ease((t-153.95)/.35));credit['reveal']=float(ease((t-154.08)/.37))
  infinity.draw(tr(*inf['position'])@sc(inf['scale']),vp,t,pulse,0,-1,gain=inf['gain']+pulse*.5,reveal=inf['reveal'])
  if k==25:EPILOGUE['clamps'].draw(tr(0,3.,-6)@np.diag([1.1-phase*.2,.8,1.,1.]),vp,t,pulse,0,-1,gain=.45+pulse*.7)
  ctx.disable(gl.DEPTH_TEST)
  if title['reveal']>0:songtitle.draw(tr(*title['position'])@rot(title['rotation'][0],0),vp,t,0,gain=title['gain'],reveal=title['reveal'])
  if credit['reveal']>0:
   maker.draw(tr(*credit['position']),vp,t,0,gain=credit['gain'],reveal=credit['reveal'])
   EPILOGUE['spine'].draw(tr(*rail['position'])@np.diag([*rail['scale'],1.]),vp,t,0,0,-1,gain=rail['gain'])
  ctx.enable(gl.DEPTH_TEST)
 # The red witness changes trajectory with its consequences, and is always
 # the same red wire motif rather than a new unrelated central ornament.
 if stage==0:
  x=-17+(k+phase)/8*34;point=np.array([x,3.0*math.sin((k+phase)*.9),0.])
  wake=[]
  for xx in np.linspace(max(-17,x-11),x,50):wake.append([xx,3*math.sin((xx+17)/34*8*.9),0.])
  draw_red_path(wake,vp,1.8+pulse)
  if k>=2:
   branch=[]
   for xx in np.linspace(max(-8,x-10),x,40):branch.append([xx,-3*math.sin((xx+17)/34*8*.9),-.4])
   draw_red_path(branch,vp,1.2+pulse*.8)
 elif stage==1:
  angle=(k-8+phase)*math.pi*.42;point=np.array([12*math.cos(angle),10*math.sin(angle),-4+4*math.sin(angle*.5)])
 elif stage==2:
  angle=(k-16+phase)*1.4;r=max(.6,10*(1-collapse));point=np.array([r*math.cos(angle),r*.7*math.sin(angle),-2+phase*2])
 else:
  a=min(math.tau,max(0,(t-152.05)/(153.87-152.05)*math.tau));point=np.array([15*math.cos(a)/(1+math.sin(a)**2),3.+10.5*math.sin(a)*math.cos(a)/(1+math.sin(a)**2),-.5])
 signal.draw(tr(*point)@sc(1.2+pulse*.9+sub*.4),vp,t,pulse,gain=4.+pulse*2.)
 if o['blast']>.015:
  age=o['beat_elapsed'];amp=o['blast'];base=tr(0,0,-4)
  BLAST['shockwaves'].draw(base@sc(.15+min(1,age/.3)*2.5),vp,age,pulse,age*2,40,gain=amp*1.7)
  if stage in [1,2]:BLAST['plates'].draw(base@sc(.45+age*2.4),vp,age,pulse,age*3,42,gain=amp*.9)
 if sub>.05:BLAST['arcs'].draw(tr(*point)@sc(.18),vp,t,sub,0,-1,gain=sub*.9)
 ctx.disable(gl.BLEND);ms.depth_mask=True

def draw_long_outro(t,vp):
 long=sample_outro_flight(t);pulse=long['pulse'];gain=long['flight_gain'];distance=long['distance'];prog['clearBox'].value=(3.,3.,.01,.01)
 ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
 for station in np.arange(0.,586.,65.):
  if not -95.<station-distance<180.:continue
  kind=['radial','vertical','fracture','recursive'][min(3,int(station/150.))]
  FLIGHT_WORLD[kind].draw(np.array(route_frame(float(station))),vp,t,0,0,-1,gain=(.52+pulse*.14)*gain)
 for scene in long['geometry_instances']:
  for draw in scene['draws']:
   EPILOGUE[draw['mesh']].draw(np.array(draw['model']),vp,t,pulse,draw['action'],draw['motion'],gain=draw['gain']*gain*1.2,reveal=draw['reveal'])
 draw_red_path([np.array(x) for x in long['witness_path']],vp,(1.7+pulse*1.5)*max(.1,gain))
 signal.draw(tr(*long['witness'])@sc(.85+pulse*.65),vp,t,pulse,gain=3.4+pulse*2.)
 if t>=152.5:
  layout=end_title_layout(t);inf=layout['infinity'];infinity.draw(tr(*inf['position'])@sc(inf['scale']),vp,t,pulse,0,-1,gain=inf['gain']+pulse*.5,reveal=min(1.,float(ease((t-152.5)/.8))))
 ctx.disable(gl.BLEND);ms.depth_mask=True

def draw_flight_scene_layers(t,vp,cam,frame,focus):
 if semantic_state(t)['name'] in ['moon','omega','basilisk','branch_seed','loom','transformer']:return
 if metaphor_state(t)['active']:return
 if cam['name'] not in NARRATIVE_EVENTS:return
 event=NARRATIVE_EVENTS[cam['name']];cross=cam['crossing_time'];handoff=cam['handoff_time'];parts=event['parts']
 times=[cross+.03,cross+(handoff-cross)*.43,handoff-.09]
 if cam['name']=='GO DISASTER':times=[95.230,95.435,95.680]
 for j,(at,part) in enumerate(zip(times,parts)):
  pose=flight_pose(at,cam['name'],True);point=np.array(pose['eye']);point[2]+=camera_state(t,np,math)['travel']-camera_state(at,np,math)['travel']
  point+=np.array(pose['flight_forward'])*5.
  matrix=tr(*point)@frame@rot((j-1)*.45,2)@rot((-.30 if j%2 else .22),1)@sc(1.5 if part not in [4,0] else 1.9)
  environments[part].draw(matrix,vp,t,.20+sample_disaster(t)['shock']*.7,0,part,gain=.55+.22*j)

def metaphor_base(name,t,index):
 cue={'chinese':'CHINESE ROOM','shoggoth':'MASK REVEAL','paperclip':'PDOOM 3','chinchilla':'DISOBEY','feedback':'ASKEW','unknown':'SELF UPGRADE'}.get(name)
 if cue:
  context=flight_context(cue);pose=flight_pose(context['event']['time'],cue);focus=context['focus']+np.array([0.,0.,camera_state(t,np,math)['travel']-camera_state(context['entry_time'],np,math)['travel']]);basis=np.eye(4);basis[:3,:3]=np.array([pose['right'],pose['up'],pose['word_plane_normal']]).T
  depth={'chinese':-6.,'shoggoth':-7.,'paperclip':-25.,'chinchilla':-30.,'feedback':-3.,'unknown':-42.}[name]
  return tr(*focus)@basis@tr(0,0,depth)
 return node_matrix(index,t)@tr(0,0,-8.)

def metaphor_station(cue,reference,t,distance=18.):
 # A sculpture is fixed along an authored flight, never attached to the lens.
 # Only the common world translation is carried forward after placement.
 pose=flight_pose(reference,cue,True);forward=unit(pose['flight_forward'])
 right=unit(np.cross(forward,pose['up']));up=unit(np.cross(right,forward))
 center=np.array(pose['eye'])+forward*distance
 center[2]+=camera_state(t,np,math)['travel']-camera_state(reference,np,math)['travel']
 basis=np.eye(4);basis[:3,:3]=np.array([right,up,-forward]).T
 return tr(*center)@basis

def draw_metaphors(t,vp):
 score=metaphor_state(t)
 if not score['active']:return
 name=score['name'];u=score['u'];amp=score['exposure'];base=metaphor_base(name,t,score['index']);ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE);ctx.line_width=1.65
 if semantic_state(t)['name']=='masked':amp*=.65
 def draw(key,matrix=None,gain=1.,reveal=1.,action=0.,motion=-1):
  METAPHOR[key].draw(base if matrix is None else matrix,vp,t,0,action,motion,gain=gain*amp,reveal=reveal)
 def extra(key,matrix=None,gain=1.,reveal=1.,action=0.,motion=-1):
  EXTRA_MET[key].draw(base if matrix is None else matrix,vp,t,0,action,motion,gain=gain*amp,reveal=reveal)
 if name=='chinese':
  phase=(t-26.06)*.8%1.;draw('chinese_shell',gain=.5);draw('chinese_rules',gain=1.4)
  draw('chinese_input',base@tr(phase*5.3,0,0),gain=1.25)
  draw('chinese_carriage',base@tr(7.*math.sin((t-26.06)*2.5),0,0),gain=1.2)
  draw('chinese_output',base@tr(max(0.,phase-.15)*3.4,0,0),gain=1.4,reveal=float(ease((t-26.5)/.6)))
  draw('chinese_chair',gain=2.)
  pp=[[-16+phase*24,4.9,-.3],[-10,4.9,-.3],[-8,7,-6.5],[7,7,-6.5],[13,5,-.3]];draw_red_path([(base@np.r_[p,1.])[:3] for p in pp],vp,2.2)
 elif name in ['shoggoth','feedback']:
  opened=float(ease((t-30.05)/1.2)) if name=='shoggoth' else float(ease((t-121.6)/.7))
  if name=='feedback':base=base@tr(-2.,0.,0.)@sc(.68)
  draw('shoggoth_shell',base,gain=.45);draw('shoggoth_tendrils',base,gain=1.1,action=opened*.55,motion=7)
  draw('shoggoth_organs',base,gain=1.3,reveal=.3+.7*opened);draw('shoggoth_puppetry',base,gain=.75)
  draw('shoggoth_mask',base@tr(-opened*5.5,0,opened*2)@rot(-opened*.45,1),gain=1.5)
  draw('shoggoth_split',base@tr(opened*5.5,0,opened*2)@rot(opened*.45,1),gain=1.5)
  if name=='shoggoth':
   # The smile opens onto a body extending around the next bend in the path.
   body=metaphor_station('MASK REVEAL',31.45,t,20.)@sc(1.3)
   draw('shoggoth_shell',body,gain=.65,reveal=.25+.75*opened)
   draw('shoggoth_tendrils',body,gain=1.65,reveal=.25+.75*opened)
   draw('shoggoth_organs',body,gain=2.3,reveal=.2+.8*opened)
   draw('shoggoth_puppetry',body,gain=1.25,reveal=opened)
  if name=='feedback':
   for j in range(3):draw('orthogonal_couplings',base@tr(8,-2,-j*2)@rot(j*1.1+opened*.7,2)@sc(.72),gain=.8)
 elif name=='paperclip':
  # Human furniture, reduction rollers and the bending die occupy successive
  # physical factory bays. Their products fill the route beyond the blast.
  for j,ref in enumerate([96.26,97.23,97.95]):
   bay=metaphor_station('PDOOM 3',ref,t,20.)@tr(3.5,1.,0.)@sc(1.1)
   feed=float(ease((t-(96.34+j*.50))/.83))
   draw('paperclip_conveyor',bay,gain=.95)
   draw('paperclip_forming',bay,gain=1.65)
   draw('paperclip_sources',bay@tr(feed*7.,-feed*2.,feed)@np.diag([1-feed*.67,1-feed*.58,1,1]),gain=1.8*(1-feed*.72))
   draw('paperclip_planet',bay@tr(-feed*7.,-feed*5.,0)@sc(1-feed*.72),gain=1.2*(1-feed*.65))
   draw('paperclip_shredder',bay@rot(math.sin(t*14)*.035,2),gain=1.45)
   draw('paperclip_swarm',bay@tr(0,0,-12),gain=1.35,reveal=.015+.985*feed)
  swarm=metaphor_station('PDOOM 3',98.45,t,13.)
  draw('paperclip_swarm',swarm,gain=1.5,reveal=float(ease((t-97.05)/.7)))
 elif name=='orthogonal':
  base=base@sc(.86);draw('orthogonal_frame',base,gain=1.3);draw('orthogonal_couplings',base,gain=1.0)
  draw('orthogonal_ability',base,gain=1.2,reveal=.12+.88*u);draw('orthogonal_ascent',base@tr(0,(u*4)%2,0),gain=1.2)
  draw('orthogonal_goal',base,gain=1.8);draw('orthogonal_clips',base,gain=1.1,reveal=.12+.88*u)
 elif name=='sharpturn':
  turn=float(ease((t-81.62)/.84));extra('constraint',gain=1.1)
  extra('capability',base@rot(-turn*1.5,1)@tr(0,0,-turn*19),gain=2.)
  path=[[0,0,z] for z in np.linspace(8,-10,18)]+[[-19*turn*s,0,-10-8*s] for s in np.linspace(0,1,25)]
  draw_red_path([(base@np.r_[p,1.])[:3] for p in path],vp,2.8)
 elif name=='chinchilla':
  dense=float(ease((t-115.23)/1.02))
  intro=metaphor_station('DISOBEY',115.10,t,17.)@sc(1.3)
  extra('hollow',intro@tr(5.,0.,1.),gain=1.5)
  extra('data',intro@tr(-3.,0.,0.),gain=1.25,reveal=.45+.55*dense)
  extra('dense',intro@sc(1.75)@tr(-6.,0.,3.),gain=1.65,reveal=float(ease((t-115.05)/.5)))
  catcher=semantic_host('chinchilla-catch',115.30,t,18.,1.15)@tr(-1,0,0)
  extra('data',catcher,gain=1.6,reveal=.7+.3*dense)
  extra('dense',catcher@tr(6,0,-3)@sc(2.3)@tr(-6,0,3),gain=1.75,reveal=float(ease((t-115.05)/.5)))
  processor=metaphor_station('DISOBEY',115.52,t,22.)@sc(1.35)
  extra('hollow',processor@tr(dense*4,0,0)@sc(1-dense*.28),gain=1.55*(1-dense*.4))
  extra('data',processor,gain=1.75,reveal=.4+.6*dense)
  extra('dense',processor@tr(6,0,-3)@sc(1.+dense*.7)@tr(-6,0,3),gain=1.65,reveal=dense)
  core=metaphor_station('DISOBEY',116.17,t,20.)@sc(1.6)@tr(-6,0,3)
  extra('data',core,gain=1.35,reveal=.15+.85*dense)
  extra('dense',core@tr(6,0,-3)@sc(2.)@tr(-6,0,3),gain=1.75,reveal=dense)
 elif name=='recursive':
  extra('robot',gain=1.0)
  for j in range(3):
   growth=float(ease((t-128.3-j*.65)/1.0));parent=base@tr(j*1.4,0,-j*16)@sc(1+j*.22)
   extra('offspring',parent,gain=1.3,reveal=growth);extra('arm',parent@rot(math.sin(t*4+j)*.09,1),gain=1.2,reveal=min(1.,growth+.2))
   if growth>.1:BLAST['arcs'].draw(parent@tr(-2,1.2,-10)@sc(.14),vp,t,0,0,-1,gain=(.5+abs(math.sin(t*35)))*amp)
 elif name=='unknown':
  extra('window',gain=1.05,action=float(ease((t-132.5)/.7)),motion=53)
 ctx.line_width=1.2;ctx.disable(gl.BLEND);ms.depth_mask=True

def semantic_host(label,reference,t,distance=20.,scale=1.):
 key=(label,reference,distance,scale)
 if key not in SEM_HOSTS:
  state,eye,target,_=frame_view(reference,0)
  view=view_matrix(eye,target,state['roll'],state['impact_camera'])
  basis=np.linalg.inv(view);center=np.array(eye)+unit(target-eye)*distance
  shot=sample_shot(reference)
  if not state['impact_camera']['active']:
   rx,ry,rz=shot['word_plane_rotation'];physical=rot(ry,1)@rot(rx,0)@rot(rz,2)
   basis[:3,:3]=physical[:3,:3]
   anchor=shot_origin(shot,reference)+np.array(shot['word_anchor'])
   center=center*.78+anchor*.22
  basis[:3,3]=center
  basis=basis@rot(-.16,1)@rot(.06,0)
  SEM_HOSTS[key]=basis@sc(scale)
 host=SEM_HOSTS[key].copy();host[2,3]+=camera_state(t,np,math)['travel']-camera_state(reference,np,math)['travel']
 return host

def draw_semantics(t,vp,hit):
 draw_integrated(t,vp,hit,globals())

def drawframe(t):
 global last_camera_stats,FREEZE_BUFFER
 if t>=154.6 and FREEZE_BUFFER is not None:return FREEZE_BUFFER
 t=min(t,154.6)
 idx=next((i for i,r in enumerate(lines) if r[0]<=t<r[1]),-1)
 if idx<0:idx=max(0,min(33,np.searchsorted([r[0] for r in lines],t,'right')-1))
 a,b,*_=lines[idx];u=float(np.clip((t-a)/(b-a),0,1));sharp,hit=beatstate(t);state,eye,target,vp=frame_view(t,hit);travel=state['travel'];section=state['section'];edit=state['edit'];cut=edit['transition'];impact=state['impact'];outro=state['outro'];prog['storytime']=float(t);prog['chapterTint'].value=tuple(edit['world_tint'])
 event=impact['event'];origin=impact_origin(event,t) if event else np.zeros(3)
 prog['stress']=(float(impact['charge']),float(impact['shock']),float(event['shock_radius'] if event else 0),float(impact['burst']));prog['blastOrigin'].value=tuple(origin)
 cue=max(impact['tension_cues'],key=lambda c:c['strain'],default=None);prog['strain'].value=(*cue['axis'],cue['strain']) if cue else (0.,0.,0.,0.)
 lexical=active_word_indices(idx,t) if t<141.2 else [];current=TOKEN_SCORES[idx][lexical[0]]['row'] if lexical else -1
 points=row_corners(idx,current,t);clip=points@vp.T;ndc=clip[:,:2]/clip[:,3:4]
 active_text=[TOKEN_SCORES[idx][j]['text'] for j in lexical]
 last_camera_stats={'t':float(t),'idx':int(idx),'row':int(current),'xmin':float(ndc[:,0].min()) if lexical else 0.,'xmax':float(ndc[:,0].max()) if lexical else 0.,'ymin':float(ndc[:,1].min()) if lexical else 0.,'ymax':float(ndc[:,1].max()) if lexical else 0.,'travel':float(travel),'shot':edit['shot'],'transition':cut['kind'],'visible_words':active_text,'word_count':len(lexical)}
 last_camera_stats.update(kind=state['shot_design']['kind'],lens=state['lens'],roll=state['roll'],eye=eye.tolist(),target=target.tolist(),base_eye=state['base_eye'].tolist(),base_target=state['base_target'].tolist(),base_roll=state['base_roll'],impact_camera=state['impact_camera'],aggression=state['aggression']['label'],metaphor=metaphor_state(t)['name'])
 # A soft local illumination pocket gives the sung line contrast, while preserving moving foreground edges.
 mn=ndc.min(axis=0);mx=ndc.max(axis=0);prog['clearBox'].value=(*(mn+mx)*.5,*np.maximum((mx-mn)*.65,.08))
 if outro['active'] or not lexical:prog['clearBox'].value=(3.,3.,.01,.01)
 ms.use();ms.clear(.002,.006,.011,1,depth=1);ctx.enable(gl.DEPTH_TEST);ctx.disable(gl.BLEND);ctx.line_width=1.35
 ag=state['aggression'];force=ag['scene_force'];prog['forces']=(force['loss_drop'],force['jaw_bite'],force['accel_lane'],force['left_turn']);prog['forces2']=(force['disobey_shear'],force['rack_askew']);disaster=sample_disaster(t);prog['disasterFX']=(*disaster['quake_displacement'],disaster['collapse'])
 growth=.1+.9*ease(t/9);tension=.7+.3*ease((t-38)/80)
 # Persistent world layers move continuously but change their physical role by chapter.
 weights=chapter_weights(t);_,_,_,_,_,_,sx,sy=weights
 wi,wc,wd,wr,ws,wm=[edit['world_weights'][k] for k in ['infrastructure','city','debris','data_ribbons','skeleton','memory']]
 semantics=metaphor_state(t);meaning=semantic_state(t);hero=meaning['name'] in ['transformer','moon','omega','branch_seed','loom','masked'];semantic_gain=(1.-semantics['exposure']*.78)*(1.-meaning['exposure']*(.60 if meaning['name']=='transformer' else .25))
 wi*=semantic_gain;wc*=semantic_gain;wd*=semantic_gain;wr*=semantic_gain;ws*=semantic_gain;wm*=semantic_gain
 # Instrument inserts need an identifiable foreground part. The surrounding
 # machine still travels past, at a lower exposure than the inspected part.
 detail=edit['shot'] in [11,15,17,26,27,29]
 if detail:wi*=.30;wc*=.35;wd*=.24;wr*=.38;ws*=.34;wm*=.32
 pressure=ease((t-22.2)/1.42)*(1-ease((t-23.620)/.18));burst=ease((t-23.620)/.20)*(1-ease((t-26.5)/1.2))
 maskMaw=ease((t-16)/.7)*(1-ease((t-26.0)/.7));maskRoom=ease((t-26)/.6)*(1-ease((t-30.0)/.6));maskFactory=ease((t-89.5)/.7)*(1-ease((t-109.2)/.7))
 wi*=1-.95*max(maskMaw,maskRoom,maskFactory);wc*=1-.95*max(maskMaw,maskFactory);ws*=1-.7*max(maskMaw,maskRoom,maskFactory)
 worldM=np.diag([sx*(1-pressure*.36+burst*.8),sy*(1-pressure*.22),1.,1.])
 rx,ry,rz=edit['world_rotation'];ex,ey,ez=edit['world_scale'];backgroundM=worldM@rot(rz,2)@rot(ry,1)@rot(rx,0)@np.diag([ex,ey,ez,1.]);worldphase=travel+edit['world_phase']+ag['world_speed']
 cityLift=-8.5*(1-ease((t-23.620)/.45)) if t>22.2 else -4*(1-ease(t/12))
 # Background engraving is additive and does not write depth, preserving clear foreground contours.
 ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
 WORLD['infrastructure'].draw(backgroundM,vp,worldphase*.78,hit,0,36,gain=.68*growth*wi)
 WORLD['city'].draw(backgroundM@tr(0,-.5+cityLift,0),vp,worldphase,hit,0,36,gain=.80*growth*wc*(.18 if t<22.2 else .25+.75*ease((t-23.620)/.35)))
 WORLD['debris'].draw(backgroundM,vp,worldphase*1.3,hit,0,37,gain=.65*growth*wd)
 WORLD['data_ribbons'].draw(backgroundM,vp,worldphase*.86,hit,0,35,gain=.90*growth*wr)
 STORY['road'].draw(worldM,vp,travel,hit,0,38,gain=(1.0-.78*max(maskMaw,maskRoom,maskFactory))*(.18 if outro['active'] else .30 if detail else 1.)*semantic_gain)
 STORY['signals'].draw(worldM,vp,travel,hit,0,38,gain=1.0+hit*.6)
 STORY['memory'].draw(worldM,vp,travel,hit,0,38,gain=.65*growth*wm*(1-.6*maskFactory))
 factory.draw(np.eye(4),vp,travel,hit,0,38,gain=1.1*maskFactory*semantic_gain)
 cam=state['impact_camera']
 if cam['active']:
  flight_ctx=flight_context(cam['name']);focus=flight_ctx['focus']+np.array([0.,0.,travel-camera_state(flight_ctx['entry_time'],np,math)['travel']]);frame=np.eye(4);frame[:3,:3]=np.array([cam['right'],cam['up'],cam['word_plane_normal']]).T
  kind={'vertical':'vertical','fracture':'fracture','recursive':'recursive'}.get(flight_ctx['event']['kind'],'radial');gain=2.1*float(ease((t-cam['start_time'])/.065))*(1.-semantics['exposure']*.85)*(1.-meaning['exposure']*.55)
  for depth in [0.,-85.]:FLIGHT_WORLD[kind].draw(tr(*focus)@frame@tr(0,0,depth),vp,t,0,0,-1,gain=gain)
  draw_flight_scene_layers(t,vp,cam,frame,focus)
 if ag['razor_gain']>.01 and not outro['active']:
  shot=state['shot_design'];rx0,ry0,rz0=shot['word_plane_rotation'];host=shot_origin(shot,t)+np.array(shot['word_anchor'])
  RUPTURE['ribs'].draw(tr(*host)@rot(ry0,1)@rot(rx0,0)@rot(rz0,2),vp,t,hit,0,46,gain=ag['razor_gain']*.64)
 ms.depth_mask=True;ctx.disable(gl.BLEND)
 # A small number of real near-field beams retain depth occlusion and sweep past the lens.
 STORY['machine_skeleton'].draw(worldM,vp,travel,hit,0,38,gain=.75*growth*ws*(.12 if meaning['name']=='transformer' else .3 if outro['active'] else 1.))
 # Previous forms physically remain behind us; future forms are visible farther along the road.
 for ni in [idx-1,idx,idx+1]:
  if outro['active']:break
  if not 0<=ni<34:continue
  if not scenery_ownership(ni,t,edit):continue
  aa,bb=lines[ni][:2];weight=.85*ease((t-aa+.55)/.35)*(1-ease((t-bb)/.65));clock=t;action=ease((t-EVENT[ni])/.7)
  # At an edit boundary the new apparatus is already present, rather than
  # spending several seconds fading into the outgoing shot's centre.
  if ni==edit['scene_group'] and t>=edit['shot_start']:weight=max(weight,.85)
  # Hold the eye and the signed approval sheet until their motivated cuts.
  # An instrumental breath is still part of the outgoing shot.
  if (ni==8 and 36.1<t<38.190) or (ni==17 and 72.5<t<73.870):weight=.85
  if weight<.02:continue
  envsize={4:2.35,5:1.7,6:1.8,7:1.5,8:1.6,13:1.6,14:1.6,16:1.7,22:1.9,23:2.0,24:1.7,27:1.5,28:1.6,29:1.6,30:1.7,31:1.6,32:1.8,33:1.8}.get(ni,1.3)
  em=node_matrix(ni,t)@sc(envsize)
  if ni==7:em=em@tr(3,0,-1)@rot(-.2,2)
  if ni==14:em=em@tr(-2,-1,-2)@rot(.55,2)@rot(.3,1)
  if ni==10:em=em@rot(-.2,0)
  if ni==27:em=em@tr(2,0,0)
  if ni==29:em=em@rot(action*.2,2)
  if ni==5 and t>23.620:em=em@sc(1+ease((t-23.620)/.25)*1.2)
  for cue in impact['tension_cues']:
   strain=cue['strain']
   if ni==4 and cue['kind']=='jaw':em=em@np.diag([1,1-strain*.4,1,1])
   if ni==11 and cue['kind']=='stretch':em=em@np.diag([1+strain*.65,1,1+strain*.9,1])
   if ni==24 and cue['kind']=='squeeze':em=em@np.diag([1-strain*.38,1+strain*.13,1,1])
   if ni==27 and cue['kind']=='shear':em=em@rot(strain*.3,1)
  wordpulse=max([math.exp(-(t-TOKEN_SCORES[idx][j]['start'])/.15) for j in lexical],default=0.) if ni==idx else 0.
  drive=TOKEN_SCORES[idx][lexical[-1]]['drive'] if lexical and ni==idx else 'trace'
  if drive=='expand':em=em@sc(1+wordpulse*.10)
  if drive=='clamp':em=em@np.diag([1-wordpulse*.08,1.,1.,1.])
  if drive=='shear':em=em@rot(wordpulse*.10,2)
  if drive=='weave':em=em@rot(wordpulse*.07,1)
  if drive=='observe':em=em@sc(1+wordpulse*.06)
  environments[ni].draw(em,vp,clock,hit*1.3+wordpulse*.3,action,ni,gain=weight*(1+wordpulse*.14)*(1.3 if detail and ni==idx else 1.)*semantic_gain*(.12 if meaning['name']=='transformer' else .75 if hero else 1.))
 draw_metaphors(t,vp)
 draw_semantics(t,vp,hit)
 if impact['active']:draw_blasts(t,vp,hit,impact,edit['world_tint'])
 # The living red signal carries impact energy forward along the actual connected road.
 pos=signal_position(t,travel)
 if not outro['active']:signal.draw(worldM@tr(*pos)@sc(1+hit*.35),vp,t,hit,gain=3.2)
 tail=[]
 for q0 in np.linspace(0,1.5 if t<103.41 else 2.3,45):
  tt=max(0,t-q0);pasttravel=camera_state(tt,np,math)['travel'];pp=signal_position(tt,pasttravel);pp[2]+=travel-pasttravel;tail.append(pp)
 arr=[]
 for j in range(len(tail)-1):
  for pp in [tail[j],tail[j+1]]:arr.append([*pp,*(ACC*(1-j/len(tail))),j/len(tail),0])
 trailbuf.write(np.array(arr,'f4').tobytes());prog['model'].write(np.eye(4,dtype='f4').tobytes());prog['vp'].write(np.array(vp.T,'f4').tobytes());prog['clock']=t;prog['energy']=hit;prog['action']=0;prog['motion']=-1;prog['gain']=1.7;prog['reveal']=1;prog['tracer']=0;prog['text_role']=1
 if not outro['active']:trailvao.render(gl.LINES,vertices=len(arr))
 current_group=EDITS[edit['shot']-1].group if edit['shot'] else 0
 if t<141.2 and (t<lines[idx][1] or idx>=current_group):draw_words(idx,t,vp,hit)
 # The Gato cable has a visible physical contact with the signal, then releases into the factory.
 if 90.0<t<95.1:
  grasp=ease((t-90)/1.2)*(1-ease((t-94.25)/.85));anchor=(word_matrix(22,0,t)@np.array([2.5,.1,.7,1.]))[:3];endpoint=(worldM@np.r_[pos,1.])[:3]
  coords=[]
  for uu in np.linspace(0,1,55):
   pp=anchor*(1-uu)+endpoint*uu;pp+=np.array([math.sin(uu*math.pi)*.35,math.sin(uu*math.pi)*(.45-.35*grasp),0]);coords.append(pp)
  ribbon=[]
  for jj in range(len(coords)-1):
   for pp in [coords[jj],coords[jj+1]]:ribbon.append([*pp,*(ACC*(.6+grasp)),jj/len(coords),0])
  contactbuf.write(np.array(ribbon,'f4').tobytes());prog['model'].write(np.eye(4,dtype='f4').tobytes());prog['vp'].write(np.array(vp.T,'f4').tobytes());prog['motion']=-1;prog['gain']=2.0*grasp;prog['reveal']=1;prog['tracer']=0;prog['text_role']=1;ctx.line_width=2.8
  contactvao.render(gl.LINES,vertices=len(ribbon));ctx.line_width=1.2
  signal.draw(tr(*endpoint)@sc(1.2-.6*grasp),vp,t,hit,gain=2.5*grasp)

 if 133.4<t<141.2:
  awakening=ease((t-133.4)/1.2);environments[0].draw(tr(0,0,-10)@sc(2.0+awakening*.7),vp,t,hit,0,0,gain=.55*awakening)
 # Burst fragments become part of the next environment instead of resetting the world.
 if idx in [5,7,10,14,16,20,23,25,27,28,29,30,31]:
  phase=t-({5:23.620,14:59.985,23:96.335,30:125.460}.get(idx,EVENT[idx]))
  if 0<phase<1.0:shards.draw(node_matrix(idx,t)@tr(0,0,2)@sc(.3+phase*10),vp,t,hit,gain=(1-phase)*.75)
 if cut['active'] and cut['kind']=='shatter':shards.draw(tr(0,0,8)@rot(t*2,2)@sc(2+cut['strength']*2),vp,t,hit,gain=cut['strength']*1.8)
 if outro['active']:draw_epilogue(t,vp,outro)
 ctx.copy_framebuffer(resolve,ms);output.use();ctx.disable(gl.DEPTH_TEST);tex.use(0)
 paper=.85*ease((t-68.2)/.16) if 68.2<=t<73.870 else 0.
 if 104.6<=t<109.330:paper=max(paper,.10*ease((t-104.6)/.16))
 fx={'occlusion':1,'whip':2,'crash':3,'pullback':3,'match':4,'shatter':5}.get(cut['kind'],0)
 angle=(math.pi/2 if cut['axis']=='y' else -.6 if cut['axis']=='diag' else 0)+(math.pi if cut['direction']<0 else 0)
 post['editFX']=(float(fx),float(cut['phase']),float(cut['strength']),float(angle));post['editColor']=tuple(edit['world_tint'])
 anchor=vp@np.r_[origin,1.];uv=anchor[:2]/anchor[3]*.5+.5 if event else np.array([.5,.5])
 post['blastUV']=tuple(float(x) for x in uv);post['blastFX']=(float(impact['shock']),float(impact['flash']),float((event['shock_radius'] if event else 0)*.032),float(impact['aberration']))
 if outro['active']:post['blastFX']=(float(outro['blast']*.6),0.,float(outro['beat_elapsed']*3),float(outro['blast']*.0015))
 if disaster['active']:post['blastUV']=(.5,.5);post['blastFX']=(float(disaster['shock']*.7),float(disaster['flash']),float((t-94.8)% .455),float(disaster['chromatic']))
 if outro['active']:
  long=state['long_outro'];post['blastFX']=(float(long['pulse']*.19*long['flight_gain']),0.,float(long['beat_elapsed']*3),float(long['chromatic']))
 post['finalFade']=1.;post['paper']=paper;post['impact']=sharp*.6;post['flash']=sharp*.12;q.render(gl.TRIANGLE_STRIP)
 result=output.read(components=3,alignment=1)
 if t>=154.6:FREEZE_BUFFER=result
 return result

def row_corners(i,j,t):
 points=[]
 for index in active_word_indices(i,t):
  gpu=TOKEN_DATA[i][index][0];matrix=token_matrix(i,index,t)
  for xx in [gpu.bmin[0],gpu.bmax[0]]:
   for yy in [gpu.bmin[1],gpu.bmax[1]]:
    for zz in [gpu.bmin[2],gpu.bmax[2]]:points.append(matrix@np.array([xx,yy,zz,1]))
 return np.array(points) if points else np.array([[0.,0.,0.,1.]])

def prepare_compositions():
 # The camera intentionally passes a physical word. Never counteract that
 # translation by widening the lens or shrinking every word in a whole shot.
 json.dump({'word_scale_guard':WORD_SCALE_GUARD,'shots':[dict(sample_shot((([0.]+list(CUT_TIMES))[i]+(list(CUT_TIMES)+[141.2])[i])*.5)) for i in range(32)]},open('v16/compositions.json','w'),indent=2)
 json.dump({'events':[dict(e.metadata(),t=e.time) for e in EDITS]},open('v16/edit_events.json','w'),indent=2)
 json.dump(TOKEN_SCORES,open('v16/word_timeline.json','w'),indent=2)
 print('planned',len(SHOTS),'independent angles; host scale safety',WORD_SCALE_GUARD,flush=True)

def main():
 (ROOT/'output_v16').mkdir(parents=True,exist_ok=True)
 prepare_compositions()
 if '--meaning-preview' in sys.argv:
  episodes=[('opening',[3.7,7.1,11.8,15.2]),('eye-gap',[34.9,36.8,37.6,39.8]),('compute',[55.7,61.5,63.2,65.0]),('training',[67.,70.6,73.3,75.0]),('symbols',[76.6,79.1,86.8,89.3]),('generalist',[90.3,92.5,99.4,101.2]),('attention',[109.9,110.8,111.7,112.8]),('decoder',[113.7,114.8,115.3,116.2]),('futures',[119.7,123.6,127.5,128.5]),('unknown',[133.7,135.2,136.3,138.8])]
  sheet=Image.new('RGB',(1920,len(episodes)*295));d=ImageDraw.Draw(sheet)
  for j,(label,times) in enumerate(episodes):
   for k,t in enumerate(times):
    im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/{label}-{k}.jpg');sheet.paste(im.resize((480,270)),(k*480,j*295));d.text((k*480+4,j*295+272),f'{label} / {t:.3f}s',fill='white')
  sheet.save('v16/meaning_storyboard.jpg');print('meaning preview saved',flush=True);return
 if '--metaphor-preview' in sys.argv:
  episodes=[('chinese',[26.2,26.9,27.5,29.2]),('shoggoth',[29.8,30.25,30.8,31.45]),('sharpturn',[80.85,81.5,82.1,83.2]),('paperclip',[96.1,96.5,97.1,97.65]),('orthogonal',[104.7,105.9,107.0,108.5]),('chinchilla',[115.1,115.55,116.1,116.7]),('feedback',[120.3,120.9,121.7,122.25]),('recursive',[128.1,129.15,130.2,131.2]),('unknown',[132.4,132.85,133.3,134.5])]
  sheet=Image.new('RGB',(1920,len(episodes)*295));d=ImageDraw.Draw(sheet)
  for j,(label,times) in enumerate(episodes):
   for k,t in enumerate(times):
    im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/{label}-{k}.jpg');sheet.paste(im.resize((480,270)),(k*480,j*295));d.text((k*480+4,j*295+272),f'{label} / {t:.3f}s',fill='white')
  sheet.save('v16/metaphor_storyboard.jpg');print('metaphor preview saved',flush=True);return
 if '--v13-preview' in sys.argv:
  batches=[('go',[94.14,94.30,94.60,94.73,94.80,94.92,95.23,95.435,95.68,95.86,96.00,96.40]),('newwords',[10.58,10.88,11.13,12.12,47.60,48.20,48.53,48.62,76.50,77.05,77.18,77.28,114.32,114.70,114.91,115.50,121.87,122.30,122.46,123.3,139.72,140.10,140.39,140.90]),('outrolong',[141.2+j*.415 for j in range(31)]+[154.6])]
  for label,times in batches:
   sheet=Image.new('RGB',(1920,math.ceil(len(times)/4)*295));d=ImageDraw.Draw(sheet)
   for j,t in enumerate(times):
    im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/{label}-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+4,y+272),f'{t:.3f}s',fill='white')
   sheet.save(f'v16/{label}_storyboard.jpg')
  print('v13 preview saved',flush=True);return
 if '--flight-preview' in sys.argv:
  from flight_camera import FLIGHTS
  sheet=Image.new('RGB',(1920,len(FLIGHTS)*206));d=ImageDraw.Draw(sheet);audit=[]
  for j,event in enumerate(FLIGHTS):
   cross=event.cross_age if event.crosses else .24;offsets=[.06,min(.15,cross-.10),cross-.045,cross+.025,min(cross+.27,event.handoff-event.time-.04),min(cross+.70,event.handoff-event.time-.015)]
   for k,dt in enumerate(offsets):
    t=event.time+dt;im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/flight-{j:02}-{k}.jpg');sheet.paste(im.resize((320,180)),(k*320,j*206));d.text((k*320+4,j*206+182),f'{event.name} {dt:+.3f}s',fill='white');audit.append(last_camera_stats)
  sheet.save('v16/flight_storyboard.jpg');json.dump(audit,open('v16/flight_preview_audit.json','w'),indent=2);print('flight preview saved',flush=True);return
 if '--ferocity-preview' in sys.argv:
  offsets=[-.12,.03,.13,.25,.43,.85];sheet=Image.new('RGB',(1920,len(IMPACTS)*202));d=ImageDraw.Draw(sheet);audit=[]
  for j,event in enumerate(IMPACTS):
   for k,dt in enumerate(offsets):
    t=event.time+dt;im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/strike-{j:02}-{k}.jpg');sheet.paste(im.resize((320,180)),(k*320,j*202));d.text((k*320+4,j*202+182),f'{event.name} {dt:+.2f}s',fill='white');audit.append(last_camera_stats)
  sheet.save('v16/strike_storyboard.jpg');json.dump(audit,open('v16/strike_preview_audit.json','w'),indent=2)
  from aggression_score import ACTIONS
  sheet=Image.new('RGB',(1920,len(ACTIONS)*295));d=ImageDraw.Draw(sheet)
  for j,action in enumerate(ACTIONS):
   for k,t in enumerate([action.start+.05,(action.start+action.peak)*.5,action.peak,action.end-.1]):
    im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/action-{j:02}-{k}.jpg');sheet.paste(im.resize((480,270)),(k*480,j*295));d.text((k*480+5,j*295+272),f'{t:.3f}s / {action.force}',fill='white')
  sheet.save('v16/action_storyboard.jpg');print('aggressive preview saved',flush=True);return
 if '--angles-preview' in sys.argv:
  times=[]
  for si in range(31):
   a=0. if si==0 else CUT_TIMES[si-1];b=CUT_TIMES[si]
   candidates=[token for row in TOKEN_SCORES for token in row if a+.17<token['start'] and token['end']<b-.12 and token['end']-token['start']>.15]
   token=min(candidates,key=lambda token:abs((token['start']+token['end'])*.5-(a+b)*.5)) if candidates else None
   times.append((token['start']+token['end'])*.5 if token else (a+b)*.5)
  sheet=Image.new('RGB',(1920,8*302));d=ImageDraw.Draw(sheet);audit=[]
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/angle-{j:02}.jpg');x=j%4*480;y=j//4*302;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{j:02} {t:.3f}s / {sample_shot(t)["kind"]}',fill='white');audit.append(last_camera_stats)
  sheet.save('v16/angle_storyboard.jpg');json.dump(audit,open('v16/angle_preview_audit.json','w'),indent=2);print('angles preview saved',flush=True);return
 if '--words-preview' in sys.argv:
  times=[1.60,2.25,2.80,3.45,23.50,23.65,23.90,25.70,26.10,26.60,27.40,28.20,59.85,60.02,96.38,125.49,99.20,99.90,103.80,106.,133.20,137.20,139.35,156.50]
  sheet=Image.new('RGB',(1920,6*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/word-preview-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{t:.3f}s',fill='white')
  sheet.save('v16/word_storyboard.jpg');print('word preview saved',flush=True);return
 if '--impact-preview' in sys.argv:
  moments=[e.time+dt for e in IMPACTS for dt in [-.13,.04,.18,.45]]
  sheet=Image.new('RGB',(1920,len(IMPACTS)*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(moments):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/blast-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{IMPACTS[j//4].name} / {t:.3f}',fill='white')
  sheet.save('v16/impact_storyboard.jpg')
  moments=[141.32+j*.455 for j in range(30)]+[154.65,156.5];sheet=Image.new('RGB',(1920,8*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(moments):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/outro-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{sample_outro(t)["motif"]} / {t:.3f}',fill='white')
  sheet.save('v16/outro_storyboard.jpg');print('impact/outro preview saved',flush=True);return
 if '--edits' in sys.argv:
  times=[]
  for event in EDITS:times.extend([event.time-.45,event.time-.10,event.time+.10,event.time+.45])
  sheet=Image.new('RGB',(1920,len(EDITS)*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/edit-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{EDITS[j//4].label} / {t:.3f}',fill='white')
  sheet.save('v16/edit_storyboard.jpg');print('edit preview saved',flush=True);return
 if '--audit' in sys.argv:
  audit=[]
  for t in np.arange(1.5,141,.25):drawframe(float(t));audit.append(last_camera_stats)
  json.dump(audit,open('v16/framing_audit.json','w'),indent=2);print('audit saved',flush=True);return
 if '--preview' in sys.argv:
  times=[(r[0]+r[1])*.5 for r in lines]+[146,155];sheet=Image.new('RGB',(1920,9*295));d=ImageDraw.Draw(sheet)
  for j,t in enumerate(times):
   im=Image.frombytes('RGB',(W,H),drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v16/preview-{j:02}.jpg');x=j%4*480;y=j//4*295;sheet.paste(im.resize((480,270)),(x,y));d.text((x+5,y+272),f'{j:02} / {t:.2f}s',fill='white')
  sheet.save('v16/storyboard.jpg');print('preview saved',flush=True);return
 ff=imageio_ffmpeg.get_ffmpeg_exe();src=str(OPTIONS.audio);dest=str(OPTIONS.output)
 OPTIONS.output.parent.mkdir(parents=True,exist_ok=True)
 if OPTIONS.sample is not None:start=OPTIONS.sample;duration=min(DUR-start,OPTIONS.duration)
 else:start=0;duration=DUR
 cmd=[ff,'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-ss',str(start),'-i',src,'-map','0:v','-map','1:a','-vf','vflip','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-t',str(duration),'-movflags','+faststart',dest]
 held_count=0;held_hash=None
 with open('v16/render.log','w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for i in range(round(duration*FPS)):
   frame=drawframe(start+i/FPS);p.stdin.write(frame)
   if start+i/FPS>=154.6:
    digest=hashlib.sha256(frame).hexdigest()
    if held_hash is not None:assert digest==held_hash,'final frame moved'
    held_hash=digest;held_count+=1
   if i%300==0:print(f'{start+i/FPS:.0f} seconds rendered',flush=True)
  p.stdin.close();p.wait();assert p.returncode==0
 if held_count:json.dump({'freeze_at':154.6,'held_input_frames':held_count,'all_identical':True,'frame_sha256':held_hash,'title':"I'm Upping My P(doom)",'credit':'Made by Chiyang001'},open('v16/freeze_validation.json','w'),indent=2)
 print(dest,flush=True)
if __name__=='__main__':main()
