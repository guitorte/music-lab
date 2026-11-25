# A = original (edit.wav), B = original + pad + plucks. Mesma intro suave da v2 nas duas (−2,5 dB e topo −2 dB até 9,0 s, cruza até 9,6 s).
import numpy as np, soundfile as sf
from scipy import signal
fs=44100; src,_=sf.read('/home/claude/mt/edit.wav',always_2d=True); N=len(src)
pad=sf.read('/home/claude/sy/pad.wav',always_2d=True)[0][:N]; plk=sf.read('/home/claude/sy/pluck.wav',always_2d=True)[0][:N]
def intro(z):
    soft=signal.sosfiltfilt(signal.butter(1,4000,'lowpass',fs=fs,output='sos'),z,axis=0)
    soft=z+(soft-z)*(1-10**(-2/20))                 # ~−2 dB acima de 4 kHz
    soft=soft*10**(-2.5/20); t=np.arange(len(z))/fs; w=np.clip((t-9.0)/0.6,0,1)[:,None]
    return soft*(1-w)+z*w
for nm,z in [('A_original',src),('B_com_sintetizadores',src+pad+plk)]:
    y=intro(z); pk=np.abs(y).max()
    if pk>10**(-1/20): y*=10**(-1/20)/pk
    sf.write(f'/home/claude/sy/{nm}_mix.wav',y.astype(np.float32),fs,subtype='FLOAT'); print(nm,'pico %.1f dBFS'%(20*np.log10(np.abs(y).max())))
