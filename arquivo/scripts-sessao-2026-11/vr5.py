import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import uniform_filter1d
src,fs=sf.read('/home/claude/vr/mix.wav'); mas,_=sf.read('/home/claude/vr/Virada_no_Diabo_Remastered_master_24bit.wav'); old,_=sf.read('/home/claude/v/mix.wav')
def tonal(z,t0,t1,N=16384):
    # stationary narrow lines: per-frame spectra, keep bins that are >8 dB above 1/3-oct neighbourhood in >80% of frames
    f,t,Z=signal.stft(z[int(t0*fs):int(t1*fs)].mean(1),fs,nperseg=N,noverlap=N*3//4); L=20*np.log10(np.abs(Z)+1e-12)
    base=uniform_filter1d(L,size=40,axis=0); prom=L-base
    pers=(prom>8).mean(1); idx=np.where((pers>0.8)&(f>60)&(f<16000))[0]
    out=[]
    for i in idx:
        if out and f[i]-out[-1][0]<5: continue
        out.append((f[i],np.median(prom[i]),np.median(L[i])))
    return out
for lab,z in [('Suno source',src),('old mix',old),('new master',mas)]:
    for t0,t1 in [(112,118),(118,124),(124,130)]:
        tl=tonal(z,t0,t1); print(f'{lab:11s} {t0}-{t1}s:',', '.join(f'{fr:.0f}Hz(+{p:.0f})' for fr,p,_ in tl[:14]) or '-')
