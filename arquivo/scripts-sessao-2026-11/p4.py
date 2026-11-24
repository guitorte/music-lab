import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/p/mix.wav'); n=len(x)
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
y=signal.sosfilt(signal.butter(2,30,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
S=S-signal.sosfiltfilt(signal.butter(4,100,'lowpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# dynamic cut on the 60 Hz note, up to -5 dB
bb,ba=signal.iirpeak(61,3,fs); band=signal.lfilter(bb,ba,y,axis=0); lv=ctrl(band)
thr=np.percentile(lv[lv>-90],45); gr=env_follow(np.clip((lv-thr)*0.6,0,5),0.01,0.12)
y=y+band*(upg(-gr,n)[:,None]-1); print('60 Hz dyn cut avg %.1f max %.1f'%(gr.mean(),gr.max()))
y=eq(y,[peq(60,-1.5,2.0),peq(160,-1.5,1.0),peq(463,-1.5,4),peq(707,-2.5,3),peq(3000,0.8,0.8),shelf(10000,1.5)])
ref=ctrl(bp(y,500,2000,2))
for lo_,hi_ in [(2500,5000),(6000,12000)]:
    b_=bp(y,lo_,hi_,2); dd=ctrl(b_)-ref; th=np.percentile(dd,95)
    g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1)
    print(f'de-harsh {lo_}-{hi_}: max {g.max():.1f}')
for target in (-12.0,-12.5,-13.0):
    gg=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    p99=np.percentile(grd,99); print(f'target {target}: GR median {np.median(grd):.2f}, 99th {p99:.2f}, max {grd.max():.2f}')
    if p99<=3.5: break
sf.write('/home/claude/p/master.wav',out,fs,subtype='PCM_24')
a=x*10**((Lr-meter.integrated_loudness(x))/20)
f,Pa=signal.welch(a.mean(1),fs,nperseg=16384); _,Pb=signal.welch(out.mean(1),fs,nperseg=16384)
print('tone change:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [40,63,100,160,500,700,2000,3150,5000,10000]))
def vi(z):
    M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
print('vocal-range index mix %.2f master %.2f'%(vi(x),vi(out)))
sf.write('/home/claude/p/ab.wav',out*10**((meter.integrated_loudness(x)-Lr)/20),fs,subtype='PCM_24')
