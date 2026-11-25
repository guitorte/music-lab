# Entrada do refrão: golpe no tempo 1, salto de agudos, prato e peso da percussão — nova x v3 da Vit x Traição
import numpy as np, soundfile as sf, scipy.signal as ss, glob
def ld(f): x,fs=sf.read(f,always_2d=True); return x.mean(1),fs
def bp(x,fs,lo,hi): return ss.sosfiltfilt(ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'),x)
def rms(x,fs,a,b): return 20*np.log10(np.sqrt((x[int(a*fs):int(b*fs)]**2).mean())+1e-9)
def pk(x,fs,a,b): return 20*np.log10(np.abs(x[int(a*fs):int(b*fs)]).max()+1e-9)
tr=[sf.read(f,always_2d=True)[0] for f in sorted(glob.glob('/home/claude/traicao/stems/*.flac'))]; L=min(len(s) for s in tr)
trm=sum(s[:L] for s in tr).mean(1); trd=sf.read('/home/claude/traicao/stems/drums (3).flac')[0].mean(1)
C=[('Nova (Traição→Mente) master','/home/claude/vt/Mente_Vit_Traicao_master_24bit.wav',[44.47,101.09],0.674),
   ('Vit v3 anterior master','/home/claude/vit/Mente_Vit_arranjo_master_v3_24bit.wav',[44.6,101.2],0.674),
   ('Traição (mix dos stems)',None,[52.81,131.9],0.79)]
print(f'{"":30s} {"golpe grave 1º tempo":>20s} {"agudos: salto":>14s} {"prato 8–16k 1ª 0,5s":>20s} {"agudos refrão rel. mix":>22s}')
for nome,f,ts,beat in C:
    if f: x,fs=ld(f)
    else: x,fs=trm/np.abs(trm).max()*10**(-1/20),44100
    lo=bp(x,fs,None,150); hi=bp(x,fs,6000,16000); cym=bp(x,fs,8000,16000)
    for t in ts:
        g=pk(lo,fs,t-0.02,t+0.12)-rms(lo,fs,t+1,t+9)          # golpe grave do tempo 1 vs grave médio do refrão
        j=rms(hi,fs,t,t+2*beat)-rms(hi,fs,t-2*beat,t)          # agudos: 1º compasso do refrão vs último compasso antes
        c=rms(cym,fs,t,t+0.5)-rms(cym,fs,t+1,t+9)              # prato: 1ª meia-segundo vs média do refrão
        h=rms(hi,fs,t+1,t+15)-rms(x,fs,t+1,t+15)               # quanto de agudo (percussão) há no refrão
        print(f'{nome[:24]+" @"+str(round(t,1)):30s} {g:+20.1f} {j:+14.1f} {c:+20.1f} {h:+22.1f}')
