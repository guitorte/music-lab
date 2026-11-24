import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); ins,_=sf.read(D+'Instrumental.wav'); cor,_=sf.read(D+'Vocais_corrigidos.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]
cor=np.roll(cor,1,axis=0)   # global lag -1 sample -> shift
# gain: least squares on nearby identical regions
ref=np.r_[np.arange(int(96*fs),int(103.5*fs)),np.arange(int(107.5*fs),int(114*fs))]
g=(voc[ref]*cor[ref]).sum()/(cor[ref]**2).sum(); print('gain cor->voc %.3f (%.2f dB)'%(g,20*np.log10(g)))
c=cor*g
w=int(0.02*fs)
def fr(z,t0,t1):
    s=z[int(t0*fs):int(t1*fs)].mean(1); k=len(s)//w; return s[:k*w].reshape(k,w)
a=fr(voc,102,108.5); b=fr(c,102,108.5)
ea=10*np.log10((a**2).mean(1)+1e-14); eb=10*np.log10((b**2).mean(1)+1e-14)
d=10*np.log10(((a-b)**2).mean(1)+1e-14)
print(' t      voc   cor   diff-vs-voc')
for i in range(0,len(ea)):
    t=102+i*0.02
    mark='  <<' if (d[i]-ea[i]>-10 and ea[i]>-50) else ''
    if i%2==0 or mark: print(f'{t:7.2f} {ea[i]:6.1f} {eb[i]:6.1f} {d[i]-ea[i]:6.1f}{mark}')
