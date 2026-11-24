import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
names=['vocals','drums','bass','guitar','piano','other']
def load(d,fmt):
    S={}
    for n in names:
        z,fs=sf.read(fmt(d,n)); S[n]=z
    k=min(len(v) for v in S.values()); return {a:b[:k] for a,b in S.items()},fs
import glob
R,fsr=load('/home/claude/ref/stems',lambda d,n: glob.glob(f'{d}/{n}*.flac')[0])
A,fsa=load('/home/claude/pg/w',lambda d,n: f'{d}/{n}.wav')
def report(S,fs,lab):
    mix=sum(S.values()); m=pyln.Meter(fs)
    up=signal.resample_poly(mix,4,1,axis=0); M=mix.mean(1); k=len(M)//(fs//10); r=M[:k*(fs//10)].reshape(k,-1)
    w=3*fs; st=np.array([m.integrated_loudness(mix[i:i+w]) for i in range(0,len(mix)-w,fs)]); st=st[st>-50]
    print(f'=== {lab}: {len(mix)/fs:.0f}s  LUFS {m.integrated_loudness(mix):.1f}  TP {20*np.log10(np.abs(up).max()):+.1f}  crest {np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)):.1f} dB  ST p10-p90 {np.percentile(st,90)-np.percentile(st,10):.1f} LU  L/R corr {np.corrcoef(*mix.T)[0,1]:.2f}')
    tot=m.integrated_loudness(mix); print('   stem loudness rel. mix (LU):',' '.join(f'{n}:{m.integrated_loudness(S[n])-tot:+.1f}' for n in names))
    print('   vocal minus rest of band: %+.1f LU'%(m.integrated_loudness(S['vocals'])-m.integrated_loudness(mix-S['vocals'])))
    bands=[40,63,100,160,250,400,630,1000,1600,2500,4000,6300,10000,16000]
    f,P=signal.welch(M,fs,nperseg=16384); ref=P[(f>200)&(f<5000)].sum()
    return np.array([10*np.log10(P[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/ref) for c in bands]),bands
sr,b=report(R,fsr,'REAL band (reference)'); sa,_=report(A,fsa,'AI (Soap Opera Thing)')
print('spectrum (dB rel. 200-5k):'); print('   band   ',' '.join(f'{c:>6}' for c in b)); print('   real   ',' '.join(f'{v:6.1f}' for v in sr)); print('   AI     ',' '.join(f'{v:6.1f}' for v in sa)); print('   AI-real',' '.join(f'{v:+6.1f}' for v in sa-sr))
