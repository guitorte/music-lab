import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/vr/mix.wav'); mx,_=sf.read('/home/claude/v/mix.wav'); old,_=sf.read('/home/claude/v/master.wav')
m=pyln.Meter(fs)
for lab,z in [('new remaster',x),('old mix',mx),('old master',old)]:
    up=signal.resample_poly(z,4,1,axis=0); mo=z.mean(1); k=len(mo)//(fs//10); r=mo[:k*(fs//10)].reshape(k,-1)
    lo=signal.sosfilt(signal.butter(4,120,'lowpass',fs=fs,output='sos'),z,axis=0)
    print(f'{lab:13s} len {len(z)/fs:.1f}s LUFS {m.integrated_loudness(z):.2f} TP {20*np.log10(np.abs(up).max()):+.2f} crest {np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9)):.1f} corr {np.corrcoef(z[:,0],z[:,1])[0,1]:.2f} side<120 {10*np.log10((((lo[:,0]-lo[:,1])/2)**2).mean()/((lo.mean(1))**2).mean()):.0f}')
bands=[30,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000]
def spec(z):
    f,P=signal.welch(z.mean(1),fs,nperseg=16384); P=P/P[(f>200)&(f<5000)].sum(); return np.array([10*np.log10(P[(f>=c/2**(1/6))&(f<c*2**(1/6))].sum()) for c in bands])
sn,sm,so=spec(x),spec(mx),spec(old)
print('band   new-oldmix  oldmaster-oldmix  new-oldmaster')
for i,c in enumerate(bands): print(f'{c:6d} {sn[i]-sm[i]:+6.1f} {so[i]-sm[i]:+8.1f} {sn[i]-so[i]:+8.1f}')
# is it the same arrangement/timing?
n=min(len(x),len(mx)); a=x[:n].mean(1); b=mx[:n].mean(1)
e=lambda z: np.log((signal.sosfilt(signal.butter(2,[100,4000],'bandpass',fs=fs,output='sos'),z)[:n//480*480].reshape(-1,480)**2).mean(1)+1e-12)
ea,eb=e(a),e(b); c=signal.correlate(ea-ea.mean(),eb-eb.mean(),'full'); L=np.argmax(c)-(len(eb)-1); print('envelope lag %.3f s, corr %.2f'%(L*0.01,c.max()/np.sqrt(((ea-ea.mean())**2).sum()*((eb-eb.mean())**2).sum())))
