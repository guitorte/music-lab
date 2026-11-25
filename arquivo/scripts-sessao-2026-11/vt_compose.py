# Mente (Vit) com o arranjo de "Traição": mesmos padrões medidos (tr_t2, tr_t9, tr_t11, tr_t12), na harmonia e forma de Mente.
# Compasso de 2/4 = 2 tempos; começa em índice de tempo par (troca de acorde). Surdo: 1º abafado, 2º aberto, puxada na 4ª 16ª do 2º.
import numpy as np, pretty_midi as pm, json
rng=np.random.default_rng(76); R='/home/claude/vt/w'
A=np.load(f'{R}/analysis.npz'); beats=A['beats']; C=np.load(f'{R}/chords.npz'); ch=C['ch']; seg=C['seg']
NB=len(beats); per=float(np.median(np.diff(beats)))
def T(b,k=0):
    b=b+k//4; s=k%4
    if b>=NB-1: return beats[-1]+(b-(NB-1))*per+s*per/4
    return beats[b]+s*(beats[b+1]-beats[b])/4
chord_at={}
for k,(a,b) in enumerate(seg):
    for bb in range(a,b): chord_at[bb]=ch[k]
def CH(b): return chord_at.get(b, chord_at[max(chord_at)])
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
def root(l,base=38): r,_=parse(l); return base+((r-base)%12)          # baixo: D2..C#3 (Traição: mediana A2)
def tone(l,iv_idx,base=38):
    r,iv=parse(l); return root(l,base)+iv[min(iv_idx,len(iv)-1)]
P={k:[] for k in ['surdo','tanta','pandeiro','tamborim','repique','ganza','pratos','palmas','aro','bass','cavaco','violao','pad','epiano','strings','sopros','sax']}
MICRO={'pandeiro':[0,0.008,0,0.003],'tanta':[0,0,0.003,0.003]}
def add(part,pitch,t,dur,vel,k=None,jit=0.003):
    if k is not None and part in MICRO: t+=MICRO[part][k%4]
    t+=rng.normal(0,jit); P[part].append([int(pitch),max(0.0,float(t)),max(0.03,float(dur)),int(np.clip(vel+rng.normal(0,3),8,127))])
def bi(t,up=False):
    if up: i=int(np.searchsorted(beats,t-0.02)); return i+(i%2)
    i=int(np.searchsorted(beats,t+0.05))-1; return max(0,i-(i%2))
# ---- forma (mesmos cortes da Vit) -> estado de "Traição"
_T=[('intro',0,'abertura'),('verso1',8.9,'abertura'),('verso2',20.0,'leve'),('pre1',31.5,'pre'),('refrao1',44.1,'cheio'),('pos',69.2,'cheio'),
    ('solo',81.9,'cheio'),('pre2',87.6,'cheio'),('refrao2',100.6,'cheio'),('refrao3',124.7,'cheio'),('final',150.1,'abertura'),('fim',162.3,'abertura')]
UP={'refrao1','solo','refrao2','refrao3'}
SEC=[]
for i,(n,t,e) in enumerate(_T):
    a=0 if t==0 else bi(t,n in UP); b=bi(_T[i+1][1],_T[i+1][0] in UP) if i+1<len(_T) else 242
    SEC.append((n,a,b,e))
END=242                                   # depois da última nota da voz (163,66 s): acorde final
CHORUS=[b for n,b,_,_ in SEC if n in ('refrao1','refrao2')]
PARADA={c-6 for c in CHORUS}; VIRADA={c-4:1,c-2:2} if False else {}
for c in CHORUS: VIRADA[c-4]=1; VIRADA[c-2]=2
def sec_of(b):
    for n,a,c,e in SEC:
        if a<=b<c: return n,e
    return 'fim','abertura'
