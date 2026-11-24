import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d
exec(open('/home/claude/scripts/l4.py').read().split('# ---------- lo-fi blocks ----------')[0])  # reuse base + helpers
# ---- tempo estimate from kick band ----
kick=signal.sosfiltfilt(signal.butter(4,[40,120],'bandpass',fs=fs,output='sos'),base.mean(1))
e=ctrl(kick[:,None]); on=np.maximum(np.diff(e,prepend=e[0]),0)
ac=np.correlate(on-on.mean(),on-on.mean(),'full')[len(on)-1:]
lags=np.arange(len(ac))/rate; m=(lags>60/180)&(lags<60/70); bpm=60/lags[m][np.argmax(ac[m])]
beat=60/bpm; print('estimated tempo %.1f BPM'%bpm)
# ---- BREATHING: whole-mix ducking keyed by kick ----
thr=np.percentile(e[e>-90],70)
gr=np.clip((e-thr)*1.0,0,5.0)
gr=env_follow(gr,0.010,beat*0.45)
br=base*upg(-gr,len(base))[:,None]
print('breathing: duck depth median on kicks %.1f dB, max %.1f'%(np.median(gr[e>thr]),gr.max()))
out,grd=master(br); sf.write('/home/claude/l/4_breathing.wav',out,fs,subtype='PCM_24')
print('breathing LUFS',round(meter.integrated_loudness(out),2),'lim max',round(float(grd.max()),2))
# ---- NEXT DOOR: small room, heard at a distance ----
def room_ir(seed,rt=(0.85,0.6,0.35),L=1.2):
    r=np.random.default_rng(seed); n=int(L*fs); t=np.arange(n)/fs; ir=np.zeros(n)
    for (lo,hi),T in zip([(20,400),(400,3000),(3000,16000)],rt):
        b=signal.sosfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),r.standard_normal(n))
        ir+=b*np.exp(-6.9*t/T)
    pre=int(0.012*fs); ir=np.r_[np.zeros(pre),ir[:-pre]]
    for d,gn in [(0.004,0.5),(0.009,0.35),(0.017,0.3),(0.026,0.22)]:
        ir[int(d*fs)+int(r.integers(0,40))]+=gn*r.choice([-1,1])*np.abs(ir).max()*3
    return ir/np.sqrt((ir**2).sum())
mono=base.mean(1)
wet=np.stack([signal.fftconvolve(mono,room_ir(s))[:len(mono)] for s in (1,2)],1)
dry=signal.sosfilt(signal.butter(2,6500,'lowpass',fs=fs,output='sos'),base,axis=0)
dry=signal.sosfilt(signal.butter(1,90,'highpass',fs=fs,output='sos'),dry,axis=0)
rms=lambda z: np.sqrt((z**2).mean())
wet*=rms(dry)/rms(wet)*10**(-3/20)   # direct-to-room ratio ~ +3 dB (distance, but voice legible)
nd=dry+wet
M=(nd[:,0]+nd[:,1])/2; S=(nd[:,0]-nd[:,1])/2; print('next door: side/mid %.1f dB, L/R corr %.2f'%(20*np.log10(rms(S)/rms(M)),np.corrcoef(nd[:,0],nd[:,1])[0,1]))
out,grd=master(nd); sf.write('/home/claude/l/5_next_door.wav',out,fs,subtype='PCM_24')
print('next door LUFS',round(meter.integrated_loudness(out),2),'lim max',round(float(grd.max()),2))
