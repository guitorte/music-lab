import numpy as np, soundfile as sf
from scipy import signal
fs=48000
a,_=sf.read('/home/claude/s/orig.wav'); b,_=sf.read('/home/claude/s/rem.wav')
# align: rem lag -1 relative -> b[n-1]? test both
N=min(len(a),len(b))-10
best=None
for lag in range(-3,4):
    bb=b[3+lag:3+lag+N-6]; aa=a[3:3+N-6]
    r=np.corrcoef(aa[::7,0],bb[::7,0])[0,1]
    if best is None or r>best[0]: best=(r,lag)
print('best lag',best)
lag=best[1]; aa=a[3:3+N-6]; bb=b[3+lag:3+lag+N-6]
cent=[31.5,50,80,125,200,315,500,800,1250,2000,3150,5000,6300,8000,10000,12500,14000,16000,18000,20000]
def bands(x):
    f,P=signal.welch(x.mean(1),fs,nperseg=16384)
    return f,P
f,Pa=bands(aa); f,Pb=bands(bb)
print('\nband   orig_dB  rem_dB  diff')
for c in cent:
    lo,hi=c/2**(1/6),c*2**(1/6); m=(f>=lo)&(f<hi)
    x=10*np.log10(Pa[m].sum()); y=10*np.log10(Pb[m].sum()); print(f'{c:7.0f} {x:7.1f} {y:7.1f} {y-x:6.1f}')
# HF ceiling
for n,P in [('orig',Pa),('rem',Pb)]:
    Pd=10*np.log10(P+1e-20); ref=Pd[(f>1000)&(f<4000)].mean()
    for thr in (40,60,80):
        hi=f[(Pd>ref-thr)&(f>8000)]; print(n,f'HF within -{thr}dB of mids up to',int(hi.max()) if len(hi) else None)
# coherence per band
fc,C=signal.coherence(aa.mean(1),bb.mean(1),fs,nperseg=4096)
print('\ncoherence by band:',[ (a_,b_,round(float(np.mean(C[(fc>=a_)&(fc<b_)])),3)) for a_,b_ in [(30,150),(150,1000),(1000,4000),(4000,8000),(8000,12000),(12000,16000),(16000,20000)]])
# stereo
def ms(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); y=signal.sosfilt(s,x[::1],axis=0)
    M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; return round(10*np.log10((S**2).sum()/(M**2).sum()),1), round(np.corrcoef(y[:,0],y[:,1])[0,1],2)
seg=slice(fs*30,fs*90)
for n,x in [('orig',aa[seg]),('rem',bb[seg])]:
    print(n,'side/mid dB (corr):',[ms(x,lo,hi) for lo,hi in [(20,150),(150,1000),(1000,5000),(5000,16000),(16000,23000)]])
np.save('/home/claude/s/lag.npy',lag)
