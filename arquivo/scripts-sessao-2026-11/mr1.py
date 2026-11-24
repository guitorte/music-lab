import mido, subprocess, numpy as np, soundfile as sf, pyloudnorm as pyln
src=mido.MidiFile('/home/claude/md/Soap_Opera_Thing_MIDI_groove.mid'); tempo_track=src.tracks[0]
names={i:next((m.name for m in t if m.type=='track_name'),'') for i,t in enumerate(src.tracks)}
print(names)
keep={'drums':None,'bass':None,'guitar':24,'piano':None}
for i,t in enumerate(src.tracks[1:],1):
    key=next((k for k in keep if names[i].lower().startswith(k)),None)
    if key is None: continue
    mf=mido.MidiFile(ticks_per_beat=src.ticks_per_beat); mf.tracks.append(tempo_track)
    nt=mido.MidiTrack()
    for m in t:
        if m.type=='program_change' and keep[key] is not None: m=m.copy(program=keep[key])
        nt.append(m)
    mf.tracks.append(nt); p=f'/home/claude/mr/{key}.mid'; mf.save(p)
    subprocess.run(['fluidsynth','-ni','-q','-g','0.5','-r','48000','-F',f'/home/claude/mr/{key}.wav','/usr/share/sounds/sf2/FluidR3_GM.sf2',p],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    z,fs=sf.read(f'/home/claude/mr/{key}.wav'); print(f'{key}: rendered {len(z)/fs:.1f}s fs {fs} peak {20*np.log10(np.abs(z).max()+1e-12):.1f} dBFS')
