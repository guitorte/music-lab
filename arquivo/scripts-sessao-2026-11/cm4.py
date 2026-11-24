import numpy as np, soundfile as sf, pyloudnorm as pyln, sys
from scipy import signal
from scipy.ndimage import minimum_filter1d, maximum_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("/home/claude/e/mix.wav","/home/claude/cm/B_ponte_up.wav"))
n=len(x); FAST=sys.argv[1]=='1'
def bp(z,lo,hi,o=2): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
y=signal.sosfiltfilt(signal.butter(2,25,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=signal.sosfiltfilt(signal.butter(2,100,'highpass',fs=fs,output='sos'),S); S=S+signal.sosfiltfilt(signal.butter(2,500,'highpass',fs=fs,output='sos'),S)*(10**(2/20)-1); y=np.stack([M+S,M-S],1)
y=eq(y,[peq(78,-1.5,1.6)])
b,a=signal.iirpeak(75,2.0,fs); band=signal.filtfilt(b,a,y,axis=0); lv=ctrl(band); thr=np.percentile(lv[lv>-90],60)
gr=env_follow(np.clip((lv-thr)*0.5,0,2.5),0.01,0.12); y=y+band*(upg(-gr,n)[:,None]-1); print('75Hz dyn avg %.1f max %.1f'%(gr.mean(),gr.max()))
y=eq(y,[peq(500,-0.8,1.0),peq(3000,2.0,0.7),shelf(9000,1.5)])
ref=ctrl(bp(y,500,2000))
for lo_,hi_ in [(2500,5000),(6000,12000)]:
    b_=bp(y,lo_,hi_); dd=ctrl(b_)-ref; th=np.percentile(dd,94)
    g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1)
lv=ctrl(y); sm=np.convolve(10**(lv/10),np.ones(int(0.05*rate))/int(0.05*rate),'same'); lv=10*np.log10(sm+1e-14)
thr=np.percentile(lv[lv>-60],85)-1.5; gr=env_follow(np.clip((lv-thr)*(1-1/1.5),0,None),0.03,0.15); y*=upg(-gr,n)[:,None]
print('glue 1.5:1 GR loud parts %.2f'%np.median(gr[lv>np.percentile(lv,90)]))
if FAST:
    pk=maximum_filter1d(np.abs(y).max(1),size=int(0.003*fs)); th=np.percentile(pk,99)
    need=np.clip(20*np.log10(np.maximum(pk,1e-9)/th),0,4); k=len(need)//H; nd=need[:k*H].reshape(k,H).max(1); nd=env_follow(nd,0.0002,0.008)
    g=np.repeat(10**(-nd/20),H); g=np.r_[g,np.full(n-len(g),g[-1])]; y=y*g[:,None]
    print('fast transient stage (<3 ms lookahead, 8 ms release): 99th %.1f, 99.9th %.1f, max %.1f dB'%(np.percentile(nd,99),np.percentile(nd,99.9),nd.max()))
for target in (-11.0,-11.5,-12.0):
    gg=target-meter.integrated_loudness(y)
    for _ in range(5):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    print(f'  target {target}: limiter GR median {np.median(grd):.2f}, 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f}')
np.save('/home/claude/cm/y_%s.npy'%sys.argv[1],y)
a2=x*10**((Lr-meter.integrated_loudness(x))/20); f,Pa=signal.welch(a2.mean(1),fs,nperseg=16384); _,Pb=signal.welch(out.mean(1),fs,nperseg=16384)
print('tone change:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [40,63,100,200,500,1000,2000,3150,5000,8000,12500]))
def vi(z): M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
mo=out.mean(1); kk=len(mo)//(fs//10); r=mo[:kk*(fs//10)].reshape(kk,-1); print('vocal idx mix %.2f master %.2f | crest %.1f (mix 10.6)'%(vi(x),vi(out),np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9))))
