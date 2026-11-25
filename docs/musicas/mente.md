# Mente

Letra original do autor. Faixa base: "Remix of Mente Vit – Treblo" (Suno), 190,8 s, 44,1 kHz, 90,7 BPM, Lá maior. As stems da IA somam a faixa com resíduo de −22 dB (separadas, não exatas). Transcrição com tempos: [`mente.srt`](mente.srt) (o bloco 28 tinha o tempo `00:01:00:50,800`, corrigido para `00:01:50,800`).

## Intenção do autor (24/11/2026)

> Começa mais intimista e lenta; no pré-refrão ("Entra outra vez na minha vida") já dá uma acelerada, com a banda imprimindo mais corpo, ritmo e groove; no refrão ("Mente, me engana") explode e troca a levada da música toda para um groove irresistível.

## Mapa (tempos do SRT → tempos da grade)

| Seção | Tempo (s) | Grade (tempos) | Letra |
|---|---|---|---|
| intro | 0–10,9 | 0–16 | — |
| verso 1 | 10,9–21,8 | 16–32 | As lágrimas que eu vejo… |
| verso 2 | 21,8–32,7 | 32–48 | As juras que eu escuto… |
| pré-refrão | 32,8–44,6 | 48–68 | Entra outra vez na minha vida… |
| refrão | 44,7–69,7 | 68–104 | Mente, me engana, faz uma cena… |
| pós-refrão | 69,8–82,8 | 104–124 | Vem me tirar da solidão… |
| instrumental | 83,5–93,8 | 124–140 | — |
| pré-refrão 2 | 93,8–105,7 | 140–158 | (E) entra outra vez… |
| refrão 2 | 105,8–129,8 | 158–196 | — |
| refrão repetido | 129,9–154,9 | 196–232 | ("Sabe que eu… sabe que eu amo novela") |
| final | 155,0–168,6 | 232–254 | Vem me tirar da escuridão… |
| fim instrumental | 168,6–190,8 | 254–fim | — |

**Paradas que existem na faixa** (banda muda, voz sozinha): 44,80–46,15 ("Mente," a capela); 47,70–48,15; 83,20–83,50; 99,05–99,50; 104,30–104,85; 106,15–106,65.

**Breques sugeridos pela quebra de linha da letra** ("Fala que eu sou / O amor da tua vida", "Sabe que eu / Amo novela", "Me diz que eu sou / O teu grande amor"). O cantor sustenta o "sou" sem pausa, então a banda dá um golpe e cala sob a nota e volta no "o amor". Tempos de palavra (whisper): golpe/volta em 57,5/58,5 · 78,8/79,5 · 110,9/112,2 · 118,9/119,8 · 134,8/136,2 · 142,8/143,8 · 163,5/164,7.

## Versões

| Versão | O que mudou | Medidas (master −12 LUFS) |
|---|---|---|
| v1 (`tools/arrange/rw*`) | arranjo contínuo, seções só com mais/menos força | refrão +2,6 LU sobre o verso; pré igual ao verso; o autor achou "muito flat" |
| v2 (`tools/arrange/v2/`) | três levadas (verso em meio-tempo intimista, pré acelerado, refrão pagode explosivo), convenção + rolo antes das paradas, prato na entrada, sopros respondendo nos buracos da voz, solo de sax com a melodia do refrão no instrumental, palmas no refrão repetido, final intimista que cresce, encerramento com acorde. Voz automatizada por seção | banda sozinha: refrão **+9,4 dB** sobre o verso 1; master: pré +3,0, refrão +4,6, final −0,5, fim +4,0 LU; limiter p99 2,8 dB; Vorbis −1,76 dBTP |
| v3 (`tools/arrange/v2/v3_mix_hibrido.py`) | autor: "a partir da entrada do refrão ficou SENSACIONAL", "preserve mais da base do arranjo original até o refrão". Intro e versos com o instrumental original do Suno no equilíbrio original com a voz; no pré, base original subindo +1,5 dB + camadas da v2 por cima (surdo marcando, percussão em semicolcheias, baixo sincopado, cavaco cortando, cordas, convenção e rolo); troca para a v2 dentro da parada de 44,8 s, que já existe na faixa original; do refrão em diante, v2 | banda: verso 1 −30,7, verso 2 −26,1, pré −19,0, refrão −16,4 LUFS; master: pré +4,2, refrão +5,7 LU sobre o verso 1; limiter p99 2,5 dB |

## Versão Vit com o arranjo de "Traição" (25/11/2026)

Pedido: adaptar todo o instrumental de "Traição" (`traicao-referencia.md`) ao MIDI da voz da Vit. As notas de Traição não
servem (outro tom, outros acordes, 76 BPM); foram transplantados os **padrões medidos**, aplicados aos acordes e à forma de
Mente (89 BPM, 2/4). Scripts `vt_*` (`vt_build.sh` reconstrói tudo).

| Estado de Traição | Seções de Mente | O que toca |
|---|---|---|
| abertura | intro, verso 1, final | voz + Rhodes (acorde no 1º tempo, notas de cima na 4ª e 7ª 16ª), baixo longo, cordas suaves |
| leve | verso 2 | surdo só no 2º tempo (+ puxada a cada 2 compassos), ganzá em colcheias, baixo com ataque no 2º tempo, violão baixo/acorde, cavaco ralo, Rhodes no tempo |
| pré | pré 1 | baixo só no 2º tempo, violão um acorde no 2º, Rhodes antecipando (4ª, 7ª e 8ª 16ª), cavaco acentos na 3ª, 5ª e 8ª |
| parada + virada | 1 compasso + 2 antes de cada refrão (40,4 s e 97,0 s) | percussão some; baixo e acordes seguram; cordas sobem; 1 golpe e crescendo de tantã/pandeiro até cair cheio no refrão |
| cheio | refrões, pós, solo, pré 2 | surdo abafado/aberto/puxada; pandeiro 0/−10/0/−6 dB; tantã + acento de repique na 4ª; baixo em linha contínua (mediana A2, como Traição); cavaco em 16ªs com acentos na 2ª, 3ª, 5ª e 8ª; Rhodes estéreo (jRhodes3d via sfizz) como tapete; cordas só nos refrões finais |
| final | depois da última nota da voz | acorde de Dó segurando 2 compassos |

Conferido contra Traição (`vt_check.py`), master −13 LUFS:

| Seção | mix rel. refrão | Traição | voz − banda | Traição |
|---|---|---|---|---|
| verso 1 (abertura) | −5,4 | −5,0 | +3,8 | +4,0 |
| verso 2 (leve) | −3,6 | −3,9 | +0,3 | +1,0 |
| pré 1 | −3,8 | −4,1 | +1,1 | +1,2 |
| refrões | 0 | 0 | −1,0 / −0,8 | −0,6 / −0,2 |
| final | −3,7 | −4,2 | +5,4 | +5,7 |

Voz −1 LU abaixo do contorno de Traição (preferência por voz integrada). Agudos da percussão por 16ª: 0 / −8,4 / 0 / −6,8 dB
(Traição 0 / −10 / 0 / −6). Punch do surdo nos refrões (master): 13,5 dB (Traição 13,4). Master: limiter p99 1,85 dB; picos
pós-codec −2,3 (MP3), −1,7 (Opus), −0,7 (AAC do ffmpeg). Teto −2,6 dBTP: com −2 o AAC do ffmpeg passava de 0 depois que o surdo
ganhou ataque.

