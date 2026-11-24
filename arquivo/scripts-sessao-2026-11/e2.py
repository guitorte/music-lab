import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/e/mix.wav'); L,R=x[:,0],x[:,1]
def bp(z,lo,hi): return signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z)
print('inter-channel lag (ms) at max |xcorr| and its value, per band (positive = R later):')
for lo,hi in [(120,500),(500,2000),(2000,8000),(8000,16000)]:
    l,r=bp(L,lo,hi),bp(R,lo,hi); seg=slice(20*fs,80*fs)
    c=signal.correlate(r[seg],l[seg],'full',method='fft'); lags=np.arange(-len(l[seg])+1,len(l[seg]))
    m=np.abs(lags)<int(0.004*fs); cc=c[m]/np.sqrt((l[seg]**2).sum()*(r[seg]**2).sum()); lg=lags[m]
    i=np.argmax(np.abs(cc)); print(f' {lo}-{hi}: lag {lg[i]/fs*1000:+.2f} ms, corr {cc[i]:+.2f} (at 0 ms: {cc[lg==0][0]:+.2f})')
# percussion onsets: transients in 2-8k; panning and per-onset L/R lag
y=bp(L+R,2000,8000); w=int(0.005*fs); k=len(y)//w; e=10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-14)
on=np.where(np.diff(e)>9)[0]; on=on[(on>10)&(on<k-20)]
# dedupe
keep=[]; 
for o in on:
    if not keep or o-keep[-1]>20: keep.append(o)
pans=[];lags=[];cors=[]
lb,rb=bp(L,2000,8000),bp(R,2000,8000)
for o in keep:
    s=slice(o*w,o*w+int(0.03*fs)); a,b=lb[s],rb[s]
    pans.append(10*np.log10((b**2).sum()/(a**2).sum()))
    c=signal.correlate(b,a,'full'); lg=np.arange(-len(a)+1,len(a)); m=np.abs(lg)<int(0.003*fs)
    cc=c[m]/np.sqrt((a**2).sum()*(b**2).sum()); i=np.argmax(cc); lags.append(lg[m][i]/fs*1000); cors.append(cc[i])
pans=np.array(pans); lags=np.array(lags); cors=np.array(cors)
print(f'\n{len(keep)} percussive onsets (2-8 kHz). R-minus-L level dB: median {np.median(pans):+.1f}, p10 {np.percentile(pans,10):+.1f}, p90 {np.percentile(pans,90):+.1f}')
print(f' per-onset L/R lag ms: median {np.median(lags):+.2f}, p10 {np.percentile(lags,10):+.2f}, p90 {np.percentile(lags,90):+.2f}; best corr median {np.median(cors):.2f}')
# mono loss per band
print('\nmono fold-down loss per band (dB, mono vs stereo avg):')
for lo,hi in [(120,500),(500,2000),(2000,8000),(8000,16000)]:
    l,r=bp(L,lo,hi),bp(R,lo,hi); st=((l**2+r**2)/2).mean(); mo=(((l+r)/2)**2).mean(); print(f' {lo}-{hi}: {10*np.log10(mo/st):+.1f}')
# room / reverb amount: decay after onsets (clarity) not trivial; skip. Crowd? check level of side in quiet moments
