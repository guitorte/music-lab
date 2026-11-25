# Mix de "Mente Vit com arranjo de Traição": equilíbrio de stems de Traição, voz seca + plate Dragonfly (DawDreamer),
# automação da voz pelo contorno de Traição (−1 LU: preferência do autor por voz integrada). Saída sem master.
import numpy as np, soundfile as sf, pyloudnorm as pyln, json, dawdreamer as daw
from scipy import signal
from scipy.ndimage import maximum_filter1d, uniform_filter1d
fs=44100; R='/home/claude/vt/r'; W='/home/claude/vt/w'; mt=pyln.Meter(fs)
F=json.load(open(f'{W}/forma.json')); beats=np.load(f'{W}/analysis.npz')['beats']; per=float(np.median(np.diff(beats)))
END_T=beats[F['END']]+4*per+3.0; N=int(END_T*fs)
def ld(n):
    z,_=sf.read(f'{R}/{n}.wav',always_2d=True); return (z[:N] if len(z)>=N else np.pad(z,((0,N-len(z)),(0,0)))).astype(np.float64)
voc,_=sf.read(f'{W}/voz_seca_44k.wav',always_2d=True); voc=(voc[:N] if len(voc)>=N else np.pad(voc,((0,N-len(voc)),(0,0)))).astype(np.float64)
def pan(z,p): m=z.mean(1); a=(p+1)*np.pi/4; return np.stack([m*np.cos(a),m*np.sin(a)],1)*np.sqrt(2)
def ms_wide(z,side_db): m=(z[:,0]+z[:,1])/2; s=(z[:,0]-z[:,1])/2*10**(side_db/20); return np.stack([m+s,m-s],1)
def plim(z,plr):
    l=mt.integrated_loudness(z); th=10**((l+plr)/20); pk=maximum_filter1d(np.abs(z).max(1),size=int(0.004*fs))
    g=np.minimum(1,th/np.maximum(pk,1e-9)); r=np.exp(-1/(0.06*fs)); out=np.empty_like(g); e=1.0
    for i in range(len(g)):
        v=g[i]; e=v if v<e else r*e+(1-r)*v; out[i]=e
    return z*out[:,None]
def dragonfly(z,plugin,params):
    eng=daw.RenderEngine(fs,512); pb=eng.make_playback_processor('src',z.T.astype(np.float32))
    p=eng.make_plugin_processor('fx',f'/usr/lib/vst3/{plugin}.vst3')
    for i,v in params.items(): p.set_parameter(i,v)
    eng.load_graph([(pb,[]),(p,['src'])]); eng.render(len(z)/fs); y=eng.get_audio().T
    return np.pad(y,((0,max(0,len(z)-len(y))),(0,0)))[:len(z)].astype(np.float64)
S0={n:(a,c) for n,a,c,e in F['SEC']}
hp=lambda z,f: signal.sosfiltfilt(signal.butter(2,f,'highpass',fs=fs,output='sos'),z,axis=0)
P={'surdo':ld('surdo'),'percussao':ld('percussao'),'pratos':pan(ld('pratos'),0.15),'baixo':pan(ld('baixo'),0),'cavaco':pan(ld('cavaco'),0.3),
   'violao':pan(ld('violao'),-0.35),'epiano':ms_wide(ld('epiano'),9.0),'cordas':ld('cordas')}
P['percussao']=hp(P['percussao'],130); P['baixo']=hp(P['baixo'],35); P['cavaco']=hp(P['cavaco'],250); P['epiano']=hp(P['epiano'],120); P['cordas']=hp(P['cordas'],90)
for k,c in [('percussao',11.0),('cavaco',10.5),('epiano',12.0),('surdo',17.0),('pratos',14.0)]: P[k]=plim(P[k],c)
# equilíbrio de Traição (LU contra a soma; mix nominal −14): bateria −5,1 / violões −8,3 / teclado −11,6 / baixo −13,7 / outros −18,8
TGT={'surdo':-20.5,'percussao':-22.5,'pratos':-29.0,'baixo':-27.7,'cavaco':-23.6,'violao':-26.5,'epiano':-25.6,'cordas':-32.8}
for k,z in P.items():
    l=mt.integrated_loudness(z); P[k]=z*10**((TGT[k]-l)/20); print(f'{k:10s} {l:6.1f} -> {TGT[k]}')
