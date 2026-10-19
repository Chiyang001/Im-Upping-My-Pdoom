from pathlib import Path
p=Path('v4/render.py');s=p.read_text(encoding='utf-8')
s=s.replace("a=np.array(m.l,'f4');self.count=len(a)", "a=np.array(m.l,'f4');self.count=len(a)\n  self.bmin=a[:,:3].min(axis=0) if len(a) else np.zeros(3);self.bmax=a[:,:3].max(axis=0) if len(a) else np.ones(3)")
# Reading positions are built from the actual three-dimensional letter geometry, so the camera can approach the structure itself.
pos=s.index("# Per-scene semantic timing markers")
s=s[:pos]+'''SHOT=[]
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
''' +s[pos:]
needle="rr=roll*math.sin(u*math.pi)+sharp*.015*(-1)**idx\n view="
s=s.replace(needle,"""# Match the active word-bearing structure to a readable hero shot. Other words remain real scenery around it.
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
 view=""")
s=s.replace('t-25.40','t-25.685').replace('t>25.4','t>25.685').replace('t-25.4','t-25.685').replace('25.4 if idx==5','25.685 if idx==5')
s=s.replace("if idx==4:\n  close=", "if idx==4:\n  close=")
s=s.replace("envmodel=envmodel@np.diag([1,1-close,1,1])", "envmodel=envmodel@np.diag([1,1-close*1.8,1,1])")
# Geometry fractures are independent of readability; front letter contours keep their role until the final accented hit.
s=s.replace("if(motion==5){p.xy*=1.+action*.65;p.z-=action*length(p.xy)*.3;}", "if(motion==5){p.xy*=1.+action*.65;p.z-=action*length(p.xy)*.3;p.xy+=vec2(sin(seed*91.),cos(seed*53.))*energy*.7;}")
s=s.replace("if(motion==29){p.x+=sin(floor(p.y)*.8+clock*4.)*action*2.;p.z+=energy*.4;}", "if(motion==29){p.x+=sin(floor(p.y)*.8+clock*4.)*action*4.5;p.z+=energy*.7;}")
p.write_text(s,encoding='utf-8')
