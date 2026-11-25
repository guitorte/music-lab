import numpy as np, soundfile as sf, json, re, os, shutil, sys
from scipy import signal
sys.path.insert(0,'/home/claude/scripts'); from smp import *
P=np.load('/home/claude/vt/w/parts.npy',allow_pickle=True)[0]; Z=json.load(open('/home/claude/samples/zones.json'))
OUT='/home/claude/vt/r'; os.makedirs(OUT,exist_ok=True); N=int(194*FS)
for n in ['surdo','cavaco','violao','pad']: shutil.copy(f'/home/claude/vt/w/{n}.wav',f'{OUT}/{n}.wav')
C='/tmp/vcsl_t'; rng=np.random.default_rng(7)
def buf(): return np.zeros((N,2),np.float32)
def save(name,y):
    pk=np.abs(y).max(); y=y/pk*0.9 if pk>0.9 else y; sf.write(f'{OUT}/{name}.wav',y,FS,subtype='PCM_24'); print(f'{name}: pico {20*np.log10(np.abs(y).max()+1e-9):.1f} dBFS')
vl=lambda b:(int(re.search(r'_v(\d)',b).group(1)) if re.search(r'_v(\d)',b) else 1)
# ---------------- percussão
perc=buf()
tum_open=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Conga/Tumba_HitN*'),vl),oneshot=True,maxlen=0.9,seed=1)
tum_mute=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Conga/Tumba_HitFM*'),vl),oneshot=True,maxlen=0.5,seed=2)
for p,t,d,v in P['tanta']:
    (tum_open if v>75 else tum_mute).note(perc,58,t,d,v,cents=8,gain=1.0)   # raiz 60 -> -2 semitons (mais grave)
tamb=Inst(zones_from(files(f'{C}/Idiophones/Struck Idiophones/Tambourine 1/Tamb1_Hit*')+files(f'{C}/Idiophones/Struck Idiophones/Tambourine 2/Tamb2_Hit*'),vl),oneshot=True,maxlen=0.6,seed=3)
skin=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Frame Drum/HDrumL_Hit_*'),vl),oneshot=True,maxlen=0.7,seed=4)
skinm=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Frame Drum/HDrumS_HitMuted*'),vl),oneshot=True,maxlen=0.3,seed=5)
for p,t,d,v in P['pandeiro']:
    tamb.note(perc,60,t,d,v,cents=15,gain=0.55)
    if v>90: skin.note(perc,60,t,d,v,cents=10,gain=0.8)
    elif v>55: skinm.note(perc,60,t,d,v,cents=10,gain=0.45)
bh_m=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Bongos/BongoH_HitMuted*'),vl),oneshot=True,maxlen=0.25,seed=6)
tmb=buf()
for p,t,d,v in P['tamborim']: bh_m.note(tmb,64,t,d,v,cents=8)
tmb=signal.sosfilt(signal.butter(2,400,'highpass',fs=FS,output='sos'),tmb,axis=0).astype(np.float32); perc+=tmb*0.9
bl=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Bongos/BongoL_Hit1*'),vl),oneshot=True,maxlen=0.5,seed=7)
bH=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Bongos/BongoH_Hit1*'),vl),oneshot=True,maxlen=0.5,seed=8)
for p,t,d,v in P['repique']: (bl if p==65 else bH).note(perc,60,t,d,v,cents=10,gain=0.9)
down=Inst(zones_from(files(f'{C}/Idiophones/Struck Idiophones/Shaker, Small/Mid_ShakerHighFaster_Down*')+files(f'{C}/Idiophones/Struck Idiophones/Shaker, Small/Mid_ShakerLowFaster_Down*')),oneshot=True,maxlen=0.3,seed=9)
up=Inst(zones_from(files(f'{C}/Idiophones/Struck Idiophones/Shaker, Small/Mid_ShakerHighFaster_Up*')+files(f'{C}/Idiophones/Struck Idiophones/Shaker, Small/Mid_ShakerLowFaster_Up*')),oneshot=True,maxlen=0.3,seed=10)
per=np.median(np.diff(np.load('/home/claude/vt/w/analysis.npz')['beats']))
b=np.load('/home/claude/vt/w/analysis.npz')['beats']
for p,t,d,v in P['ganza']:
    i=np.searchsorted(b,t+0.02)-1; ph=int(round((t-b[max(i,0)])/per*4))%2
    (down if ph==0 else up).note(perc,60,t,d,v,cents=25,gain=0.7*(1.0 if ph==0 else 0.8))
