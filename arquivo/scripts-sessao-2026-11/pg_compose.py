# Pagodiza MIDIs do MIDIGEN: uso  pg_compose.py entrada.mid nome
# Escala: 1 tempo (semínima) do gerador = 1 colcheia do pagode; compasso 4/4 do gerador = compasso 2/4 do pagode.
# Melodia: síncopes (antecipação da 4ª semicolcheia, célula semicolcheia-colcheia-semicolcheia), acentos medidos em "Traição".
# Harmonia: 1 acorde por compasso de 2/4 (Viterbi com cadências). Forma: intro, passada leve, parada+virada, drop, passada cheia, final.
import sys, json, numpy as np, mido
sys.path.insert(0,'/home/claude/scripts'); from pg_read import ler
SRC,NOME=sys.argv[1],sys.argv[2]; BPM=76.0; per=60/BPM; S16=per/4
rng=np.random.default_rng(76)
notes,bpm_src=ler(SRC)
NAMES='C C# D D# E F F# G G# A A# B'.split()
QUAL={'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10],'maj7':[0,4,7,11],'m7b5':[0,3,6,10]}
# ---------------- tonalidade (perfis de Krumhansl)
MAJ=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); MIN=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
h=np.zeros(12)
for a,d,p,_ in notes: h[p%12]+=d
best=max(((np.corrcoef(h,np.roll(prof,k))[0,1],k,m) for k in range(12) for m,prof in (('maj',MAJ),('min',MIN))))
_,TON,MODO=best
if MODO=='maj': DEG=[(0,'',"I"),(2,'m7',"ii"),(4,'m7',"iii"),(5,'',"IV"),(7,'7',"V7"),(9,'m7',"vi")]
else:           DEG=[(0,'m7',"i"),(5,'m7',"iv"),(7,'7',"V7"),(8,'',"VI"),(3,'',"III"),(10,'7',"VII7"),(2,'m7b5',"ii")]
CH=[(NAMES[(TON+r)%12]+q,(TON+r)%12,q,g) for r,q,g in DEG]
print(f'{NOME}: fonte {bpm_src:.0f} BPM, tom estimado {NAMES[TON]} {"maior" if MODO=="maj" else "menor"}')
# ---------------- melodia ou acordes?
from itertools import groupby
onsets=[k for k,g in groupby(notes,key=lambda x:round(x[0],3))]
poly=len(notes)>1.5*len(onsets)
fim_src=int(np.ceil(max(a+d for a,d,_,_ in notes)/4)*4); NBAR=fim_src//4
# ---------------- pagodização da melodia (unidades: semicolcheias do pagode)
mel=[]; log={}
CELLS={'x...':([0],0),'x.x.':([0,2],-1),'xx.x':([0,1,3],2),'.x.x':([1,3],2),'x..x':([0,3],1.5),'..xx':([2,3],0.5),
       'xxxx':([0,1,2,3],0),'.xxx':([1,2,3],1.5),'...x':([3],1),'....':([],0),'.x..':([1],0.5),'x.xx':([0,2,3],1)}
def sincopes(on):
    # onset numa semicolcheia fraca (2ª ou 4ª) que segura sobre a posição forte seguinte (sem onset nela)
    s=set(on); return sum(1 for o in s if o%2==1 and (o+1) not in s)
