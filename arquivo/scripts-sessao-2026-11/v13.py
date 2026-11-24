import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); cor,_=sf.read(D+'vocais_fix.wav'); voc,_=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav')
cor=np.r_[cor,np.zeros((len(mix)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
def bl(z,t0,t1,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,min(hi,23000)],'bandpass',fs=fs,output='sos'),z[int((t0-0.3)*fs):int((t1+0.3)*fs)].mean(1))[int(0.3*fs):-int(0.3*fs)]
    return 10*np.log10((y**2).mean()+1e-16)
print('what is in the fix stem at 140-148 s (no vocals there)? corr of 10ms envelopes with instrumental bands')
def envs(z,t0,t1,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int(t0*fs):int(t1*fs)].mean(1)); w=int(0.01*fs); k=len(y)//w
    return np.log((y[:k*w].reshape(k,w)**2).mean(1)+1e-14)
for lo,hi in [(60,200),(200,1000),(1000,5000),(5000,15000)]:
    print(f'  {lo}-{hi}: corr fix~ins {np.corrcoef(envs(cor,140,148,lo,hi),envs(ins,140,148,lo,hi))[0,1]:.2f}')
print('energy above 14 kHz (dB) in 20 ms steps: fix stem | orig stem | instrumental')
for t in np.arange(55.60,56.30,0.02):
    print(f' {t:.2f}  fix {bl(cor,t,t+0.02,14000,22000):6.1f}  orig {bl(voc,t,t+0.02,14000,22000):6.1f}  ins {bl(ins,t,t+0.02,14000,22000):6.1f} | 2-8k fix {bl(cor,t,t+0.02,2000,8000):6.1f} ins {bl(ins,t,t+0.02,2000,8000):6.1f}')
# drum hits (instrumental onsets in 4-12k) near 55.5-57
y=signal.sosfiltfilt(signal.butter(4,[4000,12000],'bandpass',fs=fs,output='sos'),ins[int(54*fs):int(58*fs)].mean(1)); w=int(0.01*fs); k=len(y)//w
e=10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-14); on=np.where(np.diff(e)>6)[0]
print('instrumental hi-hat/snare onsets:',[round(54+(o+1)*0.01,2) for o in on])
