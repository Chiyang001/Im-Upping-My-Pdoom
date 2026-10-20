"""Exact raw-RGB audit for the retained hook, cage fracture, lunar pursuit and finale.

Late lexical camera scenes and the new upgrade sequence intentionally change.
Only the specified protected scenes are compared; this is not a global frame audit.

Finish every v19 draw before creating v20's GL context. Project-local module
caches and search paths are rebuilt between imports, so this audit cannot
accidentally render v20 with cached v19 semantics or camera modules. It reads
production files and writes only its JSON report. Importing this module does
not create a context; run it as a script when the GPU is available.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'v20' / 'preserved_scenes_validation.json'
EYE_TIMES = ()
LATER_TIMES = (0., 1.4, 57.82, 63.85, 145.4, 153.4, 155.8)
TIMES = EYE_TIMES + LATER_TIMES


def in_project(path):
    try:
        return Path(path).resolve().is_relative_to(ROOT)
    except (TypeError, ValueError, OSError):
        return False


def prepare_version(version):
    removed = []
    # Includes render_options, first_half_*, semantic_*, transformer, metaphor,
    # flight_camera and their transitive helpers without relying on a stale
    # hand-maintained list. Keep prior renderer aliases alive, but never call
    # their draw functions again once the next context has been created.
    for name, module in tuple(sys.modules.items()):
        if name == '__main__' or name.startswith('qa_preserved_renderer_'):
            continue
        origin = getattr(module, '__file__', None)
        if origin and in_project(origin):
            sys.modules.pop(name, None)
            removed.append(name)
    sys.modules.pop('render_options', None)
    sys.path[:] = [entry for entry in sys.path
                   if not in_project(entry or str(Path.cwd()))]
    sys.path[:0] = [str(ROOT / version), str(ROOT)]
    importlib.invalidate_caches()
    return sorted(removed)


def render_hashes(version):
    cleared = prepare_version(version)
    alias = f'qa_preserved_renderer_{version}'
    spec = importlib.util.spec_from_file_location(alias, ROOT / version / 'render.py')
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Cannot import renderer {version}')
    renderer = importlib.util.module_from_spec(spec)
    sys.modules[alias] = renderer
    spec.loader.exec_module(renderer)
    rows = []
    for t in TIMES:
        raw = renderer.drawframe(t)
        if len(raw) != renderer.W * renderer.H * 3:
            raise AssertionError(f'{version} {t}: unexpected raw RGB buffer size')
        digest = hashlib.sha256(raw).hexdigest()
        rows.append(dict(t=t, raw_rgb_bytes=len(raw), sha256=digest,
                         group='original_single_eye' if t in EYE_TIMES else 'later_scene'))
        print(f'{version} {t:.3f}: {digest}', flush=True)
    modules = {}
    for name in ('render_options','flight_camera','semantic_score','semantic_director',
                 'transformer_geometry','metaphor_geometry','metaphor_extra',
                 'first_half_score','first_half_director','first_half_geometry',
                 'organic_geometry','orbital_geometry'):
        mod = sys.modules.get(name)
        if mod is not None:
            modules[name] = str(Path(mod.__file__).resolve())
    return dict(version=version, frames=rows, cleared_project_modules=cleared,
                loaded_module_paths=modules)


def main():
    os.chdir(ROOT)
    baseline = render_hashes('v19')
    candidate = render_hashes('v20')
    rows = [dict(t=a['t'], group=a['group'], raw_rgb_bytes=a['raw_rgb_bytes'],
                 v19_sha256=a['sha256'], v20_sha256=b['sha256'],
                 exactly_equal=a['sha256'] == b['sha256'])
            for a, b in zip(baseline['frames'], candidate['frames'])]
    eye_ok = all(row['exactly_equal'] for row in rows if row['group']=='original_single_eye')
    later_ok = all(row['exactly_equal'] for row in rows if row['group']=='later_scene')
    # The renderer imports version-local modules, while unchanged older public
    # geometry such as metaphor_geometry intentionally stays in v14.
    version_imports_ok = all(
        Path(candidate['loaded_module_paths'][name]).parent == ROOT / 'v20'
        for name in ('render_options','flight_camera','semantic_score','semantic_director',
                     'transformer_geometry','first_half_score','first_half_director',
                     'first_half_geometry','organic_geometry','orbital_geometry'))
    report = dict(baseline='v19', candidate='v20',
                  compared='Raw 1920x1080 RGB buffers before video encoding',
                  sequential_contexts=True, sampled_frames=len(rows),
                  eye_geometry_compared=False,
                  all_later_frames_exactly_equal=later_ok,
                  candidate_version_imports_correct=version_imports_ok,
                  passed=eye_ok and later_ok and version_imports_ok,
                  frames=rows,
                  cache_isolation={key:{k:v for k,v in value.items() if k!='frames'}
                                   for key,value in [('baseline',baseline),('candidate',candidate)]})
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items()
                      if key not in ('frames','cache_isolation')}, ensure_ascii=False, indent=2))
    print(OUTPUT)
    assert report['passed'], 'Original eyes or later scenes changed, or import isolation failed'


if __name__=='__main__':
    main()
