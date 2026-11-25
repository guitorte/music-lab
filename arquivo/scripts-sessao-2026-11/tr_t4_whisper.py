import json, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=2)
import librosa
x,fs=sf.read('/home/claude/traicao/stems/vocals (3).flac',dtype='float32'); a=librosa.resample(x.mean(1),orig_sr=fs,target_sr=16000)
seg,_=m.transcribe(a,language='pt',vad_filter=True,beam_size=1)
L=[[s.start,s.end,s.text.strip()] for s in seg]
json.dump({'lines':L},open('/home/claude/traicao/whisper.json','w'),ensure_ascii=False)
print(len(L),'linhas')
