import numpy as np, soundfile as sf, librosa
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1).astype(np.float32)
def ons(lo,hi,t0,t1):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),M[int(t0*fs):int(t1*fs)]).astype(np.float32)
    return librosa.onset.onset_detect(y=y,sr=fs,hop_length=64,units='time',backtrack=False,delta=0.2)+t0
def bestlag(t0,t1,lo,hi):
    A=[ons(40,120,t0,t1),ons(4000,12000,t0,t1)]; B=[ons(40,120,t0+lo-0.5,t1+hi+0.5),ons(4000,12000,t0+lo-0.5,t1+hi+0.5)]
    res=[]
    for L in np.arange(lo,hi,0.0005):
        sc=np.mean([np.sum(np.abs(a[:,None]-(b[None,:]-L)).min(1)<0.008)/len(a) for a,b in zip(A,B)]); res.append((L,sc))
    res=np.array(res); i=np.argmax(res[:,1]); return res[i]
# chorus 1 -> 2 (known ~43.72) and chorus 2 -> 3 (~66.7), per section (times in the earlier chorus)
for lab,base,lo,hi in [('ch1->ch2',0,43.4,44.1),('ch2->ch3',43.722,66.3,67.2)]:
    print(lab)
    for t0,t1,sec in [(13.5,16.5,'run-in to chorus'),(14.6,25,'Tocaína'),(25,34.6,'Tente aí'),(34.6,47,'Melhor que farmar'),(47.2,56.5,'O que é falar')]:
        L,s=bestlag(t0+base,t1+base,lo,hi); print(f'   {sec:18s} lag {L:.4f}  hits matched {s*100:.0f}%')
