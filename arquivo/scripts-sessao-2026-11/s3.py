import numpy as np, soundfile as sf
from scipy import signal
fs=48000
a,_=sf.read('/home/claude/s/orig.wav'); b,_=sf.read('/home/claude/s/rem.wav')
N=min(len(a),len(b)); a=a[:N].mean(1); b=b[:N].mean(1)
def bp(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); return signal.sosfiltfilt(s,x)
def env(x,w=480):  # 10 ms
    k=len(x)//w; return np.sqrt((x[:k*w].reshape(k,w)**2).mean(1))
print('band envelope corr (10ms) | median crest per 10ms frame | spectral flatness')
for lo,hi in [(150,1000),(1000,4000),(4000,8000),(8000,12000),(12000,16000)]:
    xa,xb=bp(a,lo,hi),bp(b,lo,hi); ea,eb=env(xa),env(xb)
    r=np.corrcoef(20*np.log10(ea+1e-9),20*np.log10(eb+1e-9))[0,1]
    # transient sharpness: 95th pct of positive env jumps (dB per 10ms)
    ja=np.percentile(np.diff(20*np.log10(ea+1e-9)),99); jb=np.percentile(np.diff(20*np.log10(eb+1e-9)),99)
    # flatness
    def flat(x):
        f,t,S=signal.stft(x,fs,nperseg=2048); P=np.abs(S)**2; m=(f>=lo)&(f<hi); P=P[m]+1e-15
        return np.median(np.exp(np.log(P).mean(0))/P.mean(0))
    print(f'{lo:5d}-{hi:5d} envcorr {r:.2f} | onset jump p99 orig {ja:.1f} rem {jb:.1f} dB | flatness orig {flat(xa):.3f} rem {flat(xb):.3f}')
# dynamics of HF over time: std of 100ms level in 4-12k
for n,x in [('orig',a),('rem',b)]:
    e=20*np.log10(env(bp(x,4000,12000),4800)+1e-9); print(n,'4-12k 100ms level std dB',round(e[e>-80].std(),2))
