import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import percentile_filter, uniform_filter1d, uniform_filter
x,fs=sf.read('/home/claude/n/in.wav')
nper=2048; hop=512
f,t,ZL=signal.stft(x[:,0],fs,nperseg=nper,noverlap=nper-hop); _,_,ZR=signal.stft(x[:,1],fs,nperseg=nper,noverlap=nper-hop)
P=(np.abs(ZL)**2+np.abs(ZR)**2)/2
Ps=uniform_filter(P,size=(3,3))
D=4; Pd=Ps[:,::D]; win=int(4*fs/hop/D)
Nd=percentile_filter(Pd,percentile=20,size=(1,win))
Nd=uniform_filter1d(Nd,size=win,axis=1)
N=np.repeat(Nd,D,axis=1)[:,:P.shape[1]]
def prof(fr):  # alpha, gmin dB
    if fr<1000: return 0,0
    if fr<4000: return 1.0,-6
    if fr<12000: return 1.6,-18
    if fr<15000: return 1.0,-6
    return 2.0,-30
al=np.array([prof(v)[0] for v in f]); gm=10**(np.array([prof(v)[1] for v in f])/20)
# smooth the profile edges across ~300 Hz
al=uniform_filter1d(al,13); gm=uniform_filter1d(gm,13)
G=np.sqrt(np.maximum(1-al[:,None]*N/np.maximum(Ps,1e-20),gm[:,None]**2))
Gs=np.empty_like(G); c=G[:,0].copy()
for i in range(G.shape[1]):
    g=G[:,i]; c=np.where(g>c,c+(g-c)*0.7,c+(g-c)*0.3); Gs[:,i]=c
Gs=uniform_filter1d(Gs,size=3,axis=0)
_,yL=signal.istft(ZL*Gs,fs,nperseg=nper,noverlap=nper-hop); _,yR=signal.istft(ZR*Gs,fs,nperseg=nper,noverlap=nper-hop)
y=np.stack([yL,yR],1)[:len(x)]
sf.write('/home/claude/n/clean2.wav',y,fs,subtype='PCM_24')