if not poly:
    orig=[[int(round(a*2)),max(1,int(round(d*2))),p] for a,d,p,_ in notes]
    nb=int(np.ceil(max(s+l for s,l,_ in orig)/8))
    porbar=[[n for n in orig if n[0]//8==k] for k in range(nb)]
    combos={}
    for n1,(c1,s1) in CELLS.items():
        for n2,(c2,s2) in CELLS.items():
            on=c1+[4+x for x in c2]; combos.setdefault(len(on),[]).append((on,s1+s2,n1+'|'+n2))
    prev_end7=False; prev_key=None; novo=[]; rr=np.random.default_rng(7)
    for k,ns in enumerate(porbar):
        n=len(ns)
        if n==0: prev_end7=False; prev_key=None; continue
        best=None
        for on,sc,key in combos[n]:
            s=sc+(1.0 if 7 in on and k%2==0 else 0)+(0.4 if 7 in on else 0)
            if prev_end7: s+=1.5 if on[0]>0 else -1.0
            if key==prev_key: s-=0.3
            s+=rr.uniform(0,0.25)
            if best is None or s>best[0]: best=(s,on,key)
        _,on,key=best
        for o,(_,_,p) in zip(on,ns): novo.append([8*k+o,0,p])
        prev_end7=7 in on; prev_key=key
    for i,nn in enumerate(novo):                  # duração: até o próximo ataque (máx. 3/16 se houver pausa longa depois)
        nxt=novo[i+1][0] if i+1<len(novo) else nn[0]+4
        nn[1]=max(1,min(nxt-nn[0],3 if nxt-nn[0]>4 else nxt-nn[0]))
    mel=novo
    log={'sincopes_antes':sincopes([s for s,_,_ in orig]),'sincopes_depois':sincopes([s for s,_,_ in mel]),
         'atravessam_compasso':sum(1 for s,l,_ in mel if s%8==7 and ((s+1) not in {x for x,_,_ in mel})),'notas':len(mel)}
    print(' melodia (mesmas notas, ritmo novo):',log)
# ---------------- harmonia por compasso
W=np.zeros((NBAR,12))
SRCN=[(s,l,p) for s,l,p in mel] if mel else [(a*2,d*2,p) for a,d,p,_ in notes]
for s,l,p in SRCN:
    bar=int(s//8)
    if bar>=NBAR: continue
    W[bar,p%12]+=l*(1.5 if (s%4 in (0,3)) else 1.0)
def fit(bar,c):
    _,r,q,_=CH[c]; tones=[(r+i)%12 for i in QUAL[q]]; w=W[bar]; tot=w.sum()+1e-9
    s=sum(w[t]*(1.0 if k<3 else 0.6) for k,t in enumerate(tones)); return (s-0.4*(tot-sum(w[t] for t in tones)))/tot
def trans(a,b):
    ga,gb=CH[a][3],CH[b][3]; v=0.0
    if a==b: v-=0.15
    if gb in ('I','i') and ga=='V7': v+=0.35
    if gb=='V7' and ga in ('ii','IV','iv','VI'): v+=0.2
    return v
K=len(CH); D=np.full((NBAR,K),-1e9); BK=np.zeros((NBAR,K),int)
for c in range(K): D[0,c]=fit(0,c)+(0.3 if CH[c][3] in ('I','i') else 0)
for b in range(1,NBAR):
    for c in range(K):
        sc=[D[b-1,a]+trans(a,c) for a in range(K)]; a=int(np.argmax(sc))
        bonus=0
        if b==NBAR-1 and CH[c][3] in ('I','i'): bonus+=1.0
        if b==NBAR-2 and CH[c][3]=='V7': bonus+=0.4
        if b%4==3 and b!=NBAR-1 and CH[c][3]=='V7': bonus+=0.15
        D[b,c]=sc[a]+fit(b,c)+bonus; BK[b,c]=a
seq=[int(np.argmax(D[-1]))]
for b in range(NBAR-1,0,-1): seq.append(BK[b,seq[-1]])
seq=seq[::-1]; PROG=[CH[c][0] for c in seq]
print(' acordes:',' | '.join(PROG))
# ---------------- forma (em compassos de 2/4 do pagode)
if poly: FORM=[('leve',PROG[:NBAR//2],False),('cheio',PROG[NBAR//2:],False)]; INTRO=0
else:    FORM=[('leve',PROG,True),('cheio',PROG,True)]; INTRO=2
bars=[]                                           # (estado, acorde, índice na passada, passada, tem melodia)
for k in range(INTRO): bars.append(('pre',PROG[k],-1,-1,False))
for pi,(est,pr,m) in enumerate(FORM):
    for j,c in enumerate(pr): bars.append((est,c,j,pi,m))
NB=len(bars); CHORUS=INTRO+len(FORM[0][1])        # compasso onde entra a passada cheia
PARADA={CHORUS-3}; VIRADA={CHORUS-2:1,CHORUS-1:2}
def T(bar,beat=0,k=0): return (bar*2+beat)*per+k*S16
P={k:[] for k in ['surdo','tanta','pandeiro','repique','ganza','pratos','bass','cavaco','violao','melodia']}
MICRO={'pandeiro':[0,0.008,0,0.003],'tanta':[0,0,0.003,0.003],'melodia':[0,0.006,0,0.003]}
def add(part,pitch,t,dur,vel,k=None,jit=0.003):
    if k is not None and part in MICRO: t+=MICRO[part][k%4]
    t+=rng.normal(0,jit); P[part].append([int(pitch),max(0.0,float(t)),max(0.03,float(dur)),int(np.clip(vel+rng.normal(0,3),8,127))])
def parse(l):
    r=NAMES.index(l[:2]) if l[:2] in NAMES else NAMES.index(l[0]); return r,QUAL[l[len(NAMES[r]):]]
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
def root(l,base=38): r,_=parse(l); return base+((r-base)%12)
def tone(l,i,base=38): r,iv=parse(l); return root(l,base)+iv[min(i,len(iv)-1)]
prev={'cav':None,'vio':None}
for b,(est,l,j,pi,m) in enumerate(bars):
    nl=bars[b+1][1] if b+1<NB else PROG[-1]; r=root(l); nr=root(nl)
    parada=b in PARADA; vir=VIRADA.get(b,0); E={'pre':0.85,'leve':0.9,'cheio':1.0}[est]
    # percussão (padrões de "Traição": surdo 1º abafado / 2º aberto / puxada na 4ª 16ª; pandeiro e tantã com acentos medidos)
    if parada: pass
    elif vir:
        if vir==1: add('surdo',41,T(b),0.3,95); add('tanta',62,T(b),0.1,96,0)
        for k in range(2 if vir==1 else 0,8 if vir==1 else 6):
            x=((vir-1)*8+k)/16; add('tanta',62,T(b,k//4,k%4),0.1,44+76*x,k)
            if vir==2: add('pandeiro',54,T(b,k//4,k%4),0.08,40+70*x,k)
        if vir==2: add('surdo',41,T(b,1),0.3,110)
    elif est=='cheio':
        add('surdo',41,T(b),0.15,72); add('surdo',41,T(b,1),0.45,122); add('surdo',41,T(b,1,3),0.15,96,3)
        for bt in (0,1):
            for k,(vp,vt) in enumerate(zip([120,67,118,84],[120,52,100,124])):
                add('pandeiro',54,T(b,bt,k),0.08,vp,k); add('tanta',62,T(b,bt,k),0.1,vt,k)
            add('repique',65,T(b,bt,3),0.08,58,3)
    elif est=='leve':
        add('surdo',41,T(b),0.12,58); add('surdo',41,T(b,1),0.4,100)
        if b%2: add('surdo',41,T(b,1,3),0.12,70,3)
        for k,v in [(0,78),(2,54),(4,80),(6,58)]: add('ganza',70,T(b,k//4,k%4),0.07,v,k)
        for bt in (0,1): add('pandeiro',54,T(b,bt,0),0.08,70,0); add('pandeiro',54,T(b,bt,3),0.08,62,3)
    else:  # pre / intro
        add('surdo',41,T(b,1),0.35,84)
        for k,v in [(0,56),(4,62)]: add('ganza',70,T(b,k//4,k%4),0.07,v,k)
    # baixo
    def appr(): return nr-1 if nr!=r else r+7-12
    if parada: add('bass',r,T(b),2*per*0.98,116)
    elif est=='pre': add('bass',r,T(b),2*per*0.95,72)
    elif est=='leve' or vir==1:
        add('bass',r,T(b),per*0.25,76); add('bass',r,T(b,1),per*0.9,104); add('bass',appr(),T(b,1,3),per*0.22,82,3)
    else:
        land=(b==CHORUS); v=b%4
        add('bass',r,T(b),per*(0.9 if land else 0.38),124 if land else 110); add('bass',r,T(b,0,1),per*0.2,72,1); add('bass',tone(l,2),T(b,0,3),per*0.22,92,3)
        add('bass',r+12 if v==1 else r,T(b,1),per*0.24,104); add('bass',tone(l,1),T(b,1,1),per*0.2,82,1)
        if vir!=2: add('bass',tone(l,2),T(b,1,2),per*0.2,86,2); add('bass',appr(),T(b,1,3),per*0.22,94,3)
    # cavaco
    cv=voicing(l,62,81,prev['cav']); prev['cav']=cv
    pat={'cheio':[80,95,110,70,115,72,80,98],'leve':[85,0,0,80,90,85,0,100],'pre':[70,0,0,0,85,0,0,80]}[est]
    if parada: pat=[78,0,0,0,0,0,0,0]
    if vir==1: pat=[0,0,95,0,100,0,0,90]
    if vir==2: pat=pat[:6]+[0,0]
    for k,v in enumerate(pat):
        if v:
            d=2*per*0.95 if parada else per*0.22
            for p in cv: add('cavaco',p,T(b,k//4,k%4),d,v*E,k)
    # violão
    vv=voicing(l,52,67,prev['vio']); prev['vio']=vv; vb=root(l,40)
    if parada: add('violao',vb,T(b),2*per,56); [add('violao',p,T(b),2*per,52) for p in vv]
    elif est in ('leve','pre'):
        add('violao',vb,T(b),per*0.9,80); [add('violao',p,T(b,1),per*0.9,92) for p in vv]; [add('violao',p,T(b,1,2),per*0.4,58) for p in vv[1:]]
    elif vir==1: [add('violao',p,T(b,1),per*1.6,98) for p in vv]
    else:
        add('violao',vb,T(b),per*0.5,78)
        for k,v in [(2,66),(3,58),(4,84),(6,66),(7,60)]:
            if vir==2 and k>=6: continue
            [add('violao',p,T(b,k//4,k%4),per*0.22,v,k) for p in vv]
# melodia nas duas passadas (cheia: mesma linha, um pouco mais forte)
VEL={0:88,1:70,2:80,3:96}
if mel:
    for pi,(est,pr,m) in enumerate(FORM):
        b0=INTRO+pi*len(PROG)
        for s,l,p in mel:
            vel=VEL[s%4]+(8 if pi==1 else 0)
            add('melodia',p,T(b0)+s*S16,l*S16*0.92,vel,s%4,jit=0.002)
# final: acorde de tônica segura 2 compassos
lf=PROG[-1]; END=NB
[add('cavaco',p,T(END),4*per,70) for p in voicing(lf,62,81,prev['cav'])]; add('bass',root(lf),T(END),4*per,86)
[add('violao',p,T(END),4*per,70) for p in voicing(lf,52,67,prev['vio'])]; add('surdo',41,T(END),0.5,90); add('pratos',49,T(END),2.5,80)
# entrada da passada cheia como a v2 aprovada de Mente: banda some 2 semicolcheias antes do tempo até a 3ª semicolcheia; pancada + crash
g0=T(CHORUS-1,1,2)-0.012; g1=T(CHORUS,0,2)-0.012
for k in P:
    if k=='melodia': continue
    keep=[]
    for n in P[k]:
        p_,t_,d_,v_=n
        if g0<=t_<g1: continue
        if t_<g0<t_+d_: n=[p_,t_,max(0.03,g0-t_),v_]
        keep.append(n)
    P[k]=keep
ts=T(CHORUS,0,2); lc=bars[CHORUS][1]
add('surdo',41,ts,0.45,127,jit=0); add('surdo',41,ts,0.45,127,jit=0); add('bass',root(lc),ts,per*0.3,127,jit=0)
add('tanta',62,ts,0.12,124,2); add('pandeiro',54,ts,0.1,124,2); add('repique',65,ts,0.1,110,2); add('pratos',49,ts,2.0,108)
# ---------------- MIDI multipista (2/4, 76 BPM; percussão no canal 10 com notas GM)
PPQ=480
def tk(t): return int(round(t/per*PPQ))
mf=mido.MidiFile(ticks_per_beat=PPQ); t0=mido.MidiTrack()
t0.append(mido.MetaMessage('time_signature',numerator=2,denominator=4,time=0)); t0.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(BPM),time=0))
t0.append(mido.MetaMessage('end_of_track',time=0)); mf.tracks.append(t0)
TR=[('melodia',['melodia'],0,73),('cavaco',['cavaco'],1,25),('violao',['violao'],2,24),('baixo',['bass'],3,33),
    ('percussao',['surdo','tanta','pandeiro','repique','ganza','pratos'],9,0)]
for name,keys,chn,prog in TR:
    ev=[]
    for k in keys:
        for p,t,d,v in P[k]: ev+= [(tk(t),1,mido.Message('note_on',note=p,velocity=v,channel=chn)),(tk(t+d),0,mido.Message('note_off',note=p,velocity=0,channel=chn))]
    if not ev: continue
    tr=mido.MidiTrack(); tr.append(mido.MetaMessage('track_name',name=name,time=0))
    if chn!=9: tr.append(mido.Message('program_change',program=prog,channel=chn,time=0))
    ev.sort(key=lambda e:(e[0],e[1])); lt=0
    for t,_,m in ev: m.time=t-lt; tr.append(m); lt=t
    tr.append(mido.MetaMessage('end_of_track',time=0)); mf.tracks.append(tr)
mf.save(f'{NOME}.mid')
# só a melodia pagodizada, uma passada, sem arranjo
if mel:
    m1=mido.MidiFile(ticks_per_beat=PPQ); m1.tracks.append(t0); tr=mido.MidiTrack(); ev=[]
    for s,l,p in mel: ev+=[(s*PPQ//4,1,mido.Message('note_on',note=p,velocity=VEL[s%4])),(s*PPQ//4+l*PPQ//4,0,mido.Message('note_off',note=p,velocity=0))]
    ev.sort(key=lambda e:(e[0],e[1])); lt=0
    for t,_,m in ev: m.time=t-lt; tr.append(m); lt=t
    m1.tracks.append(tr); m1.save(f'{NOME}_so_melodia.mid')
np.save(f'{NOME}_parts.npy',np.array([P],dtype=object),allow_pickle=True)
dur=T(NB)+4*per+2.5
json.dump({'nome':NOME,'tom':NAMES[TON]+(' maior' if MODO=='maj' else ' menor'),'acordes':PROG,'log':log,'dur':dur,'chorus_t':T(CHORUS),'poly':poly},open(f'{NOME}_info.json','w'),ensure_ascii=False)
print(f' forma: {NB} compassos de 2/4 + final, {dur:.1f} s; passada cheia em {T(CHORUS):.1f} s')
