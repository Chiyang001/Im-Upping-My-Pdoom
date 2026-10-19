from PIL import Image
from pathlib import Path
import numpy as np,json
from scipy.io import wavfile
from scipy.signal import butter,sosfilt,find_peaks
im=Image.open('assets/theatre-atlas-2.png');w,h=im.size
for j in range(4):im.crop((round(j%2*w/2),round(j//2*h/2),round((j%2+1)*w/2),round((j//2+1)*h/2))).save(f'assets/scene-{9+j:02}.png')
sr,x=wavfile.read('work/audio.wav');x=sosfilt(butter(3,[35,180],fs=sr,btype='bandpass',output='sos'),x.astype(float));n=160;env=np.sqrt(np.mean(x[:len(x)//n*n].reshape(-1,n)**2,axis=1));onset=np.maximum(0,np.diff(env,prepend=env[0]));peaks,_=find_peaks(onset,distance=24,prominence=np.percentile(onset,75)*.6);json.dump((peaks/100).tolist(),open('work/beats.json','w'))
p=Path('work/render_mv.py');s=p.read_text(encoding='utf-8');s=s.replace('range(9)]','range(13)]');s=s.replace("lines=json.load(open('work/lyrics.json'));trans=", "beats=np.array(json.load(open('work/beats.json')))\nlines=json.load(open('work/lyrics.json'));trans=")
s=s.replace("beat=max(0,1-((t-0.18)%(.42857))/.13)","past=beats[beats<=t];beat=max(0,1-(t-past[-1])/.15) if len(past) else 0")
s=s.replace("im0=imgs[asset]", "asset={0:9,5:10,18:11,20:10,27:11,28:10,31:11}.get(idx,asset)\n if outro:asset=12\n im0=imgs[asset]")
s=s.replace("'VISUAL DIRECTION / CHIYANG001'", "'VISUAL DIRECTION / CHIYANG001'")
p.write_text(s,encoding='utf-8')
