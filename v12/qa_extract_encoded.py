import subprocess,io,json
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();v=Path('output_v12/Im_Upping_My_Pdoom_Flight_1080p.mp4')
if not v.exists():raise SystemExit('not ready')
plan=[('PDOOM 1',23.62,23.985),('PDOOM 2',59.985,60.245),('PDOOM 3',96.335,96.625),('PDOOM 4',125.46,125.805)]
sheet=Image.new('RGB',(1920,4*292));d=ImageDraw.Draw(sheet);items=[]
for row,(name,at,cross) in enumerate(plan):
 for col,t in enumerate([at+.15,cross-.045,cross+.025,cross+.70]):
  proc=subprocess.run([ff,'-hide_banner','-loglevel','error','-ss',f'{t:.6f}','-i',str(v),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
  im=Image.open(io.BytesIO(proc.stdout)).convert('RGB');out=Path(f'v12/qa_encoded_flight_{row}_{col}.jpg');im.save(out,quality=92)
  x=col*480;y=row*292;sheet.paste(im.resize((480,270)),(x,y));d.text((x+4,y+274),f'{name} t={t:.3f}',fill='white');items.append({'name':name,'time':t,'file':str(out)})
sheet.save('v12/qa_encoded_flight_sheet.jpg',quality=92)
proc=subprocess.run([ff,'-hide_banner','-loglevel','error','-ss','155.3','-i',str(v),'-frames:v','1','-f','image2pipe','-vcodec','png','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
Image.open(io.BytesIO(proc.stdout)).convert('RGB').save('v12/qa_encoded_final_hold.jpg',quality=95)
Path('v12/qa_encoded_flight_plan.json').write_text(json.dumps(items,indent=2))
print('encoded frame samples ready')
