import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("/home/claude/e/mix.wav","/home/claude/vr/mix_clean.wav"))
n=len(x); old,_=sf.read('/home/claude/v/master.wav')
print('source samples at/near full scale (>-0.1 dBFS):',int((np.abs(x)>10**(-0.1/20)).sum()))
def bp(z,lo,hi,o=2): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
# ---- 1) match EQ toward the first master's tonal balance (first 150 s, same arrangement), smoothed and capped
N=16384; f,Px=signal.welch(x[:len(old)].mean(1),fs,nperseg=N); _,Po=signal.welch(old.mean(1),fs,nperseg=N)
Px/=Px[(f>200)&(f<5000)].sum(); Po/=Po[(f>200)&(f<5000)].sum()
lf=np.log2(np.maximum(f,10)); g=np.array([10*np.log10(Po[np.abs(lf-l)<1/3].sum()/Px[np.abs(lf-l)<1/3].sum()) for l in lf])   # 2/3-oct smoothing
g=np.clip(g,-4,4); g[f<25]=g[np.argmin(np.abs(f-25))]; g[f>18000]=g[np.argmin(np.abs(f-18000))]
taps=8191; fir=signal.firwin2(taps,f/(fs/2),10**(g/20)); y=signal.fftconvolve(x,fir[:,None],mode='full')[taps//2:taps//2+n]
print('match EQ (dB):',' '.join(f'{c}:{g[np.argmin(np.abs(f-c))]:+.1f}' for c in [40,63,100,200,500,1000,2000,3150,5000,8000,12500,16000]))
y=signal.sosfiltfilt(signal.butter(2,28,'highpass',fs=fs,output='sos'),y,axis=0)
# ---- 2) width toward the first master: mono <100 Hz, side +2.5 dB above 300 Hz
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=signal.sosfiltfilt(signal.butter(2,100,'highpass',fs=fs,output='sos'),S)
S=S+signal.sosfiltfilt(signal.butter(2,300,'highpass',fs=fs,output='sos'),S)*(10**(2.5/20)-1); y=np.stack([M+S,M-S],1)
# ---- 3) same dynamics as the first master's line: 63 Hz dynamic control, de-harsh, light glue
b,a=signal.iirpeak(63,2.5,fs); band=signal.filtfilt(b,a,y,axis=0); lv=ctrl(band); thr=np.percentile(lv[lv>-90],60)
gr=env_follow(np.clip((lv-thr)*0.5,0,2.5),0.01,0.12); y=y+band*(upg(-gr,n)[:,None]-1); print('63Hz dyn avg %.1f max %.1f'%(gr.mean(),gr.max()))
ref=ctrl(bp(y,500,2000))
for lo_,hi_ in [(2500,5000),(6000,12000)]:
    b_=bp(y,lo_,hi_); dd=ctrl(b_)-ref; th=np.percentile(dd,94)
    gg=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-gg,n)[:,None]-1)
lv=ctrl(y); sm=np.convolve(10**(lv/10),np.ones(int(0.05*rate))/int(0.05*rate),'same'); lv=10*np.log10(sm+1e-14)
thr=np.percentile(lv[lv>-60],85)-1.5; gr=env_follow(np.clip((lv-thr)*(1-1/1.5),0,None),0.03,0.15); y*=upg(-gr,n)[:,None]
print('glue GR loud parts %.2f'%np.median(gr[lv>np.percentile(lv,90)]))

from scipy.ndimage import maximum_filter1d
def which_band(z):
    # at the 0.5% loudest 1 ms peaks, how much of the waveform peak comes from each band
    M=z.mean(1); b={'<150':signal.sosfiltfilt(signal.butter(4,150,'lowpass',fs=fs,output='sos'),M),'150-2k':signal.sosfiltfilt(signal.butter(4,[150,2000],'bandpass',fs=fs,output='sos'),M),'>2k':signal.sosfiltfilt(signal.butter(4,2000,'highpass',fs=fs,output='sos'),M)}
    idx=np.where(np.abs(M)>np.percentile(np.abs(M),99.95))[0]
    return {k:round(float(np.mean(v[idx]*np.sign(M[idx]))/np.mean(np.abs(M[idx]))),2) for k,v in b.items()}
