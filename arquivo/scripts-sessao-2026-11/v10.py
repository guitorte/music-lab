import numpy as np, soundfile as sf
from scipy import signal
D='/home/claude/vz/w/'
mix,fs=sf.read(D+'track_original.wav'); voc,_=sf.read(D+'vocais_original.wav'); ins,_=sf.read(D+'instrumental_isolado.wav'); cor,_=sf.read(D+'vocais_fix.wav')
cor=np.r_[cor,np.zeros((len(voc)-len(cor),2))]; cor=np.roll(cor,1,axis=0)
out=np.load(D+'out2.npy'); P=np.load(D+'parts.npy',allow_pickle=True)
name,W0,yr,yn=[p for p in P if p[0]=='casal'][0]
n=len(yr); s=slice(int(W0*fs),int(W0*fs)+n)
def bl(z,lo,hi,t0,t1,off=W0):
    y=signal.sosfiltfilt(signal.butter(4,[lo,hi],'bandpass',fs=fs,output='sos'),z,axis=0)
    seg=y[int((t0-off)*fs):int((t1-off)*fs)]; return 10*np.log10((seg**2).mean()+1e-14)
comp={'mix':mix[s],'out':out[s],'yr(mix sem voz)':yr,'yn(voz nova)':yn,'ins':ins[s]*0.736,'cor':cor[s],'voc':voc[s]}
bands=[(100,500),(500,2000),(2000,5000),(5000,10000),(10000,20000)]
for t0 in np.arange(55.2,57.2,0.1):
    print(f'{t0:5.1f}',' | '.join(f'{k[:4]}:'+','.join(f'{bl(v,lo,hi,t0,t0+0.1):4.0f}' for lo,hi in bands[2:]) for k,v in comp.items() if k in('mix','out','yr(mix sem voz)','yn(voz nova)','cor')))
# noise floor of the fix stem in silent places (whole song), and spectral flatness
for lab,z in [('voc',voc),('cor',cor)]:
    for t0,t1 in [(1.5,12),(99,112)]:
        print(lab,t0,t1,'rms dB by band',[round(bl(z,lo,hi,t0,t1,0),1) for lo,hi in bands])
