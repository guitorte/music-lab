import numpy as np, pretty_midi, glob
def stats(f,a=8,b=182):
    pm=pretty_midi.PrettyMIDI(f); ns=[n for i in pm.instruments for n in i.notes if a<=n.start<b]
    if not ns: return None
    st=np.array([n.start for n in ns]); en=np.array([n.end for n in ns]); dur=en-st; o=np.argsort(st); st,en,dur=st[o],en[o],dur[o]
    fr=np.zeros(int((b-a)/0.01)); 
    for s,e in zip(st,en): fr[int((s-a)/0.01):int((min(e,b)-a)/0.01)]+=1
    # gap to next onset relative to note length (legato <=0 means overlaps/connected)
    nxt=np.r_[st[1:],np.nan]; gap=nxt-en
    return dict(nps=len(ns)/(b-a), dur=np.median(dur)*1000, short=(dur<0.08).mean()*100, cover=(fr>0).mean()*100, poly=fr[fr>0].mean(), legato=(gap<=0.03).mean()*100, gapmed=np.nanmedian(np.clip(gap,0,None))*1000)
print('instrument  version | notes/s  median dur  notes<80ms  time covered  polyphony  legato(next note within 30ms)  median gap')
for inst in ['bass','guitar','piano','other','vocals']:
    for lab,d in [('REAL','/home/claude/ref/midi'),('AI','/home/claude/ai2/other')]:
        f=glob.glob(f'{d}/bs_roformer_sw__basic_pitch__{inst}*.mid')[0]; s=stats(f)
        print(f'{inst:9s} {lab:5s} | {s["nps"]:6.1f} {s["dur"]:9.0f} ms {s["short"]:9.0f}% {s["cover"]:12.0f}% {s["poly"]:10.2f} {s["legato"]:20.0f}% {s["gapmed"]:16.0f} ms')
