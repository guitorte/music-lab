import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); ins,_=sf.read(D+'Instrumental.wav')
s=slice(int(92*fs),int(104.5*fs))
f,C=signal.coherence(mix[s,0],(voc[s,0]+ins[s,0]),fs,nperseg=4096)
print('coherence mix vs voc+ins:',' '.join(f'{c}:{np.mean(C[(f>=c/1.4)&(f<c*1.4)]):.2f}' for c in [100,300,1000,2000,4000,8000,14000]))
f,C=signal.coherence(mix[s,0],voc[s,0],fs,nperseg=4096)
print('coherence mix vs voc    :',' '.join(f'{c}:{np.mean(C[(f>=c/1.4)&(f<c*1.4)]):.2f}' for c in [100,300,1000,2000,4000,8000,14000]))
