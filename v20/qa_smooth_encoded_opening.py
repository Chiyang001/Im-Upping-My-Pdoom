"""Decode 32 early frames from the delivered smooth-v20 MP4 for visual review.

This script never imports the renderer. Contact sheets and native stills are
derived solely from the finalized encoded movie. A contact sheet cannot prove
temporal smoothness; qa_smooth_camera.py audits the final camera trajectory.
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
PLAN = (
    ('retained_hook', (0., .35, .8, 1.4)),
    ('single_eye', (1.6, 2.3, 3.7, 5.3)),
    ('circuits', (5.9, 6.5, 7.5, 8.7)),
    ('training_loss', (9.4, 10.6, 11.5, 12.2)),
    ('servant_boss', (13.1, 14.1, 15.2, 16.0)),
    ('dialogue', (17.2, 18.9, 20.45, 21.7)),
    ('pdoom_foom', (23.56, 23.98, 25., 25.6)),
    ('room_shrooms_eye', (27., 28.7, 30.8, 34.9)),
)
NATIVE = (3.7, 7.5, 21.7, 28.7, 34.9)
EXTRA_NATIVE = (28.4, 28.5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', nargs='?', type=Path, default=DEFAULT_VIDEO)
    args = parser.parse_args()
    video = args.video.expanduser().resolve(strict=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    times = [t for _, row in PLAN for t in row]
    assert len(times) == len(set(times)) == 32

    def extract(t):
        data = subprocess.run(
            [ff, '-v', 'error', '-ss', str(t), '-i', str(video),
             '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
        if len(data) != 1920*1080*3:
            raise AssertionError('Unexpected native decoded size at %.3f' % t)
        return t, Image.frombytes('RGB', (1920,1080), data), hashlib.sha256(data).hexdigest()

    with ThreadPoolExecutor(max_workers=4) as executor:
        frames = {t:(image,digest) for t,image,digest in executor.map(extract,times+list(EXTRA_NATIVE))}
    all_sheet = Image.new('RGB',(1920,len(PLAN)*296),(4,7,11))
    draw = ImageDraw.Draw(all_sheet)
    samples = []
    for row,(name,sequence) in enumerate(PLAN):
        for col,t in enumerate(sequence):
            image,digest = frames[t]
            all_sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),(480*col,296*row))
            draw.text((480*col+7,296*row+274),'%s / %.3fs' % (name,t),fill='white')
            if t in NATIVE:
                image.save(ROOT/'v20'/('qa_smooth_native_%05d.jpg' % round(t*1000)),quality=96)
            samples.append(dict(time=t,group=name,native_rgb_sha256=digest,
                                source='actual_encoded_smooth_mp4'))
    destination = ROOT/'v20/qa_smooth_encoded_opening.jpg'
    all_sheet.save(destination,quality=94)
    for page,row in enumerate(range(0,len(PLAN),4),1):
        all_sheet.crop((0,row*296,1920,min(len(PLAN),row+4)*296)).save(
            ROOT/'v20'/('qa_smooth_encoded_opening_page_%d.jpg' % page),quality=94)
    supplemental = []
    for t in EXTRA_NATIVE:
        image,digest = frames[t]
        path = ROOT/'v20'/('qa_smooth_native_%05d.jpg' % round(t*1000))
        image.save(path,quality=96)
        supplemental.append(dict(time=t,group='bag_word_pass',native_rgb_sha256=digest,
                                 image=str(path),source='actual_encoded_smooth_mp4'))
    video_digest = hashlib.sha256()
    with video.open('rb') as stream:
        for chunk in iter(lambda:stream.read(4*1024*1024),b''):
            video_digest.update(chunk)
    report = dict(video=str(video),video_bytes=video.stat().st_size,
                  video_sha256=video_digest.hexdigest(),
                  method='FFmpeg native RGB extraction from finalized encoded MP4; no rendering.',
                  sample_count=len(samples),samples=samples,contact_sheet=str(destination),
                  supplemental_native_samples=supplemental,
                  verdict='pending actual image inspection')
    (ROOT/'v20/qa_smooth_encoded_opening.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Decoded 32 opening frames, 5 native stills and 2 BAG pass checkpoints:',destination)


if __name__=='__main__':
    main()
