import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/p/mix.wav'); n=len(x)
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
# 1 zero-phase HPF 25 Hz (no phase shift on the bass)
y=signal.sosfiltfilt(signal.butter(1,25,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=S-signal.sosfiltfilt(signal.butter(4,100,'lowpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# 2 same bass treatment
bb,ba=signal.iirpeak(61,3,fs); band=signal.lfilter(bb,ba,y,axis=0); lv=ctrl(band)
thr=np.percentile(lv[lv>-90],45); gr=env_follow(np.clip((lv-thr)*0.6,0,5),0.01,0.12); y=y+band*(upg(-gr,n)[:,None]-1)
# 3 EQ, 3 kHz reduced to +0.8
y=eq(y,[peq(60,-1.5,2.0),peq(160,-1.5,1.0),peq(463,-1.5,4),peq(707,-2.5,3),peq(3000,0.8,0.8),shelf(10000,1.5)])
ref=ctrl(bp(y,500,2000,2)); b_=bp(y,6000,12000,2); dd=ctrl(b_)-ref; th=np.percentile(dd,95)
g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1)
pre=y.copy()
# 4 peak stage: 4x-oversampled soft clipper, knee starts 2 dB below the clip point
def softclip(z,clip_db):
    up=signal.resample_poly(z,4,1,axis=0); c=10**(clip_db/20); t=c*10**(-2/20)
    a=np.abs(up); o=np.where(a>t, t+(c-t)*np.tanh((a-t)/(c-t)), a)*np.sign(up)
    return signal.resample_poly(o,1,4,axis=0)[:len(z)]
def chain(z,target,clip_db=-0.3):
    gg=target-meter.integrated_loudness(z)
    for _ in range(4):
        s=softclip(z*10**(gg/20),clip_db); out,grd=limit(s); L=meter.integrated_loudness(out); gg+=target-L
    zin=z*10**(gg/20); s=softclip(zin,clip_db)
    upi=np.abs(signal.resample_poly(zin,4,1,axis=0)).max(1); ups=np.abs(signal.resample_poly(s,4,1,axis=0)).max(1)
    w=1920; k=len(upi)//w; fi=upi[:k*w].reshape(k,w).max(1); fo=ups[:k*w].reshape(k,w).max(1)
    clipred=20*np.log10(np.maximum(fi,1e-9)/np.maximum(fo,1e-9))
    return out,grd,L,clipred
for clip_db in (-0.3,0.0,0.5):
    out,grd,L,cr=chain(pre,-13.0,clip_db)
    print(f'clip at {clip_db:+.1f} dBFS: LUFS {L:.2f} | clipper peak reduction max {cr.max():.1f} dB, 99.9th {np.percentile(cr,99.9):.1f} | limiter GR 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f}')
    if np.percentile(grd,99)<=3.0 and cr.max()<=2.5: break
sf.write('/home/claude/p/master3.wav',out,fs,subtype='PCM_24')
def vi(z):
    M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
print('vocal-range index: mix %.2f | previous master %.2f | new %.2f'%(vi(x),vi(sf.read('/home/claude/p/master2.wav')[0]),vi(out)))
a=x*10**((L-meter.integrated_loudness(x))/20)
f,Pa=signal.welch(a.mean(1),fs,nperseg=16384); _,Pb=signal.welch(out.mean(1),fs,nperseg=16384)
print('tone change vs mix:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [40,63,100,160,500,700,2000,3150,5000,10000]))
sf.write('/home/claude/p/ab3.wav',out*10**((meter.integrated_loudness(x)-L)/20),fs,subtype='PCM_24')
