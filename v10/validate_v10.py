"""Decode, audio-bitstream and edit-boundary QA for the cinematic v6 master.

Run from any directory.  ``--contacts-only`` skips the full decode and audio
hash pass, making it useful while reviewing a newly rendered sample/master.
The event JSON may be a list of numbers, a list of objects containing ``t``,
or an object with an ``events`` / ``EVENTS`` / ``cuts`` list.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import pathlib
import re
import subprocess
import sys
from datetime import datetime

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = pathlib.Path(__file__).resolve().parents[1]
QA = ROOT / 'v10'
DEFAULT_VIDEO = ROOT / 'output_v10' / 'Im_Upping_My_Pdoom_Multi_Angle_1080p.mp4'
DEFAULT_SOURCE = ROOT / '吓哭了Opus5.5 AGI概念MV.mp4'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
THUMB_W, THUMB_H = 320, 180
OFFSETS = (-3, -2, -1, 0, 1, 2, 3)


def run(command: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True)
    if result.returncode:
        error = result.stderr.decode('utf-8', errors='replace')
        raise RuntimeError(f'Command failed ({result.returncode}): {error[-6000:]}')
    return result


def load_events(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f'Edit event JSON is required: {path}')
    raw = json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(raw, dict):
        for key in ('events', 'EVENTS', 'cuts', 'transitions'):
            if key in raw:
                raw = raw[key]
                break
        else:
            raise ValueError('Event JSON object needs an events, EVENTS, cuts or transitions list')
    if not isinstance(raw, list):
        raise ValueError('Edit events must be a list')
    result = []
    for index, value in enumerate(raw):
        if isinstance(value, (int, float)):
            event = {'t': float(value)}
        elif isinstance(value, dict):
            event = dict(value)
            for key in ('t', 'time', 'cut', 'at', 'start'):
                if isinstance(event.get(key), (int, float)):
                    event['t'] = float(event[key])
                    break
            else:
                raise ValueError(f'Event {index} has no numeric time: {value!r}')
        elif isinstance(value, (tuple, list)) and value and isinstance(value[0], (int, float)):
            event = {'t': float(value[0]), 'label': str(value[1]) if len(value) > 1 else ''}
        else:
            raise ValueError(f'Unsupported edit event {index}: {value!r}')
        if not math.isfinite(event['t']) or event['t'] < 0:
            raise ValueError(f'Invalid event time: {event!r}')
        result.append(event)
    return sorted(result, key=lambda item: item['t'])


def inspect_video(video: pathlib.Path) -> tuple[str, float, float]:
    result = subprocess.run([FFMPEG, '-hide_banner', '-i', str(video)], capture_output=True)
    meta = result.stderr.decode('utf-8', errors='replace')
    duration_match = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', meta)
    fps_match = re.search(r'(\d+(?:\.\d+)?)\s+fps', meta)
    if not duration_match:
        raise ValueError(f'Cannot read video duration:\n{meta}')
    hh, mm, ss = map(float, duration_match.groups())
    return meta, hh * 3600 + mm * 60 + ss, float(fps_match.group(1)) if fps_match else 30.0


def font(size: int):
    for path in ('C:/Windows/Fonts/consola.ttf', 'C:/Windows/Fonts/arial.ttf'):
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def extract_frames(video: pathlib.Path, event_time: float, fps: float, duration: float):
    cut_frame = int(math.ceil(event_time * fps - 1e-7))
    # Decoding from an exact frame boundary ensures the centre image is the
    # first displayed frame at or after the event, including off-grid times.
    start_frame = max(0, cut_frame - 3)
    start = start_frame / fps
    raw = run([FFMPEG, '-v', 'error', '-ss', f'{start:.9f}', '-i', str(video),
               '-map', '0:v:0', '-an', '-sn', '-frames:v', '7', '-vf',
               f'scale={THUMB_W}:{THUMB_H}:flags=lanczos', '-pix_fmt', 'rgb24',
               '-f', 'rawvideo', '-threads', '1', '-']).stdout
    frame_bytes = THUMB_W * THUMB_H * 3
    count = len(raw) // frame_bytes
    frames = [Image.frombytes('RGB', (THUMB_W, THUMB_H),
                             raw[i * frame_bytes:(i + 1) * frame_bytes])
              for i in range(count)]
    if not frames:
        raise ValueError(f'No frames at edit {event_time:.3f}s, video duration {duration:.3f}s')
    # Events within the first/last 3 frames repeat the boundary frame rather
    # than silently changing the seven-column temporal meaning.
    needed = []
    for offset in OFFSETS:
        absolute = max(0, min(int(duration * fps) - 1, cut_frame + offset))
        relative = max(0, min(len(frames) - 1, absolute - start_frame))
        needed.append(frames[relative])
    return cut_frame, needed


def label_for(event: dict) -> str:
    parts = [str(event.get(key, '')) for key in ('kind', 'name', 'label', 'reason')]
    return ' / '.join(dict.fromkeys(value for value in parts if value)) or 'scene edit'


def contacts(video: pathlib.Path, events: list[dict], fps: float, duration: float):
    events = [event for event in events if event['t'] < duration]
    if not events:
        raise ValueError('There are no edit events within this video')
    head_h, label_h, row_h = 42, 46, THUMB_H + 46
    width, height = THUMB_W * len(OFFSETS), head_h + row_h * len(events)
    sheet = Image.new('RGB', (width, height), '#101419')
    draw = ImageDraw.Draw(sheet)
    f_title, f_label = font(22), font(17)
    draw.text((12, 7), f'V8 KINETIC EDIT BOUNDARIES  |  {fps:g} fps  |  columns -3 ... CUT ... +3 frames',
              font=f_title, fill='#e8eeee')
    metrics = []
    for index, event in enumerate(events):
        cut_frame, images = extract_frames(video, event['t'], fps, duration)
        y = head_h + index * row_h
        draw.text((8, y + 3), f'{index + 1:02d}  {event["t"]:.3f}s  /  frame {cut_frame}  /  {label_for(event)}',
                  font=f_label, fill='#f1c778')
        for column, (offset, image) in enumerate(zip(OFFSETS, images)):
            x = column * THUMB_W
            sheet.paste(image, (x, y + label_h))
            draw.text((x + 7, y + 25), 'CUT' if offset == 0 else f'{offset:+d}',
                      font=f_label, fill='#f07892' if offset == 0 else '#b3bfc5')
        # Pixel difference is a diagnostic only; a large flash is not proof
        # of a meaningful change in composition or narrative.
        arrays = [np.asarray(image, dtype=np.float32) for image in images]
        differences = [float(np.mean(np.abs(b - a))) for a, b in zip(arrays, arrays[1:])]
        metrics.append({'t': event['t'], 'frame': cut_frame,
                        'label': label_for(event), 'adjacent_frame_mae': differences})
        print(f'Contact {index + 1}/{len(events)}: {event["t"]:.3f}s', flush=True)
    sheet.save(QA / 'transition_contact.jpg', quality=94, subsampling=0)
    # Human review is easier at full resolution in pages of six cuts.
    per_page = 6
    for page, start_row in enumerate(range(0, len(events), per_page), start=1):
        rows = min(per_page, len(events) - start_row)
        page_image = Image.new('RGB', (width, head_h + rows * row_h), '#101419')
        page_image.paste(sheet.crop((0, 0, width, head_h)), (0, 0))
        page_image.paste(sheet.crop((0, head_h + start_row * row_h,
                                     width, head_h + (start_row + rows) * row_h)), (0, head_h))
        page_image.save(QA / f'transition_contact_page_{page:02d}.jpg', quality=94, subsampling=0)
    (QA / 'transition_metrics.json').write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding='utf-8')
    return len(events)


def audio_hash(path: pathlib.Path) -> str:
    result = run([FFMPEG, '-v', 'error', '-i', str(path), '-map', '0:a:0',
                  '-c:a', 'copy', '-f', 'hash', '-hash', 'sha256', '-'])
    digest = result.stdout.decode('ascii', errors='replace').strip()
    if not re.fullmatch(r'SHA256=[0-9a-fA-F]{64}', digest):
        raise ValueError(f'Cannot obtain audio bitstream hash for {path}: {digest}')
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contacts-only', action='store_true')
    parser.add_argument('--video', type=pathlib.Path, default=DEFAULT_VIDEO)
    parser.add_argument('--source', type=pathlib.Path, default=DEFAULT_SOURCE)
    parser.add_argument('--events', type=pathlib.Path, default=QA / 'edit_events.json')
    args = parser.parse_args()
    video = args.video.resolve()
    if not video.is_file():
        parser.error(f'Video does not exist: {video}')
    QA.mkdir(parents=True, exist_ok=True)
    meta, duration, fps = inspect_video(video)
    report = [f'Checked: {datetime.now().isoformat(timespec="seconds")}',
              f'Video: {video}', f'Bytes: {video.stat().st_size}',
              f'Duration: {duration:.3f}s', f'FPS: {fps:g}']
    if not args.contacts_only:
        if not args.source.is_file():
            parser.error(f'Original audio source does not exist: {args.source}')
        print('Full decode started', flush=True)
        decoded = run([FFMPEG, '-v', 'error', '-xerror', '-i', str(video),
                       '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'])
        diagnostics = decoded.stderr.decode('utf-8', errors='replace').strip()
        if diagnostics:
            raise RuntimeError('Decode reported errors: ' + diagnostics)
        report.append('FULL DECODE: PASS')
        original_hash, master_hash = audio_hash(args.source), audio_hash(video)
        if original_hash != master_hash:
            raise AssertionError(f'Original audio bitstream differs:\n{original_hash}\n{master_hash}')
        report.extend(['AUDIO BITSTREAM MATCH: PASS', original_hash])
        print('Full decode passed; original audio bitstream SHA256 matches.', flush=True)
    else:
        report.extend(['FULL DECODE: SKIPPED (--contacts-only)',
                       'AUDIO BITSTREAM MATCH: SKIPPED (--contacts-only)'])
    count = contacts(video, load_events(args.events), fps, duration)
    report.append(f'TRANSITION CONTACTS: {count} events, 7 frames each')
    report.append(meta)
    report_path = QA / ('validation_contacts.txt' if args.contacts_only else 'validation.txt')
    report_path.write_text('\n'.join(report), encoding='utf-8')
    print(f'Saved {QA / "transition_contact.jpg"}', flush=True)
    print(f'Saved {report_path}', flush=True)


if __name__ == '__main__':
    main()
