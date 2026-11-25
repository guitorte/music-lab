#!/usr/bin/env python3
"""Gera colab/Music_Lab_Colab.ipynb (não edite o .ipynb à mão; edite aqui e rode de novo)."""
import json
from pathlib import Path

NB = Path(__file__).with_name('Music_Lab_Colab.ipynb')
BADGE = ('<a href="https://colab.research.google.com/github/guitorte/music-lab/blob/main/colab/Music_Lab_Colab.ipynb" '
         'target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>')


def md(t):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': t.strip('\n').splitlines(True)}


def code(t):
    return {'cell_type': 'code', 'metadata': {'cellView': 'form'}, 'execution_count': None, 'outputs': [],
            'source': t.strip('\n').splitlines(True)}


cells = [
    md(BADGE + '''

# music-lab no Colab

Três ferramentas testadas em 25/11/2026 (`docs/08-recursos.md`):

1. **Instrumentos SFZ de verdade** para os MIDIs do arranjo (Rhodes, baixo, piano), renderizados pelo `sfizz_render`.
2. **Tempo de cada palavra cantada** (WhisperX), para breques e respostas caírem junto com a voz.
3. **Segundo ouvido** (Music Flamingo): descreve um trecho. Erra tempo e gênero; use como teste de fumaça, não como juiz.

**Antes:** *Ambiente de execução ▸ Alterar tipo ▸ T4 GPU* (só o passo 2 usa a GPU). Para o passo 3, crie um token
em huggingface.co/settings/tokens e guarde como segredo `HF_TOKEN` (ícone de chave na barra lateral).

Nada é gravado por cima dos seus arquivos: os resultados vão para pastas novas.
Depois de uma atualização no GitHub, use *Ambiente de execução ▸ Desconectar e excluir ambiente* antes de rodar de novo.
'''),
    code('''
#@title 1. Preparar (Drive + código)
BRANCH = "main" #@param {type:"string"}
PASTA_LAB = "/content/drive/MyDrive/music-lab" #@param {type:"string"}
#@markdown `PASTA_LAB` guarda o que só precisa ser feito uma vez: o `sfizz_render` compilado (`bin/`) e os instrumentos (`sfz/`).
import os, subprocess, sys
from google.colab import drive
drive.mount('/content/drive')
if not os.path.exists('/content/music-lab'):
    r = subprocess.run(['git', 'clone', '-q', '--depth', '1', '-b', BRANCH, 'https://github.com/guitorte/music-lab', '/content/music-lab'])
    if r.returncode:
        print(f'Branch "{BRANCH}" não encontrado; usando main.')
        subprocess.run(['git', 'clone', '-q', '--depth', '1', 'https://github.com/guitorte/music-lab', '/content/music-lab'], check=True)
sys.path.insert(0, '/content/music-lab/colab')
import importlib, lab; importlib.reload(lab)
os.makedirs(PASTA_LAB, exist_ok=True)
print('Pronto. Instrumentos disponíveis:', ', '.join(lab.INSTRUMENTOS))
'''),
    md('''
## 2. Renderizar os MIDIs com instrumentos SFZ

Aponte para a pasta com as partes em MIDI (as do zip `Mente_Vit_MIDIs_para_Suno.zip`: `baixo.mid`, `epiano.mid`...).
Cada parte vira `sfizz/<parte>__<instrumento>.wav` dentro dessa pasta. A **primeira vez** compila o `sfizz_render`
(~10 min) e baixa os instrumentos; depois fica guardado no Drive.
'''),
    code('''
#@title Renderizar
PASTA_MIDIS = "/content/drive/MyDrive/music-lab/midis" #@param {type:"string"}
BAIXO = "baixo_eletrico" #@param ["baixo_eletrico", "contrabaixo_pizz", "nenhum"]
EPIANO = "rhodes" #@param ["rhodes", "rhodes_mono", "piano", "nenhum"]
PIANO = "piano" #@param ["piano", "rhodes", "nenhum"]
OUTRAS = "" #@param {type:"string"}
#@markdown `OUTRAS`: partes extras no formato `parte=instrumento, parte=instrumento` (ex.: `teclado=piano`).
TAXA = 44100 #@param [44100, 48000] {type:"raw"}
SOBRESCREVER = False #@param {type:"boolean"}
escolhas = {'baixo': BAIXO, 'epiano': EPIANO, 'piano': PIANO}
for par in filter(None, (p.strip() for p in OUTRAS.split(','))):
    k, v = (s.strip() for s in par.split('='))
    escolhas[k.casefold()] = v
escolhas = {k: v for k, v in escolhas.items() if v != 'nenhum'}
sfizz = lab.garantir_sfizz(f'{PASTA_LAB}/bin')
pasta = lab.achar(PASTA_MIDIS)
feitos = lab.renderizar(pasta, pasta / 'sfizz', escolhas, f'{PASTA_LAB}/sfz', sfizz, taxa=TAXA, sobrescrever=SOBRESCREVER)
from IPython.display import Audio, display
for f in feitos:
    print(f.name); display(Audio(lab.trecho(f, 40, 100, f'/content/{f.stem}_preview.wav')))  # 1 min a partir de 0:40
'''),
    md('''
## 3. Tempo de cada palavra (WhisperX)

Precisa do **stem de voz** e da letra com tempos aproximados (`.srt`, ou o `.json` de linhas do whisper).
Gera `<voz>_palavras.json` ao lado da voz: `{"words": [[início, fim, palavra], ...]}`.
'''),
    code('''
#@title Alinhar
VOZ = "/content/drive/MyDrive/music-lab/voz.wav" #@param {type:"string"}
LETRA = "/content/drive/MyDrive/music-lab/letra.srt" #@param {type:"string"}
import json
voz = lab.achar(VOZ)
saida = voz.with_name(voz.stem + '_palavras.json')
lab.alinhar(voz, LETRA, saida)
W = json.load(open(saida))['words']
print(f'{len(W)} palavras -> {saida}')
for s, e, w in W[:15]:
    print(f'{s:8.2f} {e:8.2f}  {w}')
'''),
    md('''
## 4. Segundo ouvido (Music Flamingo)

Recorta até ~30 s e pergunta. Sem `HF_TOKEN` a cota gratuita de GPU acaba depois de uma ou duas perguntas.
'''),
    code('''
#@title Perguntar
AUDIO = "/content/drive/MyDrive/music-lab/mix.wav" #@param {type:"string"}
INICIO = 32 #@param {type:"number"}
FIM = 60 #@param {type:"number"}
PERGUNTA = "This clip contains a section change. At what second does the new section start? Is it a clear lift in energy and groove, or does it stay flat?" #@param {type:"string"}
#@markdown Deixe `PERGUNTA` vazia para a descrição completa (gênero, tempo, tonalidade, instrumentos).
try:
    from google.colab import userdata
    token = userdata.get('HF_TOKEN')
except Exception:
    token = None
    print('Sem o segredo HF_TOKEN: usando a cota anônima.')
t = lab.trecho(AUDIO, INICIO, FIM, '/content/trecho.wav')
from IPython.display import Audio, display
display(Audio(t))
print(lab.segundo_ouvido(t, PERGUNTA, token))
'''),
]

nb = {'cells': cells, 'nbformat': 4, 'nbformat_minor': 0,
      'metadata': {'accelerator': 'GPU', 'colab': {'provenance': [], 'gpuType': 'T4', 'include_colab_link': True},
                   'kernelspec': {'name': 'python3', 'display_name': 'Python 3'}, 'language_info': {'name': 'python'}}}
NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('gravado', NB)
