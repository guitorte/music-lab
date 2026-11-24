import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
voc,fs=sf.read(D+'vocais_original.wav'); cor,_=sf.read(D+'vocais_fix.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]
def env(z,lo=150,hi=5000):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z.mean(1)); w=int(0.005*fs); k=len(y)//w
    return 10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-12)
ev=env(voc); ec=env(cor)
for name,(t0,t1) in {'casal':(53.0,58.5),'achar':(66.5,71.5),'cara':(82.5,87.0)}.items():
    a=ev[int(t0/0.005):int(t1/0.005)]; 
    best=None
    for L in range(-60,61):   # +-300 ms in 5ms steps
        b=ec[int(t0/0.005)+L:int(t1/0.005)+L]; c=np.corrcoef(np.maximum(a,-60),np.maximum(b,-60))[0,1]
        if best is None or c>best[1]: best=(L*5,c)
    # fine lag via waveform corr
    s=slice(int(t0*fs),int(t1*fs)); x=voc[s].mean(1)
    lags=np.arange(-int(0.3*fs),int(0.3*fs)+1,1)
    cc=signal.correlate(cor[int(t0*fs)-int(0.3*fs):int(t1*fs)+int(0.3*fs)].mean(1),x,'valid',method='fft'); i=np.argmax(cc)
    print(f'{name}: env lag {best[0]} ms corr {best[1]:.2f} | waveform lag {(lags[i])/fs*1000:.1f} ms norm {cc[i]/np.sqrt((x**2).sum()*(cor[int(t0*fs)+lags[i]:int(t1*fs)+lags[i]].mean(1)**2).sum()):.2f}')
