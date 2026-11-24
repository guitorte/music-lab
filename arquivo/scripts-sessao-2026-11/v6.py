import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
voc,fs=sf.read(D+'vocais_original.wav'); cor,_=sf.read(D+'vocais_fix.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
def f0(z,t):
    s=z[int(t*fs):int((t+0.04)*fs)].mean(1); s=s-s.mean(); ac=np.correlate(s,s,'full')[len(s)-1:]
    lo,hi=int(fs/600),int(fs/80); L=lo+np.argmax(ac[lo:hi]); return fs/L, ac[L]/ac[0]
print('f0 around melhor (Hz, voicing):')
for t in np.arange(56.70,57.10,0.02):
    a=f0(voc,t); b=f0(cor,t); print(f' {t:.2f}  orig {a[0]:6.1f} ({a[1]:.2f})  fix {b[0]:6.1f} ({b[1]:.2f})  diff {1200*np.log2(b[0]/a[0]):+6.0f} cents')
def bandlev(z,t0,t1,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((t0-0.2)*fs):int((t1+0.2)*fs)].mean(1))[int(0.2*fs):-int(0.2*fs)]
    return 10*np.log10((y**2).mean()+1e-14)
print('fricative check in achar (dB, 6-11k minus 1.8-4k): >0 means s-like, <0 ch-like')
for t in np.arange(68.84,69.02,0.02):
    a=bandlev(voc,t,t+0.02,6000,11000)-bandlev(voc,t,t+0.02,1800,4000); b=bandlev(cor,t,t+0.02,6000,11000)-bandlev(cor,t,t+0.02,1800,4000)
    print(f' {t:.2f} orig {a:+5.1f}  fix {b:+5.1f}')
