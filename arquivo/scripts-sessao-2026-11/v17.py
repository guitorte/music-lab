import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
D='/home/claude/vz/w/'; O='/home/claude/vz/final/'
mix,fs=sf.read(D+'track_original.wav'); out2=np.load(D+'out2.npy'); P=np.load(D+'parts.npy',allow_pickle=True)
name,W0,yr,yn=[p for p in P if p[0]=='casal'][0]
def shelf(f0,g,Q=0.707):
    A=10**(g/40); w=2*np.pi*f0/fs; c=np.cos(w); al=np.sin(w)/(2*Q); sA=2*np.sqrt(A)*al
    b=[A*((A+1)+(A-1)*c+sA),-2*A*((A-1)+(A+1)*c),A*((A+1)+(A-1)*c-sA)]; a=[(A+1)-(A-1)*c+sA,2*((A-1)-(A+1)*c),(A+1)-(A-1)*c-sA]
    return np.array(b)/a[0],np.array(a)/a[0]
b,a=shelf(5000,-3.0); ynB=signal.filtfilt(b,a,yn,axis=0)   # undo ~half of the +6 dB high transfer
A0,A1,B0,B1=55.38,55.46,56.935,56.955
s=slice(int(W0*fs),int(W0*fs)+len(yr)); tl=W0+np.arange(len(yr))/fs
w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
m=pyln.Meter(fs,block_size=0.2); seg=lambda z: z[int((A1-W0)*fs):int((B0-W0)*fs)]; L0=m.integrated_loudness(seg(mix[s]))
best=None
for g in np.arange(-1,3.01,0.25):
    o=mix[s]*(1-w)+(yr+ynB*10**(g/20))*w; d=m.integrated_loudness(seg(o))-L0
    if best is None or abs(d)<abs(best[1]): best=(g,d,o)
g,d,o=best; out3=out2.copy(); out3[s]=o; print('v2 casal gain %+.2f -> %+.2f LU'%(g,d))
np.save(D+'out3.npy',out3)
t0,t1=53.3,58.3; c=lambda z: z[int(t0*fs):int(t1*fs)]
gap=np.zeros((int(0.8*fs),2))
sf.write(O+'casal_v1_vs_v2.wav',np.r_[c(out2),gap,c(out3)],fs,subtype='PCM_24')
# diagnostics: new voice alone and bed alone, over the replaced span with short fades
k=slice(int((55.2-W0)*fs),int((57.1-W0)*fs)); fade=np.ones(k.stop-k.start); n=int(0.02*fs); fade[:n]=np.linspace(0,1,n); fade[-n:]=np.linspace(1,0,n)
sf.write(O+'diag_casal_voz_nova_sozinha.wav',(ynB*10**(g/20))[k]*fade[:,None],fs,subtype='PCM_24')
sf.write(O+'diag_casal_instrumental_sem_voz_antiga.wav',yr[k]*fade[:,None],fs,subtype='PCM_24')
up=signal.resample_poly(out3,4,1,axis=0); print('TP %.2f'%(20*np.log10(np.abs(up).max())))
