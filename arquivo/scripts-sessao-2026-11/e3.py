import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d
x,fs=sf.read('/home/claude/e/mix.wav'); meter=pyln.Meter(fs); H=32; rate=fs/H
def peq(f0,g,Q):
    A=10**(g/40); w=2*np.pi*f0/fs; c=np.cos(w); al=np.sin(w)/(2*Q)
    return np.array([1+al*A,-2*c,1-al*A])/(1+al/A), np.array([1+al/A,-2*c,1-al/A])/(1+al/A)
def shelf(f0,g,Q=0.707):
    A=10**(g/40); w=2*np.pi*f0/fs; c=np.cos(w); al=np.sin(w)/(2*Q); sA=2*np.sqrt(A)*al
    b=[A*((A+1)+(A-1)*c+sA),-2*A*((A-1)+(A+1)*c),A*((A+1)+(A-1)*c-sA)]; a=[(A+1)-(A-1)*c+sA,2*((A-1)-(A+1)*c),(A+1)-(A-1)*c-sA]
    return np.array(b)/a[0],np.array(a)/a[0]
def eq(z,specs):
    for b,a in specs: z=signal.lfilter(b,a,z,axis=0)
    return z
def env_follow(v,att,rel):
    out=np.empty_like(v); c=0.0; aa=np.exp(-1/(att*rate)); ar=np.exp(-1/(rel*rate))
    for i,s in enumerate(v): c=s+(c-s)*(aa if s>c else ar); out[i]=c
    return out
def ctrl(sig):
    s=sig if sig.ndim==2 else sig[:,None]; k=len(s)//H; return 10*np.log10((s[:k*H].reshape(k,H,-1)**2).mean((1,2))+1e-14)
def upg(gdb,n): g=np.repeat(10**(gdb/20),H); return np.r_[g,np.full(n-len(g),g[-1])]
def limit(z,ceil_db=-1.0):
    up=signal.resample_poly(z,4,1,axis=0); pk=np.abs(up).max(1).reshape(-1,4).max(1)[:len(z)]
    pk=np.r_[pk,np.full(len(z)-len(pk),pk[-1])]; gl=np.minimum(1,10**(ceil_db/20)/np.maximum(pk,1e-9))
    gl=minimum_filter1d(gl,size=2*int(0.005*fs)+1); k=len(gl)//H
    grd=env_follow(-20*np.log10(gl[:k*H].reshape(k,H).min(1)),0.0005,0.08)
    gs=np.repeat(10**(-grd/20),H); gs=np.r_[gs,np.full(len(z)-len(gs),gs[-1])]; return z*np.minimum(gs,gl)[:,None], grd
# 1 HPF 30 Hz
y=signal.sosfilt(signal.butter(2,30,'highpass',fs=fs,output='sos'),x,axis=0)
# 2 dynamic EQ on the 63-72 Hz bass resonance cluster, max -3 dB
bb,ba=signal.iirpeak(67,3,fs); band=signal.lfilter(bb,ba,y,axis=0); lv=ctrl(band)
thr=np.percentile(lv[lv>-90],55); gr=env_follow(np.clip((lv-thr)*0.6,0,3),0.01,0.12)
y=y+band*(upg(-gr,len(y))[:,None]-1); print('bass dynEQ avg cut %.1f dB'%gr.mean())
# 3 tone: body up, box down, attack up
y=eq(y,[peq(140,2.0,1.0),peq(315,-2.0,1.2),peq(700,-1.5,1.4),peq(4000,2.5,0.8),shelf(12000,1.0)])
# 4 M/S focus: centre the percussive attack band (2-8 kHz): side -3 dB, mid +1 dB
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
sos=signal.butter(2,[2000,8000],'bandpass',fs=fs,output='sos')
S=S+signal.sosfiltfilt(sos,S)*(10**(-3/20)-1); M=M+signal.sosfiltfilt(sos,M)*(10**(1/20)-1)
y=np.stack([M+S,M-S],1)
# 5 transient shaper (impact): fast vs slow envelope on 150 Hz-8 kHz, boost attacks up to +3 dB
det=signal.sosfiltfilt(signal.butter(2,[150,8000],'bandpass',fs=fs,output='sos'),y.mean(1))
lv=ctrl(det); fast=env_follow(lv-lv.min(),0.001,0.02); slow=env_follow(lv-lv.min(),0.02,0.20)
boost=np.clip((fast-slow)*0.5,0,3.0); boost=env_follow(boost,0.0005,0.04)
y=y*upg(boost,len(y))[:,None]; print('transient boost: active %.0f%% of time, median when active %.1f dB'%((boost>0.5).mean()*100,np.median(boost[boost>0.5])))
pre=y.copy()
# 6 limiter to target
target=-11.5; g=target-meter.integrated_loudness(y)
for _ in range(4):
    out,grd=limit(y*10**(g/20)); Lr=meter.integrated_loudness(out); g+=target-Lr
print('final LUFS %.2f, limiter GR median %.2f / 99th %.2f / max %.2f'%(Lr,np.median(grd),np.percentile(grd,99),grd.max()))
sf.write('/home/claude/e/master.wav',out,fs,subtype='PCM_24')
