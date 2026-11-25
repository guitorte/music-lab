# music-lab no Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/guitorte/music-lab/blob/main/colab/Music_Lab_Colab.ipynb)

Roda no Colab o que não dá para fazer na sessão de IA: compilar programas e baixar instrumentos do GitHub.

| Arquivo | Papel |
|---|---|
| `Music_Lab_Colab.ipynb` | 4 células de formulário: preparar, renderizar MIDIs, alinhar palavras, segundo ouvido |
| `lab.py` | toda a lógica (o notebook só chama daqui) |
| `gerar_notebook.py` | gera o `.ipynb`; edite aqui, nunca o JSON à mão |

## Uso

1. *Ambiente de execução ▸ Alterar tipo ▸ T4 GPU* (a GPU só acelera o alinhamento).
2. Para o segundo ouvido: token em huggingface.co/settings/tokens, guardado como segredo `HF_TOKEN` (ícone de chave).
3. **Preparar:** monta o Drive e baixa este repositório. `PASTA_LAB` (padrão `MyDrive/music-lab`) guarda o que é feito
   uma vez só: `bin/sfizz_render` (compilado na primeira vez, ~10 min) e `sfz/` (instrumentos baixados).
4. **Renderizar:** aponte `PASTA_MIDIS` para as partes em MIDI (`baixo.mid`, `epiano.mid`, ...). Saída em
   `PASTA_MIDIS/sfizz/<parte>__<instrumento>.wav`, 24 bits. Partes já renderizadas são puladas (marque `SOBRESCREVER` para refazer).
5. **Alinhar:** stem de voz + letra com tempos aproximados (`.srt` ou o `.json` de linhas do whisper).
   Gera `<voz>_palavras.json` ao lado da voz.
6. **Perguntar:** recorta até ~30 s e manda ao Music Flamingo. Bom para letra e tonalidade; erra tempo e gênero
   (lição 17 em `docs/07-licoes.md`).

Depois de uma atualização no GitHub: *Desconectar e excluir ambiente* antes de rodar de novo (o clone antigo fica no runtime).

## Instrumentos

| Nome | Biblioteca (github.com/sfzinstruments) | Observação |
|---|---|---|
| `rhodes` | jlearman.jRhodes3d, estéreo | o sfizz avisa "Parse error ... line 1": é um cabeçalho do arquivo original, o render sai completo |
| `rhodes_mono` | jlearman.jRhodes3d, mono | as mesmas amostras do sampler em Python |
| `baixo_eletrico` | karoryfer.growlybass, clean | as mesmas amostras do sampler em Python |
| `contrabaixo_pizz` | dsmolken.double-bass, pizzicato | baixo acústico |
| `piano` | SplendidGrandPiano | Steinway, domínio público |

Cordas, sopros e sax (VSCO-2-CE, VCSL) não têm arquivo `.sfz` publicado; continuam no sampler em Python.
Para acrescentar um instrumento: uma linha em `INSTRUMENTOS` no `lab.py`.

## O que foi testado (25/11/2026, fora do Colab)

Build com as mesmas opções (`sfizz_render`, 2,7 MB, só depende da libc), download dos instrumentos, render das
partes da versão Vit, pulo de arquivos existentes, alinhamento e a chamada ao Space. Não testado: o Colab em si
(montagem do Drive, segredo `HF_TOKEN`, GPU).
