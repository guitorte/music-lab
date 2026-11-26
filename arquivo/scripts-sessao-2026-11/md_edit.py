# Madeira: 4 transplantes da 1ª vez (0:37) para os blocos 2 e 3. out = mix + w·(voz_fonte(t−Δ)·g − voz(t)); fora das janelas, idêntico.
import json, numpy as np, soundfile as sf, pyloudnorm as pl
R='/home/claude/md'; mix,fs=sf.read(f'{R}/madeira.wav',always_2d=True,dtype='float64'); voz,_=sf.read(f'{R}/voz.wav',always_2d=True,dtype='float64')
N=min(len(mix),len(voz)); mix=mix[:N]; voz=voz[:N]; O=json.load(open(f'{R}/offsets.json')); m=pl.Meter(fs)
h=int(0.005*fs); k=N//h; ENV=20*np.log10(np.sqrt((voz.mean(1)[:k*h].reshape(k,h)**2).mean(1))+1e-9)
env=lambda t: ENV[min(k-1,max(0,int(t*fs)//h))]
def cut(src_lo,src_hi,d):
    """melhor ponto (relógio da fonte) onde fonte e destino estão quietos ao mesmo tempo"""
    ts=np.arange(src_lo,src_hi,0.005); sc=[max(env(t),env(t+d)) for t in ts]; i=int(np.argmin(sc)); return float(ts[i]),float(sc[i])
EDITS=[('bloco2 p1','linha',(39.30,39.95),(41.95,42.40)),('bloco3 p1','linha',(39.30,39.95),(41.95,42.40)),
       ('bloco2 p2','frase',(37.20,37.70),(45.07,45.07)),('bloco3 p2','frase',(37.20,37.70),(45.07,45.07))]
RESUME={'bloco2 p2':45.26,'bloco3 p2':45.26}   # fonte termina após o "hein" (45,07); voz em silêncio até o destino voltar na pausa dele
F=int(0.040*fs); out=mix.copy(); vnew=voz.copy(); log=[]; WIN=[]
for nome,tipo,(a0,a1),(b0,b1) in EDITS:
    d=O[nome]['delta']; ta,ea=cut(a0,a1,d); tb,eb=(b0,env(b0)) if b0==b1 else cut(b0,b1,d)
    te=RESUME.get(nome,tb)                                   # fim da janela (volta ao destino)
    i0,i1=int((ta+d)*fs),int((te+d)*fs); s0=int(ta*fs); nsrc=int((tb-ta)*fs)
    src=np.zeros((i1-i0,2)); src[:nsrc]=voz[s0:s0+nsrc]; dst=voz[i0:i1]
    r=0.5-0.5*np.cos(np.linspace(0,np.pi,F))
    fsrc=np.ones(i1-i0); fsrc[nsrc-int(0.025*fs):nsrc]=np.cos(np.linspace(0,np.pi/2,int(0.025*fs)))**2; fsrc[nsrc:]=0
    g=10**((m.integrated_loudness(dst[:nsrc])-m.integrated_loudness(src[:nsrc]))/20)   # casa loudness da voz no trecho
    w=np.ones(i1-i0); w[:F]=r; w[-F:]=r[::-1]
    if te!=tb: eb=max(env(te-0.02+d),env(te+d))
    delta=w[:,None]*(src*fsrc[:,None]*g-dst); out[i0:i1]+=delta; vnew[i0:i1]+=delta
    WIN.append((i0,i1)); log.append(dict(nome=nome,tipo=tipo,dest=(round(ta+d,3),round(te+d,3)),fonte=(round(ta,3),round(tb,3)),ganho_dB=round(20*np.log10(g),2),corte_dB=(round(ea,1),round(eb,1))))
    print(f'{nome}: destino {ta+d:7.3f}–{te+d:7.3f} s  <- fonte {ta:6.3f}–{tb:6.3f} s  | ganho {20*np.log10(g):+.2f} dB | nível nos cortes {ea:.0f} / {eb:.0f} dBFS')
# limitador só dentro das janelas: a master original foi limitada com a voz antiga; a nova soma passa do teto
from scipy.ndimage import maximum_filter1d
CEIL=min(np.abs(mix).max(),10**(-0.1/20)); LA=int(0.003*fs); REL=np.exp(-1/(0.06*fs))
for i0,i1 in WIN:
    seg=out[i0:i1]; pk=maximum_filter1d(np.abs(seg).max(1),size=2*LA+1); g=np.minimum(1,CEIL/np.maximum(pk,1e-12))
    sm=np.empty_like(g); e=1.0
    for j in range(len(g)): v=g[j]; e=v if v<e else REL*e+(1-REL)*v; sm[j]=e
    sm[:F]=np.maximum(sm[:F],1-(1-sm[:F])*0)  # mantém
    out[i0:i1]=seg*sm[:,None]; gr=-20*np.log10(sm)
    print(f'  limitador {i0/fs:7.2f}–{i1/fs:7.2f}: redução p99 {np.percentile(gr,99):.1f} dB, máx {gr.max():.1f} dB, tempo em redução >1 dB {np.mean(gr>1)*100:.1f}%%')
# prova: fora das janelas, amostras idênticas
mask=np.ones(N,bool)
for i0,i1 in WIN: mask[i0:i1]=False
print('fora das janelas: idêntico =',bool(np.array_equal(out[mask],mix[mask])),'| amostras alteradas: %.2f s'%((~mask).sum()/fs))
pk=np.abs(out).max(); print('pico %.2f dBFS'%(20*np.log10(pk)))
sf.write(f'{R}/Madeira_editada.wav',out,fs,subtype='FLOAT'); sf.write(f'{R}/voz_editada.wav',vnew,fs,subtype='FLOAT')
json.dump(log,open(f'{R}/edits.json','w'),indent=1)
