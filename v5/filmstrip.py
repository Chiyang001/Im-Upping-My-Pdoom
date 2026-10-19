from PIL import Image,ImageDraw
import pathlib,subprocess,imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
for start in [18,90]:
 dest=pathlib.Path(f'v5/strip-{start}');dest.mkdir(exist_ok=True)
 subprocess.run([ff,'-v','error','-y','-i',f'v5/sample-{start}.mp4','-vf','fps=2,scale=480:270',str(dest/'f-%03d.jpg')],check=True)
 sheet=Image.new('RGB',(1920,6*290));d=ImageDraw.Draw(sheet)
 for i,p in enumerate(sorted(dest.glob('*.jpg'))):
  x=i%4*480;y=i//4*290;sheet.paste(Image.open(p),(x,y));d.text((x+5,y+272),f'{start+i*.5:.2f}',fill='white')
 sheet.save(f'v5/filmstrip-{start}.jpg')
