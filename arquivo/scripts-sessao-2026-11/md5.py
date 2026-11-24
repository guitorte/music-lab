import numpy as np, soundfile as sf, librosa, pretty_midi, mido
from scipy import signal
W='/home/claude/pg/w/'; SRC='/home/claude/md/src/C_RoFormer_SW_Basic_Pitch_GAME_voz_ADT_STR_bateria (7).mid'
dr,fs=sf.read(W+'drums.wav'); vo,_=sf.read(W+'vocals.wav')
# --- beat grid from drums audio
sr=22050; yd=librosa.resample(dr.mean(1).astype(np.float32),orig_sr=fs,target_sr=sr)
_,beats=librosa.beat.beat_track(y=yd,sr=sr,hop_length=256,units='time',tightness=400,start_bpm=89)
# align grid to onsets (tracker sits ~40 ms late): shift beats by median offset of backtracked onsets to nearest beat
on=librosa.onset.onset_detect(y=yd,sr=sr,hop_length=64,units='time',backtrack=True,delta=0.15)
idx=np.clip(np.searchsorted(beats,on),1,len(beats)-1); near=np.where(np.abs(on-beats[idx-1])<np.abs(on-beats[idx]),beats[idx-1],beats[idx])
d=on-near; shift=np.median(d[np.abs(d)<0.08]); beats=beats+shift; print('beat grid shifted by %.1f ms; %d beats, mean %.2f BPM'%(shift*1000,len(beats),60/np.median(np.diff(beats))))
# --- per-band envelopes (10 ms RMS, dB) for velocity estimation
def benv(z,lo,hi):
    y=signal.sosfiltfilt(signal.butter(2,[lo,hi],'bandpass',fs=fs,output='sos'),z.mean(1)); w=int(0.005*fs); k=len(y)//w
    return 20*np.log10(np.sqrt((y[:k*w].reshape(k,w)**2).mean(1))+1e-9)
bands={'surdo':(40,120),'tanta':(90,400),'repique':(300,1500),'jingle':(4000,12000),'slap':(1000,5000),'rim':(1500,6000),'cym':(5000,14000)}
E={k:benv(dr,*v) for k,v in bands.items()}
# --- pagode remap (GM percussion) and band used for velocity
REMAP={35:(35,'surdo'),36:(35,'surdo'),41:(64,'tanta'),43:(64,'tanta'),45:(63,'tanta'),47:(63,'tanta'),48:(65,'repique'),50:(65,'repique'),
       54:(54,'jingle'),52:(54,'jingle'),55:(54,'jingle'),42:(70,'jingle'),44:(70,'jingle'),46:(69,'jingle'),58:(62,'slap'),38:(62,'slap'),40:(62,'slap'),39:(62,'slap'),
       37:(37,'rim'),49:(49,'cym'),57:(49,'cym'),51:(51,'cym'),59:(51,'cym')}
pm=pretty_midi.PrettyMIDI(SRC)
import sys; W_CLS=float(sys.argv[1]) if len(sys.argv)>1 else 0.5
OE=librosa.onset.onset_strength(y=yd,sr=sr,hop_length=64); TT=librosa.times_like(OE,sr=sr,hop_length=64)
_all=np.interp([n.start for i in pretty_midi.PrettyMIDI(SRC).instruments if i.is_drum for n in i.notes],TT,OE); g_lo,g_hi=np.percentile(_all,5),np.percentile(_all,97)
def vel_from(env,t,lo=35,hi=120,cls_vals=None):
    i0=max(0,int((t-0.005)/0.005)); i1=int((t+0.035)/0.005)+1; return env[i0:i1].max() if i1<=len(env) else env[-1]
new_notes={}
for ins in pm.instruments:
    if ins.is_drum:
        raw=[]
        for n in ins.notes:
            p,cl=REMAP.get(n.pitch,(n.pitch,'slap')); raw.append((n,p,cl,vel_from(E[cl],n.start)))
        out=[]
        for cl in set(r[2] for r in raw):
            vals=np.array([r[3] for r in raw if r[2]==cl]); lo,hi=np.percentile(vals,5),np.percentile(vals,97)
            for n,p,c,v in [r for r in raw if r[2]==cl]:
                cls=np.clip((v-lo)/(hi-lo+1e-9),0,1); glo=np.clip((np.interp(n.start,TT,OE)-g_lo)/(g_hi-g_lo+1e-9),0,1)
                vv=int(np.clip(30+(W_CLS*cls+(1-W_CLS)*glo)*(122-30),25,127)); out.append(pretty_midi.Note(vv,p,n.start,n.start+0.1))
        new_notes['drums']=(ins,sorted(out,key=lambda q:q.start))
    elif ins.name.lower().startswith('vocal'):
        env=benv(vo,150,4000); vals=np.array([env[int(n.start/0.005):int(min(n.end,n.start+0.15)/0.005)+1].max() for n in ins.notes]); lo,hi=np.percentile(vals,5),np.percentile(vals,97)
        new_notes['vocals']=(ins,[pretty_midi.Note(int(np.clip(50+(v-lo)/(hi-lo+1e-9)*(115-50),40,127)),n.pitch,n.start,n.end) for n,v in zip(ins.notes,vals)])
