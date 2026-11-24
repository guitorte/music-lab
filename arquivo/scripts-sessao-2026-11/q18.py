import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
fs=48000; D='/home/claude/q/w/'
mix,_=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav')
yr=np.load(D+'part_r.npy'); yn0=np.load(D+'part_n.npy'); W0=103.0
A0,A1,B0,B1=104.80,104.90,106.12,106.18
tl=W0+np.arange(len(yr))/fs
w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
def peq(f0,g,Q):
    A=10**(g/40); w0=2*np.pi*f0/fs; c=np.cos(w0); al=np.sin(w0)/(2*Q)
    return np.array([1+al*A,-2*c,1-al*A])/(1+al/A), np.array([1+al/A,-2*c,1-al/A])/(1+al/A)
bandHF=signal.butter(4,[2000,12000],'bandpass',fs=fs,output='sos')
hf=lambda z: signal.sosfiltfilt(bandHF,z,axis=0)
rms=lambda z: np.sqrt((z**2).mean())
# 1) the old "t" as it sounded inside the original track: old stem HF, scaled to the mix where the drums are silent
k=rms(hf(mix)[int(105.640*fs):int(105.665*fs)])/rms(hf(voc)[int(105.640*fs):int(105.665*fs)])
src0,src1=105.632,105.690; L=int((src1-src0)*fs)
burst=hf(voc)[int(src0*fs):int(src0*fs)+L]*k
fi,fo=int(0.003*fs),int(0.022*fs)
win=np.ones(L); win[:fi]=np.sin(np.linspace(0,np.pi/2,fi))**2; win[-fo:]=np.cos(np.linspace(0,np.pi/2,fo))**2
burst*=win[:,None]
print('scale stem->mix for the old "t": %.2f dB'%(20*np.log10(k)))
m=pyln.Meter(fs,block_size=0.4); ow=m.integrated_loudness(mix[int(105*fs):int(106.1*fs)])
def build(dst,tdb,pres,B0=106.12,B1=106.18):
    w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
    b1,a1=peq(450,1.5,0.7); yn=signal.filtfilt(b1,a1,yn0,axis=0)      # body only, no presence cut this time
    if pres:
        b2,a2=peq(3200,pres,1.0); yp=signal.lfilter(b2,a2,yn,axis=0)
        wp=np.interp(tl,[105.78,105.82,106.08,106.12],[0,1,1,0])[:,None]; yn=yn+(yp-yn)*wp
    i0=int((dst-W0)*fs); yn=yn.copy(); yn[i0:i0+L]+=burst*10**(tdb/20)
    o=mix.copy(); s=slice(int(W0*fs),int(W0*fs)+len(yr)); o[s]=mix[s]*(1-w)+(yr+yn)*w
    return o,yn
def lev(z,t0,t1,off=0,f=None):
    s=z[int((t0-off)*fs):int((t1-off)*fs)]
    if f is not None: s=f(s)
    return 10*np.log10((s**2).mean()+1e-14)

def lowlev(z,t0,t1):
    y=signal.sosfiltfilt(signal.butter(4,[80,500],'bandpass',fs=fs,output='sos'),z[int((t0-0.1)*fs):int((t1+0.1)*fs)],axis=0)[int(0.1*fs):-int(0.1*fs)]
    return 10*np.log10((y**2).mean()+1e-14)

o=build(105.812,-2,2,106.04,106.08)[0]
# reinforce the old "m" (below ~1.2 kHz the vocal stem is phase-coherent with the track)
lp=signal.butter(4,1200,'lowpass',fs=fs,output='sos')
seg=slice(int(92*fs),int(104.5*fs))
ml=signal.sosfiltfilt(lp,mix[seg],axis=0); vl=signal.sosfiltfilt(lp,voc[seg],axis=0)
g=(ml*vl).sum()/(vl**2).sum(); print('vocal stem -> track scale below 1.2 kHz: %.3f'%g)
t=np.arange(len(mix))/fs
env=np.interp(t,[106.05,106.07,106.15,106.185],[0,1,1,0])[:,None]
voc_lp=signal.sosfiltfilt(lp,voc[int(105.9*fs):int(106.3*fs)],axis=0)
add=np.zeros_like(mix); add[int(105.9*fs):int(106.3*fs)]=voc_lp
def withm(db): return o+(10**(db/20)-1)*g*add*env
def lowlev(z,t0,t1):
    y=signal.sosfiltfilt(signal.butter(4,[80,500],'bandpass',fs=fs,output='sos'),z[int((t0-0.1)*fs):int((t1+0.1)*fs)],axis=0)[int(0.1*fs):-int(0.1*fs)]
    return 10*np.log10((y**2).mean()+1e-14)
o3=build(105.812,-2,2)[0]
cand={'+0 dB':withm(0),'+3 dB':withm(3),'+4.5 dB':withm(4.5)}
print(' time   original   v3   '+'  '.join(f'{k:>8s}' for k in cand))
for tt in np.arange(106.00,106.22,0.02):
    print(f'{tt:6.2f} {lowlev(mix,tt,tt+0.02):9.1f} {lowlev(o3,tt,tt+0.02):6.1f} '+'  '.join(f'{lowlev(v,tt,tt+0.02):8.1f}' for v in cand.values()))
# how far does the "m" stand above the bass bed? old vocal estimate in track vs everything else
def mband(z,t0,t1):
    y=signal.sosfiltfilt(signal.butter(4,[100,500],'bandpass',fs=fs,output='sos'),z[int((t0-0.1)*fs):int((t1+0.1)*fs)],axis=0)[int(0.1*fs):-int(0.1*fs)]
    return 10*np.log10((y**2).mean()+1e-14)
mo=mband(g*voc,106.07,106.16); bed=mband(mix-g*signal.sosfiltfilt(lp,voc,axis=0),106.07,106.16)
print('"m" vs bed (100-500 Hz, 106.07-106.16): original %+.1f dB | +3 dB version %+.1f dB'%(mo-bed,mo+3-bed))
v=cand['+3 dB']; ow=m.integrated_loudness(mix[int(105*fs):int(106.1*fs)])
print('word loudness vs original %+.2f LU'%(m.integrated_loudness(v[int(105*fs):int(106.1*fs)])-ow))
up=signal.resample_poly(v[int(104.5*fs):int(106.5*fs)],4,1,axis=0); print('true peak %.2f dBFS'%(20*np.log10(np.abs(up).max())))
np.save(D+'out6.npy',v)
