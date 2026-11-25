# Densidade da percussão e do violão/cavaco a cada 4 tempos (onsets por tempo) + final da faixa
import numpy as np, soundfile as sf, librosa, scipy.signal as ss, pyloudnorm as pl
fs=44100; beats=np.load('/home/claude/traicao/beats.npy')
def onsets(f,lo,hi):
    x,_=sf.read(f,dtype='float32'); x=x.mean(1)
    sos=ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'); y=ss.sosfiltfilt(sos,x).astype(np.float32)
    return librosa.onset.onset_detect(y=y,sr=fs,hop_length=128,units='time'), x
oh,dr=onsets('/home/claude/traicao/stems/drums (3).flac',6000,16000); ol,_=onsets('/home/claude/traicao/stems/drums (3).flac',None,150)
og,gt=onsets('/home/claude/traicao/stems/guitar (4).flac',1500,8000)
print(' início | agudos/tempo  surdo/tempo  violão-cavaco/tempo')
for i in range(0,len(beats)-4,4):
    a,b=beats[i],beats[i+4]; c=lambda o: ((o>=a)&(o<b)).sum()/4
    print(f'{a:6.1f} | {c(oh):6.1f} {c(ol):10.1f} {c(og):12.1f}')
# depois da grade (fim)
m=pl.Meter(fs); S=[sf.read(f'/home/claude/traicao/stems/{n}',dtype='float32')[0] for n in ['vocals (3).flac','drums (3).flac','bass (3).flac','guitar (4).flac','piano (4).flac','other (4).flac']]
L=min(len(s) for s in S); mix=sum(s[:L] for s in S)
for t in range(180,206,3):
    seg=mix[int(t*fs):int((t+3)*fs)]
    lv=[20*np.log10(np.sqrt((s[int(t*fs):int((t+3)*fs)]**2).mean())+1e-9) for s in S]
    print(f'fim {t}s: mix {m.integrated_loudness(seg) if len(seg)>fs else float("nan"):6.1f} LUFS | níveis dBFS voz,bat,baixo,guit,pian,outr', ' '.join(f'{v:5.0f}' for v in lv))
