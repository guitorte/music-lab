import numpy as np, soundfile as sf, pyloudnorm as pyln, sys, subprocess
from scipy import signal
from scipy.ndimage import minimum_filter1d, maximum_filter1d
from numba import njit
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("/home/claude/e/mix.wav","/home/claude/mt/mix.wav"))
n=len(x); tt=np.arange(n)/fs
@njit
def _env(x,a,r):
    y=np.empty_like(x); e=0.0
    for i in range(len(x)):
        v=x[i]; c=a if v>e else r; e=c*e+(1-c)*v; y[i]=e
    return y
def envf(x,att,rel): return _env(np.ascontiguousarray(x),np.exp(-1/(att*fs)),np.exp(-1/(rel*fs)))
def bp(z,lo,hi,o=2): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
def transient(z,lo,hi,att_db,sus_db):
    b=bp(z,lo,hi); d=np.abs(b).max(1)+1e-9; ef=envf(d,0.0005,0.02); es=envf(d,0.02,0.2); diff=20*np.log10(ef)-20*np.log10(es)
    g=np.where(diff>0,np.clip(diff/6,0,1)*att_db,np.clip(-diff/6,0,1)*sus_db); return z-b+b*10**(g/20)[:,None]
def punch(z):
    q=signal.sosfiltfilt(signal.butter(2,[45,120],'bandpass',fs=fs,output='sos'),z.mean(1)); w=int(0.01*fs); k=len(q)//w; e=20*np.log10(np.sqrt((q[:k*w].reshape(k,w)**2).mean(1))+1e-9); return np.percentile(e,95)-np.percentile(e,50)
y=signal.sosfiltfilt(signal.butter(2,28,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=signal.sosfiltfilt(signal.butter(2,110,'highpass',fs=fs,output='sos'),S)
S=S+signal.sosfiltfilt(signal.butter(2,1000,'highpass',fs=fs,output='sos'),S)*(10**(1.5/20)-1); y=np.stack([M+S,M-S],1)
# low end: tighter surdo/kick (attack kept, tail shorter), then static trims
y=transient(y,45,120,+1.5,-2.5)
y=eq(y,[peq(63,-2.0,1.5),peq(315,-1.0,1.2),peq(1200,1.0,1.0),peq(2500,2.0,0.7),shelf(9000,2.0)])
ref=ctrl(bp(y,500,2000))
for lo_,hi_ in [(2500,5000),(6000,12000)]:
    b_=bp(y,lo_,hi_); dd=ctrl(b_)-ref; th=np.percentile(dd,94); g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1)
y=transient(y,2000,8000,+1.5,0.0)                       # percussion snap
# parallel (NY) compression for FOH density
d=np.abs(y).max(1)+1e-9; e=envf(d,0.01,0.1); lv=20*np.log10(e); thr=np.percentile(lv[lv>-60],50)
gr=np.clip((lv-thr)*(1-1/4),0,None); pc=y*10**(-gr/20)[:,None]; pc*=10**((np.median(gr[gr>0]))/20)
y=y+pc*10**(-8/20)
# glue 1.5:1, detector ignores lows
lv=ctrl(signal.sosfiltfilt(signal.butter(2,150,'highpass',fs=fs,output='sos'),y,axis=0)); thr=np.percentile(lv[lv>-60],80)-1.5
g2=env_follow(np.clip((lv-thr)*(1-1/1.5),0,None),0.03,0.17); y*=upg(-g2,n)[:,None]
# chorus lift +1 dB, entering in the stops' silence
def ride(t0,t1,up=0.12,down=1.5):
    a=np.clip((tt-t0)/up,0,1); b=np.clip((t1+down-tt)/down,0,1); w=np.minimum(a,b); return 0.5-0.5*np.cos(np.pi*w)
w=np.maximum.reduce([ride(43.36,83.0),ride(100.0,140.5),ride(143.2,157.8,up=1.0)]); y=y*10**(1.0*w/20)[:,None]
# fast transient stage (Katz: short transients)
pk=maximum_filter1d(np.abs(y).max(1),size=int(0.003*fs)); th=np.percentile(pk,99)
need=np.clip(20*np.log10(np.maximum(pk,1e-9)/th),0,4); k=len(need)//H; nd=need[:k*H].reshape(k,H).max(1); nd=env_follow(nd,0.0002,0.008)
gfs=np.repeat(10**(-nd/20),H); gfs=np.r_[gfs,np.full(n-len(gfs),gfs[-1])]; y=y*gfs[:,None]
print('fast stage: 99th %.1f, 99.9th %.1f, max %.1f dB'%(np.percentile(nd,99),np.percentile(nd,99.9),nd.max()))
np.save('/home/claude/mt/y.npy',y)
for target in (-10.0,-10.5,-11.0):
    gg=target-meter.integrated_loudness(y)
    for _ in range(6):
        out,grd=limit(y*10**(gg/20),-2.0); Lr=meter.integrated_loudness(out); gg+=target-Lr
    sf.write('/tmp/t.wav',out,fs,subtype='PCM_24'); subprocess.run('ffmpeg -hide_banner -loglevel error -y -i /tmp/t.wav -c:a aac -b:a 128k /tmp/t.m4a && ffmpeg -hide_banner -loglevel error -y -i /tmp/t.m4a -c:a pcm_f32le /tmp/t2.wav',shell=True,check=True)
    q,_=sf.read('/tmp/t2.wav'); tp=20*np.log10(np.abs(signal.resample_poly(q,4,1,axis=0)).max())
    L=lambda z,a,b: meter.integrated_loudness(z[int(a*fs):int(b*fs)])
    print(f'target {target}: limiter GR 99th {np.percentile(grd,99):.2f} max {grd.max():.2f} | AAC TP {tp:+.2f} | chorus vs verse {L(out,44,60)-L(out,16,32):+.1f} LU, stop->chorus {L(out,44,52)-L(out,36,42.3):+.1f} | surdo punch {punch(out[44*fs:80*fs]):.1f} (mix {punch(x[44*fs:80*fs]):.1f})')
