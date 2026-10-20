"""Extract actual encoded semantic actions without changing production sources."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
video=Path(sys.argv[1]) if len(sys.argv)>1 else next((ROOT/'output_v15').glob('*.mp4'))
plan=json.loads((ROOT/'v15/qa_metaphor_review_plan.json').read_text())
ff=imageio_ffmpeg.get_ffmpeg_exe()
sheet=Image.new('RGB',(4*480,len(plan)*296),(0,0,0)); draw=ImageDraw.Draw(sheet)
audit=[]
for row,item in enumerate(plan):
    times=item['times']
    chosen=[times[0],times[1],times[-2],times[-1]]
    for col,t in enumerate(chosen):
        raw=subprocess.run([ff,'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
        assert len(raw)==480*270*3,(t,len(raw))
        im=Image.frombytes('RGB',(480,270),raw)
        sheet.paste(im,(col*480,row*296))
        draw.text((col*480+6,row*296+273),f"{item['name']} / {t:.3f}s",fill='white')
        audit.append({'scene':item['name'],'time':t,'pixels':len(raw)})
path=ROOT/'v15/qa_encoded_metaphors.jpg';sheet.save(path,quality=94)
(ROOT/'v15/qa_encoded_metaphors.json').write_text(json.dumps({'video':str(video),'samples':audit},indent=2))
print(path)
