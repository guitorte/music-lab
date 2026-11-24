import numpy as np, soundfile as sf, pyloudnorm as pyln, glob
from scipy import signal
fs=44100; R='/home/claude/rw'; mt=pyln.Meter(fs)
voc,_=sf.read(glob.glob('/home/claude/ai2/stems/vocals*.flac')[0]); N=len(voc)
def ld(n):
    z,_=sf.read(f'{R}/{n}.wav'); z=z[:N] if len(z)>=N else np.pad(z,((0,N-len(z)),(0,0))); return z
def pan(z,p):  # p -1..1, equal power on mono-summed source + keep some stereo
    m=z.mean(1); a=(p+1)*np.pi/4; return np.stack([m*np.cos(a),m*np.sin(a)],1)*np.sqrt(2)
rng=np.random.default_rng(3)
from scipy.ndimage import maximum_filter1d
def plim(z,plr):  # lookahead peak control to a target peak-to-loudness ratio
    l=mt.integrated_loudness(z); th=10**((l+plr)/20); pk=maximum_filter1d(np.abs(z).max(1),size=int(0.004*fs))
    g=np.minimum(1,th/np.maximum(pk,1e-9)); a=np.exp(-1/(0.0005*fs)); r=np.exp(-1/(0.06*fs)); out=np.empty_like(g); e=1.0
    for i in range(len(g)):
        v=g[i]; e=v if v<e else r*e+(1-r)*v; out[i]=e
    return z*out[:,None]
def ir(t60,pre=0.015):
    L=int(t60*fs); t=np.arange(L)/fs; e=np.exp(-6.9*t/t60)
    h=rng.standard_normal((L,2))*e[:,None]; h=signal.sosfilt(signal.butter(2,[300,7000],'bandpass',fs=fs,output='sos'),h,axis=0)
    h=np.r_[np.zeros((int(pre*fs),2)),h]; return h/np.sqrt((h**2).sum(0))
H=ir(1.4)
def verb(z): return np.stack([signal.fftconvolve(z[:,0],H[:,0])[:len(z)],signal.fftconvolve(z[:,1],H[:,1])[:len(z)]],1)
P={'surdo':ld('surdo'),'percussao':ld('percussao'),'baixo':pan(ld('baixo'),0),'cavaco':pan(ld('cavaco'),0.3),'violao':pan(ld('violao'),-0.35),
   'epiano':pan(ld('epiano'),-0.2),'pad':ld('pad'),'cordas':ld('cordas')}
P['baixo']=signal.sosfiltfilt(signal.butter(2,35,'highpass',fs=fs,output='sos'),P['baixo'],axis=0)
P['cavaco']=signal.sosfiltfilt(signal.butter(2,250,'highpass',fs=fs,output='sos'),P['cavaco'],axis=0)
P['pad']=signal.sosfiltfilt(signal.butter(2,200,'highpass',fs=fs,output='sos'),P['pad'],axis=0)
# target loudness = reference stem ratios (rel. to a nominal -14 LUFS band+vocal mix)
TGT={'surdo':-22.0,'percussao':-20.5,'baixo':-24.8,'cavaco':-24.0,'violao':-27.5,'epiano':-29.0,'pad':-30.0,'cordas':-32.0}
for k,c in [('percussao',11.0),('cavaco',10.5),('epiano',11.0),('surdo',13.0)]: P[k]=plim(P[k],c)
for k,z in P.items():
    l=mt.integrated_loudness(z); P[k]=z*10**((TGT[k]-l)/20); print(f'{k:10s} {l:6.1f} -> {TGT[k]}')
wet=verb(P['cavaco']*0.5+P['violao']+P['epiano']+P['pad']*0.6+P['cordas'])*10**(-14/20)
band=sum(P.values())+wet
lb=mt.integrated_loudness(band); lv=mt.integrated_loudness(voc)
vg=10**(((lb-3.0)-lv)/20); mix=band+voc*vg
print(f'band {lb:.1f}  vocal {lv:.1f} -> {lb-3.0:.1f}  mix {mt.integrated_loudness(mix):.1f}  peak {20*np.log10(np.abs(mix).max()):.1f}')
mix=signal.sosfiltfilt(signal.butter(4,16500,'lowpass',fs=fs,output='sos'),mix,axis=0)
mix*=10**((-16-mt.integrated_loudness(mix))/20)
sf.write(f'{R}/mix.wav',mix,fs,subtype='FLOAT')
G=10**((-16-mt.integrated_loudness(band+voc*vg))/20)
a=np.abs(mix).max(1); top=np.argsort(a)[-300:]
for k,z in list(P.items())+[('vocal',voc*vg),('verb',wet)]:
    print(f'  at peaks {k:10s} mean |x| {20*np.log10(np.abs(z[top]*G).max(1).mean()+1e-9):6.1f} dBFS')
# quick check: layers/occupancy vs before
def act(z):
    w=int(0.05*fs); k=len(z)//w; e=20*np.log10(np.sqrt((z[:k*w].reshape(k,w,-1)**2).mean((1,2)))+1e-9); return e>np.percentile(e,95)-30
lay=sum(act(z).astype(int) for z in P.values()); print('mean active layers (band):',lay[int(12/0.05):int(180/0.05)].mean().round(2))
