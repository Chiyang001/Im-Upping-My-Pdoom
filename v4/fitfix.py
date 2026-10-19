from pathlib import Path
p=Path('v4/render.py');s=p.read_text(encoding='utf-8')
needle='clip=np.c_[pp,np.ones(len(pp))]@vp.T;ndc=clip[:,:3]/clip[:,3:4]'
s=s.replace(needle,"""# Protect the sung structure, while already-read foreground strokes may pass outside the lens.
 for attempt in range(4):
  ck=np.c_[pp,np.ones(len(pp))]@vp.T;nn=ck[:,:3]/ck[:,3:4];edge=max(abs(nn[:,:2]).max(),.01)
  if edge<=.945:break
  eye=target+(eye-target)*(edge/.93);view=rot(rr,2)@look(eye,target);vp=perspective(math.radians(fov+hit*.35),W/H,far=180)@view
 clip=np.c_[pp,np.ones(len(pp))]@vp.T;ndc=clip[:,:3]/clip[:,3:4]""")
p.write_text(s,encoding='utf-8')
