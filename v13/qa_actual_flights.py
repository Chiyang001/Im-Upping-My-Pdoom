"""Read-only flight QA against actual world words and renderer camera output."""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qa_renderer', ROOT/'v13/render.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
from flight_camera import FLIGHTS
composition = ROOT/'v13/compositions.json'
if composition.exists():
    r.WORD_SCALE_GUARD.update({int(k):v for k,v in json.loads(composition.read_text()).get('word_scale_guard',{}).items()})

def token_for(event):
    name = event['name']
    if name in getattr(r, 'NARRATIVE_EVENTS', {}):
        item = r.NARRATIVE_EVENTS[name]
        i, keyword = item['line_index'], item['keyword']
        return i, next(j for j,x in enumerate(r.TOKEN_SCORES[i]) if r.token_norm(x['text']) == keyword)
    i = r.PDOOM_LYRIC_INDICES.get(name, {'SINGULARITY':10,'ATOMS':12,'FUSE':25,'SAFETY FENCE':28,'SELF UPGRADE':31}.get(name,0))
    candidates = [j for j,token in enumerate(r.TOKEN_SCORES[i]) if token['start']<=event['time']+.04<token['end']]
    j = next(j for j,x in enumerate(r.TOKEN_SCORES[i]) if r.token_norm(x['text'])=='pdoom') if name in r.PDOOM_LYRIC_INDICES else candidates[-1] if candidates else 0
    return i, j

events = []
for f in FLIGHTS:
    ctx = r.flight_context(f.name)
    event = ctx['event']
    i, j = token_for(event)
    token = r.TOKEN_SCORES[i][j]
    gpu = r.TOKEN_DATA[i][j][0]
    start = f.time-f.pre
    times = np.arange(start, f.handoff-.0001, 1/240)
    samples = []
    for t in times:
        state, eye, target, vp = r.frame_view(float(t))
        host_focus, host_normal = r.camera_impact_focus(event, float(t))
        # Use the actually drawn matrix as well as the fixed host.  Small
        # per-word entry/exit motions must not make a host-only audit claim
        # that the lens crossed a glyph which moved out of its way.
        word_matrix = r.token_matrix(i, j, float(t))
        focus = (word_matrix @ np.r_[r.TOKEN_GROUPS[i][token['group']]['center'], 1.])[:3]
        normal = np.cross(word_matrix[:3,0], word_matrix[:3,1])
        normal /= np.linalg.norm(normal)
        relative = eye-focus
        samples.append(dict(t=float(t), signed=float(relative@normal),
                            fixed_host_signed=float((eye-host_focus)@host_normal),
                            fixed_host_relative=[float(x) for x in eye-host_focus],
                            relative=[float(x) for x in relative],
                            camera_name=state['impact_camera'].get('name'),
                            lens=state['lens']))
    crossing = []
    reverse = []
    for a, b in zip(samples,samples[1:]):
        if a['signed']>0>=b['signed']:
            crossing.append(a['t']+(b['t']-a['t'])*a['signed']/(a['signed']-b['signed']))
        if a['signed']<0<=b['signed'] and a['camera_name']==b['camera_name']:
            reverse.append(b['t'])
    readable=[]
    for frame in range(math.ceil(token['start']*30), math.ceil(token['end']*30)):
        t=frame/30
        if crossing and t>=crossing[0]:
            continue
        ts=r.token_state(t,token)
        if not ts['visible'] or ts['reveal']<.99 or ts['gain']<.6:
            continue
        state,eye,target,vp=r.frame_view(t)
        m=r.token_matrix(i,j,t)
        points=np.array([m@np.array([x,y,z,1.]) for x in [gpu.bmin[0],gpu.bmax[0]] for y in [gpu.bmin[1],gpu.bmax[1]] for z in [gpu.bmin[2],gpu.bmax[2]]])
        clip=points@vp.T
        if clip[:,3].min()<=0:
            continue
        ndc=clip[:,:2]/clip[:,3:4]
        center=(m@np.r_[r.TOKEN_GROUPS[i][token['group']]['center'],1.])[:3]
        normal=np.cross(m[:3,0],m[:3,1]);normal/=np.linalg.norm(normal)
        cosine=float(normal@((eye-center)/np.linalg.norm(eye-center)))
        if abs(ndc).max()<=1.02 and cosine>.35 and np.ptp(ndc[:,1])*r.H/2>=28:
            readable.append(t)
    rel=np.array([s['fixed_host_relative'] for s in samples])
    step=np.diff(rel,axis=0)
    events.append(dict(name=f.name, line=i, word=j, text=token['text'],
                       token_start=token['start'], token_end=token['end'],
                       interval=[start,f.handoff], crosses=f.crosses,
                       actual_crossings=crossing, reverse_crossings=reverse,
                       readable_pre_cross_frames=readable,
                       relative_path_units=float(np.linalg.norm(step,axis=1).sum()),
                       relative_net_units=float(np.linalg.norm(rel[-1]-rel[0])),
                       peak_relative_speed=float(np.linalg.norm(step,axis=1).max()*240),
                       relative_xyz_range=[float(x) for x in np.ptp(rel,axis=0)],
                       lens_range=[min(s['lens'] for s in samples),max(s['lens'] for s in samples)],
                       samples=samples))

go=next(x for x in events if x['name']=='GO DISASTER')
report=dict(all_crossing_flights_cross=all(bool(x['actual_crossings']) for x in events if x['crosses']),
            all_flights_readable_pre_cross=all(bool(x['readable_pre_cross_frames']) for x in events),
            all_flights_no_reverse=all(not x['reverse_crossings'] for x in events),
            go_has_two_readable_frames=len(go['readable_pre_cross_frames'])>=2,
            go_crosses_while_sung=bool(go['actual_crossings']) and go['token_start']<=go['actual_crossings'][0]<go['token_end'],
            events=events)
path=ROOT/'v13/qa_actual_flights.json'
path.write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='events'},indent=2))
for e in events:
    print(json.dumps({k:v for k,v in e.items() if k!='samples'}))
print(path)
