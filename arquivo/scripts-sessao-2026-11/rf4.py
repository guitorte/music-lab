import pretty_midi, glob, os, numpy as np, mido
for f in sorted(glob.glob('/home/claude/ref/midi/*.mid')):
    pm=pretty_midi.PrettyMIDI(f); mf=mido.MidiFile(f)
    tempos=pm.get_tempo_changes()[1]; ts=[(t.numerator,t.denominator) for t in pm.time_signature_changes]
    print(f'== {os.path.basename(f)}  ppq {mf.ticks_per_beat} tempo {np.round(tempos[:3],2)} ts {ts[:2]} end {pm.get_end_time():.1f}s')
    for ins in pm.instruments:
        if not ins.notes: continue
        v=np.array([n.velocity for n in ins.notes]); d=np.array([n.end-n.start for n in ins.notes]); p=np.array([n.pitch for n in ins.notes])
        print(f'   [{ins.name[:28]:28s}] drum={ins.is_drum} prog={ins.program:3d} notes={len(v):5d} pitch {p.min()}-{p.max()} vel uniq={len(np.unique(v)):3d} mean {v.mean():5.1f} std {v.std():4.1f} | dur median {np.median(d)*1000:5.0f} ms uniq {len(np.unique(np.round(d,3)))}')
