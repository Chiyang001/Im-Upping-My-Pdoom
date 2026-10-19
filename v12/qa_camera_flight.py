"""Read-only numerical FPV diagnostic against the actual renderer's word planes."""
import importlib.util,json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
version=sys.argv[1] if len(sys.argv)>1 else 'v12'
sys.path.insert(0,str(ROOT/version))
spec=importlib.util.spec_from_file_location('qa_renderer',ROOT/version/'render.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
plan=ROOT/version/'compositions.json'
if plan.exists():
 guards=json.loads(plan.read_text()).get('word_scale_guard',{})
 r.WORD_SCALE_GUARD.update({int(k):v for k,v in guards.items()})
report=[]
for e in r.IMPACTS:
 if e.name not in r.PDOOM_LYRIC_INDICES:continue
 i=r.PDOOM_LYRIC_INDICES[e.name]
 wi=next(j for j,x in enumerate(r.TOKEN_SCORES[i]) if r.token_norm(x['text'])=='pdoom')
 token=r.TOKEN_SCORES[i][wi];gpu=r.TOKEN_DATA[i][wi][0]
 samples=[];readable=[]
 for t in np.arange(e.time-.14,token['end']+.701,1/120):
  state,eye,target,vp=r.frame_view(float(t))
  focus,normal=r.camera_impact_focus(e.metadata(),float(t))
  signed=float((eye-focus)@normal)
  forward=(target-eye)/np.linalg.norm(target-eye)
  d={'t':round(float(t),6),'age':round(float(t-e.time),6),'signed_plane_distance':signed,'eye':list(map(float,eye)),'relative_eye':list(map(float,eye-focus)),'normal':list(map(float,normal)),'forward':list(map(float,forward)),'lens':float(state['lens']),'shot_id':state['shot_design']['shot_id'],'transition':state['edit']['transition']['kind'] if state['edit']['transition']['active'] else None}
  samples.append(d)
 # At encoded 30 fps, test the P(doom) actual physical face before the cross.
 crossings=[a['t']+(b['t']-a['t'])*a['signed_plane_distance']/(a['signed_plane_distance']-b['signed_plane_distance']) for a,b in zip(samples,samples[1:]) if a['signed_plane_distance']>0>=b['signed_plane_distance']]
 reverse=[{'t':a['t'],'same_shot':a['shot_id']==b['shot_id'],'from_shot':a['shot_id'],'to_shot':b['shot_id'],'transition':b['transition']} for a,b in zip(samples,samples[1:]) if a['signed_plane_distance']<0<=b['signed_plane_distance']]
 for frame in range(math.ceil(token['start']*30),math.floor(token['end']*30)+1):
  t=frame/30
  if crossings and t>=crossings[0]:continue
  ts=r.token_state(t,token)
  if not ts['visible'] or ts['reveal']<.99 or ts['gain']<.6:continue
  state,eye,target,vp=r.frame_view(t);model=r.token_matrix(i,wi,t)
  points=np.array([model@np.array([x,y,z,1.]) for x in [gpu.bmin[0],gpu.bmax[0]] for y in [gpu.bmin[1],gpu.bmax[1]] for z in [gpu.bmin[2],gpu.bmax[2]]])
  clip=points@vp.T;ndc=clip[:,:2]/clip[:,3:4]
  center=(model@np.r_[r.TOKEN_GROUPS[i][token['group']]['center'],1.])[:3]
  normal=np.cross(model[:3,0],model[:3,1]);normal/=np.linalg.norm(normal)
  cosine=float(normal@((eye-center)/np.linalg.norm(eye-center)))
  height=float(np.ptp(ndc[:,1])*r.H/2)
  if clip[:,3].min()>0 and abs(ndc).max()<=1.02 and cosine>.35 and height>=28:readable.append(t)
 rel=np.array([s['relative_eye'] for s in samples]);diff=np.diff(rel,axis=0)
 metrics={'name':e.name,'first_crossing':crossings[0] if crossings else None,'crossings':crossings,'reverse_crossings':reverse,'min_signed_plane_distance':min(s['signed_plane_distance'] for s in samples),'max_signed_plane_distance':max(s['signed_plane_distance'] for s in samples),'readable_30fps_pre_cross_frames':readable,'relative_path_units':float(np.linalg.norm(diff,axis=1).sum()),'relative_net_units':float(np.linalg.norm(rel[-1]-rel[0])),'max_relative_speed':float(np.linalg.norm(diff,axis=1).max()*120),'lens_range':[min(s['lens'] for s in samples),max(s['lens'] for s in samples)],'samples':samples}
 report.append(metrics)
out={'version':version,'events':report,'all_four_cross':all(x['first_crossing'] is not None for x in report),'all_four_read_before_cross':all(len(x['readable_30fps_pre_cross_frames'])>=2 for x in report),'all_four_no_return_cross':all(not any(z['same_shot'] and not z['transition'] for z in x['reverse_crossings']) for x in report)}
path=ROOT/'v12'/f'qa_camera_flight_{version}.json';path.write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='events'},indent=2))
for x in report:print(json.dumps({k:v for k,v in x.items() if k!='samples'}))
