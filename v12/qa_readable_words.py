"""Read-only word-frame diagnostic; intentional travel clipping is allowed after readability."""
import importlib.util,json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
version='v12';sys.path.insert(0,str(ROOT/version))
spec=importlib.util.spec_from_file_location('qa_renderer',ROOT/version/'render.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
guards=json.loads((ROOT/version/'compositions.json').read_text()).get('word_scale_guard',{})
r.WORD_SCALE_GUARD.update({int(k):v for k,v in guards.items()})
report=[]
for i,row in enumerate(r.TOKEN_SCORES):
 for wi,token in enumerate(row):
  samples=[];readable=[];flightnames=set()
  for frame in range(math.ceil(token['start']*30),math.floor(token['end']*30)+1):
   t=frame/30;ts=r.token_state(t,token)
   if not ts['visible'] or ts['reveal']<.99 or ts['gain']<.6:continue
   state,eye,target,vp=r.frame_view(t);model=r.token_matrix(i,wi,t);gpu=r.TOKEN_DATA[i][wi][0]
   points=np.array([model@np.array([x,y,z,1.]) for x in [gpu.bmin[0],gpu.bmax[0]] for y in [gpu.bmin[1],gpu.bmax[1]] for z in [gpu.bmin[2],gpu.bmax[2]]])
   clip=points@vp.T;ndc=clip[:,:2]/clip[:,3:4]
   center=(model@np.r_[r.TOKEN_GROUPS[i][token['group']]['center'],1.])[:3]
   normal=np.cross(model[:3,0],model[:3,1]);normal/=np.linalg.norm(normal)
   cosine=float(normal@((eye-center)/np.linalg.norm(eye-center)));height=float(np.ptp(ndc[:,1])*r.H/2)
   fits=clip[:,3].min()>0 and abs(ndc).max()<=1.02 and cosine>.35 and height>=28
   if fits:readable.append(t)
   cam=state.get('impact_camera',{})
   if cam.get('active'):flightnames.add(cam.get('name'))
   samples.append({'t':t,'fit':bool(fits),'cosine':cosine,'height_px':height,'reach':float(abs(ndc).max()),'depth_min':float(clip[:,3].min()),'ndc_box':[float(ndc[:,0].min()),float(ndc[:,0].max()),float(ndc[:,1].min()),float(ndc[:,1].max())]})
  report.append({'line':i,'wi':wi,'text':token['text'],'start':token['start'],'end':token['end'],'flight':list(flightnames),'readable_frame_count':len(readable),'readable_times':readable,'samples':samples})
out={'tokens':len(report),'tokens_with_complete_readable_frame':sum(bool(x['readable_frame_count']) for x in report),'missing_readable_tokens':[{k:v for k,v in x.items() if k!='samples'} for x in report if not x['readable_frame_count']],'flight_tokens_with_under_two_readable_frames':[{k:v for k,v in x.items() if k!='samples'} for x in report if x['flight'] and x['readable_frame_count']<2],'report':report}
(ROOT/version/'qa_readability.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='report'},indent=2))
