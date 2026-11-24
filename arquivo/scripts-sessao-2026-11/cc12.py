import numpy as np, soundfile as sf, pyloudnorm as pyln
x,fs=sf.read('/home/claude/cc/src.wav')
L12=43.722; L23s,L23e=66.483,66.4725
def render(cuts,d):
    # cuts: list of (from_src, to_src); equal-power crossfade of d seconds starting at each cut
    out=[]; pos=0.0; mapping=[]
    for fr,to in cuts:
        a,b=int(pos*fs),int(fr*fs); n=int(d*fs); out.append(x[a:b])
        th=np.linspace(0,np.pi/2,n)[:,None]; out.append(x[b:b+n]*np.cos(th)+x[int(to*fs):int(to*fs)+n]*np.sin(th))
        mapping.append((sum(len(o) for o in out)/fs-d,fr,to)); pos=to+d
    out.append(x[int(pos*fs):]); return np.concatenate(out),mapping
cut_ch1_end=(47.30,47.30+L12)                     # ch1 -> last line of ch2 -> bridge (as before)
cut_br_ch2=(63.12+L23s,63.12)                      # bridge ends into ch3 start -> jump back to ch2 (shared pause)
cut_ch2_ch3end=(91.05,91.05+L23e)                  # ch2 last line -> ch3 last line + ending
cut_ch2_ch1end=(91.05,91.05-L12)                   # ch2 last line -> ch1 last line (which flows into a new chorus)
cut_ch2start_ch3=(63.12,63.12+L23s)                # new chorus start -> ch3
A,mA=render([cut_ch1_end,cut_br_ch2,cut_ch2_ch3end],0.10)
B,mB=render([cut_ch1_end,cut_br_ch2,cut_ch2_ch1end,cut_ch2start_ch3],0.10)
for nm,z,mp in [('A_ponte-refrao2',A,mA),('B_ponte-refrao2-refrao3',B,mB)]:
    print(nm,'length %d:%05.2f'%(len(z)/fs//60,len(z)/fs%60),' splices at:',', '.join(f'{t//60:.0f}:{t%60:05.2f}' for t,_,_ in mp))
    sf.write(f'/home/claude/cc/Coca_na_{nm}_24bit.wav',z,fs,subtype='PCM_24')
np.save('/home/claude/cc/maps.npy',np.array([mA,mB],dtype=object),allow_pickle=True)
# loudness continuity at each splice
m=pyln.Meter(fs,block_size=0.4); mom=lambda z,t: m.integrated_loudness(z[int((t-0.2)*fs):int((t+0.2)*fs)])
for nm,z,mp in [('A',A,mA),('B',B,mB)]:
    for t,fr,to in mp:
        print(f' {nm} splice {t:6.2f}: new {mom(z,t+0.05):.1f} | source before {mom(x,fr+0.05):.1f} | source after {mom(x,to+0.05):.1f}')
