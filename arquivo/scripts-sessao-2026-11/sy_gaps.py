# Mapa de buracos da Vit: paradas (bateria+baixo mudos), cama harmônica (piano+other+guitar) e pausas da voz, por compasso de 2/4
import numpy as np, soundfile as sf, scipy.signal as ss, json
D='/home/claude/vit/stems_zip/'; A=np.load('/home/claude/vit/w/analysis.npz'); B=A['beats']
St={k:sf.read(D+f,always_2d=True)[0].mean(1) for k,f in [('bass','vit live mast - bass.flac'),('drums','vit live mast - drums.wav'),('guitar','vit live mast - guitar.flac'),('other','vit live mast - other.flac'),('piano','vit live mast - piano.flac'),('voz','vit live mast - vocals.flac')]}
fs=44100; L=min(len(v) for v in St.values()); St={k:v[:L] for k,v in St.items()}
bp=lambda x,lo,hi: ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),x)
carpet=bp(St['piano']+St['other']+St['guitar'],150,4000)
db=lambda x,a,b: 20*np.log10(np.sqrt((x[int(a*fs):int(b*fs)]**2).mean())+1e-9)
SEC=[('intro',0),('verso1',8.9),('verso2',20.0),('pre1',31.5),('refrao1',44.1),('pos',69.2),('solo',81.9),('pre2',87.6),('refrao2',100.6),('refrao3',124.7),('final',150.1),('fim',162.3),('_',999)]
sec=lambda t: [n for (n,a),(_,b) in zip(SEC,SEC[1:]) if a<=t<b][0]
rows=[]
for i in range(0,len(B)-1,1):
    a,b=B[i],B[i+1]
    rows.append(dict(t=float(a),sec=sec(a),drums=db(St['drums'],a,b),bass=db(St['bass'],a,b),carpet=db(carpet,a,b),voz=db(St['voz'],a,b),
                     piano=db(St['piano'],a,b),other=db(St['other'],a,b),guitar=db(St['guitar'],a,b)))
json.dump(rows,open('/home/claude/sy/beats.json','w'))
ref=np.median([r['carpet'] for r in rows if r['sec'].startswith('refrao')])
print(f'cama harmônica de referência (mediana dos refrões): {ref:.1f} dB\n')
print(f'{"seção":8s} {"tempos":>6s} {"parada%":>8s} {"cama rel":>9s} {"cama p10":>9s} {"piano":>6s} {"other":>6s} {"guit":>6s} {"voz pausa%":>10s}')
for n,_ in SEC[:-1]:
    R=[r for r in rows if r['sec']==n]
    if not R: continue
    stop=np.mean([(r['drums']<-55 and r['bass']<-55) for r in R])*100
    c=np.array([r['carpet'] for r in R])-ref; vp=np.mean([r['voz']<-45 for r in R])*100
    med=lambda k: np.median([r[k] for r in R])
    print(f'{n:8s} {len(R):6d} {stop:8.0f} {np.median(c):+9.1f} {np.percentile(c,10):+9.1f} {med("piano"):6.0f} {med("other"):6.0f} {med("guitar"):6.0f} {vp:10.0f}')
