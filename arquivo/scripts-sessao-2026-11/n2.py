import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/n/in.wav')
M=(x[:,0]+x[:,1])/2; S=(x[:,0]-x[:,1])/2
def floor(sig,t0,t1,nper=4096):
    f,t,Z=signal.stft(sig[int(t0*fs):int(t1*fs)],fs,nperseg=nper,noverlap=nper*3//4); L=10*np.log10(np.abs(Z)**2+1e-16)
    return f,np.percentile(L,5,axis=1)
cent=[1000,2000,4000,6000,8000,10000,12000,14000,16000,17000,18000,19000,20000,22000]
for nm,sig in [('mid',M),('side',S)]:
    f,a=floor(sig,0,15); _,b=floor(sig,160,175)
    print(nm,'floor early | late | growth:')
    print('  '+' '.join(f'{c//1000}k:{a[np.argmin(abs(f-c))]:.0f}|{b[np.argmin(abs(f-c))]:.0f}|{b[np.argmin(abs(f-c))]-a[np.argmin(abs(f-c))]:+.0f}' for c in cent))
# is the noise steady/continuous? check its level in 16-20k frames over a late 10s: fraction of time near floor
sos=signal.butter(6,[16500,20500],'bandpass',fs=fs,output='sos'); y=signal.sosfiltfilt(sos,M)
w=fs//50; seg=y[160*fs:175*fs]; k=len(seg)//w; lv=10*np.log10((seg[:k*w].reshape(k,w)**2).mean(1)+1e-16)
print('late 16.5-20.5k level spread (20ms frames) p5/p50/p95:',np.round(np.percentile(lv,[5,50,95]),1))
seg=y[0:15*fs]; k=len(seg)//w; lv=10*np.log10((seg[:k*w].reshape(k,w)**2).mean(1)+1e-16)
print('early p5/p50/p95:',np.round(np.percentile(lv,[5,50,95]),1))
