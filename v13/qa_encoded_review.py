"""Extract encoded video frames for independent final visual review."""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
VIDEO=ROOT/'output_v13/Im_Upping_My_Pdoom_Seismic_Flight_1080p.mp4'
FF=imageio_ffmpeg.get_ffmpeg_exe()
groups={
    'go':[94.30,94.60,94.7333333,94.7666667,94.80,94.8333333,95.23,95.435,95.68,95.86,95.9333333,96.40],
    'outro':[141.595,142.96,144.32,145.685,147.06,148.415,149.775,151.14,152.505,153.415,154.0,154.6],
}
for name,times in groups.items():
    sheet=Image.new('RGB',(1920,3*302))
    draw=ImageDraw.Draw(sheet)
    for n,t in enumerate(times):
        cmd=[FF,'-v','error','-ss',str(t),'-i',str(VIDEO),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']
        data=subprocess.run(cmd,check=True,stdout=subprocess.PIPE).stdout
        image=Image.frombytes('RGB',(1920,1080),data)
        x=n%4*480;y=n//4*302
        sheet.paste(image.resize((480,270)),(x,y))
        draw.text((x+5,y+273),f'{name} / {t:.3f}s',fill='white')
    path=ROOT/f'v13/qa_encoded_{name}.jpg'
    sheet.save(path,quality=94)
    print(path)
