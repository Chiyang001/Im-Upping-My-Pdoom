"""Read-only visual audit samples extracted from the actual encoded v17 MP4.

No renderer imports, OpenGL calls or production changes. Run after the final
MP4 has completed: python v17/qa_encoded_meaning.py [path/to/final.mp4]
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
DEFAULT_VIDEO = ROOT / 'output_v17/Im_Upping_My_Pdoom_First_Half_Alchemy_1080p.mp4'
PLAN = [('opening',[2.9,3.7,5.3,6.2]),('control',[7.1,8.5,14.0,15.8]),('chat',[17.3,18.7,20.5,21.8]),('rise',[22.9,23.55,24.8,25.7]),('bag',[27.95,28.4,29.15,29.4]),('mask-eye',[30.8,34.9,37.6,39.6]),('training',[40.6,42.3,43.8,45.8]),('optimization',[46.4,47.7,48.4,50.5]),('atoms',[51.3,52.3,53.4,54.3]),('sydney',[55.7,56.8,57.7,58.2]),('serpent',[60.45,61.15,61.65,62.1]),('moon',[62.5,63.1,63.85,64.0]),('omega',[64.4,65.0,65.7,67.0]),('approval',[69.0,70.5,72.2,73.3]),('later',[75.,92.5,111.7,119.7]),('outro',[125.5,133.7,145.4,155.])]


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
    assert len(times) == len(set(times)) == 64
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

    destination = ROOT / 'v17/qa_encoded_meaning.jpg'
    sheet.save(destination, quality=94)
    for page,row in enumerate(range(0,len(PLAN),4),1):
        sheet.crop((0,row*296,1920,min(len(PLAN),row+4)*296)).save(ROOT/f"v17/qa_encoded_page_{page}.jpg",quality=94)
    report = {
        'video': str(video), 'video_bytes': video.stat().st_size,
        'source': 'FFmpeg extraction from actual encoded MP4',
        'samples': samples, 'sample_count': len(samples),
        'contact_sheet': str(destination),
        'visual_verdict': 'pending human/model inspection',
    }
    (ROOT / 'v17/qa_encoded_meaning.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(destination)
    print('64 decoded samples; visual review pending')


if __name__ == '__main__':
    main()
