import numpy as np, soundfile as sf
from scipy import signal
fs=48000
a,_=sf.read('/home/claude/s/orig.wav'); b,_=sf.read('/home/claude/s/rem.wav')
N=min(len(a),len(b)); a=a[:N].mean(1); b=b[:N].mean(1)
nper=2048; hop=512
def spec(x):
    f,t,S=signal.stft(x,fs,nperseg=nper,noverlap=nper-hop); return f,t,np.abs(S)**2+1e-14
f,t,A=spec(a); _,_,B=spec(b)
LA=10*np.log10(A); LB=10*np.log10(B)
print('1) Floor (10th pct over time) vs median level, by band [orig | rem] dB')
for lo,hi in [(100,500),(500,2000),(2000,5000),(5000,10000),(10000,16000)]:
    m=(f>=lo)&(f<hi)
    fa=np.percentile(LA[m].mean(0),10); fb=np.percentile(LB[m].mean(0),10)
    ma=np.median(LA[m].mean(0)); mb=np.median(LB[m].mean(0))
    print(f'{lo:5d}-{hi:5d}: floor {fa:6.1f} | {fb:6.1f}   median {ma:6.1f} | {mb:6.1f}   floor-to-median gap {ma-fa:5.1f} | {mb-fb:5.1f}')
# quietest 2% frames overall: what's the spectrum there
lev=10*np.log10(A.sum(0)); q=lev<np.percentile(lev,3)
print('\n2) quietest 3% frames, HF energy relative to full-band level of those frames')
for nm,L,S in [('orig',LA,A),('rem',LB,B)]:
    tot=10*np.log10(S[:,q].sum(0)).mean(); hf=10*np.log10(S[(f>4000),:][:,q].sum(0)).mean(); print(nm,'HF share dB',round(hf-tot,1),' abs quiet level',round(tot,1))
# 3) modulation spectrum of HF envelope
print('\n3) modulation spectrum of 4-12k envelope: strongest peaks 5-150 Hz')
def bp(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); return signal.sosfiltfilt(s,x)
for nm,x in [('orig',a),('rem',b)]:
    e=np.abs(signal.hilbert(bp(x,4000,12000)))
    e=signal.decimate(signal.decimate(e,10),10)  # 480 Hz
    e=e-np.mean(e)
    fm,P=signal.welch(e,480,nperseg=4096)
    m=(fm>5)&(fm<150); Pm=10*np.log10(P[m]); fmm=fm[m]
    base=signal.medfilt(Pm,31); pr=Pm-base
    idx=np.argsort(pr)[-6:][::-1]
    print(nm,[(round(fmm[i],1),round(pr[i],1)) for i in idx])
# 4) tonal lines: persistent narrow peaks in long-term spectrum
print('\n4) persistent narrow spectral lines (long-term, >6 dB above local median), 2-20 kHz')
for nm,x in [('orig',a),('rem',b)]:
    ff,P=signal.welch(x,fs,nperseg=65536); Pd=10*np.log10(P+1e-20)
    base=signal.medfilt(Pd,101); pr=Pd-base; m=(ff>2000)&(ff<20000)&(pr>6)
    print(nm,len(ff[m]),[int(v) for v in ff[m][:20]])
# 5) harmonic peakiness (spectral contrast) in 200-4000: peak-to-valley within 1/3 oct, median over time
print('\n5) harmonic definition: median peak-to-valley within bands (higher = cleaner partials)')
for lo,hi in [(200,1000),(1000,4000),(4000,8000)]:
    m=(f>=lo)&(f<hi)
    ca=np.median(np.percentile(LA[m],95,axis=0)-np.percentile(LA[m],20,axis=0))
    cb=np.median(np.percentile(LB[m],95,axis=0)-np.percentile(LB[m],20,axis=0))
    print(f'{lo}-{hi}: orig {ca:.1f}  rem {cb:.1f}')
