# Deslocamento 1ª vez (0:37) -> destinos: nº de tempos pela voz (palavras do WhisperX), ajuste fino pela coincidência de batidas (±40 ms)
import json, numpy as np, soundfile as sf, librosa, scipy.signal as ss
mix,fs=sf.read('/home/claude/md/madeira.wav',always_2d=True); b=np.load('/home/claude/md/beats.npy')
W=[w for w in json.load(open('/home/claude/md/palavras_wx.json'))['words'] if w[0] is not None]
def onsets(lo,hi):
    y=ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),mix.mean(1)).astype(np.float32)
    return librosa.onset.onset_detect(y=y,sr=fs,hop_length=128,units='time')
OL,OH=onsets(40,120),onsets(4000,12000)
def coinc(d,s0=37.0,s1=46.0):
    return sum(sum(np.min(np.abs(O-x))<0.008 for x in O[(O>=s0)&(O<s1)]+d) for O in (OL,OH))
ws=lambda a,c: [w for w in W if a<=w[0]<c]
src=ws(37.5,42.3)
def match(dst):
    d=[]; used=set()
    for w in src:
        k=w[2].lower().strip(',?'); c=[x for x in dst if x[2].lower().strip(',?')==k and id(x) not in used]
        if c: x=min(c,key=lambda x: abs((x[0]-dst[0][0])-(w[0]-src[0][0]))); used.add(id(x)); d.append(x[0]-w[0])
    return np.array(d)
bi=lambda t: int(np.argmin(np.abs(b-t)))
R={}
d1=match(ws(87.9,92.4)); d3=match(ws(136.1,141.0))
print('bloco2 p1: diferenças palavra a palavra (s):',np.round(d1,2)); print('bloco3 p1:',np.round(d3,2))
i_src=bi(37.68)
for nome,dm,extra in [('bloco2 p1',np.median(d1),0),('bloco2 p2',np.median(d1),16),('bloco3 p1',np.median(d3),0),('bloco3 p2',np.median(d3),16)]:
    n=int(round((b[bi(37.68+dm)]-b[i_src])/np.median(np.diff(b))))+extra
    g=b[i_src+n]-b[i_src]
    best=max(np.arange(g-0.04,g+0.04,0.0005),key=coinc)
    R[nome]=dict(delta=float(best),beats=n)
    print(f'{nome:10s} {n} tempos ({n/4:.2f} compassos) | grade {g:.4f} s -> batidas {best:.4f} s ({(best-g)*1000:+.1f} ms), coincidências {coinc(best)} de {len(OL[(OL>=37)&(OL<46)])+len(OH[(OH>=37)&(OH<46)])}')
json.dump(R,open('/home/claude/md/offsets.json','w'))

# --- correção: Δ pela voz (mediana das palavras), 2ª passada = +16 tempos do período real; ajuste fino pelas batidas
P=float(np.median(d1))/103.0     # período real (103 tempos entre a 1ª vez e o bloco 2)
print('\nperíodo real %.5f s = %.2f BPM'%(P,60/P))
R={}
for nome,g in [('bloco2 p1',np.median(d1)),('bloco2 p2',np.median(d1)+16*P),('bloco3 p1',np.median(d3)),('bloco3 p2',np.median(d3)+16*P)]:
    grid=np.arange(g-0.06,g+0.06,0.0005); sc=np.array([coinc(d) for d in grid]); best=grid[np.argmax(sc)]
    R[nome]=dict(delta=float(best))
    print(f'{nome:10s} estimativa {g:8.3f} s -> batidas {best:8.4f} s ({(best-g)*1000:+5.1f} ms), coincidências {sc.max()} (na estimativa {coinc(g)})')
json.dump(R,open('/home/claude/md/offsets.json','w'))
