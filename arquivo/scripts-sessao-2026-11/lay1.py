import numpy as np, soundfile as sf, glob
from scipy import signal
names=['vocals','drums','bass','guitar','piano','other']
def load(d):
    S={}
    for n in names:
        z,fs=sf.read(glob.glob(f'{d}/{n}*.flac')[0]); S[n]=z[8*fs:182*fs]
    return S,fs
H=0.02
def lev(z,fs,h=H):
    w=int(h*fs); k=len(z)//w; return 20*np.log10(np.sqrt((z[:k*w].reshape(k,w,-1)**2).mean((1,2)))+1e-9)
res={}
for lab,d in [('REAL','/home/claude/ref/stems'),('AI','/home/claude/ai2/stems')]:
    S,fs=load(d); L={n:lev(S[n],fs) for n in names}; mins=len(L['vocals'])*H/60
    act={n:(L[n]>max(np.percentile(L[n],95)-30,-60)) for n in names}
    print(f'=== {lab}')
    print('   stem      active%  drops>20dB/40ms per min  short gaps(30-250ms) per min  level range p95-p10 (dB)')
    for n in names:
        l=L[n]; a=act[n]
        drop=np.sum((l[:-2]-l[2:]>20)&a[:-2])/mins                       # sudden cut within 40 ms
        # short gaps inside activity: runs of inactive frames of 2..12 frames bounded by activity
        gaps=0; i=0; ia=a.astype(int)
        while i<len(ia):
            if ia[i]==0:
                j=i
                while j<len(ia) and ia[j]==0: j+=1
                if 2<=j-i<=12 and i>0 and j<len(ia): gaps+=1
                i=j
            else: i+=1
        print(f'   {n:8s} {a.mean()*100:6.0f}% {drop:14.1f} {gaps/mins:26.1f} {np.percentile(l[a],95)-np.percentile(l[a],10):22.1f}')
    stack=np.stack([act[n] for n in names]); nl=stack.sum(0)
    print('   simultaneous layers: mean %.2f | time with >=4 layers %.0f%% | with <=2 layers %.0f%%'%(nl.mean(),(nl>=4).mean()*100,(nl<=2).mean()*100))
    L100={n:lev(S[n],fs,0.1) for n in names}; C=np.corrcoef(np.stack([L100[n] for n in names]))
    print('   stems move together? mean pairwise corr of 100 ms levels: %.2f'%(C[np.triu_indices(6,1)].mean()))
    # percussion voices inside drums stem
    dr=S['drums'].mean(1); bands={'surdo 40-120':(40,120),'tanta 120-400':(120,400),'mid 400-2k':(400,2000),'slap/tamborim 2-6k':(2000,6000),'platinela 6-14k':(6000,14000)}
    E={}
    for k,(lo,hi) in bands.items():
        q=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),dr); E[k]=lev(q[:,None],fs)
    print('   drum bands: active% / hits per s:',' | '.join(f'{k}: {(E[k]>np.percentile(E[k],95)-30).mean()*100:.0f}% / {np.sum(np.diff((E[k]>np.percentile(E[k],95)-12).astype(int))==1)/(len(E[k])*H):.1f}' for k in E))
    CE=np.corrcoef(np.stack(list(E.values()))); print('   independence of drum bands (mean pairwise corr, lower = more separate instruments): %.2f'%CE[np.triu_indices(5,1)].mean())
    # spectral fill of the full mix
    mix=sum(S.values()).mean(1); f,t,Z=signal.stft(mix,fs,nperseg=2048,noverlap=1024); A=20*np.log10(np.abs(Z)+1e-9); sel=(f>80)&(f<8000); A=A[sel]
    occ=(A>A.max(0,keepdims=True)-40).mean(); 
    from scipy.ndimage import median_filter
    nb=median_filter(A,size=(1,9)); holes=((A<nb-20)).mean()
    print('   mix spectrogram 80-8k: occupied bins %.0f%% | time-holes (bin >20 dB below its own neighborhood in time) %.1f%%'%(occ*100,holes*100))
