"""Funções do notebook Music_Lab_Colab.ipynb (o notebook só chama daqui).

Três ferramentas testadas em 25/11/2026 (docs/08-recursos.md):
  1. instrumentos SFZ de verdade para os MIDIs (sfizz_render, compilado uma vez e guardado no Drive);
  2. tempo de cada palavra cantada (WhisperX, tools/alinhar_palavras.py);
  3. "segundo ouvido" (Music Flamingo, Space da NVIDIA, com o seu token do Hugging Face).

Nunca grava por cima do áudio de entrada: tudo vai para a pasta de saída escolhida.
"""
import glob, os, shutil, subprocess, sys, unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WORK = Path('/content/music_lab_work')          # rascunho (some quando o runtime é apagado)
SFIZZ_GIT = 'https://github.com/sfztools/sfizz.git'
# mesmas opções do build testado: só o renderizador, sem JACK, testes ou plugins
SFIZZ_CMAKE = ['-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DSFIZZ_JACK=OFF', '-DSFIZZ_RENDER=ON',
               '-DSFIZZ_TESTS=OFF', '-DSFIZZ_BENCHMARKS=OFF', '-DSFIZZ_DEMOS=OFF', '-DSFIZZ_DEVTOOLS=OFF']

# instrumentos SFZ gratuitos (github.com/sfzinstruments): nome -> (repositório, arquivo .sfz)
INSTRUMENTOS = {
    'rhodes': ('jlearman.jRhodes3d', 'jRhodes3d-st.sfz'),                 # Rhodes Mark I 1977; licença do autor: livre para usar em música
    'rhodes_mono': ('jlearman.jRhodes3d', 'jRhodes3d-mono.sfz'),          # o que o sampler atual usa
    'baixo_eletrico': ('karoryfer.growlybass', 'growlybass_clean.sfz'),  # o que o sampler atual usa
    'contrabaixo_pizz': ('dsmolken.double-bass', 'd_smolken_rubner_bass_pizz.sfz'),
    'piano': ('SplendidGrandPiano', 'Splendid Grand Piano.sfz'),         # Steinway, domínio público
}
# parte do arranjo (nome do .mid) -> instrumento padrão
PADRAO = {'epiano': 'rhodes', 'baixo': 'baixo_eletrico', 'piano': 'piano'}


def run(cmd, **kw):
    """Roda um programa mostrando a saída na célula (o Colab esconde a saída dos filhos)."""
    cmd = [str(c) for c in cmd]
    print('$', ' '.join(cmd), flush=True)
    tail = []
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          errors='replace', bufsize=1, **kw) as p:
        for line in p.stdout:
            print(line, end='', flush=True)
            tail = (tail + [line.rstrip()])[-25:]
    if p.returncode:
        raise RuntimeError(f'{os.path.basename(cmd[0])} falhou (saída {p.returncode}). Últimas linhas:\n' + '\n'.join(tail))


def _nfc(s):
    return unicodedata.normalize('NFC', s).casefold()


def achar(caminho):
    """Resolve um caminho do Drive ignorando acentos em NFD e maiúsculas ("áudio" == "Áudio")."""
    p = Path(caminho)
    if p.exists():
        return p
    atual = Path(p.anchor or '/')
    for parte in p.parts[1:] if p.anchor else p.parts:
        alvo = atual / parte
        if not alvo.exists() and atual.is_dir():
            achado = [c for c in atual.iterdir() if _nfc(c.name) == _nfc(parte)]
            alvo = achado[0] if achado else alvo
        atual = alvo
    if not atual.exists():
        raise FileNotFoundError(f'Não achei: {caminho}')
    return atual


# ---------------------------------------------------------------- 1. instrumentos SFZ

def garantir_sfizz(cache_dir):
    """Devolve o caminho do sfizz_render. Compila uma vez (~10 min) e guarda em cache_dir (Drive)."""
    cache = Path(cache_dir); cache.mkdir(parents=True, exist_ok=True)
    binario = cache / 'sfizz_render'
    if binario.exists():
        os.chmod(binario, 0o755)
        return binario
    if not shutil.which('ninja'):
        run(['apt-get', 'install', '-y', '-qq', 'ninja-build'])
    src = WORK / 'sfizz'
    if not (src / 'CMakeLists.txt').exists():
        WORK.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '-q', '--recursive', '--depth', '1', SFIZZ_GIT, src])
    run(['cmake', '-B', src / 'build', '-S', src, *SFIZZ_CMAKE])
    run(['cmake', '--build', src / 'build', '--target', 'sfizz_render', '-j', str(os.cpu_count() or 2)])
    feito = next(p for p in (src / 'build').rglob('sfizz_render') if p.is_file())
    shutil.copy2(feito, binario); os.chmod(binario, 0o755)
    print('sfizz_render guardado em', binario)
    return binario


