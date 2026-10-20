"""Read-only pursuit metrics from actual renderer matrices and camera poses."""
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qa_renderer', ROOT/'v18/render.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

samples = []
old_i = r.PDOOM_LYRIC_INDICES['PDOOM 2']
old_j = next(j for j,x in enumerate(r.TOKEN_SCORES[old_i]) if r.token_norm(x['text']) == 'pdoom')
old_token = r.TOKEN_SCORES[old_i][old_j]
for t in np.arange(62.34, 65.94, 1/240):
    t = float(t)
    state, eye, target, vp = r.frame_view(t)
    orbit, omega = r.orbital_models(t)
    marks = r.pursuit_landmarks(t, orbit, omega, np=np)
    phase = state['object_pursuit']
    name = ('sled' if phase == 'payload_chase' else
            'omega' if phase == 'omega_convergence' else 'moon')
    actor = marks[name]
    sight = (target-eye)/np.linalg.norm(target-eye)
    offset = actor-eye
    cosine = float(sight @ (offset/np.linalg.norm(offset)))
    m = r.token_matrix(old_i, old_j, t)
    group = r.TOKEN_GROUPS[old_i][old_token['group']]
    centre = (m @ np.r_[group['center'], 1.])[:3]
    normal = np.cross(m[:3,0], m[:3,1]);normal /= np.linalg.norm(normal)
    samples.append(dict(t=t, phase=phase, eye=eye.tolist(), target=target.tolist(),
                        focus_subject=name, subject_position=actor.tolist(),
                        subject_distance=float(np.linalg.norm(offset)),
                        aim_cosine=cosine, lens=float(state['lens']),
                        old_pdoom_signed=float((eye-centre)@normal),
                        old_pdoom_visible=bool(r.token_state(t,old_token)['visible'])))
eyes = np.asarray([s['eye'] for s in samples])
crossings = []
for a,b in zip(samples,samples[1:]):
    if a['old_pdoom_signed']*b['old_pdoom_signed'] < 0:
        crossings.append(dict(t=(a['t']+b['t'])*.5,
                              direction='front_to_back' if a['old_pdoom_signed']>0 else 'back_to_front',
                              word_visible=a['old_pdoom_visible'] or b['old_pdoom_visible']))
phases = {}
for phase in dict.fromkeys(s['phase'] for s in samples):
    part = [s for s in samples if s['phase'] == phase]
    p = np.asarray([s['eye'] for s in part])
    phases[phase] = dict(interval=[part[0]['t'], part[-1]['t']],
                         xyz_range=np.ptp(p,axis=0).tolist(),
                         path_distance=float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum()),
                         subject_distance=[min(s['subject_distance'] for s in part),
                                           max(s['subject_distance'] for s in part)],
                         aim_cosine=[min(s['aim_cosine'] for s in part),max(s['aim_cosine'] for s in part)])
report = dict(samples=len(samples), interval=[samples[0]['t'],samples[-1]['t']],
              world_xyz_range=np.ptp(eyes,axis=0).tolist(),
              world_path_distance=float(np.linalg.norm(np.diff(eyes,axis=0),axis=1).sum()),
              peak_world_speed=float(np.linalg.norm(np.diff(eyes,axis=0),axis=1).max()*240),
              phases=phases, old_pdoom_plane_crossings=crossings,
              visible_old_pdoom_crossings=[x for x in crossings if x['word_visible']],
              original_pdoom_2_interval_untouched=bool(62.34 >= old_token['end']),
              actor_hosts_sample_authored_camera='authored_frame_view(reference,0)' in (ROOT/'v18/render.py').read_text(encoding='utf8'),
              finite=bool(np.isfinite(eyes).all()))
path = ROOT/'v18/qa_object_pursuit.json'
path.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2));print(path)
