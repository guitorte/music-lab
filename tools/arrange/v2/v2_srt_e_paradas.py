import numpy as np, soundfile as sf, glob, re, json
from scipy.ndimage import median_filter
srt=open('/mnt/user-data/uploads/e3312926-ai_studio_code.txt').read().replace('00:01:00:50,800','00:01:50,800')
def ts(s): h,m,r=s.split(':'); sec,ms=r.split(','); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
L=[]
for blk in srt.strip().split('\n\n'):
    ln=blk.strip().split('\n'); a,b=[ts(t.strip()) for t in ln[1].split('-->')]; L.append((a,b,' '.join(ln[2:])))
json.dump(L,open('/home/claude/rw2/srt.json','w'),ensure_ascii=False)
fs=44100; S={n:sf.read(glob.glob(f'/home/claude/ai2/stems/{n}*.flac')[0])[0] for n in ['drums','bass','guitar','piano','other']}
band=sum(S.values()); w=int(0.05*fs); k=len(band)//w; E=20*np.log10(np.sqrt((band[:k*w].reshape(k,w,2)**2).mean((1,2)))+1e-9)
med=median_filter(E,size=61); q=E<med-10
runs=[];i=0
while i<k:
    if q[i]:
        j=i
        while j<k and q[j]: j+=1
        if j-i>=2: runs.append((i*0.05,j*0.05,float((med[i:j]-E[i:j]).mean())))
        i=j
    else: i+=1
A=np.load('/home/claude/rw/analysis.npz'); beats=A['beats']
def lyric(t):
    for a,b,s in L:
        if a-0.3<=t<=b+0.3: return s
    return '-'
for a,b,dd in runs:
    if 8<a<186:
        ib=np.argmin(np.abs(beats-a)); print(f'dip {a:6.2f}-{b:6.2f} ({(b-a)*1000:4.0f} ms, -{dd:4.1f} dB) beat#{ib} ph{ib%4} | {lyric(a)}')