def baixar_instrumento(nome, biblioteca):
    """Clona a biblioteca SFZ (uma vez) para a pasta biblioteca (Drive) e devolve o .sfz."""
    repo, sfz = INSTRUMENTOS[nome]
    pasta = Path(biblioteca) / repo
    if not (pasta / sfz).exists():
        pasta.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '-q', '--depth', '1', f'https://github.com/sfzinstruments/{repo}', pasta])
    return pasta / sfz


def renderizar(pasta_midis, saida, escolhas, biblioteca, sfizz, taxa=44100, sobrescrever=False):
    """Renderiza cada parte.mid com o instrumento escolhido. escolhas: {'baixo': 'baixo_eletrico', ...}.

    Grava saida/<parte>__<instrumento>.wav (24 bits). Partes sem instrumento são puladas.
    """
    import numpy as np, soundfile as sf
    pasta_midis, saida = achar(pasta_midis), Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    feitos = []
    for mid in sorted(pasta_midis.glob('*.mid')):
        nome = escolhas.get(mid.stem.casefold())
        if not nome:
            continue
        destino = saida / f'{mid.stem}__{nome}.wav'
        if destino.exists() and not sobrescrever:
            print('já existe, pulando:', destino.name); feitos.append(destino); continue
        sfz = baixar_instrumento(nome, biblioteca)
        tmp = WORK / 'render.wav'; WORK.mkdir(parents=True, exist_ok=True)
        run([sfizz, '--sfz', sfz, '--midi', mid, '--wav', tmp, '-s', taxa, '-q', 3, '--use-eot'])
        x, fs = sf.read(tmp, always_2d=True)
        pico = float(np.abs(x).max()) if len(x) else 0.0
        if pico > 0.89:   # o render sai em ponto flutuante; deixa ~1 dB de folga sem mudar a dinâmica
            x = x * (0.89 / pico)
        sf.write(destino, x, fs, subtype='PCM_24')
        print(f'ok: {destino.name}  ({len(x)/fs:.1f} s, pico {20*np.log10(max(pico,1e-9)):+.1f} dBFS antes do ajuste)')
        feitos.append(destino)
    if not feitos:
        print('Nenhuma parte reconhecida. Os .mid precisam se chamar como as chaves escolhidas (ex.: baixo.mid, epiano.mid).')
    return feitos


# ---------------------------------------------------------------- 2. tempo das palavras

def preparar_whisperx():
    """Instala o WhisperX sem trocar o torch do Colab (mesmo caminho testado)."""
    try:
        import whisperx  # noqa: F401
        return
    except ImportError:
        pass
    run([sys.executable, '-m', 'pip', 'install', '-q', '--no-deps', 'whisperx'])
    run([sys.executable, '-m', 'pip', 'install', '-q', 'transformers', 'nltk', 'omegaconf'])


def alinhar(voz, letra, saida_json):
    import torch
    preparar_whisperx()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    run([sys.executable, REPO / 'tools' / 'alinhar_palavras.py', achar(voz), achar(letra), saida_json, '--device', dev])
    return saida_json


# ---------------------------------------------------------------- 3. segundo ouvido

def segundo_ouvido(audio, pergunta='', token=None, espaco='nvidia/music-flamingo'):
    """Pergunta ao Music Flamingo sobre um trecho (até ~30 s). Sem token a cota de GPU acaba rápido.

    Lembrete (docs/07-licoes.md, lição 17): ele erra tempo e gênero; serve de teste de fumaça, não de juiz.
    """
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        run([sys.executable, '-m', 'pip', 'install', '-q', 'gradio_client'])
        from gradio_client import Client, handle_file
    c = Client(espaco, token=token or None, verbose=False)
    args = [handle_file(str(achar(audio))), '']
    return c.predict(*args, pergunta, api_name='/infer') if pergunta else c.predict(*args, api_name='/infer')


def trecho(audio, inicio, fim, saida):
    """Recorta um trecho (o modelo trabalha melhor com até ~30 s)."""
    import soundfile as sf
    x, fs = sf.read(achar(audio), always_2d=True)
    sf.write(saida, x[int(inicio * fs):int(fim * fs)], fs)
    return saida
