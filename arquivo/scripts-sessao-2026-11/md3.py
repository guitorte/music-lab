import numpy as np, soundfile as sf, librosa, pretty_midi
from scipy import signal
sr=22050; z,fs=sf.read('/home/claude/pg/w/drums.wav'); y=librosa.resample(z.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,hop_length=256,units='time',tightness=400,start_bpm=89)
tempo=float(np.atleast_1d(tempo)[0]); ibi=np.median(np.diff(beats)); print('drums tempo %.2f BPM (beat %.3f s), %d beats'%(tempo,ibi,len(beats)))
on=librosa.onset.onset_detect(y=y,sr=sr,hop_length=64,units='time',backtrack=True,delta=0.15)
oe=librosa.onset.onset_strength(y=y,sr=sr,hop_length=64); tt=librosa.times_like(oe,sr=sr,hop_length=64)
strength=np.interp(on,tt,oe)
def phase(times):
    i=np.searchsorted(beats,times)-1; ok=(i>=0)&(i<len(beats)-1); t=times[ok]; i=i[ok]
    return (t-beats[i])/(beats[i+1]-beats[i]), ok
def slot_stats(times,w=None,label=''):
    ph,ok=phase(np.asarray(times)); w=np.ones(len(ph)) if w is None else np.asarray(w)[ok]
    slot=np.round(ph*4)%4; dev=(ph-np.round(ph*4)/4)  # deviation from straight 16th grid (fraction of beat)
    out=[]
    for s in range(4):
        m=slot==s; out.append((m.sum(), np.median(dev[m])*ibi*1000 if m.any() else np.nan, np.mean(w[m]) if m.any() else np.nan))
    print(f'{label:34s}'+' | '.join(f'16th {s+1}: n={n:4d} timing {d:+5.1f} ms level {v:6.1f}' for s,(n,d,v) in enumerate(out)))
    return out
print('position within the beat (straight-16th grid). timing = median early(-)/late(+) vs the straight grid')
a=slot_stats(on,strength,'AUDIO drums (onset strength)')
for lab,f in [('ADTOF (A/B)','/home/claude/md/src/bs_roformer_sw__adtof__drums (5).mid'),('ADT-STR (C)','/home/claude/md/src/bs_roformer_sw__adt_str__drums (8).mid')]:
    pm=pretty_midi.PrettyMIDI(f); ns=[n for ins in pm.instruments for n in ins.notes]
    st=np.array(sorted(set(round(n.start,3) for n in ns))); vel={}
    for n in ns: vel[round(n.start,3)]=max(vel.get(round(n.start,3),0),n.velocity)
    slot_stats(st-0.020,[vel[s] for s in st],f'{lab} (velocity)')
    p,c=np.unique([n.pitch for n in ns],return_counts=True); names={35:'kick',36:'kick',37:'stick',38:'snare',39:'clap',40:'snare2',41:'tomL',42:'hh closed',43:'tomL2',44:'hh pedal',45:'tomM',46:'hh open',47:'tomM2',48:'tomH',49:'crash',50:'tomH2',51:'ride',53:'ride bell',54:'tamb',56:'cowbell',57:'crash2',59:'ride2'}
    print('   kit pieces used:',', '.join(f'{names.get(int(k),k)}:{v}' for k,v in zip(p,c)))
# swing in audio: ratio of 2nd 16th position (0.25 straight) using strongest onsets
ph,_=phase(on); s2=ph[(ph>0.15)&(ph<0.38)]; s4=ph[(ph>0.65)&(ph<0.88)]
print('audio swing: 2nd 16th at %.3f of beat (straight 0.250), 4th at %.3f (straight 0.750)'%(np.median(s2),np.median(s4)))
# accent pattern: audio onset strength per 16th slot (relative), vs ADT-STR velocity per slot; per-note correlation
ph,ok=phase(on); sl=np.round(ph*4)%4; s=strength[ok]
print('AUDIO accent by 16th (mean onset strength rel. to slot 1):',' '.join(f'{(s[sl==k].mean()/s[sl==0].mean()):.2f}' for k in range(4)))
pm=pretty_midi.PrettyMIDI('/home/claude/md/src/bs_roformer_sw__adt_str__drums (8).mid'); ns=[n for ins in pm.instruments for n in ins.notes]
t=np.array([n.start for n in ns]); v=np.array([n.velocity for n in ns])
a_at=np.interp(t,tt,oe); print('ADT-STR: corr(note velocity, audio onset strength at that time) = %.2f'%np.corrcoef(v,a_at)[0,1])
for p in [52,55,58,54,41,45,50,36]:
    m=np.array([n.pitch for n in ns])==p
    if m.any():
        # what band dominates the audio at those hits
        print(f'  pitch {p}: {m.sum()} notes, velocity median {np.median(v[m]):.0f}')