print('seções:',[(n,a,round(beats[a],2),e) for n,a,_,e in SEC]); print('paradas em',[round(beats[p],2) for p in sorted(PARADA)],' refrões em',[round(beats[c],2) for c in CHORUS])
# ---- textura "outros" (cordas) por seção: Traição -> 1º refrão quase sem, refrão final +8 dB, sobe nas paradas
OUT_V={'intro':58,'verso1':52,'verso2':46,'pre1':60,'refrao1':0,'pos':0,'solo':0,'pre2':48,'refrao2':56,'refrao3':74,'final':60,'fim':60}
prev={'cav':None,'vio':None,'kb':None,'st':None}
for b in range(0,END,2):
    sec,est=sec_of(b); l=CH(b); nl=CH(b+2) if b+2<END else 'C'
    r=root(l); nr=root(nl); bar=b//2
    parada=b in PARADA; vir=VIRADA.get(b,0); chorus_land=b in CHORUS
    E={'abertura':0.8,'leve':0.88,'pre':0.9,'cheio':1.0}[est]
    # =============== PERCUSSÃO
    if parada: pass
    elif vir:
        if vir==1: add('surdo',41,T(b),0.3,95); add('tanta',62,T(b),0.1,96,0)      # 1 golpe
        for k in range(2 if vir==1 else 0,8):                                        # crescendo de 2 compassos (−27 -> −15 dB)
            x=((vir-1)*8+k)/16; add('tanta',62,T(b,k),0.1,44+76*x,k)
            if vir==2: add('pandeiro',54,T(b,k),0.08,40+70*x,k)
        if vir==2: add('surdo',41,T(b+1),0.3,110); add('surdo',41,T(b+1,3),0.15,100,3)
    elif est=='cheio':
        add('surdo',41,T(b),0.15,72); add('surdo',41,T(b+1),0.45,122); add('surdo',41,T(b+1,3),0.15,96,3)
        for bt in (0,1):
            for k,(vp,vt) in enumerate(zip([120,67,118,84],[120,52,100,124])):
                add('pandeiro',54,T(b+bt,k),0.08,vp*E,k); add('tanta',62,T(b+bt,k),0.1,vt*E,k)
            add('repique',65,T(b+bt,3),0.08,58*E,3)          # acento da 4ª 16ª nos médios (repique de mão)
    elif est=='leve':
        add('surdo',41,T(b),0.12,58); add('surdo',41,T(b+1),0.4,100)
        if bar%2: add('surdo',41,T(b+1,3),0.12,70,3)
        for k,v in [(0,78),(2,54),(4,80),(6,58)]: add('ganza',70,T(b+k//4,k%4),0.07,v,k)
    elif est=='pre':
        add('surdo',41,T(b+1),0.35,84)
        for k,v in [(0,56),(4,62)]: add('ganza',70,T(b+k//4,k%4),0.07,v,k)
    if chorus_land: add('pratos',49,T(b),1.6,112)
    if sec=='refrao3' and b==[a for n,a,_,_ in SEC if n=='refrao3'][0]: add('pratos',49,T(b),1.4,100)
    # =============== BAIXO (Traição: leve = ataque no 2º tempo; pré = só o 2º; cheio = linha contínua, fundamental no 1º)
    def appr(): return nr-1 if nr!=r else r+7-12
    if parada: add('bass',r,T(b),2*per*0.98,116)
    elif est=='abertura':
        if sec!='intro' or bar%2==0: add('bass',r,T(b),2*per*0.95,68*E/0.8)
    elif est=='leve':
        add('bass',r,T(b),per*0.25,76); add('bass',r,T(b+1),per*0.9,104); add('bass',appr(),T(b+1,3),per*0.22,82,3)
    elif est=='pre' or vir==1:
        add('bass',r,T(b+1),per*0.18,98); add('bass',tone(l,2),T(b+1,1),per*0.2,80,1); add('bass',appr(),T(b+1,3),per*0.2,86,3)
    else:   # cheio
        v=bar%4
        add('bass',r,T(b),per*0.38,110); add('bass',r,T(b,1),per*0.2,72,1); add('bass',tone(l,2),T(b,3),per*0.22,92,3)
        add('bass',r+12 if v==1 else r,T(b+1),per*0.24,104); add('bass',tone(l,1),T(b+1,1),per*0.2,82,1)
        add('bass',tone(l,2),T(b+1,2),per*0.2,86,2); add('bass',appr(),T(b+1,3),per*0.22,94,3)
    # =============== CAVACO (cheio: 16ªs com acento na 2ª, 3ª, 5ª e 8ª do compasso; leve e pré mais ralos)
    cv=voicing(l,62,81,prev['cav']); prev['cav']=cv
    pat={'cheio':[80,95,110,70,115,72,80,98],'leve':[85,0,0,80,90,85,0,100],'pre':[60,0,95,0,100,0,0,90],'abertura':[0]*8}[est]
    if parada: pat=[78,0,0,0,0,0,0,0]
    if vir==1: pat=[0,0,95,0,100,0,0,90]
    for k,v in enumerate(pat):
        if v:
            d=2*per*0.95 if parada else per*0.22
            for p in cv: add('cavaco',p,T(b+k//4,k%4),d,v*E,k)
    # =============== VIOLÃO (leve: baixo no 1º + acorde no 2º; pré: só o 2º; cheio: levada leve de 16ªs)
    vv=voicing(l,52,67,prev['vio']); prev['vio']=vv; vb=root(l,40)
    if parada:
        add('violao',vb,T(b),2*per,56); [add('violao',p,T(b),2*per,52) for p in vv]
    elif est=='leve':
        add('violao',vb,T(b),per*0.9,80); [add('violao',p,T(b+1),per*0.9,92) for p in vv]; [add('violao',p,T(b+1,2),per*0.4,58) for p in vv[1:]]
    elif est=='pre' or vir==1:
        [add('violao',p,T(b+1),per*1.6,98) for p in vv]
    elif est=='cheio':
        add('violao',vb,T(b),per*0.5,78)
        for k,v in [(2,66),(3,58),(4,84),(6,66),(7,60)]: [add('violao',p,T(b+k//4,k%4),per*0.22,v,k) for p in vv]
    # =============== TECLADO (Rhodes estéreo; abertura: acorde no 1º + notas de cima; leve: no tempo; pré: antecipações; cheio: tapete)
    kv=voicing(l,55,79,prev['kb']); prev['kb']=kv; top=sorted(kv)[-2:]
    if parada: [add('epiano',p,T(b),2*per*0.98,60) for p in kv]
    elif est=='abertura':
        [add('epiano',p,T(b),2*per*0.98,72) for p in kv]
        [add('epiano',p,T(b,3),per*0.7,56) for p in top]; add('epiano',top[-1],T(b+1,2),per*0.5,52,2)
    elif est=='leve':
        [add('epiano',p,T(b),per*0.95,70) for p in kv]; [add('epiano',p,T(b+1),per*0.95,76) for p in kv]
    elif est=='pre' or vir==1:
        nv=voicing(nl,55,79,kv)
        [add('epiano',p,T(b,3),per*0.4,74) for p in kv]; [add('epiano',p,T(b+1,2),per*0.25,82) for p in nv]; [add('epiano',p,T(b+1,3),per*0.5,78) for p in nv]
    else:
        [add('epiano',p,T(b),2*per*0.9,66) for p in kv]; [add('epiano',p,T(b,2),per*0.4,52) for p in top]; [add('epiano',p,T(b+1,1),per*0.4,50) for p in top]
    # =============== OUTROS = cordas sustentadas (sobem nas paradas e no refrão final)
    ov=OUT_V.get(sec,0)+(14 if parada else 0)+(6 if vir else 0)
    if ov>0:
        rr,iv=parse(l); vc=48+((rr-48)%12)
        sv=[vc]+voicing(l,57,79,prev['st'],n=2); prev['st']=sv[1:]
        for p in sv: add('strings',p,T(b),2*per*1.02,ov)
# ---- solo (82,2–87,6 s): cordas tocam a melodia do 1º refrão uma oitava acima
VOC=pm.PrettyMIDI(f'{R}/voz.mid').instruments[0].notes
s0=[a for n,a,_,_ in SEC if n=='solo'][0]; s1=[a for n,a,_,_ in SEC if n=='pre2'][0]; c0=CHORUS[0]; off=beats[s0]-beats[c0]
for x in VOC:
    t=x.start+off
    if beats[s0]-0.2<=t<beats[s1]-0.1: add('strings',x.pitch+12,t,min(x.end-x.start,beats[s1]-t)*1.02,92)
# ---- acorde final (Traição termina logo depois da voz): tudo segura 2 compassos
lf='C'; kv=voicing(lf,55,79,prev['kb'])+[74]; cv=voicing(lf,62,81,prev['cav'])
[add('epiano',p,T(END),4*per,70) for p in kv]; add('bass',root(lf),T(END),4*per,86); [add('cavaco',p,T(END),4*per,70) for p in cv]
[add('violao',p,T(END),4*per,70) for p in voicing(lf,52,67,prev['vio'])]; [add('strings',p,T(END),4.5*per,62) for p in [48,64,67,72]]
add('surdo',41,T(END),0.5,90); add('pratos',49,T(END),2.5,80)
P={k:sorted(v,key=lambda x:x[1]) for k,v in P.items()}
print({k:len(v) for k,v in P.items() if v}); np.save(f'{R}/parts.npy',np.array([P],dtype=object),allow_pickle=True)
json.dump({'SEC':[(n,a,c,e) for n,a,c,e in SEC],'PARADA':sorted(PARADA),'CHORUS':CHORUS,'END':END},open(f'{R}/forma.json','w'))
