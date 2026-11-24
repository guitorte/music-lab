import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
voc,fs=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav')
def lag(a,b,maxl):
    c=signal.correlate(b,a,'full',method='fft'); l=np.arange(-len(a)+1,len(b)); m=np.abs(l)<=maxl; i=np.argmax(c[m]); return l[m][i], c[m][i]/np.sqrt((a**2).sum()*(b[max(0,l[m][i]):][:len(a)]**2).sum())
# reference: chorus2 lines 1-3 (74.8-84.3) vs chorus1 and chorus3
ref=voc[int(74.8*fs):int(84.3*fs)].mean(1)
for lab,guess in [('chorus1',30.4),('chorus3',113.4),('chorus1b',41.6),('chorus3b',124.6)]:
    seg=voc[int((guess-0.6)*fs):int((guess+9.5+0.6)*fs)].mean(1)
    c=signal.correlate(seg,ref,'valid',method='fft'); i=np.argmax(c); st=guess-0.6+i/fs
    print(f'{lab}: chorus2 74.8 aligns to {st:.4f} (offset {st-74.8:+.4f}) corr {c[i]/np.sqrt((ref**2).sum()*(seg[i:i+len(ref)]**2).sum()):.2f}')
# instrumental repeat check with the same offsets
