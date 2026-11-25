# Linha do tempo a cada 2 compassos de 2/4 (4 tempos): loudness da mix e nível de cada stem
import numpy as np, soundfile as sf, glob, os, pyloudnorm as pl
S={}
for f in sorted(glob.glob('/home/claude/traicao/stems/*.flac')):
    x,fs=sf.read(f,always_2d=True,dtype='float32'); S[os.path.basename(f).split(' ')[0]]=x
L=min(len(x) for x in S.values()); S={k:v[:L] for k,v in S.items()}; mix=sum(S.values())
beats=np.load('/home/claude/traicao/beats.npy'); m=pl.Meter(fs)
def db(x): return 20*np.log10(np.sqrt((x**2).mean())+1e-9)
ref={k:np.percentile([db(v[int(beats[i]*fs):int(beats[i+4]*fs)]) for i in range(0,len(beats)-4,4)],95) for k,v in S.items()}
rows=[]
print(' início   mix LUFS |  voz  bat baixo guit pian outr   (dB abaixo do próprio p95 do stem; "." = mudo, < -30)')
for i in range(0,len(beats)-4,4):
    a,b=int(beats[i]*fs),int(beats[i+4]*fs); seg=mix[a:b]
    lu=m.integrated_loudness(seg) if b-a>fs*0.5 else np.nan
    lv={k:db(S[k][a:b])-ref[k] for k in ['vocals','drums','bass','guitar','piano','other']}
    rows.append([beats[i],lu]+list(lv.values()))
    print(f'{beats[i]:6.1f}  {lu:8.1f} | '+' '.join(f'{v:4.0f}' if v>-30 else '   .' for v in lv.values()))
np.save('/home/claude/traicao/linha.npy',np.array(rows))
