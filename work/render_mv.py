import os,json,math,random,re,difflib,subprocess,pathlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter
import imageio_ffmpeg
W,H=1280,720;FPS=30;DURATION=156.667
IV=(244,237,217);RED=(244,58,38);BLUE=(24,54,202)
FONT='C:/Windows/Fonts/arialbd.ttf';SERIF='C:/Windows/Fonts/timesi.ttf';MONO='C:/Windows/Fonts/consola.ttf'
F={}
def ft(n,font=FONT):
 k=(int(n),font)
 if k not in F:F[k]=ImageFont.truetype(font,int(n))
 return F[k]
def txt(d,xy,s,n=30,fill=IV,font=FONT,anchor=None):d.text(xy,s,font=ft(n,font),fill=fill,anchor=anchor,stroke_width=0)
def width(s,n,font=FONT):return ft(n,font).getlength(s)
def fit(s,maxw,n=95,font=FONT):return min(n,max(16,int(n*maxw/max(1,width(s,n,font)))))
beats=np.array(json.load(open('work/beats.json')))
lines=json.load(open('work/lyrics.json'));trans=json.load(open('work/transcript.json'))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
for r in lines:
 words=r[3].replace('|',' ').split(); ws=[w for s in trans for w in s['words'] if r[0]-.1<=w['start']<r[1]]
 match=difflib.SequenceMatcher(None,[norm(x) for x in words],[norm(w['word']) for w in ws],autojunk=False)
 timing={}
 for block in match.get_matching_blocks():
  for k in range(block.size):timing[block.a+k]=ws[block.b+k]['start']
 for j in range(len(words)):
  if j not in timing:
   lo=max([k for k in timing if k<j],default=-1);hi=min([k for k in timing if k>j],default=len(words));t0=timing.get(lo,r[0]);t1=timing.get(hi,r[1]-.25);timing[j]=t0+(t1-t0)*(j-lo)/(hi-lo)
 r.append([timing[j] for j in range(len(words))])
imgs=[Image.open(f'assets/scene-{i:02}.png').convert('RGB').resize((1536,864),Image.Resampling.LANCZOS) for i in range(13)]
# dark vignette preserves the artwork while giving type a clean field
Y,X=np.mgrid[0:H,0:W]; vignette=np.uint8(np.clip(22+75*((X-W/2)**2/(W/2)**2+(Y-H/2)**2/(H/2)**2),0,160))
shade=Image.new('RGBA',(W,H),(3,7,24,0));shade.putalpha(Image.fromarray(vignette))
random.seed(24);particles=[(random.random()*W,random.random()*H,random.random()*2+1) for _ in range(70)]
def phrase_layer(s,times,t,maxw,size,color=IV,font=FONT):
 n=fit(s,maxw,size,font); im=Image.new('RGBA',(maxw+20,n+30));d=ImageDraw.Draw(im);x=0
 for k,w in enumerate(s.split()):
  active=t>=times[k] if k<len(times) else True
  # future words remain as delicate outlines; sung words take physical weight
  if active:txt(d,(x,2),w,n,color,font)
  else:d.text((x,2),w,font=ft(n,font),fill=(244,237,217,38))
  x+=width(w+' ',n,font)
 return im

