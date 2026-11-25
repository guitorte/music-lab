# Camada sintetizada para a Vit original: pad onde falta cama harmônica + plucks nas pausas da voz; mudo nas paradas.
import numpy as np, soundfile as sf, scipy.signal as ss, pretty_midi as pm, pyloudnorm as pl, json
from scipy.ndimage import uniform_filter1d, binary_dilation
fs=44100; R='/home/claude/sy'; rng=np.random.default_rng(89)
A=np.load('/home/claude/vit/w/analysis.npz'); B=A['beats']; C=np.load('/home/claude/vit/w/chords.npz'); ch=C['ch']; seg=C['seg']
src,_=sf.read('/home/claude/mt/edit.wav',always_2d=True); N=len(src); per=float(np.median(np.diff(B)))
D='/home/claude/vit/stems_zip/'
def T(b,k=0):
    b=b+k//4; s=k%4
    if b>=len(B)-1: return B[-1]+(b-len(B)+1)*per+s*per/4
    return B[b]+s*(B[b+1]-B[b])/4
names='C C# D D# E F F# G G# A A# B'.split()
def parse(l):
    r=names.index(l[:2]) if l[:2] in names else names.index(l[0]); q=l[len(names[r]):]
    return r,{'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10],'maj7':[0,4,7,11],'m7b5':[0,3,6,10]}[q]
def voicing(l,lo,hi,prev=None,n=4):
    r,iv=parse(l); pcs=[(r+i)%12 for i in iv]; opts=[]
    for bottom in range(lo,lo+12):
        if bottom%12 not in pcs: continue
        v=[bottom]; x=bottom
        while len(v)<n:
            x+=1
            if x%12 in pcs and x not in v: v.append(x)
        if v[-1]<=hi: opts.append(v)
    if prev is None: return opts[len(opts)//2]
    return min(opts,key=lambda v: sum(min(abs(a-b) for b in prev) for a in v))
SEC=[('intro',0),('verso1',8.9),('verso2',20.0),('pre1',31.5),('refrao1',44.1),('pos',69.2),('solo',81.9),('pre2',87.6),('refrao2',100.6),('refrao3',124.7),('final',150.1),('fim',162.3),('_',999)]
def sec(t): return [n for (n,a),(_,b) in zip(SEC,SEC[1:]) if a<=t<b][0]
# ---------- máscara de paradas: bateria e baixo mudos juntos (10 ms), dilatada 30 ms
def env10(f):
    x=sf.read(D+f,always_2d=True)[0].mean(1); h=441; k=len(x)//h; return 20*np.log10(np.sqrt((x[:k*h].reshape(k,h)**2).mean(1))+1e-9)
from scipy.ndimage import label
dr,ba,gu=env10('vit live mast - drums.wav'),env10('vit live mast - bass.flac'),env10('vit live mast - guitar.flac'); k=min(len(dr),len(ba),len(gu))
raw=(dr[:k]<-50)&(ba[:k]<-50)&(gu[:k]<-50); lab_,nl=label(raw); stop=np.zeros(k,bool)
for i in range(1,nl+1):                      # só paradas de verdade (>=0,2 s); o ar entre golpes do groove não conta
    w=np.where(lab_==i)[0]
    if len(w)>=20: stop[w]=True
stop=binary_dilation(stop,iterations=3)
gate=np.ones(N);
for i in np.where(stop)[0]: gate[i*441:(i+1)*441]=0
gate=uniform_filter1d(gate,size=int(0.015*fs))
# ---------- voz: notas do MIDI (alinhado à Vit) -> envelope para ducking e pausas
VN=sorted(pm.PrettyMIDI('/home/claude/vt/w/voz.mid').instruments[0].notes,key=lambda n:n.start)
vact=np.zeros(N)
for n in VN: vact[int(n.start*fs):int(n.end*fs)]=1
vduck=10**(-2.5*uniform_filter1d(vact,size=int(0.12*fs))/20)
gaps=[]
for a,b in zip(VN,VN[1:]):
    if b.start-a.end>=0.55: gaps.append((a.end,b.start))
# ---------- osciladores por tabela (saw limitado em banda)
TAB={}
def saw_tab(f):
    K=max(1,int(9000//f)); key=K
    if key not in TAB:
        x=np.arange(4096)/4096; TAB[key]=sum(np.sin(2*np.pi*k*x)/k for k in range(1,K+1))*(2/np.pi)
    return TAB[key]
def osc(f,n,cents=0.0,vib=0.0):
    ff=f*2**(cents/1200)*(1+vib*np.sin(2*np.pi*4.7*np.arange(n)/fs+rng.uniform(0,6.28)))
    ph=(np.cumsum(ff/fs)+rng.uniform())%1.0; t=saw_tab(f); return np.interp(ph*4096,np.arange(4097),np.append(t,t[0]))
mid=lambda p: 440*2**((p-69)/12)
# ---------- PAD: um acorde por segmento de acorde, ataque 0,35 s, release 0,7 s, 3 osciladores desafinados (estéreo)
PADLV={'verso1':-3,'verso2':-2,'pre1':(-2,0),'refrao1':0,'pos':-1,'pre2':(-1,0),'refrao2':0,'refrao3':1,'final':-3,'fim':-5}
PADLP={'verso1':1300,'verso2':1500,'pre1':(1600,2600),'refrao1':2800,'pos':2200,'pre2':(1800,2600),'refrao2':2800,'refrao3':3000,'final':1300,'fim':1200}
pad=np.zeros((N,2)); padmidi=[]; prev=None
for (a,b),lab in zip(seg,ch):
    if a>=len(B)-1: break
    t0=B[a]; t1=B[min(b,len(B)-1)]; s=sec(t0)
    if s not in PADLV: continue
    v=voicing(lab,50,74,prev); prev=v; dur=t1-t0; n=int((dur+0.7)*fs); i0=int(t0*fs)
    if i0+n>N: n=N-i0
    if n<=0: continue
    tt=np.arange(n)/fs; env=np.minimum(1,tt/0.35)*np.where(tt<dur,1,np.exp(-(tt-dur)/0.25))
    for p in v:
        f=mid(p); L=osc(f,n,-7,0.0015)+0.7*osc(f,n,0,0.001); Rr=osc(f,n,7,0.0015)+0.7*osc(f,n,0,0.001)
        pad[i0:i0+n,0]+=L*env*0.25; pad[i0:i0+n,1]+=Rr*env*0.25; padmidi.append((p,t0,dur,70))
# filtro e nível por seção (rampas no pré), passa-altas 180 Hz para não embolar com surdo/baixo
cut=np.full(N,1500.0); lvl=np.full(N,-60.0)
for (nme,a),(_,b) in zip(SEC,SEC[1:]):
    if nme not in PADLV: continue
    i0,i1=int(a*fs),min(N,int(b*fs)); x=np.linspace(0,1,max(1,i1-i0))
    lv=PADLV[nme]; lp=PADLP[nme]
    lvl[i0:i1]=lv[0]+(lv[1]-lv[0])*x if isinstance(lv,tuple) else lv
    cut[i0:i1]=lp[0]+(lp[1]-lp[0])*x if isinstance(lp,tuple) else lp
lvl=uniform_filter1d(lvl,size=int(0.5*fs))
out=np.zeros_like(pad); H=int(0.5*fs)
for i in range(0,N,H):          # filtro variável em blocos de 0,5 s com sobreposição
    j=min(N,i+H); c=float(np.median(cut[i:j])); sos=ss.butter(2,[180,c],btype='bandpass',fs=fs,output='sos')
    a0=max(0,i-H); y=ss.sosfilt(sos,pad[a0:j],axis=0)[i-a0:]; w=np.ones(j-i)
    out[i:j]+=y*w[:,None]
pad=out*(10**(lvl/20)*vduck*gate)[:,None]
# ---------- PLUCKS nas pausas da voz: arpejo de 16ªs do acorde, acima da voz (C5–D6), delay em colcheia pontuada
PLK={'verso2':0.8,'pre1':0.9,'refrao1':1.0,'pos':1.0,'pre2':0.9,'refrao2':1.0,'refrao3':1.0,'final':0.6,'verso1':0.55}
def chord_at(t):
    b=int(np.searchsorted(B,t)-1); b-=b%2
    for (a,c),lab in zip(seg,ch):
        if a<=b<c: return lab
    return ch[-1]
plk=np.zeros((N,2)); plkmidi=[]
for g0,g1 in gaps:
    s=sec(g0)
    if s not in PLK: continue
    b=int(np.searchsorted(B,g0));
    ks=[(bb,kk) for bb in range(b-1,b+4) for kk in range(4) if g0+0.06<=T(bb,kk)<=g1-0.12]
    sp=1 if s not in ('verso1','final') else 2          # versos íntimos: colcheias
    ks=ks[::sp][:8]
    if len(ks)<2: continue
    lab=chord_at(g0); r,iv=parse(lab); tones=sorted({72+((r+i-72)%12) for i in iv}|{84+((r+i-84)%12) for i in iv if 84+((r+i-84)%12)<=86})
    up=rng.random()<0.6
    for j,(bb,kk) in enumerate(ks):
        p=tones[j%len(tones)] if up else tones[::-1][j%len(tones)]; t=T(bb,kk); v=PLK[s]*(1-0.06*j)
        n=int(0.45*fs); i0=int(t*fs)
        if i0+n>N or gate[i0]<0.5: continue
        tt=np.arange(n)/fs; e=np.exp(-tt/0.16)*np.minimum(1,tt/0.003)
        x=(osc(mid(p),n,0)+0.5*osc(mid(p)*2,n,3))*e*v
        pa=0.25*np.sin(j*1.3); plk[i0:i0+n,0]+=x*(1-pa); plk[i0:i0+n,1]+=x*(1+pa); plkmidi.append((p,t,0.2,int(90*v)))
plk=ss.sosfilt(ss.butter(2,[400,5500],btype='bandpass',fs=fs,output='sos'),plk,axis=0)
dl=int(0.75*per*fs); fb=np.zeros_like(plk)
for k_,g_ in [(1,0.38),(2,0.16)]:
    sh=np.zeros_like(plk); sh[dl*k_:]=plk[:-dl*k_]; fb+=sh[:,::-1]*g_ if k_%2 else sh*g_
plk=(plk+fb)*gate[:,None]
# ---------- calibração: pad no refrão = mix −16 LU; plucks = mix −19 LU (onde soam)
m=pl.Meter(fs); ra,rb=int(44.6*fs),int(68.5*fs)
Lmix=m.integrated_loudness(src[ra:rb]); pad*=10**((Lmix-16-m.integrated_loudness(pad[ra:rb]))/20)
act=np.abs(plk).max(1)>1e-5; plk*=10**((m.integrated_loudness(src[act])-19-m.integrated_loudness(plk[act]))/20)
for nm,z in [('pad',pad),('pluck',plk)]: sf.write(f'{R}/{nm}.wav',z.astype(np.float32),fs,subtype='FLOAT')
mm=pm.PrettyMIDI(initial_tempo=float(60/per))
for nm,prog,L in [('Pad sintetizado',89,padmidi),('Pluck sintetizado',84,plkmidi)]:
    ins=pm.Instrument(prog,name=nm); ins.notes=[pm.Note(int(v),int(p),float(t),float(t+d)) for p,t,d,v in L]; mm.instruments.append(ins)
mm.write(f'{R}/Mente_Vit_sintetizadores.mid')
print(f'pad: {len(padmidi)} notas; plucks: {len(plkmidi)} notas em {len(gaps)} pausas da voz; paradas mascaradas: {stop.sum()*10/1000:.1f} s')
json.dump({'gaps':gaps},open(f'{R}/gaps.json','w'))
