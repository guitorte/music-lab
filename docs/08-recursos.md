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

## 10. Áudio e voz em geral

Fora do fluxo principal, mas úteis em qualquer trabalho de voz e áudio. Clonar ou converter voz só com voz própria, voz liberada ou voz gerada por você; a voz de uma pessoa real exige autorização dela.

### Clonar voz falada (texto → voz)

| Recurso | O que é | Link |
|---|---|---|
| Voxtral TTS | Mistral, 4B, 9 línguas. Os pesos abertos (CC BY-NC) trazem só vozes prontas; clonar exige a API | https://huggingface.co/mistralai/Voxtral-4B-TTS-2603 |
| X-Voice | 0,4B; clona sem transcrição da referência, em 30 línguas | https://github.com/sunnyxrxrx/X-Voice |
| VoxCPM2 | Clonagem sem treino e controle da voz por texto | https://github.com/OpenBMB/VoxCPM |
| XTTS v2 | Coqui, multilíngue, clássico | https://huggingface.co/coqui/XTTS-v2 |
| Fish Speech | TTS com clonagem | https://github.com/fishaudio/fish-speech |
| CosyVoice | TTS com clonagem | https://github.com/FunAudioLLM/CosyVoice |
| IndexTTS-2 | TTS com controle de duração e emoção | https://github.com/index-tts/index-tts |
| Chatterbox | TTS aberto da Resemble | https://github.com/resemble-ai/chatterbox |

### Converter voz e canto (trocar o timbre, manter a interpretação)

| Recurso | O que é | Link |
|---|---|---|
| ⭐ Seed-VC | Conversão de fala e canto sem treino, com 1 a 30 s de referência. Daria um timbre consistente à voz do Suno entre versões | https://github.com/Plachtaa/seed-vc |
| RVC | O clássico; treina um modelo por voz | https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI |
| R2-SVC | Feito para voz com ruído e artefatos de separação | https://arxiv.org/abs/2510.20677 |
| Poly-SVC | Preserva as harmonias que sobram no stem de voz | https://arxiv.org/abs/2605.12310 |

### Editar fala e canto

| Recurso | O que é | Link |
|---|---|---|
| AuK | Tencent, 1,5B: insere, apaga ou troca trechos falados e cantados; também troca letra preservando melodia, remove respirações, limpa e separa | https://huggingface.co/tencent/AuK |
| MeloDISinger | Troca a letra cantada preservando melodia e duração | https://arxiv.org/abs/2606.30580 |

### Limpar e restaurar

| Recurso | O que é | Link |
|---|---|---|
| ClearerVoice-Studio | Realce, separação, super-resolução e extração da voz de uma pessoa | https://github.com/modelscope/ClearerVoice-Studio |
| StuPASE | Cisco: tira ruído e reverb com poucas alucinações. Só fala, 16 kHz | https://huggingface.co/cisco-ai/stupase |
| DPDFNet | Evolução do DeepFilterNet2, tempo real, tem versão 48 kHz | https://github.com/ceva-ip/DPDFNet |
| Resemble Enhance | Remoção de ruído e realce de fala | https://github.com/resemble-ai/resemble-enhance |
| AudioSR | Devolve agudos perdidos, até 48 kHz | https://github.com/haoheliu/versatile_audio_super_resolution |
| AudioLBM | Super-resolução que supera o AudioSR; vai até 192 kHz | https://audiolbm.github.io/ |
| SAGA-SR | Super-resolução guiada por texto (KAIST) | https://arxiv.org/abs/2509.24924 |

### Transcrever e alinhar a letra

| Recurso | O que é | Link |
|---|---|---|
| ✅ WhisperX | Tempo por palavra com alinhamento forçado. Testado: ver abaixo; virou `tools/alinhar_palavras.py` | https://github.com/m-bain/whisperX |
| lyric-align | A letra já está certa, só faltam os tempos; exporta LRC, SRT, ASS, JSON | https://pypi.org/project/lyric-align/ |
| UltraSinger | Letra + nota cantada por palavra (formato karaokê) | https://github.com/rakuri255/UltraSinger |
| Montreal Forced Aligner | Alinhador tradicional por fonemas | https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner |
| HeartTranscriptor | Whisper ajustado para letra em música | https://huggingface.co/HeartMuLa/HeartTranscriptor-oss |

### Afinação

| Recurso | O que é | Link |
|---|---|---|
| Parselmouth (Praat) | Detecção de altura e PSOLA em Python: base de um autotune simples | https://github.com/YannickJadoul/Parselmouth |
| pyworld (WORLD) | Separa altura, envelope e aperiodicidade para ressintetizar afinado | https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder |
| Diff-Pitcher | Correção de afinação neural (difusão) | https://github.com/haidog-yaqub/DiffPitcher |
| KaraTuner | Correção de afinação neural (Tencent Music) | https://arxiv.org/abs/2110.09121 |

### "DAW sem DAW" em Python

| Recurso | O que é | Link |
|---|---|---|
| ✅ DawDreamer | Hospeda instrumentos e efeitos VST3, Faust, automação. Testado: funciona sem tela; falta instrumento bom (ver abaixo) | https://github.com/DBraun/DawDreamer |
| pedalboard | Spotify: efeitos prontos e plugins VST3 | https://github.com/spotify/pedalboard |

### Gerar a música inteira (aberto)

| Recurso | O que é | Link |
|---|---|---|
| YuE | Da letra à música completa, com voz e acompanhamento | https://github.com/multimodal-art-projection/YuE |
| HeartMuLa | Estilo controlado por seção; Apache 2.0 | https://github.com/HeartMuLa/heartlib |
| DiffRhythm 2 | Músicas de até 210 s, Apache 2.0 | https://github.com/xiaomi-research/diffrhythm2 |
| LeVo / LeVo 2 | Tencent SongGeneration | https://github.com/tencent-ailab/songgeneration |

