from pathlib import Path
s=Path('code3d/render.py').read_text(encoding='utf-8');s=s[:s.index('font=TTFont')];s=s.replace('W,H=1920,1080;FPS=30;DUR=156.667','W,H=1920,1080;FPS=30;DUR=156.667')
Path('v4/engine.py').write_text(s,encoding='utf-8')
