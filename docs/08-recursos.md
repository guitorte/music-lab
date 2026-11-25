# Recursos: modelos, repositórios e ferramentas

Pesquisa de 25/11/2026 no Hugging Face, no GitHub e no arXiv, organizada pelas etapas do fluxo (`01-pipeline.md`).

- ✅ = já usado neste laboratório
- ⭐ = próximo a testar

## 1. Separação de stems e limpeza da voz

| Recurso | O que é | Link |
|---|---|---|
| ✅ MSST (ZFTurbo) | Framework de treino e inferência para MDX, Demucs, RoFormers (Band Split e Mel-Band), BSMamba2 e Apollo. Foi o motor dos testes de limpeza da voz. | https://github.com/ZFTurbo/Music-Source-Separation-Training |
| ✅ Modelos da comunidade UVR | Mel-RoFormer "kim ft2 bleedless" (voz com menos vazamento) e "denoise" do aufr33; configs + checkpoints | https://huggingface.co/Politrees/UVR_resources |
| ✅ Apollo / Apollo vocal | Restauração generativa de artefatos de codec e separação. É lento em CPU: cerca de 36× o tempo real, com blocos de 3 s. | https://github.com/JusperLee/Apollo · https://huggingface.co/oulianov/Apollo-vocal-msst |
| python-audio-separator | Os mesmos modelos numa linha de comando simples | https://github.com/nomadkaraoke/python-audio-separator |
| Mel-RoFormer (artigo) | Separação de voz + transcrição da melodia | https://arxiv.org/abs/2409.04702 |

O Demucs foi arquivado em jan./2025; os RoFormers são o caminho atual.

## 2. Transcrição de áudio para MIDI

| Recurso | O que é | Link |
|---|---|---|
| ✅ Basic Pitch / ADTOF | Pipeline atual do repo `audio`. O Basic Pitch deixa as notas +1/3 de semitom agudas por causa dos pitch bends; ver `06`. | repo `guitorte/audio` |
| MuScriptor (2026) | Transcrição aberta com vários instrumentos, de qualquer gênero. Pesos liberados mediante cadastro. | https://github.com/muscriptor/muscriptor · https://huggingface.co/MuScriptor/muscriptor-large |
| YourMT3+ | Vários instrumentos + voz. Demo no Hugging Face; em CPU leva mais de 3 min para 30 s de áudio. | https://github.com/mimbres/YourMT3 |
| GAME (OpenVPI) / ADT_STR | Melodia da voz / bateria com força dos golpes (no bake-off) | https://github.com/openvpi/GAME · https://arxiv.org/abs/2601.09520 |

## 3. Análise: tempo, estrutura, acordes

| Recurso | O que é | Link |
|---|---|---|
| ⭐ Beat This! (CPJKU) | Batidas e tempos fortes; MIT, com notebook no Colab. A grade atual chega a desviar 28 ms. | https://github.com/CPJKU/beat_this |
| ⭐ All-In-One (mir-aidj) | Tempo, batidas, tempos fortes e seções rotuladas (intro, verso, refrão…). Automatizaria o mapa que hoje vem do SRT. | https://github.com/mir-aidj/all-in-one |
| madmom | Biblioteca clássica de análise rítmica (instalar a versão do GitHub) | https://github.com/CPJKU/madmom |
| BTC | Reconhecimento de acordes; segue como referência ("professor") em trabalhos de 2026 | https://arxiv.org/abs/2602.19778 |
| ChordCoT | Junta várias ferramentas, converte para texto e deixa um LLM corrigir os acordes | https://github.com/WildHoneyPie/ChordCoT |

## 4. Arranjo e groove em MIDI

| Recurso | O que é | Link |
|---|---|---|
| Anticipatory Music Transformer | Gera acompanhamento para uma melodia dada (infilling) | https://arxiv.org/abs/2306.08620 |
| MIDI-GPT | Preenche material por trilha e por compasso, em General MIDI | https://arxiv.org/abs/2501.17011 |
| AccoMontage | Acompanhamento a partir de cifra + melodia | https://arxiv.org/abs/2108.11213 |
| GrooVAE + Groove MIDI Dataset | Humanização (força e microtempo) aprendida de bateristas reais | https://magenta.tensorflow.org/groovae |
| bossa-groove | Humaniza bateria imitando um baterista de bossa nova | https://github.com/dhunstack/bossa-groove |

