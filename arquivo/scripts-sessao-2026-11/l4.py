import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d
x,fs=sf.read('/home/claude/l/mix.wav'); meter=pyln.Meter(fs); rng=np.random.default_rng(7)
H=32; rate=fs/H
def rbj_peak(f0,g,Q):
    A=10**(g/40); w=2*np.pi*f0/fs; c=np.cos(w); al=np.sin(w)/(2*Q)
    b=[1+al*A,-2*c,1-al*A]; a=[1+al/A,-2*c,1-al/A]; return np.array(b)/a[0],np.array(a)/a[0]
def env_follow(v,att,rel):
    out=np.empty_like(v); c=0.0; aa=np.exp(-1/(att*rate)); ar=np.exp(-1/(rel*rate))
    for i,s in enumerate(v): c=s+(c-s)*(aa if s>c else ar); out[i]=c
    return out
def ctrl(sig):
    k=len(sig)//H; return 10*np.log10((sig[:k*H].reshape(k,H,-1)**2).mean((1,2))+1e-14)
def upg(gdb,n): g=np.repeat(10**(gdb/20),H); return np.r_[g,np.full(n-len(g),g[-1])]
def dyn_cut(y,f0,Q,maxcut):
    bb,ba=signal.iirpeak(f0,Q,fs); band=signal.lfilter(bb,ba,y,axis=0); lv=ctrl(band)
    thr=np.percentile(lv[lv>-90],50); gr=env_follow(np.clip((lv-thr)*0.6,0,maxcut),0.01,0.12)
    return y+band*(upg(-gr,len(y))[:,None]-1), gr.mean()
def limit(z,ceil_db=-1.0):
    up=signal.resample_poly(z,4,1,axis=0); pk=np.abs(up).max(1).reshape(-1,4).max(1)[:len(z)]
    pk=np.r_[pk,np.full(len(z)-len(pk),pk[-1])]; gl=np.minimum(1,10**(ceil_db/20)/np.maximum(pk,1e-9))
    gl=minimum_filter1d(gl,size=2*int(0.005*fs)+1); k=len(gl)//H
    grd=env_follow(-20*np.log10(gl[:k*H].reshape(k,H).min(1)),0.0005,0.08)
    gs=np.repeat(10**(-grd/20),H); gs=np.r_[gs,np.full(len(z)-len(gs),gs[-1])]; return z*np.minimum(gs,gl)[:,None], grd
def master(y,target=-12.0):
    g=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(g/20)); L=meter.integrated_loudness(out); g+=target-L
    return out,grd
# ---------- quality base ----------
y=signal.sosfilt(signal.butter(2,25,'highpass',fs=fs,output='sos'),x,axis=0)
y,c1=dyn_cut(y,63,4,4); y,c2=dyn_cut(y,125,4,4)
b,a=rbj_peak(3000,2,0.7); base=signal.lfilter(b,a,y,axis=0)
print(f'dyn cuts avg: 63Hz {c1:.1f} dB, 125Hz {c2:.1f} dB')
# ---------- lo-fi blocks ----------
def bandlimit(y,hp,lp,order):
    y=signal.sosfilt(signal.butter(2,hp,'highpass',fs=fs,output='sos'),y,axis=0)
    return signal.sosfilt(signal.butter(order,lp,'lowpass',fs=fs,output='sos'),y,axis=0)
def tape(y,drive,wet):
    up=signal.resample_poly(y,4,1,axis=0); s=np.max(np.abs(up))+1e-9; u=up/s
    sat=(np.tanh(drive*(u+0.15))-np.tanh(drive*0.15))/drive*s
    w=signal.resample_poly(sat,1,4,axis=0)[:len(y)]
    rms=lambda z: np.sqrt((z**2).mean()); w*=rms(y)/rms(w)
    return y*(1-wet)+w*wet
def wowflutter(y,wow_pct,flut_pct):
    n=len(y); t=np.arange(n)/fs
    D=wow_pct/100/(2*np.pi*0.55)*np.sin(2*np.pi*0.55*t+rng.uniform(0,6)) + flut_pct/100/(2*np.pi*6.3)*np.sin(2*np.pi*6.3*t)
    idx=np.clip(np.arange(n)-(D+0.005)*fs,0,n-1)
    return np.stack([np.interp(idx,np.arange(n),y[:,c]) for c in range(y.shape[1])],1)
def noise_bed(n,lp,rel_db,crackle_rate,ref):
    w=rng.standard_normal(n); P=np.fft.rfft(w); fr=np.fft.rfftfreq(n,1/fs); P/=np.sqrt(np.maximum(fr,20)/1000)
    hiss=np.fft.irfft(P,n); hiss=signal.sosfilt(signal.butter(4,lp,'lowpass',fs=fs,output='sos'),hiss)
    hiss*=np.sqrt((ref**2).mean())*10**(rel_db/20)/np.sqrt((hiss**2).mean())
    cr=np.zeros(n)
    if crackle_rate>0:
        k=rng.poisson(crackle_rate*n/fs); pos=rng.integers(0,n,k); cr[pos]=rng.uniform(-1,1,k)*rng.pareto(3,k)
        cr=signal.sosfilt(signal.butter(2,[800,min(lp,6000)],'bandpass',fs=fs,output='sos'),cr)
        cr*=np.sqrt((ref**2).mean())*10**((rel_db+4)/20)/ (np.sqrt((cr**2).mean())+1e-12)
    z=hiss+cr; return np.stack([z,z],1)
versions={}
versions['1_clean']=base.copy()
v=bandlimit(base,40,10000,2); v=tape(v,2.0,0.35); v=wowflutter(v,0.10,0.03)
versions['2_lofi_light']=v+noise_bed(len(v),10000,-50,0,v)
v=bandlimit(base,60,7500,4); v=tape(v,3.5,0.6); v=wowflutter(v,0.25,0.06)
versions['3_lofi_heavy']=v+noise_bed(len(v),7500,-42,5,v)
for k,v in versions.items():
    out,grd=master(v); sf.write(f'/home/claude/l/{k}.wav',out,fs,subtype='PCM_24')
    print(k,'LUFS',round(meter.integrated_loudness(out),2),'limiter GR median/max',round(float(np.median(grd)),2),round(float(grd.max()),2))
