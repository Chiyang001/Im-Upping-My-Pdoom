"""Verify the actual encoded moving ending without importing the GPU renderer.

Run after the full master has finished rendering.  This decodes only the last
62 frames and six requested inspection stills; it never re-encodes the video.
The source audit is independent of the raw-input motion report, while decoded
pixel hashes / MAE establish that motion survived the MP4 encode.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import subprocess
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'v20'
DEFAULT_VIDEO = ROOT / 'output_v20' / 'Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30
TAIL_START, EXPECTED_FRAMES = 154.6, 62
SAMPLES = (152.960, 153.415, 154.325, 155.150, 155.800, 156.600)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def source_audit():
    """Audit executable source, including inactive old code if still present."""
    paths = (QA / 'render.py', QA / 'infinity_finale.py')
    trees = []
    hashes = {}
    for path in paths:
        source = path.read_text(encoding='utf-8-sig')
        trees.append((path, ast.parse(source, filename=str(path))))
        hashes[path.name] = hashlib.sha256(source.encode('utf-8')).hexdigest()

    names = {node.id for _, tree in trees for node in ast.walk(tree)
             if isinstance(node, ast.Name)}
    imported = {alias.name for _, tree in trees for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names}
    literal_strings = [node.value for _, tree in trees for node in ast.walk(tree)
                       if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    # The song still has its canonical lyrics; this checks only the full
    # ending inscription strings, not the sung tokens "I'm upping my".
    no_inscription = not any(
        "I'm Upping My P(doom)" in value or 'Made by Chiyang001' in value
        for value in literal_strings)
    no_title_layout = 'end_title_layout' not in names | imported
    no_freeze_buffer = 'FREEZE_BUFFER' not in names

    time_clamps = []
    for path, tree in trees:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            assigns_time = any(isinstance(target, ast.Name) and target.id == 't'
                               for target in node.targets)
            if not assigns_time:
                continue
            for item in ast.walk(node.value):
                if (isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
                        and item.func.id in ('min', 'max')):
                    if any(isinstance(arg, ast.Name) and arg.id == 't'
                           for arg in ast.walk(item)):
                        time_clamps.append(f'{path.name}:{node.lineno}')

    checks = dict(no_song_title_or_maker_inscription=no_inscription,
                  no_end_title_layout=no_title_layout,
                  no_freeze_buffer=no_freeze_buffer,
                  no_render_time_clamp=not time_clamps)
    for name, passed in checks.items():
        require(passed, f'Source ending audit failed: {name}; time clamps={time_clamps}')
    return dict(checks=checks, source_sha256=hashes, time_clamp_locations=time_clamps)


def decoded_tail(video: Path):
    # Asking for one extra frame detects an unexpected duration/frame count.
    command = [FFMPEG, '-v', 'error', '-ss', f'{TAIL_START:.9f}', '-i', str(video),
               '-map', '0:v:0', '-an', '-sn', '-dn', '-vsync', '0',
               '-frames:v', str(EXPECTED_FRAMES+1), '-f', 'rawvideo',
               '-pix_fmt', 'rgb24', '-']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    frame_bytes = W*H*3
    hashes, differences, first_differences = [], [], []
    last_eight = deque(maxlen=8)
    previous = reference = None
    count = 0
    try:
        while True:
            raw = process.stdout.read(frame_bytes)
            if not raw:
                break
            require(len(raw) == frame_bytes,
                    f'Partial frame at tail index {count}: {len(raw)} bytes')
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(H,W,3)
            signed = frame.astype(np.int16)
            hashes.append(hashlib.sha256(raw).hexdigest())
            if reference is None:
                reference = signed.copy()
            first_differences.append(float(np.abs(signed-reference).mean()))
            if previous is not None:
                differences.append(float(np.abs(signed-previous).mean()))
            previous = signed
            # Eight inspection stills are retained, rather than holding the
            # 385MB decoded tail in memory at once.
            last_eight.append((count, Image.fromarray(frame.copy())))
            count += 1
        stderr = process.stderr.read().decode('utf-8', errors='replace')
        result = process.wait()
        require(result == 0, f'FFmpeg tail decode failed: {stderr[-4000:]}')
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()

    unique = len(set(hashes))
    require(count == EXPECTED_FRAMES,
            f'Expected {EXPECTED_FRAMES} encoded tail frames; decoded {count}')
    require(unique >= 60, f'Encoded ending has only {unique} unique frames')
    last_seven = differences[-7:]
    require(len(last_seven) == 7 and min(last_seven) > .01,
            f'Last eight frames lack continuous decoded motion: {last_seven}')
    require(first_differences[-1] > .05,
            'Final decoded frame does not visibly differ from the 154.6s frame')

    sheet = Image.new('RGB',(1920,590))
    painter = ImageDraw.Draw(sheet)
    tail_images=[]
    for j,(index,frame) in enumerate(last_eight):
        time = TAIL_START+index/FPS
        path = QA/f'ending-tail-{index:02d}.jpg'
        frame.save(path, quality=95)
        x,y=(j%4)*480,(j//4)*295
        sheet.paste(frame.resize((480,270)),(x,y))
        painter.text((x+5,y+275),f'tail {index:02d} / {time:.6f}s',fill='white')
        tail_images.append(dict(index=index,t=time,path=str(path)))
    sheet_path=QA/'ending-last-eight.jpg'
    sheet.save(sheet_path,quality=95)
    return dict(frame_count=count, unique_frames=unique,
                decoded_frame_sha256=hashes,
                first_frame_t=TAIL_START,
                final_frame_t=TAIL_START+(count-1)/FPS,
                neighbor_mae_255=differences,
                neighbor_mae_min_255=min(differences),
                neighbor_mae_mean_255=float(np.mean(differences)),
                neighbor_mae_max_255=max(differences),
                last_seven_neighbor_mae_255=last_seven,
                final_vs_first_mae_255=first_differences[-1],
                last_eight_stills=tail_images, last_eight_sheet=str(sheet_path))


def extract_samples(video: Path):
    samples=[]
    sheet=Image.new('RGB',(1920,780))
    painter=ImageDraw.Draw(sheet)
    for index,requested in enumerate(SAMPLES):
        frame_index=round(requested*FPS)
        actual=frame_index/FPS
        command=[FFMPEG,'-v','error','-ss',f'{actual:.9f}','-i',str(video),
                 '-map','0:v:0','-an','-sn','-dn','-frames:v','1',
                 '-f','rawvideo','-pix_fmt','rgb24','-']
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        require(result.returncode==0,
                f'Sample decode failed at {requested}s: {result.stderr[-2000:]}')
        require(len(result.stdout)==W*H*3,
                f'Sample {requested}s is missing or has an unexpected resolution')
        frame=Image.frombytes('RGB',(W,H),result.stdout)
        path=QA/f'ending-{index}.jpg'
        frame.save(path,quality=95)
        x,y=(index%3)*640,(index//3)*390
        sheet.paste(frame.resize((640,360)),(x,y))
        painter.text((x+5,y+365),
                     f'{requested:.3f}s requested / {actual:.6f}s frame',fill='white')
        samples.append(dict(requested_t=requested,frame_t=actual,
                            source_frame_index=frame_index,path=str(path)))
    path=QA/'ending-samples.jpg'
    sheet.save(path,quality=95)
    return dict(stills=samples,sheet=str(path))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,default=DEFAULT_VIDEO)
    args=parser.parse_args()
    video=args.video.resolve()
    require(video.is_file(),f'Rendered master does not exist: {video}')
    input_path=QA/'moving_tail_validation.json'
    require(input_path.is_file(),f'Raw input motion report missing: {input_path}')
    raw_motion=json.loads(input_path.read_text(encoding='utf-8-sig'))
    require(raw_motion.get('moving_tail_frames')==EXPECTED_FRAMES,
            f'Raw motion report needs exactly {EXPECTED_FRAMES} tail frames')
    require(raw_motion.get('unique_frames')==EXPECTED_FRAMES,
            f'Raw motion report needs {EXPECTED_FRAMES} genuinely unique input frames')
    require(raw_motion.get('freeze') is False,
            'Raw motion report still describes a frozen ending')
    require(raw_motion.get('no_titles_or_credit') is True,
            'Raw motion report must confirm no ending inscription')

    source=source_audit()
    tail=decoded_tail(video)
    samples=extract_samples(video)
    report=dict(status='PASS',checked_at_utc=datetime.now(timezone.utc).isoformat(),
                video=str(video),video_bytes=video.stat().st_size,
                raw_input_report_path=str(input_path),raw_input_motion=raw_motion,
                source_audit=source,encoded_tail=tail,samples=samples,
                note='No video re-encoding or OpenGL rendering performed.')
    path=QA/'encoded_ending_validation.json'
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(dict(status='PASS',encoded_tail_frames=tail['frame_count'],
                          encoded_unique_frames=tail['unique_frames'],
                          raw_unique_frames=raw_motion['unique_frames'],
                          neighbor_mae_255=[tail['neighbor_mae_min_255'],
                                            tail['neighbor_mae_mean_255'],
                                            tail['neighbor_mae_max_255']],
                          last_frame_motion_min_mae_255=min(tail['last_seven_neighbor_mae_255']),
                          report=str(path)),indent=2))


if __name__=='__main__':
    main()
