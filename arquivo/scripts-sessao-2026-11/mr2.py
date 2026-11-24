import numpy as np, soundfile as sf, pyloudnorm as pyln, librosa
from scipy import signal
from scipy.ndimage import minimum_filter1d
W='/home/claude/pg/w/'; R='/home/claude/mr/'; fs=48000; m=pyln.Meter(fs)
voc,_=sf.read(W+'vocals.wav'); n=len(voc)
def load(p):
    z,_=sf.read(p); z=np.atleast_2d(z.T).T
    if z.shape[1]==1: z=np.repeat(z,2,1)
    return np.r_[z,np.zeros((max(0,n-len(z)),2))][:n]
inst={k:load(R+k+'.wav') for k in ['drums','bass','guitar','piano']}
stem={k:load(W+k+'.wav') for k in inst}
# timing check: rendered drums vs drum stem
sr=22050; hop=64
oe=lambda z: librosa.onset.onset_strength(y=librosa.resample(z.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr),sr=sr,hop_length=hop)
a,b=oe(stem['drums'][int(20*fs):int(80*fs)]),oe(inst['drums'][int(20*fs):int(80*fs)])
c=signal.correlate(a-a.mean(),b-b.mean(),'full'); l=np.arange(-len(b)+1,len(a)); mm=np.abs(l)<int(0.1*sr/hop); i=np.argmax(c[mm]); lag=l[mm][i]*hop/sr
print('rendered drums vs drum stem: lag %+.1f ms (+ = render early), corr %.2f'%(lag*1000,c[mm][i]/np.sqrt(((a-a.mean())**2).sum()*((b-b.mean())**2).sum())))
sh=int(round(lag*fs))
if abs(lag)>0.003:
    for k in inst: inst[k]=np.roll(inst[k],sh,axis=0)
    print('-> shifted instrumental by %+.1f ms'%(lag*1000))
b0=slice(12*fs,158*fs)
for k in inst:
    g=m.integrated_loudness(stem[k][b0])-m.integrated_loudness(inst[k][b0]); inst[k]*=10**(g/20); print(f'{k}: gain {g:+.1f} dB to match stem loudness')
band=sum(inst.values())
orig_rest=sum(stem.values())+load(W+'other.wav')
target=m.integrated_loudness(voc[b0])-m.integrated_loudness(orig_rest[b0])   # original vocal-vs-band balance
cur=m.integrated_loudness(voc[b0])-m.integrated_loudness(band[b0]); band*=10**((cur-target)/20)
print('vocal vs band: original %+.1f LU -> mix %+.1f LU'%(target,m.integrated_loudness(voc[b0])-m.integrated_loudness(band[b0])))
mix=voc+band
t=np.arange(n)/fs; fade=np.clip((n/fs-t)/3.0,0,1); mix*=(np.sin(fade*np.pi/2)**2)[:,None]
sf.write(R+'mix_raw.wav',mix,fs,subtype='FLOAT')
# light master: HPF, mono lows, limiter to -13 LUFS / -1.5 dBTP
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')].replace("/home/claude/e/mix.wav",R+'mix_raw.wav'))
y=signal.sosfiltfilt(signal.butter(2,28,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2; S=signal.sosfiltfilt(signal.butter(2,100,'highpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
gg=-13.0-meter.integrated_loudness(y)
for _ in range(6):
    out,grd=limit(y*10**(gg/20),-1.5); Lr=meter.integrated_loudness(out); gg+=-13.0-Lr
print(f'LUFS {Lr:.2f}, limiter GR 99th {np.percentile(grd,99):.2f}, max {grd.max():.2f}')
sf.write(R+'Soap_Opera_Thing_voz_stem_instrumental_MIDI.wav',out,fs,subtype='PCM_24')
