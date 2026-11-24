import numpy as np, soundfile as sf, librosa, pyloudnorm as pyln
for nm in ['song','sample']:
    x,fs=sf.read(f'/home/claude/ch/{nm}.wav'); x=np.atleast_2d(x.T).T; M=x.mean(1).astype(np.float32)
    m=pyln.Meter(fs,block_size=min(0.4,len(M)/fs/2))
    print(f'== {nm}: {len(M)/fs:.2f}s fs {fs} ch {x.shape[1]} LUFS {m.integrated_loudness(x):.1f} peak {20*np.log10(np.abs(x).max()):.1f}')
    tempo,beats=librosa.beat.beat_track(y=M,sr=fs,hop_length=256,units='time')
    print('   tempo %.2f BPM, beats %d'%(float(np.atleast_1d(tempo)[0]),len(beats)))
    ch=librosa.feature.chroma_cqt(y=M,sr=fs,hop_length=1024).mean(1)
    maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); mi=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
    names='C C# D D# E F F# G G# A A# B'.split()
    sc=[(np.corrcoef(np.roll(maj,k),ch)[0,1],names[k]+' major') for k in range(12)]+[(np.corrcoef(np.roll(mi,k),ch)[0,1],names[k]+' minor') for k in range(12)]
    sc.sort(reverse=True); print('   key estimate:',', '.join(f'{k} ({c:.2f})' for c,k in sc[:3]))
    print('   chroma:',' '.join(f'{n}:{v/ch.max():.2f}' for n,v in zip(names,ch)))
    if nm=='sample':
        f=librosa.pyin(M,fmin=60,fmax=1200,sr=fs,frame_length=4096)[0]; f=f[~np.isnan(f)]
        if len(f): print('   pitched content: median f0 %.1f Hz (%s), voiced %.0f%%'%(np.median(f),librosa.hz_to_note(np.median(f)),100*len(f)/len(librosa.pyin(M,fmin=60,fmax=1200,sr=fs,frame_length=4096)[0])))
        on=librosa.onset.onset_detect(y=M,sr=fs,units='time'); print('   onsets:',' '.join(f'{o:.2f}' for o in on[:30]))
