import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d, uniform_filter
x,fs=sf.read('/home/claude/n/in.wav')
nper=2048; hop=512
f,t,ZL=signal.stft(x[:,0],fs,nperseg=nper,noverlap=nper-hop); _,_,ZR=signal.stft(x[:,1],fs,nperseg=nper,noverlap=nper-hop)
P=(np.abs(ZL)**2+np.abs(ZR)**2)/2
Ps=uniform_filter(P,size=(3,5))                      # smooth 3 bins x 5 frames
win=int(3*fs/hop)                                     # 3 s minimum-statistics window
N=minimum_filter1d(Ps,size=win,axis=1)*2.0            # bias correction for min stats
N=uniform_filter1d(N,size=win//2,axis=1)              # smooth the noise track
alpha=np.ones_like(f); gmin=np.ones_like(f)
hi=f>=15000; mid=(f>=800)&(f<15000); tr=(f>=14000)&(f<15000)
alpha[hi]=2.0; gmin[hi]=10**(-30/20)
alpha[mid]=1.0; gmin[mid]=10**(-9/20)
alpha[f<800]=0; gmin[f<800]=1
G=np.maximum(1-alpha[:,None]*N/np.maximum(Ps,1e-20),gmin[:,None])
G=np.sqrt(np.maximum(G,0))**2  # keep as amplitude-ish gain (power subtraction -> amplitude ratio)
G=np.sqrt(np.maximum(1-alpha[:,None]*N/np.maximum(Ps,1e-20),gmin[:,None]**2))
# temporal smoothing of gain: fast attack (gain up), slower release (gain down) to avoid musical noise
Gs=np.empty_like(G); c=G[:,0].copy(); up=0.6; dn=0.25
for i in range(G.shape[1]):
    g=G[:,i]; c=np.where(g>c, c+(g-c)*up, c+(g-c)*dn); Gs[:,i]=c
Gs=uniform_filter1d(Gs,size=3,axis=0)
_,yL=signal.istft(ZL*Gs,fs,nperseg=nper,noverlap=nper-hop); _,yR=signal.istft(ZR*Gs,fs,nperseg=nper,noverlap=nper-hop)
y=np.stack([yL,yR],1)[:len(x)]
sf.write('/home/claude/n/clean.wav',y,fs,subtype='PCM_24')
# report average reduction per band over time
bands=[(800,4000),(4000,8000),(8000,15000),(15000,21000)]
W=int(15*fs/hop)
print('avg gain (dB) per 15s window:')
for lo,h in bands:
    m=(f>=lo)&(f<h); print(f'{lo}-{h}:',[round(float(20*np.log10(Gs[m,i:i+W].mean())),1) for i in range(0,Gs.shape[1]-W+1,W)])
