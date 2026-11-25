# Tempo a tempo na passagem pré-refrão -> refrão (40–56 s) e no breque do 2º pré (120–134 s)
import numpy as np, soundfile as sf, librosa, scipy.signal as ss
fs=44100; beats=np.load('/home/claude/traicao/beats.npy')
dr,_=sf.read('/home/claude/traicao/stems/drums (3).flac',dtype='float32'); dr=dr.mean(1)
gt,_=sf.read('/home/claude/traicao/stems/guitar (4).flac',dtype='float32'); gt=gt.mean(1)
vo,_=sf.read('/home/claude/traicao/stems/vocals (3).flac',dtype='float32'); vo=vo.mean(1)
def bp(x,lo,hi):
    sos=ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'); return ss.sosfiltfilt(sos,x).astype(np.float32)
ol=librosa.onset.onset_detect(y=bp(dr,None,150),sr=fs,hop_length=128,units='time'); oh=librosa.onset.onset_detect(y=bp(dr,6000,16000),sr=fs,hop_length=128,units='time')
og=librosa.onset.onset_detect(y=bp(gt,1500,8000),sr=fs,hop_length=128,units='time')
db=lambda x,a,b: 20*np.log10(np.sqrt((x[int(a*fs):int(b*fs)]**2).mean())+1e-9)
for lo,hi in [(40,56),(119,134)]:
    print(f'\n tempo    graves agudos cav/viol | bateria dB  voz dB')
    for i in np.where((beats>=lo)&(beats<hi))[0]:
        a,b=beats[i],beats[i+1]; c=lambda o: ((o>=a)&(o<b)).sum()
        print(f'{a:7.2f}  {c(ol):5d} {c(oh):6d} {c(og):6d}   | {db(dr,a,b):7.1f} {db(vo,a,b):7.1f}')