### Modelos que "entendem" áudio (um segundo ouvido)

| Recurso | O que é | Link |
|---|---|---|
| Qwen3-Omni Captioner | Descrições detalhadas de qualquer áudio, Apache 2.0. 30B: não roda aqui; o Space oficial falhou em 25/11/2026 | https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Captioner |
| ✅ Music Flamingo | NVIDIA, especializado em música (pesquisa, não comercial). Testado: errou tempo e gênero (ver abaixo) | https://huggingface.co/nvidia/music-flamingo-hf |
| MOSS-Audio | 4B e 8B, instruct e thinking | https://github.com/OpenMOSS/MOSS-Audio |
| Eureka-Audio | 1,7B, compete com modelos de 4 a 18 vezes maiores | https://github.com/Alittleegg/Eureka-Audio |

## Próximos testes sugeridos

1. Beat This! no lugar da grade atual, comparando o desvio contra os onsets.
2. All-In-One para gerar o mapa de seções automaticamente.
3. BRID para tirar moldes de groove por instrumento, em vez de um molde único.
4. ACE-Step 1.5 (cover/repaint) e YingMusic-Singer (troca de palavras), quando houver GPU (Colab).
5. Refazer os breques da versão Vit com os tempos do WhisperX (4 de 7 voltas da banda mudam uma semicolcheia).
6. ✅ Feito: `colab/Music_Lab_Colab.ipynb` (sfizz + instrumentos SFZ, WhisperX, segundo ouvido com token). Falta ouvir o A/B do sfizz contra o sampler atual.

## Resultados dos testes (25/11/2026, "Mente" versão Vit)

**WhisperX: adotar.** Alinhamento forçado (wav2vec2 português) sobre as linhas do whisper, no stem de voz.
Medido contra a própria voz:

| | whisper (faster-whisper medium) | WhisperX |
|---|---|---|
| Início de frase (29 ataques após pausa), erro mediano | 213 ms, sempre atrasado | 71 ms |
| Início de frase, p90 | 301 ms | 139 ms |
| Todas as palavras (onset mais próximo), mediana | 39 ms | 24 ms |

Nos breques, as palavras que disparam o golpe já batiam (±0,15 s) e não mudam de semicolcheia. A volta da
banda ("o amor", "amo") muda uma semicolcheia em 4 de 7 breques, e o WhisperX fica mais perto do ataque real
em 4 desses. Exemplo: 1º breque, voz em 57,24 s; whisper põe a volta em 57,61 s, WhisperX em 57,28 s.
Instalação sem trocar o torch: `pip install --no-deps whisperx` + `transformers nltk omegaconf`; o script
dispensa torchaudio e o punkt do NLTK. Modelo: `jonatasgrosman/wav2vec2-large-xlsr-53-portuguese` (1,26 GB).

**DawDreamer: funciona, mas aqui não melhora o som.** Carrega VST3 sem tela (Dragonfly Hall/Plate/Room,
plugins DPF via apt) e renderiza MIDI rápido: 176 s de cavaquinho em 3,8 s. O gargalo é o instrumento:
os VST3 de qualidade (sfizz, Surge XT, Vital) só saem de downloads do GitHub, bloqueados neste ambiente, e o
apt só tem sintetizadores simples (Kars, Nekobi). O A/B do cavaquinho (sampler atual × Kars) está em
`vit/AB_cavaco_sampler_vs_DawDreamer_Kars.mp3` (fora do git). Ganho imediato possível: reverbs Dragonfly na
cadeia em Python. Ganho real (instrumentos): rodar com sfizz + bibliotecas SFZ num Colab.

**sfizz_render: o caminho para instrumentos sem DAW.** Para tocar bibliotecas SFZ não precisa do DawDreamer: o
`sfizz_render` (linha de comando do sfizz) lê `.sfz` + `.mid` e grava o WAV. Compilado aqui da fonte
(`sfztools/sfizz`, só o alvo `sfizz_render`, ~10 min em 2 núcleos), vira um binário de 2,7 MB que só depende da libc.
Renderizou o e-piano da Vit (jRhodes3d) em 7 s e o baixo (growlybass) em 15 s; o atraso contra o sampler em Python ficou
entre 0 e −10 ms. A/B com volume igualado: `sfz_ab/AB_epiano_sampler_atual_vs_sfizz.mp3` e `AB_baixo_...` (fora do git).
VSCO-2-CE e VCSL não publicam `.sfz`; a coleção `sfzinstruments/mappings` também não tem mapeamento deles.

**Segundo ouvido: não confiável para groove.** O Space do Qwen3-Omni Captioner falha no back-end (API
DashScope), até com 10 s. O Music Flamingo (Space da NVIDIA) respondeu uma vez antes de esgotar a cota anônima
de GPU. No trecho pré-refrão → refrão:

- acertou: tonalidade (Dó maior; acordes reais Em7–Am7–Fmaj7–G7–C), um verso da letra, voz em português;
- errou: tempo (166,7 BPM; o real é 89), gênero ("pop com sertanejo"; é pagode), instrumentos ("bateria
  eletrônica, congas, synth pads"; não citou cavaquinho nem surdo), e inventou um "refrão final" num trecho de 28 s.

A pergunta que interessava ("a mudança de seção é uma subida clara?") não rodou por falta de cota. Com token
do Hugging Face a cota aumenta; até lá, as medidas do `groove_report.py` continuam sendo o juiz.
