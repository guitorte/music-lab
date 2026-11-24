import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
x,fs=sf.read('/home/claude/c/mix.wav'); m=x.mean(1)
# tonal balance: 1/3-oct, normalized, vs pink (-3dB/oct => flat in 1/3 oct sum? pink = equal energy per octave -> flat)
cent=[25,31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000,20000]
f,P=signal.welch(m,fs,nperseg=32768)
b=[]
for c in cent:
    mm=(f>=c/2**(1/6))&(f<c*2**(1/6)); b.append(10*np.log10(P[mm].sum()))
b=np.array(b); ref=b[(np.array(cent)>=500)&(np.array(cent)<=2000)].mean()
print('1/3-oct level rel. to 500-2k avg (pink=0, typical modern mix slopes down ~-4 to -6 dB by 10k, sub ~ +2..+5):')
print(' '.join(f'{c}:{v-ref:+.1f}' for c,v in zip(cent,b)))
# stereo
def bpx(x,lo,hi):
    s=signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'); return signal.sosfiltfilt(s,x,axis=0)
print('\nstereo side/mid dB (corr):')
for lo,hi in [(20,120),(120,500),(500,2000),(2000,8000),(8000,20000)]:
    y=bpx(x,lo,hi); M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
    print(f' {lo}-{hi}: {10*np.log10((S**2).sum()/(M**2).sum()):.1f} ({np.corrcoef(y[:,0],y[:,1])[0,1]:.2f})')
print(' L/R level diff dB:',round(10*np.log10((x[:,0]**2).mean()/(x[:,1]**2).mean()),2))
# section loudness (short-term over time, 10s)
meter=pyln.Meter(fs)
print('\nloudness per 10s:',[round(meter.integrated_loudness(x[i:i+fs*10]),1) for i in range(0,len(x)-fs*10+1,fs*10)])
# crest / PLR
pk=np.abs(x).max(); print('PLR (peak - LUFS):', round(20*np.log10(pk)-meter.integrated_loudness(x),1))
# short-term crest 100 ms median
w=fs//10; k=len(m)//w; xr=m[:k*w].reshape(k,w); cr=20*np.log10(np.abs(xr).max(1)/np.sqrt((xr**2).mean(1))+1e-9)
print('median 100ms crest dB',round(np.median(cr[np.sqrt((xr**2).mean(1))>1e-3]),1))
# sibilance: 5-9k short-term peaks vs 1-4k
def env(y,w=480):
    k=len(y)//w; return 10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-14)
s=env(bpx(m,5000,9000)); p=env(bpx(m,1000,4000)); d=s-p
print('sibilance index: median 5-9k minus 1-4k',round(np.median(d),1),' 99th pct',round(np.percentile(d,99),1))
# low-mid build-up: 200-400 vs 80-160 and 1-2k
# resonances: narrow peaks in long-term spectrum 60-6000
ff,PP=signal.welch(m,fs,nperseg=65536); Pd=10*np.log10(PP+1e-20); base=signal.medfilt(Pd,151); pr=Pd-base
mm=(ff>60)&(ff<6000)&(pr>8); 
g=[]
for fr,p in zip(ff[mm],pr[mm]):
    if g and fr-g[-1][0]<fr*0.03: g[-1]=(g[-1][0],max(g[-1][1],p))
    else: g.append((fr,p))
print('\nnarrow spectral peaks (>8 dB above local median):',[(int(a),round(b,1)) for a,b in g][:15])
# sub content below 30 Hz
print('energy <30 Hz rel total dB', round(10*np.log10(PP[ff<30].sum()/PP.sum()),1))