def frame(t):
 idx=next((i for i,r in enumerate(lines) if r[0]<=t<r[1]),-1)
 outro=t>=141.2
 if idx>=0:r=lines[idx];a,b,asset,lyric,key,times=r;p=(t-a)/(b-a)
 else:a=0;b=1;asset=8 if t<1.42 or outro else 2;lyric='';key='';p=t%1
 past=beats[beats<=t];beat=max(0,1-(t-past[-1])/.15) if len(past) else 0
 # continuous dolly, with a new axis on each cut
 asset={0:9,5:10,18:11,20:10,27:11,28:10,31:11}.get(idx,asset)
 if outro:asset=12
 im0=imgs[asset];zoom=1.04+.09*p+.007*beat
 cw=int(W/zoom);ch=int(H/zoom);cx=768+int(45*math.sin(t*.23));cy=432+int(22*math.cos(t*.3));im=im0.crop((cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)).resize((W,H),Image.Resampling.BICUBIC).convert('RGBA');im.alpha_composite(shade)
 d=ImageDraw.Draw(im)
 # architectural marks, scene number, physical framing
 d.line((36,40,110,40),fill=RED,width=3);d.line((36,40,36,95),fill=IV,width=1)
 txt(d,(50,53),'THE LAST MACHINE THEATRE',14,font=MONO)
 txt(d,(W-48,50),f'ACT {1 if t<38 else 2 if t<74 else 3 if t<109 else 4:02} / {max(0,idx)+1:02}',14,font=MONO,anchor='ra')
 d.line((36,H-34,W-36,H-34),fill=(130,134,152),width=1);d.line((36,H-34,36+(W-72)*t/DURATION,H-34),fill=RED,width=3)
 # suspended dust and animated red threads
 for x,y,z in particles[:35]:
  yy=(y-t*7*z)%H;xx=x+8*math.sin(t*.5+z);d.ellipse((xx,yy,xx+z,yy+z),fill=(223,225,238,100))
 if idx<0:
  if t<1.42:
   txt(d,(W/2,290),'P(doom)',130,anchor='mm',font=SERIF);txt(d,(W/2,386),'A MACHINE THEATRE IN FOUR ACTS',21,anchor='mm',font=MONO)
  elif outro:
   q=(t-141.2)/15.467
   # kinetic closing probability rises while paperclip orbital trajectories invade
   for j in range(38):
    x=(j*173+t*90)%1400-60;y=150+(j*67)%420+25*math.sin(t+j)
    d.rounded_rectangle((x,y,x+75,y+24),radius=12,outline=IV,width=2)
   d.rectangle((290,230,990,490),fill=(7,15,47,225),outline=RED,width=2)
   txt(d,(640,275),'FINAL PROBABILITY',18,anchor='mm',font=MONO)
   txt(d,(640,357),'P(doom) = '+('∞' if q>.68 else f'{min(.999, .5+q*.75):.3f}'),72,anchor='mm',font=SERIF)
   txt(d,(640,441),'THE SHOW CONTINUES.',20,anchor='mm',font=MONO)
   if q>.78:
    black=Image.new('RGBA',(W,H),(3,7,18,int(255*min(1,(q-.78)/.15))));im.alpha_composite(black);dd=ImageDraw.Draw(im)
    txt(dd,(640,300),'THE LAST MACHINE THEATRE',35,anchor='mm');txt(dd,(640,360),'VISUAL DIRECTION / CHIYANG001',17,anchor='mm',font=MONO);txt(dd,(640,405),'MUSIC / ORIGINAL SOURCE AUDIO',14,anchor='mm',font=MONO)
  base=Image.new('RGBA',(W,H),(3,7,18,255));base.alpha_composite(im);return base.convert('RGB')
 chorus=key=='P(doom)';mode=idx%5
 # restrained documentary fragments add context as set dressing
 txt(d,(52,622),f'EXPERIMENT {idx+1:03}   /   T + {t:06.2f}',13,font=MONO)
 if chorus:
  d.rectangle((0,100,1280,267),fill=(12,33,120,215))
  txt(d,(52,110),'P(doom)',142+int(4*beat),font=SERIF)
  txt(d,(1220,160),f'{[.17,.48,.81,.99][[5,14,23,30].index(idx)] if idx in [5,14,23,30] else .99:.2f}',80,RED,MONO,anchor='ra')
  # probability diagram becomes a moving part of the set
  for j in range(18):
   x=610+j*25;ht=20+(j/18)**2*100+beat*12
   d.rectangle((x,248-ht,x+13,248),fill=IV if j<18*p else RED)
 elif mode in (0,3):
  # giant architectural keyword runs behind the lyric placard
  n=fit(key,1150,155);txt(d,(55,115+5*math.sin(t)),key,n,IV if mode==0 else RED,font=SERIF if idx in (8,26,33) else FONT)
 elif mode==1:
  # floating stamp, changes scale in rhythm
  st=Image.new('RGBA',(580,155));sd=ImageDraw.Draw(st);sd.rectangle((3,3,575,145),outline=RED,width=5);n=fit(key,530,100);txt(sd,(290,72),key,n,RED,anchor='mm');st=st.rotate(-9+2*math.sin(t),resample=Image.Resampling.BICUBIC,expand=True);im.alpha_composite(st,(60,130))
 elif mode==2:
  # orbital lettering and scientific framing
  for j in range(3):
   rr=100+j*24+beat*4;d.ellipse((950-rr,230-rr*.52,950+rr,230+rr*.52),outline=IV if j!=1 else RED,width=2)
  txt(d,(50,155),key,fit(key,820,130),RED)
 # Lyrics are separate scenic treatments: hanging banners, poster, monumental type, skewed signage, and floor inscriptions.
 parts=lyric.split('|');cursor=0
 for j,s in enumerate(parts):
  count=len(s.split());tt=times[cursor:cursor+count];cursor+=count
  maxw=1080;fs=80 if len(parts)==1 else 67
  if mode==0 and not chorus:maxw=760;fs=91
  if mode==2 and not chorus:maxw=1130;fs=92
  if mode==4 and not chorus:maxw=1000;fs=86
  layer=phrase_layer(s,tt,t,maxw,fs,IV,SERIF if idx in (8,26,33) else FONT)
  enter=min(1,max(0,(t-a)*3));ease=1-(1-enter)**3
  x=65+int((1-ease)*70);y=390+j*100
  if chorus:
   x=65+j*85;y=365+j*100
  elif mode==0:
   x=100+j*150;y=335+j*115
  elif mode==1:
   x=60+j*60;y=410+j*95
  elif mode==2:
   x=65;y=365+j*110
  elif mode==3:
   x=70+j*60;y=300+j*200
  else:
   x=90+j*60;y=370+j*120
  if mode in (1,3) or chorus:
   plate=Image.new('RGBA',(min(layer.width+30,1160),layer.height+16),(7,15,43,220));pd=ImageDraw.Draw(plate);pd.rectangle((0,0,5,plate.height),fill=RED);plate.alpha_composite(layer,(18,3))
  else:
   # cast shadow makes the words read as dimensional objects in the stage light
   alpha=layer.getchannel('A');shadow=Image.new('RGBA',layer.size,(0,0,0,0));shadow.putalpha(alpha);shadow=shadow.filter(ImageFilter.GaussianBlur(6));im.alpha_composite(shadow,(x+4,y+7));plate=layer
  if mode==3:plate=plate.rotate(4 if j==0 else -2,resample=Image.Resampling.BICUBIC,expand=True)
  elif mode==4:plate=plate.rotate(-4,resample=Image.Resampling.BICUBIC,expand=True)
  im.alpha_composite(plate,(x,y))
 # concept-specific motion drawn into the same world
 d=ImageDraw.Draw(im)
 if key in ['TRAINING LOSS','STABLE','ACCELERATING']:
  pts=[(60+x*4,310+int(45*math.exp(-x/35)*math.sin(x*.3+t*3)+x*.15)) for x in range(220)]
  d.line(pts,fill=RED,width=3)
 if key in ['ATOMS','UPGRADE','OBSOLETE']:
  for j in range(20):
   ang=j*2.4+t;rad=40+130*p;xx=990+rad*math.cos(ang);yy=270+rad*.5*math.sin(ang);d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=IV)
 if key=='LEFT TURN':d.line((80,315,340,315,340,250,520,250),fill=RED,width=9)
 if key=='1e30':
  for j in range(30):d.rectangle((60+j*38,320-int(20+30*math.sin(j+t*10)**2),72+j*38,320),fill=IV)
 # chapter cuts are crisp, with a short shutter on the first two frames
 if t-a<.065:
  overlay=Image.new('RGBA',(W,H),(*RED,int(105*(1-(t-a)/.065))));im.alpha_composite(overlay)
 base=Image.new('RGBA',(W,H),(3,7,18,255));base.alpha_composite(im);return base.convert('RGB')

def render():
 ff=imageio_ffmpeg.get_ffmpeg_exe();src=str(next(pathlib.Path('.').glob('*.mp4')))
 cmd=[ff,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',src,'-map','0:v','-map','1:a','-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-t',str(DURATION),'-movflags','+faststart','output/Pdoom_Machine_Theatre_1080p.mp4']
 with open('work/render.log','w') as log:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  for i in range(round(DURATION*FPS)):
   proc.stdin.write(frame(i/FPS).tobytes())
   if i%300==0:print(f'{i/FPS:.0f}s / {DURATION:.0f}s',flush=True)
  proc.stdin.close();proc.wait()
  if proc.returncode:raise RuntimeError('ffmpeg failed')
if __name__=='__main__':
 import sys
 if '--preview' in sys.argv:
  times=[3,11,19,24,28,34,45,50,60,67,70,76,82,87,96,103,112,117,121,126,133,139,146,154]
  sheet=Image.new('RGB',(4*480,6*270))
  for j,t in enumerate(times):
   im=frame(t);im.save(f'work/preview-{t}.jpg');sheet.paste(im.resize((480,270)),((j%4)*480,(j//4)*270))
  sheet.save('work/new-storyboard.jpg')
 else:render()
