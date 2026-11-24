import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
D='/home/claude/vz2/w/'
mix,fs=sf.read(D+'mix.wav'); voc,_=sf.read(D+'voc.wav'); cor,_=sf.read(D+'cor.wav'); cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]
m=pyln.Meter(fs,block_size=0.2)
def ramp(A0,A1,B0,B1):
    t=np.arange(len(mix))/fs; w=np.clip((t-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-t)/(B1-B0),0,1)); return (0.5-0.5*np.cos(np.pi*w))[:,None]
# ---- transplant for "a cara": chorus1 -> L, chorus3 -> R, from the clean vocal stem
def env(z,t0,t1):
    y=signal.sosfiltfilt(signal.butter(2,[150,5000],'bandpass',fs=fs,output='sos'),z[int(t0*fs):int(t1*fs)]); w=int(0.002*fs); k=len(y)//w
    return np.maximum(10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-12),-70)
vm=voc.mean(1); ref=env(vm,84.5,85.25); offs=[]
for o in (-44.403,38.829):
    best=max(((o+d*0.001, np.corrcoef(ref,env(vm,84.5+o+d*0.001,85.25+o+d*0.001)[:len(ref)])[0,1]) for d in range(-20,21)),key=lambda q:q[1]); offs.append(best); 
print('offsets',[(round(a,3),round(c,2)) for a,c in offs])
sh=lambda o: np.roll(vm,-int(round(o*fs)))
a,b=sh(offs[0][0]),sh(offs[1][0]); M=(a+b)/2; S=(a-b)/2
sl=slice(int(84.53*fs),int(85.2*fs))
tgt=10*np.log10(((voc[sl,0]-voc[sl,1])**2).mean()/((voc[sl,0]+voc[sl,1])**2).mean()); cur=10*np.log10((S[sl]**2).mean()/(M[sl]**2).mean())
k=10**((tgt-cur)/20); T=np.stack([M+k*S,M-k*S],1); print(f'side/mid target {tgt:.1f}, k={k:.2f}')
# tonal match to chorus-2 vocal context (line 3 + after), 1/3-oct smoothed, applied via STFT
N=4096;H=1024; ctx=np.r_[np.arange(int(80.4*fs),int(84.4*fs)),np.arange(int(85.25*fs),int(89.5*fs))]
f,Pv=signal.welch(voc[ctx].mean(1),fs,nperseg=N); _,Pt=signal.welch(T[ctx].mean(1),fs,nperseg=N)
lf=np.log(np.maximum(f,20)); G=np.array([np.sqrt(Pv[np.abs(lf-lf[i])<np.log(2)/6].sum()/(Pt[np.abs(lf-lf[i])<np.log(2)/6].sum()+1e-20)) for i in range(len(f))])
print('transplant->chorus2 EQ (dB):',' '.join(f'{c}:{20*np.log10(G[(f>=c/1.2)&(f<c*1.2)].mean()):+.1f}' for c in [150,300,600,1200,2500,5000,10000]))
seg=slice(int(82*fs),int(88*fs)); Tq=T.copy()
for ch in (0,1):
    _,_,Z=signal.stft(T[seg,ch],fs,nperseg=N,noverlap=N-H); _,z=signal.istft(Z*G[:,None],fs,nperseg=N,noverlap=N-H); Tq[seg,ch]=z[:seg.stop-seg.start]
np.save(D+'transplant.npy',Tq[seg])
# ---- assemble: out = mix + w*(new - old), with per-region gain to match word loudness
R={'casal':((55.38,55.46,56.935,56.955),cor),'achar':((68.57,68.62,69.31,69.36),cor),'cara':((84.48,84.54,85.19,85.23),Tq)}
out=mix.copy(); res={}
for nm,((A0,A1,B0,B1),new) in R.items():
    w=ramp(A0,A1,B0,B1); s=slice(int((A0-0.01)*fs),int((B1+0.01)*fs)); ws=w[s]
    L0=m.integrated_loudness(mix[int(A1*fs):int(B0*fs)])
    best=None
    for g in np.arange(-3,3.01,0.25):
        o=mix[s]+ws*(new[s]*10**(g/20)-voc[s]); d=m.integrated_loudness(o[int((A1-A0+0.01)*fs):int((B0-A0+0.01)*fs)])-L0
        if best is None or abs(d)<abs(best[1]): best=(g,d,o)
    g,d,o=best; out[s]=o; res[nm]=g
    def band(z,lo,hi):
        y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((A1-0.5)*fs):int((B0+0.5)*fs)],axis=0)[int(0.5*fs):-int(0.5*fs)]; return 10*np.log10((y**2).mean())
    print(f'{nm}: gain {g:+.2f} dB -> word {d:+.2f} LU | bands vs original',' '.join(f'{lo}-{hi}:{band(out,lo,hi)-band(mix,lo,hi):+.1f}' for lo,hi in [(60,200),(200,1000),(1000,4000),(4000,12000)]))
np.save(D+'out.npy',out)
d=np.abs(out-mix).max(1); nz=np.where(d>0)[0]; sg=np.split(nz,np.where(np.diff(nz)>1)[0]+1); print('changed:',', '.join(f'{x[0]/fs:.3f}-{x[-1]/fs:.3f}' for x in sg))
up=signal.resample_poly(out,4,1,axis=0); print('TP %.2f'%(20*np.log10(np.abs(up).max())))
# "a cara" brightness vs how the word sits in choruses 1 and 3
def rel(z,o,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((79.9+o)*fs):int((85.7+o)*fs)],axis=0); a_=y[int(4.64*fs):int(5.29*fs)]; c_=y[int(0.5*fs):int(4.5*fs)]; return 10*np.log10((a_**2).mean()/(c_**2).mean())
for lab,z,o in [('chorus1',mix,offs[0][0]),('chorus3',mix,offs[1][0]),('chorus2 new',out,0)]:
    print(f'  {lab:12s} word minus line3:',' '.join(f'{lo}-{hi}:{rel(z,o,lo,hi):+.1f}' for lo,hi in [(200,1000),(1000,4000),(4000,12000)]))
