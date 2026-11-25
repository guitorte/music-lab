#!/bin/bash
# reconstrói a versão "Mente Vit com arranjo de Traição" do zero
set -e; cd /home/claude/vt
python3 /home/claude/scripts/vt_compose.py | tail -1
python3 /home/claude/scripts/vt_render.py > /dev/null
python3 /home/claude/scripts/vt_surdo.py > /dev/null
python3 /home/claude/scripts/vt_smp.py 2>&1 | grep -v -i warn | tail -1
python3 /home/claude/scripts/vt_cavaco.py | tail -1
/home/claude/bin/sfizz_render --sfz /home/claude/samples/jlearman.jRhodes3d/jRhodes3d-st.sfz --midi w/epiano.mid --wav /tmp/ep_sfz.wav -s 44100 -q 3 > /dev/null 2>&1
python3 -c "
import soundfile as sf, numpy as np
a,fs=sf.read('r/epiano.wav'); b,_=sf.read('/tmp/ep_sfz.wav'); N=len(a); b=b[:N] if len(b)>=N else np.pad(b,((0,N-len(b)),(0,0)))
pk=np.abs(b).max(); sf.write('r/epiano.wav',b/pk*0.9 if pk>0.9 else b,fs,subtype='PCM_24')"
cp w/pratos.wav r/pratos_gm.wav; rm -f /tmp/ep_sfz.wav w/*[!k].wav r/pad.wav r/sopros.wav r/sax.wav
echo render ok
