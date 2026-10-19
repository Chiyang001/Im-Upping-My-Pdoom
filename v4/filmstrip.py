import pathlib,subprocess,imageio_ffmpeg
from PIL import Image,ImageDraw
ff=imageio_ffmpeg.get_ffmpeg_exe()
for start in [20,80,115]:
 dest=pathlib.Path(f'v4/check-{start}');dest.mkdir(exist_ok=True)
 subprocess.run([ff,'-v','error','-y','-i',f'v4/sample-{start}.mp4','-vf','fps=3,scale=480:270',str(dest/'f-%03d.jpg')],check=True)
 files=sorted(dest.glob('*.jpg'));sheet=Image.new('RGB',(1920,6*290));d=ImageDraw.Draw(sheet)
 for i,f in enumerate(files):
  x=i%4*480;y=i//4*290;sheet.paste(Image.open(f),(x,y));d.text((x+5,y+272),f'{start+i/3:.2f}',fill='white')
 sheet.save(f'v4/filmstrip-{start}.jpg')
