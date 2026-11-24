import numpy as np, soundfile as sf, glob, librosa
from scipy import signal
names=['vocals','drums','bass','guitar','piano','other']
def feats(z,fs):
    M=z.mean(1); f,t,Z=signal.stft(M,fs,nperseg=4096,noverlap=2048); A=np.abs(Z)**2
    fl=A.sum(0); act=fl>np.percentile(fl,95)*10**(-30/10); A=A[:,act]
    if A.shape[1]<10: return None
    P=A.mean(1); cen=(f[:,None]*A).sum(0)/A.sum(0)
    cs=np.cumsum(P)/P.sum(); roll=f[np.searchsorted(cs,0.85)]
    ref=10*np.log10(P[(f>1000)&(f<4000)].mean()+1e-20); Ld=10*np.log10(P+1e-20)
    hi=np.where((f>4000)&(Ld>ref-40))[0]; cutoff=f[hi.max()] if len(hi) else 4000
    flat=np.median(np.exp(np.log(A[(f>200)&(f<8000)]+1e-20).mean(0))/A[(f>200)&(f<8000)].mean(0))
    y=librosa.resample(M.astype(np.float32),orig_sr=fs,target_sr=22050); Hh,Pp=librosa.effects.hpss(y); hp=10*np.log10((Hh**2).sum()/((Pp**2).sum()+1e-12))
    # attack and decay around onsets
    on=librosa.onset.onset_detect(y=y,sr=22050,units='samples',hop_length=128,backtrack=True)
    w=int(0.002*22050); env=np.sqrt(np.convolve(y**2,np.ones(w)/w,'same'))
    att=[];dec=[]
    for o in on[:400]:
        seg=env[o:o+int(0.6*22050)]
        if len(seg)<100 or seg.max()<1e-4: continue
        pk=np.argmax(seg[:int(0.12*22050)]); att.append(pk/22050*1000)
        tail=seg[pk:]; below=np.where(tail<seg[pk]*0.1)[0]; dec.append((below[0] if len(below) else len(tail))/22050*1000)
    S=(z[:,0]-z[:,1])/2; width=10*np.log10((S**2).mean()/((M**2).mean()+1e-12)+1e-12)
    return dict(cen=np.median(cen),roll=roll,cut=cutoff,flat=flat,hp=hp,att=np.median(att) if att else np.nan,dec=np.median(dec) if dec else np.nan,width=width)
print('stem     ver  | brightness(centroid)  85% rolloff  top end (-40 dB)  noisiness(flatness)  tonal vs percussive  attack   decay to -20dB  stereo side vs mid')
for n in names:
    for lab,d in [('REAL','/home/claude/ref/stems'),('AI','/home/claude/ai2/stems')]:
        z,fs=sf.read(glob.glob(f'{d}/{n}*.flac')[0]); r=feats(z[8*fs:182*fs],fs)
        if r is None: print(f'{n:8s} {lab:4s} | (almost silent)'); continue
        print(f'{n:8s} {lab:4s} | {r["cen"]:8.0f} Hz {r["roll"]:12.0f} Hz {r["cut"]:12.0f} Hz {r["flat"]:16.3f} {r["hp"]:+14.1f} dB {r["att"]:7.0f} ms {r["dec"]:9.0f} ms {r["width"]:+12.1f} dB')
