# Renderiza a prévia de um MIDI pagodizado (pg_compose.py): pg_render.py NOME
import sys, json, subprocess, numpy as np, soundfile as sf, mido, pyloudnorm as pyln, xml.etree.ElementTree as ET
from scipy import signal
from collections import defaultdict
sys.path.insert(0,'/home/claude/scripts'); from smp import Inst, FS
NOME=sys.argv[1]; P=np.load(f'{NOME}_parts.npy',allow_pickle=True)[0]; info=json.load(open(f'{NOME}_info.json'))
BPM=76.0; per=60/BPM; N=int((info['dur']+1.0)*FS)
SF2='/usr/share/sounds/sf2/FluidR3_GM.sf2'; TMP=f'/tmp/pg_{NOME}'
def fit(x): x=x if x.ndim==2 else np.stack([x,x],1); return np.pad(x,((0,max(0,N-len(x))),(0,0)))[:N]
def midi(keys,chn,prog,path,shift=0):
    PPQ=480; mf=mido.MidiFile(ticks_per_beat=PPQ); tr=mido.MidiTrack(); mf.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM),time=0))
    if chn!=9: tr.append(mido.Message('program_change',program=prog,channel=chn,time=0))
    tk=lambda t:int(round(t/per*PPQ)); ev=[]
    for k in keys:
        for p,t,d,v in P[k]: ev+=[(tk(t),1,mido.Message('note_on',note=p+shift,velocity=v,channel=chn)),(tk(t+d),0,mido.Message('note_off',note=p+shift,velocity=0,channel=chn))]
    ev.sort(key=lambda e:(e[0],e[1])); lt=0
    for t,_,m in ev: m.time=t-lt; tr.append(m); lt=t
    mf.save(path)
