import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/n/in.wav'); m=x.mean(1); dur=len(m)/fs
nper=4096; hop=1024
f,t,S=signal.stft(m,fs,nperseg=nper,noverlap=nper-hop); L=10*np.log10(np.abs(S)**2+1e-16)
# floor per 15 s window: 5th percentile per bin, averaged per band
W=int(15*fs/hop)
bands=[(50,200),(200,1000),(1000,4000),(4000,8000),(8000,12000),(12000,16000),(16000,20000)]
print('5th-pct floor per band (dB) per 15 s window; and median level')
print('t(s)  '+'  '.join(f'{lo//1000 if lo>=1000 else lo}{"k" if lo>=1000 else ""}-{hi//1000}k' for lo,hi in bands))
for i in range(0,L.shape[1]-W+1,W):
    seg=L[:,i:i+W]; fl=np.percentile(seg,5,axis=1)
    print(f'{t[i]:5.0f} '+'  '.join(f'{fl[(f>=lo)&(f<hi)].mean():7.1f}' for lo,hi in bands))
print('median level per window, 8-16k:', [round(float(np.median(L[(f>=8000)&(f<16000),i:i+W])),1) for i in range(0,L.shape[1]-W+1,W)])
# tonal lines persistent
ff,P=signal.welch(m,fs,nperseg=65536); Pd=10*np.log10(P+1e-20); base=signal.medfilt(Pd,151); pr=Pd-base
mm=(ff>40)&(ff<22000)&(pr>8); g=[]
for fr,p in zip(ff[mm],pr[mm]):
    if g and fr-g[-1][0]<max(5,fr*0.01): g[-1]=(g[-1][0],max(g[-1][1],p))
    else: g.append((fr,p))
print('narrow lines:',[(int(a),round(b,1)) for a,b in g][:25])
# quietest moments: where, and spectrum shape there
w=fs//5; k=len(m)//w; lv=10*np.log10((m[:k*w].reshape(k,w)**2).mean(1)+1e-14)
idx=np.argsort(lv)[:8]; print('quietest 200ms frames at s:',sorted(np.round(idx/5,1)), 'levels',np.round(np.sort(lv)[:8],1))
