import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
fs=48000
a,_=sf.read('orig.wav'); b,_=sf.read('rem.wav')
print(len(a),len(b))
# alignment on 20 s middle segment
s=fs*60; L=fs*20
c=signal.correlate(b[s-fs:s+L+fs,0],a[s:s+L,0],mode='valid',method='fft')
lag=np.argmax(c)-fs; print('lag',lag, 'peak corr norm', c.max()/np.sqrt((a[s:s+L,0]**2).sum()*(b[s-fs+np.argmax(c):s-fs+np.argmax(c)+L,0]**2).sum()))
m=pyln.Meter(fs)
for n,x in [('orig',a),('rem',b)]:
    print(n,'LUFS',round(m.integrated_loudness(x),2),'peak',round(20*np.log10(np.abs(x).max()),2),'crest',round(20*np.log10(np.abs(x).max()/np.sqrt((x**2).mean())),2))
