# v2: três estados (verso meio-tempo intimista / pré acelerado / refrão pagode explosivo), transições e breques
import numpy as np, soundfile as sf, glob, json
from scipy import signal
rng=np.random.default_rng(21); R='/home/claude/rw2'
A=np.load(f'{R}/analysis.npz'); beats=A['beats']; C=np.load(f'{R}/chords.npz'); ch=C['ch']; seg=C['seg']
NB=len(beats); per=np.median(np.diff(beats))
def T(b,step=0):
    b=b+step//4; s=step%4
    if b>=NB-1: return beats[-1]+(b-(NB-1))*per+s*per/4
    return beats[b]+s*(beats[b+1]-beats[b])/4
TMPL=np.array([1.00,0.23,0.99,0.59]); MICRO=[0.0,0.006,0.0,0.003]
STOPS=[(44.80,46.15),(47.70,48.15),(83.20,83.50),(99.05,99.50),(104.30,104.85),(106.15,106.65)]
SEC=[('intro',0,16),('verso1',16,32),('verso2',32,48),('pre',48,68),('refrao',68,104),('pos',104,124),('solo',124,140),
     ('pre',140,158),('refrao',158,196),('refrao3',196,232),('final',232,254),('fim',254,NB-1)]
def sec_of(b):
    for n,a,c in SEC:
        if a<=b<c: return n,a,c
    return 'fim',254,NB-1
