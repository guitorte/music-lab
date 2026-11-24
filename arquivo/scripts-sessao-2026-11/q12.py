import numpy as np, soundfile as sf
from scipy import signal
fs=48000; D='/home/claude/q/w/'
mix,_=sf.read(D+'Que_nem_eu_ITA.wav'); ins,_=sf.read(D+'Instrumental.wav'); voc,_=sf.read(D+'Vocais_isolados.wav')
yr=np.load(D+'part_r.npy'); W0=103.0
w=int(0.02*fs)
def env(z,t0,t1,off=0):
    s=z[int((t0-off)*fs):int((t1-off)*fs)].mean(1); k=len(s)//w; return 10*np.log10((s[:k*w].reshape(k,w)**2).mean(1)+1e-14)
t0,t1=105.56,105.90
a=env(mix,t0,t1); b=env(ins,t0,t1); c=env(yr,t0,t1,W0); d=env(voc,t0,t1)
print(' time   mix   instr  backgr(after removal)  oldVoc')
for i in range(len(a)): print(f'{t0+i*0.02:6.2f} {a[i]:6.1f} {b[i]:6.1f} {c[i]:8.1f} {d[i]:12.1f}')
# spectral check at 105.66-105.78: does the background look like the instrumental or like the old vocal?
s0,s1=int((105.66-W0)*fs),int((105.78-W0)*fs)
def spec(z): f,P=signal.welch(z,fs,nperseg=2048); return f,10*np.log10(P+1e-20)
f,Pb=spec(yr[s0:s1].mean(1)); _,Pi=spec(ins[int(105.66*fs):int(105.78*fs)].mean(1)); _,Pv=spec(voc[int(105.66*fs):int(105.78*fs)].mean(1))
m=(f>100)&(f<8000)
print('background spectrum corr with instrumental %.2f, with old vocal %.2f'%(np.corrcoef(Pb[m],Pi[m])[0,1],np.corrcoef(Pb[m],Pv[m])[0,1]))
