#!/usr/bin/env python3
"""Cadeia de masterização padrão do music-lab (a da master aprovada de "Mente", generalizada).

Uso:
  python tools/master.py mix.wav saida_base --target -12 --ceiling -2 \
      --ride 46.0:83.0 --ride 104.75:171.5 --ride-db 1.5 [--groove] [--lowcut-63 -2] [--lp 16500]

Gera <saida_base>_24bit.wav e <saida_base>.mp3 e imprime as checagens (Owsinski/Katz):
redução do limiter no p99, true peak após codecs, diferença refrão/verso, punch.

Cadeia: HPF 28 Hz → graves mono (<110 Hz) + side +1.5 dB acima de 1 kHz → transient shaper no surdo
→ EQ tonal → de-harsh dinâmico (2.5–5k, 6–12k) → snap de percussão → compressão paralela (−8 dB)
→ glue 1.5:1 (detector acima de 150 Hz) → "ride" de refrão → estágio rápido → limiter iterado ao alvo.
"""
import argparse, os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.dsp import (peq, shelf, eq, hp, lp, bp, ms, lr, ctrl, upg, env_follow, env_sample, transient,
                     fast_stage, limit, H)
from lib.metrics import codec_peaks, surdo_punch

ap = argparse.ArgumentParser()
ap.add_argument('mix'); ap.add_argument('out')
ap.add_argument('--target', type=float, default=-12.0, help='LUFS integrado (típico −10.5 a −13)')
ap.add_argument('--ceiling', type=float, default=-2.0, help='dBTP (−2 para masters mais altas que −14 LUFS)')
ap.add_argument('--ride', action='append', default=[], help='t0:t1 em s; refrão sobe RIDE dB entrando na pausa antes dele')
ap.add_argument('--ride-db', type=float, default=1.5)
ap.add_argument('--lowcut-63', type=float, default=-2.0, help='corte estático em 63 Hz; use 0 se o surdo carrega o groove')
ap.add_argument('--lp', type=float, default=0, help='passa-baixa (Hz) para artefatos de topo da IA, ex. 16500')
ap.add_argument('--no-fast', action='store_true', help='pula o estágio rápido (quando o groove depende dos transientes)')
ap.add_argument('--fade-out', type=float, default=0.0)
ap.add_argument('--verse', default='', help='t0:t1 de um verso, para comparar com o 1º ride')
a = ap.parse_args()

x, fs = sf.read(a.mix, always_2d=True); n = len(x); tt = np.arange(n) / fs; meter = pyln.Meter(fs); rate = fs / H
y = hp(x, fs, 28)
if a.lp: y = lp(y, fs, a.lp)
M, S = ms(y); S = hp(S, fs, 110); S = S + hp(S, fs, 1000) * (10 ** (1.5 / 20) - 1); y = lr(M, S)
y = transient(y, fs, 45, 120, +1.5, -2.5)
y = eq(y, [peq(fs, 63, a.lowcut_63, 1.5), peq(fs, 315, -1.0, 1.2), peq(fs, 1200, 1.0, 1.0), peq(fs, 2500, 2.0, 0.7), shelf(fs, 9000, 2.0)])
ref = ctrl(bp(y, fs, 500, 2000))
for lo, hi in [(2500, 5000), (6000, 12000)]:
    b = bp(y, fs, lo, hi); dd = ctrl(b) - ref; th = np.percentile(dd, 94)
    g = env_follow(np.clip((dd - th) * 0.7, 0, 3.0), 0.002, 0.07, rate); y = y + b * (upg(-g, n)[:, None] - 1)
y = transient(y, fs, 2000, 8000, +1.5, 0.0)
d = np.abs(y).max(1) + 1e-9; lv = 20 * np.log10(env_sample(d, fs, 0.01, 0.1)); thr = np.percentile(lv[lv > -60], 50)
gr = np.clip((lv - thr) * (1 - 1 / 4), 0, None); pc = y * 10 ** (-gr / 20)[:, None] * 10 ** (np.median(gr[gr > 0]) / 20)
y = y + pc * 10 ** (-8 / 20)
lv = ctrl(hp(y, fs, 150)); thr = np.percentile(lv[lv > -60], 80) - 1.5
y *= upg(-env_follow(np.clip((lv - thr) * (1 - 1 / 1.5), 0, None), 0.03, 0.17, rate), n)[:, None]
rides = [tuple(map(float, r.split(':'))) for r in a.ride]
if rides:
    def ride(t0, t1, up=0.12, down=1.5):
        w = np.minimum(np.clip((tt - t0) / up, 0, 1), np.clip((t1 + down - tt) / down, 0, 1)); return 0.5 - 0.5 * np.cos(np.pi * w)
    y = y * 10 ** (a.ride_db * np.maximum.reduce([ride(*r) for r in rides]) / 20)[:, None]
if not a.no_fast:
    y, nd = fast_stage(y, fs); print('estágio rápido: p99 %.1f dB, máx %.1f dB' % (np.percentile(nd, 99), nd.max()))
gg = a.target - meter.integrated_loudness(y)
for _ in range(6):
    out, grd = limit(y * 10 ** (gg / 20), fs, a.ceiling); gg += a.target - meter.integrated_loudness(out)
fo = np.clip((n / fs - tt) / a.fade_out, 0, 1) ** 1.5 if a.fade_out else 1.0
out = out * (np.asarray(fo) * np.clip(tt / 0.02, 0, 1))[:, None]
sf.write(a.out + '_24bit.wav', out, fs, subtype='PCM_24')
subprocess.run(f'ffmpeg -hide_banner -loglevel error -y -i "{a.out}_24bit.wav" -c:a libmp3lame -b:a 320k "{a.out}.mp3"', shell=True, check=True)
L = lambda z, t0, t1: meter.integrated_loudness(z[int(t0 * fs):int(t1 * fs)])
print(f'LUFS {meter.integrated_loudness(out):.2f} | limiter GR p99 {np.percentile(grd, 99):.2f} dB (Owsinski: ≤2–3) máx {grd.max():.2f}')
if rides and a.verse:
    v0, v1 = map(float, a.verse.split(':')); r0, r1 = rides[0]; print(f'refrão vs verso {L(out, r0 + 1, min(r1, r0 + 17)) - L(out, v0, v1):+.1f} LU')
print(f'punch surdo {surdo_punch(out, fs):.1f} dB (mix {surdo_punch(x, fs):.1f})')
print('true peak após codecs:', codec_peaks(a.out + '_24bit.wav'))
