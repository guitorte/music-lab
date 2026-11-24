import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1)
# 1) offset between chorus 1 and chorus 2: coarse with envelopes, fine with waveform
def env(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z); w=int(0.005*fs); k=len(y)//w; return np.log((y[:k*w].reshape(k,w)**2).mean(1)+1e-10)
e=env(M,100,8000); a=e[int(15/0.005):int(56/0.005)]
best=None
for L in np.arange(42.0,46.5,0.005):
    b=e[int((15+L)/0.005):int((56+L)/0.005)][:len(a)]; c=np.corrcoef(a,b)[0,1]
    if best is None or c>best[1]: best=(L,c)
L0=best[0]; print('coarse chorus offset %.3f s (env corr %.3f)'%best)
s0=int(20*fs); n=int(20*fs); ref=M[s0:s0+n]; seg=M[s0+int((L0-0.05)*fs):s0+int((L0+0.05)*fs)+n]
c=signal.correlate(seg,ref,'valid',method='fft'); i=np.argmax(c); L=(L0-0.05)+i/fs; Ls=int(round(L*fs))
print('fine offset %.5f s = %d samples, waveform corr %.3f'%(L,Ls,c[i]/np.sqrt((ref**2).sum()*(seg[i:i+n]**2).sum())))
# 2) how identical are chorus 1 and chorus 2 along time (200 ms windows), after offset
print('t(ch1)  corr   level diff dB  (ch2 - ch1)')
for t in np.arange(40.0,59.0,0.25):
    a=x[int(t*fs):int((t+0.2)*fs)]; b=x[int(t*fs)+Ls:int((t+0.2)*fs)+Ls]
    cc=np.sum(a*b)/np.sqrt(np.sum(a*a)*np.sum(b*b)); ld=10*np.log10(np.sum(b*b)/np.sum(a*a))
    print(f' {t:5.2f}  {cc:5.2f}  {ld:+5.1f}  {"#"*int(max(cc,0)*20)}')
np.save('/home/claude/cc/Ls.npy',Ls)
