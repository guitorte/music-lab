import numpy as np, soundfile as sf, pyloudnorm as pyln, sys
from scipy import signal
from scipy.ndimage import minimum_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("/home/claude/e/mix.wav","/home/claude/pg/w/newmix_b.wav"))
n=len(x)
def bp(z,lo,hi,o=2): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
y=signal.sosfiltfilt(signal.butter(2,25,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=signal.sosfiltfilt(signal.butter(2,100,'highpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# surdo kept: only a light dynamic trim on the boomiest hits (max 1.5 dB), no static cut
y=eq(y,[peq(63,-1.0,1.5),peq(250,-0.8,1.2),peq(2500,1.5,0.8),shelf(10000,1.5)])
ref=ctrl(bp(y,500,2000))
for lo_,hi_ in [(2500,5000),(6000,12000)]:
    b_=bp(y,lo_,hi_); dd=ctrl(b_)-ref; th=np.percentile(dd,95)
    g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1)
# groove glue: 1.5:1, slow attack (30 ms) lets the hits through, release ~ a 16th at ~89 BPM
lv=ctrl(signal.sosfiltfilt(signal.butter(2,150,'highpass',fs=fs,output='sos'),y,axis=0)); thr=np.percentile(lv[lv>-60],80)-1.5; gr=env_follow(np.clip((lv-thr)*(1-1/1.5),0,None),0.03,0.17); y*=upg(-gr,n)[:,None]
print('glue GR loud parts %.2f'%np.median(gr[lv>np.percentile(lv,90)]))
tt=np.arange(n)/fs
def ride(t0,t1,up=0.12,down=1.5):
    a=np.clip((tt-t0)/up,0,1); b=np.clip((t1+down-tt)/down,0,1); w=np.minimum(a,b); return 0.5-0.5*np.cos(np.pi*w)
w=np.maximum(ride(43.68,81.5),ride(104.95,142.5)); y=y*10**(1.0*w/20)[:,None]
np.save('/home/claude/pg/w/y_b.npy',y)
for target in (-11.0,-11.5,-12.0):
    gg=target-meter.integrated_loudness(y)
    for _ in range(5):
        out,grd=limit(y*10**(gg/20),-2.0); Lr=meter.integrated_loudness(out); gg+=target-Lr
    print(f'  target {target}: limiter GR median {np.median(grd):.2f}, 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f}')
