import numpy as np
A=np.load('/home/claude/rw/analysis.npz'); beats=A['beats']; bc=A['bc']; broot=A['broot']
names='C C# D D# E F F# G G# A A# B'.split()
qual={'':[0,4,7],'m':[0,3,7],'7':[0,4,7,10],'m7':[0,3,7,10]}
T=[];lab=[];roots=[]
for r in range(12):
    for q,iv in qual.items():
        t=np.zeros(12); t[[(r+i)%12 for i in iv]]=1; t[r]+=0.5; T.append(t/np.linalg.norm(t)); lab.append(names[r]+q); roots.append(r)
T=np.array(T); roots=np.array(roots)
key=9  # A major
dia={(key+0)%12:'',(key+2)%12:'m',(key+4)%12:'m',(key+5)%12:'',(key+7)%12:'',(key+9)%12:'m'}
prior=np.array([0.06 if (roots[i] in dia and (lab[i][len(names[roots[i]]):] in (dia[roots[i]],dia[roots[i]]+'7' if dia[roots[i]]=='' else 'm7'))) else 0.0 for i in range(len(lab))])
# secondary dominants are common in pagode: E7, B7, F#7, C#7
for i,l in enumerate(lab):
    if l in ('E7','B7','F#7','C#7','A7'): prior[i]=0.04
seg=[(i,min(i+2,bc.shape[1])) for i in range(0,bc.shape[1],2)]
X=[];B=[]
for a,b in seg:
    v=bc[:,a:b].mean(1); X.append(v/(np.linalg.norm(v)+1e-9))
    br=[r for r in broot[a:b] if r>=0]; B.append(max(set(br),key=br.count) if br else -1)
X=np.array(X); E=X@T.T+prior[None,:]
for k,b in enumerate(B):
    if b>=0: E[k,roots==b]+=0.12
energy=np.array([bc[:,a:b].sum() for a,b in seg]); quiet=energy<np.percentile(energy,8)
# viterbi with switch penalty
P=0.08; n,K=E.shape; dp=E[0].copy(); bp=np.zeros((n,K),int)
for t in range(1,n):
    stay=dp; sw=dp.max()-P; choose=np.where(stay>=sw,np.arange(K),dp.argmax()); dp=np.maximum(stay,sw)+E[t]; bp[t]=choose
path=[int(dp.argmax())]
for t in range(n-1,0,-1): path.append(bp[t][path[-1]])
path=path[::-1]; ch=[lab[p] for p in path]
fit=np.array([E[k,path[k]]-prior[path[k]] for k in range(n)])
np.savez('/home/claude/rw/chords.npz',ch=np.array(ch),seg=np.array(seg),fit=fit,quiet=quiet)
print('mean template fit %.2f (1 = perfect)'%fit.mean())
line=[]
for k,(a,b) in enumerate(seg):
    if k%8==0: line.append(f'\n{beats[a]:6.1f}s |')
    line.append(f' {ch[k]:4s}')
print(''.join(line))
