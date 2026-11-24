import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); P=np.load(D+'parts.npy',allow_pickle=True)
R={'casal':(55.38,55.46,56.85,56.93),'achar':(68.57,68.62,69.31,69.36),'cara':(84.47,84.53,85.20,85.24)}
m=pyln.Meter(fs,block_size=0.2)
def band(z,t0,t1,lo,hi):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((t0-0.5)*fs):int((t1+0.5)*fs)],axis=0)[int(0.5*fs):-int(0.5*fs)]
    return 10*np.log10((y**2).mean()+1e-14)
out=mix.copy(); choice={}
for name,W0,yr,yn in P:
    A0,A1,B0,B1=R[name]; s=slice(int(W0*fs),int(W0*fs)+len(yr)); tl=W0+np.arange(len(yr))/fs
    w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
    def build(g):
        o=mix[s]*(1-w)+(yr+yn*10**(g/20))*w; return o
    seg=lambda z: z[int((A1-W0)*fs):int((B0-W0)*fs)]
    L0=m.integrated_loudness(seg(mix[s]))
    best=None
    for g in np.arange(-3,3.01,0.25):
        o=build(g); d=m.integrated_loudness(seg(o))-L0
        if best is None or abs(d)<abs(best[1]): best=(g,d,o)
    g,d,o=best; out[s]=o; choice[name]=g
    bands=' '.join(f'{lo}-{hi}:{band(out,A1,B0,lo,hi)-band(mix,A1,B0,lo,hi):+.1f}' for lo,hi in [(60,200),(200,1000),(1000,4000),(4000,12000)])
    # momentary profile 200ms
    ts=np.arange(A1,B0-0.2,0.1); mo=[m.integrated_loudness(out[int(t*fs):int((t+0.2)*fs)])-m.integrated_loudness(mix[int(t*fs):int((t+0.2)*fs)]) for t in ts]
    print(f'{name}: gain {g:+.2f} dB -> word loudness {d:+.2f} LU | bands {bands}\n   200ms diffs: '+' '.join(f'{x:+.1f}' for x in mo))
d=out-mix; nz=np.where(np.abs(d).max(1)>0)[0]
segs=np.split(nz,np.where(np.diff(nz)>1)[0]+1); print('changed spans:',', '.join(f'{x[0]/fs:.3f}-{x[-1]/fs:.3f}' for x in segs))
up=signal.resample_poly(out,4,1,axis=0); print('true peak out %.2f dBFS (orig %.2f)'%(20*np.log10(np.abs(up).max()),20*np.log10(np.abs(signal.resample_poly(mix,4,1,axis=0)).max())))
np.save(D+'out1.npy',out)
