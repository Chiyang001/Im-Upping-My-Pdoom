from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8')
s=s.replace('uniform float storytime;out vec3 C;', 'uniform float storytime;uniform vec3 chapterTint;uniform float text_role;out vec3 C;')
s=s.replace('C=color;phase=data.x;', 'C=mix(color,vec3(max(color.r,max(color.g,color.b)))*chapterTint,(1.-min(1.,text_role))*.65);phase=data.x;')
s=s.replace("state['travel'];section=state['section'];prog['storytime']=float(t)","state['travel'];section=state['section'];prog['storytime']=float(t);prog['chapterTint'].value=tuple(chapter_tint(t))")
pos=s.index('def drawframe(t):')
s=s[:pos]+'''TINT=np.array([[.45,.9,1.],[.35,1.,.78],[.45,.64,1.],[.6,.8,1.],[.65,.85,1.],[.8,.9,1.],[1.,.48,.67],[.85,.6,1.],[.8,.78,1.],[.9,.7,.9],[.9,.75,.9]])
def chapter_tint(t):
 i=max(0,min(len(CHAPTER_T)-2,np.searchsorted(CHAPTER_T,t,'right')-1));u=ease((t-CHAPTER_T[i])/max(.01,CHAPTER_T[i+1]-CHAPTER_T[i]));return TINT[i]*(1-u)+TINT[i+1]*u
''' +s[pos:]
s=s.replace("growth=.55+.45*ease(t/18)","growth=.1+.9*ease(t/9)")
s=s.replace("WORLD['city'].draw(worldM@tr(0,-.5+cityLift,0),vp,travel,hit,0,36,gain=.80*growth*wc)","WORLD['city'].draw(worldM@tr(0,-.5+cityLift,0),vp,travel,hit,0,36,gain=.80*growth*wc*(.18 if t<22.2 else .25+.75*ease((t-25.685)/.45)))")
# Offline sentence-specific size corrections keep the camera autonomous and continuous.
s=s.replace('return node_matrix(i,t)@GLYPH_SCALE@tr(x,y,z)', 'factor=.90 if i in [5,11,27,29] else .95 if i in [8,23] else 1.\n return node_matrix(i,t)@GLYPH_SCALE@sc(factor)@tr(x,y,z)')
p.write_text(s,encoding='utf-8')
