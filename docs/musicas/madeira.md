# Madeira (Remix, Angela) — correções de voz (26/11/2026)

Faixa do Suno, 44,1 kHz, −14,1 LUFS, sem stems. Pedido: "Vigando" em vez de "ligando" (1:30,8 e 2:19,4) e uma vogal ou pausa
arrastada (1:36–1:38 e 2:25–2:27). Scripts `md_offsets.py`, `md_edit.py`.

- Voz separada com Mel-RoFormer Kim FT2 bleedless (32 min de CPU para 191 s). Instrumental = mix − voz; reseparar o instrumental
  nas janelas não achou voz residual (só 0,25 s a −28,7 dB).
- O trecho "Não, não liga pra ninguém / Ela não tá ligando pra nada também / Quem não ouve conselho, ouve coitado, hein" aparece
  em 0:37 (1 vez), 1:28 + 1:35 (2 vezes) e 2:16 + 2:23 (2 vezes).
- **Diagnóstico das 2ªs passadas (WhisperX + grade de tempos):** "não liga pra ninguém" entra 0,5 s adiantado, "ela não tá ligando
  pra nada" ~1 s adiantado (2 tempos), "também" fica segurado, "Quem" volta ao lugar e "ouve coitado, hein" atrasa 0,3 s.
  As duas 2ªs passadas têm o mesmo desvio.
- **Correção:** transplante da voz de 0:37 (mesma cantora, mesma tomada). 1ªs passadas: só a linha "Ela… também"; 2ªs: a frase
  do 1º "Não" ao "hein". Deslocamento pela voz (50,05 s e 98,74 s; período real 0,48588 s = 123,5 BPM) + ajuste fino pela
  coincidência de batidas (≤ 10 ms). Cortes em pausas comuns (≤ −49 dBFS). Ganho da voz +1,5 a +2,5 dB (loudness casada).
- Fora das janelas: idêntico amostra a amostra (21,2 s alterados). I −14,1 LUFS, LRA 4,6 LU, pico verdadeiro +0,3 dBTP:
  iguais ao original.
