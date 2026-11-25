# Entrada do refrão: master v2 aprovada (original Suno) x versão Traição→Mente entregue — mesmas medidas, mesma linha do tempo
import numpy as np, soundfile as sf, scipy.signal as ss
B=np.load('/home/claude/vt/w/analysis.npz')['beats']
def bands(f):
    x,fs=sf.read(f,always_2d=True); m=x.mean(1); bp=lambda lo,hi: ss.sosfiltfilt(ss.butter(4,[lo,hi] if lo else hi,btype='bandpass' if lo else 'lowpass',fs=fs,output='sos'),m)
    return m,bp(None,150),bp(6000,16000),bp(8000,16000),fs
db=lambda z,fs,a,c: 20*np.log10(np.sqrt((z[int(a*fs):int(c*fs)]**2).mean())+1e-9)
pk=lambda z,fs,a,c: 20*np.log10(np.abs(z[int(a*fs):int(c*fs)]).max()+1e-9)
V={'v2 aprovada (Suno)':'/tmp/mv2.wav','Traição→Mente entregue':'/home/claude/vt/Mente_Vit_Traicao_master_24bit.wav'}
per=float(np.median(np.diff(B)))
print(f'{"":26s} {"refrão":>7s} {"grave: 4 tempos antes":>22s} {"golpe grave t1":>15s} {"agudos salto":>13s} {"prato 0,5s":>11s} {"grave t1 - t2 no refrão":>24s}')
for nome,f in V.items():
    m,lo,hi,cy,fs=bands(f)
    for cb in (64,148):
        t=B[cb]
        pre=db(lo,fs,t-4*per,t)-db(lo,fs,t+1,t+9)                          # grave nos 4 tempos antes, rel. ao refrão
        g=pk(lo,fs,t-0.02,t+0.15)-db(lo,fs,t+1,t+9)
        j=db(hi,fs,t,t+2*per)-db(hi,fs,t-2*per,t)
        c=db(cy,fs,t,t+0.5)-db(cy,fs,t+1,t+9)
        bars=range(cb,cb+24,2); acc=np.mean([db(lo,fs,B[i],B[i]+0.25)-db(lo,fs,B[i+1],B[i+1]+0.25) for i in bars])
        print(f'{nome:26s} {t:7.2f} {pre:+22.1f} {g:+15.1f} {j:+13.1f} {c:+11.1f} {acc:+24.1f}')
