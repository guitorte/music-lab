import numpy as np, soundfile as sf, librosa, pretty_midi, glob
z,fs=sf.read(glob.glob('/home/claude/ref/stems/drums*.flac')[0]); sr=22050; y=librosa.resample(z.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
beats=np.load('/home/claude/ref/beats.npy')
oe=librosa.onset.onset_strength(y=y,sr=sr,hop_length=64); tt=librosa.times_like(oe,sr=sr,hop_length=64)
def slots(times,w):
    times=np.asarray(times); w=np.asarray(w,float); i=np.searchsorted(beats,times)-1; ok=(i>=0)&(i<len(beats)-1); t=times[ok]; i=i[ok]; ph=(t-beats[i])/(beats[i+1]-beats[i]); sl=np.round(ph*4)%4; ww=w[ok]
    return [ww[sl==k].mean()/ww[sl==0].mean() for k in range(4)],[int((sl==k).sum()) for k in range(4)]
on=librosa.onset.onset_detect(y=y,sr=sr,hop_length=64,units='time',backtrack=True,delta=0.12)
a,c=slots(on,np.interp(on,tt,oe)); print('AUDIO accents     :',' '.join(f'{v:.2f}' for v in a),' counts',c)
for lab,f in [('ADTOF  (velocity)','/home/claude/ref/midi/bs_roformer_sw__adtof__drums (6).mid'),('ADT-STR (velocity)','/home/claude/ref/midi/bs_roformer_sw__adt_str__drums (9).mid')]:
    pm=pretty_midi.PrettyMIDI(f); ns=[n for i in pm.instruments for n in i.notes]; t=np.array([n.start for n in ns]); v=np.array([n.velocity for n in ns])
    a,c=slots(t,v); print(f'{lab}:',' '.join(f'{x:.2f}' for x in a),' counts',c,' | corr(vel, audio strength) %.2f'%np.corrcoef(v,np.interp(t,tt,oe))[0,1])
    p,cc=np.unique([n.pitch for n in ns],return_counts=True); print('    pieces:',dict(zip(p.tolist(),cc.tolist())))
