# Reescrita de arranjo em MIDI sob a voz original

Primeira versão feita em 24/11/2026 com a faixa gerada **"Mente"**: arranjo novo, render com FluidSynth, mix com o stem vocal original e master. Scripts em `tools/arrange/` (`rw1`–`rw7`). Os parâmetros da música estão no topo de cada script e precisam ser trocados para outra faixa.

## Etapas

| # | Script | O que faz | Resultado em "Mente" |
|---|---|---|---|
| 1 | `rw1_grid.py` | grade de tempos a partir da mix (librosa com `start_bpm` próximo + `tightness 400`, deslocada pela mediana dos onsets), fase do surdo, chroma por tempo, fundamentais do baixo (pyin) | 90,67 BPM, 288 tempos, surdo forte nas fases 0 e 2, Lá maior |
| 2 | `rw2_chords.py` | acordes a cada meio compasso: moldes {maior, menor, 7, m7} × 12, prior diatônico, bônus quando o baixo confirma a fundamental, Viterbi com penalidade de troca | ajuste médio de 0,78 |
| — | (checagem) | **conferir os acordes contra a melodia** (pyin no vocal): % de notas do vocal em notas do acorde e na escala | Ré menor batia com o Dó# do vocal → trocado por Ré maior; 83% das notas do vocal na escala |
| 3 | `rw3_compose.py` | estrutura (whisper + perfil de loudness + pausas da banda) e composição das partes | intro, verso, pré, refrão, quebra, pré, refrão, outro; 4 *stops* |
| 4 | `rw4_midi_render.py` | MIDI com mapa de tempo tempo a tempo (PPQ 480), um `.mid` por parte + o completo; render FluidSynth (FluidR3_GM) | 8 trilhas |
| 5 | `rw7_surdo.py` | surdo sintético afinado em Lá (55 Hz, queda de afinação, aberto/abafado) + corpo do tom GM | grave controlado |
| 6 | `rw5_mix.py` | controle de pico por parte, loudness por parte nas proporções da banda real, pan, reverb de convolução curta, voz 3 LU abaixo da banda, passa-baixa 16,5 kHz | 7 camadas ativas em média |
| 7 | `rw6_master.py` / `tools/master.py` | cadeia padrão, rides nos refrões | −12 LUFS, limiter p99 2,9 dB, Vorbis −1,75 dBTP |

## Regras de composição usadas (pagode)

- **Surdo:** forte nos tempos 1 e 3 do compasso (fase medida na faixa), fraco nos outros; no pré-refrão e no refrão, bumbo grave e antecipação na 4ª semicolcheia.
- **Tantã, pandeiro e ganzá** em semicolcheias com o **molde de acentos da banda real** (1,00 / 0,23 / 0,99 / 0,59) e microatraso de 6 ms na 2ª e 3 ms na 4ª.
- **Tamborim** (padrão de 16 semicolcheias) e **repique** só no refrão.
- **Baixo contínuo:** fundamental no tempo forte, quinta antecipada na 4ª semicolcheia, oitava no refrão, nota de aproximação cromática para o próximo acorde.
- **Cavaco:** acordes em voicing fechado (condução de vozes mínima), cortes curtos em semicolcheia com o molde de acentos; na quebra, só colcheias.
- **Violão de náilon:** arpejo em colcheias. **Pad** sustentado em todas as seções. **Piano elétrico** com antecipações e **cordas** suaves só nos refrões.
- **Dinâmica por seção:** intro 0,45, verso 0,65, pré 0,8, refrão 1,0, quebra 0,5, outro 0,75 (fator de velocity).
- **Humanização:** ±4 ms de jitter e ±5 de velocity.
- **Stops:** nenhuma nota começa dentro das pausas originais, e as que atravessam são encurtadas.

## Limites conhecidos (v1)

- Timbres General MIDI: soa como uma demo bem tocada, não como gravação. O ganho real está em arranjo, camadas e groove; os timbres melhoram trocando os instrumentos (samples reais, por exemplo VCSL, ou bibliotecas numa DAW).
- O punch do surdo no barramento de percussão ficou em ~16 dB contra 21 da banda real (mesmo método, stem com stem).
- Harmonia extraída do áudio da IA: conferir sempre contra a melodia.
- Estrutura, seções e *stops* ainda são escritos à mão no topo de `rw3_compose.py`.

## Próximos passos naturais

1. Detectar seções e *stops* automaticamente.
2. Trocar os timbres GM por samples reais (o caminho do shaker VCSL em raio-x funcionou; ver `06-transcricao-midi.md`).
3. Derivar o molde de acentos de outras referências (outros gêneros), em vez de um molde fixo de pagode.
4. Exportar cada parte em WAV para montagem externa.
