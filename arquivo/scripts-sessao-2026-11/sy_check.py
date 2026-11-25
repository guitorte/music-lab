import numpy as np, soundfile as sf, scipy.signal as ss, pretty_midi as pm, pyloudnorm as pl
fs=44100; D='/home/claude/vit/stems_zip/'
st={k:sf.read(D+f,always_2d=True)[0].mean(1) for k,f in [('guitar','vit live mast - guitar.flac'),('other','vit live mast - other.flac'),('piano','vit live mast - piano.flac'),('voz','vit live mast - vocals.flac')]}
pad=sf.read('/home/claude/sy/pad.wav',always_2d=True)[0].mean(1); plk=sf.read('/home/claude/sy/pluck.wav',always_2d=True)[0].mean(1)
L=min(len(pad),*(len(v) for v in st.values())); st={k:v[:L] for k,v in st.items()}; pad,plk=pad[:L],plk[:L]; syn=pad+plk
bp=lambda x,lo,hi: ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),x)
cam0=bp(st['piano']+st['other']+st['guitar'],150,4000); cam1=cam0+bp(syn,150,4000)
B=np.load('/home/claude/vit/w/analysis.npz')['beats']
db=lambda x,a,b: 20*np.log10(np.sqrt((x[int(a*fs):int(b*fs)]**2).mean())+1e-12)
SEC=[('verso1',8.9,20),('verso2',20,31.5),('pre1',31.5,44.1),('refrao1',44.8,69.2),('pos',69.2,81.9),('pre2',87.6,100.6),('refrao2',101.4,124.7),('refrao3',124.7,150.1),('final',150.1,162.3)]
ref=np.median([db(cam0,B[i],B[i+1]) for i in range(len(B)-1) if 44.8<=B[i]<69])
print('cama harmônica por tempo, rel. à mediana do refrão original (antes -> depois):')
for n,a,b in SEC:
    bb=[i for i in range(len(B)-1) if a<=B[i]<b]; c0=np.array([db(cam0,B[i],B[i+1]) for i in bb])-ref; c1=np.array([db(cam1,B[i],B[i+1]) for i in bb])-ref
    print(f'  {n:8s} mediana {np.median(c0):+5.1f} -> {np.median(c1):+5.1f}   p10 (buracos) {np.percentile(c0,10):+5.1f} -> {np.percentile(c1,10):+5.1f}')
print('\nparadas (síntese, dBFS):',' '.join(f'{a:.1f}s:{db(syn,a+0.03,b-0.03):.0f}' for a,b in [(41.16,41.38),(42.81,43.07),(43.40,43.74),(44.13,44.77),(97.73,98.0),(99.32,99.69),(100.01,100.37),(100.93,101.37)]))
VN=pm.PrettyMIDI('/home/claude/vt/w/voz.mid').instruments[0].notes; act=np.zeros(L,bool)
for n in VN: act[int(n.start*fs):int(n.end*fs)]=True
v14=bp(st['voz'],1000,4000)[act]; s14=bp(syn,1000,4000)[act]
print('\nvoz x síntese em 1–4 kHz enquanto a voz canta: margem %.1f dB'%(10*np.log10((v14**2).mean()/(s14**2).mean())))
src,_=sf.read('/home/claude/mt/edit.wav',always_2d=True); m=pl.Meter(fs)
for n,a,b in SEC: print(f'  pad+plucks rel. à mix em {n:8s}: {m.integrated_loudness(np.stack([syn,syn],1)[int(a*fs):int(b*fs)])-m.integrated_loudness(src[int(a*fs):int(b*fs)]):+.1f} LU')
