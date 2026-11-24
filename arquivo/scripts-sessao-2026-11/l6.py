import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d
exec(open('/home/claude/scripts/l4.py').read().split('# ---------- lo-fi blocks ----------')[0])
kick=signal.sosfiltfilt(signal.butter(4,[40,120],'bandpass',fs=fs,output='sos'),base.mean(1))
e=ctrl(kick[:,None]); beat=60/166.7
thr=np.percentile(e[e>-90],70)
gr=env_follow(np.clip((e-thr)*1.0,0,5.0),0.010,beat*0.45)
avg=uniform_filter1d(gr,size=int(1.2*rate))          # running mean of ducking (~1.2 s)
gain_db=-gr+avg                                        # pulse around the normal level
br=base*upg(gain_db,len(base))[:,None]
# breaks without kick (>1 s)
nok=uniform_filter1d((e<thr-15).astype(float),size=int(1*rate))>0.95
edges=np.flatnonzero(np.diff(nok.astype(int)))
segs=[(edges[i]/rate,edges[i+1]/rate) for i in range(0,len(edges)-1,2) if nok[edges[i]+1]]
print('kick-less stretches:',[(f'{int(a//60)}:{a%60:04.1f}',f'{int(b//60)}:{b%60:04.1f}') for a,b in segs])
out,grd=master(br); sf.write('/home/claude/l/breathing_final.wav',out,fs,subtype='PCM_24')
print('LUFS',round(meter.integrated_loudness(out),2),'limiter GR median/99th/max',round(float(np.median(grd)),2),round(float(np.percentile(grd,99)),2),round(float(grd.max()),2))
# compare vs clean, 1-s windows 70-86 s
c,_=sf.read('/home/claude/l/1_clean.wav')
def lv(x,t0,t1):
    s=x[int(t0*fs):int(t1*fs)].mean(1); return 10*np.log10((s**2).mean())
print('final minus clean (dB), 1 s windows from 1:10:',[round(lv(out,t,t+1)-lv(c,t,t+1),1) for t in range(70,86)])
print('pulse depth in kick sections: gain range p5..p95 =',np.round(np.percentile(gain_db[e>thr-15],[5,95]),1))
