"""Medidas usadas para decidir sem ouvir: loudness, true peak, codecs, punch, acentos, camadas.

O assistente não escuta; toda decisão é uma medida e o ouvido do usuário é o juiz final.
"""
import subprocess, tempfile, os
import numpy as np, soundfile as sf
from scipy import signal


def true_peak(z):
    return 20 * np.log10(np.abs(signal.resample_poly(z, 4, 1, axis=0)).max() + 1e-12)


def codec_peaks(path, fs=None):
    """True peak depois de MP3 320, Ogg Vorbis q9 (Spotify), Opus 160 (YouTube) e AAC 128k (ffmpeg nativo).

    O AAC nativo do ffmpeg exagera picos em material com transientes muito secos (samples GM);
    Vorbis/Opus são a referência mais realista. Ver docs/02-masterizacao.md.
    """
    out = {}
    tmp = tempfile.mkdtemp()
    for name, args, ext in [('mp3_320', '-c:a libmp3lame -b:a 320k', 'mp3'), ('vorbis_q9', '-c:a libvorbis -q:a 9', 'ogg'),
                            ('opus_160', '-c:a libopus -b:a 160k', 'opus'), ('aac_128_ffmpeg', '-c:a aac -b:a 128k', 'm4a')]:
        enc = os.path.join(tmp, 'c.' + ext); dec = os.path.join(tmp, 'c.wav')
        r = subprocess.run(f'ffmpeg -hide_banner -loglevel error -y -i "{path}" {args} {enc} && '
                           f'ffmpeg -hide_banner -loglevel error -y -i {enc} -c:a pcm_f32le {dec}', shell=True)
        if r.returncode == 0:
            q, _ = sf.read(dec); out[name] = round(float(true_peak(q)), 2)
    return out


def frames_db(x, fs, win=0.01):
    m = x.mean(1) if x.ndim == 2 else x; w = int(win * fs); k = len(m) // w
    return 20 * np.log10(np.sqrt((m[:k * w].reshape(k, w) ** 2).mean(1)) + 1e-9)


def surdo_punch(x, fs):
    """Punch do surdo/bumbo: percentil 95 menos a mediana de quadros de 10 ms em 45–120 Hz.
    Os valores de referência foram medidos no STEM DE BATERIA: banda ao vivo ~21 dB, faixa IA ~33
    (picos soltos). Medido na mix inteira o número cai (o baixo preenche a banda); não misture os dois."""
    q = signal.sosfiltfilt(signal.butter(2, [45, 120], 'bandpass', fs=fs, output='sos'), x.mean(1) if x.ndim == 2 else x)
    e = frames_db(q, fs); return float(np.percentile(e, 95) - np.percentile(e, 50))


def beat_grid(x, fs, start_bpm=90, tightness=400):
    """Grade de tempos (librosa, 22.05 kHz), deslocada pela mediana do atraso dos onsets.
    start_bpm próximo do real evita travar em dobro/metade."""
    import librosa
    y = librosa.resample((x.mean(1) if x.ndim == 2 else x).astype(np.float32), orig_sr=fs, target_sr=22050)
    tempo, beats = librosa.beat.beat_track(y=y, sr=22050, start_bpm=start_bpm, tightness=tightness, units='time')
    on = librosa.onset.onset_detect(y=y, sr=22050, units='time')
    d = [o - beats[np.argmin(np.abs(beats - o))] for o in on]; d = [v for v in d if abs(v) < 0.05]
    return float(np.atleast_1d(tempo)[0]), beats + (np.median(d) if d else 0)


