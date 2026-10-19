from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8')
s=s.replace('uniform float clock;uniform float energy;uniform float action;uniform int motion;', 'uniform float clock;uniform float energy;uniform float action;uniform int motion;uniform float storytime;')
s=s.replace('if(motion==35){p.z=mod(p.z+clock+70.,100.)-70.;}', 'if(motion==35){p.z=mod(p.z+clock+70.,100.)-70.;}\n if(motion==38){p.z=mod(p.z+clock+70.,82.)-70.;}')
s=s.replace('vec4 world=model*vec4(p,1);gl_Position=', '''vec4 world=model*vec4(p,1);
 if(motion>=35 && motion<=38){
 float collapse=smoothstep(42.05,44.15,storytime)*(1.-smoothstep(48.,51.,storytime));float front=1.-smoothstep(-18.,6.,world.z);world.x*=1.-.58*collapse*front;world.y-=5.5*collapse*front;
 float turn=smoothstep(81.96,82.61,storytime)*(1.-smoothstep(86.7,89.3,storytime));float theta=-1.0*turn*(1.-smoothstep(-10.,5.,world.z));mat2 ry=mat2(cos(theta),-sin(theta),sin(theta),cos(theta));world.xz=ry*(world.xz-vec2(0.,-4.))+vec2(0.,-4.);
 float pinch=smoothstep(96.59,100.23,storytime)*(1.-smoothstep(102.3,104.5,storytime));world.x*=1.-.5*pinch*(1.-smoothstep(-12.,8.,world.z));
 float shred=smoothstep(116.59,118.5,storytime)*(1.-smoothstep(121.14,124.,storytime));world.x+=sign(world.x)*shred*2.5;world.y+=sin(seed*39.)*shred;
 float shear=smoothstep(121.14,123.0,storytime)*(1.-smoothstep(125.69,128.,storytime));world.x+=world.y*.45*shear;
 }
 gl_Position=''')
# Stable physical node fades independent of next/current/previous roles.
s=s.replace("if ni==idx:weight=.85;clock=t;action=ease((t-EVENT[ni])/.7)\n  elif ni<idx:weight=.36*(1-ease((t-a)/4.0));clock=t;action=1\n  else:weight=.14+.17*ease(u);clock=t;action=0", "aa,bb=lines[ni][:2];weight=.85*ease((t-aa+2.2)/2.2)*(1-ease((t-bb)/3.0));clock=t;action=ease((t-EVENT[ni])/.7)")
# Fix the exact connected road period, and make the signal a visible moving actor.
s=s.replace('((ahead-travel+70)%100)-70','((ahead-travel+70)%82)-70').replace('((z+travel+70)%100)-70','((z+travel+70)%82)-70')
s=s.replace('(.12+j*.025,axis=j','(.28+j*.035,axis=j')
s=s.replace("for q0 in np.linspace(0,.9,45)","for q0 in np.linspace(0,1.5 if t<103.41 else 2.3,45)")
s=s.replace("state['travel'];section=state['section']", "state['travel'];section=state['section'];prog['storytime']=float(t)")
# Clear but evolving atmospheric layers. City rise is a visible consequence of FOOM.
s=s.replace("worldM=np.diag([sx,sy,1.,1.])", """pressure=ease((t-22.2)/3.2)*(1-ease((t-25.685)/.35));burst=ease((t-25.685)/.35)*(1-ease((t-29)/2.))
 worldM=np.diag([sx*(1-pressure*.36+burst*.8),sy*(1-pressure*.22),1.,1.])
 cityLift=-8.5*(1-ease((t-25.685)/.6)) if t>22.2 else -4*(1-ease(t/12))""")
s=s.replace("worldM@tr(0,-.5,0)", "worldM@tr(0,-.5+cityLift,0)")
for key in ['road','signals','memory','machine_skeleton']:
 s=s.replace(f"STORY['{key}'].draw(np.eye(4),vp,travel,hit,0,35",f"STORY['{key}'].draw(worldM,vp,travel,hit,0,38")
s=s.replace("gain=.78*growth*wi", "gain=.68*growth*wi").replace("gain=.86*growth*wc", "gain=.80*growth*wc")
s=s.replace("signal.draw(tr(*pos)@sc(1+hit*.3)", "signal.draw(worldM@tr(*pos)@sc(1+hit*.35)")
s=s.replace("gain=2.4)", "gain=3.2)")
# The opening eye returns inside the final machine, binding the end to the beginning.
s=s.replace(" # Burst fragments become part", """ if t>133.4:
  awakening=ease((t-133.4)/1.2);environments[0].draw(tr(0,0,-10)@sc(2.0+awakening*.7),vp,t,hit,0,0,gain=.55*awakening)
 # Burst fragments become part""")
# Full fade at the end includes the world, so the last frame closes decisively.
s=s.replace("post['paper']=paper;post['impact']", "post['paper']=paper;post['impact']")
p.write_text(s,encoding='utf-8')
