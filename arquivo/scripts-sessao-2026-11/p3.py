import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/p/mix.wav'); m=x.mean(1); H=32; rate=fs/H
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z)
# surdo: strongest periodic low hits 40-150 Hz; find fundamental by spectrum of onset-gated frames
lo=bp(m,40,150); k=len(lo)//H; e=10*np.log10((lo[:k*H].reshape(k,H)**2).mean(1)+1e-14)
pk=signal.find_peaks(e,height=np.percentile(e,85),distance=int(0.25*rate),prominence=6)[0]
print('low hits found:',len(pk))
spec=np.zeros(4097)
for p in pk[:400]:
    s=m[p*H:p*H+8192]
    if len(s)==8192: spec+=np.abs(np.fft.rfft(s*np.hanning(8192)))**2
f=np.fft.rfftfreq(8192,1/fs); mm=(f>35)&(f<200); top=np.argsort(spec[mm])[-5:][::-1]
print('hit spectrum peaks (Hz):',[round(f[mm][i],1) for i in top])
iv=np.diff(pk)/rate; iv=iv[(iv>0.25)&(iv<2.5)]
print('inter-hit interval median %.3f s -> %.1f hits/min'%(np.median(iv),60/np.median(iv)))
# hit decay in 40-150 band: ms to fall 10 dB
dec=[]
for p in pk:
    seg=e[p:p+int(rate*0.8)]; w=np.where(seg<e[p]-10)[0]
    if len(w): dec.append(w[0]/rate*1000)
print('median decay to -10 dB: %.0f ms'%np.median(dec))
# harshness: 2-5 kHz short-term peaks vs 500-2k; and 8-12k
def env(z,w=480):
    kk=len(z)//w; return 10*np.log10((z[:kk*w].reshape(kk,w)**2).mean(1)+1e-14)
a=env(bp(m,2500,5000)); b=env(bp(m,500,2000)); c=env(bp(m,7000,12000))
print('2.5-5k minus 0.5-2k: median %.1f, p99 %.1f | 7-12k minus 0.5-2k: median %.1f, p99 %.1f'%(np.median(a-b),np.percentile(a-b,99),np.median(c-b),np.percentile(c-b,99)))
