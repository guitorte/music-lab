import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import uniform_filter1d
x,fs=sf.read('/home/claude/vr/mix.wav'); N=8192; H=1024
lines=[(849.6,14),(12799.8,10)]
y=np.zeros_like(x)
for ch in (0,1):
    f,t,Z=signal.stft(x[:,ch],fs,nperseg=N,noverlap=N-H); A=np.abs(Z); G=np.ones_like(A)
    for fc,bw in lines:
        tgt=(np.abs(f-fc)<=bw); nb=(np.abs(f-fc)>bw*2.5)&(np.abs(f-fc)<bw*2.5+60)
        floor=np.median(A[nb],0)*10**(2/20)                  # allow line bins up to +2 dB over the neighbourhood
        g=np.minimum(1,floor[None,:]/(A[tgt]+1e-12)); g=uniform_filter1d(g,5,axis=1)   # smooth over ~100 ms
        G[tgt]=np.minimum(G[tgt],g)
    _,z=signal.istft(Z*G,fs,nperseg=N,noverlap=N-H); y[:,ch]=z[:len(x)]
sf.write('/home/claude/vr/mix_clean.wav',y,fs,subtype='FLOAT')
# verify: prominence before/after, and what else changed
N2=16384; f,t,L0=signal.stft(x.mean(1),fs,nperseg=N2,noverlap=N2//2); _,_,L1=signal.stft(y.mean(1),fs,nperseg=N2,noverlap=N2//2)
L0=20*np.log10(np.abs(L0)+1e-12); L1=20*np.log10(np.abs(L1)+1e-12)
for fc in (849.6,12799.8):
    i=np.argmin(np.abs(f-fc)); nb=lambda L: np.median(np.r_[L[i-60:i-6],L[i+6:i+60]],0)
    p0=L0[i-1:i+2].max(0)-nb(L0); p1=L1[i-1:i+2].max(0)-nb(L1); s=(t>1)&(t<171)
    print(f'{fc:.0f} Hz: prominence median {np.median(p0[s]):+.1f} -> {np.median(p1[s]):+.1f} dB, 95th {np.percentile(p0[s],95):+.1f} -> {np.percentile(p1[s],95):+.1f}; around 2:00 {np.median(p0[(t>116)&(t<130)]):+.1f} -> {np.median(p1[(t>116)&(t<130)]):+.1f}')
d=x-y; print('removed signal level relative to track: %.1f dB'%(10*np.log10((d**2).mean()/(x**2).mean())))
