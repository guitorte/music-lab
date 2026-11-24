import numpy as np, soundfile as sf
from scipy import signal
import sys
a,fs=sf.read('/home/claude/n/in.wav'); b,_=sf.read(sys.argv[1] if len(sys.argv)>1 else '/home/claude/n/clean.wav')
def bandlev(x,lo,hi):
    y=signal.sosfiltfilt(signal.butter(6,[lo,hi],'bandpass',fs=fs,output='sos'),x.mean(1)); w=fs//50; k=len(y)//w
    return 10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-16)
for lo,hi in [(1000,4000),(4000,8000),(8000,15000),(16500,20500)]:
    la=bandlev(a,lo,hi); lb=bandlev(b,lo,hi); W=50*15
    print(f'{lo}-{hi}  p5 floor before→after per 15s:', ' '.join(f'{np.percentile(la[i:i+W],5):.0f}→{np.percentile(lb[i:i+W],5):.0f}' for i in range(0,len(la)-W+1,W*2)))
    loud=la>np.percentile(la,90); print('        loudest-10% frames change (music loss) dB:',round(float(np.median(lb[loud]-la[loud])),1))
