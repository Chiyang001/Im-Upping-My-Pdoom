from pathlib import Path
p=Path('code3d/render.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('import math,json,pathlib,subprocess,sys,random','import math,json,pathlib,subprocess,sys,random,re,difflib')
s=s.replace('uniform float pulse;void main(){vec3 n=', 'uniform float pulse;uniform float gain;void main(){vec3 n=')
s=s.replace('frag=vec4(col*fog,1);','frag=vec4(col*fog*gain,1);')
s=s.replace('uniform float pulse;out vec4 frag;', 'uniform float pulse;uniform float gain;out vec4 frag;')
s=s.replace('C*(.8+pulse*.25)*exp(-dist*.014)','C*(1.1+pulse*.35)*exp(-dist*.010)*gain')
s=s.replace('eye,pulse=0):','eye,pulse=0,gain=1):')
s=s.replace("if 'pulse' in p:p['pulse'].value=pulse", "if 'pulse' in p:p['pulse'].value=pulse\n   if 'gain' in p:p['gain'].value=gain")
s=s.replace('dep=.13','dep=.24')
start=s.index('layouts=[]');end=s.index("title=GPU",start)
s=s[:start]+'''layouts=[]
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
''' +s[end:]
s=s.replace('math.sin(yaw)*24,3.2+math.sin(local*.3)*.6,math.cos(yaw)*24','math.sin(yaw)*21,2.0+math.sin(local*.3)*.6,math.cos(yaw)*21')
s=s.replace('yaw=.13*math.sin(local*.38+idx*.8)','yaw=.22*math.sin(local*.38+idx*.8)')
s=s.replace('model=tr(*objpos)@rot(.12*local+idx*.5,1)@rot(.06*math.sin(t),2)','model=tr(*objpos)@rot(.12*local+idx*.5,1)@rot(.06*math.sin(t),2)@sc(1.65)')
s=s.replace('model=tr(*objpos)@rot(.10*math.sin(local*.4),1)','model=tr(*objpos)@rot(.18*math.sin(local*.4),1)@sc(1.55)')
s=s.replace('objects[kind].draw(model,vp,eye,pulse)','objects[kind].draw(model,vp,eye,pulse,1.15)\n  precision.draw(tr(0,1,-4)@rot(.16*math.sin(t*.4),1)@rot(local*.045,2),vp,eye,pulse)\n  labels[idx].draw(np.eye(4),vp,eye,pulse)')
s=s.replace('for j,(gpu,width,size) in enumerate(rows):','for j,(words,width,size,rail,radius) in enumerate(rows):')
s=s.replace('ang=-.10','ang=-.26').replace('ang=.16','ang=.28').replace('ang=-.13','ang=-.29').replace('ang=.15','ang=.24').replace('ang=-.17','ang=-.30')
s=s.replace('   gpu.draw(model,vp,eye,pulse)','''   rail.draw(model,vp,eye,pulse)
   for gpu,wx,wt in words:
    arcx=radius*math.sin(wx/radius);arcz=radius*(1-math.cos(wx/radius));since=t-wt
    lift=max(0,1-min(1,max(0,since)/.24))*.3 if since>=0 else .3
    wm=model@tr(arcx,lift,arcz)@rot(-wx/radius,1)
    gain=.24 if since<0 else 1.0+max(0,1-since/.35)*.35
    gpu.draw(wm,vp,eye,pulse,gain)''')
s=s.replace("elif mode==1:x=-1.5;y=2.4-j*2.1;z=2+j*.5", "elif mode==1:x=-1.5;y=2.1-j*2.1;z=2+j*.5")
s=s.replace('objects[kind].draw(tr(0,.3,-3)@rot(t*.18,1),vp,eye,pulse)','objects[kind].draw(tr(0,.3,-3)@rot(t*.18,1)@sc(1.8),vp,eye,pulse)\n  precision.draw(tr(0,.5,-3)@rot(t*.05,2),vp,eye,pulse)')
p.write_text(s,encoding='utf-8')
