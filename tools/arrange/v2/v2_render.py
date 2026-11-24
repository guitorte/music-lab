import numpy as np, mido, subprocess, soundfile as sf
parts=np.load('/home/claude/rw2/parts.npy',allow_pickle=True)[0]; A=np.load('/home/claude/rw2/analysis.npz'); beats=A['beats']
PPQ=480; grid=np.r_[0.0,beats] if beats[0]>0.02 else beats
def s2t(t):
    if t<=grid[0]: return 0
    if t>=grid[-1]: per=grid[-1]-grid[-2]; return int(round(((len(grid)-1)+(t-grid[-1])/per)*PPQ))
    i=min(np.searchsorted(grid,t)-1,len(grid)-2); return int(round((i+(t-grid[i])/(grid[i+1]-grid[i]))*PPQ))
def tempo_track():
    tr=mido.MidiTrack(); tr.append(mido.MetaMessage('time_signature',numerator=4,denominator=4,time=0)); last=0
    for i in range(len(grid)-1): tick=i*PPQ; tr.append(mido.MetaMessage('set_tempo',tempo=int(round((grid[i+1]-grid[i])*1e6)),time=tick-last)); last=tick
    tr.append(mido.MetaMessage('end_of_track',time=0)); return tr
GROUPS={'surdo':(['surdo'],9,0),'percussao':(['tanta','pandeiro','tamborim','repique','ganza','aro'],9,0),'pratos':(['pratos','palmas'],9,0),
 'baixo':(['bass'],0,33),'cavaco':(['cavaco'],1,25),'violao':(['violao'],2,24),'pad':(['pad'],3,89),'epiano':(['epiano'],4,4),'cordas':(['strings'],5,48),
 'sopros':(['sopros'],6,61),'sax':(['sax'],7,65)}
def track(name,keys,chn,prog):
    tr=mido.MidiTrack(); tr.append(mido.MetaMessage('track_name',name=name,time=0)); tr.append(mido.Message('program_change',program=prog,channel=chn,time=0))
    ev=[]
    for k in keys:
        for p,t,d,v in parts[k]:
            ev.append((s2t(t),1,mido.Message('note_on',note=int(p),velocity=int(v),channel=chn))); ev.append((s2t(t+d),0,mido.Message('note_off',note=int(p),velocity=0,channel=chn)))
    ev.sort(key=lambda e:(e[0],e[1])); lt=0
    for t,_,m in ev: m.time=t-lt; tr.append(m); lt=t
    tr.append(mido.MetaMessage('end_of_track',time=0)); return tr
full=mido.MidiFile(ticks_per_beat=PPQ); full.tracks.append(tempo_track())
import sys
ONLY=sys.argv[1:]
for name,(keys,chn,prog) in GROUPS.items():
    full.tracks.append(track(name,keys,chn,prog))
    if ONLY and name not in ONLY: continue
    one=mido.MidiFile(ticks_per_beat=PPQ); one.tracks.append(tempo_track()); one.tracks.append(track(name,keys,chn,prog)); one.save(f'/home/claude/rw2/{name}.mid')
    subprocess.run(['fluidsynth','-ni','-q','-g','0.5','-r','44100','-F',f'/home/claude/rw2/{name}.wav','/usr/share/sounds/sf2/FluidR3_GM.sf2',f'/home/claude/rw2/{name}.mid'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    z,fs=sf.read(f'/home/claude/rw2/{name}.wav'); print(f'{name}: {len(z)/fs:.1f}s peak {20*np.log10(np.abs(z).max()+1e-12):.1f} dBFS')
full.save('/home/claude/rw2/Mente_arranjo_v2.mid'); print('saved full MIDI')
