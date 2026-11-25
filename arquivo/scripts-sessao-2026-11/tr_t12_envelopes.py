# Perfil de ataque por semicolcheia (compasso de 2/4) de cada instrumento, por estado, a partir do áudio dos stems
import numpy as np, soundfile as sf, scipy.signal as ss, json
fs=44100; beats=np.load('/home/claude/traicao/beats.npy')
EST={'leve':[(22.8,40.1)],'pre':[(40.1,46.4)],'cheio':[(52.7,101.5),(108,123.5),(131.9,180)],'abertura':[(1.7,22.8)]}
ST={'baixo':('bass (3).flac',(40,400)),'cavaco (1,5–8 kHz)':('guitar (4).flac',(1500,8000)),'violão (80–300 Hz)':('guitar (4).flac',(80,300)),
    'teclado':('piano (4).flac',(100,4000)),'outros':('other (4).flac',(100,4000))}
R={}
for nome,(f,(lo,hi)) in ST.items():
    x,_=sf.read('/home/claude/traicao/stems/'+f,dtype='float32'); x=x.mean(1)
    y=ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),x)
    env=np.sqrt(np.convolve(y**2,np.ones(int(0.005*fs))/int(0.005*fs),'same')); R[nome]={}
    print(f'\n== {nome}   (pico da 16ª em dB rel. ao maior | subida no ataque dB)')
    for e,iv in EST.items():
        bars=[i for i in range(0,len(beats)-2,2) if any(a<=beats[i]<b for a,b in iv)]
        if not bars: continue
        P=np.zeros(32)
        for i in bars:
            t=np.concatenate([beats[i]+np.arange(16)/16*(beats[i+1]-beats[i]),beats[i+1]+np.arange(16)/16*(beats[i+2]-beats[i+1])]); P+=env[(t*fs).astype(int)]
        P=20*np.log10(P/P.max()+1e-9); pk=[P[s*4:(s+1)*4].max() for s in range(8)]; rise=[P[s*4]-P[s*4-1] for s in range(8)]
        R[nome][e]={'pico':[round(float(v),1) for v in pk],'subida':[round(float(v),1) for v in rise]}
        print(f'  {e:8s} '+' '.join(f'{p:5.1f}|{r:+4.1f}' for p,r in zip(pk,rise)))
json.dump(R,open('/home/claude/traicao/envelopes.json','w'),ensure_ascii=False,indent=1)
