# Loudness e voz-banda por seção (Traição) — mesmo critério da automação de Mente (voz menos banda, LU)
import numpy as np, soundfile as sf, glob, os, pyloudnorm as pl
S={}
for f in sorted(glob.glob('/home/claude/traicao/stems/*.flac')):
    x,fs=sf.read(f,always_2d=True,dtype='float32'); S[os.path.basename(f).split(' ')[0]]=x
L=min(len(x) for x in S.values()); S={k:v[:L] for k,v in S.items()}
band=sum(v for k,v in S.items() if k!='vocals'); mix=band+S['vocals']; m=pl.Meter(fs)
SEC=[('verso 1a: voz+teclado',1.7,22.8),('verso 1b: banda leve',22.8,40.1),('pré 1',40.1,46.4),('parada+virada',46.4,52.7),
     ('refrão 1 (2x)',52.7,106.7),('verso 2 (banda cheia)',106.7,123.8),('pré 2 c/ parada',123.8,131.9),('refrão final (2x)',131.9,185.2),('final (1ª frase)',185.2,190)]
lu=lambda x,a,b: m.integrated_loudness(x[int(a*fs):int(b*fs)])
print(f'{"seção":24s} {"início":>6s} {"mix":>6s} {"banda":>6s} {"voz":>6s} {"voz−banda":>9s}  outros(dB)')
for n,a,b in SEC:
    print(f'{n:24s} {a:6.1f} {lu(mix,a,b):6.1f} {lu(band,a,b):6.1f} {lu(S["vocals"],a,b):6.1f} {lu(S["vocals"],a,b)-lu(band,a,b):+9.1f}  {lu(S["other"],a,b):6.1f}')
# faixa dinâmica de curto prazo da mix (só música, até 190 s)
st=[m.integrated_loudness(mix[int(t*fs):int((t+3)*fs)]) for t in np.arange(1.7,187,1.0)]
st=np.array(st); st=st[np.isfinite(st)]
print('LUFS 3 s: p10 %.1f  p50 %.1f  p95 %.1f  -> faixa (p95-p10) %.1f LU; integrado %.1f LUFS'%(np.percentile(st,10),np.median(st),np.percentile(st,95),np.percentile(st,95)-np.percentile(st,10),m.integrated_loudness(mix[:int(190*fs)])))
