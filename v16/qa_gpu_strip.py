"""Extract four GPU-sequence frames from the finished MP4, without OpenGL."""
from pathlib import Path
import hashlib
import json
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / 'output_v16/Im_Upping_My_Pdoom_Integrated_Linework_1080p.mp4'
TIMES = (118.75, 119.15, 119.65, 120.05)


def extract(t, name):
    proc = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-ss', str(t),
         '-i', str(VIDEO), '-frames:v', '1', '-f', 'rawvideo',
         '-pix_fmt', 'rgb24', '-'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if len(proc.stdout) != 1920 * 1080 * 3:
        raise RuntimeError(f'Unexpected decoded frame length at {t}')
    image = Image.frombytes('RGB', (1920, 1080), proc.stdout)
    path = ROOT / 'v16' / name
    image.save(path, quality=96)
    return image, dict(time=t, path=str(path),
                       decoded_pixels_sha256=hashlib.sha256(proc.stdout).hexdigest())


def main():
    sheet = Image.new('RGB', (1920, 1120), (4, 7, 11))
    draw = ImageDraw.Draw(sheet)
    frames = []
    for i, t in enumerate(TIMES):
        im, row = extract(t, f'qa_encoded_gpu_{t:.2f}.jpg')
        x, y = (i % 2) * 960, (i // 2) * 560
        sheet.paste(im.resize((960, 540)), (x, y))
        draw.text((x + 8, y + 544), f'GPU sequence / {t:.2f}s', fill='white')
        frames.append(row)
    path = ROOT / 'v16/qa_encoded_gpu_strip.jpg'
    sheet.save(path, quality=94)
    native = []
    for t in (3.7, 34.9, 111.7, 115.3):
        _, row = extract(t, f'qa_encoded_native_{t:.2f}.jpg')
        native.append(row)
    report = dict(video=str(VIDEO), source='actual_encoded_mp4', frames=frames,
                  contact_sheet=str(path), native_detail_frames=native,
                  visual_verdict='pending model inspection')
    (ROOT / 'v16/qa_encoded_gpu_strip.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(path)


if __name__ == '__main__':
    main()
