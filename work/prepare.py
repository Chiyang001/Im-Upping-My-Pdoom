import json
p='work/lyrics.json';a=json.load(open(p));starts=[1.42,5.58,9.08,12.94,16.2,22.2,26.06,29.68,31.78,38.12,41.16,44.72,48.64,52.56,58.4,62.34,65.94,68.2,73.96,77.34,80.68,84.72,89.86,94.86,98.7,102.32,104.54,109.4,115.,118.7,124.04,127.9,131.46,136.9]
for i,r in enumerate(a):
 r[0]=starts[i];r[1]=starts[i+1] if i+1<len(a) else 141.2
for i,e in [(8,36.5),(17,72.9),(21,88.8),(29,123.3),(32,135.9)]:a[i][1]=e
json.dump(a,open(p,'w'),indent=2)
from PIL import Image
im=Image.open('assets/theatre-atlas.png');w,h=im.size
for i in range(9): im.crop((round(i%3*w/3),round(i//3*h/3),round((i%3+1)*w/3),round((i//3+1)*h/3))).save(f'assets/scene-{i:02}.png')
