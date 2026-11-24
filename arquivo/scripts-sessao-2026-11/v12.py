import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); cor,_=sf.read(D+'vocais_fix.wav'); voc,_=sf.read(D+'vocais_original.wav')
cor=np.r_[cor,np.zeros((len(mix)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
out=np.load(D+'out2.npy'); P=np.load(D+'parts.npy',allow_pickle=True)
N=1024;H=256
def flux(z,t0,t1,lo,hi):
    f,t,Z=signal.stft(z[int(t0*fs):int(t1*fs)].mean(1),fs,nperseg=N,noverlap=N-H); b=(f>=lo)&(f<hi)
    L=20*np.log10(np.abs(Z[b])+1e-9); L=L-L.mean(0)    # remove frame level -> spectral-shape fluctuation
    return np.median(np.abs(np.diff(L,axis=1)))
print('musical-noise index (median |frame-to-frame change| of spectral shape, dB) - mix vs out')
for nm,(a,b),(c,d) in [('casal',(55.47,56.84),(50.0,51.4)),('achar',(68.63,69.30),(64.0,64.7)),('cara',(84.54,85.19),(40.0,40.7))]:
    print(f' {nm}: ',' '.join(f'{lo}-{hi}: mix {flux(mix,a,b,lo,hi):.2f} out {flux(out,a,b,lo,hi):.2f}' for lo,hi in [(200,1000),(1000,4000),(4000,12000)]))
# glitch hunt in the fix stem: per 10 ms, flatness & level, compare to same lyric elsewhere not possible -> look for clicks/broadband bursts
x=cor[int(55.3*fs):int(57.0*fs)].mean(1)
d=np.abs(np.diff(x)); thr=np.percentile(np.abs(np.diff(cor[int(30*fs):int(50*fs)].mean(1))),99.99)
idx=np.where(d>thr)[0]; print('fix-stem sample jumps above 99.99th pct of 30-50s:',len(idx),[round(55.3+i/fs,3) for i in idx[:15]])
f,t,Z=signal.stft(x,fs,nperseg=N,noverlap=N-H); A=np.abs(Z)+1e-12
flat=np.exp(np.log(A[(f>500)&(f<12000)]).mean(0))/A[(f>500)&(f<12000)].mean(0); lev=20*np.log10(np.sqrt((A**2).mean(0)))
lev-=lev.max()
print('fix stem 55.3-57.0: frames with broadband noise (flatness>0.35 and level>-30):',[f'{55.3+tt:.2f}({fl:.2f},{lv:.0f})' for tt,fl,lv in zip(t,flat,lev) if fl>0.35 and lv>-30])
x=voc[int(55.3*fs):int(57.0*fs)].mean(1); f,t,Z=signal.stft(x,fs,nperseg=N,noverlap=N-H); A=np.abs(Z)+1e-12
flat=np.exp(np.log(A[(f>500)&(f<12000)]).mean(0))/A[(f>500)&(f<12000)].mean(0); lev=20*np.log10(np.sqrt((A**2).mean(0))); lev-=lev.max()
print('orig stem same span, same test:',[f'{55.3+tt:.2f}({fl:.2f},{lv:.0f})' for tt,fl,lv in zip(t,flat,lev) if fl>0.35 and lv>-30])
