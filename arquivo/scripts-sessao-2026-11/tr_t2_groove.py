# Traição: groove por faixa de frequência do stem de bateria e pelos MIDIs de bateria (ADTOF)
import numpy as np, soundfile as sf, librosa, scipy.signal as ss, pretty_midi as pm
fs=44100; dr,_=sf.read('/home/claude/traicao/stems/drums (3).flac',dtype='float32'); dr=dr.mean(1)
beats=np.load('/home/claude/traicao/beats.npy'); hop=128
def band(x,lo,hi):
    sos=ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'); return ss.sosfiltfilt(sos,x).astype(np.float32)
# realinha a grade ao ataque mediano do grave (o beat_track pode ficar alguns ms deslocado)
def analise(sig,nome,thr=0.15):
    e=librosa.onset.onset_strength(y=sig,sr=fs,hop_length=hop); te=librosa.times_like(e,sr=fs,hop_length=hop)
    on=librosa.onset.onset_detect(onset_envelope=e,sr=fs,hop_length=hop,units='time',backtrack=False,delta=thr*e.max()/e.std()/10)
    st=np.interp(on,te,e); st=st/np.percentile(st,95)
    i=np.searchsorted(beats,on)-1; ok=(i>=0)&(i<len(beats)-1); on,st,i=on[ok],st[ok],i[ok]
    ph=(on-beats[i])/(beats[i+1]-beats[i]); sl=np.round(ph*4).astype(int); nxt=sl==4; sl[nxt]=0; i[nxt]+=1
    dev=(ph-np.round(ph*4)/4)*np.median(np.diff(beats))*1000
    nb=len(beats)-1; out=[]
    for par in (0,1):   # tempo 1 e tempo 2 do compasso de 2/4
        for k in range(4):
            sel=(sl==k)&(i%2==par); n_b=nb//2
            pres=min(1,len(np.unique(i[sel]))/n_b); forca=np.median(st[sel]) if sel.any() else 0; md=np.median(dev[sel]) if sel.sum()>5 else np.nan
            out.append((pres,forca,md))
    base=np.nanmedian([o[2] for o in (out[0],out[4])])
    print(f'\n{nome}  (tempo 1 | tempo 2; por 16ª: presença % / força mediana / microtempo ms rel. à 1ª)')
    for par in (0,1):
        print('  tempo',par+1,' '.join(f'[{o[0]*100:3.0f}% {o[1]:.2f} {o[2]-base:+5.1f}]' for o in out[par*4:par*4+4]))
analise(band(dr,None,150),'SURDO (<150 Hz)')
analise(band(dr,200,1500),'MÉDIOS 0,2–1,5 kHz (tantã/rebolo/pandeiro couro)')
analise(band(dr,6000,16000),'AGUDOS >6 kHz (platinelas/ganzá/chimbal)')
# MIDI ADTOF: presença por posição para cada classe
n=[x for ins in pm.PrettyMIDI('/home/claude/traicao/midi/bs_roformer_sw__adtof__drums (6).mid').instruments for x in ins.notes]
print('\nMIDI ADTOF (presença % por 16ª, tempo 1 | tempo 2):')
for p,nm in [(35,'bumbo/surdo 35'),(38,'caixa 38'),(42,'chimbal 42'),(47,'tom 47'),(49,'prato 49')]:
    t=np.array([x.start for x in n if x.pitch==p]); i=np.searchsorted(beats,t)-1; ok=(i>=0)&(i<len(beats)-1); t,i=t[ok],i[ok]
    sl=np.round((t-beats[i])/(beats[i+1]-beats[i])*4).astype(int); nx=sl==4; sl[nx]=0; i[nx]+=1
    nb=(len(beats)-1)//2; row=[len(np.unique(i[(sl==k)&(i%2==par)]))/nb*100 for par in (0,1) for k in range(4)]
    print(f'  {nm:15s}',' '.join(f'{v:3.0f}' for v in row[:4]),'|',' '.join(f'{v:3.0f}' for v in row[4:]))
