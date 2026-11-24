import sys, soundfile as sf, numpy as np
from scipy import signal
from faster_whisper import WhisperModel
x,fs=sf.read('/home/claude/cc/src.wav'); print('fs',fs,'dur %.2f'%(len(x)/fs))
m=WhisperModel('medium',device='cpu',compute_type='int8')
z=signal.resample_poly(x.mean(1),1,fs//16000 if fs%16000==0 else 1).astype(np.float32) if fs%16000==0 else signal.resample_poly(x.mean(1),160,441).astype(np.float32)
segs,_=m.transcribe(z,language='pt',word_timestamps=True,beam_size=5)
for s in segs: print('%6.2f-%6.2f | %s'%(s.start,s.end,s.text.strip()))
