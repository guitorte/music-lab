# Diário de faixas (nov. 2026)

Registro de decisões por faixa: o que foi pedido, o que foi feito, com que números e o que o autor disse. Os scripts originais estão em `arquivo/scripts-sessao-2026-11/` (prefixos indicados).

| Faixa | Pedido | O que foi feito | Resultado | Scripts |
|---|---|---|---|---|
| **Que nem eu ITA** | master depois das correções (v4) | cadeia padrão | — | `qm*` |
| **AFLX_004** (skate punk, estilo Millencolin) | master | cadeia padrão, mais alta | −10 LUFS | `sk*` |
| **Virada no Diabo** | trocar "Se for de casal", "achar" (soava "as-char") e "a cara" (soava "carara") | v1 NNLS/Wiener → ruído em "casal" (crossfade de 20 ms) → "a cara" bizarra (transplante dos refrões 1 e 3 em L/R) → stems exatos novos: v3 aritmética exata; versão sem remendos (voz corrigida + instrumental, limiter −1 dBTP) | master −11 LUFS | `v*`, `w3`, `w4`, `vm*` |
| **Virada no Diabo (Remastered)** | master como a primeira; ruído constante por volta de 2:00 | removidas as linhas de 12,8 kHz e 850 Hz | −11,5 LUFS | `vr*` |
| **TPTM** | master seguindo os livros do projeto | pente de artefatos de 16,9 a 20 kHz removido; dois estágios | −13 LUFS | `tp*` |
| **Vai e Volta (Ama e Despreza)** | master | cadeia padrão | −12 LUFS | `vv*` |
| **Coca_na** | tirar o refrão 2 aproveitando o final para a ponte | deslocamento por coincidência de batidas (43,722 s); "apressado" corrigido; versões A e B; master da B com a ponte +4 dB | −11 LUFS, aprovado ("Ficou ótimo!") | `c*`, `cc*`, `cm*` |
| **Marina Chinesa** | inserir um sample em alguns momentos | sample em Sol6 −35 cents → reafinado +35 cents, em 3 tempos fortes | — | `ch*` |
| **Soap Opera Thing** | master; depois groove de pagode a partir dos stems ao vivo; multidão no final | master −12 → stems: shaper no surdo, snap, detector do glue com HPF 150 → "perdeu punch/impacto" → v3: multidão de volta, presença +1,5 em 2,5k, ride +1, −2 dBTP | v3 | `so*`, `pg*` |
| **Soap Opera Thing (MIDI)** | achar a dureza nos MIDIs; versão MIDI + voz; bateria para dar força ao refrão | MIDI com velocities do áudio (30% por banda, 70% global), remapa de percussão GM de pagode, mapa de tempo; render FluidSynth; kit Power (banco 128, preset 16) | mp3 + `.mid` | `md*`, `mr*`, `kit1` |
| **Mente** | master com "impacto, punch, volume, front of house" | cadeia padrão + paralela + ride 2,0 | −10,5 LUFS, **aprovada** ("Ficou excelente") | `mt3`, `mt4` |
| **Mente (final editado)** | aplicar a mesma master ao WAV com final editado | idem, 44,1 kHz | — | `mt5` |
| **Mente (intro)** | "o sopro do início ficou muito estridente" | cadeia suave até 9,0–9,6 s, intro −2,5 dB; idêntico à v1 depois de 0:10 | `Mente_final_master_v2` | `mt6`, `mt7` |
| **Mente DiP Extended** (outro vocal) | master | corte no 100 Hz (não no 63) | −11 LUFS, −2,2 dBTP | `dp*` |
| **Referência ao vivo** (banda real) | analisar mix e MIDIs | ver `04-groove-e-camadas.md` | números de referência | `rf*` |
| **Mente (faixa IA) vs referência** | comparar instrumentos, camadas, buracos, timbres | ver `04-groove-e-camadas.md` | diagnóstico | `ai*`, `lay*`, `tim1` |
| **Mente (arranjo reescrito)** | reescrever o MIDI inteiro e renderizar com o stem vocal + noção de master | ver `05-reescrita-de-arranjo.md` | −12 LUFS, `.mid` com 8 trilhas | `rw*` |
| **Mente (arranjo v2)** | "muito flat": versos intimistas, pré que acelera, refrão que explode e troca a levada | três levadas, transições, breques na quebra de linha da letra, sopros, solo de sax, automação da voz; ver `docs/musicas/mente.md` | −12 LUFS, refrão +4,6 LU sobre o verso | `tools/arrange/v2/` |

Da conversa "Transcrição MIDI" (detalhes em `06-transcricao-midi.md`):

| Faixa | O que foi feito |
|---|---|
| virada-dois, gnt ("A gente"), qne-maq | montagem MIDI + REMI; qne-maq com limpeza completa (904 → 719 notas) |
| raio-x | bateria por peça, shaker real da VCSL no lugar do shaker da IA, master −13 LUFS; arquivos separados de instrumental e voz |
| Virada no Diabo 1 | duas remasters; ruído de público no fim tratado com EQ M/S e fade |

Preferências do autor que aparecem em todo o diário:
- Voz integrada, não na frente demais.
- Refrão como ponto alto: entrada com impacto.
- Pausas e respiros preservados ("não perdeu uma pausa mínima?").
- Groove acima de volume.
| **Traição** (referência gravada, outros autores) | analisar timbres, groove, arranjo e evolução dinâmica | stems BS-RoFormer + MIDIs do bakeoff; presença por semicolcheia, densidade por seção, paradas tempo a tempo; comparação de timbre com Mente Vit | `docs/musicas/traicao-referencia.md`; nova métrica `slot_presence` | `tr_*` |
| **Mente (Vit) com arranjo de Traição** | adaptar todo o instrumental de Traição ao MIDI vocal | padrões medidos de Traição (percussão, baixo, cavaco, violão, teclado, textura) nos acordes e na forma de Mente; parada + virada antes dos refrões; Rhodes estéreo via sfizz; plate Dragonfly na voz seca via DawDreamer | master −13 LUFS, contorno de seções a ±0,5 LU de Traição, punch 13,5 dB | `vt_*` |
