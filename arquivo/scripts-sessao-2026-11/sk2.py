import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("/home/claude/e/mix.wav","/home/claude/sk/mix.wav"))
n=len(x)
def bp(z,lo,hi,o=2): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
y=signal.sosfiltfilt(signal.butter(2,30,'highpass',fs=fs,output='sos'),x,axis=0)
# mono below 100 Hz
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=signal.sosfiltfilt(signal.butter(2,100,'highpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# low end: dynamic control of bass 85-140 (max -2.5 dB), kick weight +1 dB at 60
band=bp(y,85,140); lv=ctrl(band); thr=np.percentile(lv[lv>-90],60)
gr=env_follow(np.clip((lv-thr)*0.5,0,2.5),0.01,0.12); y=y+band*(upg(-gr,n)[:,None]-1); print('bass dyn avg %.1f max %.1f'%(gr.mean(),gr.max()))
y=eq(y,[peq(60,1.0,1.2),peq(520,-1.0,0.9),peq(800,-0.5,1.4),peq(3000,0.5,0.9),shelf(9000,3.0)])
# de-harsh spikes 2.5-5k and 6-12k
ref=ctrl(bp(y,500,2000))
for lo_,hi_ in [(2500,5000),(6000,12000)]:
    b_=bp(y,lo_,hi_); dd=ctrl(b_)-ref; th=np.percentile(dd,93)
    g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1); print(f'de-harsh {lo_}-{hi_} active {(g>0.3).mean()*100:.0f}% max {g.max():.1f}')
# snare/pick attack: transient shaper on 1.5-8k, up to +2 dB
det=bp(y.mean(1),1500,8000); lv=ctrl(det); fast=env_follow(lv-lv.min(),0.001,0.02); slow=env_follow(lv-lv.min(),0.02,0.2)
boost=env_follow(np.clip((fast-slow)*0.4,0,2.0),0.0005,0.04); hb=bp(y,1500,8000); y=y+hb*(upg(boost,n)[:,None]-1)
print('transient: active %.0f%%'%((boost>0.5).mean()*100))
# glue 2:1
lv=ctrl(y); sm=np.convolve(10**(lv/10),np.ones(int(0.05*rate))/int(0.05*rate),'same'); lv=10*np.log10(sm+1e-14)
thr=np.percentile(lv[lv>-60],80)-2; gr=env_follow(np.clip((lv-thr)*0.5,0,None),0.02,0.12); y*=upg(-gr,n)[:,None]
print('glue GR loud parts %.2f'%np.median(gr[lv>np.percentile(lv,90)]))
for target in (-10.0,-10.5,-11.0,-11.5):
    gg=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    p99=np.percentile(grd,99); print(f'target {target}: GR median {np.median(grd):.2f}, 99th {p99:.2f}, max {grd.max():.2f}')
    if p99<=3.0: break
d='/home/claude/sk/'; sf.write(d+'AFLX_004_master_24bit.wav',out,fs,subtype='PCM_24')
Lx=meter.integrated_loudness(x); sf.write(d+'AFLX_004_master_AB_matched_24bit.wav',out*10**((Lx-Lr)/20),fs,subtype='PCM_24')
a2=x*10**((Lr-Lx)/20); f,Pa=signal.welch(a2.mean(1),fs,nperseg=16384); _,Pb=signal.welch(out.mean(1),fs,nperseg=16384)
print('tone change:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [50,63,100,125,250,500,800,1600,3150,5000,8000,12500,16000]))
def vi(z): M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
print('vocal-range index mix %.2f master %.2f'%(vi(x),vi(out)))
mo=out.mean(1); k=len(mo)//(fs//10); r=mo[:k*(fs//10)].reshape(k,-1); print('crest %.1f (mix 9.9)'%np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)))
print('corr %.2f'%np.corrcoef(out[:,0],out[:,1])[0,1])
