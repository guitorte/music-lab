import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal
src=open('/home/claude/scripts/e3.py').read(); exec(src[:src.index('# 1 HPF')])
x,fs=sf.read('/home/claude/p/mix.wav'); n=len(x)
def bp(z,lo,hi,o=4): return signal.sosfiltfilt(signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
y=signal.sosfilt(signal.butter(2,30,'highpass',fs=fs,output='sos'),x,axis=0)
M=(y[:,0]+y[:,1])/2; S=(y[:,0]-y[:,1])/2
S=S-signal.sosfiltfilt(signal.butter(4,100,'lowpass',fs=fs,output='sos'),S); y=np.stack([M+S,M-S],1)
# dynamic cut on the 60 Hz note, up to -5 dB
bb,ba=signal.iirpeak(61,3,fs); band=signal.lfilter(bb,ba,y,axis=0); lv=ctrl(band)
thr=np.percentile(lv[lv>-90],45); gr=env_follow(np.clip((lv-thr)*0.6,0,5),0.01,0.12)
y=y+band*(upg(-gr,n)[:,None]-1); print('60 Hz dyn cut avg %.1f max %.1f'%(gr.mean(),gr.max()))
y=eq(y,[peq(60,-1.5,2.0),peq(160,-1.5,1.0),peq(463,-1.5,4),peq(707,-2.5,3),peq(3000,1.5,0.8),shelf(10000,1.5)])
ref=ctrl(bp(y,500,2000,2))
for lo_,hi_ in [(6000,12000)]:
    b_=bp(y,lo_,hi_,2); dd=ctrl(b_)-ref; th=np.percentile(dd,95)
    g=env_follow(np.clip((dd-th)*0.7,0,3.0),0.002,0.07); y=y+b_*(upg(-g,n)[:,None]-1)
    print(f'de-harsh {lo_}-{hi_}: max {g.max():.1f}')
sf.write('/home/claude/p/prelim.wav',y,fs,subtype='FLOAT')
