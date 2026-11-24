import numpy as np, soundfile as sf
from scipy import signal
fs=48000; D='/home/claude/q/w/'
voc,_=sf.read(D+'Vocais_isolados.wav'); yr=np.load(D+'part_r.npy'); yn0=np.load(D+'part_n.npy'); W0=103.0
ins,_=sf.read(D+'Instrumental.wav')
hp=lambda z: signal.sosfiltfilt(signal.butter(4,[2500,9000],'bandpass',fs=fs,output='sos'),z,axis=0)
w=int(0.005*fs)
def env(z,t0,t1,off=0):
    s=z[int((t0-off)*fs):int((t1-off)*fs)].mean(1); k=len(s)//w; return 10*np.log10((s[:k*w].reshape(k,w)**2).mean(1)+1e-14)
print('2.5-9 kHz, 5 ms steps:  time  newVoc  oldVoc  instr')
a=env(hp(yn0),105.56,105.92,W0); b=env(hp(voc),105.56,105.92); c=env(hp(ins),105.56,105.92)
for i in range(len(a)):
    t=105.56+i*0.005
    if i%2==0: print(f'   {t:7.3f} {a[i]:6.1f} {b[i]:6.1f} {c[i]:6.1f}')
