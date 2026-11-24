import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import uniform_filter1d
x,fs=sf.read('/home/claude/tp/mix.wav'); N=16384; H=2048
lines=[16901.4+99.6*k for k in range(32)]
# use exact detected positions: snap to nearest STFT bin peak per line later
def clean(x):
    y=np.zeros_like(x)
    for ch in (0,1):
        f,t,Z=signal.stft(x[:,ch],fs,nperseg=N,noverlap=N-H); A=np.abs(Z); G=np.ones_like(A)
        for fc in lines:
            tgt=np.abs(f-fc)<=6; nb=((np.abs(f-fc)>15)&(np.abs(f-fc)<40))
            floor=np.median(A[nb],0); g=np.minimum(1,floor[None,:]/(A[tgt]+1e-12)); g=uniform_filter1d(g,3,axis=1); G[tgt]=np.minimum(G[tgt],g)
        _,z=signal.istft(Z*G,fs,nperseg=N,noverlap=N-H); y[:,ch]=z[:len(x)]
    return y
y=clean(clean(x))
sf.write('/home/claude/tp/mix_clean.wav',y,fs,subtype='FLOAT')
f,t,L0=signal.stft(x.mean(1),fs,nperseg=N,noverlap=N//2); _,_,L1=signal.stft(y.mean(1),fs,nperseg=N,noverlap=N//2)
L0=20*np.log10(np.abs(L0)+1e-12); L1=20*np.log10(np.abs(L1)+1e-12); b0=uniform_filter1d(L0,40,axis=0); b1=uniform_filter1d(L1,40,axis=0)
p0=[np.median((L0-b0)[np.argmin(np.abs(f-fc))]) for fc in lines]; p1=[np.median((L1-b1)[np.argmin(np.abs(f-fc))]) for fc in lines]
print('comb prominence: median over lines %.1f -> %.1f dB, worst %.1f -> %.1f dB'%(np.median(p0),np.median(p1),max(p0),max(p1)))
d=x-y; print('removed signal: %.1f dB below the track'%(-10*np.log10((d**2).mean()/(x**2).mean())))
lp=lambda z: signal.sosfiltfilt(signal.butter(8,15000,'lowpass',fs=fs,output='sos'),z,axis=0)
print('change below 15 kHz: %.1f dB below the track (should be tiny)'%(-10*np.log10((lp(d)**2).mean()/(x**2).mean())))
