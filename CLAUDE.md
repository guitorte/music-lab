# Instruções para sessões de IA neste repositório

## Quem e como

- O autor escreve letras originais, gera as faixas com IA (Suno) e **não tem DAW**. Todo processamento de áudio/MIDI, render e entrega é feito pela sessão, em Python.
- Responda em **português** (o autor alterna com "br"/"usen"; o padrão nas sessões de música tem sido português).
- Você não ouve. Decida por medidas e explique em linguagem simples, com números só quando ajudam a decidir. O ouvido do autor é o juiz final: quando ele relatar algo, ache a medida que explica antes de mexer (`docs/07-licoes.md`).
- Preferências estáveis: voz integrada (não na frente demais); refrão como ponto alto; pausas preservadas; groove acima de volume.

## Antes de trabalhar

- Leia `docs/00-visao.md` (o objetivo) e o documento da etapa: master → `02`, edição → `03`, groove/mix → `04`, arranjo → `05`, MIDI → `06`.
- Use `lib/` e `tools/` em vez de reescrever a cadeia. Se precisar mudar a cadeia, mude em `tools/master.py` e documente em `docs/02-masterizacao.md`.

## Padrões de entrega

- WAV 24-bit + MP3 320; `.mid` quando houver arranjo; cópias A/B com volume igualado quando houver comparação.
- −10.5 a −13 LUFS; **−2 dBTP**; limiter p99 ≤ 2–3 dB; true peak pós-codec conferido (`lib.metrics.codec_peaks`).
- Manter a taxa de amostragem da fonte.
- Edições: provar que o resto ficou idêntico.

## Manutenção do repo

- Toda faixa trabalhada ganha uma linha em `docs/faixas.md`; todo erro novo com princípio geral vai para `docs/07-licoes.md`.
- Scripts de sessão (caminhos fixos) vão para `arquivo/`; o que for reutilizável vira função em `lib/` ou CLI em `tools/`, testado num arquivo real.
- Arquivos de áudio não entram no git (ver `.gitignore`).
