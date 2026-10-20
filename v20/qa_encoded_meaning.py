"""Read-only visual audit samples extracted from the actual encoded v20 MP4.

No renderer imports, OpenGL calls or production changes. Run after the final
MP4 has completed: python v20/qa_encoded_meaning.py [path/to/final.mp4]
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
DEFAULT_VIDEO = ROOT / 'output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_Smooth_1080p.mp4'
PLAN = [('hook',[0.,.35,.8,1.4]),('eye',[3.7,34.9,36.9,37.9]),('free',[56.86,57.545,57.82,58.25]),('pursuit',[62.8,63.4,63.85,64.35]),('repeat',[74.1,75.6,76.1,76.9]),('cdr',[85.,86.5,87.8,89.4]),('memory',[78.3,79.1,79.9,80.5]),('operator',[99.3,99.6,100.05,101.8]),('fuse',[102.5,102.76,103.42,104.12]),('axes',[105.3,106.5,107.1,108.7]),('transformer',[110.7,112.1,113.1,114.6]),('feedback',[119.2,119.8,120.8,122.1]),('branch',[125.1,126.2,126.8,127.6]),('upgrade',[128.47,129.42,129.8,130.36]),('cascade',[130.76,131.36,131.96,132.2]),('witness',[132.6,134.1,136.55,138.5]),('outro',[145.4,153.415,155.8,156.6])]



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
    assert len(times) == len(set(times)) == 68
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

    destination = ROOT / 'v20/qa_encoded_meaning.jpg'
    sheet.save(destination, quality=94)
    for page,row in enumerate(range(0,len(PLAN),4),1):
        sheet.crop((0,row*296,1920,min(len(PLAN),row+4)*296)).save(ROOT/f"v20/qa_encoded_page_{page}.jpg",quality=94)
    report = {
        'video': str(video), 'video_bytes': video.stat().st_size,
        'source': 'FFmpeg extraction from actual encoded MP4',
        'samples': samples, 'sample_count': len(samples),
        'contact_sheet': str(destination),
        'visual_verdict': 'pending human/model inspection',
    }
    (ROOT / 'v20/qa_encoded_meaning.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(destination)
    print('68 decoded samples; visual review pending')


if __name__ == '__main__':
    main()