def fluid(keys,chn,prog,g=0.5):
    midi(keys,chn,prog,TMP+'.mid'); subprocess.run(['fluidsynth','-ni','-q','-g',str(g),'-r',str(FS),'-F',TMP+'.wav',SF2,TMP+'.mid'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    x,_=sf.read(TMP+'.wav'); return fit(x)
st={}
# percussão (sem surdo), passa-altas 130 Hz para não brigar com o surdo (lição 20)
pc=fluid(['tanta','pandeiro','repique','ganza','pratos'],9,0)
st['perc']=signal.sosfiltfilt(signal.butter(2,130,'highpass',fs=FS,output='sos'),pc,axis=0)
# surdo: camada sintética (A1/C2 com queda de afinação, aberto longo / abafado curto) + corpo do tom GM
out=np.zeros(N); rng=np.random.default_rng(5)
for p,t,d,v in P['surdo']:
    a=(v/127)**1.6; strong=v>80; L=int((0.42 if strong else 0.14)*FS); tt=np.arange(L)/FS
    f=65.4*(1+0.35*np.exp(-tt/0.025)); ph=2*np.pi*np.cumsum(f)/FS
    env=np.exp(-tt/(0.20 if strong else 0.05))*np.clip(tt/0.002,0,1)
    x=np.sin(ph)*env+0.25*np.sin(2*ph)*env*np.exp(-tt/0.05)
    click=signal.sosfilt(signal.butter(2,[400,3000],'bandpass',fs=FS,output='sos'),rng.standard_normal(L)*np.exp(-tt/0.006)*0.15)
    i=int(t*FS); j=min(N,i+L); out[i:j]+=a*(x+click)[:j-i]
g=fluid(['surdo'],9,0).mean(1); g=signal.sosfiltfilt(signal.butter(2,[90,400],'bandpass',fs=FS,output='sos'),g)
st['surdo']=fit(out/np.abs(out).max()*0.8+g/np.abs(g).max()*0.35)
# cavaco com amostras reais (palhetada ida/volta)
B='/home/claude/samples/cavaco_ds/Cavaquinho [Decent Sampler]/Cavaquinho.dsbundle'
r=ET.parse(f'{B}/Cavaquinho.dspreset').getroot(); Z={'DI':[],'Ribbon':[]}
for gr in r.findall('.//group'):
    if gr.attrib.get('name') not in Z: continue
    for s in gr.findall('sample'):
        a=s.attrib; Z[gr.attrib['name']].append({'file':f"{B}/{a['path']}",'root':int(a['rootNote']),'tune':0.0,'layer':1 if int(a['hiVel'])<=63 else 2,'rr':int(a.get('seqPosition',1))})
cav=np.zeros((N,2),np.float32); DI=Inst(Z['DI'],release=0.05,seed=32,vel_exp=1.1); RB=Inst(Z['Ribbon'],release=0.05,seed=33,vel_exp=1.1)
grp=defaultdict(list)
for p,t,d,v in P['cavaco']: grp[round(t,3)].append((p,t,d,v))
rng=np.random.default_rng(31)
for key in sorted(grp):
    ch=sorted(grp[key]); t=min(x[1] for x in ch); d=ch[0][2]; v=max(x[3] for x in ch)
    ph=int(round(t/per*4))%4; down=(ph%2==0) or d>0.3; order=ch if down else ch[::-1]
    if not down and v<60: order=order[:2]
    spread=(0.011 if down else 0.007)*(1.2 if v<60 else 1.0); DI.rel=RB.rel=0.30 if d>0.3 else 0.035
    for k,(p,_,_,vv) in enumerate(order):
        tt=t+k*spread*rng.uniform(0.8,1.2)+rng.normal(0,0.002); vk=vv*(1.0-0.06*k if down else 1.0-0.08*k); dd=max(0.03,d-k*spread)
        z1=DI.pick(p,vk); z2=next((z for z in Z['Ribbon'] if z['root']==z1['root'] and z['layer']==z1['layer'] and z['rr']==z1['rr']),None)
        DI.note(cav,p,tt,dd,vk,cents=0,gain=0.45,zone=z1)
        if z2: RB.note(cav,p,tt,dd,vk,cents=0,gain=0.75,zone=z2)
st['cavaco']=cav.astype(float)
st['violao']=fluid(['violao'],2,24)
# baixo (Growlybass limpo, sfizz)
midi(['bass'],0,33,TMP+'_b.mid')
subprocess.run(['/home/claude/bin/sfizz_render','--sfz','/home/claude/samples/karoryfer.growlybass/growlybass_clean.sfz','--midi',TMP+'_b.mid','--wav',TMP+'_b.wav','-s',str(FS),'-q','3'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
x,_=sf.read(TMP+'_b.wav'); st['baixo']=fit(x)
if P['melodia']: st['melodia']=fluid(['melodia'],0,73)    # flauta no lugar da voz
# níveis por stem (LUFS) e soma
ALVO={'melodia':-16,'cavaco':-21,'violao':-24,'baixo':-20,'surdo':-20,'perc':-23}
if not P['melodia']: ALVO.update(cavaco=-18,violao=-21)   # sem melodia, cavaco e violão viram o centro
meter=pyln.Meter(FS); mix=np.zeros((N,2))
for k,x in st.items():
    L=meter.integrated_loudness(x); g=10**((ALVO[k]-L)/20); mix+=x*g; print(f'{k}: {L:.1f} -> {ALVO[k]} LUFS')
# ambiência curta (sala) para colar: ruído decaindo 0,6 s, 12% molhado, sem graves
ir=np.random.default_rng(9).standard_normal((int(0.6*FS),2))*np.exp(-np.arange(int(0.6*FS))/(0.12*FS))[:,None]
ir=signal.sosfilt(signal.butter(2,[300,7000],'bandpass',fs=FS,output='sos'),ir,axis=0); ir/=np.sqrt((ir**2).sum(0))
wet=np.stack([signal.fftconvolve(mix[:,c],ir[:,c])[:N] for c in range(2)],1)
mix=mix+0.12*wet*np.sqrt((mix**2).mean())/np.sqrt((wet**2).mean()+1e-12)
mix/=np.abs(mix).max()/0.7
sf.write(f'{NOME}_mix.wav',mix,FS,subtype='FLOAT'); print('mix ok')
subprocess.run(['rm','-f',TMP+'.mid',TMP+'.wav',TMP+'_b.mid',TMP+'_b.wav'])
