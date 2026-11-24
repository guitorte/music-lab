import numpy as np, soundfile as sf
from scipy import signal
fs=48000; D='/home/claude/q/w/'
voc,_=sf.read(D+'Vocais_isolados.wav'); cor,_=sf.read(D+'Vocais_corrigidos.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
def bands(z,t):
    s=z[int(t*fs):int((t+0.02)*fs)].mean(1)
    def b(lo,hi):
        y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z[int((t-0.05)*fs):int((t+0.07)*fs)].mean(1))[int(0.05*fs):int(0.07*fs)]
        return 10*np.log10((y**2).mean()+1e-14)
    return b(80,500),b(500,2000),b(2000,8000)
def pitch(z,t):
    s=z[int(t*fs):int((t+0.04)*fs)].mean(1); s=s-s.mean()
    if (s**2).mean()<1e-7: return 0,0
    ac=np.correlate(s,s,'full')[len(s)-1:]; lo,hi=int(fs/600),int(fs/70)
    i=np.argmax(ac[lo:hi])+lo; return fs/i, ac[i]/ac[0]
print('            CORRECTED vocal                         |  ORIGINAL vocal')
print(' time   <500  .5-2k  >2k   pitch(Hz) voicing |  <500  .5-2k  >2k   pitch voicing')
for t in np.arange(105.90,106.46,0.02):
    a=bands(cor,t); p=pitch(cor,t); b=bands(voc,t); q=pitch(voc,t)
    print(f'{t:6.2f} {a[0]:6.1f} {a[1]:6.1f} {a[2]:6.1f} {p[0]:7.0f} {p[1]:6.2f}  | {b[0]:6.1f} {b[1]:6.1f} {b[2]:6.1f} {q[0]:6.0f} {q[1]:5.2f}')
