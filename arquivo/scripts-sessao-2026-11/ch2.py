import numpy as np, soundfile as sf, pyloudnorm as pyln, librosa
from scipy import signal
x,fs=sf.read('/home/claude/ch/song.wav'); s,_=sf.read('/home/claude/ch/sample.wav'); beats=np.load('/home/claude/ch/beats.npy')
# +1 semitone by resampling (F#6 -> G6), duration shrinks by 2^(-1/12)
r=2**(35/1200); n_out=int(round(len(s)/r)); s2=signal.resample_poly(s,int(round(10000/r)),10000,axis=0)
s2=signal.sosfiltfilt(signal.butter(2,180,'highpass',fs=fs,output='sos'),s2,axis=0)   # keep it out of the song's low end
f0=librosa.pyin(s2.mean(1).astype(np.float32),fmin=200,fmax=2500,sr=fs,frame_length=4096)[0]; import numpy as _n; md=69+12*_n.log2(_n.nanmedian(f0)/440); print('shifted sample: %.2f s, median pitch %s %+.0f cents'%(len(s2)/fs,librosa.midi_to_note(round(md)),100*(md-round(md))))
sf.write('/home/claude/ch/sample_afinado_G6.wav',s2,fs,subtype='PCM_24')
first_on=librosa.onset.onset_detect(y=s2.mean(1).astype(np.float32),sr=fs,units='time')[0]; print('sample first onset %.3f s'%first_on)
down=beats[3::4]
m=pyln.Meter(fs); Ls=m.integrated_loudness(s2)
out=x.copy(); placed=[]
for want in (62.0,74.0,85.0):
    d=down[down>=want][0]; st=d-first_on; a=int(st*fs); b=a+len(s2)
    sec=m.integrated_loudness(x[a:b]); g=(sec-2.5)-Ls          # sample sits ~2.5 LU under the section
    fade=np.ones(len(s2)); k=int(0.01*fs); fade[:k]=np.linspace(0,1,k); fade[-int(0.05*fs):]=np.linspace(1,0,int(0.05*fs))
    out[a:b]+=s2*10**(g/20)*fade[:,None]; placed.append((d,st,st+len(s2)/fs,sec,g))
for d,st,en,sec,g in placed: print(f'downbeat {int(d//60)}:{d%60:05.2f} -> sample {int(st//60)}:{st%60:05.2f}-{int(en//60)}:{en%60:05.2f} | section {sec:.1f} LUFS, sample gain {g:+.1f} dB')
up=signal.resample_poly(out,4,1,axis=0); tp=20*np.log10(np.abs(up).max()); print('true peak after mixing %.2f dBTP'%tp)
if tp>-1.0:
    out*=10**((-1.0-tp)/20); print('-> trimmed %.2f dB to keep -1 dBTP'%(-1.0-tp))
sf.write('/home/claude/ch/Chinesa_com_sample_24bit.wav',out,fs,subtype='PCM_24')
print('LUFS song %.1f -> %.1f'%(m.integrated_loudness(x),m.integrated_loudness(out)))
