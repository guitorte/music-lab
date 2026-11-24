import numpy as np, soundfile as sf
from scipy import signal
from scipy.optimize import nnls
from scipy.ndimage import uniform_filter
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); ins,_=sf.read(D+'Instrumental.wav'); cor,_=sf.read(D+'Vocais_corrigidos.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
W0,W1=103.0,108.0                       # processing span (seconds)
A0,A1,B0,B1=104.80,104.90,106.12,106.18 # ramp in / ramp out (both vocals near-silent there)
N=2048; H=256
s=slice(int(W0*fs),int(W1*fs)); fitspan=slice(int(92*fs),int(118*fs))
out=mix.copy(); stats=[]; parts={}
for ch in (0,1):
    # power-domain fit of how much of each stem lives in the mix (robust to phase mismatch)
    f,t,Mf=signal.stft(mix[fitspan,ch],fs,nperseg=N,noverlap=N-H); _,_,Vf=signal.stft(voc[fitspan,ch],fs,nperseg=N,noverlap=N-H); _,_,If=signal.stft(ins[fitspan,ch],fs,nperseg=N,noverlap=N-H)
    tt=t+92; fit=(tt<104.7)|(tt>106.4)
    gv=np.zeros(len(f)); gi=np.zeros(len(f))
    for k in range(len(f)):
        lo,hi=max(0,k-3),min(len(f),k+4)   # pool neighbouring bins for stability
        X=np.stack([(np.abs(Vf[lo:hi][:,fit])**2).ravel(),(np.abs(If[lo:hi][:,fit])**2).ravel()],1); y=(np.abs(Mf[lo:hi][:,fit])**2).ravel()
        gv[k],gi[k]=nnls(X,y)[0]
    # processing span
    _,t2,M=signal.stft(mix[s,ch],fs,nperseg=N,noverlap=N-H); _,_,V=signal.stft(voc[s,ch],fs,nperseg=N,noverlap=N-H)
    _,_,I=signal.stft(ins[s,ch],fs,nperseg=N,noverlap=N-H); _,_,C=signal.stft(cor[s,ch],fs,nperseg=N,noverlap=N-H)
    Pv=gv[:,None]*np.abs(V)**2; Pi=gi[:,None]*np.abs(I)**2
    Pv=uniform_filter(Pv,size=(3,5)); Pi=uniform_filter(Pi,size=(3,5))     # smooth to avoid musical noise
    G=np.maximum(Pi/(Pi+Pv+1e-20),10**(-25/20))                            # Wiener removal of the old vocal, floor -25 dB
    Yr=G*M; Yn=np.sqrt(gv)[:,None]*C; Y=Yr+Yn
    _,yr=signal.istft(Yr,fs,nperseg=N,noverlap=N-H); _,yn=signal.istft(Yn,fs,nperseg=N,noverlap=N-H)
    parts.setdefault('r',[]).append(yr[:s.stop-s.start]); parts.setdefault('n',[]).append(yn[:s.stop-s.start])                                             # add corrected vocal, shaped like the original vocal in the mix
    _,y=signal.istft(Y,fs,nperseg=N,noverlap=N-H); y=y[:s.stop-s.start]
    # crossfade into the untouched original
    tl=W0+np.arange(len(y))/fs
    w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=0.5-0.5*np.cos(np.pi*w)
    out[s,ch]=mix[s,ch]*(1-w)+y*w
    # diagnostics: does the window now look like "instrumental + NEW word" rather than the old word?
    tw=(t2+W0>105.0)&(t2+W0<106.1); vb=(f>300)&(f<6000)
    _,_,O=signal.stft(out[s,ch],fs,nperseg=N,noverlap=N-H)
    lo_=np.log(np.abs(O[np.ix_(vb,tw)])+1e-7).ravel()
    new=np.log(np.sqrt(gi[vb,None]*np.abs(I[np.ix_(vb,tw)])**2+gv[vb,None]*np.abs(C[np.ix_(vb,tw)])**2)+1e-7).ravel()
    old=np.log(np.abs(M[np.ix_(vb,tw)])+1e-7).ravel()
    stats.append((np.corrcoef(lo_,new)[0,1],np.corrcoef(lo_,old)[0,1],np.corrcoef(new,old)[0,1]))
for ch,(a,b,c) in enumerate(stats): print(f'ch{ch}: output resembles NEW-word target {a:.2f} | resembles ORIGINAL {b:.2f} | (target vs original {c:.2f})')
d=out-mix; nz=np.where(np.abs(d).max(1)>0)[0]
print('samples changed from %.3f s to %.3f s'%(nz[0]/fs,nz[-1]/fs))
up=signal.resample_poly(out[int(104.5*fs):int(106.5*fs)],4,1,axis=0)
print('true peak in window %.2f dBFS (original track peak 0.00)'%(20*np.log10(np.abs(up).max())))
db=lambda z: 10*np.log10((z**2).mean())
print('level in word window: original %.1f dB, fixed %.1f dB'%(db(mix[int(105*fs):int(106.1*fs)]),db(out[int(105*fs):int(106.1*fs)])))
np.save('/home/claude/q/w/part_r.npy',np.stack(parts['r'],1)); np.save('/home/claude/q/w/part_n.npy',np.stack(parts['n'],1))
