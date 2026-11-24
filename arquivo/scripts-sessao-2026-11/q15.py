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
def build(dst,tdb,pres):
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
lq=lambda yn: lev(yn,105.06,105.44,W0)
print('variant                          word LU | "t" 2-12k in output (105.81-105.84) | tum vs quan level')
print(f'{"original track (old t at 105.64)":32s}   ---  | {lev(mix,105.640,105.670,0,hf):6.1f} (old t)')
o_prev=np.load(D+'out2.npy'); print(f'{"previous v2":32s} {m.integrated_loudness(o_prev[int(105*fs):int(106.1*fs)])-ow:+5.2f} | {lev(o_prev,105.812,105.842,0,hf):6.1f}')
for name,args in [('t at -2 dB, presence +2',(105.812,-2,2)),('t at 0 dB, presence +2',(105.812,0,2)),('t at -4 dB, presence +2',(105.812,-4,2))]:
    o,yn=build(*args)
    print(f'{name:32s} {m.integrated_loudness(o[int(105*fs):int(106.1*fs)])-ow:+5.2f} | {lev(o,105.812,105.842,0,hf):6.1f} | {lev(yn,105.84,106.08,W0)-lq(yn):+5.1f}')
    if args==(105.812,-2,2): np.save(D+'out4.npy',o)
o=np.load(D+'out4.npy'); up=signal.resample_poly(o[int(104.5*fs):int(106.5*fs)],4,1,axis=0)
print('true peak in window %.2f dBFS'%(20*np.log10(np.abs(up).max())))