names='C C# D D# E F F# G G# A A# B'.split()
def parse(l):
    r=names.index(l[:2]) if l[:2] in names else names.index(l[0]); q=l[len(names[r]):]
    return r,{'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10]}[q]
chord_at={}
for k,(a,b) in enumerate(seg):
    for bb in range(a,b): chord_at[bb]=ch[k]
P={k:[] for k in ['surdo','tanta','pandeiro','tamborim','repique','ganza','pratos','palmas','aro','bass','cavaco','violao','pad','epiano','strings','sopros','sax']}
def add(part,pitch,t,dur,vel,slot=None,jit=0.004):
    if slot is not None: t+=MICRO[slot%4]
    t+=rng.normal(0,jit); P[part].append([int(pitch),max(0.0,t),max(0.03,dur),int(np.clip(vel+rng.normal(0,4),10,127))])
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
def rootnote(l,base=28): r,_=parse(l); return base+((r-4)%12)
# ---- vocal activity per 16th (for brass answers and breques)
v,fs=sf.read(glob.glob('/home/claude/ai2/stems/vocals*.flac')[0]); vm=v.mean(1); w=int(0.03*fs); k=len(vm)//w
ve=20*np.log10(np.sqrt((vm[:k*w].reshape(k,w)**2).mean(1))+1e-9); vth=np.percentile(ve[ve>-80],60)-18
def vocal_on(t0,t1): i0,i1=int(t0/0.03),max(int(t0/0.03)+1,int(t1/0.03)); return (ve[i0:i1]>vth).mean()
# breques (tempos das palavras via whisper): banda dá um golpe e cala sob a voz; volta junto no "o amor"/"amo"
W=json.load(open(f'{R}/words.json'))
def wt(word,near): c=[x for x in W if x[2].strip(',.').lower()==word and abs(x[0]-near)<2.5]; return min(c,key=lambda x:abs(x[0]-near))[0]
BRQ=[(wt('sou',58.0),wt('o',58.5)),(wt('sou',78.8),wt('o',79.5)),(wt('sabe',111.3),wt('amo',112.2)),(wt('sou',119.4),wt('o',119.9)),
     (wt('que',134.8),wt('amo',136.2)),(wt('sou',143.3),wt('o',143.8)),(wt('diz',163.5),wt('o',164.7))]
def q16(t):
    i=np.searchsorted(beats,t)-1; st=np.round((t-beats[i])/(beats[i+1]-beats[i])*4)/4; return beats[i]+st*(beats[i+1]-beats[i])
BREQ=[]
for ws,wr in BRQ:
    i=np.searchsorted(beats,ws+0.08)-1; tstab=beats[i]; tres=q16(wr-0.02)
    if tres-tstab<0.3: tstab=beats[i-1]
    BREQ.append((tstab,tres))
print('breques (golpe, volta):',[(round(a,2),round(b,2)) for a,b in BREQ])
in_breq=lambda b: False
is_breq_hit=lambda b: False
# ---- solo: vocal melody of chorus 1 ("Mente, me engana... amo novela") -> alto sax in the instrumental
import librosa
seg_v=librosa.resample(vm[int(44.5*fs):int(53.0*fs)].astype(np.float32),orig_sr=fs,target_sr=16000)
f0,vd,_=librosa.pyin(seg_v,fmin=110,fmax=700,sr=16000,frame_length=1024,hop_length=160); tt=44.5+np.arange(len(f0))*0.01
mid=np.where(vd,np.round(librosa.hz_to_midi(np.nan_to_num(f0,nan=1))),-1); notes=[];i=0
while i<len(mid):
    if mid[i]<0: i+=1; continue
    j=i
    while j<len(mid) and abs(mid[j]-mid[i])<1: j+=1
    if j-i>=8: notes.append((tt[i],tt[j-1]-tt[i]+0.01,int(mid[i])))
    i=j
def tb(t): i=np.searchsorted(beats,t)-1; return i+(t-beats[i])/(beats[i+1]-beats[i])
def bt(x): i=int(np.floor(x)); return beats[i]+(x-i)*(beats[i+1]-beats[i])
OFF=126-67
for t,d,p in notes:
    x=tb(t)+OFF; q=np.round(x*4)/4
    if q<139.5: add('sax',p+12 if p<60 else p,bt(q),d*0.95,92 if (q%1)==0 else 80,jit=0.006)
print('solo notes',len(P['sax']))
# ---- main loop
prev_cav=prev_pad=prev_ep=None
TAMB=[1,0,1,0,1,1,0,1]                        # teleco-teco (2 tempos)
CAV_PA=[1.0,0.25,0.75,1.0, 0.25,1.0,0.25,0.8]  # cavaco partido-alto (2 tempos, 16ths)
for b in range(NB-1):
    s,s0,s1=sec_of(b); lbl=chord_at.get(b,ch[-1]); r,iv=parse(lbl); even=(b%2==0); root=rootnote(lbl)
    nxt=chord_at.get(b+2,lbl); nroot=rootnote(nxt); fifth=root+7 if root+7<=52 else root-5
    last_bar=(b>=s1-4); breq=in_breq(b); hit=is_breq_hit(b)
    if s in ('intro',):
        if even: 
            for p in voicing(lbl,52,74,prev_pad,4): add('pad',p,T(b),2*per*0.98,38)
        vv=voicing(lbl,47,68,None,4); arp=[vv[0],vv[2],vv[1],vv[3]]
        for j in range(2): add('violao',arp[(2*(b%2)+j)%4],T(b,2*j),per*0.9,52+10*(j==0),2*j)
        if b>=s1-2:   # repique pickup into verse
            for k in range(4): add('repique',65,T(b,k),0.08,35+12*k+(20 if b==s1-1 else 0),k)
        continue
    if s in ('verso1','verso2','final'):
        E=0.55 if s=='verso1' else 0.68 if s=='verso2' else 0.6
        build = (s=='final' and b>=s1-6)
        # violão dedilhado (colcheias), baixo longo, aro no 3 (meio-tempo), shaker suave
        vv=voicing(lbl,47,68,None,4); arp=[vv[0],vv[2],vv[1],vv[3],vv[2],vv[1],vv[3],vv[2]]
        for j in range(2): add('violao',arp[(2*(b%4)+j)%8],T(b,2*j),per*0.85,(50+12*(j==0))*(1.15 if build else 1),2*j)
        if even:
            for p in voicing(lbl,52,74,prev_pad,4): add('pad',p,T(b),2*per*0.98,40)
            add('bass',root,T(b),2*per*0.9,72*E**0.3,0)
        if b%4==0: add('surdo',41,T(b),0.3,70*E)
        if b%4==2: add('aro',37,T(b),0.1,58*E/0.6)
        for k in (0,2): add('ganza',70,T(b,k),0.07,(26+22*TMPL[k])*(1.4 if build else 1),k)
        if s=='verso2':
            if even:
                v2=voicing(lbl,60,79,prev_cav,4); prev_cav=v2
                for p in v2: add('cavaco',p,T(b),per*1.6,40)          # acorde longo, sem levada
            for k in range(4): add('pandeiro',54,T(b,k),0.08,(18+40*TMPL[k]),k)
        if build:   # final building back
            for k in range(4): add('repique',65,T(b,k),0.08,40+8*k+6*(b-(s1-6)),k)
        continue
    # ---------------- groove sections
    ch_like = s in ('refrao','refrao3','fim','solo')
    E={'pre':0.82,'refrao':1.0,'refrao3':1.06,'pos':0.92,'solo':0.95,'fim':1.0}[s]
    if hit:   # breque: one tutti stab then silence until the voice returns
        for p in voicing(lbl,60,79,prev_cav,4): add('cavaco',p,T(b),0.12,112)
        add('surdo',41,T(b),0.3,118); add('bass',root,T(b),0.25,110,0); add('pratos',57,T(b),1.0,85)
        for p in voicing(lbl,65,84,None,3): add('sopros',p,T(b),0.18,105)
        continue
    if breq: continue
    # surdo
    if s=='pre':
        add('surdo',41,T(b),0.3,(108 if even else 78)*E**0.5)
    else:
        add('surdo',41,T(b),0.3,(118 if even else 62)*E**0.5)
        if not even: add('surdo',41,T(b,3),0.15,70*E,3)
        if even: add('surdo',35,T(b),0.3,76*E)
    # pandeiro / tantã / ganzá
    for k in range(4):
        a=TMPL[k]
        add('pandeiro',54,T(b,k),0.09,(26+80*a)*E,k)
        add('ganza',70,T(b,k),0.07,(34+40*a)*E,k)
        if ch_like or s=='pos': add('tanta',[64,62,63,64][k],T(b,k),0.12,(32+82*a)*E,k)
    if s=='pre' and b%2==1: add('aro',37,T(b),0.1,70)   # backbeat de aro empurra o pré
    if ch_like:
        for k in range(4):
            if TAMB[(b%2)*4+k]: add('tamborim',76,T(b,k),0.08,(60+45*TMPL[k])*E,k)
        if b%2==1:
            for k,p,vv in [(1,65,68),(3,66,88)]: add('repique',p,T(b,k),0.1,vv*E,k)
    if s in ('refrao3','fim') and b%2==1: add('palmas',39,T(b),0.1,96)
    # pratos: crash na entrada do refrão (depois da parada), em cada 8 compassos, e no fim
    if (s in ('refrao','refrao3','solo') and (b-s0)%16==0) or (s=='pos' and b==s0):
        tcrash=T(b)
        for a_,b_ in STOPS:
            if a_-0.02<=tcrash<b_: tcrash=b_+0.01
        add('pratos',49,tcrash,1.5,105*E)
    # baixo
    if s=='pre':
        add('bass',root,T(b,0),per*0.45,96,0); add('bass',root+12 if root+12<=52 else root,T(b,2),per*0.22,78,2); add('bass',fifth,T(b,3),per*0.22,84,3)
    else:
        if even:
            add('bass',root,T(b,0),per*0.6,108,0); add('bass',fifth,T(b,3),per*0.22,86,3)
        else:
            add('bass',root+12 if root+12<=55 else root,T(b,0),per*0.35,94,0)
            appr=nroot-1 if nroot>root else nroot+2; add('bass',appr,T(b,2),per*0.4,90,2)
    # cavaco
    v4=voicing(lbl,62,82,prev_cav,4); prev_cav=v4
    if s=='pre':
        for k in (0,2):   # colcheias cortadas, acento no contratempo
            for p in v4: add('cavaco',p,T(b,k),0.08,(62 if k==0 else 84)*E,k)
    else:
        for k in range(4):
            a=CAV_PA[(b%2)*4+k]; dur=0.06 if a<0.5 else 0.11
            for p in v4: add('cavaco',p,T(b,k),dur,(22+90*a)*E,k)
    # violão segue, mais curto
    vv=voicing(lbl,47,68,None,4)
    for j in range(2): add('violao',[vv[0],vv[2]][j],T(b,2*j),per*0.45,58*E,2*j)
    # pad / strings / epiano
    if even:
        for p in voicing(lbl,52,74,prev_pad,4): add('pad',p,T(b),2*per*0.98,46 if s=='pre' else 52)
        if s=='pre':   # cordas crescendo ao longo do pré
            prog=(b-s0)/(s1-s0)
            for p in voicing(lbl,60,84,None,3): add('strings',p,T(b),2*per*0.98,int(38+60*prog))
        if s in ('refrao','refrao3','pos','fim'):
            for p in voicing(lbl,60,84,None,3): add('strings',p,T(b),2*per*0.98,58)
            ve4=voicing(lbl,55,76,prev_ep,4); prev_ep=ve4
            for st,vel in [(1,62),(6,76)]:
                for p in ve4: add('epiano',p,T(b,st),per*0.3,vel,st%4)
    # sopros: resposta à voz (só refrão/pós/fim), em buracos da voz de >= 1 tempo
    if s in ('refrao','refrao3','pos','fim') and even and vocal_on(T(b),T(b+2))<0.25 and not in_breq(b+1):
        tv=voicing(lbl,64,84,None,3)
        for st,d,vel in [(0,0.14,96),(3,0.12,88),(6,0.32,104)]:
            for p in tv: add('sopros',p,T(b,st),d,vel*E,st%4)
    # convenção + rolo no fim do pré (antes da parada)
    if s=='pre' and last_bar:
        if b>=s1-2:
            for k in range(4): add('repique',65 if k%2 else 66,T(b,k),0.08,60+10*k+18*(b-(s1-2)),k)
            for k in range(4): add('tanta',62,T(b,k),0.1,70+12*k,k)
        if b==s1-3:
            for st in (0,3):
                for p in voicing(lbl,60,79,prev_cav,4): add('cavaco',p,T(b,st),0.1,112,st)
                add('sopros',76,T(b,st),0.12,90) if False else None
# --- ending: final convenção and held chord at beat 276, nothing after except ring
END=276
for k in P:
    P[k]=[e for e in P[k] if e[1]<T(END)-0.02]
lbl='A'
for p in voicing(lbl,60,79,None,4): add('cavaco',p,T(END),0.2,115)
for p in voicing(lbl,52,74,None,4): add('pad',p,T(END),5.0,60)
for p in voicing(lbl,60,84,None,3): add('strings',p,T(END),5.0,70); add('sopros',p+12 if p<72 else p,T(END),1.2,108)
add('surdo',41,T(END),0.5,122); add('surdo',35,T(END),0.5,100); add('bass',33,T(END),2.5,112); add('pratos',49,T(END),4.0,115); add('violao',45,T(END),3.0,70)
# aplicar breques
for k in P:
    out=[]
    for p,t,d,v in P[k]:
        if any(a+0.03<t<b_-0.03 for a,b_ in BREQ): continue
        for a,b_ in BREQ:
            if t<=a+0.03 and t+d>a+0.03: d=max(0.05,min(d,a-t+0.18))
        out.append([p,t,d,v])
    P[k]=out
for a,b_ in BREQ:
    bi=int(np.argmin(np.abs(beats-a))); l=chord_at.get(bi,'A'); r_=rootnote(l)
    for p in voicing(l,60,79,None,4): add('cavaco',p,a,0.14,114,jit=0.002)
    for p in voicing(l,65,84,None,3): add('sopros',p,a,0.2,108,jit=0.002)
    add('surdo',41,a,0.3,120,jit=0.002); add('bass',r_,a,0.22,112,jit=0.002); add('pratos',55,a,0.6,80,jit=0.002)
    bj=int(np.argmin(np.abs(beats-b_))); l2=chord_at.get(bj,'A')
    add('pratos',49,b_,1.6,108,jit=0.002); add('surdo',35,b_,0.3,100,jit=0.002)
    for p in voicing(l2,65,84,None,3): add('sopros',p,b_,0.16,100,jit=0.002)
# stops
for k in P:
    out=[]
    for p,t,d,v in P[k]:
        if any(a-0.02<=t<b for a,b in STOPS): continue
        for a,b in STOPS:
            if t<a<t+d: d=max(0.03,a-t-0.01)
        out.append([p,t,d,v])
    P[k]=out
np.save(f'{R}/parts.npy',np.array([P],dtype=object),allow_pickle=True)
print({k:len(v) for k,v in P.items()})
