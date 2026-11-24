import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
voc,fs=sf.read(D+'vocais_original.wav'); cor,_=sf.read(D+'vocais_fix.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
N=2048; H=480
for name,(t0,t1) in {'casal':(54.8,57.3),'achar':(67.6,70.0),'cara':(83.8,86.0)}.items():
    a=voc[int(t0*fs):int(t1*fs)].mean(1); b=cor[int(t0*fs):int(t1*fs)].mean(1)
    f,t,A=signal.stft(a,fs,nperseg=N,noverlap=N-H); _,_,B=signal.stft(b,fs,nperseg=N,noverlap=N-H)
    m=(f>100)&(f<8000); A=np.abs(A[m]); B=np.abs(B[m]); fm=f[m]
    la=np.log(A+1e-6); lb=np.log(B+1e-6)
    sim=np.array([np.corrcoef(la[:,i],lb[:,i])[0,1] for i in range(A.shape[1])])
    lv=20*np.log10(np.sqrt((A**2).mean(0))+1e-9); lc=20*np.log10(np.sqrt((B**2).mean(0))+1e-9)
    # high band (s/ch fricatives) 4-10k
    hv=20*np.log10(np.sqrt((A[fm>4000]**2).mean(0))+1e-9); hc=20*np.log10(np.sqrt((B[fm>4000]**2).mean(0))+1e-9)
    ref=max(lv.max(),lc.max())
    print(f'=== {name}   t    voc   cor  | hi>4k voc cor | sim')
    for i in range(len(t)):
        print(f'{t[i]+t0:7.2f} {lv[i]-ref:5.0f} {lc[i]-ref:5.0f}  | {hv[i]-ref:5.0f} {hc[i]-ref:5.0f} | {sim[i]:5.2f}')
