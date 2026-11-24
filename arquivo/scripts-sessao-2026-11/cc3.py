import numpy as np, soundfile as sf, librosa
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1).astype(np.float32)
tempo,beats=librosa.beat.beat_track(y=M,sr=fs,hop_length=256,units='time',tightness=200)
tempo=float(np.atleast_1d(tempo)[0]); print('tempo %.2f BPM, %d beats'%(tempo,len(beats)))
ibi=np.diff(beats); print('inter-beat: median %.4f s, std %.4f s, min %.3f max %.3f'%(np.median(ibi),ibi.std(),ibi.min(),ibi.max()))
# downbeat phase: kick-band onset strength per beat position mod 4
on=librosa.onset.onset_strength(y=librosa.effects.harmonic(M) if False else M,sr=fs,hop_length=256,fmax=150)
tt=librosa.times_like(on,sr=fs,hop_length=256); val=np.interp(beats,tt,on)
for ph in range(4): print(' phase',ph,'mean kick onset %.2f'%val[ph::4].mean())
np.save('/home/claude/cc/beats.npy',beats)
for lo,hi in [(44,50),(88,94),(98,103)]:
    print(f'beats {lo}-{hi}s:',' '.join(f'{b:.3f}' for b in beats if lo<=b<=hi))
