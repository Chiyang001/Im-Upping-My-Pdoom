from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8')
# Improve the visibility of meaningful forms: ambient line fields do not punch black holes through lyric strokes.
s=s.replace("for j,(words,scaffold,sr) in enumerate(rows[i]):", "if ghost:\n  ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)\n for j,(words,scaffold,sr) in enumerate(rows[i]):")
s=s.replace(" ctx.line_width=1.2\n\ndef signal_position", " ctx.line_width=1.2\n if ghost:ms.depth_mask=True;ctx.disable(gl.BLEND)\n\ndef signal_position")
s=s.replace("if ni!=idx:draw_words(ni,t,vp,hit,gain=weight*.6,ghost=True)","if ni<idx:draw_words(ni,t,vp,hit,gain=weight*.22,ghost=True)")
# Continuous transformations let the shared infrastructure become city, factory, splinter field and loom.
pos=s.index('def drawframe(t):')
s=s[:pos]+'''CHAPTER_T=np.array([0.,22.2,38.12,58.4,73.96,94.86,109.4,124.04,131.46,141.2,156.667])
# infrastructure / city / debris / ribbons / skeleton / memory / xscale / yscale
CHAPTER_W=np.array([[.75,.30,.20,.65,.55,.30,1.,1.], [.42,1.20,.42,.50,.65,.20,1.15,.95], [.75,.70,.45,.90,.60,.55,1.15,.75], [.35,1.35,.60,.45,.55,.35,.95,1.35], [.45,.35,.55,1.1,.85,.85,1.4,.8], [.40,.85,1.20,.40,.90,.50,1.15,1.05], [.35,.9,1.35,.65,.70,.45,1.25,1.0], [.25,.30,.50,1.7,.50,.65,1.15,.95], [.55,.25,.35,.55,1.0,1.3,.95,1.15], [.7,.8,.9,1.1,1.1,1.0,1.2,1.1], [.8,.8,1.,1.4,1.2,1.3,1.3,1.2]])
def chapter_weights(t):
 i=max(0,min(len(CHAPTER_T)-2,np.searchsorted(CHAPTER_T,t,'right')-1));u=ease((t-CHAPTER_T[i])/max(.01,CHAPTER_T[i+1]-CHAPTER_T[i]));return CHAPTER_W[i]*(1-u)+CHAPTER_W[i+1]*u

''' +s[pos:]
start=s.index(" # Persistent layers remain");end=s.index(" # Previous forms physically",start)
s=s[:start]+''' # Persistent world layers move continuously but change their physical role by chapter.
 weights=chapter_weights(t);wi,wc,wd,wr,ws,wm,sx,sy=weights
 worldM=np.diag([sx,sy,1.,1.])
 # Background engraving is additive and does not write depth, preserving clear foreground contours.
 ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)
 WORLD['infrastructure'].draw(worldM,vp,travel*.78,hit,0,36,gain=.78*growth*wi)
 WORLD['city'].draw(worldM@tr(0,-.5,0),vp,travel,hit,0,36,gain=.86*growth*wc)
 WORLD['debris'].draw(np.eye(4),vp,travel*1.3,hit,0,37,gain=.65*growth*wd)
 WORLD['data_ribbons'].draw(worldM,vp,travel*.86,hit,0,35,gain=.90*growth*wr)
 STORY['road'].draw(np.eye(4),vp,travel,hit,0,35,gain=1.0)
 STORY['signals'].draw(np.eye(4),vp,travel,hit,0,35,gain=1.0+hit*.6)
 STORY['memory'].draw(np.eye(4),vp,travel,hit,0,35,gain=.65*growth*wm)
 ms.depth_mask=True;ctx.disable(gl.BLEND)
 # A small number of real near-field beams retain depth occlusion and sweep past the lens.
 STORY['machine_skeleton'].draw(np.eye(4),vp,travel,hit,0,35,gain=.75*growth*ws)
''' +s[end:]
# Prevent residual verse text from sitting on top of the ending story.
s=s.replace(' draw_words(idx,t,vp,hit)\n # Burst', ' if t<141.2:draw_words(idx,t,vp,hit)\n # Burst')
s=s.replace("if ni<idx:draw_words", "if ni<idx and t<141.2:draw_words")
p.write_text(s,encoding='utf-8')
