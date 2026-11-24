import numpy as np, soundfile as sf
from scipy import signal
fs=48000
a,_=sf.read('/home/claude/s/orig.wav'); b,_=sf.read('/home/claude/s/rem.wav')
s0,s1=120*fs,150*fs; A=a[s0:s1]; B=b[s0:s1]
fade=np.ones(len(A)); r=fs//10; fade[:r]=np.linspace(0,1,r); fade[-r:]=np.linspace(1,0,r)
hp=signal.butter(8,8000,'highpass',fs=fs,output='sos')
g=10**(18/20)
for nm,X in [('1_original_above_8kHz',A),('2_suno_v6_above_8kHz',B)]:
    y=signal.sosfiltfilt(hp,X,axis=0)*g*fade[:,None]; sf.write(f'out/{nm}.wav',np.clip(y,-1,1),fs)
# notch the tonal lines in remaster
y=B.copy()
for f0 in [8800,11893,12796,13799,14399,17199]:
    bq,aq=signal.iirnotch(f0,25,fs); y=signal.filtfilt(bq,aq,y,axis=0)
sf.write('out/3_suno_v6_lines_removed.wav',y*fade[:,None],fs)
sf.write('out/0_suno_v6_unchanged.wav',B*fade[:,None],fs)
# verify line removal
for nm,x in [('before',B.mean(1)),('after',y.mean(1))]:
    ff,P=signal.welch(x,fs,nperseg=65536); Pd=10*np.log10(P+1e-20); base=signal.medfilt(Pd,101)
    print(nm,[round(float((Pd-base)[np.argmin(abs(ff-f0))]),1) for f0 in [8800,11893,12796,13799,14399,17199]])
