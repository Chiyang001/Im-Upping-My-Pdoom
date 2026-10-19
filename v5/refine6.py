from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8-sig');s=s.replace('th=gx/20+math.pi/2;rr=9+v[1];v[0]=rr*math.cos(th);v[1]=rr*math.sin(th)-6;v[2]=v[2]*.3','th=math.pi/2-gx/23;rr=13.5+v[1];v[0]=rr*math.cos(th);v[1]=rr*math.sin(th)-12.8;v[2]=v[2]*.3');s=s.replace("dim=1-.78*ease((t-rowend-.25)/.75)","dim=1-.78*ease((t-rowend-(.08 if i==10 else .25))/(.45 if i==10 else .75))")
p.write_text(s,encoding='utf-8')
