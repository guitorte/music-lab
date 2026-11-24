import numpy as np
exec(open('v8.py').read().split("out=mix.copy()")[0])
src=open('/home/claude/scripts/e3.py').read()
def shelf(f0,g,Q=0.707):
    A=10**(g/40); w=2*np.pi*f0/fs; c=np.cos(w); al=np.sin(w)/(2*Q); sA=2*np.sqrt(A)*al
    b=[A*((A+1)+(A-1)*c+sA),-2*A*((A-1)+(A+1)*c),A*((A+1)+(A-1)*c-sA)]; a=[(A+1)-(A-1)*c+sA,2*((A-1)-(A+1)*c),(A+1)-(A-1)*c-sA]
    return np.array(b)/a[0],np.array(a)/a[0]
out=np.load(D+'out1.npy')
for name,W0,yr,yn in P:
    if name!='cara': continue
    A0,A1,B0,B1=R[name]; s=slice(int(W0*fs),int(W0*fs)+len(yr)); tl=W0+np.arange(len(yr))/fs
    w=np.clip((tl-A0)/(A1-A0),0,1); w=np.minimum(w,np.clip((B1-tl)/(B1-B0),0,1)); w=(0.5-0.5*np.cos(np.pi*w))[:,None]
    seg=lambda z: z[int((A1-W0)*fs):int((B0-W0)*fs)]; L0=m.integrated_loudness(seg(mix[s]))
    for sh in (2.0,3.0):
        b,a=shelf(4000,sh); yn2=signal.filtfilt(b,a,yn,axis=0)
        best=None
        for g in np.arange(-1,3.01,0.25):
            o=mix[s]*(1-w)+(yr+yn2*10**(g/20))*w; d=m.integrated_loudness(seg(o))-L0
            if best is None or abs(d)<abs(best[1]): best=(g,d,o)
        g,d,o=best; t=out.copy(); t[s]=o
        bands=' '.join(f'{lo}-{hi}:{band(t,A1,B0,lo,hi)-band(mix,A1,B0,lo,hi):+.1f}' for lo,hi in [(60,200),(200,1000),(1000,4000),(4000,12000)])
        print(f'shelf +{sh}: gain {g:+.2f} -> {d:+.2f} LU | {bands}')
        if sh==3.0: out=t
up=signal.resample_poly(out,4,1,axis=0); print('TP %.2f'%(20*np.log10(np.abs(up).max())))
np.save(D+'out2.npy',out)
