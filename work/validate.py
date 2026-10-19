import subprocess,pathlib,imageio_ffmpeg,json
from PIL import Image,ImageDraw
ff=imageio_ffmpeg.get_ffmpeg_exe();out='output/Pdoom_Machine_Theatre_Final.mp4';src=str(next(pathlib.Path('.').glob('*.mp4')))
r=subprocess.run([ff,'-v','error','-i',out,'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0 and not r.stderr,r.stderr
hashes=[]
for f in [src,out]:
 h=subprocess.run([ff,'-v','error','-i',f,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],capture_output=True,text=True);hashes.append(h.stdout.strip())
assert hashes[0]==hashes[1],hashes
meta=subprocess.run([ff,'-i',out],capture_output=True,text=True).stderr
pathlib.Path('work/validation.txt').write_text('FULL DECODE: PASS\nAUDIO BITSTREAM MATCH: PASS\n'+hashes[0]+'\n'+meta,encoding='utf-8')
for t in [24,117,155]:subprocess.run([ff,'-v','error','-y','-ss',str(t),'-i',out,'-frames:v','1',f'work/final-{t}.jpg'],check=True)
print('Full decode passed; original audio SHA256 matches.');print(meta[meta.index('Duration:'):meta.index('Duration:')+430])
