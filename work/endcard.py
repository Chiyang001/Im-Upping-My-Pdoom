import subprocess,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1920,1080),(3,7,18));d=ImageDraw.Draw(im)
def text(y,s,size,font='arialbd.ttf',color=(244,237,217)):
 d.text((960,y),s,font=ImageFont.truetype('C:/Windows/Fonts/'+font,size),fill=color,anchor='mm')
d.line((820,330,1100,330),fill=(244,58,38),width=4)
text(425,'THE LAST MACHINE THEATRE',54);text(520,'P(doom)',72,'timesi.ttf');text(640,'VISUAL DIRECTION / CHIYANG001',24,'consola.ttf');text(695,'MUSIC / ORIGINAL SOURCE AUDIO',22,'consola.ttf')
im.save('assets/endcard.png')
ff=imageio_ffmpeg.get_ffmpeg_exe()
p=subprocess.run([ff,'-y','-i','output/Pdoom_Machine_Theatre_1080p.mp4','-i','assets/endcard.png','-filter_complex',"[0:v][1:v]overlay=0:0:enable='gte(t,153)'[v]",'-map','[v]','-map','0:a','-c:v','libx264','-preset','veryfast','-crf','18','-c:a','copy','-movflags','+faststart','output/Pdoom_Machine_Theatre_Final.mp4'],stdout=subprocess.DEVNULL,stderr=open('work/finalize.log','w'))
assert p.returncode==0
