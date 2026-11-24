# Transcrição MIDI, montagem e percussão (conversa "Transcrição MIDI", nov. 2026)

O código desta parte vive no repo **`guitorte/audio`** (notebooks Colab + módulos). Aqui fica o resumo do que se aprendeu e onde está cada coisa.

## Motores: o que existe e o que foi testado

| Etapa | Pipeline original (`music-to-midi/`) | Alternativas avaliadas |
|---|---|---|
| Separação | htdemucs_6s | **BS-RoFormer SW** (via `audio-separator`) |
| Voz | Basic Pitch | **GAME** (OpenVPI), rodado a partir da release ONNX |
| Bateria | ADTOF | **ADT_STR** (venv Python 3.12 próprio; ele fixa o torch 2.8) |
| Mix inteira | — | **MuScriptor** (pesos fechados, CC BY-NC, exige `HF_TOKEN`) |

- Bake-off: `music-to-midi/notebooks/MIDI_Engine_Bakeoff.ipynb` + `modules/bakeoff.py` (PRs #29, #30, #31, #35).
  - Mede tempo e VRAM de pico.
  - Sem gabarito, a qualidade é aproximada: chroma CENS entre o áudio e um render senoidal do MIDI, F1 dos onsets de bateria, RMS do stem (o Basic Pitch escreve notas em stems quase mudos de vazamento).
  - Com MIDI de referência, calcula o F1 real (mir_eval).
- Recomendação da época: manter o pipeline atual como modo rápido, trocar o separador por BS-RoFormer SW e comparar o MuScriptor em 2 ou 3 músicas.

## Montagem: MIDIs por stem → música tocável + texto (REMI)

`music-to-midi/notebooks/Assemble_MIDI_to_REMI.ipynb` + `modules/remi.py` (PRs #32, #34, #36):
- Escolhe um MIDI por stem (arquivos do bake-off, nomes simples, `*_vocals.mid` do vocal-lab, que tem prioridade).
- Escreve `<música>.mid`, `<música>_instrumental.mid` e as versões em **MIDI-TEXT v2 (estilo REMI)**: cabeçalho com tonalidade (Krumhansl-Schmuckler), tempo e acordes por compasso, depois cada nota com a posição em semicolcheias no compasso e o tempo exato. **Todo texto é verificado: precisa voltar às mesmas notas.**
- Por que existe: é a música num formato que uma IA lê, edita e devolve como MIDI.

## Defeitos sistemáticos encontrados (e corrigidos no assembler)

- **Basic Pitch deixa tudo ~33 cents agudo:** ele escreve notas afinadas com um pitch bend de +1/3 de semitom que fica ativo no canal. Cerca de 3/4 das notas instrumentais soavam desafinadas contra a voz. O assembler agora descarta os bends.
- **Vazamento entre stems:** o piano de qne-maq era quase todo vazamento. As notas eram harmônicos do Ré# do baixo (Ré#, Lá#, Sol = 4º, 3º e 5º harmônicos, caindo junto com o baixo) ou cópias de guitarra/outros. Limpeza: 904 → 719 notas, com log CSV de cada mudança.
- **Tempo errado sem metadado:** o beat tracker começa em 120 BPM e travou num bumbo pontuado em raio-x (107,7 em vez de ~160). Correção: `drum_tempo_hint()` usa a grade do chimbal.
- **Nome do vocal:** aceitar sufixos de tomada (`_vocals_dry`, `_voz_limpa`).

## Músicas montadas nessa conversa

| Música | Tom / tempo | Observação |
|---|---|---|
| virada-dois | — | base "Remix_of_vdb" |
| gnt ("A gente") | Si♭ maior, 92,3 BPM | — |
| qne-maq | Mi menor (riff Em7–Em7♭5), 86,1 BPM | limpeza teórica completa do instrumental |
| raio-x | Ré# menor, ~160 BPM | transcrição MIDI de "Voodoo Child (Slight Return)"; trabalho pesado de percussão |

## Bateria por peça: `stem-mastering/` (repo audio, PR #33)

- `separate.py` (DrumSep: bumbo, caixa, tons, chimbal, ride, crash + resíduo), `drums.py` (transient shaper + EQ + compressor por peça, resíduo intocado, teto de pico; `--humanize-hh`), `master.py` e `check.py` (comparação com volume igualado).
- Reproduz a master entregue de raio-x a −90 dB.

## A lição do pandeiro (e por que o shaker real funcionou)

- **Tentativa:** reconstruir um pandeiro real a partir de recortes de gravação. Resultado com falhas: **as platinelas nunca param entre os golpes**, então não existe ponto limpo de corte. É como montar frases recortando palavras de jornal.
- **Híbrido:** pele de frame drum + platinelas de pandeirola da biblioteca **VCSL** (domínio público, CC0) funcionou parcialmente, mas não é um pandeiro.
- **O que deu certo:** trocar o shaker robótico da IA por **golpes reais de shaker da VCSL**, ida no tempo e volta no contratempo, nos mesmos golpes do original. Nenhuma tomada se repete duas vezes seguidas, há variação de ±25 cents, nível e tempo, e ele abaixa 3 dB sob a voz. Aprovado: *"Ficou incrível, hein. Parabéns."*
- **Princípio:** a variação humana precisa vir de **movimento gravado de verdade** (ida/volta, tomadas diferentes), não de mudanças de nível aplicadas ao mesmo som.

## Bibliotecas de percussão brasileira (pesquisa)

Muletone, Urutu Audio, Sonokinetic, VCSL, Splice, Plugin Boutique, 85audio e Loopmasters. Atenção: várias são **Kontakt versão completa** (não rodam sem DAW nem no Kontakt Player). Para trabalho sem DAW, servem as que vêm em WAV (VCSL é CC0).

## Armadilhas de ambiente (Colab)

- `resampy<0.4.3` quebra com setuptools 81 (`pkg_resources`); o `audio-separator` importa `audioread` sem declarar.
- O GAME só publica pesos ONNX, e o ADT_STR exige Python < 3.13.
- Depois de um `git push`, faça *Runtime ▸ Disconnect and delete runtime*, ou o Colab roda o código antigo.
