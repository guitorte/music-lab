import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz2/w/'
voc,fs=sf.read(D+'voc.wav'); cor,_=sf.read(D+'cor.wav'); cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]
old,_=sf.read('/home/claude/vz/w/vocais_fix.wav'); old=np.r_[old,np.zeros((len(voc)-len(old),2))]
for nm,(a,b) in [('casal',(55.3,57.0)),('achar',(68.5,69.4)),('cara',(84.4,85.3))]:
    s=slice(int(a*fs),int(b*fs))
    def lagc(x,y,maxl=200):
        c=signal.correlate(y,x,'full',method='fft'); l=np.arange(-len(x)+1,len(y)); m=np.abs(l)<=maxl; i=np.argmax(c[m]); return l[m][i], c[m][i]/np.sqrt((x**2).sum()*(y**2).sum())
    print(f'{nm}: new fix vs new voc lag/corr {lagc(voc[s].mean(1),cor[s].mean(1))} | new fix vs OLD fix {lagc(old[s].mean(1),cor[s].mean(1))}')
    M=signal.sosfiltfilt(signal.butter(4,[150,6000],'bandpass',fs=fs,output='sos'),cor[s],axis=0); V=signal.sosfiltfilt(signal.butter(4,[150,6000],'bandpass',fs=fs,output='sos'),voc[s],axis=0)
    print(f'    L/R corr: voc {np.corrcoef(*V.T)[0,1]:.2f}  new fix {np.corrcoef(*M.T)[0,1]:.2f}')
# global level/tone transfer new fix -> new voc on shared material (20-95 s)
s=slice(20*fs,95*fs); f,Pv=signal.welch(voc[s].mean(1),fs,nperseg=8192); _,Pc=signal.welch(cor[s].mean(1),fs,nperseg=8192)
print('tone voc minus fix (dB):',' '.join(f'{c}:{10*np.log10(Pv[(f>=c/1.4)&(f<c*1.4)].sum()/Pc[(f>=c/1.4)&(f<c*1.4)].sum()):+.1f}' for c in [150,300,600,1200,2500,5000,10000]))
