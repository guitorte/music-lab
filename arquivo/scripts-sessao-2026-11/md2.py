import numpy as np, soundfile as sf, librosa, pretty_midi, glob, os
from scipy import signal
sr=22050; W='/home/claude/pg/w/'
aud={}
for n in ['drums','bass','guitar','piano','other','vocals']:
    z,fs=sf.read(W+n+'.wav'); aud[n]=librosa.resample(z.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
hop=64; fr=sr/hop
def oenv(y): o=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop); return (o-o.mean())/(o.std()+1e-9)
OE={n:oenv(y) for n,y in aud.items()}
def lag_of(notes,n):
    tr=np.zeros(len(OE[n]))
    for t,v in notes:
        i=int(round(t*fr))
        if i<len(tr): tr[i]+=v
    tr=np.convolve(tr,np.hanning(5),'same')
    c=signal.correlate(OE[n],tr,'full'); l=np.arange(-len(tr)+1,len(OE[n])); m=np.abs(l)<=int(0.1*fr); i=np.argmax(c[m])
    return l[m][i]/fr*1000, c[m][i]/np.sqrt((tr**2).sum()*(OE[n]**2).sum())
print('systematic timing offset of MIDI onsets vs the audio stem (ms; + = MIDI late), and match strength')
for f in sorted(glob.glob('/home/claude/md/src/*.mid')):
    pm=pretty_midi.PrettyMIDI(f); b=os.path.basename(f)
    for ins in pm.instruments:
        if not ins.notes: continue
        nm=(ins.name or '').lower()
        src='drums' if ins.is_drum else next((k for k in ['bass','guitar','piano','other','vocals'] if k in (nm or b.lower())),None)
        if src is None: continue
        lag,c=lag_of([(n.start,1.0) for n in ins.notes],src)
        print(f'  {b[:55]:55s} {src:7s} {lag:+6.1f} ms  (match {c:.2f})')
