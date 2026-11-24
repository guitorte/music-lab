import numpy as np, soundfile as sf, pyloudnorm as pyln, sys
from scipy import signal
D='/home/claude/pg/w/'; names=['vocals','drums','bass','guitar','piano','other']
S={n:sf.read(D+n+'.wav')[0] for n in names}; fs=48000; n=min(len(v) for v in S.values()); S={k:v[:n] for k,v in S.items()}
t=np.arange(n)/fs
def bp(z,lo,hi,o=2):
    sos=signal.butter(o,[lo,hi],'bandpass',fs=fs,output='sos') if lo else signal.butter(o,hi,'lowpass',fs=fs,output='sos')
    return signal.sosfiltfilt(sos,z,axis=0)
def env(x,att,rel):
    # one-pole peak follower on |x| (mono), samples
    a=np.exp(-1/(att*fs)); r=np.exp(-1/(rel*fs)); y=np.zeros_like(x); e=0.0
    for i in range(len(x)):
        v=x[i]; c=a if v>e else r; e=c*e+(1-c)*v; y[i]=e
    return y
from numba import njit
@njit
def _env(x,a,r):
    y=np.empty_like(x); e=0.0
    for i in range(len(x)):
        v=x[i]
        c=a if v>e else r
        e=c*e+(1-c)*v; y[i]=e
    return y
def envf(x,att,rel): return _env(np.ascontiguousarray(x),np.exp(-1/(att*fs)),np.exp(-1/(rel*fs)))
def transient(z,lo,hi,att_db,sus_db,fast=(0.0005,0.02),slow=(0.02,0.2)):
    b=bp(z,lo,hi) if (lo or hi) else z; d=np.abs(b).max(1)+1e-9
    ef=envf(d,*fast); es=envf(d,*slow); diff=20*np.log10(ef+1e-9)-20*np.log10(es+1e-9)   # >0 at attacks
    g=np.where(diff>0, np.clip(diff/6,0,1)*att_db, 0.0)+np.where(diff<=0, np.clip(-diff/6,0,1)*sus_db, 0.0)
    g=envf(np.abs(g)*np.sign(g)+50,0.0003,0.01)-50 if False else g
    return z-b+b*10**(g/20)[:,None], g
def comp(z,thr_db,ratio,att,rel):
    d=np.abs(z).max(1)+1e-9; e=envf(d,att,rel); lv=20*np.log10(e); gr=np.clip((lv-thr_db)*(1-1/ratio),0,None); return z*10**(-gr/20)[:,None], gr
dr=S['drums'].copy()
# 1) surdo: more attack, shorter tail (45-120 Hz)
dr,g1=transient(dr,45,120,+2.5,-2.0)
# 2) high percussion (pandeiro, tanta slap, repique): snap
dr,g2=transient(dr,2000,12000,+4.0,0.0)
# 3) parallel compression on drums -> ghost notes / body (NY style), blended under
drh=signal.sosfiltfilt(signal.butter(2,150,'highpass',fs=fs,output='sos'),dr,axis=0)
pc,gr=comp(drh,np.percentile(20*np.log10(np.abs(dr).max(1)+1e-9),90)-12,4.0,0.003,0.08)
pc*=10**((np.median(gr[gr>0])-6)/20) if (gr>0).any() else 1
dr=dr+pc*0.75
print('drums: surdo attack max +%.1f / tail %.1f dB; perc attack max +%.1f dB; parallel comp GR median %.1f dB'%(g1.max(),g1.min(),g2.max(),np.median(gr[gr>0])))
# 4) cavaco/violao chops
gt,g3=transient(S['guitar'],1000,7000,+2.0,0.0)
# 5) bass +2 dB with light saturation (harmonics for small speakers), mono
bs=S['bass'].mean(1); k=3.0; sat=np.tanh(k*bs/np.abs(bs).max())/np.tanh(k)*np.abs(bs).max(); harm=signal.sosfiltfilt(signal.butter(4,150,'highpass',fs=fs,output='sos'),sat-bs); bs=bs+0.6*harm
bs=np.stack([bs,bs],1)*10**(2/20)
# 6) crowd/ambience ("other"): body -2 dB, side -4 dB; ending: down to -9 dB, side -8 dB, then fade
o=S['other']; Mo=o.mean(1); So=(o[:,0]-o[:,1])/2
end_w=np.clip((t-157.6)/1.6,0,1); end_w=0.5-0.5*np.cos(np.pi*end_w)
side_g=10**((-4-4*end_w)/20); lvl_g=10**((0-3.4*end_w)/20)
o=np.stack([Mo+So*side_g,Mo-So*side_g],1)*lvl_g[:,None]
fade=np.clip((n/fs-t)/3.0,0,1); fade=np.sin(fade*np.pi/2)**2
vo=S['vocals']*10**(1.1/20); pi=S['piano']
mix=(vo+dr+bs+gt+pi+o)*fade[:,None]
sf.write('/home/claude/pg/w/newmix_b.wav',mix,fs,subtype='FLOAT')
orig=sum(S.values())
m=pyln.Meter(fs)
def L(z,a,b): return m.integrated_loudness(z[int(a*fs):int(b*fs)])
print('loudness  orig sum: body %.1f | ending %.1f   new: body %.1f | ending %.1f'%(L(orig,12,158),L(orig,158.5,167),L(mix,12,158),L(mix,158.5,166)))
for nm,z in [('orig',orig),('new',mix)]:
    s=z[12*fs:158*fs]; print(f'{nm}: L/R corr body {np.corrcoef(*s.T)[0,1]:.2f}, ending {np.corrcoef(*z[int(158.5*fs):int(165*fs)].T)[0,1]:.2f}; mono loss body {10*np.log10((s.mean(1)**2).mean()/((s**2).mean()))+3.01:+.1f} dB')
rest_o=orig-S['vocals']; rest_n=mix/np.maximum(fade[:,None],1e-6)-vo
b=slice(12*fs,158*fs)
print('vocal minus rest of the band (body): orig %+.1f LU, new %+.1f LU'%(m.integrated_loudness(S['vocals'][b])-m.integrated_loudness(rest_o[b]),m.integrated_loudness(vo[b])-m.integrated_loudness(rest_n[b])))
def crest(z):
    d=z.mean(1); k=len(d)//(fs//10); r=d[:k*(fs//10)].reshape(k,-1); return np.median(20*np.log10(np.abs(r).max(1)/np.sqrt((r**2).mean(1))+1e-9))
print('drum stem: crest 100 ms orig %.1f new %.1f dB (attack)'%(crest(S['drums'][b]),crest(dr[b])))
q=S['drums'][b].mean(1); qn=dr[b].mean(1); w=int(0.01*fs); kk=len(q)//w
eo=20*np.log10(np.sqrt((q[:kk*w].reshape(kk,w)**2).mean(1))+1e-9); en=20*np.log10(np.sqrt((qn[:kk*w].reshape(kk,w)**2).mean(1))+1e-9)
print('drum ghost-note level (20th pct of 10 ms frames vs 95th): orig %.1f dB, new %.1f dB'%(np.percentile(eo,20)-np.percentile(eo,95),np.percentile(en,20)-np.percentile(en,95)))
