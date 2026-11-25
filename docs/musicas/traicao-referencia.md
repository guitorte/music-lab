# "Traição" — referência gravada (pagode romântico)

Música de outros autores, enviada pelo autor em 25/11/2026 como **referência**: 6 stems (BS-RoFormer SW) + MIDIs do
bakeoff (Basic Pitch, ADTOF, ADT_STR, GAME). Só medidas; a letra não é reproduzida aqui. Scripts: `arquivo/scripts-sessao-2026-11/tr_*.py`.

## Ficha

- 206 s de arquivo, música até ~189 s (depois, silêncio). 76 BPM, compasso de 2/4. Mix −10,5 LUFS, pico −0,7 dBFS.
- Voz masculina, D3–A4 (mediana D4).
- Forma: verso (voz + teclado) → verso com banda leve → pré → **parada + virada** → refrão ×2 → verso 2 já com banda cheia
  → pré com parada → refrão ×2 → final que volta à 1ª frase da música.

## Groove

Agudos da bateria (platinelas/ganzá), % dos tempos em que cada semicolcheia é tocada (medição manual, `tr_t2`):

| | 1ª | 2ª | 3ª | 4ª |
|---|---|---|---|---|
| tempo 1 | 77 | 12 | 56 | 39 |
| tempo 2 | 77 | 15 | 60 | 63 |

- **A 2ª semicolcheia é quase vazia; a 4ª é tocada.** Mesmo desenho da referência ao vivo (1.00 / 0.23 / 0.99 / 0.59).
- Surdo (grave): 1º tempo e 2º tempo (~70% cada) + **4ª semicolcheia do 2º tempo** (59%), a puxada para o compasso seguinte.
  No MIDI do ADTOF o golpe do 2º tempo é detectado 72% das vezes contra 32% do 1º: o 1º é o abafado, o 2º é o aberto.
- Microtempo pequeno: atrasos de 3 a 8 ms nas semicolcheias fracas (2ª dos agudos +8 ms, 3ª dos médios no 2º tempo +6 ms).
- `groove_report.py` dá acentos 1.00 / 0.95 / **1.6** / 1.02 aqui: mede só a força quando há golpe. Por isso agora o
  relatório também mostra a presença (`slot_presence`: 88 / 34 / 78 / 71 % por aquele detector). Lição 18.

## Timbres (comparados com os stems do Suno de "Mente Vit", mesmo método, `tr_t3`)

| stem | Traição | Mente Vit (Suno) |
|---|---|---|
| voz | brilho 971 Hz, médios 1–4 kHz −6,7 dB, largura −12,8 dB | 765 Hz, −11,1 dB, −17,3 dB (mais escura e mais estreita) |
| bateria | médios 1–4 kHz **−18 dB**, crista 10,6 dB | **−28 dB**, 9,6 dB: grave + chiado, "oca" no meio |
| baixo | médios 1–4 kHz **−13,6 dB** (ataque de dedo/corda), F#1–C#4 | **−48,6 dB**: só grave, sem ataque |
| violão/cavaco | B2–D5, maioria D4–G4 (região do cavaco) + graves de violão | mais ar (−29 dB acima de 10 kHz) |
| teclado | ativo 85%, muito largo (−1,6 dB), escuro | ativo 32% |
| outros | ativo 76%, F#3–B4, entra e sai (textura) | ativo 34% |

## Arranjo e dinâmica (`tr_t5`–`tr_t8`)

| seção | início (s) | mix LUFS | voz − banda | percussão (graves/tempo) |
|---|---|---|---|---|
| verso 1a: voz + teclado | 1,7 | −14,8 | +4,0 | 0 |
| verso 1b: banda leve | 22,8 | −13,7 | +1,0 | ~0,8 |
| pré 1 | 40,1 | −13,9 | +1,2 | ~0,5 |
| parada + virada | 46,4 | −11,0 | +1,9 | 0 → crescendo |
| refrão ×2 | 52,7 | −9,8 | −0,6 | 6–7 |
| verso 2 (banda cheia) | 106,7 | −9,8 | 0,0 | ~6 |
| pré 2 com parada | 123,8 | −9,9 | +1,8 | 0 → 6 |
| refrão final ×2 | 131,9 | −9,5 | −0,2 | 6–7 |
| final (1ª frase) | 185,2 | −14,0 | +5,7 | 0 |

- **O salto é de levada, não só de volume.** Da banda leve ao refrão: +4 LU, mas a densidade da percussão grave vai de ~1
  para 6–7 golpes por tempo; agudos de 1,5 para 3,5; violão/cavaco de 1,2 para 3,5–4.
- **Parada:** a percussão some por exatamente 1 compasso de 2/4 (−40 dB) sob a voz; baixo segura, violão e teclado ficam
  8–16 dB mais baixos, a camada "outros" sobe 2–4 dB. Depois, 1 golpe e uma virada de 2 compassos em crescendo
  (bateria −27 → −15 dB) que cai cheia **na primeira palavra do refrão**. Na 2ª vez, a mesma parada no mesmo ponto da letra.
- **Depois do 1º refrão o nível quase não muda** (−9,5 a −9,9 LUFS até o fim). O contraste da 2ª metade vem da parada do
  pré e da camada "outros" no refrão final (+8 dB contra o 1º refrão), não de volume.
- Faixa de loudness de curto prazo (3 s): p10 −14,4, p95 −9,0 → 5,4 LU; quase toda a variação está no 1º minuto.
- Voz − banda: versos +1 a +4, refrões −0,6 a −0,2. A automação de "Mente" (versos +3,5, refrão −2,5) põe a voz
  **mais baixa no refrão** do que esta gravação.
