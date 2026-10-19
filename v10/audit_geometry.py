"""Inspect all fully traced lyric frames against authored camera geometry."""
import json, math
from pathlib import Path
import render as r
import numpy as np

r.prepare_compositions()
seen={}; complete={}; clipped=[]; backfaces=[]; tiny=[]; shots={}
for frame in range(math.ceil(141.2*30)):
    t=frame/30
    idx=next((i for i,line in enumerate(r.lines) if line[0]<=t<line[1]),-1)
    if idx<0:continue
    state,eye,target,vp=r.frame_view(t)
    shot=state['shot_design']; sid=shot['shot_id']
    shots[sid]=shot['kind']
    if state['edit']['transition']['active']:continue
    for wi in r.active_word_indices(idx,t):
        token=r.TOKEN_SCORES[idx][wi]; ts=r.token_state(t,token)
        if ts['reveal']<.99 or ts['gain']<.60:continue
        gpu=r.TOKEN_DATA[idx][wi][0]; model=r.token_matrix(idx,wi,t)
        points=np.array([model@np.array([x,y,z,1.]) for x in [gpu.bmin[0],gpu.bmax[0]] for y in [gpu.bmin[1],gpu.bmax[1]] for z in [gpu.bmin[2],gpu.bmax[2]]])
        clip=points@vp.T; ndc=clip[:,:2]/clip[:,3:4]
        centre=(model@np.r_[r.TOKEN_GROUPS[idx][token['group']]['center'],1.])[:3]
        normal=np.cross(model[:3,0],model[:3,1]); normal/=np.linalg.norm(normal)
        view=eye-centre;view/=np.linalg.norm(view)
        dot=float(normal@view)
        height=float(np.ptp(ndc[:,1])*r.H/2)
        key=f'{idx}:{wi}'
        seen.setdefault(key,[]).append((t,float(abs(ndc).max()),height,dot))
        if clip[:,3].min()<=0 or abs(ndc).max()>1.02:clipped.append([t,token['text'],float(abs(ndc).max())])
        if dot<=.35:backfaces.append([t,token['text'],dot])
        if height<28:tiny.append([t,token['text'],height])
        if clip[:,3].min()>0 and abs(ndc).max()<=1.02 and dot>.35 and height>=28:complete[key]=True
missing=[token['text'] for i,row in enumerate(r.TOKEN_SCORES) for wi,token in enumerate(row) if f'{i}:{wi}' not in complete]
report={'tokens_with_complete_readable_frame':len(complete),'missing_readable_tokens':missing,'full_reveal_clipped_frames':clipped,'backface_or_thin_frames':backfaces,'under_28px_frames':tiny,'independent_camera_shots':len(shots),'shot_kinds':shots,'min_complete_height_pixels':min(v[2] for row in seen.values() for v in row),'min_frontface_cosine':min(v[3] for row in seen.values() for v in row)}
Path('v10/geometry_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['full_reveal_clipped_frames','backface_or_thin_frames','under_28px_frames']},indent=2))
print('clipped',len(clipped),'backface',len(backfaces),'tiny',len(tiny))
assert not missing, missing
assert not clipped, clipped[:10]
assert not backfaces, backfaces[:10]
