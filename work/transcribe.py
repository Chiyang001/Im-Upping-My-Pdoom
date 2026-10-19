from faster_whisper import WhisperModel
import json
m=WhisperModel('small',device='cpu',compute_type='int8',local_files_only=True)
segs,info=m.transcribe(__import__('scipy.io.wavfile',fromlist=['read']).read('work/audio.wav')[1].astype('float32')/32768,language='en',word_timestamps=True,beam_size=5,initial_prompt='AGI training loss ChatGPT P doom foom Chinese room shoggoth Shinigami Sydney basilisk NVDA Omega FLOPS MLP von Neumann CDR Gato paperclips orthogonality Chinchilla GPU RLHF Ilya Loom')
a=[]
for s in segs:
 a.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word} for w in s.words]});print(s.start,s.end,s.text,flush=True)
json.dump(a,open('work/transcript.json','w'),indent=2)
