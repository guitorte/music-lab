import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/r/mix.wav'); n=len(x); t=np.arange(n)/fs
print('source samples at/over full scale:',int((np.abs(x)>=0.999).sum()))
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
# 1 HPF 25 Hz + mono below 100 Hz
y=signal.sosfilt(signal.butter(2,25,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
S=S-signal.sosfiltfilt(signal.butter(4,100,'lowpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# 2 sub extension: boost centred at 45 Hz, automated +2 dB (first half) -> +4 dB from ~1:35
sub=bp(y,35,60,2)
amt_db=np.interp(t,[0,90,100,t[-1]],[2,2,4,4]); g=10**(amt_db/20)-1
y=y+sub*g[:,None]
# 3 harmonics of the 40-80 Hz band so phones/small speakers "hear" the sub
lowb=bp(y.mean(1),40,80,2); up=signal.resample_poly(lowb,4,1); sc=np.abs(up).max()+1e-9
h=signal.resample_poly(np.tanh(3*up/sc)*sc,1,4)[:n]-lowb   # generated harmonics only (approx.)
h=bp(h,90,300,2); h*=np.sqrt((lowb**2).mean())/np.sqrt((h**2).mean())*10**(-12/20)
y=y+h[:,None]
# 4 tidy mids a little (mix is boxy at 500-630 and dull at 2-5 kHz)
y=eq(y,[peq(560,-1.5,1.2),peq(3500,1.5,0.8)])
# 5 kick-keyed pump: duck everything above 150 Hz on each kick, compensated so sections keep their level
kick=bp(y.mean(1),40,120); e=ctrl(kick); thr=np.percentile(e[e>-90],65)
gr=env_follow(np.clip((e-thr)*0.8,0,3.5),0.005,0.16)
gdb=-gr+uniform_filter1d(gr,size=int(1.2*rate))
hp=signal.sosfiltfilt(signal.butter(2,150,'highpass',fs=fs,output='sos'),y,axis=0); lo=y-hp
y=lo+hp*upg(gdb,n)[:,None]
print('pump: depth p5..p95 on kicks %.1f..%.1f dB'%tuple(np.percentile(gdb[e>thr],[5,95])))
# 6 limiter, choose loudness so limiting stays moderate on the sub
for target in (-11.0,-11.5,-12.0):
    gg=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    p99=np.percentile(grd,99); print(f'target {target}: GR median {np.median(grd):.2f}, 99th {p99:.2f}, max {grd.max():.2f}')
    if p99<=3.0: break
sf.write('/home/claude/r/master.wav',out,fs,subtype='PCM_24'); print('final LUFS %.2f'%Lr)
