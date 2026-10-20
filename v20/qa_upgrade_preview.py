"""Focused actual frames of the rebuilt pre-training / self-upgrade scene.

With --encoded FILE, inspect the delivered MP4 instead of raw production
frames. The source is never modified. The JSON records objective image
statistics only; an observer must inspect the contact pages and native frames.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
TIMES = (127.80, 127.99, 128.12, 128.28, 128.47, 128.65,
         128.82, 129.02, 129.20, 129.42, 129.59, 129.76,
         129.96, 130.16, 130.36, 130.56, 130.76, 130.96,
         131.16, 131.36, 131.56, 131.76, 131.96, 132.20, 132.40)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='v20')
    parser.add_argument('--encoded', type=Path)
    args = parser.parse_args()
    output = ROOT/args.version
    if args.encoded:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        def frame(t):
            data = subprocess.check_output([ffmpeg, '-v', 'error', '-ss', str(round(t*30)/30),
                    '-i', str(args.encoded), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
            return Image.frombytes('RGB', (1920, 1080), data)
        source = str(args.encoded.resolve())
        prefix = 'qa_upgrade_encoded'
    else:
        sys.path.insert(0, str(output))
        spec = importlib.util.spec_from_file_location('upgrade_qa_renderer', output/'render.py')
        r = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(r)
        r.prepare_compositions()
        def frame(t):
            return Image.frombytes('RGB', (r.W, r.H), r.drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        source = str(output/'render.py')
        prefix = 'qa_upgrade_preview'
    rows = []
    frames = []
    for i, t in enumerate(TIMES):
        im = frame(t)
        path = output/f'{prefix}_{t:.3f}.jpg'
        im.save(path, quality=95)
        a = np.asarray(im, dtype=float)
        lum = a.mean(axis=2)
        grid = [float(np.mean(lum[y:y+270, x:x+480] > 15))
                for y in range(0, 1080, 270) for x in range(0, 1920, 480)]
        rows.append(dict(t=t, path=str(path), mean_luma=float(lum.mean()),
                         lit_fraction=float(np.mean(lum > 15)), quadrant_lit_fraction=grid,
                         rgb_sha256=hashlib.sha256(np.asarray(im).tobytes()).hexdigest()))
        frames.append(im)
    for page, offset in enumerate(range(0, len(frames), 9), 1):
        slab = frames[offset:offset+9]
        sheet = Image.new('RGB', (1920, 3*385), (8, 10, 13))
        d = ImageDraw.Draw(sheet)
        for j, im in enumerate(slab):
            x, y = j%3*640, j//3*385
            sheet.paste(im.resize((640, 360)), (x, y))
            d.text((x+6, y+363), f'{TIMES[offset+j]:.3f}s', fill='white')
        sheet.save(output/f'{prefix}_page_{page}.jpg', quality=95)
    report = dict(source=source, version=args.version, frames=rows,
                  status='Visual review required; numerical image statistics are not an aesthetic verdict.',
                  intended_review=['Old central concentric ring presentation absent during 127.96-132.22.',
                                   'Camera has readable motivated lateral / vertical / forward parallax.',
                                   'Masking, pre-training and recursive self-upgrade are visible physical changes.',
                                   'Physical lyrics remain visible and full-frame composition stays coherent.',
                                   'Check 127.80 and 132.40 handoffs for continuity.'])
    path = output/f'{prefix}.json'
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(source=source, frames=len(rows), pages=3, report=str(path)), indent=2))


if __name__ == '__main__':
    main()
