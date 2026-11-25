# Timbre por stem: perfil de bandas, brilho, transiente, largura estéreo; Traição (real) x Mente Vit (Suno)
import numpy as np, soundfile as sf, glob, os, scipy.signal as ss, pretty_midi as pm
BANDS=[(20,60,'sub'),(60,250,'grave'),(250,1000,'médio-grave'),(1000,4000,'médio'),(4000,10000,'presença'),(10000,20000,'ar')]
def stems(d):
    S={}
    for f in sorted(glob.glob(d+'/*')):
        if f.endswith(('.flac','.wav')):
            k=next((n for n in ['vocals','drums','bass','guitar','piano','other'] if n in os.path.basename(f).lower()),None)
            if k: x,fs=sf.read(f,always_2d=True,dtype='float32'); S[k]=x
    return S,fs
def perfil(x,fs):
    m=x.mean(1); n=4096; f,P=ss.welch(m,fs,nperseg=n)
    # só quadros ativos (até 30 dB abaixo do p95) para não medir silêncio
    w=int(0.1*fs); k=len(m)//w; e=20*np.log10(np.sqrt((m[:k*w].reshape(k,w)**2).mean(1))+1e-9); act=e>np.percentile(e,95)-30
    tot=P.sum(); prof=[10*np.log10(P[(f>=a)&(f<b)].sum()/tot+1e-12) for a,b,_ in BANDS]
    cent=(f*P).sum()/P.sum()
    seg=m[:k*w].reshape(k,w)[act]; crest=np.median(20*np.log10(np.abs(seg).max(1)/(np.sqrt((seg**2).mean(1))+1e-9)))
    M=(x[:,0]+x[:,1])/2; Sd=(x[:,0]-x[:,1])/2; width=10*np.log10((Sd**2).sum()/((M**2).sum()+1e-12)+1e-12)
    return prof,cent,crest,width,act.mean()*100
for nome,d in [('TRAIÇÃO (gravação real)','/home/claude/traicao/stems'),('MENTE Vit (Suno)','/home/claude/vit/stems_zip')]:
    S,fs=stems(d); print(f'\n{nome}'); print(f'  {"stem":7s} '+' '.join(f'{b[2]:>11s}' for b in BANDS)+'   brilho  crista  largura  ativo')
    for k in ['vocals','drums','bass','guitar','piano','other']:
        if k not in S: continue
        p,c,cr,wd,ac=perfil(S[k],fs)
        print(f'  {k:7s} '+' '.join(f'{v:11.1f}' for v in p)+f'  {c:6.0f} Hz {cr:5.1f} dB {wd:6.1f} dB {ac:5.0f}%')
# quem está em cada stem (Traição): extensão das notas dos MIDIs do Basic Pitch
print('\nTRAIÇÃO: extensão das notas (Basic Pitch), p5–p50–p95 em nome de nota')
for s in ['bass','guitar','piano','other','vocals']:
    f=glob.glob(f'/home/claude/traicao/midi/bs_roformer_sw__basic_pitch__{s}*.mid')[0]
    p=np.array([x.pitch for i in pm.PrettyMIDI(f).instruments for x in i.notes])
    h=np.histogram(p,bins=np.arange(20,110,6))[0]
    print(f'  {s:7s} {pm.note_number_to_name(int(np.percentile(p,5)))}–{pm.note_number_to_name(int(np.median(p)))}–{pm.note_number_to_name(int(np.percentile(p,95)))}   histograma por 6 semitons a partir de G#0: {h.tolist()}')
