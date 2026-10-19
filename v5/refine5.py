from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8')
s=s.replace("trailvao=ctx.vertex_array(prog,[(trailbuf,'3f 3f 2f','pos','color','data')])", "trailvao=ctx.vertex_array(prog,[(trailbuf,'3f 3f 2f','pos','color','data')])\ncontactbuf=ctx.buffer(reserve=256*8*4);contactvao=ctx.vertex_array(prog,[(contactbuf,'3f 3f 2f','pos','color','data')])")
needle=' if t<141.2:draw_words(idx,t,vp,hit)'
s=s.replace(needle,""" if t<141.2:draw_words(idx,t,vp,hit)
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
""")
s=s.replace('uniform float paper;out vec4 frag;', 'uniform float paper;uniform float finalFade;out vec4 frag;')
s=s.replace('frag=vec4(pow(max(c,0),vec3(.91)),1);','frag=vec4(pow(max(c,0),vec3(.91))*finalFade,1);')
s=s.replace("post['paper']=paper;post['impact']", "post['finalFade']=float(min(1,max(0,(DUR-t)/.38)));post['paper']=paper;post['impact']")
p.write_text(s,encoding='utf-8')
