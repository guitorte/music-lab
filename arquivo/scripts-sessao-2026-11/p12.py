import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/p/mix.wav'); y=np.load('/home/claude/p/pre4.npy')
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
gg=-14.0-meter.integrated_loudness(y)
for _ in range(4):
    out,grd=limit(y*10**(gg/20)); L=meter.integrated_loudness(out); gg+=-14.0-L
up=np.abs(signal.resample_poly(y*10**(gg/20),4,1,axis=0)).max(1); need=20*np.log10(np.maximum(up,1e-9))+1
w=1920; k=len(need)//w; nd=need[:k*w].reshape(k,w).max(1)
print(f'-14 LUFS: final {L:.2f} | instantaneous need max {nd.max():.1f} dB, frames >3 dB: {(nd>3).sum()} | GR envelope 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f} | time with GR>1 dB {(grd>1).mean()*100:.2f}%')
sf.write('/home/claude/p/master5.wav',out,fs,subtype='PCM_24')
def vi(z):
    M=z.mean(1); return 10*np.log10((bp(M,1000,4000)**2).mean()/(bp(M,150,1000)**2).mean())
print('vocal index mix %.2f new %.2f'%(vi(x),vi(out)))
sf.write('/home/claude/p/ab5.wav',out*10**((meter.integrated_loudness(x)-L)/20),fs,subtype='PCM_24')
