import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/vz/final/Virada_no_Diabo_palavras_corrigidas_v2_24bit.wav'); old,_=sf.read('/home/claude/v/master.wav'); mx,_=sf.read('/home/claude/v/mix.wav')
m=pyln.Meter(fs)
for lab,z in [('mix v2',x),('old master',old)]:
    up=signal.resample_poly(z,4,1,axis=0); mo=z.mean(1); k=len(mo)//(fs//10); r=mo[:k*(fs//10)].reshape(k,-1)
    print(f'{lab}: LUFS {m.integrated_loudness(z):.2f} TP {20*np.log10(np.abs(up).max()):.2f} crest {np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)):.1f} corr {np.corrcoef(z[:,0],z[:,1])[0,1]:.2f}')
a=mx*10**((m.integrated_loudness(old)-m.integrated_loudness(mx))/20)
f,Pa=signal.welch(a.mean(1),fs,nperseg=16384); _,Pb=signal.welch(old.mean(1),fs,nperseg=16384)
bands=[30,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000]
print('old master tone change vs mix:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in bands))
f,P=signal.welch(x.mean(1),fs,nperseg=16384); tot=P.sum()
print('mix 1/3-oct:',' '.join(f'{c}:{10*np.log10(P[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/tot):.0f}' for c in bands))
lo=signal.sosfilt(signal.butter(4,120,'lowpass',fs=fs,output='sos'),x,axis=0); print('side<120 vs mid<120 %.1f dB'%(10*np.log10((((lo[:,0]-lo[:,1])/2)**2).mean()/((lo.mean(1))**2).mean())))
w=3*fs; st=np.array([m.integrated_loudness(x[i:i+w]) for i in range(0,len(x)-w,fs)]); print('ST p10/50/90 %.1f %.1f %.1f'%tuple(np.percentile(st[st>-50],[10,50,90])))
# old master gain reduction estimate: short-term crest change
