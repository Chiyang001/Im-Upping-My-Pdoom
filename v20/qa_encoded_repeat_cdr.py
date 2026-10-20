"""Read-only Repeat/CDR samples from the FINISHED v20 MP4, without OpenGL.

Run only after encoding completes. A single FFmpeg decode selects sixteen
source frames between 74 and 90 seconds. Four native 1080p details support
visual review of rail retracing, the physical word pass, shared CDR supports
and actual viewpoint parallax. Reports do not auto-claim an aesthetic pass.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_VIDEO=ROOT/'output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4'
PLAN=(('same neural rail',(74.15,74.8,75.35,76.05)),
      ('reverse and repeated launch',(76.25,76.55,76.9,77.18)),
      ('single mounted cons spine',(84.95,85.55,86.,86.75)),
      ('tail selection and departure',(87.3,88.1,88.85,89.6)))
NATIVE_TIMES=(76.9,77.18,86.,88.85)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video',type=Path,nargs='?',default=DEFAULT_VIDEO)
    args=parser.parse_args()
    video=args.video.expanduser().resolve(strict=True)
    bytes_before=video.stat().st_size
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    metadata=subprocess.run([ff,'-hide_banner','-i',str(video)],capture_output=True,
                            encoding='utf-8',errors='replace').stderr
    duration_match=re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)',metadata)
    fps_match=re.search(r'(\d+(?:\.\d+)?)\s+fps',metadata)
    if not duration_match or 'Video:' not in metadata:
        raise RuntimeError('MP4 is not finalized/readable: '+metadata[-1000:])
    h,m,s=map(float,duration_match.groups());duration=h*3600+m*60+s
    fps=float(fps_match.group(1)) if fps_match else 0.
    if duration<156.6 or abs(fps-30)>1e-6:
        raise RuntimeError('Expected finished 156.667 s / 30 fps v20 master')
    width,height=960,540
    start=73.
    times=[t for _,group in PLAN for t in group]
    frames=[int(math.ceil(t*fps-1e-7)) for t in times]
    relative=[f-int(start*fps) for f in frames]
    select='+'.join(f'eq(n\\,{f})' for f in relative)
    cmd=[ff,'-v','error','-ss',str(start),'-i',str(video),'-map','0:v:0',
         '-an','-sn','-t','17','-vf',f'select={select},scale={width}:{height}:flags=lanczos',
         '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-threads','1','-']
    proc=subprocess.run(cmd,capture_output=True,check=True)
    size=width*height*3
    if len(proc.stdout)!=size*len(times):
        raise RuntimeError(f'Expected {len(times)} selected frames, got {len(proc.stdout)/size}')
    images=[Image.frombytes('RGB',(width,height),proc.stdout[i*size:(i+1)*size])
            for i in range(len(times))]
    sheet=Image.new('RGB',(1920,len(PLAN)*296),(4,7,11));draw=ImageDraw.Draw(sheet)
    samples=[]
    for row,(label,group) in enumerate(PLAN):
        for col,t in enumerate(group):
            i=row*4+col;frame=frames[i];im=images[i]
            sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(480*col,296*row))
            draw.text((480*col+6,296*row+274),f'{label}: {frame/fps:.3f}s',fill='white')
            samples.append(dict(label=label,requested_time=t,frame=frame,time=frame/fps,
                                sha256=hashlib.sha256(im.tobytes()).hexdigest()))
    sheet_path=ROOT/'v20/qa_encoded_repeat_cdr.jpg';sheet.save(sheet_path,quality=95)
    for page in range(2):
        sheet.crop((0,page*592,1920,(page+1)*592)).save(
            ROOT/'v20'/f'qa_encoded_repeat_cdr_page_{page+1}.jpg',quality=95)
    def extract_native(t):
        frame=int(math.ceil(t*fps-1e-7));timestamp=frame/fps
        raw=subprocess.run([ff,'-v','error','-ss',str(timestamp),'-i',str(video),
            '-map','0:v:0','-an','-sn','-frames:v','1','-pix_fmt','rgb24','-f',
            'rawvideo','-threads','1','-'],capture_output=True,check=True).stdout
        if len(raw)!=1920*1080*3:raise RuntimeError('Not a 1920x1080 master')
        destination=ROOT/'v20'/f'encoded-repeat-cdr-{t:.3f}.jpg'
        Image.frombytes('RGB',(1920,1080),raw).save(destination,quality=95)
        return dict(requested_time=t,frame=frame,time=timestamp,path=str(destination),
                    sha256=hashlib.sha256(raw).hexdigest())
    with ThreadPoolExecutor(max_workers=2) as pool:
        native=list(pool.map(extract_native,NATIVE_TIMES))
    bytes_after=video.stat().st_size
    if bytes_before!=bytes_after:
        raise RuntimeError('Source video changed during review; wait for encoding completion')
    report=dict(video=str(video),video_bytes=bytes_after,duration=duration,fps=fps,
                source='actual_encoded_mp4',sample_count=len(samples),samples=samples,
                native=native,visual_verdict='pending visual inspection')
    (ROOT/'v20/qa_encoded_repeat_cdr.json').write_text(
        json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(sheet_path)
    print('16 encoded samples and 4 native details; visual review pending')


if __name__=='__main__':main()
