# Confere a versão nova contra as medidas de Traição
import numpy as np, soundfile as sf, pyloudnorm as pl, json, librosa, scipy.signal as ss
fs=44100; W='/home/claude/vt/w'; F=json.load(open(f'{W}/forma.json')); beats=np.load(f'{W}/analysis.npz')['beats']; S={n:(a,c) for n,a,c,e in F['SEC']}
mix,_=sf.read('/home/claude/vt/Mente_Vit_Traicao_mix_sem_master.wav'); inst,_=sf.read('/home/claude/vt/Mente_Vit_Traicao_instrumental.wav'); voz,_=sf.read('/home/claude/vt/Mente_Vit_Traicao_voz.wav')
m=pl.Meter(fs); B=lambda i: beats[i]; lu=lambda x,a,b: m.integrated_loudness(x[int(a*fs):int(b*fs)])
c0=F['CHORUS'][0]; par=F['PARADA'][0]
SEC=[('abertura (verso 1)',B(S['verso1'][0]),B(S['verso2'][0]),-14.8,4.0),('leve (verso 2)',B(S['verso2'][0]),B(S['pre1'][0]),-13.7,1.0),('pré 1',B(S['pre1'][0]),B(par),-13.9,1.2),
     ('parada+virada',B(par),B(c0),-11.0,1.9),('refrão 1 + pós',B(c0),B(S['solo'][0]),-9.8,-0.6),('pré 2 (cheio)',B(S['pre2'][0]),B(F['PARADA'][1]),-9.9,1.8),('refrão 2+3',B(S['refrao2'][0]),B(S['final'][0]),-9.5,-0.2),('final',B(S['final'][0]),163.7,-14.0,5.7)]
ref=lu(mix,B(c0),B(S['solo'][0])); print(f'{"seção":20s} {"mix rel. refrão":>15s} {"(Traição)":>10s} {"voz−banda":>10s} {"(Traição)":>10s}')
for n,a,b,tr,vb in SEC:
    print(f'{n:20s} {lu(mix,a,b)-ref:+15.1f} {tr+9.8:+10.1f} {lu(voz,a,b)-lu(inst,a,b):+10.1f} {vb:+10.1f}')
perc,_=sf.read('/home/claude/vt/r/percussao.wav'); perc=perc.mean(1)
for nome,(lo,hi),alvo in [('agudos >6 kHz',(6000,16000),[0,-10,0,-6]),('médios 0,2–1,5 kHz',(200,1500),[0,-9,-2,-1])]:
    y=ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),perc); env=np.sqrt(np.convolve(y**2,np.ones(int(0.004*fs))/int(0.004*fs),'same'))
    sel=[i for i in range(len(beats)-1) if B(c0)<=beats[i]<B(S['solo'][0])]; Pk=np.zeros(32)
    for i in sel: Pk+=env[((beats[i]+np.arange(32)/32*(beats[i+1]-beats[i]))*fs).astype(int)]
    Pk=20*np.log10(Pk/Pk.max()); pk=[Pk[k*8:(k+1)*8].max() for k in range(4)]; print(f'{nome}: por 16ª {np.round(pk,1)}  (Traição {alvo})')
dr=sf.read('/home/claude/vt/r/percussao.wav')[0].mean(1)+sf.read('/home/claude/vt/r/surdo.wav')[0].mean(1)
def dens(lo,hi,a,b):
    y=ss.sosfiltfilt(ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'),dr).astype(np.float32)
    o=librosa.onset.onset_detect(y=y,sr=fs,hop_length=128,units='time'); n=((beats>=a)&(beats<b)).sum(); return ((o>=a)&(o<b)).sum()/max(n,1)
for n,a,b in [('leve',B(S['verso2'][0]),B(S['pre1'][0])),('pré',B(S['pre1'][0]),B(par)),('refrão',B(c0),B(S['solo'][0]))]:
    print(f'densidade {n:7s}: graves {dens(None,150,a,b):.1f}/tempo  agudos {dens(6000,16000,a,b):.1f}/tempo')
print('(Traição: leve ~0,8 e 1,5; pré ~0,5 e 1; refrão 6–7 e 3,5)')
st={k:sf.read(f'/home/claude/vt/r/{k}.wav')[0] for k in ['percussao','surdo','baixo','cavaco','violao','epiano','cordas']}
db=lambda x,a,b: 20*np.log10(np.sqrt((x[int(a*fs):int(b*fs)]**2).mean())+1e-9)
for p in F['PARADA']:
    a,b=B(p)+0.05,B(p+2); r0,r1=B(c0)+5,B(c0)+11
    print('parada %.1f s:'%B(p),' '.join(f'{k} {db(v,a,b)-db(v,r0,r1):+.0f}' for k,v in st.items()),' (dB vs refrão; Traição: percussão −40, baixo −4..+3, violão −8, teclado −10..−16, outros +2..+4)')
