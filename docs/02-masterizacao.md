# Masterização

Base teórica: os livros do projeto, **Bob Katz** (*Mastering Audio*) e **Bobby Owsinski** (*The Mastering Engineer's Handbook*). Implementação: `tools/master.py` (cadeia) e `lib/dsp.py` (blocos).

## Alvos e regras

| Item | Regra | Fonte / motivo |
|---|---|---|
| Loudness | −10.5 a −13 LUFS integrado; escolher o mais alto que passe nas checagens | gênero + regra do limiter |
| Teto | **−2 dBTP** para masters mais altas que −14 LUFS | Spotify recomenda −2 dBTP para masters acima de −14 LUFS; faixas mais altas distorcem mais quando codificadas |
| Limiter | redução no **p99 ≤ 2–3 dB** | Owsinski |
| Transientes curtos | toleram 4–6 dB de redução → estágio rápido (janela 3 ms, release 8 ms, limiar no p99, máx. 4 dB) antes do limiter | Katz |
| Compressão | razões de 1,5 a 3:1; glue 1,5:1, ataque 30 ms, release 150–170 ms, ~1 dB nos trechos fortes | Katz |
| Comparação | sempre com volume igualado (cópia `AB_matched` no loudness da fonte) | Katz |
| Taxa de amostragem | manter a da fonte; se os stems vierem em outra taxa, reamostrar os stems, nunca a faixa | — |
| Entrega | WAV 24-bit (master), MP3 320 (escuta); `.mid` quando houver arranjo | — |

## A cadeia padrão (`tools/master.py`)

1. **HPF 25–28 Hz.**
2. **Graves mono:** M/S com o side passando por um HPF de 100–110 Hz; side +1,5 dB acima de 1 kHz para abrir.
3. **Transient shaper no surdo/bumbo (45–120 Hz):** ataque +1,5, cauda −2,5 dB. Aperta o grave sem tirar o golpe.
4. **EQ tonal:** 63 Hz −1 a −2 (acúmulo típico das mixes do Suno), 315 Hz −1, 1,2 kHz +1, presença 2,5 kHz +1,5 a +2, prateleira de 9 kHz +1,5 a +2.
   - *Exceção:* se o 63 Hz é o surdo que carrega o groove (pagode), não corte (`--lowcut-63 0`).
5. **De-harsh dinâmico** em 2,5–5 kHz e 6–12 kHz. Só reduz quando a banda passa da referência de 500–2000 Hz acima do seu p94; máximo de 3 dB.
6. **Snap de percussão:** shaper em 2–8 kHz, ataque +1,5.
7. **Compressão paralela (NY)** misturada a −8 dB: densidade de "front of house".
8. **Glue 1,5:1** com o detector passando por HPF de 150 Hz, para que o surdo não dispare o compressor.
9. **Ride de refrão:** +1 a +2 dB. Sobe em 0,12 s **dentro do silêncio da pausa** antes do refrão e desce em 1,5 s. O ouvinte sente o refrão maior sem perceber a automação.
10. **Estágio rápido** (opcional, `--no-fast` desliga).
11. **Limiter** com lookahead de ~5 ms e detecção true-peak 4×, iterado até o alvo.

## Checagens obrigatórias depois do render

- Redução do limiter no p99 (≤ 2–3 dB) e no máximo.
- **True peak depois de codecs** (`lib.metrics.codec_peaks`): MP3 320, **Ogg Vorbis q9 (Spotify)**, Opus 160 (YouTube), AAC 128k.
  - O AAC nativo do ffmpeg exagera picos em material com transientes muito secos (samples GM, percussão sintética): deu +2 dB a 256k numa faixa que fica a −1,7 em Vorbis. Use Vorbis/Opus como critério e o AAC como alerta.
- Diferença refrão − verso em LU (não achatar o contraste que a música tem).
- Punch do surdo antes/depois (não perder groove).
- Índice de voz (1–4 kHz vs 150–1000 Hz no mid): não deve subir muito mais que ~1 dB. O autor não gosta de voz na frente demais.
- Correlação L/R e perda em mono.

## Artefatos típicos do Suno (remover antes da cadeia)

| Artefato | Como achar | Como tirar |
|---|---|---|
| Tom fixo em 12.800 Hz | linha estacionária > 8 dB acima da mediana de 1/3 de oitava em > 50% dos quadros (STFT N=16384) | "clamp" espectral estreito (±6–12 Hz puxados à mediana da vizinhança), 2 passadas |
| Zumbido de ~850 Hz | idem; muito mais forte na faixa que no instrumental | idem |
| Pente de tons a cada ~100 Hz de 16,9 a 20 kHz | idem | idem, ou passa-baixa de 16,5 kHz |
| Topo plano até 20–22 kHz em todos os stems | espectro 16–20k tão forte quanto 12–16k | passa-baixa de 16,5 kHz (também evita picos nos codecs) |

*Cuidado:* linhas que oscilam alguns Hz ou caem em frequências de notas (61,5 Hz do baixo, 495/659/987 Hz) são música. Ficam.

## Armadilhas já vividas

- **Punch perdido no pagode:** glue, corte de 63 Hz e saturação do baixo comiam o surdo. Correção: detector do glue com HPF de 150 Hz, sem corte de 63 Hz, harmônicos do baixo só acima de 150 Hz.
- **"Perdeu impacto" no refrão:** a causa era a região de 400 Hz a 2,5 kHz cerca de 1 dB abaixo no refrão. Correção: presença +1,5 em 2,5k e ride +1.
- **Sopro estridente na intro de "Mente":** presença +3 dB, compressão paralela e snap empurravam o metal para o limiter. A fonte já tinha o metal até +40 cents desafinado. Correção: cadeia suave só na intro e intro 2,5 dB abaixo; o limiter passou a agir só em 4% da intro.
- **Compressão paralela levantando *ghost notes*** foi na direção errada: na banda real os ghosts são muito suaves (−30 dB).
- **Teto −1 dBTP** estourava depois do AAC 128k (+0,52 dBTP). Daí o padrão −2.
