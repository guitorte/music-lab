import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz2/w/'
mix,fs=sf.read(D+'mix.wav'); voc,_=sf.read(D+'voc.wav'); ins,_=sf.read(D+'ins.wav'); cor,_=sf.read(D+'cor.wav')
db=lambda z: 10*np.log10((z**2).mean()+1e-20)
print('lens',len(mix),len(voc),len(ins),len(cor))
print('levels mix %.1f voc %.1f ins %.1f cor %.1f'%(db(mix),db(voc),db(ins),db(cor)))
print('residual mix-(voc+ins) %.1f dB'%(db(mix-(voc+ins))-db(mix)))
X=np.stack([voc[:,0],ins[:,0]],1); g=np.linalg.lstsq(X,mix[:,0],rcond=None)[0]; print('LS gains',np.round(g,3))
print('peak mix %.2f, voc+ins %.2f'%(20*np.log10(np.abs(mix).max()),20*np.log10(np.abs(voc+ins).max())))
def lag(a,b,maxl):
    c=signal.correlate(b,a,'full',method='fft'); l=np.arange(-len(a)+1,len(b)); m=np.abs(l)<=maxl; i=np.argmax(c[m]); return l[m][i], c[m][i]/np.sqrt((a**2).sum()*(b**2).sum())
n=min(len(voc),len(cor)); s=slice(5*fs,n-5*fs)
print('global lag voc vs mix',lag(mix[s].mean(1),voc[s].mean(1),fs))
print('global lag cor vs voc',lag(voc[s].mean(1),cor[s].mean(1),fs))
for t0 in range(0,146,10):
    ss=slice(int(t0*fs),int((t0+4)*fs)); print(f' {t0}s', lag(voc[ss].mean(1),cor[ss].mean(1),int(0.3*fs)))
