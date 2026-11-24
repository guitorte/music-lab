import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); ins,_=sf.read(D+'Instrumental.wav'); cor,_=sf.read(D+'Vocais_corrigidos.wav')
db=lambda z: 10*np.log10((z**2).mean()+1e-20)
print('levels dB: mix %.1f voc %.1f ins %.1f cor %.1f'%(db(mix),db(voc),db(ins),db(cor)))
# 1) does mix = voc + ins ?
r=mix-(voc+ins); print('residual mix-(voc+ins): %.1f dB rel mix'%(db(r)-db(mix)))
def lag(a,b,maxl=fs):  # lag of b relative to a
    c=signal.correlate(b,a,'full',method='fft'); l=np.arange(-len(a)+1,len(b)); m=np.abs(l)<=maxl
    i=np.argmax(c[m]); return l[m][i], c[m][i]/np.sqrt((a**2).sum()*(b**2).sum())
# global alignment voc vs mix, cor vs voc (mono, 60-160 s)
s=slice(30*fs,150*fs)
print('lag voc vs mix', lag(mix[s].mean(1),voc[s].mean(1)))
print('lag cor vs voc', lag(voc[s].mean(1),cor[s].mean(1)))
# local alignment cor vs voc in windows
for t0 in [10,40,70,100,104,110,130,150]:
    ss=slice(int(t0*fs),int((t0+4)*fs)); 
    if ss.stop>len(cor): continue
    print(f' window {t0}s: cor vs voc lag/corr',lag(voc[ss].mean(1),cor[ss].mean(1),int(0.2*fs)))
