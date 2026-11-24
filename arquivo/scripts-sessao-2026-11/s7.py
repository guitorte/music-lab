import numpy as np, soundfile as sf
from scipy import signal
fs=48000
a,_=sf.read('/home/claude/s/orig.wav'); b,_=sf.read('/home/claude/s/rem.wav')
N=min(len(a),len(b)); a=a[:N].mean(1); b=b[:N].mean(1)
def bp(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); return signal.sosfiltfilt(s,x)
# A) partial pitch stability: track spectral peaks frame to frame, measure inst. freq jitter via phase vocoder
nper=4096; hop=256
def ifjit(x):
    f,t,S=signal.stft(x[fs*30:fs*150],fs,nperseg=nper,noverlap=nper-hop)
    mag=np.abs(S); ph=np.angle(S)
    k=np.arange(len(f))[:,None]
    dphi=np.diff(ph,axis=1)-2*np.pi*hop*k/nper
    dphi=(dphi+np.pi)%(2*np.pi)-np.pi
    inst=(k/nper+dphi/(2*np.pi*hop))*fs  # Hz
    res=[]
    for lo,hi in [(200,1000),(1000,4000),(4000,8000)]:
        m=(f>=lo)&(f<hi); M=mag[m,1:]; I=inst[m]; F=f[m][:,None]
        # strong peaks: local maxima above 90th pct
        thr=np.percentile(M,95); pk=(M>thr)
        # jitter: abs change of inst freq between consecutive frames at peaks, in cents
        di=np.abs(np.diff(I,axis=1)); pkk=pk[:,1:]&pk[:,:-1]
        cents=1200*np.log2((I[:,1:][pkk]+di[pkk])/np.maximum(I[:,1:][pkk],1))
        res.append(round(float(np.median(cents)),2))
    return res
print('A) partial frequency jitter (cents/frame, median) 0.2-1k,1-4k,4-8k: orig',ifjit(a),' rem',ifjit(b))
# B) short-term HF flicker in steady parts: std of 5ms level after removing 100ms trend
def flick(x,lo,hi):
    y=bp(x,lo,hi); w=240; k=len(y)//w; e=10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-14)
    tr=np.convolve(e,np.ones(20)/20,'same'); d=e-tr; return round(float(np.median(np.abs(d[20:-20]))),2)
print('B) 5ms level flicker (dB) 1-4k / 4-8k / 8-16k: orig',[flick(a,*r) for r in [(1000,4000),(4000,8000),(8000,16000)]],' rem',[flick(b,*r) for r in [(1000,4000),(4000,8000),(8000,16000)]])
# C) modulation spectrum 1-4k envelope peaks
for nm,x in [('orig',a),('rem',b)]:
    e=np.abs(signal.hilbert(bp(x,1000,4000))); e=signal.decimate(signal.decimate(e,10),10); e-=e.mean()
    fm,P=signal.welch(e,480,nperseg=8192); m=(fm>8)&(fm<200); Pm=10*np.log10(P[m]); base=signal.medfilt(Pm,41); pr=Pm-base
    idx=np.argsort(pr)[-5:][::-1]; print('C) 1-4k env modulation peaks',nm,[(round(fm[m][i],1),round(pr[i],1)) for i in idx])
# D) metallic comb: cepstral peak in 3-16k log spectrum per frame
def comb(x):
    f,t,S=signal.stft(x[fs*30:fs*150],fs,nperseg=2048,noverlap=1024); m=(f>=3000)&(f<16000)
    L=np.log(np.abs(S[m])+1e-9); L-=L.mean(0); C=np.abs(np.fft.rfft(L,axis=0))
    C=C[3:]/ (np.median(C[3:],axis=0)+1e-9); return round(float(np.median(C.max(0))),2), int(np.median(np.argmax(C,axis=0)+3))
print('D) spectral ripple (cepstral peak ratio, quefrency bin): orig',comb(a),' rem',comb(b))
# E) pre-echo before HF onsets
def preecho(x):
    y=bp(x,4000,12000); w=48; k=len(y)//w; e=(y[:k*w].reshape(k,w)**2).mean(1)
    le=10*np.log10(e+1e-14); on=np.where(np.diff(le)>12)[0]
    on=on[(on>50)&(on<len(le)-50)]
    pre=[10*np.log10(e[i-20:i-2].mean()/e[i+1:i+5].mean()) for i in on]
    return len(on), round(float(np.median(pre)),1)
print('E) HF onsets count, median pre-onset energy rel. to onset (dB, 2-20ms before): orig',preecho(a),' rem',preecho(b))
