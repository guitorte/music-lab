# compara tempos de palavra (whisper vs WhisperX) contra os ataques reais da voz
import json, numpy as np, soundfile as sf, librosa
R='/home/claude/vit'
A=json.load(open(f'{R}/w/whisper.json'))['words']; B=json.load(open(f'{R}/w/whisperx.json'))['words']
v,fs=sf.read(f'{R}/stems_zip/vit live mast - vocals.flac'); vm=v.mean(1)
h=int(0.005*fs); k=len(vm)//h
e=20*np.log10(np.sqrt((vm[:k*h].reshape(k,h)**2).mean(1))+1e-9)
e=np.convolve(e,np.ones(3)/3,'same')
th=np.percentile(e[e>-80],50)-15   # limiar de "voz presente"
on=e>th
# ataques após pausa: >=150 ms abaixo do limiar e depois >=60 ms acima
att=[]
i=30
while i<k-12:
    if on[i] and not on[i-30:i].any() and on[i:i+12].all(): att.append(i*h/fs); i+=30
    else: i+=1
att=np.array(att)
fl=librosa.onset.onset_detect(y=vm.astype(np.float32),sr=fs,hop_length=256,units='time',backtrack=True)
def stats(W,ref,tol):
    d=[]
    for s,_,w in W:
        j=np.argmin(abs(ref-s)); 
        if abs(ref[j]-s)<tol: d.append(s-ref[j])
    d=np.array(d); return len(d), np.median(abs(d))*1000, np.percentile(abs(d),90)*1000, np.median(d)*1000
# só palavras que começam frase (ataque após pausa), casando pela palavra do whisper
print(f'ataques após pausa detectados: {len(att)}')
for nm,W in [('whisper',A),('WhisperX',B)]:
    st=np.array([w[0] for w in W]); d=np.array([st[np.argmin(abs(st-a))]-a for a in att]); d=d[abs(d)<0.5]
    print(f'{nm:9s} início de frase (1 palavra por ataque): n={len(d):2d}  erro mediano {np.median(abs(d))*1000:4.0f} ms  p90 {np.percentile(abs(d),90)*1000:4.0f} ms  viés {np.median(d)*1000:+4.0f} ms')
for nm,W in [('whisper',A),('WhisperX',B)]:
    n,med,p90,bias=stats(W,fl,0.15)
    print(f'{nm:9s} todas (onset mais próximo): n={n:3d}  mediana {med:4.0f} ms  p90 {p90:4.0f} ms  viés {bias:+4.0f} ms')
# palavras dos breques
an=np.load(f'{R}/w/analysis.npz'); beats=an['beats']
def wt(W,word,near):
    c=[x for x in W if x[2].strip(',.').lower()==word and abs(x[0]-near)<2.5]; return min(c,key=lambda x:abs(x[0]-near))[0]
def q16(t):
    i=np.searchsorted(beats,t)-1; st=np.round((t-beats[i])/(beats[i+1]-beats[i])*4)/4; return beats[i]+st*(beats[i+1]-beats[i])
P=[('sou',57.1,'o',57.6),('sou',78.0,'o',78.7),('sabe',105.9,'amo',106.5),('sou',113.7,'o',114.2),('sabe',130.1,'amo',130.8),('sou',137.9,'o',138.4),('diz',158.4,'o',159.5)]
print('\nbreques: palavra  whisper  WhisperX  onset | volta da banda (16ª) whisper vs WhisperX')
for a,na,b,nb in P:
    ta,xa=wt(A,a,na),wt(B,a,na); tb,xb=wt(A,b,nb),wt(B,b,nb)
    ra=fl[np.argmin(abs(fl-xa))]; rb=fl[np.argmin(abs(fl-xb))]
    print(f'  {a:5s} {ta:7.2f} {xa:8.2f} {ra:8.2f}   {b:4s} {tb:7.2f} {xb:8.2f} {rb:8.2f} | {q16(tb-0.02):7.2f} {q16(xb-0.02):7.2f}')
