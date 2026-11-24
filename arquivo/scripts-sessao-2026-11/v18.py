import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
cor,fs=sf.read(D+'vocais_fix.wav'); voc,_=sf.read(D+'vocais_original.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
def lr(z,t0,t1):
    s=z[int(t0*fs):int(t1*fs)]; s=signal.sosfiltfilt(signal.butter(4,[150,6000],'bandpass',fs=fs,output='sos'),s,axis=0)
    c=signal.correlate(s[:,1],s[:,0],'full',method='fft'); l=np.arange(-len(s)+1,len(s)); m=np.abs(l)<int(0.05*fs); i=np.argmax(c[m])
    M=s.mean(1); S=(s[:,0]-s[:,1])/2
    return np.corrcoef(s[:,0],s[:,1])[0,1], l[m][i]/fs*1000, c[m][i]/np.sqrt((s[:,0]**2).sum()*(s[:,1]**2).sum()), 10*np.log10((S**2).mean()/(M**2).mean())
print('L/R: corr@0 | best lag ms, corr@lag | side vs mid dB')
for lab,(a,b) in [('chorus2 line4 "ta a cara" 84.53-85.20',(84.53,85.20)),('chorus2 line3 80.4-84.4',(80.4,84.4)),('chorus1 line4 40.1-41.0',(40.1,41.0)),('chorus3 line4 123.3-124.4',(123.3,124.4))]:
    for nm,z in [('orig',voc),('fix',cor)]:
        c0,lag,cl,sd=lr(z,a,b); print(f' {lab:38s} {nm}: {c0:5.2f} | {lag:6.2f} ms {cl:5.2f} | side {sd:+5.1f}')
for t in np.arange(84.4,85.4,0.1):
    a=lr(voc,t,t+0.1); b=lr(cor,t,t+0.1); print(f'  {t:.1f} orig {a[0]:5.2f}/{a[3]:+4.0f}  fix {b[0]:5.2f}/{b[3]:+4.0f}')
