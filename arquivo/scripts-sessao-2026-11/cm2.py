import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import uniform_filter1d
x,fs=sf.read('/home/claude/cm/B_ponte_up.wav'); N=16384
f,t,Z=signal.stft(x.mean(1),fs,nperseg=N,noverlap=N//2); L=20*np.log10(np.abs(Z)+1e-12)
base=uniform_filter1d(L,size=40,axis=0); prom=L-base
pers=(prom>8).mean(1); idx=np.where((pers>0.5)&(f>40)&(f<20000))[0]
res=[]
for i in idx:
    if res and f[i]-res[-1][0]<6: 
        if pers[i]>res[-1][1]: res[-1]=(f[i],pers[i],np.median(prom[i]))
        continue
    res.append((f[i],pers[i],np.median(prom[i])))
print('lines present in >50% of frames:'); [print(f'  {fr:8.1f} Hz  present {p*100:3.0f}%  median prominence {pr:+.1f} dB') for fr,p,pr in res]
# frequency stability of each (std of peak position)
for fr,_,_ in res:
    i=np.argmin(np.abs(f-fr)); pos=[f[i-3+np.argmax(L[i-3:i+4,k])] for k in range(L.shape[1])]; print(f'  {fr:.1f}: freq std {np.std(pos):.2f} Hz')
