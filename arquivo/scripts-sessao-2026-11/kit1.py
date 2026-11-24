import numpy as np, mido, subprocess, soundfile as sf
rng=np.random.default_rng(7)
beats=np.load('/home/claude/mr/beats.npy'); nb=len(beats)
def t_of(i,frac=0.0):
    i=int(i); 
    if i>=nb-1: per=beats[-1]-beats[-2]; return beats[-1]+(i-(nb-1)+frac)*per
    return beats[i]+frac*(beats[i+1]-beats[i])
KICK,SNARE,XSTICK,HHC,HHO,CRASH,RIDE=36,38,37,42,46,49,51
notes=[]
def add(p,t,v,dur=0.08):
    v=int(np.clip(v+rng.normal(0,4),20,127)); t=t+rng.normal(0,0.003); notes.append((p,max(0,t),v,dur))
# sections in beat indices (bar "1" = surdo-strong landing beats are odd)
SEC=[('intro',0,17),('verse',17,47),('pre',47,64),('stop',64,65),('chorus',65,121),('post',121,140),('pre',140,156),('stop',156,157),('chorus',157,214),('outro',214,231)]
for name,a,b in SEC:
    for i in range(a,b):
        strong=(i%2==1)            # backbeat = strong surdo beat
        if name=='intro': continue
        if name=='verse':
            if not strong: add(KICK,t_of(i),68)
            else: add(XSTICK,t_of(i),62)
            add(HHC,t_of(i),48); add(HHC,t_of(i,0.5),36)
        elif name in ('pre','post','outro'):
            last_pre=(name=='pre' and i==b-1)
            if not strong: add(KICK,t_of(i),84); add(KICK,t_of(i,0.75),64)
            elif not last_pre: add(SNARE,t_of(i),84 if name!='pre' else 80+12*(i-a)/(b-a))
            if last_pre:   # fill: 16th snare crescendo into the stop
                for k,v in enumerate([70,82,94,108]): add(SNARE,t_of(i,k/4),v)
            else:
                add(HHC,t_of(i),58); add(HHC,t_of(i,0.5),46)
        elif name=='stop':
            add(KICK,t_of(i),112); add(SNARE,t_of(i),110); add(CRASH,t_of(i),96,0.3)
        elif name=='chorus':
            first=(i==a); add(KICK,t_of(i),114 if (not strong or first) else 0) if (not strong or first) else None
            if strong: add(SNARE,t_of(i),112); add(KICK,t_of(i,0.75),88) if False else None
            if not strong: add(KICK,t_of(i,0.75),90)
            if (i-a)%8==0: add(CRASH,t_of(i),110,0.4)
            add(HHC,t_of(i),80)
            if strong: add(HHO,t_of(i,0.5),78,0.18)
            else: add(HHC,t_of(i,0.5),66)
    if name=='chorus': add(CRASH,t_of(b),104,0.5)
add(CRASH,t_of(231),100,0.6); add(KICK,t_of(231),105)
notes=[n for n in notes if n[2]>20]; notes.sort(key=lambda q:q[1])
print('kit notes:',len(notes))
# write: kit-only midi (for rendering) and append track to the groove MIDI; ticks via the same beat tempo map
src=mido.MidiFile('/home/claude/md/Soap_Opera_Thing_MIDI_groove.mid'); PPQ=src.ticks_per_beat
grid=np.r_[0.0,beats] if beats[0]>0.05 else beats.copy()
def s2t(t):
    if t<=grid[0]: return 0
    if t>grid[-1]: per=grid[-1]-grid[-2]; return int(round(((len(grid)-1)+(t-grid[-1])/per)*PPQ))
    i=min(np.searchsorted(grid,t)-1,len(grid)-2); return int(round((i+(t-grid[i])/(grid[i+1]-grid[i]))*PPQ))
kt=mido.MidiTrack(); kt.append(mido.MetaMessage('track_name',name='drum kit (Power) - forca no refrao',time=0)); kt.append(mido.Message('program_change',program=16,channel=9,time=0))
ev=[]
for p,t,v,d in notes: ev.append((s2t(t),1,mido.Message('note_on',note=p,velocity=v,channel=9))); ev.append((s2t(t+d),0,mido.Message('note_off',note=p,velocity=0,channel=9)))
ev.sort(key=lambda e:(e[0],e[1])); lt=0
for t,_,m in ev: m.time=t-lt; kt.append(m); lt=t
kt.append(mido.MetaMessage('end_of_track',time=0))
k=mido.MidiFile(ticks_per_beat=PPQ); k.tracks.append(src.tracks[0]); k.tracks.append(kt); k.save('/home/claude/mr/kit.mid')
full=mido.MidiFile(ticks_per_beat=PPQ); [full.tracks.append(t) for t in src.tracks]; full.tracks.append(kt); full.save('/home/claude/mr/Soap_Opera_Thing_MIDI_groove_com_bateria.mid')
subprocess.run(['fluidsynth','-ni','-q','-g','0.5','-r','48000','-F','/home/claude/mr/kit.wav','/usr/share/sounds/sf2/FluidR3_GM.sf2','/home/claude/mr/kit.mid'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
z,fs=sf.read('/home/claude/mr/kit.wav'); print('kit render %.1fs peak %.1f dBFS'%(len(z)/fs,20*np.log10(np.abs(z).max())))
