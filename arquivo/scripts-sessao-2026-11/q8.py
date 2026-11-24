import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); out=np.load(D+'out.npy')
def bl(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0); s=y[int(105*fs):int(106.1*fs)]
    return 10*np.log10((s**2).mean())
for lo,hi in [(30,200),(200,1000),(1000,4000),(4000,12000)]:
    print(f'{lo}-{hi} Hz: original {bl(mix,lo,hi):6.1f} fixed {bl(out,lo,hi):6.1f} diff {bl(out,lo,hi)-bl(mix,lo,hi):+.1f}')
# neighbour phrases level (vocal band) for reference
def seg(z,t0,t1,lo=200,hi=4000):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((t0-1)*fs):int((t1+1)*fs)],axis=0)[fs:-fs]; return 10*np.log10((y**2).mean())
print('200-4k level: phrase before (103.0-104.4) %.1f | word orig %.1f fixed %.1f | after (106.2-107.8) %.1f'%(seg(mix,103.0,104.4),seg(mix,105,106.1),seg(out,105,106.1),seg(mix,106.2,107.8)))
