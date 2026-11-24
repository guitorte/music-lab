import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
src,fs=sf.read('/home/claude/vr/mix.wav'); old,_=sf.read('/home/claude/v/mix.wav'); mas,_=sf.read('/home/claude/vr/Virada_no_Diabo_Remastered_master_24bit.wav')
N=32768
def stft(z): f,t,Z=signal.stft(z.mean(1),fs,nperseg=N,noverlap=N//2); return f,t,20*np.log10(np.abs(Z)+1e-12)
f,t,L=stft(src); _,to,Lo=stft(old)
i0=np.argmin(np.abs(f-850)); j=i0-40+np.argmax(np.median(L[i0-40:i0+40],1)); fc=f[j]; print('exact line %.2f Hz'%fc)
def prom(L,fc):
    i=np.argmin(np.abs(f-fc)); pk=L[i-1:i+2].max(0); nb=np.r_[L[i-60:i-6],L[i+6:i+60]]; return pk-np.median(nb,0), pk
p,pk=prom(L,fc); po,_=prom(Lo,fc)
print('850 line prominence, Suno vs old mix (every ~5 s):')
for k in range(0,len(t),15):
    oo=po[min(k,len(po)-1)] if t[k]<150 else np.nan
    print(f'  {t[k]:5.0f}s  suno {p[k]:+5.1f}  old {oo:+5.1f}')
# frequency stability (constant tone vs musical note)
seg=(t>5)&(t<170); fr=[f[np.argmin(np.abs(f-fc))-8+np.argmax(L[np.argmin(np.abs(f-fc))-8:np.argmin(np.abs(f-fc))+9,k])] for k in np.where(seg)[0]]
print('peak freq spread %.2f Hz (std)'%np.std(fr))
# context loudness: short-term, to see why 2:00 stands out
m=pyln.Meter(fs)
print('short-term LUFS of master and line level relative to music:')
for t0 in range(100,141,4):
    s=slice(int(t0*fs),int((t0+3)*fs)); k=np.argmin(np.abs(t-(t0+1.5)))
    print(f'  {t0}s  LUFS {m.integrated_loudness(mas[s]):6.1f} | 850 prom {p[k]:+.0f} | 12.8k prom', end='')
    i=np.argmin(np.abs(f-12800)); print(f' {L[i-1:i+2,k].max()-np.median(np.r_[L[i-60:i-6,k],L[i+6:i+60,k]]):+.0f}')
