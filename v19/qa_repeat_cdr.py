"""Targeted actual-renderer audit and contact sheet for semantic camera work.

Uses the integrated v19 renderer when available.  --baseline-injection is a
development adapter against unchanged v18, never a production source edit.
"""
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
VERSION='v18' if '--baseline-injection' in sys.argv else 'v19'
sys.path.insert(0,str(ROOT/VERSION))
spec=importlib.util.spec_from_file_location('qa_semantic_renderer',ROOT/VERSION/'render.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
sys.path.insert(0,str(ROOT/'v19'))
from cdr_geometry import build_cdr, cdr_path
from meaning_camera import meaning_camera, repeat_travel
if VERSION=='v18':
    spec=importlib.util.spec_from_file_location('new_semantic_director',ROOT/'v19/semantic_director.py')
    director=importlib.util.module_from_spec(spec);spec.loader.exec_module(director)
    r.draw_integrated=director.draw_integrated
    r.CDR={k:r.GPU(m) for k,m in build_cdr(r.Mesh,np,math,r.C,r.WHITE,r.ACC).items()}
    original=r.frame_view
    def camera(t,hit=0):
        state,eye,target,vp=original(t,hit)
        move=meaning_camera(t,eye,target,state['roll'],state['lens'],g=r.__dict__)
        if move:
            eye,target=np.array(move['eye']),np.array(move['target'])
            state['roll'],state['lens']=move['roll'],move['fov']
            state['meaning_camera']=move['phase']
            cam=state['impact_camera'] if state['impact_camera']['active'] else None
            vp=r.perspective(math.radians(state['lens']),r.W/r.H,far=300)@r.view_matrix(eye,target,state['roll'],cam)
        return state,eye,target,vp
    r.frame_view=camera

r.prepare_compositions()
rows=[]
for i in [18,21]:
    for j,token in enumerate(r.TOKEN_SCORES[i]):
        readable=[];best=None
        gpu=r.TOKEN_DATA[i][j][0]
        for f in range(math.ceil(token['start']*30),math.ceil(token['end']*30)):
            t=f/30;ts=r.token_state(t,token)
            if not ts['visible'] or ts['reveal']<.99 or ts['gain']<.6:continue
            state,eye,target,vp=r.frame_view(t)
            m=r.token_matrix(i,j,t)
            p=np.array([m@np.array([x,y,z,1.]) for x in [gpu.bmin[0],gpu.bmax[0]] for y in [gpu.bmin[1],gpu.bmax[1]] for z in [gpu.bmin[2],gpu.bmax[2]]])
            clip=p@vp.T;ndc=clip[:,:2]/np.maximum(clip[:,3:4],1e-9)
            center=(m@np.r_[r.TOKEN_GROUPS[i][token['group']]['center'],1.])[:3]
            normal=np.cross(m[:3,0],m[:3,1]);normal/=np.linalg.norm(normal)
            cosine=float(normal@((eye-center)/np.linalg.norm(eye-center)))
            height=float(np.ptp(ndc[:,1])*r.H/2);reach=float(abs(ndc).max())
            item=dict(t=t,reach=reach,cosine=cosine,height=height)
            if best is None or reach<best['reach']:best=item
            if clip[:,3].min()>0 and reach<=1.02 and cosine>.35 and height>=28:readable.append(t)
        rows.append(dict(text=token['text'],readable_frames=readable,best=best))

samples=[]
for t in np.arange(76.30,77.24,1/240):
    event=r.NARRATIVE_EVENTS['FEEDBACK REPEAT'];eye=r.frame_view(float(t))[1]
    i,j=18,3;token=r.TOKEN_SCORES[i][j];m=r.token_matrix(i,j,float(t))
    focus=(m@np.r_[r.TOKEN_GROUPS[i][token['group']]['center'],1.])[:3]
    normal=np.cross(m[:3,0],m[:3,1]);normal/=np.linalg.norm(normal)
    samples.append((float(t),float((eye-focus)@normal)))
crosses=[a[0]+(b[0]-a[0])*a[1]/(a[1]-b[1]) for a,b in zip(samples,samples[1:]) if a[1]>0>=b[1]]
reverse=[b[0] for a,b in zip(samples,samples[1:]) if a[1]<0<=b[1]]

episodes=[('same neural rail',[74.15,75.35,76.05,76.25]),
          ('repeat launch',[76.45,76.70,77.02,77.18]),
          ('one physical cons spine',[84.95,85.55,86.00,86.75]),
          ('tail selection / departure',[87.30,88.10,88.85,89.60])]
sheet=Image.new('RGB',(1920,len(episodes)*295));d=ImageDraw.Draw(sheet)
for j,(label,times) in enumerate(episodes):
    for k,t in enumerate(times):
        im=Image.frombytes('RGB',(r.W,r.H),r.drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        im.save(ROOT/'v19'/f'repeat-cdr-{j}-{k}.jpg',quality=94)
        x,y=k*480,j*295;sheet.paste(im.resize((480,270)),(x,y))
        d.text((x+4,y+272),f'{label}: {t:.3f}s',fill='white')
sheet.save(ROOT/'v19/qa_repeat_cdr.jpg',quality=95)
for i in [0,2]:sheet.crop((0,i*295,1920,(i+2)*295)).save(ROOT/'v19'/f'qa_repeat_cdr_page_{i//2+1}.jpg',quality=95)
report=dict(version=VERSION,all_words_readable=all(x['readable_frames'] for x in rows),words=rows,
            repeat_actual_crossings=crosses,repeat_reverse_crossings=reverse,
            repeated_rail=[repeat_travel(t) for t in [73.87,75.9,76.30,77.239]])
(ROOT/'v19/qa_repeat_cdr.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
