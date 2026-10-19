from pathlib import Path
p=Path('v5/render.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("('begun',14,0,-3,-5,0,0,0)","('begun',12,0,-4.6,-5,0,0,0)")
s=s.replace("ctx.line_width=1.75 if age>=0 and age<.4 else 1.45\n   if not ghost", "ctx.line_width=1.75 if age>=0 and age<.4 else 1.45\n   translucent=not ghost and (age<-.035 or dim<.6)\n   if translucent:ms.depth_mask=False;ctx.enable(gl.BLEND);ctx.blend_func=(gl.ONE,gl.ONE)\n   if not ghost")
s=s.replace("else:gpu.draw(wm,vp,t,hit,gain=level)\n ctx.line_width=1.2", "else:gpu.draw(wm,vp,t,hit,gain=level)\n   if translucent:ms.depth_mask=True;ctx.disable(gl.BLEND)\n ctx.line_width=1.2")
p.write_text(s,encoding='utf-8')
