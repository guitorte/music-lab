#!/usr/bin/env python3
"""Tempo de cada palavra cantada por alinhamento forçado (WhisperX + wav2vec2 em português).

Uso: python tools/alinhar_palavras.py voz.wav letra.srt saida.json [--lang pt]
     (letra também pode ser um JSON com "lines": [[ini, fim, "texto"], ...])

Precisa do stem de voz (não da mix) e de linhas com tempo aproximado (SRT ou whisper). O texto das
linhas é o que se alinha: com a letra certa, as palavras saem certas. Grava {"words": [[ini, fim, palavra]]}.

Teste (Mente, versão Vit, 25/11/2026): contra os ataques reais da voz, o início de frase errou em
mediana 71 ms (whisper puro: 213 ms, sempre atrasado); em todas as palavras, 24 ms (whisper: 39 ms).
Ver docs/08-recursos.md.

Instalação sem trocar o torch: pip install --no-deps whisperx; pip install transformers nltk omegaconf.
O script dispensa torchaudio e o punkt do NLTK (bloqueados ou ausentes neste ambiente).
"""
import argparse, json, re, sys, types
import numpy as np, soundfile as sf, librosa

# whisperx só usa torchaudio.pipelines para modelos em inglês; em português o modelo vem do HF
try:
    import torchaudio  # noqa: F401
    import whisperx.alignment as A
except ImportError:  # módulo vazio no lugar do torchaudio (só pipelines em inglês o usam)
    import importlib.machinery
    ta = types.ModuleType('torchaudio'); ta.__spec__ = importlib.machinery.ModuleSpec('torchaudio', None)
    ta.pipelines = types.SimpleNamespace(__all__=[]); sys.modules['torchaudio'] = ta
    import whisperx.alignment as A


class _LinhaInteira:  # cada linha da letra é tratada como uma frase (sem punkt)
    def span_tokenize(self, t):
        return [(0, len(t))]


A.nltk_load = lambda *a, **k: _LinhaInteira()


def ler_linhas(p):
    if p.lower().endswith('.json'):
        return [{'start': s, 'end': e, 'text': t} for s, e, t in json.load(open(p))['lines']]
    t = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    out = []
    for bloco in re.split(r'\n\s*\n', open(p, encoding='utf-8').read().strip()):
        lin = bloco.strip().splitlines()
        m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', lin[1] if len(lin) > 1 else '')
        if m:
            out.append({'start': t(*m.groups()[:4]), 'end': t(*m.groups()[4:]), 'text': ' '.join(lin[2:])})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('voz'); ap.add_argument('letra'); ap.add_argument('saida'); ap.add_argument('--lang', default='pt')
    a = ap.parse_args()
    v, fs = sf.read(a.voz, always_2d=True)
    y = librosa.resample(v.mean(1).astype(np.float32), orig_sr=fs, target_sr=16000)
    segs = ler_linhas(a.letra)
    modelo, meta = A.load_align_model(a.lang, 'cpu')
    r = A.align(segs, modelo, meta, y, 'cpu', return_char_alignments=False)
    W = [[w.get('start'), w.get('end'), w['word']] for s in r['segments'] for w in s['words']]
    json.dump({'words': W}, open(a.saida, 'w'), ensure_ascii=False)
    print(f'{len(W)} palavras, {sum(w[0] is None for w in W)} sem tempo -> {a.saida}')


if __name__ == '__main__':
    main()
