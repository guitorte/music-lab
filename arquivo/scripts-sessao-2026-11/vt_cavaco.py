# Cavaco com amostras reais (Decent Samples, DI + microfone de fita), palhetada simulada: ida grave->agudo, volta agudo->grave
import numpy as np, soundfile as sf, xml.etree.ElementTree as ET, sys
sys.path.insert(0,'/home/claude/scripts'); from smp import *
B='/home/claude/samples/cavaco_ds/Cavaquinho [Decent Sampler]/Cavaquinho.dsbundle'
r=ET.parse(f'{B}/Cavaquinho.dspreset').getroot(); Z={'DI':[],'Ribbon':[]}
for g in r.findall('.//group'):
    if g.attrib.get('name') not in Z: continue
    for s in g.findall('sample'):
        a=s.attrib; Z[g.attrib['name']].append({'file':f"{B}/{a['path']}",'root':int(a['rootNote']),'tune':0.0,'layer':1 if int(a['hiVel'])<=63 else 2,'rr':int(a.get('seqPosition',1))})
for k,z in Z.items(): print(k,len(z),'amostras, notas',min(x['root'] for x in z),'-',max(x['root'] for x in z),'camadas',sorted(set(x['layer'] for x in z)))
P=np.load('/home/claude/vt/w/parts.npy',allow_pickle=True)[0]; beats=np.load('/home/claude/vt/w/analysis.npz')['beats']; per=np.median(np.diff(beats))
N=int(194*FS); out=np.zeros((N,2),np.float32); rng=np.random.default_rng(31)
DI=Inst(Z['DI'],release=0.05,seed=32,vel_exp=1.1); RB=Inst(Z['Ribbon'],release=0.05,seed=33,vel_exp=1.1)
from collections import defaultdict
g=defaultdict(list)
for p,t,d,v in P['cavaco']: g[round(t,3)].append((p,t,d,v))
n_down=n_up=0
for key in sorted(g):
    ch=sorted(g[key]); t=min(x[1] for x in ch); d=ch[0][2]; v=max(x[3] for x in ch)
    i=np.searchsorted(beats,t+0.02)-1; ph=int(round((t-beats[max(i,0)])/per*4))%4
    down=(ph%2==0) or d>0.3
    order=ch if down else ch[::-1]
    if not down and v<60: order=order[:2]                     # volta fraca: só as cordas agudas
    spread=(0.011 if down else 0.007)*(1.2 if v<60 else 1.0)
    rel=0.30 if d>0.3 else 0.035                              # acorde longo soa; corte abafa
    DI.rel=RB.rel=rel
    for k,(p,_,_,vv) in enumerate(order):
        tt=t+k*spread*rng.uniform(0.8,1.2)+rng.normal(0,0.002); vk=vv*(1.0-0.06*k if down else 1.0-0.08*k)
        dd=max(0.03,d-k*spread)
        z1=DI.pick(p,vk); z2=next((z for z in Z['Ribbon'] if z['root']==z1['root'] and z['layer']==z1['layer'] and z['rr']==z1['rr']),None)
        c=rng.normal(0,4)/100
        DI.note(out,p,tt,dd,vk,cents=0,gain=0.45,zone=z1)
        if z2: RB.note(out,p,tt,dd,vk,cents=0,gain=0.75,zone=z2)
    n_down+=down; n_up+=not down
print('palhetadas: ida',n_down,'volta',n_up)
sf.write('/home/claude/vt/r/cavaco.wav',out/np.abs(out).max()*0.9,FS,subtype='PCM_24'); print('pico %.1f dBFS'%(20*np.log10(np.abs(out).max())))