print('share of the biggest peaks by band (before):',which_band(y))
def pkctl(M,lo=None,hi=None,pct=99.5,maxdb=6,rel=0.04):
    sos=signal.butter(2,hi,'lowpass',fs=fs,output='sos') if lo is None else signal.butter(2,lo,'highpass',fs=fs,output='sos')
    bnd=signal.sosfiltfilt(sos,M); pk=maximum_filter1d(np.abs(bnd),size=int(0.003*fs)); thr=np.percentile(pk,pct)
    need=np.clip(20*np.log10(np.maximum(pk,1e-9)/thr),0,maxdb); k=len(need)//H; nd=need[:k*H].reshape(k,H).max(1); nd=env_follow(nd,0.0003,rel)
    g=np.repeat(10**(-nd/20),H); g=np.r_[g,np.full(len(M)-len(g),g[-1])]; return M-bnd+bnd*g, nd
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
M,nh=pkctl(M,lo=2000,pct=99.3); print('HF (>2k) peak control: active %.2f%%, 99.9th %.1f, max %.1f dB'%((nh>0.5).mean()*100,np.percentile(nh,99.9),nh.max()))
M,nl=pkctl(M,hi=150,pct=99.5,rel=0.08); print('LF (<150) peak control: active %.2f%%, 99.9th %.1f, max %.1f dB'%((nl>0.5).mean()*100,np.percentile(nl,99.9),nl.max()))
y=np.stack([M+S,M-S],1)
print('share after:',which_band(y))

import sys
MODE=sys.argv[1]
y0=y.copy()
def midctl(y,pct,maxdb):
    M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
    bnd=signal.sosfiltfilt(signal.butter(2,[150,2000],'bandpass',fs=fs,output='sos'),M); pk=maximum_filter1d(np.abs(bnd),size=int(0.003*fs)); thr=np.percentile(pk,pct)
    need=np.clip(20*np.log10(np.maximum(pk,1e-9)/thr),0,maxdb); k=len(need)//H; nd=need[:k*H].reshape(k,H).max(1); nd=env_follow(nd,0.0003,0.03)
    g=np.repeat(10**(-nd/20),H); g=np.r_[g,np.full(len(M)-len(g),g[-1])]; M=M-bnd+bnd*g; return np.stack([M+S,M-S],1), nd
def fastlim(z,ceil_rel):
    # stage 1: 1.5 ms lookahead, 8 ms release, only shaves transient tips
    pk=maximum_filter1d(np.abs(z).max(1),size=int(0.003*fs)); thr=np.percentile(pk,100-ceil_rel)
    need=np.clip(20*np.log10(np.maximum(pk,1e-9)/thr),0,4); k=len(need)//H; nd=need[:k*H].reshape(k,H).max(1); nd=env_follow(nd,0.0002,0.008)
    g=np.repeat(10**(-nd/20),H); g=np.r_[g,np.full(len(z)-len(g),g[-1])]; return z*g[:,None], nd
if MODE=='a': y,nd=midctl(y,99.5,4); print('mid peak control: 99.9th %.1f max %.1f dB'%(np.percentile(nd,99.9),nd.max()))
if MODE=='b': y,nd=fastlim(y,1.0); print('fast stage: 99th %.1f 99.9th %.1f max %.1f dB'%(np.percentile(nd,99),np.percentile(nd,99.9),nd.max()))
if MODE=='ab':
    y,nd=midctl(y,99.5,4); print('mid peak control: 99.9th %.1f max %.1f dB'%(np.percentile(nd,99.9),nd.max()))
    y,nd=fastlim(y,1.0); print('fast stage: 99th %.1f 99.9th %.1f max %.1f dB'%(np.percentile(nd,99),np.percentile(nd,99.9),nd.max()))
for target in (-11.0,-11.5,-12.0):
    gg=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    print(f'  target {target}: main limiter GR median {np.median(grd):.2f}, 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f}')
def vi(z): M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
mo=out.mean(1); kk=len(mo)//(fs//10); r=mo[:kk*(fs//10)].reshape(kk,-1); print('  crest %.1f, vocal idx %.2f'%(np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)),vi(out)))
np.save('/home/claude/vr/yc_%s.npy'%MODE,y)