def accent_template(drums, fs, a=0, b=None, start_bpm=90):
    """Acento e microtempo por semicolcheia, medidos nos onsets do stem de BATERIA (método rf2).

    Retorna (acentos relativos à 1ª semicolcheia, desvio mediano em ms de cada uma, bpm).
    Referência (pagode ao vivo, nov. 2026): acentos 1.00 / 0.23 / 0.99 / 0.59.
    Faixa IA da mesma época: 1.00 / 0.69 / 0.91 / 1.17 (contratempo mais forte que o tempo).
    """
    import librosa
    sr = 22050; seg = drums[int(a * fs):int(b * fs) if b else None]
    d = librosa.resample((seg.mean(1) if seg.ndim == 2 else seg).astype(np.float32), orig_sr=fs, target_sr=sr)
    _, beats = librosa.beat.beat_track(y=d, sr=sr, hop_length=256, units='time', start_bpm=start_bpm, tightness=400)
    on = librosa.onset.onset_detect(y=d, sr=sr, hop_length=64, units='time', backtrack=True, delta=0.12)
    oe = librosa.onset.onset_strength(y=d, sr=sr, hop_length=64); tt = librosa.times_like(oe, sr=sr, hop_length=64)
    st = np.interp(on, tt, oe)
    idx = np.clip(np.searchsorted(beats, on), 1, len(beats) - 1)
    near = np.where(np.abs(on - beats[idx - 1]) < np.abs(on - beats[idx]), beats[idx - 1], beats[idx]); dd = on - near
    beats = beats + np.median(dd[np.abs(dd) < 0.08]); ibi = np.diff(beats)
    i = np.searchsorted(beats, on) - 1; ok = (i >= 0) & (i < len(beats) - 1); t = on[ok]; i = i[ok]; s = st[ok]
    ph = (t - beats[i]) / (beats[i + 1] - beats[i]); sl = np.round(ph * 4) % 4
    dev = (ph - np.round(ph * 4) / 4) * np.median(ibi) * 1000; base = np.median(dev[sl == 0])
    acc = np.array([s[sl == k].mean() / s[sl == 0].mean() for k in range(4)])
    micro = np.array([np.median(dev[sl == k]) - base for k in range(4)])
    return acc, micro, float(np.median(60 / ibi))


def slot_presence(drums, fs, a=0, b=None, start_bpm=90, lo=6000, hi=16000):
    """Em quantos tempos cada semicolcheia é tocada (%), nos agudos da bateria (platinelas, ganzá, chimbal).

    Complementa accent_template, que mede só a força QUANDO há golpe: uma posição tocada raramente mas
    com força aparece "forte" lá (Traição, nov. 2026: 3ª semicolcheia 1.6x a 1ª) e quase vazia aqui.
    Traição (pagode romântico gravado), por esta função: 88 / 34 / 78 / 71 %. Compare só números desta função.
    """
    import librosa, scipy.signal as ss
    sr = 22050; seg = drums[int(a * fs):int(b * fs) if b else None]
    d = librosa.resample((seg.mean(1) if seg.ndim == 2 else seg).astype(np.float32), orig_sr=fs, target_sr=sr)
    _, beats = librosa.beat.beat_track(y=d, sr=sr, hop_length=256, units='time', start_bpm=start_bpm, tightness=400)
    sos = ss.butter(4, [lo, min(hi, sr / 2 - 100)], btype='bandpass', fs=sr, output='sos')
    on = librosa.onset.onset_detect(y=ss.sosfiltfilt(sos, d).astype(np.float32), sr=sr, hop_length=64, units='time')
    i = np.searchsorted(beats, on) - 1; ok = (i >= 0) & (i < len(beats) - 1); on, i = on[ok], i[ok]
    sl = np.round((on - beats[i]) / (beats[i + 1] - beats[i]) * 4).astype(int); nx = sl == 4; sl[nx] = 0; i[nx] += 1
    return np.array([100 * len(np.unique(i[sl == k])) / (len(beats) - 1) for k in range(4)])


def active(z, fs, win=0.05, below=30):
    """Quadros em que um stem está "tocando" (até `below` dB abaixo do seu p95)."""
    e = frames_db(z, fs, win); return e > np.percentile(e, 95) - below


def layer_report(stems, fs, t0=None, t1=None):
    """Camadas simultâneas e % de tempo ativo por stem. Banda real: 5.6 camadas em média; IA: 3.1."""
    acts = {k: active(v, fs) for k, v in stems.items()}; n = min(len(a) for a in acts.values())
    a0 = int((t0 or 0) / 0.05); a1 = int(t1 / 0.05) if t1 else n
    L = sum(a[:n].astype(int) for a in acts.values())[a0:a1]
    return {'camadas_media': round(float(L.mean()), 2), 'pct_>=4_camadas': round(100 * float((L >= 4).mean()), 1),
            'ativo_%': {k: round(100 * float(a[a0:a1].mean()), 1) for k, a in acts.items()}}


def stem_balance(stems, meter):
    """Loudness de cada stem relativa à soma (LU). Referência ao vivo: voz −4.7, bateria −4.4,
    baixo −10.8, guitarra −9.0, piano −15.0, outros −14.3; voz vs banda −3.1."""
    mix = sum(stems.values()); L = meter.integrated_loudness(mix)
    return {k: round(meter.integrated_loudness(v) - L, 1) for k, v in stems.items()}
