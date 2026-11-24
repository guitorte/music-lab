import numpy as np, soundfile as sf
from scipy import signal
src,fs=sf.read('/home/claude/vr/mix.wav'); mas,_=sf.read('/home/claude/vr/Virada_no_Diabo_Remastered_master_24bit.wav')
N=16384
f,t,Z=signal.stft(src.mean(1),fs,nperseg=N,noverlap=N//2); L=20*np.log10(np.abs(Z)+1e-12)
_,_,Zm=signal.stft(mas.mean(1),fs,nperseg=N,noverlap=N//2); Lm=20*np.log10(np.abs(Zm)+1e-12)
def line(L,fc,bw=6):
    i=np.argmin(np.abs(f-fc)); pk=L[i-1:i+2].max(0); nb=np.r_[L[i-40:i-bw],L[i+bw:i+40]]; return pk-np.median(nb,0), pk
# exact frequency
seg=(t>118)&(t<140); i0=np.argmin(np.abs(f-12800)); j=i0-20+np.argmax(L[i0-20:i0+20][:,seg].mean(1)); fc=f[j]; print('line at %.1f Hz'%fc)
pr,pk=line(L,fc)
print('prominence over time (dB above neighbourhood), every 4 s:')
print(' '.join(f'{tt:.0f}:{p:+.0f}' for tt,p in zip(t[::7],pr[::7])))
on=t[pr>8]; print('present (>8 dB) from %.1f to %.1f s, %.0f%% of that span'%(on.min(),on.max(),100*((pr>8)&(t>=on.min())&(t<=on.max())).sum()/((t>=on.min())&(t<=on.max())).sum()))
# harmonics / subharmonics / companions
seg=(t>on.min())&(t<on.max())
cand=[fc/2,fc/3,fc*2/3,fc*3/4,fc*1.5,6400,4266,850]
for c in cand:
    if c<20000:
        p,_=line(L[:, :],c); print(f'  {c:7.0f} Hz: median prominence in span {np.median(p[seg]):+.1f} dB')
# level of the line vs band energy 10-16k
i=np.argmin(np.abs(f-fc)); band=(f>10000)&(f<16000)
r=10*np.log10((10**(L[i-1:i+2]/10)).sum(0)/(10**(L[band]/10)).sum(0))
print('line share of 10-16 kHz energy in span: median %.1f dB (0 = all of it)'%np.median(r[seg]))
# 850 Hz in master
p8,_=line(Lm,850); p8s,_=line(L,850); s2=(t>116)&(t<126); print('850 Hz prominence 116-126 s: source', ' '.join(f'{x:+.0f}' for x in p8s[s2]),' | master',' '.join(f'{x:+.0f}' for x in p8[s2]))
