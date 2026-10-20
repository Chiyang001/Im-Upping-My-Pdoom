"""Source-level rhythm, continuity and complete-fracture QA; no GPU needed."""
import importlib.util
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'v4'))
from engine import Mesh

spec = importlib.util.spec_from_file_location('free_under_test',
                                            ROOT / 'v20/free_impact.py')
free = importlib.util.module_from_spec(spec)
spec.loader.exec_module(free)


def main():
    meshes = free.build_free_impact(
        Mesh, np, math, np.array([.2, .93, .8]), np.array([.89, .95, 1]),
        np.array([1, .22, .4]))
    f = free._FIELD
    rhythm = json.loads((ROOT / 'code3d/rhythm_v3.json').read_text('utf-8'))
    kicks = {round(e['t'], 3) for e in rhythm['events']
             if e['components'].get('kick', 0) > .8}
    assert len(free.FREE_STRIKES) == 7
    assert all(round(e[0], 3) in kicks for e in free.FREE_STRIKES)
    assert all(not m.v for m in meshes.values()), 'Only drawn line geometry'
    assert f['chunk_count'] >= 300
    assert f['max_chunk_span'] < 2.8, 'No intact frame-sized fragment'
    assert set(meshes) == {'cage_field', 'contact_faults', 'pressure_rim'}
    peaks = []
    for onset, power, _, _ in free.FREE_STRIKES:
        s = free.sample_free_impact(onset + .014)
        assert s['strike'] > power * .88
        assert s['camera_local'][2] > .12, 'Each blow retreats physically'
        assert s['pressure'] > .35
        peaks.append({'kick': onset, 'strike_peak': s['strike'],
                      'camera_recoil_z': s['camera_local'][2],
                      'damage': s['damage']})
    # Damage is cumulative between attacks; it cannot reset between blows.
    damages = [free.sample_free_impact(e[0] + .12)['damage']
               for e in free.FREE_STRIKES[:-1]]
    assert all(b > a for a, b in zip(damages, damages[1:]))
    assert free.sample_free_impact(57.74)['damage'] > .99
    # Every source cell is liberated, including rear/side frames. Rotation
    # preserves each cell's shape while its centroid follows a ballistic path.
    deltas = []
    p = free._field_vertices(58.05, np)
    q = f['break_source']
    for idx in np.unique(f['ids']):
        mask = f['ids'] == idx
        delta = np.linalg.norm(p[mask].mean(0) - q[mask].mean(0))
        deltas.append(float(delta))
        # Rigid fragments keep all pairwise distances from a common origin.
        before = np.linalg.norm(q[mask] - q[mask][0], axis=1)
        after = np.linalg.norm(p[mask] - p[mask][0], axis=1)
        assert np.max(np.abs(before - after)) < 1.e-8
    assert min(deltas) > 2., 'Every fragment must leave its source cell'
    # At fracture time the vertices start at the deformed cage positions.
    a = free._field_vertices(free.FREE_HIT - 1.e-6, np)
    b = free._field_vertices(free.FREE_HIT, np)
    continuity = float(np.max(np.linalg.norm(a - b, axis=1)))
    assert continuity < .002
    finite = 0
    for t in np.linspace(free.FREE_START, free.FREE_END - 1.e-5, 401):
        pose = free._field_vertices(float(t), np)
        state = free.sample_free_impact(float(t))
        assert np.isfinite(pose).all()
        assert np.isfinite(state['camera_local']).all()
        assert np.isfinite(state['target_local']).all()
        finite += 1
    assert not free.sample_free_impact(free.FREE_START - .001)['active']
    assert not free.sample_free_impact(free.FREE_END)['active']
    report = {
        'status': 'PASS', 'strike_count': len(peaks), 'strikes': peaks,
        'all_measured_kicks': True, 'fragment_cells': f['chunk_count'],
        'line_vertices': len(meshes['cage_field'].l), 'triangle_vertices': 0,
        'maximum_fragment_axis_span': f['max_chunk_span'],
        'minimum_all_cell_displacement_at_58_05': min(deltas),
        'maximum_all_cell_displacement_at_58_05': max(deltas),
        'fracture_continuity_max_delta': continuity,
        'all_fragments_rigid': True, 'intact_frame_after_final': False,
        'finite_pose_samples': finite, 'cage_draw_calls_per_frame': 1,
    }
    (ROOT / 'v20/qa_free_impact.json').write_text(
        json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
