from pathlib import Path
p=Path('code3d/render.py');s=p.read_text(encoding='utf-8')
s=s.replace('objects=[GPU(objectmesh(k)) for k in range(11)]','''objects=[GPU(objectmesh(k)) for k in range(11)]
marker=Mesh();marker.sphere(.11,color=C,rings=5);marker=GPU(marker)
burst=Mesh();rng=np.random.default_rng(16)
for j in range(140):
 v=unit(rng.normal(size=3));burst.line([v*1.2,v*(1.8+rng.random()*2.5)],C if j%4 else WHITE)
burst=GPU(burst)''')
s=s.replace('objects[kind].draw(model,vp,eye,pulse,1.15)', '''if kind==7:model=model@sc(.75+u*.65)
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
''')
s=s.replace("gain=.24 if since<0 else", "gain=.40 if since<0 else")
# Native 1080p output; all visible pixels originate in the geometry render.
p.write_text(s,encoding='utf-8')
