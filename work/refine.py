from pathlib import Path
p=Path('work/render_mv.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace("txt(d,(1220,213)","txt(d,(1220,160)")
s=s.replace("x=650+j*30", "x=610+j*25")
start=s.index(' # integrate full lyric');end=s.index(' # concept-specific motion')
s=s[:start]+''' # Lyrics are separate scenic treatments: hanging banners, poster, monumental type, skewed signage, and floor inscriptions.
 parts=lyric.split('|');cursor=0
 for j,s in enumerate(parts):
  count=len(s.split());tt=times[cursor:cursor+count];cursor+=count
  maxw=1080;fs=80 if len(parts)==1 else 67
  if mode==0 and not chorus:maxw=760;fs=91
  if mode==2 and not chorus:maxw=1130;fs=92
  if mode==4 and not chorus:maxw=1000;fs=86
  layer=phrase_layer(s,tt,t,maxw,fs,IV,SERIF if idx in (8,26,33) else FONT)
  enter=min(1,max(0,(t-a)*3));ease=1-(1-enter)**3
  x=65+int((1-ease)*70);y=390+j*100
  if chorus:
   x=65+j*85;y=365+j*100
  elif mode==0:
   x=100+j*150;y=335+j*115
  elif mode==1:
   x=60+j*60;y=410+j*95
  elif mode==2:
   x=65;y=365+j*110
  elif mode==3:
   x=70+j*60;y=340+j*120
  else:
   x=90+j*60;y=370+j*120
  if mode in (1,3) or chorus:
   plate=Image.new('RGBA',(min(layer.width+30,1160),layer.height+16),(7,15,43,220));pd=ImageDraw.Draw(plate);pd.rectangle((0,0,5,plate.height),fill=RED);plate.alpha_composite(layer,(18,3))
  else:
   # cast shadow makes the words read as dimensional objects in the stage light
   alpha=layer.getchannel('A');shadow=Image.new('RGBA',layer.size,(0,0,0,0));shadow.putalpha(alpha);shadow=shadow.filter(ImageFilter.GaussianBlur(6));im.alpha_composite(shadow,(x+4,y+7));plate=layer
  if mode==3:plate=plate.rotate(7 if j==0 else -5,resample=Image.Resampling.BICUBIC,expand=True)
  elif mode==4:plate=plate.rotate(-4,resample=Image.Resampling.BICUBIC,expand=True)
  im.alpha_composite(plate,(x,y))
''' +s[end:]
s=s.replace("return im.convert('RGB')", "base=Image.new('RGBA',(W,H),(3,7,18,255));base.alpha_composite(im);return base.convert('RGB')")
p.write_text(s,encoding='utf-8')
