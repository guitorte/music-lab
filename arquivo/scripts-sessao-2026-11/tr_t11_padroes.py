# Padrões de Traição por instrumento e por estado (leve / pré / cheio), num compasso de 2/4 = 8 semicolcheias
import numpy as np, pretty_midi as pm, glob, json
beats=np.load('/home/claude/traicao/beats.npy'); D='/home/claude/traicao/midi/'
EST={'leve':[(22.8,40.1)],'pre':[(40.1,46.4)],'cheio':[(52.7,101.5),(108,123.5),(131.9,180)],'abertura':[(1.7,22.8)]}
def notes(stem): return [x for i in pm.PrettyMIDI(glob.glob(D+f'bs_roformer_sw__basic_pitch__{stem}*.mid')[0]).instruments for x in i.notes]
def slot(t):
    i=np.searchsorted(beats,t)-1
    if i<0 or i>=len(beats)-1: return None
    s=int(round((t-beats[i])/(beats[i+1]-beats[i])*4)); 
    if s==4: i+=1; s=0
    bar=i//2; return bar,(i%2)*4+s
def est(t):
    for k,v in EST.items():
        if any(a<=t<b for a,b in v): return k
def stats(stem,lo=0,hi=200,minvel=0):
    N=[x for x in notes(stem) if lo<=x.pitch<hi and x.velocity>=minvel]; out={}
    for e in EST:
        bars={}
        for x in N:
            if est(x.start)!=e: continue
            r=slot(x.start)
            if r: bars.setdefault(r[0],[]).append((r[1],x.pitch,x.end-x.start,x.velocity))
        if not bars: continue
        nb=sum(int((b-a)/(beats[1]-beats[0])/2) for a,b in EST[e])
        pres=np.zeros(8); dur=[[] for _ in range(8)]; poly=[]
        for bar,L in bars.items():
            for s in set(l[0] for l in L): pres[s]+=1
            for s,p,d,v in L: dur[s].append(d/((beats[1]-beats[0])/4))
            poly.append(len(L)/max(1,len(set(l[0] for l in L))))
        out[e]=dict(pres=np.round(100*pres/nb).astype(int).tolist(),dur16=[round(float(np.median(d)),1) if d else 0 for d in dur],notas_por_golpe=round(float(np.mean(poly)),1),compassos=nb)
    return out
R={'baixo':stats('bass',0,60),'cavaco(>=D4)':stats('guitar',62,100),'violão(<D4)':stats('guitar',36,62),'teclado':stats('piano'),'outros':stats('other')}
for k,v in R.items():
    print('\n==',k)
    for e,d in v.items(): print(f'  {e:8s} presença% por 16ª {d["pres"]}  dur(16ªs) {d["dur16"]}  notas/golpe {d["notas_por_golpe"]}')
# baixo: função das notas em relação à fundamental do compasso (nota mais longa+grave do compasso)
N=[x for x in notes('bass') if x.pitch<60]; bars={}
for x in N:
    if est(x.start)!='cheio': continue
    r=slot(x.start)
    if r: bars.setdefault(r[0],[]).append((r[1],x.pitch,x.end-x.start))
fun=[{} for _ in range(8)]; nxt=[]
keys=sorted(bars)
for b in keys:
    L=sorted(bars[b]); root=min(L,key=lambda l:(l[0],-l[2]))[1]%12
    for s,p,d in L:
        iv=(p-root)%12; fun[s][iv]=fun[s].get(iv,0)+1
print('\nbaixo (cheio): intervalo em relação à nota do 1º tempo, por 16ª (mais comuns):')
nm={0:'1',7:'5',5:'4',2:'2',10:'b7',3:'b3',4:'3',9:'6',11:'7',1:'b2',8:'b6',6:'#4'}
for s in range(8):
    t=sum(fun[s].values()); top=sorted(fun[s].items(),key=lambda kv:-kv[1])[:3]
    print(f'  16ª {s+1}: n={t:3d} '+', '.join(f'{nm[i]} {100*c//max(t,1)}%' for i,c in top))
json.dump(R,open('/home/claude/traicao/padroes.json','w'),ensure_ascii=False,indent=1)
