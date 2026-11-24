import sys, soundfile as sf, numpy as np
from scipy import signal
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[2],device='cpu',compute_type='int8')
x,fs=sf.read(sys.argv[1]); x=signal.resample_poly(x.mean(1),1,3).astype(np.float32)
segs,_=m.transcribe(x,language='pt',word_timestamps=True,vad_filter=False,beam_size=5,initial_prompt='Tá pegando todo mundo, tá sem namorado. Tá virada no diabo. Se for de casal melhor é já evitar.')
for s in segs:
    print('%.2f-%.2f |'%(s.start,s.end),' '.join(f'{w.word.strip()}[{w.start:.2f}]' for w in s.words))
