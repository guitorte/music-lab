import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
fs=48000; D='/home/claude/q/w/'
mix,_=sf.read(D+'Que_nem_eu_ITA.wav'); yr=np.load(D+'part_r.npy'); yn=np.load(D+'part_n.npy')
W0=103.0; A0,A1,B0,B1=104.80,104.90,106.12,106.18
s=slice(int(W0*fs),int(W0*fs)+len(yr))
tl=W0+np.arange(len(yr))/fs
w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
def build(gdb):
    o=mix.copy(); o[s]=mix[s]*(1-w)+(yr+yn*10**(gdb/20))*w; return o
m=pyln.Meter(fs,block_size=0.4)
def momentary(z,t0,t1,step=0.1):
    return np.array([m.integrated_loudness(z[int(t*fs):int((t+0.4)*fs)]) if True else 0 for t in np.arange(t0,t1,step)])
def band(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int(104*fs):int(107*fs)],axis=0)[int(1*fs):int(2.1*fs)]
    return 10*np.log10((y**2).mean())
mo=momentary(mix,104.8,105.8)
for g in [0.0,1.0,1.5,2.0,2.5]:
    o=build(g); mf=momentary(o,104.8,105.8)
    ow=m.integrated_loudness(mix[int(105*fs):int(106.1*fs)]); fw=m.integrated_loudness(o[int(105*fs):int(106.1*fs)])
    print(f'new-word gain {g:+.1f} dB: word loudness {fw-ow:+.2f} LU vs original | momentary diff mean {np.mean(mf-mo):+.2f}, worst {np.min(mf-mo):+.2f} | 200-1k {band(o,200,1000)-band(mix,200,1000):+.1f} dB, 1-4k {band(o,1000,4000)-band(mix,1000,4000):+.1f} dB')
np.save(D+'build_ok.npy',np.array([1]))
print('---- tilted gain on the new word (more body, not more brightness)')
def peq(f0,g,Q):
    A=10**(g/40); w0=2*np.pi*f0/fs; c=np.cos(w0); al=np.sin(w0)/(2*Q)
    return np.array([1+al*A,-2*c,1-al*A])/(1+al/A), np.array([1+al/A,-2*c,1-al/A])/(1+al/A)
yn0=yn.copy()
best=None
for gdb,body,pres in [(0.5,2.0,-0.5),(0.5,2.5,-1.0),(1.0,2.0,-1.0),(0.8,2.0,-0.8)]:
    b1,a1=peq(450,body,0.7); b2,a2=peq(2500,pres,0.9)
    yn=signal.filtfilt(b2,a2,signal.filtfilt(b1,a1,yn0,axis=0),axis=0)
    o=build(gdb); mf=momentary(o,104.8,105.8)
    ow=m.integrated_loudness(mix[int(105*fs):int(106.1*fs)]); fw=m.integrated_loudness(o[int(105*fs):int(106.1*fs)])
    sc=abs(fw-ow)+abs(band(o,200,1000)-band(mix,200,1000))+abs(band(o,1000,4000)-band(mix,1000,4000))
    print(f'gain {gdb:+.1f}, 450 Hz {body:+.1f}, 2.5 kHz {pres:+.1f}: word {fw-ow:+.2f} LU | momentary mean {np.mean(mf-mo):+.2f}, worst {np.min(mf-mo):+.2f} | 200-1k {band(o,200,1000)-band(mix,200,1000):+.1f}, 1-4k {band(o,1000,4000)-band(mix,1000,4000):+.1f}')
    if best is None or sc<best[0]: best=(sc,gdb,body,pres,o)
sc,gdb,body,pres,o=best; print('chosen:',gdb,body,pres)
mf=momentary(o,104.8,106.1,0.1); mo2=momentary(mix,104.8,106.1,0.1)
print('momentary diff over time (400 ms windows starting at):',' '.join(f'{t:.1f}:{d:+.1f}' for t,d in zip(np.arange(104.8,106.1,0.1),mf-mo2)))
np.save(D+'out2.npy',o)
