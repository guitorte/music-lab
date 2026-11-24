import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import maximum_filter1d
exec(open('/home/claude/scripts/p8.py').read().split('pre=y.copy()')[0].replace('peq(3000,0.8,0.8)','peq(3000,1.1,0.8)'))
# 4 high-band peak control on the centre channel (2-16 kHz), sample-accurate with 1.5 ms lookahead
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
hb=signal.sosfiltfilt(signal.butter(2,2000,'highpass',fs=fs,output='sos'),M); rest=M-hb
pk=maximum_filter1d(np.abs(hb),size=int(0.003*fs))       # peak envelope with ~1.5 ms lookahead
thr=np.percentile(pk,99.5)
need=np.clip(20*np.log10(np.maximum(pk,1e-9)/thr),0,8)     # dB to remove above threshold (ratio inf)
# smooth: instant attack, 40 ms release (control-rate)
k=len(need)//H; nd=need[:k*H].reshape(k,H).max(1); nd=env_follow(nd,0.0003,0.04)
g=np.repeat(10**(-nd/20),H); g=np.r_[g,np.full(len(M)-len(g),g[-1])]
M=rest+hb*g; y=np.stack([M+S,M-S],1)
print('HF peak control: active %.2f%% of time, max %.1f dB, 99.9th pct %.1f dB'%((nd>0.5).mean()*100,nd.max(),np.percentile(nd,99.9)))
gg=-13.0-meter.integrated_loudness(y)
for _ in range(4):
    out,grd=limit(y*10**(gg/20)); L=meter.integrated_loudness(out); gg+=-13.0-L
print(f'limiter: LUFS {L:.2f}, GR median {np.median(grd):.2f}, 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f}')
sf.write('/home/claude/p/master4.wav',out,fs,subtype='PCM_24')
def vi(z):
    M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
print('vocal-range index: mix %.2f | previous master %.2f | new %.2f'%(vi(x),vi(sf.read('/home/claude/p/master2.wav')[0]),vi(out)))
a=x*10**((L-meter.integrated_loudness(x))/20)
f,Pa=signal.welch(a.mean(1),fs,nperseg=16384); _,Pb=signal.welch(out.mean(1),fs,nperseg=16384)
print('tone change vs mix:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [40,63,100,160,500,700,2000,3150,5000,10000]))
sf.write('/home/claude/p/ab4.wav',out*10**((meter.integrated_loudness(x)-L)/20),fs,subtype='PCM_24')
