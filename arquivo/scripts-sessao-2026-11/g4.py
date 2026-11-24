import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import uniform_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/g/mix.wav'); n=len(x)
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
# 1 HPF + mono below 100 Hz
y=signal.sosfilt(signal.butter(2,25,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
S=S-signal.sosfiltfilt(signal.butter(4,100,'lowpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# 2 surdo accent: transient lift of the 50-110 Hz band on each hit (up to +3.5 dB, ~100 ms)
sb=bp(y,50,110,2); e=ctrl(sb.mean(1)); base=e-e.min()
fast=env_follow(base,0.002,0.03); slow=env_follow(base,0.04,0.40)
d=fast-slow; th=np.percentile(d,80)
lift=env_follow(np.clip((d-th)*0.7,0,3.5),0.002,0.10)
y=y+sb*(upg(lift,n)[:,None]-1)
print('surdo lift: active %.0f%% of time, median when active %.1f dB'%((lift>0.5).mean()*100,np.median(lift[lift>0.5])))
# 3 sub extension (moderate) + harmonics for small speakers
y=eq(y,[peq(45,2.0,0.9)])
lowb=bp(y.mean(1),50,90,2); up=signal.resample_poly(lowb,4,1); sc=np.abs(up).max()+1e-9
h=signal.resample_poly(np.tanh(3*up/sc)*sc,1,4)[:n]-lowb
h=bp(h,110,280,2); h*=np.sqrt((lowb**2).mean())/np.sqrt((h**2).mean())*10**(-14/20); y=y+h[:,None]
# 4 make room in low-mids
y=eq(y,[peq(200,-0.8,1.0)])
# 5 dynamic de-harsh: 2.5-5k and 7-12k reduced only when they spike above the mids (max -3 dB)
ref=ctrl(bp(y,500,2000,2))
for lo_,hi_,pct in [(2500,5000,95),(7000,12000,95)]:
    band=bp(y,lo_,hi_,2); dd=ctrl(band)-ref; th=np.percentile(dd,pct)
    g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.08); y=y+band*(upg(-g,n)[:,None]-1)
    print(f'de-harsh {lo_}-{hi_}: active {(g>0.3).mean()*100:.0f}% of time, max {g.max():.1f} dB')
# 6 sit the vocal back: presence dip on the MID channel only (vocal is centred), sides untouched
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
M=eq(M[:,None],[peq(2500,-1.8,0.9),peq(5000,-1.0,1.0)])[:,0]
y=np.stack([M+S,M-S],1)
# 7 limiter
for target in (-12.0,-12.5):
    gg=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    p99=np.percentile(grd,99); print(f'target {target}: GR median {np.median(grd):.2f}, 99th {p99:.2f}, max {grd.max():.2f}')
    if p99<=3.0: break
sf.write('/home/claude/g/master2.wav',out,fs,subtype='PCM_24'); print('final LUFS %.2f'%Lr)
