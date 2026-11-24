import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
D='/home/claude/a/'; names=['original','universal','fire','clarity','tape']; fs=48000; LAG=48
X={n:sf.read(D+n+'.wav')[0] for n in names}
N=len(X['original'])-LAG
X={n:(X[n][:N] if n=='original' else X[n][LAG:LAG+N]) for n in names}
meter=pyln.Meter(fs)
# loudness-match all to original
Lo=meter.integrated_loudness(X['original'])
Y={n:X[n]*10**((Lo-meter.integrated_loudness(X[n]))/20) for n in names}
# clipping / near-FS
for n in names: print(n,'samples > -0.1dBFS:',int((np.abs(X[n])>10**(-0.1/20)).sum()))
# spectra 1/3 octave (mid channel, loudness matched)
cent=[31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000,20000]
def bands(x):
    f,P=signal.welch(x.mean(1),fs,nperseg=16384)
    out=[]
    for c in cent:
        lo,hi=c/2**(1/6),c*2**(1/6); out.append(10*np.log10(P[(f>=lo)&(f<hi)].sum()+1e-20))
    return np.array(out)
B={n:bands(Y[n]) for n in names}
print('\nEQ difference vs original (loudness-matched, dB)')
print('Hz      '+' '.join(f'{n[:5]:>6s}' for n in names[1:]))
for i,c in enumerate(cent):
    print(f'{c:7.0f} '+' '.join(f'{B[n][i]-B["original"][i]:6.1f}' for n in names[1:]))
# stereo width: side/mid energy ratio per band
def sb(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); y=signal.sosfiltfilt(s,x,axis=0)
    M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
    return 10*np.log10((S**2).sum()/(M**2).sum()), np.corrcoef(y[:,0],y[:,1])[0,1]
print('\nSide/Mid ratio dB (corr) per band')
for n in names:
    r=[sb(X[n],lo,hi) for lo,hi in [(20,150),(150,1000),(1000,5000),(5000,18000)]]
    print(f'{n:9s} '+'  '.join(f'{a:6.1f}({c:.2f})' for a,c in r))