room={2:0.0,3:0.4,4:0.2,5:1.0,6:0.5,7:0.7,8:0.1,9:0.111,10:0.7,11:0.2,12:0.2,13:0.467,14:0.4,15:0.3,16:0.0,18:1.0}
wet=dragonfly(P['cavaco']*0.5+P['violao']+P['epiano']+P['cordas']+P['percussao']*0.25,'DragonflyRoomReverb',room)*10**(-13/20)
band=sum(P.values())+wet
# dinâmica de Traição: banda leve/pré ~4 LU abaixo do refrão (tocar mais baixo), pré 2 sem passar do refrão
bg=np.zeros(N)
for a,b,g_ in [(beats[S0['verso2'][0]],beats[F['PARADA'][0]],-1.6),(beats[S0['pre2'][0]],beats[F['PARADA'][1]],-0.7)]:
    bg[int((a-0.3)*fs):int((b-0.05)*fs)]=g_
bg=uniform_filter1d(bg,size=int(0.3*fs)); band=band*10**(bg/20)[:,None]
# voz: plate Dragonfly (100% molhado, mixado por baixo)
plate={2:0.0,3:1.0,4:0.5,5:0.7,6:0.3,7:0.1515,8:0.75,9:0.533,10:0.4}
vwet=dragonfly(hp(voc,150),'DragonflyPlateReverb',plate)
lb=mt.integrated_loudness(band); lv=mt.integrated_loudness(voc); voc*=10**(((lb-1.0)-lv)/20); vwet*=10**(((lb-1.0)-lv)/20)*10**(-11/20)
# automação: contorno de Traição (abertura +4, leve +1, pré +1,2, refrão −0,6, verso/pré cheio +1, final +5,7) − 1 LU
B=lambda i: beats[i]
S={n:(a,c) for n,a,c,e in F['SEC']}
SECV=[(0,B(S['verso2'][0]),3.0),(B(S['verso2'][0]),B(S['pre1'][0]),0.0),(B(S['pre1'][0]),B(S['refrao1'][0]),0.4),(B(S['refrao1'][0]),B(S['solo'][0]),-1.6),
      (B(S['pre2'][0]),B(S['refrao2'][0]),0.0),(B(S['refrao2'][0]),B(S['final'][0]),-1.4),(B(S['final'][0]),END_T,4.0)]
gdb=np.zeros(N)
for a,b,tg in SECV:
    a=max(0,a-0.35); b=b-0.35; i0,i1=int(a*fs),int(b*fs); Lb=mt.integrated_loudness(band[i0:i1]); Lv=mt.integrated_loudness(voc[i0:i1])
    gdb[i0:i1]=np.clip((Lb+tg)-Lv,-4,6); print(f'  voz {a:6.1f}-{b:6.1f}: banda {Lb:6.1f} voz {Lv:6.1f} -> {gdb[i0]:+.1f} dB (alvo {tg:+.1f})')
i0,i1=int((B(S['solo'][0])-0.35)*fs),int((B(S['pre2'][0])-0.35)*fs); gdb[i0:i1]=gdb[i0-1]
gdb=uniform_filter1d(gdb,size=int(0.25*fs)); g=10**(gdb/20)[:,None]; voc*=g; vwet*=g
mix=band+voc+vwet
mix=signal.sosfiltfilt(signal.butter(4,16500,'lowpass',fs=fs,output='sos'),mix,axis=0)
f=int(2.5*fs); fade=np.ones(N); fade[-f:]=np.linspace(1,0,f)**2; mix*=fade[:,None]; band*=fade[:,None]
G=10**((-16-mt.integrated_loudness(mix))/20); mix*=G
inst=(band)*G; voz=(voc+vwet)*G*fade[:,None]
for nm,z in [('Mente_Vit_Traicao_mix_sem_master',mix),('Mente_Vit_Traicao_instrumental',inst),('Mente_Vit_Traicao_voz',voz)]:
    sf.write(f'/home/claude/vt/{nm}.wav',z.astype(np.float32),fs,subtype='PCM_24'); print(nm, 'LUFS %.1f pico %.1f dBFS'%(mt.integrated_loudness(z),20*np.log10(np.abs(z).max())))
np.save(f'{W}/gdb.npy',gdb.astype(np.float32))
