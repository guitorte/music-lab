import numpy as np, soundfile as sf, pyloudnorm as pyln, sys
from scipy import signal
fs=48000; m=pyln.Meter(fs)
a,_=sf.read('/home/claude/e/mix.wav'); b,_=sf.read(sys.argv[1])
def bp(z,lo,hi): return signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
def stats(x):
    mo=x.mean(1); w=fs//10; k=len(mo)//w; r=mo[:k*w].reshape(k,w); cr=20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)
    y=bp(mo,2000,8000); w2=int(0.005*fs); k2=len(y)//w2; e=10*np.log10((y[:k2*w2].reshape(k2,w2)**2).mean(1)+1e-14)
    jump=np.percentile(np.diff(e),99)
    lb,rb=bp(x[:,0],2000,8000),bp(x[:,1],2000,8000); on=np.where(np.diff(e)>9)[0]; on=on[(on>10)&(on<k2-20)]
    cs=[np.corrcoef(lb[o*w2:o*w2+int(.03*fs)],rb[o*w2:o*w2+int(.03*fs)])[0,1] for o in on[::3]]
    return np.median(cr),jump,np.median(cs)
for nm,x in [('mix',a),('master',b)]:
    c,j,cs=stats(x); print(f'{nm}: LUFS {m.integrated_loudness(x):.1f}  median 100ms crest {c:.1f} dB  attack sharpness p99 {j:.1f} dB/5ms  perc L/R corr {cs:.2f}')
a2=a*10**((m.integrated_loudness(b)-m.integrated_loudness(a))/20)
f,Pa=signal.welch(a2.mean(1),fs,nperseg=16384); _,Pb=signal.welch(b.mean(1),fs,nperseg=16384)
print('tone change (loudness-matched):',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [63,140,315,700,2000,4000,8000,12500]))
