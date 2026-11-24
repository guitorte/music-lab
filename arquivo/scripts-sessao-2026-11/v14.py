import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
cor,fs=sf.read(D+'vocais_fix.wav'); voc,_=sf.read(D+'vocais_original.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
def st(z,t0,t1,lo=200,hi=8000):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((t0-0.3)*fs):int((t1+0.3)*fs)],axis=0)[int(0.3*fs):-int(0.3*fs)]
    M=y.mean(1); S=(y[:,0]-y[:,1])/2; return np.corrcoef(y[:,0],y[:,1])[0,1], 10*np.log10((S**2).mean()/(M**2).mean()+1e-12)
print('stereo (L/R corr, side vs mid dB) 200-8k')
for lab,(a,b) in [('casal phrase',(55.46,56.85)),('achar',(68.62,69.31)),('a cara',(84.53,85.20)),('verse 16-29',(16,29)),('chorus 30-46',(30,46))]:
    c1=st(voc,a,b); c2=st(cor,a,b); print(f' {lab:13s} orig corr {c1[0]:.2f} side {c1[1]:+.1f} | fix corr {c2[0]:.2f} side {c2[1]:+.1f}')
for t in np.arange(55.6,56.9,0.1):
    c1=st(voc,t,t+0.1); c2=st(cor,t,t+0.1); print(f'  {t:.1f}: orig {c1[0]:.2f}/{c1[1]:+.0f}  fix {c2[0]:.2f}/{c2[1]:+.0f}')
