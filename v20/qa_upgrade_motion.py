"""Deterministic geometry/word-cue checks without creating a GL context."""
import sys, pathlib, json, math
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'v20'),str(ROOT/'v4')]
from engine import Mesh,tr,rot
from upgrade_geometry import build_upgrade
from upgrade_director import sample_upgrade,upgrade_camera,upgrade_token_surface


def main():
    parts=build_upgrade(Mesh,np,math,np.array([.2,.93,.8]),np.array([.89,.95,1]),np.array([1,.22,.4]))
    assert all(not mesh.v for mesh in parts.values())
    assert all(np.isfinite(np.array(mesh.l)).all() for mesh in parts.values())
    g=dict(np=np,tr=tr,rot=rot,semantic_host=lambda *args:np.eye(4))
    steps=[]
    for a,b in [(127.90,128.56),(128.56,129.18),(129.18,129.60),(129.60,129.98),(129.98,130.56)]:
        poses=[upgrade_camera(t,[0,0,0],[0,0,-1],0,60,g=g) for t in np.linspace(a+.0001,b-.0001,120)]
        eye=np.array([p['eye'] for p in poses]);span=np.ptp(eye,axis=0)
        assert np.isfinite(eye).all() and span.min()>.1
        steps.append(dict(start=a,end=b,xyz_span=span.tolist(),distance=float(np.linalg.norm(np.diff(eye,axis=0),axis=1).sum())))
    assert upgrade_camera(130.56,[0,0,0],[0,0,-1],0,60,g=g) is None
    assert upgrade_token_surface(6,131.2,g=g) is None
    for k in range(6):
        a=upgrade_token_surface(k,128.,g=g)['matrix']
        b=upgrade_token_surface(k,129.,g=g)['matrix']
        assert np.array_equal(a,b),'Physical lyric surface followed the camera'
    facing=[]
    for k,t in enumerate([128.02,128.30,128.90,129.38,129.80,130.25]):
        m=upgrade_token_surface(k,t,g=g)['matrix']
        pose=upgrade_camera(t,[0,0,0],[0,0,-1],0,60,g=g)
        delta=np.array(pose['eye'])-m[:3,3]
        normal=m[:3,2]/np.linalg.norm(m[:3,2])
        cosine=float(delta@normal/np.linalg.norm(delta))
        assert cosine>.65,'Word plate is back-facing or edge-on'
        facing.append(dict(index=k,t=t,front_normal_cosine=cosine))
    events=[sample_upgrade(t+.0001)['phase'] for t in [127.90,128.08,128.56,129.18,129.60,129.98,130.56]]
    assert len(events)==len(set(events))==7
    stages=[len(parts[k].l) for k in ['successor_a','successor_b','successor_c']]
    assert stages[0]<stages[1]<stages[2]
    report=dict(pass_=True,parts=len(parts),line_vertices=sum(len(p.l) for p in parts.values()),triangle_vertices=0,
                word_motivated_phases=events,motion_segments=steps,successor_topology_vertices=stages,
                physical_surface_front_facing=facing,preserved_self_upgrade_flight_from=131.14,
                physical_surfaces_camera_independent=True)
    path=ROOT/'v20'/'qa_upgrade_motion.json'
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
