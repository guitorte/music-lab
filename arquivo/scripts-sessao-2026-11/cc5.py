import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1)
# sample-accurate lag on the last line via high-band envelope at 0.5 ms
def env(z,lo,hi,h):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z); w=max(1,int(h*fs)); k=len(y)//w; return np.log((y[:k*w].reshape(k,w)**2).mean(1)+1e-10)
best=None
for L in np.arange(43.810,43.830,0.0001):
    Ls=int(round(L*fs)); a=M[int(47*fs):int(56*fs)]; b=M[int(47*fs)+Ls:int(56*fs)+Ls]
    ea=np.abs(signal.hilbert(signal.sosfiltfilt(signal.butter(2,[2000,8000],'bandpass',fs=fs,output='sos'),a))); eb=np.abs(signal.hilbert(signal.sosfiltfilt(signal.butter(2,[2000,8000],'bandpass',fs=fs,output='sos'),b)))
    ea=np.convolve(ea,np.ones(22)/22,'same'); eb=np.convolve(eb,np.ones(22)/22,'same'); c=np.corrcoef(ea,eb)[0,1]
    if best is None or c>best[1]: best=(L,c)
L=best[0]; Ls=int(round(L*fs)); print('refined lag %.4f s (%d samples), corr %.3f'%(L,Ls,best[1]))
np.save('/home/claude/cc/Ls.npy',Ls)
# map ch1 44-50 s: vocal-band level and kick onsets, for ch1 and ch2 (shifted)
h=0.01; ev1=env(M[int(44*fs):int(50*fs)],300,3000,h); ev2=env(M[int(44*fs)+Ls:int(50*fs)+Ls],300,3000,h)
ek1=env(M[int(44*fs):int(50*fs)],40,120,h); ek2=env(M[int(44*fs)+Ls:int(50*fs)+Ls],40,120,h)
ref=max(ev1.max(),ev2.max())
print(' t(ch1)  vocal-band ch1 ch2 (dB)   kick ch1 ch2')
for i in range(0,len(ev1),2):
    print(f' {44+i*h:6.2f}   {10*(ev1[i]-ref)/np.log(10):6.1f} {10*(ev2[i]-ref)/np.log(10):6.1f}   {10*ek1[i]/np.log(10):6.1f} {10*ek2[i]/np.log(10):6.1f}')
