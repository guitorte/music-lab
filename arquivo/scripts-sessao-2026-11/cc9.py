import numpy as np, soundfile as sf
from scipy import signal
x,fs=sf.read('/home/claude/cc/src.wav'); M=x.mean(1); Ls=int(np.load('/home/claude/cc/Ls2.npy'))
def env(z,lo,hi,h):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z); w=int(round(h*fs)); k=len(y)//w; return 10*np.log10((y[:k*w].reshape(k,w)**2).mean(1)+1e-12)
h=0.01; t0,t1=47.0,58.0
v1=env(M[int(t0*fs):int(t1*fs)],300,3000,h); v2=env(M[int(t0*fs)+Ls:int(t1*fs)+Ls],300,3000,h); ref=max(v1.max(),v2.max()); v1-=ref; v2-=ref
k1=env(M[int(t0*fs):int(t1*fs)],40,120,h); k2=env(M[int(t0*fs)+Ls:int(t1*fs)+Ls],40,120,h)
# vocal onsets (rises of >12 dB within 40 ms from a quiet state) in each chorus
def onsets(v):
    o=[]
    for i in range(4,len(v)):
        if v[i]>-12 and v[i-4]<-24 and (not o or i-o[-1]>15): o.append(i)
    return np.array(o)
o1,o2=onsets(v1),onsets(v2)
print('vocal phrase onsets after a pause (ch1 time):')
print(' ch1:',' '.join(f'{t0+i*h:.2f}' for i in o1)); print(' ch2:',' '.join(f'{t0+i*h:.2f}' for i in o2))
pairs=[(a,b) for a in o1 for b in o2 if abs(a-b)<=6]
print(' matched (ch1 vs ch2, diff ms):',' '.join(f'{t0+a*h:.2f}/{t0+b*h:.2f}({(b-a)*h*1000:+.0f})' for a,b in pairs))
# shared quiet windows (both vocals < -25 dB for >= 60 ms), with local vocal-envelope correlation over the next 2 s
q=(v1<-25)&(v2<-25); runs=[]; i=0
while i<len(q):
    if q[i]:
        j=i
        while j<len(q) and q[j]: j+=1
        if j-i>=6: runs.append((i,j))
        i=j
    else: i+=1
print('shared vocal pauses (ch1 time), length, and how well the following 2 s of vocal line up:')
for i,j in runs:
    a=v1[j:j+200]; b=v2[j:j+200]
    if len(a)<50: continue
    c=np.corrcoef(np.maximum(a,-40),np.maximum(b,-40))[0,1]
    nxt1=next((t0+o*h for o in o1 if o>=j-2),None); nxt2=next((t0+o*h for o in o2 if o>=j-2),None)
    print(f'  {t0+i*h:.2f}-{t0+j*h:.2f} ({(j-i)*10} ms)  next-2s vocal corr {c:.2f}  next entry ch1 {nxt1} ch2 {nxt2}')
