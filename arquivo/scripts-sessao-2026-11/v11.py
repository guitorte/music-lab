import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); voc,_=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav')
P=np.load(D+'parts.npy',allow_pickle=True)
for name,W0,yr,yn in P:
    s=slice(int(W0*fs),int(W0*fs)+len(yr)); N=2048;H=480
    f,t,Y=signal.stft(yr.mean(1),fs,nperseg=N,noverlap=N-H); _,_,M=signal.stft(mix[s].mean(1),fs,nperseg=N,noverlap=N-H)
    _,_,V=signal.stft(voc[s].mean(1),fs,nperseg=N,noverlap=N-H); _,_,I=signal.stft(ins[s].mean(1),fs,nperseg=N,noverlap=N-H)
    tt=t+W0; R={'casal':(55.46,56.85),'achar':(68.62,69.31),'cara':(84.53,85.20)}[name]; w=(tt>R[0])&(tt<R[1])
    print(f'=== {name}: how much does each signal follow the OLD vocal (corr of log-magnitude over time, per band); and level drop mix->yr')
    for lo,hi in [(100,300),(300,800),(800,2000),(2000,5000),(5000,10000)]:
        b=(f>=lo)&(f<hi)
        ev=np.log(np.abs(V[b][:,w]).sum(0)+1e-9); em=np.log(np.abs(M[b][:,w]).sum(0)+1e-9); ey=np.log(np.abs(Y[b][:,w]).sum(0)+1e-9); ei=np.log(np.abs(I[b][:,w]).sum(0)+1e-9)
        drop=20*np.log10(np.abs(Y[b][:,w]).sum()/np.abs(M[b][:,w]).sum())
        print(f'  {lo}-{hi}: mix~voc {np.corrcoef(em,ev)[0,1]:.2f}  yr~voc {np.corrcoef(ey,ev)[0,1]:.2f}  yr~ins {np.corrcoef(ey,ei)[0,1]:.2f}  ins~voc {np.corrcoef(ei,ev)[0,1]:.2f} | yr vs mix {drop:+.1f} dB')
