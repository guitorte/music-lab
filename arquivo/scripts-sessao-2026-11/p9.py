import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
exec(open('/home/claude/scripts/p8.py').read().split('pre=y.copy()')[0]); pre=y
z=pre*10**((-13.0-meter.integrated_loudness(pre))/20)
w=480; k=len(z)//w; fp=np.abs(z[:k*w]).max(1).reshape(k,w).max(1)
hot=fp>np.percentile(fp,99.8)
bands={'30-120':(30,120),'120-500':(120,500),'500-2k':(500,2000),'2k-6k':(2000,6000),'6k+':(6000,20000)}
print('peaks: top 0.2% of 10ms frames =',hot.sum(),'frames; times (s):',np.round(np.where(hot)[0][::max(1,hot.sum()//12)]/100,1))
for nm,(lo,hi) in bands.items():
    b=bp(z,lo,hi); bf=np.abs(b[:k*w]).max(1).reshape(k,w).max(1)
    print(f' {nm:8s} peak amplitude in hot frames vs typical frames: {20*np.log10(np.median(bf[hot])/np.median(bf)):+5.1f} dB | share of frame peak {np.median(bf[hot]/fp[hot]):.2f}')
# is it the centre (vocal) or sides?
M=z.mean(1); S=(z[:,0]-z[:,1])/2
mf=np.abs(M[:k*w]).reshape(k,w).max(1); sf_=np.abs(S[:k*w]).reshape(k,w).max(1)
print(' mid/side peak ratio in hot frames: %.1f dB'%(20*np.log10(np.median(mf[hot])/np.median(sf_[hot]))))
