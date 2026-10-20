"""Read-only v14 shot coverage review; no OpenGL imports."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, json
import imageio_ffmpeg
from PIL import Image, ImageDraw
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
video=next((ROOT/'output_v14').glob('*.mp4'))
ff=imageio_ffmpeg.get_ffmpeg_exe()
groups=[
 ('opening', [0.6,3.7,7.0,11.8,15.2]),
 ('eyes breath', [34.7,36.4,36.8,37.4,38.0]),
 ('compute', [54.7,57.7,63.3,66.8,69.8]),
 ('safe breath', [71.9,72.7,73.1,73.5,73.82]),
 ('CDR breath', [86.8,88.4,88.8,89.3,89.8]),
 ('factory after', [98.35,99.4,100.7,102.0,103.6]),
 ('transformer', [109.6,110.4,111.4,112.5,113.6]),
 ('disobey', [114.2,114.8,115.3,116.2,117.4]),
 ('GPU breath', [119.4,121.2,122.7,123.4,123.8]),
 ('unknown breath', [133.7,135.3,135.95,136.3,136.8]),
 ('show handoff', [137.4,138.4,139.3,140.4,141.1]),
]
def get(t):
    raw=subprocess.run([ff,'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=384:216','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
    im=Image.frombytes('RGB',(384,216),raw)
    arr=np.array(im)
    occupied=(arr.max(axis=2)>28).reshape(6,36,8,48).mean(axis=(1,3))
    return t,im,{'luma_occupied':float((arr.max(axis=2)>28).mean()), 'occupied_tiles_48':int((occupied>.025).sum())}
times=[t for _,ts in groups for t in ts]
with ThreadPoolExecutor(max_workers=4) as ex: samples={t:(im,stats) for t,im,stats in ex.map(get,times)}
sheet=Image.new('RGB',(1920,len(groups)*246),(6,8,12)); d=ImageDraw.Draw(sheet)
audit=[]
for row,(name,ts) in enumerate(groups):
    for col,t in enumerate(ts):
        im,stats=samples[t]
        sheet.paste(im,(col*384,row*246))
        d.text((col*384+7,row*246+219),f'{name} {t:.2f}s {stats["occupied_tiles_48"]}/48 tiles',fill='white')
        audit.append({'name':name,'time':t,**stats})
sheet.save(ROOT/'v15/gap_contacts.jpg',quality=92)
(ROOT/'v15/gap_metrics.json').write_text(json.dumps(audit,indent=2))
print(ROOT/'v15/gap_contacts.jpg')
