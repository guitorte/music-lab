import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
fs=48000
x,_=sf.read('/home/claude/s/orig.wav'); r,_=sf.read('/home/claude/s/rem.wav')
def shelf(f0,g,Q=0.707):  # RBJ high shelf
    A=10**(g/40); w=2*np.pi*f0/fs; al=np.sin(w)/(2*Q); c=np.cos(w)
    b=[A*((A+1)+(A-1)*c+2*np.sqrt(A)*al), -2*A*((A-1)+(A+1)*c), A*((A+1)+(A-1)*c-2*np.sqrt(A)*al)]
    a=[(A+1)-(A-1)*c+2*np.sqrt(A)*al, 2*((A-1)-(A+1)*c), (A+1)-(A-1)*c-2*np.sqrt(A)*al]
    return np.array(b)/a[0], np.array(a)/a[0]
def peak(f0,g,Q):
    A=10**(g/40); w=2*np.pi*f0/fs; al=np.sin(w)/(2*Q); c=np.cos(w)
    b=[1+al*A,-2*c,1-al*A]; a=[1+al/A,-2*c,1-al/A]; return np.array(b)/a[0],np.array(a)/a[0]
y=x.copy()
for bq,aq in [shelf(12500,3.5),peak(14500,2.5,1.0),peak(18500,-3,0.8)]:
    y=signal.lfilter(bq,aq,y,axis=0)
m=pyln.Meter(fs); target=m.integrated_loudness(r)
y*=10**((target-m.integrated_loudness(y))/20)
# simple lookahead peak limiter at -1 dBFS (4x oversampled detection)
up=signal.resample_poly(y,4,1,axis=0); pk=np.abs(up).max(1).reshape(-1,4).max(1)[:len(y)]
ceil=10**(-1/20); g=np.minimum(1,ceil/np.maximum(pk,1e-9))
la=int(0.005*fs); g=np.minimum.accumulate(np.r_[g,np.ones(la)][::-1])[::-1] if False else g
# min over lookahead window then smooth release
from scipy.ndimage import minimum_filter1d
g=minimum_filter1d(g,size=la*2+1)
rel=np.exp(-1/(0.08*fs)); out=np.empty_like(g); c=1.0
for i,v in enumerate(g):
    c=v if v<c else v+(c-v)*rel; out[i]=c
y*=out[:,None]
sf.write('/home/claude/s/out/air.wav',y,fs,subtype='PCM_24')
print('LUFS orig',round(m.integrated_loudness(x),2),'rem',round(target,2),'new',round(m.integrated_loudness(y),2),'max GR dB',round(20*np.log10(out.min()),2))
# spectral check vs orig
def band(z):
    f,P=signal.welch(z.mean(1),fs,nperseg=16384); return f,P
f,Po=band(x); _,Pr=band(r); _,Pn=band(y)
for c in [5000,8000,10000,12500,14000,16000,18000,20000]:
    mm=(f>=c/2**(1/6))&(f<c*2**(1/6)); d=lambda P:10*np.log10(P[mm].sum()/Po[mm].sum())
    print(c,'V6',round(d(Pr),1),'new',round(d(Pn),1))
