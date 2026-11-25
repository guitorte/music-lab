# Há ghost note na 2ª semicolcheia ou é só o decaimento da 1ª? Envelope dos agudos dobrado em 32 posições por tempo
import numpy as np, soundfile as sf, scipy.signal as ss
fs=44100; beats=np.load('/home/claude/traicao/beats.npy')
x,_=sf.read('/home/claude/traicao/stems/drums (3).flac',dtype='float32'); x=x.mean(1)
for nome,(lo,hi) in [('agudos >6 kHz',(6000,16000)),('médios 0,2–1,5 kHz',(200,1500))]:
    y=ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),x)
    env=np.sqrt(np.convolve(y**2,np.ones(int(0.004*fs))/int(0.004*fs),'same'))
    sel=[i for i in range(len(beats)-1) if 52.7<=beats[i]<180]   # só refrões/banda cheia
    P=np.zeros(32); 
    for i in sel:
        t=beats[i]+np.arange(32)/32*(beats[i+1]-beats[i]); P+=env[(t*fs).astype(int)]
    P=20*np.log10(P/P.max())
    print(f'\n{nome} (dB rel. ao pico; | marca cada semicolcheia)')
    for k in range(4):
        seg=P[k*8:(k+1)*8]; print(f'  {k+1}ª: '+' '.join(f'{v:5.1f}' for v in seg), f'  | subida no ataque: {seg[0]-P[k*8-1]:+.1f} dB')
