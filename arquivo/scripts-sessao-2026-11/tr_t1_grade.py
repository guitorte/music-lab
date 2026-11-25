# Traição: duração, loudness, tempo e fase da grade conferidos pelo surdo
import numpy as np, soundfile as sf, librosa, pyloudnorm as pl, glob, os, scipy.signal as ss, pretty_midi as pm
D='/home/claude/traicao/stems'; S={}
for f in sorted(glob.glob(D+'/*.flac')):
    x,fs=sf.read(f,always_2d=True,dtype='float32'); S[os.path.basename(f).split(' ')[0]]=x
L=min(len(x) for x in S.values()); S={k:v[:L] for k,v in S.items()}; mix=sum(S.values())
m=pl.Meter(fs); print('dur %.1f s, fs %d'%(L/fs,fs),' mix %.1f LUFS'%m.integrated_loudness(mix), ' pico %.1f dBFS'%(20*np.log10(np.abs(mix).max())))
dr=S['drums'].mean(1)
def band(x,lo,hi):
    sos=ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'); return ss.sosfiltfilt(sos,x)
low=band(dr,None,150); 
hop=256
for bpm in (76,152,114):
    t,b=librosa.beat.beat_track(y=dr,sr=fs,hop_length=hop,start_bpm=bpm,tightness=400,units='time')
    print('beat_track start',bpm,'->',np.round(float(np.atleast_1d(t)[0]),2),'BPM, n beats',len(b))
# fase: dobra onsets do surdo (grave) em 16 posições de um compasso de 2 tempos a 76 BPM
t,beats=librosa.beat.beat_track(y=dr,sr=fs,hop_length=hop,start_bpm=76,tightness=400,units='time')
beats=np.array(beats); per=np.median(np.diff(beats)); print('período mediano %.4f s = %.2f BPM'%(per,60/per))
def fold(sig,beats,nsub=4):
    env=np.abs(ss.hilbert(sig)) if False else np.abs(sig)
    e=librosa.onset.onset_strength(y=sig.astype(np.float32),sr=fs,hop_length=hop); te=librosa.frames_to_time(np.arange(len(e)),sr=fs,hop_length=hop)
    acc=np.zeros(nsub*2); 
    for i in range(0,len(beats)-2,2):
        for j in range(2):
            b0,b1=beats[i+j],beats[i+j+1]
            for k in range(nsub):
                tt=b0+(b1-b0)*k/nsub; w=(te>tt-0.03)&(te<tt+0.03); acc[j*nsub+k]+=e[w].max() if w.any() else 0
    return acc/acc.max()
print('surdo (<150 Hz) por 16ª em 2 tempos:',np.round(fold(low,beats),2))
print('bateria toda por 16ª em 2 tempos:   ',np.round(fold(dr,beats),2))
hi=band(dr,5000,16000); print('agudos (>5 kHz) por 16ª em 2 tempos: ',np.round(fold(hi,beats),2))
mid=band(dr,300,3000); print('médios (0,3–3 kHz) por 16ª:         ',np.round(fold(mid,beats),2))
np.save('/home/claude/traicao/beats.npy',beats)
# MIDI de bateria (ADTOF): classes
for f in ['bs_roformer_sw__adtof__drums (6).mid','bs_roformer_sw__adt_str__drums (9).mid']:
    n=[x for i in pm.PrettyMIDI('/home/claude/traicao/midi/'+f).instruments for x in i.notes]
    u,c=np.unique([x.pitch for x in n],return_counts=True); print(f,dict(zip(u.tolist(),c.tolist())))
