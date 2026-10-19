import sys,math,numpy as np
sys.path.insert(0,'v4')
from engine import Mesh
C=np.array([.22,.9,.78]);W=np.array([.88,.94,1.]);A=np.array([1.,.24,.43]);D=np.array([.08,.26,.28])
def build(idx):
 m=Mesh();rng=np.random.default_rng(idx+432)
 if idx==0: # giant engraved iris, radial arc field
  for k in range(95):
   rr=1.1+k*.046
   m.line([[rr*math.cos(t),rr*math.sin(t)*.75,-3+.3*math.sin(t*9+k*.15)] for t in np.linspace(0,math.tau,260)],C*.55 if k%5 else W)
  for k in range(220):
   a=k*math.tau/220;m.line([[r*math.cos(a+.022*math.sin(r*8+a*5)),r*math.sin(a+.022*math.sin(r*8+a*5))*.75,-3] for r in np.linspace(1.5,5.5,55)],C*.6)
  for k in range(45):
   yy=3.9+k*.08
   m.line([[x,yy*math.sin((x+12)/24*math.pi),-4-k*.12] for x in np.linspace(-12,12,180)],D*1.4)
   m.line([[x,-yy*math.sin((x+12)/24*math.pi),-4-k*.12] for x in np.linspace(-12,12,180)],D*1.4)
  for k in range(30):m.circle(1+k*.008,(0,0,-2.8),2,A,180)
 elif idx==1: # typography powered by printed-circuit paths
  for side in [-1,1]:
   for j in range(130):
    y=(j-65)*.12;z=-4+(j%7)*.06;x=side*(4.5+(j%9)*.2)
    m.line([[side*18,y*.8,z],[side*11,y*.8,z],[side*9,y,z],[x,y,z],[x,y*.48,z],[side*2.1,y*.48,z]],C*.65 if j%4 else W)
    m.circle(.06,(side*11,y*.8,z),2,W,n=16)
  for j in range(14):
   for k in range(9):
    x=(j-7)*.38;y=(k-4)*.38;m.box((x,y,-6),(.22,.22,.5),D*2)
  for j in range(40):m.box((0,0,-7-j*.13),(6+j*.08,4+j*.04,.01),D)
 elif idx==2: # loss cliff / contour cascade
  for z in np.linspace(-12,10,110):
   m.line([[x,3.1*math.tanh((x-1)*1.7)+.4*math.sin(z*.6+x*.4),z] for x in np.linspace(-16,16,220)],C*.55 if int(z*10)%5 else W)
  for x in np.linspace(-16,16,90):m.line([[x,3.1*math.tanh((x-1)*1.7)+.4*math.sin(z*.6+x*.4),z] for z in np.linspace(-12,10,140)],D*1.5)
  for j in range(12):m.line([[x,3.15*math.tanh((x-1)*1.7)+.4*math.sin(j*.3+x*.4),j*.3] for x in np.linspace(-16,16,220)],A*.8)
 elif idx==3: # hierarchy, suspension rig, physical strings
  for side in [-1,1]:
   for j in range(50):
    x=side*(6+j*.14);m.line([[x,-8,-2],[x,7,-2],[side*2,7,-2],[side*2,4,-2]],D*2 if j%4 else C)
  for j in range(100):
   x=(j-50)*.23;m.line([[x,8,-5],[x,3.7,-5],[x*.55,2.8,-2]],C*.45)
  for j in range(24):m.box((0,-4,-6-j*.13),(23-j*.07,1+j*.05,.01),W*.45)
  for j in range(40):m.line([[x,-4.5+.2*math.sin(x*1.8+j*.2),-1+j*.03] for x in np.linspace(-12,12,130)],A*.65)
 elif idx==4: # closing mechanical jaw, glyph chamber
  for side in [-1,1]:
   for k in range(64):
    r=6.0+k*.045
    m.line([[r*math.cos(t),side*(2.2+abs(r*math.sin(t))*.62),-3+k*.02] for t in np.linspace(0,math.pi,130)],C*.6)
   for j in range(27):
    x=(j-13)*.8;y=side*(3.2+.4*abs(x)/10)
    for k in range(5):m.line([[x-.3+k*.04,y,-3],[x,side*1.8,-2.5],[x+.3-k*.04,y,-3]],W*.8)
  for j in range(70):
   a=j*math.tau/70;m.line([[r*math.cos(a),r*math.sin(a),-7] for r in np.linspace(7,14,45)],D*1.8)
 elif idx==5: # probability pressure vessel / explosive radial lines
  for k in range(70):
   r=2.4+k*.085;m.circle(r,(0,0,-6-k*.02),2,C*.5 if k%5 else W,n=210)
  for j in range(280):
   a=j*math.tau/280;rng0=rng.uniform(5,8);m.line([[rng0*math.cos(a),rng0*math.sin(a),-4],[(rng0+7)*math.cos(a),(rng0+7)*math.sin(a),-9]],A*.8 if j%9==0 else D*2)
  for k in range(15):
   r=3+k*.35;m.line([[r*math.cos(t),r*math.sin(t),-.5] for t in np.linspace(.4,2.2,80)],A*.7)
 elif idx==6: # Chinese room maze architecture all edges
  for j in range(36):
   z=7-j*.75;m.box((0,0,z),(19,12,.025),C*.4 if j%4 else W)
   for k in range(7):
    x=(k-3)*3.1;m.line([[x,-6,z],[x,-6,z-.7]],D*2)
   if j%3==0:
    xx=(-1)**j*6.8;m.box((xx,0,z),(3.6,9,.1),C)
  for j in range(50):
   x=(j-25)*.4;m.line([[x,-6,8],[x,-6,-28]],D*2);m.line([[x,6,8],[x,6,-28]],D*2)
  for j in range(90):
   x,y,z=rng.uniform([-10,-6,-27],[10,6,-2]);m.box((x,y,z),(.25,.25,.02),A*.8)
 elif idx==7: # shoggoth, fractal tangled bodies and hollow mask
  for k in range(270):
   a=k*math.tau/270
   m.line([[(3.6+1.9*t+.4*math.sin(t*14+a*5))*math.cos(a+t*3),(3.6+1.9*t)*math.sin(a+t*3)*.65, -4+2*math.sin(a*3+t*9)*t] for t in np.linspace(0,1,160)],C*.55 if k%8 else W)
  for k in range(45):m.circle(1.6+k*.02,(0,0,-2),2,A*.7,n=180)
  for j in range(80):
   x=(j-40)*.35;m.line([[x,-5+.3*math.sin(x+j),-8],[x+1.4,-4,-8],[x+1.4,-2,-8]],D*2)
 elif idx==8: # twin deadly ocular structures
  for side in [-1,1]:
   for k in range(80):
    rr=.6+k*.036;m.line([[side*5+rr*math.cos(t),rr*math.sin(t),-3+.12*math.cos(t*13+k)] for t in np.linspace(0,math.tau,180)],C*.65 if k%6 else W)
   for k in range(100):
    a=k*math.tau/100;m.line([[side*5+r*math.cos(a),r*math.sin(a),-3] for r in np.linspace(3.6,5.2,40)],A*.5)
  for j in range(100):m.line([[x,2*math.sin(x*.2+j*.01),-8-j*.04] for x in np.linspace(-17,17,160)],D*1.7)
 elif idx==9: # stable run oscilloscope bank
  for j in range(70):
   z=-12+j*.3;m.line([[x,math.sin(x*.7)*.12, z] for x in np.linspace(-16,16,160)],C*.7 if j%7 else W)
  for j in range(40):m.box((0,0,-10-j*.15),(30,8,.01),D*2)
  for j in range(18):
   x=-14+j*1.65;m.line([[x,-3,-5],[x,3,-5]],D*2)
   for k in range(15):m.line([[x-.13,-3+k*.4,-5],[x+.13,-3+k*.4,-5]],W*.7)
 elif idx==10: # warped spacetime funnel
  for k in range(100):
   r=.25+k*.13;pts=[]
   for a in np.linspace(0,math.tau,200):pts.append([r*math.cos(a),r*math.sin(a),-2-8*math.exp(-r*.48)])
   m.line(pts,C*.6 if k%7 else W)
  for j in range(180):
   a=j*math.tau/180;m.line([[r*math.cos(a),r*math.sin(a),-2-8*math.exp(-r*.48)] for r in np.linspace(.3,14,140)],D*2 if j%9 else A*.6)
 elif idx==11: # racing tunnel full field, asymmetric lane fins
  for j in range(80):
   z=10-j*.65;r=5.5
   pts=[[r*math.cos(a),r*.65*math.sin(a),z] for a in np.linspace(0,math.tau,13)];m.line(pts,C*.45 if j%5 else W)
  for j in range(96):
   a=j*math.tau/96;r=5.5;m.line([[r*math.cos(a),r*.65*math.sin(a),-42],[r*math.cos(a),r*.65*math.sin(a),10]],D*2)
  for j in range(220):
   a=rng.uniform(0,math.tau);r=rng.uniform(6,12);z=rng.uniform(-35,10);m.line([[r*math.cos(a),r*.6*math.sin(a),z],[r*math.cos(a),r*.6*math.sin(a),z+rng.uniform(1,5)]],A*.6 if j%8==0 else C*.5)
 elif idx==12: # atomic lattice becoming explosion
  for j in range(75):
   x,y,z=rng.uniform([-12,-6,-10],[12,6,2]);r=rng.uniform(.15,.5)
   m.sphere(r,(x,y,z),C*.7,rings=5)
   for k in range(2):
    q=np.array([x,y,z])+rng.uniform(-2,2,3);m.line([[x,y,z],q],D*2)
  for k in range(34):
   a=k*math.pi/34;m.line([[5*math.cos(t)*math.cos(a),3*math.sin(t),-4+5*math.cos(t)*math.sin(a)] for t in np.linspace(0,math.tau,180)],W*.65 if k%4 else A*.7)
 elif idx==13: # prison/escape vertically condensed gates
  for side in [-1,1]:
   for j in range(35):
    x=-16+j*.94;m.box((x,0,side*5-4),(.12,16,.12),C*.7)
  for j in range(24):m.box((0,0,7-j*.9),(30,15,.01),D*2)
  for j in range(130):
   z=rng.uniform(-14,6);y=rng.uniform(-7,7);m.line([[-15,y,z],[15,y,z]],D*.6)
 elif idx==14: # serpentine basilisk as densely braided double helix
  for j in range(120):
   a=j*math.tau/120;pts=[]
   for t in np.linspace(-math.pi*2,math.pi*2,500):
    rr=4.0+.4*math.cos(t*.8);pts.append([(rr+.7*math.cos(a))*math.cos(t),t*.65+.7*math.sin(a),-5+(rr+.7*math.cos(a))*math.sin(t)])
   m.line(pts,C*.6 if j%9 else W)
  for j in range(70):
   r=5+j*.06;m.line([[r*math.cos(t),r*math.sin(t),-10] for t in np.linspace(0,math.tau,200)],D*2)
 elif idx==15: # bullish trajectory rising into a wireframe moon
  for k in range(80):
   rr=2.1+k*.025;m.circle(rr,(6,2,-3),2,C*.8,n=200)
  for k in range(100):
   x=-15+k*.27;y=-4+((x+15)/22)**2*8
   m.line([[x,-7,-5],[x,y,-5]],D*2 if k%4 else W)
  for j in range(28):m.line([[x,-4+((x+15)/22)**2*8+j*.025,-4+j*.025] for x in np.linspace(-15,7,220)],A*.85)
  for j in range(50):m.line([[x,-7,-14+j*.4] for x in np.linspace(-17,17,50)],D)
 elif idx==16: # huge compute canyon densely ruled modules
  for side in [-1,1]:
   for j in range(15):
    z=-j*1.2
    for y in range(-5,6):
     x=side*(7+(j%3)*.1);m.box((x,y*.9,z),(3,.7,.85),C*.7)
     for k in range(6):m.line([[x-1.4,y*.9-.25+k*.08,z+.43],[x+1.4,y*.9-.25+k*.08,z+.43]],D*2)
  for j in range(90):
   x=-5+j*.115;m.line([[x,-5,8],[x,-5,-25]],D*2)
 return m
