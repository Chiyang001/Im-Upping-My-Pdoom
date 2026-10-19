import pathlib,subprocess,imageio_ffmpeg
from PIL import Image,ImageDraw
ff=imageio_ffmpeg.get_ffmpeg_exe();src=str(next(pathlib.Path('.').glob('*.mp4')));out='output_v4/Pdoom_Line_Architecture_1080p.mp4'
times=[4.5,11.7,24.7,31.4,51.8,67.5,82.9,97.9,107.6,117.9,122.1,127.3]
for block in range(2):
 sh=Image.new('RGB',(1920,1440));d=ImageDraw.Draw(sh)
 for j,t in enumerate(times[block*6:block*6+6]):
  for k,file in enumerate([src,out]):
   dest=f'v4/compare-{block}-{j}-{k}.jpg';subprocess.run([ff,'-v','error','-y','-ss',str(t),'-i',file,'-frames:v','1','-vf','scale=640:360',dest],check=True)
   x=j%3*640;y=j//3*720+k*360;sh.paste(Image.open(dest),(x,y));d.text((x+8,y+8),('REFERENCE / ' if k==0 else 'V4 / ')+str(t),fill='white')
 sh.save(f'v4/comparison-{block}.jpg')
