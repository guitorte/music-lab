import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1)
def env(z,lo,hi,h):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z); w=max(1,int(round(h*fs))); k=len(y)//w; return np.log((y[:k*w].reshape(k,w)**2).mean(1)+1e-10)
h=0.0005; t0,t1=47.0,56.5
res=[]
for lo,hi in [(40,120),(2000,8000),(300,3000)]:
    e=env(M,lo,hi,h); a=e[int(t0/h):int(t1/h)]; best=None
    for k in range(int(43.79/h),int(43.85/h)):
        b=e[int(t0/h)+k:int(t0/h)+k+len(a)]; c=np.corrcoef(a,b)[0,1]
        if best is None or c>best[1]: best=(k*h,c)
    res.append(best); print(f'{lo}-{hi}: lag {best[0]:.4f} corr {best[1]:.3f}')
L=np.median([r[0] for r in res]); Ls=int(round(L*fs)); print('using lag %.4f s = %d samples'%(L,Ls)); np.save('/home/claude/cc/Ls.npy',Ls)
h=0.01; ev1=env(M[int(46*fs):int(49*fs)],300,3000,h); ev2=env(M[int(46*fs)+Ls:int(49*fs)+Ls],300,3000,h)
ek1=env(M[int(46*fs):int(49*fs)],40,120,h); ek2=env(M[int(46*fs)+Ls:int(49*fs)+Ls],40,120,h); ref=max(ev1.max(),ev2.max())
d=lambda v: 10*v/np.log(10)
print(' t(ch1)  vocal ch1  ch2 |  kick ch1  ch2')
for i in range(len(ev1)):
    print(f' {46+i*h:6.2f}  {d(ev1[i]-ref):6.1f} {d(ev2[i]-ref):6.1f} | {d(ek1[i]):6.1f} {d(ek2[i]):6.1f}')
