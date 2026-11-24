import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); ins,_=sf.read(D+'Instrumental.wav')
db=lambda z: 10*np.log10((z**2).mean()+1e-20)
# where is the residual mix-(voc+ins)? over time and frequency
r=mix-(voc+ins)
for t0 in range(0,150,15):
    s=slice(t0*fs,(t0+15)*fs); print(f'{t0:3d}-{t0+15}s residual {db(r[s])-db(mix[s]):6.1f} dB rel mix')
f,Pr=signal.welch(r.mean(1),fs,nperseg=8192); _,Pm=signal.welch(mix.mean(1),fs,nperseg=8192)
print('residual spectrum rel mix (dB):',' '.join(f'{c}:{10*np.log10(Pr[(f>=c/1.4)&(f<c*1.4)].sum()/Pm[(f>=c/1.4)&(f<c*1.4)].sum()):+.0f}' for c in [50,100,200,500,1000,2000,4000,8000,16000]))
# is mix just scaled/processed? LS gains
X=np.stack([voc[:,0],ins[:,0]],1); g=np.linalg.lstsq(X,mix[:,0],rcond=None)[0]; print('LS gains voc,ins (L):',np.round(g,3))
print('residual after LS gains: %.1f dB'%(db(mix[:,0]-X@g)-db(mix[:,0])))
# peaks
print('peak mix %.2f dBFS, peak voc+ins %.2f dBFS'%(20*np.log10(np.abs(mix).max()),20*np.log10(np.abs(voc+ins).max())))
