import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/p/mix.wav'); o4,_=sf.read('/home/claude/p/master4.wav')
def inst_need(z):
    up=np.abs(signal.resample_poly(z,4,1,axis=0)).max(1); need=20*np.log10(np.maximum(up,1e-9))+1
    w=1920; k=len(need)//w; return need[:k*w].reshape(k,w).max(1)
def report(nm,z):
    zz=z*10**((-13.0-meter.integrated_loudness(z))/20)
    nd=inst_need(zz); out,grd=limit(zz)
    print(f'{nm}: instantaneous need max {nd.max():.1f} dB, 10ms frames needing >3 dB: {(nd>3).sum()} | limiter envelope 99th {np.percentile(grd,99):.2f} | time with GR>1 dB {(grd>1).mean()*100:.2f}%')
report('raw mix          ',x)
# reconstruct pre-limiter of v4 by undoing nothing: rerun chain without limiter
s=open('/home/claude/scripts/p10.py').read(); s=s[:s.index('gg=-13.0')]+"np.save('/home/claude/p/pre4.npy',y)\n"
exec(s)
report('new chain pre-lim',np.load('/home/claude/p/pre4.npy'))
