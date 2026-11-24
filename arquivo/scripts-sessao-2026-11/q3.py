import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
voc,fs=sf.read(D+'Vocais_isolados.wav'); cor,_=sf.read(D+'Vocais_corrigidos.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
t0,t1=96,114
a=voc[int(t0*fs):int(t1*fs)].mean(1); b=cor[int(t0*fs):int(t1*fs)].mean(1)
f,t,A=signal.stft(a,fs,nperseg=2048,noverlap=2048-480); _,_,B=signal.stft(b,fs,nperseg=2048,noverlap=2048-480)
m=(f>100)&(f<8000); A=np.abs(A[m]); B=np.abs(B[m])
la=np.log(A+1e-6); lb=np.log(B+1e-6)
sim=np.array([np.corrcoef(la[:,i],lb[:,i])[0,1] for i in range(A.shape[1])])
lev=20*np.log10(np.sqrt((A**2).mean(0))+1e-9); levb=20*np.log10(np.sqrt((B**2).mean(0))+1e-9)
# smooth over 3 frames
sim_s=np.convolve(sim,np.ones(3)/3,'same')
print('baseline similarity in voiced frames (96-103.5 & 108-114):',np.round(np.median(sim_s[((t+t0<103.5)|(t+t0>108))&(lev>lev.max()-40)]),3))
voiced=(lev>lev.max()-40)|(levb>levb.max()-40)
print(' time   sim   levV  levC')
for i in range(len(t)):
    tt=t[i]+t0
    if 103.0<=tt<=110.0 and i%2==0: print(f'{tt:7.2f} {sim_s[i]:5.2f} {lev[i]-lev.max():6.1f} {levb[i]-levb.max():6.1f} {"*" if voiced[i] and sim_s[i]<0.75 else ""}')
