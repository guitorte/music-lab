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
o3,_=build(105.812,-2,2)
print('<500 Hz level, 20 ms steps 106.00-106.20 (where the "m" lives):')
print(' time   original   v3(no m)  ', end='')
cands=[(106.05,106.09),(106.06,106.10),(106.04,106.08)]
for c in cands: print(f'  end {c[0]:.2f}-{c[1]:.2f}', end='')
print()
outs=[build(105.812,-2,2,*c)[0] for c in cands]
for t in np.arange(106.00,106.20,0.02):
    print(f'{t:6.2f} {lowlev(mix,t,t+0.02):9.1f} {lowlev(o3,t,t+0.02):9.1f}   '+'   '.join(f'{lowlev(o,t,t+0.02):12.1f}' for o in outs))
def pitchtrack(z,t0,t1):
    r=[]
    for t in np.arange(t0,t1,0.01):
        s_=signal.sosfiltfilt(signal.butter(4,[80,500],'bandpass',fs=fs,output='sos'),z[int((t-0.05)*fs):int((t+0.09)*fs)].mean(1))[int(0.05*fs):int(0.09*fs)]
        ac=np.correlate(s_,s_,'full')[len(s_)-1:]; lo_,hi_=int(fs/300),int(fs/90); i=np.argmax(ac[lo_:hi_])+lo_; r.append((round(fs/i),round(ac[i]/ac[0],2)))
    return r
print('pitch (Hz, voicing) through the handover, chosen end 106.05-106.09:')
print(pitchtrack(outs[0],106.02,106.16))
o=outs[0]; ow=m.integrated_loudness(mix[int(105*fs):int(106.1*fs)])
print('word loudness vs original %+.2f LU'%(m.integrated_loudness(o[int(105*fs):int(106.1*fs)])-ow))
up=signal.resample_poly(o[int(104.5*fs):int(106.5*fs)],4,1,axis=0); print('true peak %.2f dBFS'%(20*np.log10(np.abs(up).max())))
np.save(D+'out5.npy',o)
