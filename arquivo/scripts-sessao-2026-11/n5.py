import numpy as np, soundfile as sf
from scipy import signal
a,fs=sf.read('/home/claude/n/in.wav'); M=a.mean(1); S=(a[:,0]-a[:,1])/2
def lev(x,lo,hi,w=fs//50):
    y=signal.sosfiltfilt(signal.butter(6,[lo,hi],'bandpass',fs=fs,output='sos'),x); k=len(y)//w
    return 10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-16)
print('spread p95-p5 (dB) of 20ms level, early(0-30s) vs late(140-170s); small spread = steady layer')
for lo,hi in [(1000,4000),(4000,8000),(8000,12000),(12000,15000),(15000,21000)]:
    l=lev(M,lo,hi); e=l[0:1500]; L=l[7000:8500]
    print(f'{lo}-{hi}: early {np.percentile(e,95)-np.percentile(e,5):.1f} (p50 {np.median(e):.0f}) | late {np.percentile(L,95)-np.percentile(L,5):.1f} (p50 {np.median(L):.0f})')
# correlation of 15-21k envelope with 2-8k envelope late (does it follow music?)
h=lev(M,15000,21000,fs//20); m=lev(M,2000,8000,fs//20)
for s0,s1 in [(0,600),(2800,3400)]:
    print('env corr 15-21k vs 2-8k',s0/20,'s:',round(np.corrcoef(h[s0:s1],m[s0:s1])[0,1],2))
