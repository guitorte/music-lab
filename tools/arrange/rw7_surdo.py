# synthetic surdo layer (A1 ~55 Hz, pitch drop, open on 1/3, muted otherwise) blended with GM tom body
import numpy as np, soundfile as sf
from scipy import signal
fs=44100; parts=np.load('/home/claude/rw/parts.npy',allow_pickle=True)[0]
N=int(194*fs); out=np.zeros(N); rng=np.random.default_rng(5)
for p,t,d,v in parts['surdo']:
    if p==35: continue
    a=(v/127)**1.6; strong=v>80; L=int((0.55 if strong else 0.18)*fs); tt=np.arange(L)/fs
    f=55*(1+0.35*np.exp(-tt/0.025)); ph=2*np.pi*np.cumsum(f)/fs
    env=np.exp(-tt/(0.32 if strong else 0.07))*np.clip(tt/0.002,0,1)
    x=np.sin(ph)*env+0.25*np.sin(2*ph)*env*np.exp(-tt/0.05)
    click=rng.standard_normal(L)*np.exp(-tt/0.006)*0.15; click=signal.sosfilt(signal.butter(2,[400,3000],'bandpass',fs=fs,output='sos'),click)
    i=int(t*fs); j=min(N,i+L); out[i:j]+=a*(x+click)[:j-i]
g,_=sf.read('/home/claude/rw/surdo.wav'); g=g.mean(1); g=np.pad(g,(0,max(0,N-len(g))))[:N]
g=signal.sosfiltfilt(signal.butter(2,[90,400],'bandpass',fs=fs,output='sos'),g)
out=out/np.abs(out).max()*0.8; g=g/np.abs(g).max()*0.35
sf.write('/home/claude/rw/surdo.wav',np.stack([out+g]*2,1),fs,subtype='FLOAT'); print('ok')
