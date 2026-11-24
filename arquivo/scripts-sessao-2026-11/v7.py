import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.optimize import nnls
from scipy.ndimage import uniform_filter, uniform_filter1d
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); voc,_=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav'); cor,_=sf.read(D+'vocais_fix.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
N=2048; H=256
# name: (ramp-in start, end, ramp-out start, end)
R={'casal':(55.38,55.46,56.85,56.93),'achar':(68.57,68.62,69.31,69.36),'cara':(84.47,84.53,85.20,85.24)}
parts={}
for name,(A0,A1,B0,B1) in R.items():
    W0,W1=A0-1.0,B1+1.0; s=slice(int(W0*fs),int(W1*fs))
    F0,F1=A0-7,B1+7; fsp=slice(int(F0*fs),int(F1*fs))
    pr,pn=[],[]
    for ch in (0,1):
        f,t,Mf=signal.stft(mix[fsp,ch],fs,nperseg=N,noverlap=N-H); _,_,Vf=signal.stft(voc[fsp,ch],fs,nperseg=N,noverlap=N-H)
        _,_,If=signal.stft(ins[fsp,ch],fs,nperseg=N,noverlap=N-H); _,_,Cf=signal.stft(cor[fsp,ch],fs,nperseg=N,noverlap=N-H)
        tt=t+F0; fit=(tt<A0-0.2)|(tt>B1+0.2)
        gv=np.zeros(len(f)); gi=np.zeros(len(f))
        for k in range(len(f)):
            lo,hi=max(0,k-3),min(len(f),k+4)
            X=np.stack([(np.abs(Vf[lo:hi][:,fit])**2).ravel(),(np.abs(If[lo:hi][:,fit])**2).ravel()],1); y=(np.abs(Mf[lo:hi][:,fit])**2).ravel()
            gv[k],gi[k]=nnls(X,y)[0]
        # transfer fixed-take -> original-take, from long-term spectra in the context (different takes, so smooth heavily)
        pv=(np.abs(Vf[:,fit])**2).mean(1); pc=(np.abs(Cf[:,fit])**2).mean(1)
        lf=np.log(np.maximum(f,20)); T=np.zeros(len(f))
        for k in range(len(f)):
            m=np.abs(lf-lf[k])<np.log(2)/6
            T[k]=np.sqrt(pv[m].sum()/(pc[m].sum()+1e-20))
        _,t2,M=signal.stft(mix[s,ch],fs,nperseg=N,noverlap=N-H); _,_,V=signal.stft(voc[s,ch],fs,nperseg=N,noverlap=N-H)
        _,_,I=signal.stft(ins[s,ch],fs,nperseg=N,noverlap=N-H); _,_,C=signal.stft(cor[s,ch],fs,nperseg=N,noverlap=N-H)
        Pv=uniform_filter(gv[:,None]*np.abs(V)**2,size=(3,5)); Pi=uniform_filter(gi[:,None]*np.abs(I)**2,size=(3,5))
        G=np.maximum(Pi/(Pi+Pv+1e-20),10**(-25/20))
        _,yr=signal.istft(G*M,fs,nperseg=N,noverlap=N-H); _,yn=signal.istft((np.sqrt(gv)*T)[:,None]*C,fs,nperseg=N,noverlap=N-H)
        pr.append(yr[:s.stop-s.start]); pn.append(yn[:s.stop-s.start])
        if ch==0: print(f'{name}: transfer fix->orig by band (dB):',' '.join(f'{c}:{20*np.log10(T[(f>=c/1.2)&(f<c*1.2)].mean()):+.1f}' for c in [150,300,600,1200,2500,5000,10000]))
    parts[name]=(W0,np.stack(pr,1),np.stack(pn,1))
np.save(D+'parts.npy',np.array([(k,)+v for k,v in parts.items()],dtype=object),allow_pickle=True)
