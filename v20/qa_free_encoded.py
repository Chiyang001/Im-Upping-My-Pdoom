"""Extract 24 actual encoded FREE frames; inspect images before verdict."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4'
PLAN=(
    ('blow_1',(1691,1692,1695)),
    ('blow_2',(1698,1699,1702)),
    ('blow_3',(1705,1706,1709)),
    ('blow_4',(1712,1713,1716)),
    ('blow_5',(1718,1719,1722)),
    ('blow_6',(1725,1726,1729)),
    ('final_break',(1732,1733,1735)),
    ('debris_flight',(1739,1743,1747)),
)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video',nargs='?',type=Path,default=DEFAULT)
    args=parser.parse_args();video=args.video.resolve(strict=True)
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    def extract(frame):
        t=frame/30
        proc=subprocess.run([ff,'-v','error','-ss',f'{t:.9f}','-i',str(video),
                             '-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        assert len(proc.stdout)==1920*1080*3,(t,len(proc.stdout))
        a=np.frombuffer(proc.stdout,np.uint8).reshape(1080,1920,3)
        im=Image.fromarray(a)
        path=ROOT/f'v20/qa_free_encoded_{frame}.jpg'
        im.save(path,quality=94)
        return frame,im,dict(frame=frame,requested_seconds=t,full_hd=str(path),
                             rgb_sha256=hashlib.sha256(proc.stdout).hexdigest(),
                             clipped_white_fraction=float((a.min(2)>245).mean()))
    frames=[f for _,row in PLAN for f in row]
    with ThreadPoolExecutor(max_workers=4) as pool:
        result={f:(im,data) for f,im,data in pool.map(extract,frames)}
    sheet=Image.new('RGB',(1920,8*388),(4,7,11));d=ImageDraw.Draw(sheet)
    samples=[]
    for row,(name,frames) in enumerate(PLAN):
        for col,frame in enumerate(frames):
            im,data=result[frame];x=col*640;y=row*388
            sheet.paste(im.resize((640,360)),(x,y))
            d.text((x+8,y+365),f'{name} / {frame/30:.3f}s / frame {frame}',fill='white')
            samples.append(dict(group=name,**data))
    sheet.save(ROOT/'v20/qa_free_encoded.jpg',quality=94)
    for j,start in enumerate((0,3,6),1):
        sheet.crop((0,start*388,1920,min(8,start+3)*388)).save(
            ROOT/f'v20/qa_free_encoded_page_{j}.jpg',quality=94)
    report=dict(video=str(video),video_bytes=video.stat().st_size,
                source='Actual encoded MP4 decoded with FFmpeg',
                sample_count=len(samples),samples=samples,
                visual_verdict='pending image inspection')
    (ROOT/'v20/qa_free_encoded.json').write_text(
        json.dumps(report,indent=2),encoding='utf8')
    print('24 actual encoded frames extracted; visual review pending')


if __name__=='__main__':main()
