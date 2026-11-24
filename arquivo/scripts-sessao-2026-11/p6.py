import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/p/mix.wav'); m=pyln.Meter(fs)
y=x*10**((-13.0-m.integrated_loudness(x))/20)   # pre-limiter level at target, raw mix approx
def bp(z,lo,hi): return signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
w=fs//100; k=len(y)//w
pk=np.abs(y[:k*w]).max(1).reshape(k,w).max(1); over=20*np.log10(pk+1e-12)+1  # dB above -1
hot=over>2.0
print('10ms frames needing >2 dB limiting: %.2f%%'%(hot.mean()*100))
t=np.where(hot)[0]/100
print('where (s), first/last and histogram per 20 s:',np.round(t[:3],2),np.round(t[-3:],2),np.histogram(t,bins=range(0,200,20))[0])
for nm,(lo,hi) in {'sub/bass 30-120':(30,120),'low-mid 120-500':(120,500),'mid 500-4k':(500,4000),'high 4k+':(4000,20000)}.items():
    b=bp(y,lo,hi); bpk=np.abs(b[:k*w]).max(1).reshape(k,w).max(1)
    print(f'{nm}: share of peak amplitude in hot frames, median {np.median(bpk[hot]/pk[hot]):.2f}')
