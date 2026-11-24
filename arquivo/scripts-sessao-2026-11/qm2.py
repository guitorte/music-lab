import numpy as np, soundfile as sf, pyloudnorm as pyln, subprocess
from scipy import signal
from scipy.ndimage import minimum_filter1d
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("x,fs=sf.read('/home/claude/e/mix.wav')","x,fs=sf.read('/home/claude/q/final/Que_nem_eu_ITA_quantum_fixed_v4_24bit.wav')"))
n=len(x)
def bp(z,lo,hi,o=2): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
y=signal.sosfiltfilt(signal.butter(2,27,'highpass',fs=fs,output='sos'),x,axis=0)
# 50 Hz build-up: static -1.5 dB + dynamic up to -3 dB on loudest hits
y=eq(y,[peq(50,-1.5,2.0)])
b,a=signal.iirpeak(50,2.5,fs); band=signal.filtfilt(b,a,y,axis=0); lv=ctrl(band); thr=np.percentile(lv[lv>-90],60)
gr=env_follow(np.clip((lv-thr)*0.5,0,3),0.01,0.12); y=y+band*(upg(-gr,n)[:,None]-1); print('50Hz dyn cut avg %.1f max %.1f'%(gr.mean(),gr.max()))
# tone: slight warmth control and air
y=eq(y,[peq(250,-1.0,1.4),peq(3500,1.0,0.8),shelf(10000,1.5)])
# M/S: mono below 120, side +1.5 dB 3-12k
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
S=signal.sosfiltfilt(signal.butter(2,120,'highpass',fs=fs,output='sos'),S)
S=S+bp(S,3000,12000)*(10**(1.5/20)-1); y=np.stack([M+S,M-S],1)
# de-harsh on spikes 5-10k
ref=ctrl(bp(y,500,2000)); b_=bp(y,5000,10000); dd=ctrl(b_)-ref; th=np.percentile(dd,94)
g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1); print('de-harsh active %.0f%% max %.1f'%((g>0.3).mean()*100,g.max()))
# glue 1.5:1 on loud parts
lv=ctrl(y); sm=np.convolve(10**(lv/10),np.ones(int(0.05*rate))/int(0.05*rate),'same'); lv=10*np.log10(sm+1e-14)
thr=np.percentile(lv[lv>-60],85)-1.5; gr=env_follow(np.clip((lv-thr)*(1-1/1.5),0,None),0.03,0.15); y*=upg(-gr,n)[:,None]
print('glue GR loud parts %.2f'%np.median(gr[lv>np.percentile(lv,90)]))
for target in (-12.5,-13.0,-13.5):
    gg=target-meter.integrated_loudness(y)
    for _ in range(4):
        out,grd=limit(y*10**(gg/20)); Lr=meter.integrated_loudness(out); gg+=target-Lr
    p99=np.percentile(grd,99); print(f'target {target}: GR median {np.median(grd):.2f}, 99th {p99:.2f}, max {grd.max():.2f}')
    if p99<=3.0: break
d='/home/claude/qm/'; sf.write(d+'Que_nem_eu_ITA_master_24bit.wav',out,fs,subtype='PCM_24')
Lx=meter.integrated_loudness(x)
sf.write(d+'Que_nem_eu_ITA_master_AB_matched_24bit.wav',out*10**((Lx-Lr)/20),fs,subtype='PCM_24')
a2=x*10**((Lr-Lx)/20); f,Pa=signal.welch(a2.mean(1),fs,nperseg=16384); _,Pb=signal.welch(out.mean(1),fs,nperseg=16384)
print('tone change:',' '.join(f'{c}:{10*np.log10(Pb[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()/Pa[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()):+.1f}' for c in [40,50,63,100,250,500,1000,2000,3500,6300,10000,14000]))
def vi(z): M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
print('vocal-range index mix %.2f master %.2f'%(vi(x),vi(out)))
mo=out.mean(1); k=len(mo)//(fs//10); r=mo[:k*(fs//10)].reshape(k,-1); print('crest %.1f'%np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)))
print('corr %.2f'%np.corrcoef(out[:,0],out[:,1])[0,1])
