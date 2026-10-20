"""Forty actual late-pair composition samples, raw or from a finished MP4.

Run this file for actual OpenGL preview frames.  Pass --encoded FILE for the
same frame numbers from the finalized movie.  The report records provenance
and leaves the aesthetic verdict pending until the sheets are viewed.
"""

from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import math
import subprocess
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ('memory retirement', (77.70, 78.80, 79.95, 80.48)),
    ('left junction', (81.05, 81.95, 82.80, 83.60)),
    ('switch / absent operator', (99.22, 99.53, 99.87, 100.46)),
    ('blocked escape / too late', (101.22, 101.50, 101.92, 102.42)),
    ('trace ignition', (102.70, 102.99, 103.28, 103.61)),
    ('independent axes', (105.30, 106.97, 107.65, 108.80)),
    ('core / failed feedback', (118.98, 119.85, 120.45, 121.65)),
    ('selected future', (126.66, 127.25, 127.58, 127.84)),
    ('occluded witness', (133.00, 133.55, 134.65, 135.50)),
    ('backstage strings', (137.30, 138.25, 139.10, 140.45)),
)
NATIVE = (99.87, 103.28, 119.85, 133.55)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--encoded', type=Path)
    args = parser.parse_args()
    prefix = 'qa_pair_encoded' if args.encoded else 'qa_pair_preview'
    all_times = [t for _, group in PLAN for t in group]
    frames = [int(math.ceil(t*30.-1.e-7)) for t in all_times]
    video = args.encoded.resolve(strict=True) if args.encoded else None
    video_size = video.stat().st_size if video else None
    if video:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        def get_frame(frame):
            data = subprocess.run([ffmpeg, '-v', 'error', '-ss', str(frame/30.),
                '-i', str(video), '-an', '-sn', '-frames:v', '1', '-f',
                'rawvideo', '-pix_fmt', 'rgb24', '-threads', '1', '-'],
                capture_output=True, check=True).stdout
            if len(data) != 1920*1080*3:
                raise RuntimeError('Expected finalized 1920x1080 movie')
            return Image.frombytes('RGB', (1920, 1080), data)
        with ThreadPoolExecutor(max_workers=2) as pool:
            images = list(pool.map(get_frame, frames))
    else:
        sys.path.insert(0, str(ROOT/'v20'))
        spec = importlib.util.spec_from_file_location('late_pair_preview_renderer', ROOT/'v20/render.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        images = []
        for i, frame in enumerate(frames):
            data = renderer.drawframe(frame/30.)
            images.append(Image.frombytes('RGB', (renderer.W, renderer.H), data).transpose(Image.Transpose.FLIP_TOP_BOTTOM))
            print(f'{i+1}/{len(frames)} actual frame {frame/30.:.3f}s', flush=True)
    sheet = Image.new('RGB', (1920, len(PLAN)*296), (4, 7, 11))
    draw = ImageDraw.Draw(sheet)
    samples = []
    for row, (label, group) in enumerate(PLAN):
        for col, t in enumerate(group):
            i = row*4+col
            im = images[i]
            sheet.paste(im.resize((480, 270), Image.Resampling.LANCZOS), (col*480, row*296))
            draw.text((col*480+6, row*296+274), f'{label}: {frames[i]/30.:.3f}s', fill='white')
            path = None
            if t in NATIVE:
                path = ROOT/'v20'/f'{prefix}-{t:.3f}.jpg'
                im.save(path, quality=96)
            samples.append(dict(label=label, requested_time=t, frame=frames[i],
                time=frames[i]/30., path=str(path) if path else None,
                sha256=hashlib.sha256(im.tobytes()).hexdigest()))
    destination = ROOT/'v20'/f'{prefix}.jpg'
    sheet.save(destination, quality=95)
    for page in range(5):
        sheet.crop((0, page*592, 1920, (page+1)*592)).save(
            ROOT/'v20'/f'{prefix}_page_{page+1}.jpg', quality=95)
    if video and video.stat().st_size != video_size:
        raise RuntimeError('Movie changed during extraction')
    report = dict(source='actual_encoded_mp4' if video else 'actual_production_drawframe',
        video=str(video) if video else None, video_bytes=video_size,
        sample_count=len(samples), visual_verdict='pending actual visual inspection', samples=samples)
    (ROOT/'v20'/f'{prefix}.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(destination, flush=True)


if __name__ == '__main__':
    main()
