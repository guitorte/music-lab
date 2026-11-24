import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
cor,fs=sf.read(D+'vocais_fix.wav'); voc,_=sf.read(D+'vocais_original.wav'); out=np.load(D+'out2.npy'); mix,_=sf.read(D+'track_original.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
sos=signal.butter(6,12000,'highpass',fs=fs,output='sos')
def clicks(z,t0,t1):
    y=signal.sosfiltfilt(sos,z[int(t0*fs):int(t1*fs)].mean(1)); w=int(0.002*fs); k=len(y)//w; r=y[:k*w].reshape(k,w)
    rms=np.sqrt((r**2).mean(1)); loc=np.convolve(rms,np.ones(15)/15,'same'); ratio=20*np.log10(np.abs(r).max(1)/(loc+1e-12)+1e-12)
    return [(round(t0+i*0.002,3),round(ratio[i],1)) for i in np.where(ratio>16)[0]]
print('impulsive spikes >12k (peak vs local rms > 16 dB):')
print(' fix stem casal  :',clicks(cor,55.3,57.0))
print(' orig stem casal :',clicks(voc,55.3,57.0))
print(' fix stem achar  :',clicks(cor,68.5,69.4),' cara:',clicks(cor,84.4,85.3))
print(' fix stem elsewhere 30-46s count:',len(clicks(cor,30,46)),' orig stem 30-46s:',len(clicks(voc,30,46)))
print(' OUT casal:',clicks(out,55.3,57.0),' | MIX casal:',clicks(mix,55.3,57.0))