rim=Inst(zones_from(files(f'{C}/Membranophones/Struck Membranophones/Snare Drum, Modern 1/Snare2_stick*'),vl),oneshot=True,maxlen=0.4,seed=11)
for p,t,d,v in P['aro']: rim.note(perc,60,t,d,v,cents=10,gain=0.8)
save('percussao',perc)
# ---------------- pratos e palmas
pr=buf(); cy=lambda f: [{'file':f'{C}/Idiophones/Struck Idiophones/Suspended Cymbal 1/{f}','root':60,'tune':0,'layer':1,'rr':1}]
crash_f=Inst(cy('susCymb1_hit_f1.wav'),oneshot=True,maxlen=4.0,seed=12); crash_ff=Inst(cy('susCymb1_hit_fff1.wav'),oneshot=True,maxlen=4.0,seed=13)
splash=Inst(cy('susCymb1_hit_stick_mp1.wav'),oneshot=True,maxlen=1.2,seed=14)
for p,t,d,v in P['pratos']:
    if p==49: (crash_ff if v>105 else crash_f).note(pr,60,t,d,v,cents=20,gain=0.9)
    else: splash.note(pr,60,t,d,v,cents=20,gain=0.7)
claps=Inst(zones_from(files(f'{C}/Idiophones/Struck Idiophones/Claps/Clap_rr*')),oneshot=True,maxlen=0.4,seed=15)
for p,t,d,v in P['palmas']: claps.note(pr,60,t,d,v,cents=20,gain=0.8,dt=rng.normal(0,0.006))
save('pratos',pr)
# ---------------- baixo
bs=buf(); BS=Inst(Z['bass_sus'],release=0.06,seed=16,vel_exp=0.9); BT=Inst(Z['bass_stac'],release=0.05,seed=17,oneshot=False,vel_exp=0.9)
for p,t,d,v in P['bass']: (BT if d<0.17 else BS).note(bs,p,t,d,v,cents=3)
save('baixo',bs)
# ---------------- rhodes
ep=buf(); RH=Inst(Z['rhodes'],release=0.35,seed=18,vel_exp=1.0,max_shift=3)
for p,t,d,v in P['epiano']: RH.note(ep,p,t,d,v,cents=3)
save('epiano',ep)
# ---------------- cordas (violinos em cima, violas no meio, cellos embaixo)
st=buf(); VN=Inst(Z['vln'],release=0.45,attack=0.06,seed=19,vel_exp=0.8); VA=Inst(Z['vla'],release=0.45,attack=0.06,seed=20,vel_exp=0.8); VC=Inst(Z['vlc'],release=0.45,attack=0.06,seed=21,vel_exp=0.8)
from collections import defaultdict
def chords(lst):
    g=defaultdict(list)
    for p,t,d,v in lst: g[round(t,2)].append((p,t,d,v))
    return g.values()
for ch in chords(P['strings']):
    ch=sorted(ch); n=len(ch)
    for k,(p,t,d,v) in enumerate(ch):
        inst=VN if k==n-1 else (VA if k>0 or p>64 else VC)
        inst.note(st,p,t,d,v,cents=4)
save('cordas',st)
# ---------------- metais (trompete em cima, sax tenor no meio, trombone embaixo)
br=buf(); TS=Inst(Z['tpt_stac'],release=0.08,seed=22); TU=Inst(Z['tpt_sus'],release=0.15,seed=23)
XS=Inst(Z['sax_stac'],release=0.08,seed=24); XN=Inst(Z['sax_nv'],release=0.12,seed=25)
BS_=Inst(Z['tbn_stac'],release=0.08,seed=26); BU=Inst(Z['tbn_sus'],release=0.15,seed=27)
for ch in chords(P['sopros']):
    ch=sorted(ch); n=len(ch)
    for k,(p,t,d,v) in enumerate(ch):
        short=d<=0.25
        if k==n-1 or n==1: (TS if short else TU).note(br,p,t,d,v,cents=6,dt=rng.normal(0,0.004))
        elif k==0 and n>=3: (BS_ if short else BU).note(br,p-12 if p-12>=40 else p,t,d,v,cents=6,dt=rng.normal(0,0.005))
        else: (XS if short else XN).note(br,p-12 if p>76 else p,t,d,v,cents=6,dt=rng.normal(0,0.005))
save('sopros',br)
# ---------------- sax solo
sx=buf(); SV=Inst(Z['sax_vib'],release=0.15,attack=0.01,seed=28,max_shift=2); SN=Inst(Z['sax_nv'],release=0.12,attack=0.008,seed=29,max_shift=2); SS=Inst(Z['sax_stac'],release=0.08,seed=30)
for p,t,d,v in P['sax']:
    q=p-12 if p>74 else p
    (SS if d<0.22 else SN if d<0.6 else SV).note(sx,q,t,d*1.05,v,cents=4)
save('sax',sx)
