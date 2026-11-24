import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1)
h=0.002
def env(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z); w=int(h*fs); k=len(y)//w; return np.log((y[:k*w].reshape(k,w)**2).mean(1)+1e-10)
bands={'kick 40-120':(40,120),'snare/hat 2-8k':(2000,8000),'vocal 300-3k':(300,3000)}
E={k:env(M,*v) for k,v in bands.items()}
def loc(t0,t1,lo=43.0,hi=44.6):
    out={}
    for k,e in E.items():
        a=e[int(t0/h):int(t1/h)]; best=None
        for L in np.arange(lo,hi,h):
            b=e[int((t0+L)/h):int((t1+L)/h)][:len(a)]; c=np.corrcoef(a,b)[0,1]
            if best is None or c>best[1]: best=(L,c)
        out[k]=best
    return out
for t0,t1,lab in [(15,25,'chorus start'),(25,35,'tente aí'),(35,47,'melhor que farmar'),(47,52,'O que é falar (1st half)'),(52,57,'O que é falar (2nd half)')]:
    r=loc(t0,t1); print(f'{lab:26s}',' | '.join(f'{k}: {v[0]:.3f} ({v[1]:.2f})' for k,v in r.items()))
