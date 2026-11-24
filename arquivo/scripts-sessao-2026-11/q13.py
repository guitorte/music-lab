import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
fs=48000; D='/home/claude/q/w/'
mix,_=sf.read(D+'Que_nem_eu_ITA.wav'); yr=np.load(D+'part_r.npy'); yn0=np.load(D+'part_n.npy'); W0=103.0
A0,A1,B0,B1=104.80,104.90,106.12,106.18
tl=W0+np.arange(len(yr))/fs
w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
def peq(f0,g,Q):
    A=10**(g/40); w0=2*np.pi*f0/fs; c=np.cos(w0); al=np.sin(w0)/(2*Q)
    return np.array([1+al*A,-2*c,1-al*A])/(1+al/A), np.array([1+al/A,-2*c,1-al/A])/(1+al/A)
def env_db(points):  # piecewise-linear gain curve in dB over time, smooth
    ts,gs=zip(*points); g=np.interp(tl,ts,gs); return 10**(g/20)[:,None]
m=pyln.Meter(fs,block_size=0.4)
def build(gbase,body,onset_db,body_db,pres):
    b1,a1=peq(450,body,0.7); yn=signal.filtfilt(b1,a1,yn0,axis=0)*10**(gbase/20)
    if pres:
        b2,a2=peq(3200,pres,1.0); yp=signal.lfilter(b2,a2,yn,axis=0)
        wp=env_db([(105.58,0),(105.62,1),(106.10,1),(106.14,0)]); wp=20*np.log10(wp) # reuse as 0..1 weight
        wp=np.interp(tl,[105.58,105.62,106.10,106.14],[0,1,1,0])[:,None]; yn=yn+(yp-yn)*wp
    g=env_db([(105.58,0),(105.62,onset_db),(105.92,onset_db),(106.00,body_db),(106.10,body_db),(106.14,0)])
    o=mix.copy(); s=slice(int(W0*fs),int(W0*fs)+len(yr)); o[s]=mix[s]*(1-w)+(yr+yn*g)*w
    return o,yn*g
def lev(z,t0,t1,off=0,hp=None):
    s=z[int((t0-off)*fs):int((t1-off)*fs)]
    if hp: s=signal.sosfiltfilt(signal.butter(2,hp,'highpass',fs=fs,output='sos'),s,axis=0)
    return 10*np.log10((s**2).mean()+1e-14)
ow=m.integrated_loudness(mix[int(105*fs):int(106.1*fs)])
# reference: old word, how the stressed TUM onset sat vs the drums
print('variant                         word LU | V/B "t" 105.64-.80 | V/B tum-attack .84-.92 | V/B tum-body .92-1.08 | tum vs quan level | 2k+ in "t"')
for name,args in [('previous v2 (presence cut)',None),('no presence cut',(0,1.5,0,0,0)),('onset +6, body +1.5',(0,1.5,6,1.5,0)),('onset +6, body +1.5, pres +3',(0,1.5,6,1.5,3)),('onset +8, body +2, pres +3',(-0.3,1.5,8,2,3))]:
    if args is None:
        o=np.load(D+'out2.npy'); b1,a1=peq(450,1.5,0.7); b2,a2=peq(2500,-1.5,0.9); yv=signal.filtfilt(b2,a2,signal.filtfilt(b1,a1,yn0,axis=0),axis=0)
    else: o,yv=build(*args)
    bg=lambda t0,t1: lev(yr,t0,t1,W0); vv=lambda t0,t1,hp=None: lev(yv,t0,t1,W0,hp)
    print(f'{name:31s} {m.integrated_loudness(o[int(105*fs):int(106.1*fs)])-ow:+5.2f} | {vv(105.64,105.80)-bg(105.64,105.80):+6.1f} | {vv(105.84,105.92)-bg(105.84,105.92):+6.1f} | {vv(105.92,106.08)-bg(105.92,106.08):+6.1f} | {vv(105.84,106.08)-vv(105.06,105.44):+5.1f} | {vv(105.64,105.80,2000):6.1f}')
    if args==(0,1.5,6,1.5,3): np.save(D+'out3.npy',o)
yo=np.load(D+'Vocais_isolados.wav') if False else sf.read(D+'Vocais_isolados.wav')[0]
print('old (wrong) word for reference: stressed "TUM" vs "quan" level %+.1f dB'%(lev(yo,105.66,106.08)-lev(yo,105.06,105.44)))
