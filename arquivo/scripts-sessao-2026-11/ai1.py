import numpy as np, soundfile as sf, pyloudnorm as pyln, glob, librosa
from scipy import signal
names=['vocals','drums','bass','guitar','piano','other']
def load(d): 
    S={n:sf.read(glob.glob(f'{d}/{n}*.flac')[0])[0] for n in names}; k=min(len(v) for v in S.values()); return {a:b[:k] for a,b in S.items()}
R=load('/home/claude/ref/stems'); A=load('/home/claude/ai2/stems'); fs=44100
mR=sum(R.values()); mA=sum(A.values()); m=pyln.Meter(fs)
# alignment / structure
def env(z):
    y=signal.sosfiltfilt(signal.butter(2,[100,6000],'bandpass',fs=fs,output='sos'),z.mean(1)); w=int(0.05*fs); k=len(y)//w; return np.log((y[:k*w].reshape(k,w)**2).mean(1)+1e-10)
eR,eA=env(mR),env(mA); c=signal.correlate(eA-eA.mean(),eR-eR.mean(),'full'); l=np.arange(-len(eR)+1,len(eA)); i=np.argmax(c); print('global envelope lag AI vs real: %.2f s, corr %.2f'%(l[i]*0.05,c[i]/np.sqrt(((eA-eA.mean())**2).sum()*((eR-eR.mean())**2).sum())))
vR=env(R['vocals']); vA=env(A['vocals']); print('vocal envelope corr at lag 0: %.2f'%np.corrcoef(vR,vA)[0,1])
for lab,S,mix in [('REAL',R,mR),('AI',A,mA)]:
    B={k:v[8*fs:182*fs] for k,v in S.items()}; bm=sum(B.values()); tot=m.integrated_loudness(bm)
    M=bm.mean(1); k=len(M)//(fs//10); r=M[:k*(fs//10)].reshape(k,-1); rms=np.sqrt((r**2).mean(1)); ok=rms>1e-5
    up=signal.resample_poly(mix,4,1,axis=0)
    w=3*fs; st=np.array([m.integrated_loudness(mix[j:j+w]) for j in range(0,len(mix)-w,fs)]); st=st[st>-50]
    print(f'=== {lab}: LUFS {m.integrated_loudness(mix):.1f} TP {20*np.log10(np.abs(up).max()):+.1f} | crest {np.median(20*np.log10(np.abs(r[ok]).max(1)/rms[ok])):.1f} | ST p10-p90 {np.percentile(st,90)-np.percentile(st,10):.1f} LU | corr {np.corrcoef(*mix.T)[0,1]:.2f}')
    print('    stems rel. mix:',' '.join(f'{n}:{m.integrated_loudness(B[n])-tot:+.1f}' for n in names),f'| vocal vs band {m.integrated_loudness(B["vocals"])-m.integrated_loudness(bm-B["vocals"]):+.1f}')
bands=[40,63,100,160,250,400,630,1000,1600,2500,4000,6300,10000,16000]
def sp(z):
    f,P=signal.welch(z[8*fs:182*fs].mean(1),fs,nperseg=16384); ref=P[(f>200)&(f<5000)].sum(); return np.array([10*np.log10(P[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/ref) for c in bands])
sR,sA=sp(mR),sp(mA); print('spectrum   ',' '.join(f'{c:>6}' for c in bands)); print('  real     ',' '.join(f'{v:6.1f}' for v in sR)); print('  AI       ',' '.join(f'{v:6.1f}' for v in sA)); print('  AI-real  ',' '.join(f'{v:+6.1f}' for v in sA-sR))
