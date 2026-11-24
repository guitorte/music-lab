import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.optimize import nnls
from scipy.ndimage import uniform_filter
D='/home/claude/vz/w/'; O='/home/claude/vz/final/'
mix,fs=sf.read(D+'track_original.wav'); voc,_=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav')
o1,o3=np.load(D+'offs.npy')
def env(z,t0,t1):
    y=signal.sosfiltfilt(signal.butter(2,[150,5000],'bandpass',fs=fs,output='sos'),z[int(t0*fs):int(t1*fs)]); w=int(0.002*fs); k=len(y)//w
    return np.maximum(10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-12),-70)
ref=env(voc.mean(1),84.5,85.25)
def refine(o):
    best=None
    for d in range(-15,16):
        c=np.corrcoef(ref,env(voc.mean(1),84.5+o+d*0.002,85.25+o+d*0.002)[:len(ref)])[0,1]
        if best is None or c>best[1]: best=(o+d*0.002,c)
    return best
(o1,c1),(o3,c3)=refine(o1),refine(o3); print(f'refined offsets c1 {o1:+.3f} ({c1:.2f})  c3 {o3:+.3f} ({c3:.2f})')
sh=lambda o: np.roll(voc.mean(1),-int(round(o*fs)))
a,b=sh(o1),sh(o3)
# build a double: L from chorus1, R from chorus3, then set side/mid to the original chorus-2 value
M=(a+b)/2; S=(a-b)/2
def sm(z,t0,t1): s=z[int(t0*fs):int(t1*fs)]; return 10*np.log10(((s[:,0]-s[:,1])**2).mean()/((s[:,0]+s[:,1])**2).mean())
target=sm(voc,84.53,85.20); cur=10*np.log10((S[int(84.53*fs):int(85.2*fs)]**2).mean()/(M[int(84.53*fs):int(85.2*fs)]**2).mean())
k=10**((target-cur)/20); C=np.stack([M+k*S,M-k*S],1); print(f'side/mid target {target:.1f} dB, transplant raw {cur:.1f} -> scaled k={k:.2f}')
np.save(D+'transplant.npy',C[int(80*fs):int(90*fs)])
Cz=np.zeros_like(C); Cz[int(80*fs):int(90*fs)]=C[int(80*fs):int(90*fs)]; C=Cz
# same removal/insert pipeline, but the inserted vocal is the singer's own stem, so no take-to-take transfer
A0,A1,B0,B1=84.48,84.54,85.19,85.23
N=2048;H=256; W0,W1=A0-1,B1+1; s=slice(int(W0*fs),int(W1*fs)); F0,F1=A0-7,B1+7; fsp=slice(int(F0*fs),int(F1*fs))
yr_,yn_=[],[]
for ch in (0,1):
    f,t,Mf=signal.stft(mix[fsp,ch],fs,nperseg=N,noverlap=N-H); _,_,Vf=signal.stft(voc[fsp,ch],fs,nperseg=N,noverlap=N-H); _,_,If=signal.stft(ins[fsp,ch],fs,nperseg=N,noverlap=N-H)
    tt=t+F0; fit=(tt<A0-0.2)|(tt>B1+0.2); gv=np.zeros(len(f)); gi=np.zeros(len(f))
    for kk in range(len(f)):
        lo,hi=max(0,kk-3),min(len(f),kk+4)
        X=np.stack([(np.abs(Vf[lo:hi][:,fit])**2).ravel(),(np.abs(If[lo:hi][:,fit])**2).ravel()],1); gv[kk],gi[kk]=nnls(X,(np.abs(Mf[lo:hi][:,fit])**2).ravel())[0]
    _,_,Cf=signal.stft(C[fsp,ch],fs,nperseg=N,noverlap=N-H)
    ctx=((tt>80.4)&(tt<84.4))|((tt>85.25)&(tt<89.5)); pv=(np.abs(Vf[:,ctx])**2).mean(1); pc=(np.abs(Cf[:,ctx])**2).mean(1)
    lf=np.log(np.maximum(f,20)); T=np.array([np.sqrt(pv[np.abs(lf-lf[kk])<np.log(2)/6].sum()/(pc[np.abs(lf-lf[kk])<np.log(2)/6].sum()+1e-20)) for kk in range(len(f))])
    if ch==0: print('transfer transplant->chorus2 (dB):',' '.join(f'{c}:{20*np.log10(T[(f>=c/1.2)&(f<c*1.2)].mean()):+.1f}' for c in [150,300,600,1200,2500,5000,10000]))
    _,_,Mm=signal.stft(mix[s,ch],fs,nperseg=N,noverlap=N-H); _,_,V=signal.stft(voc[s,ch],fs,nperseg=N,noverlap=N-H); _,_,I=signal.stft(ins[s,ch],fs,nperseg=N,noverlap=N-H); _,_,Cc=signal.stft(C[s,ch],fs,nperseg=N,noverlap=N-H)
    Pv=uniform_filter(gv[:,None]*np.abs(V)**2,size=(3,5)); Pi=uniform_filter(gi[:,None]*np.abs(I)**2,size=(3,5)); G=np.maximum(Pi/(Pi+Pv+1e-20),10**(-25/20))
    _,yr=signal.istft(G*Mm,fs,nperseg=N,noverlap=N-H); _,yn=signal.istft((np.sqrt(gv)*T)[:,None]*Cc,fs,nperseg=N,noverlap=N-H)
    yr_.append(yr[:s.stop-s.start]); yn_.append(yn[:s.stop-s.start])
