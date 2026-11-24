import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
D='/home/claude/pg/w/'; names=['vocals','drums','bass','guitar','piano','other']
mix,fs=sf.read('/home/claude/so/mix.wav'); S={}
for n in names:
    z,_=sf.read(D+n+'.wav'); z=np.r_[z,np.zeros((max(0,len(mix)-len(z)),2))][:len(mix)]; S[n]=z
tot=sum(S.values()); db=lambda z: 10*np.log10((z**2).mean()+1e-20)
print('sum of stems vs track: residual %.1f dB (rel. track)'%(db(mix-tot)-db(mix)))
X=np.stack([S[n][:,0] for n in names],1); g=np.linalg.lstsq(X,mix[:,0],rcond=None)[0]; print('LS gains:',dict(zip(names,np.round(g,2))))
m=pyln.Meter(fs)
def L(z,a,b):
    try: return m.integrated_loudness(z[int(a*fs):int(b*fs)])
    except: return -99
print('stem       whole  body(12-158) outro(158.5-167)  outro L/R corr   body L/R corr')
for n in names:
    z=S[n]; o=z[int(158.5*fs):]; b=z[int(12*fs):int(158*fs)]
    c=lambda q: np.corrcoef(*q.T)[0,1] if q.std()>1e-6 else np.nan
    print(f'{n:8s} {L(z,0,167.4):6.1f} {L(z,12,158):10.1f} {L(z,158.5,167.4):12.1f} {c(o):14.2f} {c(b):14.2f}')
np.save('/home/claude/pg/w/g.npy',g)
