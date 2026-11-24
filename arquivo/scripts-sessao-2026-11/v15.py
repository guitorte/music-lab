import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); voc,_=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav')
w=int(0.01*fs)
def env(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z.mean(1) if z.ndim>1 else z); k=len(y)//w
    return (y[:k*w].reshape(k,w)**2).mean(1)
lo,hi=800,3000
em,ev,ei=env(mix,lo,hi),env(voc,lo,hi),env(ins,lo,hi)
seg=slice(1450,9700)  # 14.5-97 s
X=np.stack([ev[seg],ei[seg]],1); g=np.linalg.lstsq(X,em[seg],rcond=None)[0]; r=em[seg]-X@g
v=ev[seg]
print('band %d-%d: residual power vs vocal power at lag (ms) -> corr'%(lo,hi))
cs=[]
for L in range(0,80):
    a=v[:len(v)-L]; b=r[L:]; cs.append(np.corrcoef(a,b)[0,1])
cs=np.array(cs); print(' '.join(f'{L*10}:{c:.2f}' for L,c in enumerate(cs) if L%3==0))
# vocal pause test: after phrase ends, mix minus scaled ins in vocal band
for t0,t1,lab in [(97.6,98.6,'after "diabo" before drum solo'),(136.2,137.2,'after last "diabo"')]:
    s=slice(int(t0*fs),int(t1*fs)); 
    def b(z): y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((t0-0.5)*fs):int((t1+0.5)*fs)].mean(1))[int(0.5*fs):-int(0.5*fs)]; return 10*np.log10((y**2).mean()+1e-14)
    print(f'{lab}: mix {b(mix):.1f} | ins*{g[1]**.5:.2f} {b(ins*np.sqrt(g[1])):.1f} | voc stem {b(voc):.1f} dB')
