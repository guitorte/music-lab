"""Blocos de DSP usados em todas as masters: EQ biquad, envelopes, controle de ganho e limiter.

Tudo em numpy/scipy, sem DAW. `fs` é sempre passado explicitamente.
Origem: scripts e3.py / mt4.py das sessões de nov. 2026.
"""
import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d, maximum_filter1d

H = 32  # passo (amostras) dos detectores de nível


# ---------- EQ (RBJ cookbook) ----------
def peq(fs, f0, g, Q):
    A = 10 ** (g / 40); w = 2 * np.pi * f0 / fs; c = np.cos(w); al = np.sin(w) / (2 * Q)
    b = np.array([1 + al * A, -2 * c, 1 - al * A]); a = np.array([1 + al / A, -2 * c, 1 - al / A])
    return b / a[0], a / a[0]


def shelf(fs, f0, g, Q=0.707):
    """High shelf."""
    A = 10 ** (g / 40); w = 2 * np.pi * f0 / fs; c = np.cos(w); al = np.sin(w) / (2 * Q); sA = 2 * np.sqrt(A) * al
    b = [A * ((A + 1) + (A - 1) * c + sA), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sA)]
    a = [(A + 1) - (A - 1) * c + sA, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sA]
    return np.array(b) / a[0], np.array(a) / a[0]


def eq(z, specs):
    for b, a in specs:
        z = signal.lfilter(b, a, z, axis=0)
    return z


def hp(z, fs, f, order=2):
    return signal.sosfiltfilt(signal.butter(order, f, 'highpass', fs=fs, output='sos'), z, axis=0)


def lp(z, fs, f, order=4):
    return signal.sosfiltfilt(signal.butter(order, f, 'lowpass', fs=fs, output='sos'), z, axis=0)


def bp(z, fs, lo, hi, order=2):
    return signal.sosfiltfilt(signal.butter(order, [lo, hi], 'bandpass', fs=fs, output='sos'), z, axis=0)


# ---------- envelopes / níveis ----------
def env_follow(v, att, rel, rate):
    """Seguidor de envelope sobre uma série de controle amostrada a `rate` Hz."""
    out = np.empty_like(v); c = 0.0; aa = np.exp(-1 / (att * rate)); ar = np.exp(-1 / (rel * rate))
    for i, s in enumerate(v):
        c = s + (c - s) * (aa if s > c else ar); out[i] = c
    return out


def env_sample(x, fs, att, rel):
    """Envelope por amostra (lento em Python puro; usa numba se houver)."""
    try:
        from numba import njit

        @njit
        def _e(x, a, r):
            y = np.empty_like(x); e = 0.0
            for i in range(len(x)):
                v = x[i]; c = a if v > e else r; e = c * e + (1 - c) * v; y[i] = e
            return y
        return _e(np.ascontiguousarray(x), np.exp(-1 / (att * fs)), np.exp(-1 / (rel * fs)))
    except ImportError:
        return signal.lfilter([1 - np.exp(-1 / (rel * fs))], [1, -np.exp(-1 / (rel * fs))], x)


def ctrl(sig):
    """Nível em dB por bloco de H amostras."""
    s = sig if sig.ndim == 2 else sig[:, None]; k = len(s) // H
    return 10 * np.log10((s[:k * H].reshape(k, H, -1) ** 2).mean((1, 2)) + 1e-14)


def upg(gdb, n):
    """Série de ganho (dB, por bloco) → ganho linear por amostra."""
    g = np.repeat(10 ** (gdb / 20), H); return np.r_[g, np.full(n - len(g), g[-1])]


def ms(y):
    return (y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2


def lr(M, S):
    return np.stack([M + S, M - S], 1)


# ---------- dinâmica ----------
def transient(z, fs, lo, hi, att_db, sus_db):
    """Transient shaper numa banda: realça ataque (att_db) e encurta/alonga a cauda (sus_db)."""
    b = bp(z, fs, lo, hi); d = np.abs(b).max(1) + 1e-9
    ef = env_sample(d, fs, 0.0005, 0.02); es = env_sample(d, fs, 0.02, 0.2)
    diff = 20 * np.log10(ef) - 20 * np.log10(es)
    g = np.where(diff > 0, np.clip(diff / 6, 0, 1) * att_db, np.clip(-diff / 6, 0, 1) * sus_db)
    return z - b + b * 10 ** (g / 20)[:, None]


def fast_stage(y, fs, max_db=4.0, pct=99):
    """Estágio rápido de transientes antes do limiter (Katz: transientes curtos toleram 4–6 dB)."""
    rate = fs / H
    pk = maximum_filter1d(np.abs(y).max(1), size=int(0.003 * fs)); th = np.percentile(pk, pct)
    need = np.clip(20 * np.log10(np.maximum(pk, 1e-9) / th), 0, max_db); k = len(need) // H
    nd = env_follow(need[:k * H].reshape(k, H).max(1), 0.0002, 0.008, rate)
    return y * upg(-nd, len(y))[:, None], nd


def limit(z, fs, ceil_db=-1.0):
    """Limiter com lookahead (~5 ms), detecção true-peak 4x. Retorna (saída, redução em dB por bloco)."""
    rate = fs / H
    up = signal.resample_poly(z, 4, 1, axis=0); pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(z)]
    pk = np.r_[pk, np.full(len(z) - len(pk), pk[-1])]
    gl = np.minimum(1, 10 ** (ceil_db / 20) / np.maximum(pk, 1e-9))
    gl = minimum_filter1d(gl, size=2 * int(0.005 * fs) + 1); k = len(gl) // H
    grd = env_follow(-20 * np.log10(gl[:k * H].reshape(k, H).min(1)), 0.0005, 0.08, rate)
    gs = np.repeat(10 ** (-grd / 20), H); gs = np.r_[gs, np.full(len(z) - len(gs), gs[-1])]
    return z * np.minimum(gs, gl)[:, None], grd


def peak_control(z, fs, plr, meter):
    """Controle de pico de um stem até uma razão pico/loudness alvo (usado em partes MIDI renderizadas)."""
    l = meter.integrated_loudness(z); th = 10 ** ((l + plr) / 20)
    pk = maximum_filter1d(np.abs(z).max(1), size=int(0.004 * fs))
    g = np.minimum(1, th / np.maximum(pk, 1e-9)); r = np.exp(-1 / (0.06 * fs)); out = np.empty_like(g); e = 1.0
    for i in range(len(g)):
        v = g[i]; e = v if v < e else r * e + (1 - r) * v; out[i] = e
    return z * out[:, None]
