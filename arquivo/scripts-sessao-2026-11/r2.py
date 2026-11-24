import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/r/mix.wav'); m=x.mean(1); dur=len(m)/fs
def bp(z,lo,hi): return signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z)
meter=pyln.Meter(fs); W=10
sub=bp(m,30,60); low=bp(m,60,120); kick=bp(m,40,120)
print('per 10 s: LUFS | sub 30-60 rel. to full (dB) | 60-120 rel. full')
for i in range(0,int(dur)-W+1,W):
    s=slice(i*fs,(i+W)*fs); full=(m[s]**2).mean()
    print(f'{i:4d}s {meter.integrated_loudness(x[s]):6.1f} {10*np.log10((sub[s]**2).mean()/full):6.1f} {10*np.log10((low[s]**2).mean()/full):6.1f}')
# tempo from kick onsets
H=32; rate=fs/H; k=len(kick)//H; e=10*np.log10((kick[:k*H].reshape(k,H)**2).mean(1)+1e-14)
on=np.maximum(np.diff(e,prepend=e[0]),0); ac=np.correlate(on-on.mean(),on-on.mean(),'full')[len(on)-1:]
lags=np.arange(len(ac))/rate; mm=(lags>60/200)&(lags<60/60); print('tempo candidates (BPM):',[round(60/lags[mm][i],1) for i in np.argsort(ac[mm])[-4:][::-1]])
# sub sustain: decay after kick peaks (ms to drop 12 dB) in sub band
se=10*np.log10((sub[:k*H].reshape(k,H)**2).mean(1)+1e-14)
pk=signal.find_peaks(se,height=np.percentile(se,90),distance=int(0.2*rate))[0]
dec=[]
for p in pk:
    t=np.where(se[p:p+int(rate)]<se[p]-12)[0]
    if len(t): dec.append(t[0]/rate*1000)
print('sub hits:',len(pk),' median time to fall 12 dB: %.0f ms'%np.median(dec))
