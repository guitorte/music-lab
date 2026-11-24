# v3: base original (Suno) até o refrão + camadas MIDI do pré-refrão v2 por cima; do refrão em diante, v2 idêntica
import numpy as np, soundfile as sf, glob, pyloudnorm as pyln
from scipy import signal
fs=44100; R='/home/claude/rw2'; mt=pyln.Meter(fs)
c=np.load(f'{R}/components.npy',allow_pickle=True)[0]; P=c['P']; wet=c['wet']; voc=c['voc']; G=c['G']; N=len(voc)
orig=sum(sf.read(glob.glob(f'/home/claude/ai2/stems/{n}*.flac')[0])[0] for n in ['drums','bass','guitar','piano','other'])[:N]
k=c['vg_base']*10**(c['gdb'][int(15*fs)]/20)            # mesmo ganho da voz nos versos -> equilíbrio original do Suno
t=np.arange(N)/fs; PRE0,CUT=31.98,44.80
def win(a,b,fi=0.03,fo=0.015): return np.clip((t-a)/fi,0,1)*np.clip((b-t)/fo,0,1)
# base original até a parada, subindo +1,5 dB ao longo do pré
ramp=10**((1.5*np.clip((t-PRE0)/(CUT-PRE0),0,1))/20)
base=orig*k*(ramp*win(-1,CUT))[:,None]
# camadas do pré v2 por cima (acelerada): surdo, percussão, baixo, cavaco, cordas + reverb delas
H_=[ 'surdo','percussao','baixo','cavaco','cordas']
rng=np.random.default_rng(3)
L_=int(1.4*fs); tt=np.arange(L_)/fs; h=rng.standard_normal((L_,2))*np.exp(-6.9*tt/1.4)[:,None]
h=signal.sosfilt(signal.butter(2,[300,7000],'bandpass',fs=fs,output='sos'),h,axis=0); h/=np.sqrt((h**2).sum(0))
pre_layers=sum(P[n] for n in H_)
pw=P['cavaco']*0.5+P['cordas']; pw=np.stack([signal.fftconvolve(pw[:,i],h[:,i])[:N] for i in range(2)],1)*10**(-14/20)
pre=(pre_layers+pw)*win(PRE0,CUT)[:,None]
# do refrão em diante: banda v2 inteira
v2band=(sum(P.values())+wet)*np.clip((t-CUT)/0.015,0,1)[:,None]
band=base+pre+v2band
# voz: automação da v2; no pré recalcula para ficar ~0,5 LU abaixo da banda nova
i0,i1=int(32.4*fs),int(44.2*fs); Lb=mt.integrated_loudness(band[i0:i1]); Lv=mt.integrated_loudness(voc[i0:i1])
gp=np.clip((Lb-0.5)-Lv,-2,4); g=np.ones(N); g[int(32.4*fs):int(44.25*fs)]=10**(gp/20)
from scipy.ndimage import uniform_filter1d
g=uniform_filter1d(g,size=int(0.25*fs)); vocx=voc*g[:,None]
print(f'pré: banda {Lb:.1f} voz {Lv:.1f} -> ajuste {gp:+.1f} dB')
mix=(band+vocx)*G; mix=signal.sosfiltfilt(signal.butter(4,16500,'lowpass',fs=fs,output='sos'),mix,axis=0)
sf.write(f'{R}/mix_v3.wav',mix,fs,subtype='FLOAT')
bb=band*G
for n,a,b in [('intro',1,10.5),('verso1',11,21.4),('verso2',21.8,32),('pré',33,44.7),('refrão',46.2,69.5)]:
    print(f'  banda {n:7s} {mt.integrated_loudness(bb[int(a*fs):int(b*fs)]):6.1f} LUFS')
