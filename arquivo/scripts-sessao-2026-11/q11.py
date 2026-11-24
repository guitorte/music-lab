import numpy as np, soundfile as sf
from scipy import signal
fs=48000; D='/home/claude/q/w/'
mix,_=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); cor,_=sf.read(D+'Vocais_corrigidos.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
yr=np.load(D+'part_r.npy'); yn=np.load(D+'part_n.npy'); W0=103.0
def peq(f0,g,Q):
    A=10**(g/40); w0=2*np.pi*f0/fs; c=np.cos(w0); al=np.sin(w0)/(2*Q)
    return np.array([1+al*A,-2*c,1-al*A])/(1+al/A), np.array([1+al/A,-2*c,1-al/A])/(1+al/A)
b1,a1=peq(450,1.5,0.7); b2,a2=peq(2500,-1.5,0.9); yn=signal.filtfilt(b2,a2,signal.filtfilt(b1,a1,yn,axis=0),axis=0)
np.save(D+'part_n_eq.npy',yn)
w=int(0.02*fs)
def env(z,t0,t1):
    s=z[int(t0*fs):int(t1*fs)].mean(1); k=len(s)//w; return 10*np.log10((s[:k*w].reshape(k,w)**2).mean(1)+1e-14)
def envw(z,t0,t1): # z indexed from W0
    s=z[int((t0-W0)*fs):int((t1-W0)*fs)].mean(1); k=len(s)//w; return 10*np.log10((s[:k*w].reshape(k,w)**2).mean(1)+1e-14)
def hp(z,f0): return signal.sosfiltfilt(signal.butter(2,f0,'highpass',fs=fs,output='sos'),z,axis=0)
t0,t1=104.96,106.60
n=envw(yn,t0,t1); bg=envw(yr,t0,t1); nh=envw(hp(yn,2000),t0,t1)
vo=env(voc,t0,t1); co=env(cor,t0,t1); voh=env(hp(voc,2000),t0,t1); coh=env(hp(cor,2000),t0,t1)
print(' time  newVoc  backgr  V/B   | stems: orig  corr | >2k: orig  corr')
for i in range(len(n)):
    t=t0+i*0.02
    print(f'{t:6.2f} {n[i]:7.1f} {bg[i]:7.1f} {n[i]-bg[i]:5.1f}  | {vo[i]:6.1f} {co[i]:6.1f} | {voh[i]:6.1f} {coh[i]:6.1f}')
