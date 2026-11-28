# Pagodizar melodias do MIDIGEN 1.0

O autor gerou ideias no MIDIGEN 1.0, um gerador web de melodias aleatórias. Ele escolhe escala, tom, compassos, BPM, duração dominante, oitava, arpejos, pausas e acordes. Pediu para "pagodizar" três delas. Scripts: `arquivo/scripts-sessao-2026-11/pg_compose.py` (MIDI) e `pg_render.py` (prévia).

## O que o gerador entrega

- Grade reta: colcheias e semínimas, nenhuma síncope que segure sobre o tempo forte.
- Pausas gravadas como `note_on` na nota 0 com velocidade 0. É preciso ignorar a nota 0 ao ler.
- O "tom" escolhido nem sempre é o centro da melodia:
  - "G maior" saiu centrado em Mi (Em7 | C | B7 …);
  - "C maior" saiu centrado em Fá.

  A tonalidade é estimada pelo histograma de alturas com perfis de Krumhansl.
- Com *Chords* ligado, o arquivo não tem melodia: é um acorde aleatório a cada colcheia ou semicolcheia.

## Regras

1. **Escala de tempo:** 1 tempo do gerador = 1 colcheia do pagode, então um compasso 4/4 dele vira um compasso de 2/4 do pagode. Tudo sai a 76 BPM, o tempo medido em "Traição". A 144 BPM a velocidade real quase não muda.
2. **Ritmo:** as notas e a ordem ficam; o ritmo de cada compasso de 2/4 é trocado por duas células de 4 semicolcheias com o mesmo número de notas.
   - Células preferidas: `xx.x` (semicolcheia–colcheia–semicolcheia), `.x.x`, `.xxx`, `x..x`, `...x`.
   - Evitadas: `x.x.` (colcheias retas) e `xxxx`.
   - Bônus quando o compasso termina na 4ª semicolcheia e o seguinte começa sem nota no tempo 1. É a antecipação que atravessa a barra.
   - A duração vai até o próximo ataque, com no máximo 3/16 antes de uma pausa longa.
3. **Acentos da melodia** por posição: 88/70/80/96 (o acento fica na 4ª). Microtempo: 2ª semicolcheia +6 ms, 4ª +3 ms.
4. **Harmonia:** um acorde por compasso de 2/4, escolhido por Viterbi.
   - Encaixe: notas do acorde valem, notas estranhas em posição forte custam.
   - Cadências: V7→I, ii/IV→V7, V7 no penúltimo compasso, tônica no último.
   - Arquivo só de acordes: as notas de cada compasso são somadas e entram no mesmo Viterbi.
5. **Arranjo:** padrões de "Traição", na forma intro (2 compassos) → passada leve → parada e virada nos 3 últimos compassos → drop da v2 aprovada de Mente → passada cheia → acorde final.

## Resultados (28/11/2026)

| arquivo | tom estimado | acordes | síncopes antes → depois |
|---|---|---|---|
| Major G 8 compassos 144 BPM | Mi menor | Em7 C B7 Em7 C Em7 B7 Em7 | 6 → 16 |
| Major C 8 compassos 120 BPM | Fá maior | F Dm7 C7 F C7 F C7 F | 7 → 22 |
| Major G 20 compassos 84 BPM, acordes | Sol maior | G Em7 Am7 D7 G Am7 D7 G Em7 C D7 G Am7 D7 G D7 G Am7 D7 G | — |

Síncope aqui é nota que começa numa semicolcheia fraca (2ª ou 4ª) e segura sobre a posição forte seguinte (ver lição 25).

A passada cheia soa +1,7 a +2,0 LU acima da leve.

Masters:
- **melodias:** −13 LUFS, limiter p99 1,2–1,7 dB;
- **só acordes:** −13,5 LUFS. Sem melodia, a −13 o limiter passava de 3 dB.

True peak pós-codec ≤ −1,0 dBTP em todas.

A prévia usa flauta no lugar da voz: cavaco de amostras reais, violão GM, Growlybass limpo e surdo sintético mais corpo GM.
