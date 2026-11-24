import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/a/'; names=['original','universal','fire','clarity','tape']; fs=48000; LAG=48
X={n:sf.read(D+n+'.wav')[0] for n in names}
N=len(X['original'])-LAG
X={n:(X[n][:N] if n=='original' else X[n][LAG:LAG+N]) for n in names}
o=X['original'].mean(1)
# absolute low-end levels (dBFS spectral density) to see if Fire is creating sub
f,P=signal.welch(o,fs,nperseg=16384)
for n in ['original','fire']:
    f,P=signal.welch(X[n].mean(1),fs,nperseg=16384)
    print(n,'abs band dB 25-40,40-60,60-100,100-200,1k-2k:',[round(10*np.log10(P[(f>=a)&(f<b)].sum()),1) for a,b in [(25,40),(40,60),(60,100),(100,200),(1000,2000)]])
# HF ceiling
for n in names:
    f,P=signal.welch(X[n].mean(1),fs,nperseg=8192); Pd=10*np.log10(P+1e-20)
    ref=Pd[(f>1000)&(f<4000)].mean(); hi=f[(Pd>ref-60)&(f>10000)]
    print(n,'HF extends to ~',int(hi.max()) if len(hi) else None,'Hz')
# dynamics: gain vs input frame level (50ms frames), per band
def frames(x,w=2400):
    k=len(x)//w; return 10*np.log10((x[:k*w].reshape(k,w)**2).mean(1)+1e-12)
bandsdef={'full':None,'low<150':(20,150),'mid150-4k':(150,4000),'high>4k':(4000,18000)}
def bp(x,b):
    if b is None: return x
    s=signal.butter(4,b,'bandpass',fs=fs,output='sos'); return signal.sosfiltfilt(s,x)
print('\nGain (out-in, dB) at input-level percentiles 10/50/90/99 of frames; slope = compression (1.0 = none)')
for bn,b in bandsdef.items():
    li=frames(bp(o,b))
    for n in names[1:]:
        lo=frames(bp(X[n].mean(1),b)); g=lo-li
        m=li>np.percentile(li,5)
        q=[np.median(g[(li>=np.percentile(li,p-5))&(li<=np.percentile(li,p+5 if p<99 else 100))]) for p in (10,50,90,99)]
        slope=np.polyfit(li[m],lo[m],1)[0]
        print(f'{bn:10s} {n:9s} '+' '.join(f'{v:6.2f}' for v in q)+f'  slope {slope:.3f}')
# transient / crest per 50ms frame: peak-to-rms short term median
print('\nmedian short-term crest (dB), 10ms frames peak/rms over 100ms windows')
for n in names:
    x=X[n].mean(1); w=4800; k=len(x)//w; xr=x[:k*w].reshape(k,w)
    cr=20*np.log10(np.abs(xr).max(1)/np.sqrt((xr**2).mean(1)+1e-12)); print(f'{n:9s} {np.median(cr):.2f}')
# nonlinearity: coherence original->master
print('\ncoherence (1=purely linear/time-invariant) by band')
for n in names[1:]:
    f,C=signal.coherence(o,X[n].mean(1),fs,nperseg=4096)
    print(f'{n:9s} '+' '.join(f'{np.mean(C[(f>=a)&(f<b)]):.4f}' for a,b in [(30,150),(150,1000),(1000,4000),(4000,10000),(10000,16000)]))
# residual after best linear fit (FIR via spectral division) -> added distortion/noise level
print('\nnon-linear residual relative to output (dB)')
for n in names[1:]:
    y=X[n].mean(1); f,Pxy=signal.csd(o,y,fs,nperseg=4096); f,Pxx=signal.welch(o,fs,nperseg=4096); f,Pyy=signal.welch(y,fs,nperseg=4096)
    _,C=signal.coherence(o,y,fs,nperseg=4096)
    res=((1-C)*Pyy).sum()/Pyy.sum(); print(f'{n:9s} {10*np.log10(res):.1f}')
