import subprocess,pathlib,imageio_ffmpeg
from PIL import Image,ImageDraw
f=next(pathlib.Path('.').glob('*.mp4')); ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-i',str(f),'-vn','-ar','16000','-ac','1','work/audio.wav'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run([ff,'-y','-i',str(f),'-vf','fps=1/5,scale=384:216','work/ref_%03d.jpg'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
files=list(pathlib.Path('work').glob('ref_*.jpg')); sheet=Image.new('RGB',(384*4,240*8))
d=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
 x=(i%4)*384;y=(i//4)*240;sheet.paste(Image.open(p),(x,y));d.text((x+8,y+218),str(i*5)+'s',fill='white')
sheet.save('work/reference.jpg')
