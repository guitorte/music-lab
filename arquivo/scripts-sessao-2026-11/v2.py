import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
voc,fs=sf.read(D+'vocais_original.wav'); cor,_=sf.read(D+'vocais_fix.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
a=voc.mean(1); b=cor.mean(1)
f,t,A=signal.stft(a,fs,nperseg=2048,noverlap=2048-960); _,_,B=signal.stft(b,fs,nperseg=2048,noverlap=2048-960)
m=(f>100)&(f<8000); A=np.abs(A[m]); B=np.abs(B[m])
la=np.log(A+1e-6); lb=np.log(B+1e-6)
sim=np.array([np.corrcoef(la[:,i],lb[:,i])[0,1] for i in range(A.shape[1])]); sim=np.convolve(sim,np.ones(5)/5,'same')
lev=20*np.log10(np.sqrt((A**2).mean(0))+1e-9); levb=20*np.log10(np.sqrt((B**2).mean(0))+1e-9)
lev-=np.percentile(lev,99); levb-=np.percentile(levb,99)
# per 0.5 s summary
step=0.5; k=int(step/(960/fs))
print(' t    levV  levC  sim')
for i in range(0,len(t)-k,k):
    sl=slice(i,i+k); v=(lev[sl]>-35)|(levb[sl]>-35)
    s=np.median(sim[sl][v]) if v.any() else np.nan
    print(f'{t[i]:6.1f} {lev[sl].max():5.0f} {levb[sl].max():5.0f} {s:5.2f} {"*" if v.any() and s<0.7 else ""}')
