# music-lab

Um estúdio feito de método: pegar músicas geradas por IA a partir das letras do autor e torná-las **abertas, corrigíveis e tocadas**, sem DAW, só com conversa + código.

> A voz cantando a letra é o centro intocável. O instrumental gerado é rascunho: dá para medir, corrigir, reescrever e masterizar até soar como gente tocando.
> Leia [`docs/00-visao.md`](docs/00-visao.md).

## Mapa

| Documento | Conteúdo |
|---|---|
| [00 · Visão](docs/00-visao.md) | a ideia central por trás de tudo |
| [01 · Pipeline](docs/01-pipeline.md) | o fluxo de ponta a ponta e onde mora cada coisa |
| [02 · Masterização](docs/02-masterizacao.md) | alvos (Katz/Owsinski), cadeia, checagens, artefatos do Suno |
| [03 · Edição cirúrgica](docs/03-edicao-cirurgica.md) | trocar palavras, tirar seções, inserir samples |
| [04 · Groove e camadas](docs/04-groove-e-camadas.md) | banda real vs faixa gerada, em números |
| [05 · Reescrita de arranjo](docs/05-reescrita-de-arranjo.md) | MIDI novo sob a voz original, render, mix, master |
| [06 · Transcrição MIDI](docs/06-transcricao-midi.md) | motores, montagem REMI, defeitos do Basic Pitch, percussão real |
| [07 · Lições](docs/07-licoes.md) | erros já cometidos e o princípio de cada um |
| [08 · Recursos](docs/08-recursos.md) | modelos, repositórios e ferramentas por etapa (pesquisa de nov. 2026) |
| [Diário de faixas](docs/faixas.md) | cada música, o que foi feito e com quais números |

## Código

```
lib/dsp.py             EQ, envelopes, transient shaper, estágio rápido, limiter true-peak
lib/metrics.py         true peak pós-codec, punch, acentos por semicolcheia, camadas, equilíbrio de stems
tools/master.py        cadeia de masterização padrão (CLI)
tools/groove_report.py raio-x de groove/mix de uma pasta de stems vs a referência ao vivo
tools/arrange/         reescrita de arranjo em MIDI (rw1–rw7, primeira versão, parâmetros por música)
skills/                skill "mastering-ai-tracks" (instruções compactas para uma sessão de IA)
arquivo/               scripts originais das sessões, como foram rodados (caminhos fixos)
```

```bash
pip install -r requirements.txt          # + ffmpeg e fluidsynth/fluid-soundfont-gm no sistema
python tools/master.py mix.wav saida --target -12 --ceiling -2 --ride 46:83 --ride 104.75:171.5 --verse 17:33
python tools/groove_report.py pasta_de_stems --bpm 90
```

## Repositórios irmãos

- [`guitorte/audio`](https://github.com/guitorte/audio): notebooks Colab de separação, música → MIDI, bake-off de motores, montagem MIDI → REMI, `stem-mastering/`, conversão de voz.
