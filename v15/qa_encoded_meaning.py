"""Read-only visual audit samples extracted from the actual encoded v15 MP4.

No renderer imports, OpenGL calls or production changes. Run after the final
MP4 has completed: python v15/qa_encoded_meaning.py [path/to/final.mp4]
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / 'output_v15/Im_Upping_My_Pdoom_Meaning_in_Motion_1080p.mp4'
PLAN = [
    ('opening', [3.7, 7.1, 11.8, 15.2]),
    ('eyes to training', [34.9, 36.8, 37.6, 39.8]),
    ('compute scale', [55.7, 63.2, 65.0, 67.0]),
    ('approval to MLP', [70.6, 73.3, 75.0, 76.6]),
    ('symbols to Gato', [79.1, 86.8, 89.3, 92.5]),
    ('control to axes', [94.8, 99.4, 101.2, 106.8]),
    ('Transformer', [109.9, 110.8, 111.7, 112.8]),
    ('disobey to dense', [113.7, 114.8, 115.3, 116.2]),
    ('GPU to futures', [119.7, 121.2, 123.6, 127.5]),
    ('masked to unknown', [128.5, 130.2, 133.7, 136.3]),
    ('show and finale', [138.8, 145.4, 150.7, 155.0]),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path, nargs='?', default=DEFAULT_VIDEO)
    args = parser.parse_args()
    video = args.video.expanduser().resolve(strict=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    metadata = subprocess.run(
        [ff, '-hide_banner', '-i', str(video)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding='utf-8', errors='replace',
    ).stderr
    if 'Video:' not in metadata:
        raise RuntimeError('Not a finalized readable video: ' + metadata[-1500:])

    def extract(t):
        proc = subprocess.run(
            [ff, '-v', 'error', '-ss', str(t), '-i', str(video),
             '-frames:v', '1', '-vf', 'scale=480:270', '-f', 'rawvideo',
             '-pix_fmt', 'rgb24', '-'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
        if len(proc.stdout) != 480 * 270 * 3:
            raise RuntimeError('Unexpected decoded frame length at %.3f' % t)
        return t, Image.frombytes('RGB', (480, 270), proc.stdout), hashlib.sha256(proc.stdout).hexdigest()

    times = [t for _, row in PLAN for t in row]
    assert len(times) == len(set(times)) == 44
    with ThreadPoolExecutor(max_workers=4) as executor:
        decoded = {t: (im, digest) for t, im, digest in executor.map(extract, times)}

    sheet = Image.new('RGB', (1920, 296 * len(PLAN)), (4, 7, 11))
    draw = ImageDraw.Draw(sheet)
    samples = []
    for row, (group, group_times) in enumerate(PLAN):
        for col, t in enumerate(group_times):
            im, digest = decoded[t]
            sheet.paste(im, (480 * col, 296 * row))
            draw.text((480 * col + 7, 296 * row + 274),
                      '%s / %.3fs' % (group, t), fill='white')
            samples.append({'group': group, 'time': t,
                            'decoded_pixels_sha256': digest,
                            'source': 'actual_encoded_mp4'})

    destination = ROOT / 'v15/qa_encoded_meaning.jpg'
    sheet.save(destination, quality=94)
    report = {
        'video': str(video), 'video_bytes': video.stat().st_size,
        'source': 'FFmpeg extraction from actual encoded MP4',
        'samples': samples, 'sample_count': len(samples),
        'contact_sheet': str(destination),
        'visual_verdict': 'pending human/model inspection',
    }
    (ROOT / 'v15/qa_encoded_meaning.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(destination)
    print('44 decoded samples; visual review pending')


if __name__ == '__main__':
    main()
