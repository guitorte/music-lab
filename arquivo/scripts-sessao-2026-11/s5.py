import numpy as np, soundfile as sf
from scipy import signal
fs=48000
a,_=sf.read('/home/claude/s/orig.wav'); b,_=sf.read('/home/claude/s/rem.wav')
N=min(len(a),len(b)); a=a[:N]; b=b[:N]; am=a.mean(1); bm=b.mean(1)
# lines detail
for nm,x in [('orig',am),('rem',bm)]:
    ff,P=signal.welch(x,fs,nperseg=65536); Pd=10*np.log10(P+1e-20)
    base=signal.medfilt(Pd,101); pr=Pd-base; m=(ff>2000)&(ff<20000)&(pr>6)
    # group
    groups=[];
    for fr,p in zip(ff[m],pr[m]):
        if groups and fr-groups[-1][0]<30: groups[-1]=(groups[-1][0],max(groups[-1][1],p),groups[-1][2])
        else: groups.append((fr,p,Pd[ff==fr][0]))
    print(nm,[(int(g[0]),round(g[1],1)) for g in groups])
# persistence of 12.8k line in rem: per 1s, prominence
nper=16384
for nm,x in [('orig',am),('rem',bm)]:
    f,t,S=signal.stft(x,fs,nperseg=nper,noverlap=nper//2); L=10*np.log10(np.abs(S)**2+1e-16)
    i=np.argmin(np.abs(f-12800)); nb=(np.abs(f-12800)>60)&(np.abs(f-12800)<400)
    prom=L[i]-np.median(L[nb],axis=0)
    print(nm,'12.8k prominence: % of time >6 dB:',round((prom>6).mean()*100),' median',round(np.median(prom),1))
# quiet sections: where
w=fs//10; k=N//w
la=10*np.log10((am[:k*w].reshape(k,w)**2).mean(1)+1e-14); lb=10*np.log10((bm[:k*w].reshape(k,w)**2).mean(1)+1e-14)
q=np.where(la<np.percentile(la,3))[0]
print('quiet frames (s):',np.round(q[:5]/10,1),'...',np.round(q[-5:]/10,1))
for s0,s1 in [(0,3),(206,210)]:
    sl=slice(s0*10,s1*10); print(f'{s0}-{s1}s level orig {la[sl].mean():.1f} rem {lb[sl].mean():.1f}')
# noise in breaks: find frames where orig drops >20 dB below its median but rem stays
d=lb-la; med=np.median(la)
quiet=la<med-20
print('frames where orig is >20 dB below its median:',quiet.sum(),' rem minus orig there (dB):',round(np.median(d[quiet]),1) if quiet.any() else None)
# per-section: 10 s windows, diff of 10-16k level
def bp(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); return signal.sosfiltfilt(s,x)
ha=bp(am,10000,16000); hb=bp(bm,10000,16000)
W=fs*10; print('10-16k diff per 10s window (dB):',[round(10*np.log10((hb[i:i+W]**2).mean()/(ha[i:i+W]**2).mean()),1) for i in range(0,N-W,W)])
