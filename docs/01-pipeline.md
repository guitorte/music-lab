# O fluxo completo

Visão de ponta a ponta do que já foi feito (nov. 2026). Cada etapa aponta para o documento com os detalhes.

```
letra (autor)
   │
   ▼
gerador (Suno) ──► faixa .flac/.wav  ──────────────────────────────┐
   │                                                               │
   │  (opcional) stems do gerador ou separação                     │  caminho curto:
   │  htdemucs_6s · BS-RoFormer SW · DrumSep (repo audio)          │  master direta
   ▼                                                               │  (02-masterizacao)
stems: vocals · drums · bass · guitar · piano · other               │
   │                                                               │
   ├─► edição cirúrgica: palavras, emendas, samples (03)            │
   │                                                               │
   ├─► transcrição MIDI: Basic Pitch / ADTOF / GAME / MuScriptor    │
   │      → limpeza → montagem → MIDI-TEXT (REMI) (06)              │
   │                                                               │
   ├─► diagnóstico: groove, camadas, timbres vs banda real (04)     │
   │                                                               │
   ├─► reescrita do arranjo em MIDI sob a voz original (05)         │
   │      grade → harmonia → estrutura → partes → render            │
   │                                                               │
   ▼                                                               │
mix (proporções da banda de referência)  ──────────────────────────┤
                                                                   ▼
                                                   master: −10.5 a −13 LUFS, −2 dBTP
                                                   checagens: limiter p99, codecs, A/B
```

## Onde mora cada coisa

| Coisa | Onde |
|---|---|
| Separação, transcrição, bake-off de motores, montagem MIDI→REMI, `stem-mastering/` (bateria por peça) | repo **`guitorte/audio`** (notebooks Colab + módulos) |
| Método, medidas de referência, masterização, edição, reescrita de arranjo, diário de faixas | **este repo** (`music-lab`) |
| Instruções compactas para uma sessão de IA masterizar/editar | `skills/mastering-ai-tracks/SKILL.md` (também salva como skill da conta) |

## Ferramentas sem DAW

Tudo roda em Python: `numpy`, `scipy`, `soundfile`, `pyloudnorm`, `librosa`, `mido`/`pretty_midi`, `faster-whisper` (letra e estrutura), `ffmpeg` (I/O e codecs) e `fluidsynth` + `FluidR3_GM.sf2` (render de MIDI). Ver `requirements.txt`.

## Regra de ouro do processo

O assistente **não ouve**. Toda decisão sai de uma medida (LUFS, true peak, espectro, punch, acentos, camadas, correlação L/R), e o ouvido do autor é o juiz final. Quando o autor diz "ficou apressado", "perdeu punch" ou "o sopro estourou", a tarefa é achar a medida que explica a queixa antes de mexer.
