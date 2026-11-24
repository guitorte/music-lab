import numpy as np, soundfile as sf, pyloudnorm as pyln, glob, librosa
from scipy import signal
names=['vocals','drums','bass','guitar','piano','other']
def load(fmt):
    S={n:sf.read(fmt(n))[0] for n in names}; k=min(len(v) for v in S.values()); return {a:b[:k] for a,b in S.items()}
R=load(lambda n: glob.glob(f'/home/claude/ref/stems/{n}*.flac')[0]); fr=44100
A=load(lambda n: f'/home/claude/pg/w/{n}.wav'); fa=48000
def body(S,fs,a,b): return {k:v[int(a*fs):int(b*fs)] for k,v in S.items()}
for lab,S,fs,(a,b) in []:
    B=body(S,fs,a,b); mix=sum(B.values()); m=pyln.Meter(fs); tot=m.integrated_loudness(mix)
    M=mix.mean(1); k=len(M)//(fs//10); r=M[:k*(fs//10)].reshape(k,-1); rms=np.sqrt((r**2).mean(1)); ok=rms>1e-5
# ---- groove from drums
def groove(S,fs,lab,a,b,SB):
    sr=22050; d=librosa.resample(S['drums'][int(a*fs):int(b*fs)].mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
    _,beats=librosa.beat.beat_track(y=d,sr=sr,hop_length=256,units='time',tightness=400,start_bpm=SB)
    on=librosa.onset.onset_detect(y=d,sr=sr,hop_length=64,units='time',backtrack=True,delta=0.12)
    oe=librosa.onset.onset_strength(y=d,sr=sr,hop_length=64); tt=librosa.times_like(oe,sr=sr,hop_length=64); st=np.interp(on,tt,oe)
    idx=np.clip(np.searchsorted(beats,on),1,len(beats)-1); near=np.where(np.abs(on-beats[idx-1])<np.abs(on-beats[idx]),beats[idx-1],beats[idx]); dd=on-near; beats=beats+np.median(dd[np.abs(dd)<0.08])
    ibi=np.diff(beats); bpm=60/ibi; loc=np.convolve(bpm,np.ones(8)/8,'valid')
    print(f'--- {lab}: tempo median {np.median(bpm):.1f} BPM | beat-to-beat jitter (std of IBI) {ibi.std()*1000:.1f} ms | slow drift range (8-beat avg) {loc.min():.1f}-{loc.max():.1f} BPM')
    i=np.searchsorted(beats,on)-1; okk=(i>=0)&(i<len(beats)-1); t=on[okk]; i=i[okk]; ph=(t-beats[i])/(beats[i+1]-beats[i]); s=st[okk]
    sl=np.round(ph*4)%4; dev=(ph-np.round(ph*4)/4)*np.median(ibi)*1000
    base=np.median(dev[sl==0])
    print('    16th slots: timing vs straight grid (ms, rel. slot 1) / accent (rel. slot 1) / count')
    print('    ',' | '.join(f'{k+1}: {np.median(dev[sl==k])-base:+5.1f} ms, acc {s[sl==k].mean()/s[sl==0].mean():.2f}, n={int((sl==k).sum())}' for k in range(4)))
    print('    timing spread within slot (IQR, ms):',' '.join(f'{k+1}:{np.subtract(*np.percentile(dev[sl==k],[75,25])):.1f}' for k in range(4)))
    w=int(0.01*sr); kk=len(d)//w; e=20*np.log10(np.sqrt((d[:kk*w].reshape(kk,w)**2).mean(1))+1e-9)
    hp=signal.sosfiltfilt(signal.butter(2,[2000,10000],'bandpass',fs=sr,output='sos'),d); eh=20*np.log10(np.sqrt((hp[:kk*w].reshape(kk,w)**2).mean(1))+1e-9)
    lo=signal.sosfiltfilt(signal.butter(2,[45,120],'bandpass',fs=sr,output='sos'),d); el=20*np.log10(np.sqrt((lo[:kk*w].reshape(kk,w)**2).mean(1))+1e-9)
    print(f'    surdo punch (45-120, p95-p50) {np.percentile(el,95)-np.percentile(el,50):.1f} dB | percussion ghost level (2-10k p30 vs p95) {np.percentile(eh,30)-np.percentile(eh,95):.1f} dB | onset strength variation (CV) {st.std()/st.mean():.2f}')
    return beats+a
bR=groove(R,fr,'REAL',8,182,80); bA=groove(A,fa,'AI',12,158,89)
np.save('/home/claude/ref/beats.npy',bR)
