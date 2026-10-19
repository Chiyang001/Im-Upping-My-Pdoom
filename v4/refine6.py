from pathlib import Path
p=Path('v4/render.py');s=p.read_text(encoding='utf-8')
s=s.replace("(\"shoggoth's\",25,0,.4,-3,.2,0,8)","(\"shoggoth's\",25,0,.4,-3,.2,0,22)")
s=s.replace("('\\\"That was safe enough\\\"',25,0,2,-2,0,0,10)","('\\\"That was safe enough\\\"',25,0,2,-2,0,0,18)")
# The singularity inscription is the rim of the funnel, not a flat cylinder facing the lens.
s=s.replace("if idx==15 and rowid==0:v[1]+=.023", "if idx==10 and rowid==1:\n     th=gx/20+math.pi/2;rr=9+v[1];v[0]=rr*math.cos(th);v[1]=rr*math.sin(th)-6;v[2]=v[2]*.3\n    if idx==15 and rowid==0:v[1]+=.023")
s=s.replace("def drawframe(t):\n idx=", "def drawframe(t):\n global last_camera_stats\n idx=")
s=s.replace("ms.use();ms.clear(.002", "clip=np.c_[pp,np.ones(len(pp))]@vp.T;ndc=clip[:,:3]/clip[:,3:4]\n last_camera_stats={'t':float(t),'idx':int(idx),'row':int(active),'xmin':float(ndc[:,0].min()),'xmax':float(ndc[:,0].max()),'ymin':float(ndc[:,1].min()),'ymax':float(ndc[:,1].max())}\n ms.use();ms.clear(.002",1)
s=s.replace("def main():\n if '--preview'", "def main():\n if '--audit' in sys.argv:\n  audit=[]\n  for t in np.arange(1.5,141,.25):drawframe(float(t));audit.append(last_camera_stats)\n  json.dump(audit,open('v4/framing_audit.json','w'),indent=2);print('audit samples',len(audit),flush=True);return\n if '--preview'")
p.write_text(s,encoding='utf-8')
