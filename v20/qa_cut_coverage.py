"""Measure actual frame-view phrase coverage and cold-open full-frame presence."""
from pathlib import Path
import importlib.util,sys,json,math
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'v20'))
spec=importlib.util.spec_from_file_location('qa_cut_renderer',ROOT/'v20/render.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
from first_half_score import PHRASE_CUTS,SILENT_CUTS
from hook_director import HOOK_CUTS
seen={};finite=True;frames=0
for frame in range(math.ceil(73.87*30)):
 t=frame/30;state,eye,target,vp=r.frame_view(t)
 finite &= bool(np.isfinite(eye).all() and np.isfinite(target).all() and np.isfinite(vp).all())
 phase=state.get('meaning_camera')
 if phase:
  seen.setdefault(phase,[]).append(t)
 frames+=1
rows=[]
for phase,ts in seen.items():
 eyes=np.array([r.frame_view(t)[1] for t in ts]);d=np.ptp(eyes,axis=0)
 rows.append(dict(phase=phase,frames=len(ts),start=ts[0],end=ts[-1],eye_xyz_range=d.tolist()))
report=dict(frame_samples=frames,finite_camera_matrices=finite,lexical_groups_defined=len(PHRASE_CUTS),
            active_lexical_camera_groups=sum(not x['phase'].startswith('pair_-1_') for x in rows),
            active_silent_camera_groups=sum(x['phase'].startswith('pair_-1_') for x in rows),
            hook_cuts=list(HOOK_CUTS),groups=rows)
(ROOT/'v20/qa_cut_coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='groups'},indent=2))
assert finite