# --- write with a beat-by-beat tempo map (seconds preserved), ppq 480
PPQ=480; grid=np.r_[0.0,beats] if beats[0]>0.05 else beats.copy()
def sec2tick(t):
    if t<=grid[0]: return 0
    i=min(np.searchsorted(grid,t)-1,len(grid)-2)
    if t>grid[-1]: per=grid[-1]-grid[-2]; return int(round(((len(grid)-1)+(t-grid[-1])/per)*PPQ))
    return int(round((i+(t-grid[i])/(grid[i+1]-grid[i]))*PPQ))
mf=mido.MidiFile(ticks_per_beat=PPQ); tr0=mido.MidiTrack(); mf.tracks.append(tr0)
tr0.append(mido.MetaMessage('time_signature',numerator=4,denominator=4,time=0))
last=0
for i in range(len(grid)-1):
    tick=i*PPQ; tr0.append(mido.MetaMessage('set_tempo',tempo=int(round((grid[i+1]-grid[i])*1e6)),time=tick-last)); last=tick
tr0.append(mido.MetaMessage('end_of_track',time=0))
ch=0
for ins in pm.instruments:
    nm=ins.name or 'track'; notes=new_notes[('drums' if ins.is_drum else 'vocals')][1] if (ins.is_drum or nm.lower().startswith('vocal')) else ins.notes
    tr=mido.MidiTrack(); mf.tracks.append(tr); tr.append(mido.MetaMessage('track_name',name=nm+(' (pagode, velocity do audio)' if ins.is_drum else (' (velocity do audio)' if nm.lower().startswith('vocal') else '')),time=0))
    c=9 if ins.is_drum else ch
    if not ins.is_drum: tr.append(mido.Message('program_change',program=ins.program,channel=c,time=0)); ch+=1; ch+= (ch==9)
    ev=[]
    for n in notes:
        ev.append((sec2tick(n.start),1,mido.Message('note_on',note=n.pitch,velocity=n.velocity,channel=c)))
        ev.append((sec2tick(max(n.end,n.start+0.03)),0,mido.Message('note_off',note=n.pitch,velocity=0,channel=c)))
    ev.sort(key=lambda e:(e[0],e[1])); lt=0
    for t,_,msg in ev: msg.time=t-lt; tr.append(msg); lt=t
    tr.append(mido.MetaMessage('end_of_track',time=0))
out='/home/claude/md/Soap_Opera_Thing_MIDI_groove.mid'; mf.save(out); print('saved',out)
# --- verify: seconds preserved, velocities follow audio, accent pattern by 16th
chk=pretty_midi.PrettyMIDI(out)
orig_d=sorted(n.start for i in pm.instruments if i.is_drum for n in i.notes); new_d=sorted(n.start for i in chk.instruments if i.is_drum for n in i.notes)
print('drum note times preserved: max diff %.2f ms'%(np.max(np.abs(np.array(orig_d)-np.array(new_d)))*1000))
oe=librosa.onset.onset_strength(y=yd,sr=sr,hop_length=64); tt=librosa.times_like(oe,sr=sr,hop_length=64)
dn=[n for i in chk.instruments if i.is_drum for n in i.notes]; t=np.array([n.start for n in dn]); v=np.array([n.velocity for n in dn])
print('drums: corr(velocity, audio onset strength) = %.2f (was 0.06); velocity range %d-%d, %d distinct values'%(np.corrcoef(v,np.interp(t,tt,oe))[0,1],v.min(),v.max(),len(np.unique(v))))
i=np.searchsorted(beats,t)-1; ok=(i>=0)&(i<len(beats)-1); ph=(t[ok]-beats[i[ok]])/(beats[i[ok]+1]-beats[i[ok]]); sl=np.round(ph*4)%4; vv=v[ok]
print('MIDI accent by 16th (mean velocity rel. slot 1):',' '.join(f'{vv[sl==k].mean()/vv[sl==0].mean():.2f}' for k in range(4)),' | audio: 1.00 0.83 0.97 1.00')
p,c=np.unique([n.pitch for n in dn],return_counts=True); print('kit after remap:',dict(zip(p.tolist(),c.tolist())))
vn=[n for i in chk.instruments if (i.name or '').lower().startswith('vocal') for n in i.notes]; vv2=np.array([n.velocity for n in vn]); print('vocals velocity: %d distinct values, %d-%d (was fixed 90)'%(len(np.unique(vv2)),vv2.min(),vv2.max()))
print('grid: first beat at %.3f s; tempo range %.1f-%.1f BPM'%(beats[0],60/np.max(np.diff(beats)),60/np.min(np.diff(beats))))
