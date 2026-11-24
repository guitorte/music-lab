import numpy as np, soundfile as sf, librosa, glob
from scipy import signal
sr=22050
def load(d,n):
    z,fs=sf.read(glob.glob(f'{d}/{n}*.flac')[0]); return librosa.resample(z.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
dR,dA=load('/home/claude/ref/stems','drums'),load('/home/claude/ai2/stems','drums')
def grid(d):
    _,beats=librosa.beat.beat_track(y=d,sr=sr,hop_length=256,units='time',tightness=400,start_bpm=80)
    on=librosa.onset.onset_detect(y=d,sr=sr,hop_length=64,units='time',backtrack=True,delta=0.12)
    idx=np.clip(np.searchsorted(beats,on),1,len(beats)-1); near=np.where(np.abs(on-beats[idx-1])<np.abs(on-beats[idx]),beats[idx-1],beats[idx]); dd=on-near; return beats+np.median(dd[np.abs(dd)<0.08]), on
for lab,d in [('REAL',dR),('AI',dA)]:
    beats,on=grid(d); oe=librosa.onset.onset_strength(y=d,sr=sr,hop_length=64); tt=librosa.times_like(oe,sr=sr,hop_length=64); st=np.interp(on,tt,oe)
    ibi=np.diff(beats[(beats>8)&(beats<182)]); loc=np.convolve(60/ibi,np.ones(8)/8,'valid')
    i=np.searchsorted(beats,on)-1; ok=(i>=0)&(i<len(beats)-1)&(on>8)&(on<182); t=on[ok]; i=i[ok]; ph=(t-beats[i])/(beats[i+1]-beats[i]); s=st[ok]; sl=np.round(ph*4)%4; dev=(ph-np.round(ph*4)/4)*np.median(ibi)*1000; base=np.median(dev[sl==0])
    w=int(0.01*sr); seg=d[8*sr:182*sr]; kk=len(seg)//w
    def bl(lo,hi): q=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=sr,output='sos'),seg); return 20*np.log10(np.sqrt((q[:kk*w].reshape(kk,w)**2).mean(1))+1e-9)
    el,eh=bl(45,120),bl(2000,10000)
    print(f'=== {lab}: tempo {np.median(60/ibi):.1f} BPM, jitter {ibi.std()*1000:.1f} ms, drift {loc.min():.1f}-{loc.max():.1f}')
    print('    accents  :',' '.join(f'{s[sl==k].mean()/s[sl==0].mean():.2f}' for k in range(4)),' | timing vs grid (ms):',' '.join(f'{np.median(dev[sl==k])-base:+.1f}' for k in range(4)),' | counts',[int((sl==k).sum()) for k in range(4)])
    print(f'    surdo punch {np.percentile(el,95)-np.percentile(el,50):.1f} dB | ghost level {np.percentile(eh,30)-np.percentile(eh,95):.1f} dB | attack variation CV {s.std()/s.mean():.2f}')
    if lab=='REAL': onR=on; bR=beats
    else: onA=on
# direct comparison: matched drum onsets AI vs REAL (within 60 ms)
j=np.searchsorted(onR,onA); j=np.clip(j,1,len(onR)-1); nr=np.where(np.abs(onA-onR[j-1])<np.abs(onA-onR[j]),onR[j-1],onR[j]); d=onA-nr; m=np.abs(d)<0.06
print(f'AI vs REAL drum hits: {m.mean()*100:.0f}% of AI hits within 60 ms of a real hit; median offset {np.median(d[m])*1000:+.1f} ms, IQR {np.percentile(d[m],25)*1000:+.1f}..{np.percentile(d[m],75)*1000:+.1f} ms')
for a,b in [(8,40),(40,80),(80,120),(120,160),(160,182)]:
    mm=m&(onA>a)&(onA<b); print(f'   {a:3d}-{b:3d}s: offset median {np.median(d[mm])*1000:+5.1f} ms (n={mm.sum()})')
