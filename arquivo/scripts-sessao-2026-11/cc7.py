import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); Ls=int(np.load('/home/claude/cc/Ls.npy'))
c0,c1=47.27,47.35; a=int(c0*fs); b=int(c1*fs); n=b-a
th=np.linspace(0,np.pi/2,n)[:,None]; fo=np.cos(th); fi=np.sin(th)   # equal-power: the two takes are uncorrelated
out=np.concatenate([x[:a], x[a:b]*fo + x[a+Ls:b+Ls]*fi, x[b+Ls:]])
print('new length %.2f s (was %.2f, removed %.3f s)'%(len(out)/fs,len(x)/fs,Ls/fs))
sf.write('/home/claude/cc/Coca_na_sem_refrao2_24bit.wav',out,fs,subtype='PCM_24')
m=pyln.Meter(fs,block_size=0.4)
def mom(z,t): return m.integrated_loudness(z[int((t-0.2)*fs):int((t+0.2)*fs)])
print('momentary loudness around the splice (new file) vs original refrão 2 at the same musical spot:')
for dt in np.arange(-1.0,1.01,0.25):
    t=c0+dt; print(f'  {dt:+.2f}s  new {mom(out,t):6.1f}  orig-ch1 {mom(x,t):6.1f}  orig-ch2 {mom(x,t+Ls/fs):6.1f}')
# discontinuity check: sample-to-sample jump at splice vs typical
d=np.abs(np.diff(out[a-200:b+200],axis=0)).max(); typ=np.percentile(np.abs(np.diff(out[a-fs:a],axis=0)),99.9); print('max step near splice %.4f vs 99.9th pct of preceding second %.4f'%(d,typ))
