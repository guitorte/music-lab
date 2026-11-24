import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/q/w/'
mix,fs=sf.read(D+'Que_nem_eu_ITA.wav'); voc,_=sf.read(D+'Vocais_isolados.wav'); ins,_=sf.read(D+'Instrumental.wav')
N=2048; H=512
T0,T1=92.0,118.0
s=slice(int(T0*fs),int(T1*fs))
def stft(z): return signal.stft(z,fs,nperseg=N,noverlap=N-H)
res={}
for ch in (0,1):
    f,t,M=stft(mix[s,ch]); _,_,V=stft(voc[s,ch]); _,_,I=stft(ins[s,ch])
    tt=t+T0; word=(tt>104.9)&(tt<106.25); fit=~word
    av=np.zeros(len(f),complex); ai=np.zeros(len(f),complex)
    for k in range(len(f)):
        X=np.stack([V[k,fit],I[k,fit]],1); y=M[k,fit]
        sol=np.linalg.lstsq(X,y,rcond=None)[0]; av[k],ai[k]=sol
    R=M-(av[:,None]*V+ai[:,None]*I)
    e=lambda Z,m: 10*np.log10((np.abs(Z[:,m])**2).sum()+1e-20)
    print(f'ch{ch}: residual vs mix  fit-region {e(R,fit)-e(M,fit):.1f} dB | word-region {e(R,word)-e(M,word):.1f} dB')
    # ghost test: in the word region, how much of the old vocal is left after removing av*V?
    VV=av[:,None]*V
    vb=(f>300)&(f<5000)
    ew=lambda Z: 10*np.log10((np.abs(Z[np.ix_(vb,word)])**2).sum()+1e-20)
    print(f'      word region 300-5k: old vocal in mix {ew(VV):.1f} | unexplained residual {ew(R):.1f} | ratio {ew(R)-ew(VV):.1f} dB')
    print('      |av| by band (dB):',' '.join(f'{c}:{20*np.log10(np.abs(av[(f>=c/1.4)&(f<c*1.4)]).mean()):+.1f}' for c in [100,300,1000,3000,8000,14000]))
    res[ch]=(av,ai)
np.save('/home/claude/q/w/gains.npy',np.array([res[0][0],res[0][1],res[1][0],res[1][1]]))
