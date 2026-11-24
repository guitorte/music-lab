# Edição cirúrgica: palavras, emendas, samples

Objetivo comum: **mudar o mínimo e provar que o resto ficou idêntico.**

## Trocar palavras ("Virada no Diabo", "Que nem eu ITA")

1. **Localizar** com faster-whisper (medium, `pt`, timestamps por palavra).
2. **Testar se os stems somam a faixa** (ganhos por mínimos quadrados + resíduo).
   - **Somam** (resíduo ~−69 dB): a edição é aritmética exata, `out = mix + w·(novo − velho)` dentro da janela; fora dela, amostras idênticas.
   - **Não somam** (separados, resíduo −3 a −16 dB): ajuste NNLS de potência por bin (voz + instrumental), máscara de Wiener com piso de −25 dB e ressíntese.
3. **Cortar só em pausas compartilhadas ou consoantes.** Se o crossfade cair em som vozeado, conferir que a afinação bate (±25 cents). Crossfades curtos, de 20 a 120 ms.
4. **Casar loudness** da palavra trocada (±0,3 LU) e as bandas contra a mesma palavra em outros refrões.
5. **Transplante** quando a nova tomada da IA soa estranha. A dobra estéreo dela costuma divergir (correlação L/R 0,19–0,37 contra o original). Solução: copiar a mesma palavra de outros refrões do cantor original, **refrão 1 no L e refrão 3 no R**, o que recria uma dobra natural, com EQ casado ao contexto.
6. **Conferir** transcrevendo a faixa inteira de novo.

Casos: "casal" ganhou um ruído (encurtar o crossfade de saída para 20 ms no ponto de afinação igual); "a cara" ficou bizarro (resolvido com o transplante); "achar" tinha um "s" a mais.

## Tirar ou reordenar seções ("Coca_na")

- Refrões não são idênticos amostra a amostra, e o tempo deriva.
- **Medir o deslocamento pela coincidência das batidas** (onsets em 40–120 Hz e 4–12 kHz dentro de ±8 ms), seção por seção.
  - A correlação de envelope travou uma semicolcheia fora (43,8195 s em vez de 43,722 s), e o autor ouviu na hora: *"pareceu meio apressado"*.
- Emendar numa pausa vocal comum; crossfade de potência igual para tomadas não correlacionadas.
- Versões entregues: A (ponte → refrão 2) e B (ponte → refrão 2 → refrão 3); B masterizada com a ponte +4 dB.

## Inserir um sample ("Marina Chinesa")

- Medir a afinação da música (`librosa.estimate_tuning`) e a nota exata do sample em cents (pyin).
- Reafinar pelos cents medidos por reamostragem, sem phase vocoder, mirando uma nota do acorde. Lá estava em Sol6 −35 cents, então +35 cents. Um semitom inteiro passava do ponto e virava Sol#.
- Colocar em tempos fortes (fase mais forte do bumbo), em vãos instrumentais que terminam antes da próxima frase; HPF de ~180 Hz; uns 2,5 LU abaixo da seção.

## Tirar ruídos e artefatos localizados

Ver a tabela de artefatos em `02-masterizacao.md`. Exemplo: "Virada no Diabo (Remastered)", ruído constante por volta de 2:00, que eram as linhas de 12,8 kHz e 850 Hz.

## Multidão em gravação ao vivo

O ruído de público costuma ficar no stem `other`, largo e fora de fase. Controlar com M/S (baixar o side) e envelopes de nível, sem cortar, porque a multidão também é energia do refrão. Tirar demais contribuiu para o "perdeu impacto" do pagode.
