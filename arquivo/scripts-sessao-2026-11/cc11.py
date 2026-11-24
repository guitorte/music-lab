import numpy as np, soundfile as sf, librosa, sys
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1).astype(np.float32)
def ons(lo,hi,t0,t1):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),M[int(t0*fs):int(t1*fs)]).astype(np.float32)
    return librosa.onset.onset_detect(y=y,sr=fs,hop_length=64,units='time',backtrack=False,delta=0.2)+t0
def env(t0,t1,lo,hi,h=0.01):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),M[int(t0*fs):int(t1*fs)]); w=int(h*fs); k=len(y)//w; return 10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-12)
def analyse(a0,a1,lo,hi,label):
    # a0..a1 in the EARLIER chorus; search lag in [lo,hi]
    A=[ons(40,120,a0,a1),ons(4000,12000,a0,a1)]; B=[ons(40,120,a0+lo-0.3,a1+hi+0.3),ons(4000,12000,a0+lo-0.3,a1+hi+0.3)]
    va=env(a0,a1,300,3000)
    res=[]
    for L in np.arange(lo,hi,0.0005):
        dr=np.mean([np.sum(np.abs(a[:,None]-(b[None,:]-L)).min(1)<0.008)/len(a) for a,b in zip(A,B)])
        vb=env(a0+L,a1+L+0.05,300,3000)[:len(va)]; vc=np.corrcoef(np.maximum(va,va.max()-40),np.maximum(vb,vb.max()-40))[0,1]
        res.append((L,dr,vc))
    res=np.array(res); sc=res[:,1]+res[:,2]; i=np.argmax(sc); L=res[i,0]
    print(f'{label}: best lag {L:.4f} (drum hits {res[i,1]*100:.0f}%, vocal-envelope corr {res[i,2]:.2f}); drum-only best {res[np.argmax(res[:,1]),0]:.4f}, vocal-only best {res[np.argmax(res[:,2]),0]:.4f}')
    v1=env(a0,a1,300,3000); v2=env(a0+L,a1+L+0.05,300,3000)[:len(v1)]; ref=max(v1.max(),v2.max()); v1-=ref; v2-=ref
    q=(v1<-25)&(v2<-25); i=0
    while i<len(q):
        if q[i]:
            j=i
            while j<len(q) and q[j]: j+=1
            if j-i>=8: print(f'    shared vocal pause {a0+i*0.01:.2f}-{a0+j*0.01:.2f} ({(j-i)*10} ms) [earlier-chorus time]')
            i=j
        else: i+=1
    return L
L_start=analyse(58.0,64.0,66.2,66.8,'chorus START  ch2 -> ch3')
L_end=analyse(89.5,97.0,66.2,66.8,'LAST LINE     ch2 -> ch3')
np.save('/home/claude/cc/L23.npy',np.array([L_start,L_end]))
