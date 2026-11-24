import numpy as np, soundfile as sf, librosa, glob
sr=22050; D='/home/claude/ai2/stems'
def load(n):
    z,fs=sf.read(glob.glob(f'{D}/{n}*.flac')[0]); return librosa.resample(z.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
S={n:load(n) for n in ['drums','bass','guitar','piano','other','vocals']}
dur=len(S['drums'])/sr
_,beats=librosa.beat.beat_track(y=S['drums'],sr=sr,hop_length=256,units='time',tightness=400,start_bpm=90)
on=librosa.onset.onset_detect(y=S['drums'],sr=sr,hop_length=64,units='time',backtrack=True,delta=0.12)
idx=np.clip(np.searchsorted(beats,on),1,len(beats)-1); near=np.where(np.abs(on-beats[idx-1])<np.abs(on-beats[idx]),beats[idx-1],beats[idx]); dd=on-near; beats=beats+np.median(dd[np.abs(dd)<0.08])
# extend grid to cover the whole song (before first and after last tracked beat)
per=np.median(np.diff(beats)); pre=np.arange(beats[0]-per,-1e-9,-per)[::-1]; post=np.arange(beats[-1]+per,dur+per,per); beats=np.r_[pre,beats,post]
print('tempo %.2f BPM, %d beats, first %.3f'%(60/per,len(beats),beats[0]))
# downbeat phase: surdo (low band) strength by beat phase mod 4 and mod 2
from scipy import signal
lo=signal.sosfiltfilt(signal.butter(2,[40,120],'bandpass',fs=sr,output='sos'),S['drums'])
def lv(t): a=int(t*sr); return 20*np.log10(np.sqrt((lo[a:a+int(0.08*sr)]**2).mean())+1e-9) if a<len(lo)-100 else -120
L=np.array([lv(b) for b in beats]); print('surdo by phase mod4:',[round(L[p::4][L[p::4]>-100].mean(),1) for p in range(4)])
# harmonic chroma per beat from harmonic stems (+ vocals lower weight)
hop=512
def chroma(y,w): 
    h=librosa.effects.harmonic(y,margin=2.0); return w*librosa.feature.chroma_cqt(y=h,sr=sr,hop_length=hop,bins_per_octave=36)
C=chroma(S['guitar'],1.0)+chroma(S['piano'],1.0)+chroma(S['other'],0.5)+chroma(S['bass'],1.2)+chroma(S['vocals'],0.4)
fr=librosa.frames_to_time(np.arange(C.shape[1]),sr=sr,hop_length=hop)
bc=np.stack([C[:,(fr>=beats[i])&(fr<beats[i+1])].mean(1) if np.any((fr>=beats[i])&(fr<beats[i+1])) else np.zeros(12) for i in range(len(beats)-1)],1)
# bass root per beat from bass stem (pyin) where active
f0,vf,_=librosa.pyin(S['bass'],fmin=35,fmax=300,sr=sr,frame_length=4096,hop_length=hop); ft=librosa.times_like(f0,sr=sr,hop_length=hop)
broot=[]
for i in range(len(beats)-1):
    m=(ft>=beats[i])&(ft<beats[i+1])&vf
    broot.append(int(np.round(np.median(librosa.hz_to_midi(f0[m]))))%12 if m.sum()>=3 else -1)
np.savez('/home/claude/rw/analysis.npz',beats=beats,bc=bc,broot=np.array(broot),surdo=L)
# key
maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); mi=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
tot=bc.sum(1); names='C C# D D# E F F# G G# A A# B'.split()
sc=sorted([(np.corrcoef(np.roll(maj,k),tot)[0,1],names[k]+' maior') for k in range(12)]+[(np.corrcoef(np.roll(mi,k),tot)[0,1],names[k]+' menor') for k in range(12)],reverse=True)
print('key:',sc[:3]); print('bass roots found on %d of %d beats'%(np.sum(np.array(broot)>=0),len(broot)))
