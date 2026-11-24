import numpy as np, soundfile as sf, pyloudnorm as pyln, sys
from scipy import signal
D='/home/claude/a/'; names=['original','universal','fire','clarity','tape']
X={n:sf.read(D+n+'.wav')[0] for n in names}; fs=48000
o=X['original']
# alignment
for n in names[1:]:
    a=o[:fs*10,0]; b=X[n][:fs*10,0]
    c=signal.correlate(b,a,mode='full',method='fft'); lag=np.argmax(np.abs(c))-(len(a)-1)
    print(n,'lag samples',lag)
meter=pyln.Meter(fs)
def stats(x):
    m=x.mean(1); pk=np.abs(x).max(); rms=np.sqrt((x**2).mean())
    return 20*np.log10(pk), 20*np.log10(pk/rms)
print('\nname  LUFS  samplePeak  crest(dB)')
for n in names:
    L=meter.integrated_loudness(X[n]); p,cr=stats(X[n]); print(f'{n:9s} {L:6.1f} {p:6.2f} {cr:6.2f}')
