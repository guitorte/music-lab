import mido
def ler(f):
    m=mido.MidiFile(f); tpb=m.ticks_per_beat; t=0; on={}; notes=[]; tempo=500000
    for tr in m.tracks:
        t=0
        for x in tr:
            t+=x.time
            if x.type=='set_tempo': tempo=x.tempo
            if x.type=='note_on' and x.velocity>0 and x.note>0: on.setdefault(x.note,[]).append(t)
            elif x.type in('note_off','note_on') and x.note>0 and on.get(x.note):
                s=on[x.note].pop(0); notes.append((s/tpb,(t-s)/tpb,x.note,x.velocity))
    notes.sort(); return notes, 60e6/tempo
