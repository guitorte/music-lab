import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
voc,fs=sf.read(D+'vocais_original.wav')
def env(t0,t1):
    y=signal.sosfiltfilt(signal.butter(2,[150,5000],'bandpass',fs=fs,output='sos'),voc[int(t0*fs):int(t1*fs)].mean(1)); w=int(0.005*fs); k=len(y)//w
    return np.maximum(10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-12),-70)
ref=env(83.6,85.8)
offs={}
for lab,o in [('c1',-44.39),('c3',38.857)]:
    best=None
    for d in range(-40,41):
        e=env(83.6+o+d*0.005,85.8+o+d*0.005); c=np.corrcoef(ref,e[:len(ref)])[0,1]
        if best is None or c>best[1]: best=(o+d*0.005,c)
    offs[lab]=best[0]; print(f'{lab}: offset {best[0]:+.3f} env corr {best[1]:.2f}')
def f0(t):
    s=voc[int(t*fs):int((t+0.04)*fs)].mean(1); s=s-s.mean(); ac=np.correlate(s,s,'full')[len(s)-1:]
    lo,hi=int(fs/500),int(fs/80); L=lo+np.argmax(ac[lo:hi]); return fs/L if ac[L]/ac[0]>0.5 else np.nan
print(' t(c2)   c2     c1     c3   (Hz)   level c2/c1/c3')
for t in np.arange(84.40,85.45,0.03):
    lv=[10*np.log10((voc[int(tt*fs):int((tt+0.03)*fs)]**2).mean()+1e-12) for tt in (t,t+offs['c1'],t+offs['c3'])]
    print(f' {t:.2f} {f0(t):6.1f} {f0(t+offs["c1"]):6.1f} {f0(t+offs["c3"]):6.1f}   {lv[0]:5.0f} {lv[1]:5.0f} {lv[2]:5.0f}')
np.save(D+'offs.npy',np.array([offs['c1'],offs['c3']]))
