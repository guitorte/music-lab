# MIDI didático do groove de Traição (76 BPM, 2/4): agudos, médios e surdo, entrando em camadas
import sys, numpy as np, pretty_midi as pm, subprocess, soundfile as sf, scipy.signal as ss
BPM=76.0; B=60/BPM; S=B/4; OUT='/home/claude/ghost/groove_traicao'
V=eval(sys.argv[1]) if len(sys.argv)>1 else {'hi':[120,62,118,84],'mid':[120,66,106,113]}
DELAY={'hi':[0,0.008,0,0.003],'mid':[0,0,0.003,0.003]}       # microtempo medido (s)
HI,MID,SURDO=42,64,41                                            # chimbal fechado, conga grave, tom grave (GM)
m=pm.PrettyMIDI(initial_tempo=BPM)
tr={k:pm.Instrument(0,is_drum=True,name=n) for k,n in [('hi','Agudos (platinela, ganzá)'),('mid','Médios (tantã, couro do pandeiro)'),('su','Surdo')]}
for bar in range(16):                       # 1–4: só agudos; 5–8: + médios; 9–16: tudo
    for beat in range(2):
        t0=(bar*2+beat)*B
        for k,(lay,note) in enumerate([('hi',HI),('mid',MID)]):
            if lay=='mid' and bar<4: continue
            for s in range(4):
                t=t0+s*S+DELAY[lay][s]; tr[lay].notes.append(pm.Note(V[lay][s],note,t,t+0.06))
        if bar>=8:
            if beat==0: tr['su'].notes.append(pm.Note(72,SURDO,t0,t0+0.12))            # 1º tempo abafado
            else:
                tr['su'].notes.append(pm.Note(122,SURDO,t0,t0+0.45))                     # 2º tempo aberto
                tr['su'].notes.append(pm.Note(96,SURDO,t0+3*S,t0+3*S+0.15))              # puxada na 4ª
for k in ['hi','mid','su']: m.instruments.append(tr[k])
m.write(OUT+'.mid')
subprocess.run(['fluidsynth','-ni','-q','-g','0.8','-r','44100','-F',OUT+'.wav','/usr/share/sounds/sf2/FluidR3_GM.sf2',OUT+'.mid'],check=True)
# confere: perfil por semicolcheia de cada camada renderizada sozinha (compassos 1–4 = só agudos; 5–8 agudos+médios)
x,fs=sf.read(OUT+'.wav'); x=x.mean(1)
def perfil(a,b,lo,hi):
    y=ss.sosfiltfilt(ss.butter(4,[lo,hi],btype='bandpass',fs=fs,output='sos'),x); pk=[]
    for s in range(4):
        v=[np.abs(y[int((t+s*S)*fs):int((t+s*S+0.03)*fs)]).max() for t in np.arange(a,b,B)]; pk.append(np.median(v))
    pk=20*np.log10(np.array(pk)/max(pk)); return np.round(pk,1)
print('agudos (compassos 1–4) dB por 16ª:',perfil(0,8*B,6000,16000),' alvo [0, -10, 0, -6]')
print('médios (só conga: compassos 5–8, banda 150–600 Hz) dB:',perfil(8*B,16*B,150,600),' alvo [0, -9, -2, -1]')
