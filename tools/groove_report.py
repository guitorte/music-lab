#!/usr/bin/env python3
"""Raio-x de groove e mix de uma pasta de stems (vocals/drums/bass/guitar/piano/other).

Uso: python tools/groove_report.py pasta_de_stems [--bpm 90]

Imprime tempo, molde de acentos por semicolcheia, punch do surdo, equilíbrio dos stems (LU relativo
à soma), camadas simultâneas e % de tempo ativo, comparando com a referência ao vivo medida em nov. 2026.
"""
import argparse, glob, os, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.metrics import accent_template, slot_presence, surdo_punch, stem_balance, layer_report

REF = {'bpm': 79.5, 'acentos': [1.00, 0.23, 0.99, 0.59], 'punch': 21.1, 'camadas': 5.56,
       'balanco': {'vocals': -4.7, 'drums': -4.4, 'bass': -10.8, 'guitar': -9.0, 'piano': -15.0, 'other': -14.3}}
ap = argparse.ArgumentParser(); ap.add_argument('stems'); ap.add_argument('--bpm', type=float, default=90, help='palpite de tempo (evita travar no dobro)'); a = ap.parse_args()
S = {}
for f in sorted(glob.glob(os.path.join(a.stems, '*'))):
    if f.lower().endswith(('.wav', '.flac', '.mp3')):
        z, fs = sf.read(f, always_2d=True); name = next((k for k in REF['balanco'] if k[:4] in os.path.basename(f).lower()), os.path.basename(f))
        S[name] = z
n = min(len(z) for z in S.values()); S = {k: v[:n] for k, v in S.items()}; mix = sum(S.values()); m = pyln.Meter(fs)
band = sum(v for k, v in S.items() if k != 'vocals')
dr = S.get('drums', band); t0, t1 = 8, n / fs - 8
acc, micro, bpm = accent_template(dr, fs, t0, t1, a.bpm)
print(f'tempo {bpm:.1f} BPM (ref {REF["bpm"]})')
print('acentos 16ª (força quando há golpe):', np.round(acc, 2), '(ref', REF['acentos'], ') | microtempo ms:', np.round(micro, 1))
print('presença 16ª nos agudos (% dos tempos):', np.round(slot_presence(dr, fs, t0, t1, a.bpm)).astype(int), '(Traição 88/34/78/71)')
print(f'punch surdo (stem de bateria) {surdo_punch(dr[int(t0*fs):int(t1*fs)], fs):.1f} dB (ref {REF["punch"]})')
print('equilíbrio LU vs soma:', {k: float(v) for k, v in stem_balance(S, m).items()}, '\n  ref:', REF['balanco'])
if 'vocals' in S: print(f'voz vs banda {m.integrated_loudness(S["vocals"]) - m.integrated_loudness(band):+.1f} LU (ref −3.1)')
print('camadas:', layer_report({k: v for k, v in S.items() if k != 'vocals'}, fs, 10, n / fs - 10), f'(ref média {REF["camadas"]})')
