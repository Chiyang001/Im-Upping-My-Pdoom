import sys
sys.path.insert(0,'v4')
import render
from PIL import Image
for t in [3.7,4.0,4.25,15.65,82.95,123,153,155.7]:
 im=Image.frombytes('RGB',(render.W,render.H),render.drawframe(t)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.save(f'v4/check-{t}.jpg')
print('AGI',[(a[1],a[2]) for a in render.rows[0][1][0]])
