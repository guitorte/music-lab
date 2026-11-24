import numpy as np, mido
rng=np.random.default_rng(11)
A=np.load('/home/claude/rw/analysis.npz'); beats=A['beats']; C=np.load('/home/claude/rw/chords.npz'); ch=C['ch']; seg=C['seg']
NB=len(beats); per=np.median(np.diff(beats))
def T(b,step=0):  # time of beat index b + 16th step (0-3, may exceed)
    b=b+step//4; s=step%4
    if b>=NB-1: base=beats[-1]+(b-(NB-1))*per; return base+s*per/4
    return beats[b]+s*(beats[b+1]-beats[b])/4
TMPL=np.array([1.00,0.23,0.99,0.59]); MICRO=[0.0,0.006,0.0,0.003]
STOPS=[(45.40,46.05),(47.75,48.15),(99.05,99.50),(104.30,104.80)]
SEC=[('intro',0,17),('verse',17,49),('pre',49,68),('chorus',68,125),('break',125,141),('pre',141,158),('chorus',158,258),('outro',258,NB-1)]
def sec_of(b):
    for n,a,c in SEC:
        if a<=b<c: return n
    return 'outro'
ENER={'intro':0.45,'verse':0.65,'pre':0.8,'chorus':1.0,'break':0.5,'outro':0.75}
names='C C# D D# E F F# G G# A A# B'.split()
def parse(lbl):
    r=names.index(lbl[:2]) if lbl[:2] in names else names.index(lbl[0]); q=lbl[len(names[r]):]
    iv={'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10]}[q]; return r,iv
chord_at={}
for k,(a,b) in enumerate(seg):
    for bb in range(a,b): chord_at[bb]=ch[k]
parts={k:[] for k in ['surdo','tanta','pandeiro','tamborim','repique','ganza','bass','cavaco','violao','pad','epiano','strings']}
def add(part,pitch,t,dur,vel,stepslot=None):
    if stepslot is not None: t+=MICRO[stepslot]
    t+=rng.normal(0,0.004); vel=int(np.clip(vel+rng.normal(0,5),12,127))
    parts[part].append([pitch,max(0.0,t),max(0.03,dur),vel])
def voicing(lbl,lo,hi,prev=None,n=4):
    r,iv=parse(lbl); pcs=[(r+i)%12 for i in iv]
    cands=[]
    for base in range(lo,hi):
        if base%12 in pcs:
            v=[base]; 
            for p in pcs:
                pass
    # build close voicings starting from each chord tone as bottom
    opts=[]
    for bottom in range(lo,lo+12):
        if bottom%12 not in pcs: continue
        v=[bottom]; x=bottom
        while len(v)<n:
            x+=1
            if x%12 in pcs and x not in v: v.append(x)
        if v[-1]<=hi: opts.append(v)
    if not opts: opts=[[lo+((p-lo)%12) for p in pcs][:n]]
    if prev is None: return opts[len(opts)//2]
    return min(opts,key=lambda v: sum(min(abs(a-b) for b in prev) for a in v))
tamb_pat=[1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,0]
prev_cav=prev_pad=prev_ep=None
for b in range(NB-1):
    s=sec_of(b); E=ENER[s]; lbl=chord_at.get(b,ch[-1]); r,iv=parse(lbl); strong=(b%2==0); barpos=b%4
    seg_start=(b%2==0)
    # ---------- percussion
    if s!='intro':
        add('surdo',41,T(b),0.3,(112 if strong else 58)*E**0.5)
        if strong and s in ('chorus','pre'): add('surdo',35,T(b),0.3,70*E)
        if not strong and s in ('chorus','pre'): add('surdo',41,T(b,3),0.15,55*E,3)
    for k in range(4):
        a=TMPL[k]
        if s not in ('intro',):
            add('tanta',[64,62,63,64][k],T(b,k),0.12,(30+80*a)*E,k)
            add('pandeiro',54,T(b,k),0.1,(28+82*a)*E,k)
        if s in ('pre','chorus','outro') or (s in ('verse','intro','break') and k%2==0):
            add('ganza',70,T(b,k),0.08,(35+40*a)*E*(0.7 if s in ('intro','verse','break') else 1),k)
    if s=='chorus':
        for k in range(4):
            st=(b%4)*4+k
            if tamb_pat[st]: add('tamborim',76,T(b,k),0.08,(55+45*TMPL[k]),k)
        if b%4 in (1,3):
            for k,p,v in [(1,65,70),(3,66,85)]: add('repique',p,T(b,k),0.1,v,k)
    # ---------- bass (pagode: root, anticipated 5th, octave/root, approach to next chord)
    if s!='intro':
        root=28+((r-4)%12)   # E1..D#2
        nxt=chord_at.get(b+2,lbl); nr,_=parse(nxt); nroot=28+((nr-4)%12)
        fifth=root+7 if root+7<=52 else root-5
        if seg_start:
            add('bass',root,T(b,0),per*0.7,100*E**0.4,0)
            add('bass',fifth,T(b,3),per*0.22,70*E**0.4,3)
        else:
            add('bass',root+12 if s=='chorus' and root+12<=55 else root,T(b,0),per*0.45,85*E**0.4,0)
            if s in ('chorus','pre','outro'):
                appr=nroot-1 if nroot>root else nroot+2
                add('bass',appr,T(b,2),per*0.4,78*E**0.4,2)
            else: add('bass',root,T(b,2),per*0.4,70*E**0.4,2)
    # ---------- cavaco (16th chops, short), from verse on
    if s!='intro':
        v=voicing(lbl,62,82,prev_cav,4); prev_cav=v
        for k in range(4):
            vel=(30+85*TMPL[k])*(E if s!='break' else 0.5)
            if s=='break' and k%2: continue
            for p in v: add('cavaco',p,T(b,k),0.07 if k!=2 else 0.12,vel,k)
    # ---------- violao (nylon, arpeggio 8ths)
    v2=voicing(lbl,47,68,None,4)
    for j,p in enumerate([v2[0],v2[2],v2[1],v2[3]][:2] if True else []):
        add('violao',p,T(b,2*j),per*0.6,(55+20*(j==0))*max(E,0.6),2*j)
    # ---------- pad (sustained), every chord segment
    if seg_start or b==0:
        v=voicing(lbl,52,74,prev_pad,4); prev_pad=v
        for p in v: add('pad',p,T(b),2*per*0.98,(42 if s in ('intro','verse','break') else 50))
    # ---------- e-piano comping (choruses): anticipations on 'e' of 1 and '&' of 2
    if s=='chorus' and seg_start:
        v=voicing(lbl,55,76,prev_ep,4); prev_ep=v
        for st,vel in [(1,62),(6,74)]:
            for p in v: add('epiano',p,T(b,st),per*0.35,vel,st%4)
    # ---------- strings in choruses (soft, sustained)
    if s=='chorus' and seg_start:
        v=voicing(lbl,60,84,None,3)
        for p in v: add('strings',p,T(b),2*per*0.98,48)
# ---------- stops: cut everything inside stop windows
for k in parts:
    out=[]
    for p,t,d,v in parts[k]:
        bad=any(a-0.02<=t<b for a,b in STOPS)
        if bad: continue
        for a,b in STOPS:
            if t<a<t+d: d=max(0.03,a-t-0.01)
        out.append([p,t,d,v])
    parts[k]=out
# end hit after last stop before chorus landing (keep groove); final crash-less ending handled by fade
np.save('/home/claude/rw/parts.npy',np.array([parts],dtype=object),allow_pickle=True)
print({k:len(v) for k,v in parts.items()})
