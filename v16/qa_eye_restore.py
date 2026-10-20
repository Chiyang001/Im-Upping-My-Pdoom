"""Compare original single-eye shots as raw RGB, without encoding noise.

All v14 draws finish before v16 creates its GL context.  No production file is
modified.  Use --static-only to inspect the semantic director without a GPU.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'v16' / 'eye_restore_validation.json'
TIMES = (1.6, 3.7, 5.3, 32.8, 34.9, 36.8, 37.8)


def inspect_director():
    source = ROOT / 'v16' / 'semantic_director.py'
    text = source.read_text(encoding='utf-8')
    tree = ast.parse(text, filename=str(source))
    red_calls = []
    dynamic_modulo = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else '')
            if name == 'draw_red_path':
                red_calls.append(node.lineno)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            names = {child.id for child in ast.walk(node)
                     if isinstance(child, ast.Name)}
            if names & {'t', 'u', 'phase', 'clock', 'time'}:
                dynamic_modulo.append(dict(line=node.lineno,
                                           expression=ast.unparse(node)))
    return dict(source=str(source),
                draw_red_path_mentions='draw_red_path' in text,
                draw_red_path_calls=red_calls,
                dynamic_phase_modulo=dynamic_modulo,
                passed='draw_red_path' not in text and not dynamic_modulo)


def load_renderer(version):
    # render_options is imported before a renderer sets up its version paths.
    # Remove its cached version, and resolve the requested local module first.
    sys.modules.pop('render_options', None)
    sys.path.insert(0, str(ROOT / version))
    sys.path.insert(1, str(ROOT))
    alias = f'qa_eye_renderer_{version}'
    spec = importlib.util.spec_from_file_location(alias, ROOT / version / 'render.py')
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Cannot load {version} renderer')
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def render_hashes(version):
    renderer = load_renderer(version)
    rows = []
    for t in TIMES:
        rgb = renderer.drawframe(t)
        expected = renderer.W * renderer.H * 3
        if len(rgb) != expected:
            raise AssertionError(f'{version} {t}: {len(rgb)} RGB bytes, expected {expected}')
        digest = hashlib.sha256(rgb).hexdigest()
        rows.append(dict(t=t, raw_rgb_bytes=len(rgb), sha256=digest))
        print(f'{version} {t:.3f}: {digest}', flush=True)
    # Do not call this renderer after loading the next GL context.
    return rows


def main():
    os.chdir(ROOT)
    director = inspect_director()
    if '--static-only' in sys.argv:
        print(json.dumps(director, indent=2))
        assert director['passed'], 'Semantic director contains dynamic foreground scans'
        return
    original = render_hashes('v14')
    candidate = render_hashes('v16')
    frames = [dict(t=a['t'], v14_sha256=a['sha256'], v16_sha256=b['sha256'],
                   raw_rgb_bytes=a['raw_rgb_bytes'], exactly_equal=a['sha256'] == b['sha256'])
              for a, b in zip(original, candidate)]
    passed = director['passed'] and all(row['exactly_equal'] for row in frames)
    report = dict(baseline='v14', candidate='v16',
                  compared='Raw 1920x1080 RGB buffers before video encoding',
                  sequential_contexts=True, sampled_frames=len(frames),
                  all_eye_frames_exactly_equal=all(row['exactly_equal'] for row in frames),
                  semantic_director_static=director, passed=passed, frames=frames)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(OUTPUT)
    assert passed, 'Single-eye restoration or finite-action static validation failed'


if __name__ == '__main__':
    main()
