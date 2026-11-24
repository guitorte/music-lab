import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/mt/mix.wav'); m=pyln.Meter(fs)
print('fs',fs,'len %.1f'%(len(x)/fs),'LUFS %.2f'%m.integrated_loudness(x))
up=signal.resample_poly(x,4,1,axis=0); print('TP %.2f dBTP, sample peak %.2f'%(20*np.log10(np.abs(up).max()),20*np.log10(np.abs(x).max())))
# short-term loudness profile
w=3*fs;h=fs; st=[m.integrated_loudness(x[i:i+w]) if np.abs(x[i:i+w]).max()>1e-4 else -70 for i in range(0,len(x)-w,h)]
st=np.array(st); print('ST LUFS p10/50/90/max: %.1f %.1f %.1f %.1f'%tuple(np.percentile(st[st>-60],[10,50,90,100])))
print('ST by 6s:',' '.join('%.0f'%v for v in st[::6]))
f,P=signal.welch(x.mean(1),fs,nperseg=16384)
bands=[30,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000]
tot=P.sum(); print('1/3-oct dB:',' '.join(f'{c}:{10*np.log10(P[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/tot):.0f}' for c in bands))
M=x.mean(1);S=(x[:,0]-x[:,1])/2; print('side/mid %.1f dB, corr %.2f'%(10*np.log10((S**2).mean()/(M**2).mean()),np.corrcoef(x[:,0],x[:,1])[0,1]))
lo=signal.sosfilt(signal.butter(4,120,'lowpass',fs=fs,output='sos'),x,axis=0); print('side<120Hz rel mid<120: %.1f dB'%(10*np.log10((((lo[:,0]-lo[:,1])/2)**2).mean()/((lo.mean(1))**2).mean())))
mo=x.mean(1); k=len(mo)//(fs//10); r=mo[:k*(fs//10)].reshape(k,-1); cr=20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9); print('median crest 100ms %.1f'%np.median(cr))
# tempo
kb=signal.sosfilt(signal.butter(4,[40,120],'bandpass',fs=fs,output='sos'),mo); H=480; e=np.sqrt((kb[:len(kb)//H*H].reshape(-1,H)**2).mean(1)); o=np.maximum(np.diff(e),0); ac=np.correlate(o-o.mean(),o-o.mean(),'full')[len(o)-1:]
lags=np.arange(len(ac))/100; sel=(lags>0.25)&(lags<1.5); L=lags[sel][np.argmax(ac[sel])]; print('kick period %.3f s -> %.1f BPM'%(L,60/L))