yr=np.stack(yr_,1); yn=np.stack(yn_,1)
tl=W0+np.arange(len(yr))/fs; w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
m=pyln.Meter(fs,block_size=0.2); seg=lambda z: z[int((A1-W0)*fs):int((B0-W0)*fs)]; L0=m.integrated_loudness(seg(mix[s]))
best=None
for g in np.arange(-3,3.01,0.25):
    o=mix[s]*(1-w)+(yr+yn*10**(g/20))*w; d=m.integrated_loudness(seg(o))-L0
    if best is None or abs(d)<abs(best[1]): best=(g,d,o)
g,d,o=best
out3=np.load(D+'out3.npy'); orig_cara_mix=mix.copy()
out4=out3.copy(); out4[int(84.3*fs):int(85.5*fs)]=mix[int(84.3*fs):int(85.5*fs)]  # drop the AI-take cara edit
out4[s]=np.where(w>0,o,out4[s]); 
print(f'transplant gain {g:+.2f} dB -> word loudness {d:+.2f} LU')
def band(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int(84*fs):int(86*fs)],axis=0)[int(0.54*fs):int(1.19*fs)]; return 10*np.log10((y**2).mean())
print('bands vs original:',' '.join(f'{lo}-{hi}:{band(out4,lo,hi)-band(mix,lo,hi):+.1f}' for lo,hi in [(60,200),(200,1000),(1000,4000),(4000,12000)]))
ts=np.arange(84.54,85.0,0.1); print('200ms diffs:',' '.join(f'{m.integrated_loudness(out4[int(t*fs):int((t+.2)*fs)])-m.integrated_loudness(mix[int(t*fs):int((t+.2)*fs)]):+.1f}' for t in ts))
print('L/R corr in word: orig %.2f new %.2f'%(np.corrcoef(*mix[int(84.54*fs):int(85.19*fs)].T)[0,1],np.corrcoef(*out4[int(84.54*fs):int(85.19*fs)].T)[0,1]))
up=signal.resample_poly(out4,4,1,axis=0); print('TP %.2f'%(20*np.log10(np.abs(up).max())))
np.save(D+'out4.npy',out4)
d=np.abs(out4-mix).max(1); nz=np.where(d>0)[0]; sg=np.split(nz,np.where(np.diff(nz)>1)[0]+1); print('changed:',', '.join(f'{x[0]/fs:.3f}-{x[-1]/fs:.3f}' for x in sg))
