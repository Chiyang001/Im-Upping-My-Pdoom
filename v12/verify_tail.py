import hashlib,json,subprocess
from pathlib import Path
import imageio_ffmpeg,numpy as np
from PIL import Image

video=Path('output_v12/Im_Upping_My_Pdoom_Flight_1080p.mp4')
ff=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ff,'-v','error','-ss','154.6','-i',str(video),'-an','-f','rawvideo','-pix_fmt','rgb24','-']
raw=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,1080,1920,3)
reference=frames[0].astype(np.int16)
differences=[float(np.abs(frame.astype(np.int16)-reference).mean()) for frame in frames]
Image.fromarray(frames[len(frames)//2]).save('v12/final-frame.jpg')
report={'encoded_frames_in_hold':len(frames),'max_mean_absolute_pixel_difference_255':max(differences),'input_hold':json.loads(Path('v12/freeze_validation.json').read_text()),'video_bytes':video.stat().st_size}
Path('v12/encoded_freeze_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert len(frames)==62
assert max(differences)<.30