## 5. Do MIDI ao som

| Recurso | O que é | Link |
|---|---|---|
| ✅ VCSL / VSCO-2 (CC0) | Percussão, sax, metais e cordas | https://github.com/sgossner/VCSL · https://github.com/sgossner/VSCO-2-CE |
| ✅ sfzinstruments | Rhodes (jRhodes3d) e baixo (Growlybass), entre outros | https://github.com/sfzinstruments |
| ✅ Cavaquinho (Decent Samples) | Gratuito: 3 variações por nota, gravado com captador + microfone de fita | https://www.decentsamples.com/product/cavaquinho/ |
| ConvertWithMoss | Converte bibliotecas do Kontakt versão completa (Muletone, Urutu…) para SFZ e outros formatos | https://www.kvraudio.com/forum/viewtopic.php?p=8751111 |
| MIDI-DDSP | Síntese neural de 13 instrumentos; num teste de audição, mais realista que um sampler profissional | https://arxiv.org/abs/2112.09312 |
| Spectrogram Diffusion | MIDI com vários instrumentos para áudio | https://github.com/magenta/music-spectrogram-diffusion |
| CoSaRef | Toca as amostras a partir do MIDI e depois "refina" com um modelo generativo; ataca o "som de MIDI" | https://arxiv.org/abs/2410.16785 |
| ✅ Suno Studio | Gera áudio a partir de clipes MIDI (plano Premier) | https://suno.com/release-notes/studio-improved-midi |

## 6. Gerar ou editar a música inteira (aberto)

| Recurso | O que é | Link |
|---|---|---|
| ⭐ ACE-Step 1.5 | Cover a partir de áudio, repintar e editar trechos, separar stems; MIT. Alternativa aberta ao Suno para "regravar" o arranjo. | https://github.com/ACE-Step/ACE-Step-1.5 |
| MIDI-SAG (ComposerFlow) | Acompanhamento condicionado à melodia da voz em MIDI; código anunciado | https://arxiv.org/abs/2602.22029 |

## 7. Editar a voz e a letra

| Recurso | O que é | Link |
|---|---|---|
| ⭐ YingMusic-Singer | Regenera a voz com a letra modificada, mantendo melodia e ritmo; código e pesos públicos | https://github.com/ASLP-lab/YingMusic-Singer |
| SoulX-Singer | Síntese de voz cantada aberta (42 mil horas de treino) | https://github.com/Soul-AILab/SoulX-Singer |

## 8. Mix e master

| Recurso | O que é | Link |
|---|---|---|
| Matchering 2.0 | Master por referência: RMS, resposta de frequência, pico e largura estéreo da faixa de referência (GPL-3.0) | https://github.com/sergree/matchering |
| Diff-MST | Mixa as faixas inferindo a produção de uma música de referência | https://arxiv.org/abs/2407.08889 |
| pyloudnorm | LUFS (BS.1770), já usado em `lib/` | https://github.com/csteinmetz1/pyloudnorm |

## 9. Dados de referência

| Recurso | O que é | Link |
|---|---|---|
| ⭐ BRID | 367 faixas de instrumentos rítmicos brasileiros (samba, partido-alto, samba-enredo, capoeira, marcha), gravadas em estúdio; carregável pelo `mirdata`. Fonte para moldes de acento e microtempo de surdo, pandeiro e tamborim reais. | https://zenodo.org/records/14051323 |
| Separação de percussão brasileira | U-Net treinada no BRID para isolar o surdo | https://arxiv.org/abs/2503.04995 |

## Próximos testes sugeridos

1. Beat This! no lugar da grade atual, comparando o desvio contra os onsets.
2. All-In-One para gerar o mapa de seções automaticamente.
3. BRID para tirar moldes de groove por instrumento, em vez de um molde único.
4. ACE-Step 1.5 (cover/repaint) e YingMusic-Singer (troca de palavras), quando houver GPU (Colab).
