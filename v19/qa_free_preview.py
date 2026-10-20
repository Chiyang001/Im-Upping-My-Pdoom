"""Render repeated-contact and all-cell-fracture contact sheet for review."""
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qa_free_renderer', ROOT/'v19/render.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

TIMES = [56.30, 56.40, 56.52, 56.635, 56.86,
         57.09, 57.315, 57.545, 57.63, 57.765,
         57.82, 57.90, 57.97, 58.10, 58.25]
rows=[]
sheet=Image.new('RGB', (1920, 3*385))
d=ImageDraw.Draw(sheet)
for j,t in enumerate(TIMES):
    a=np.frombuffer(r.drawframe(t),np.uint8).reshape(r.H,r.W,3)
    im=Image.fromarray(a).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    path=ROOT/f'v19/qa_free_{t:.3f}.jpg'
    im.save(path,quality=94)
    x=j%5*384;y=j//5*385
    sheet.paste(im.resize((384,216)),(x,y))
    s=r.sample_free_impact(t)
    d.text((x+7,y+222),f'{t:.3f} / blow {s["strike_index"]+1}',fill='white')
    d.text((x+7,y+240),f'damage {s["damage"]:.2f} / split {s["breakage"]:.2f}',fill='white')
    rows.append(dict(t=t,full_hd=str(path),strike=s['strike'],damage=s['damage'],
                     broken=s['breakage'],lit_pixel_fraction=float((a.max(2)>35).mean()),
                     clipped_white_fraction=float((a.min(2)>245).mean())))
sheet.save(ROOT/'v19/qa_free_preview.jpg',quality=94)
(ROOT/'v19/qa_free_preview.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('Saved 15 full-HD frames and v19/qa_free_preview.jpg',flush=True)
