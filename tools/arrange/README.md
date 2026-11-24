# Reescrita de arranjo (v1, "Mente", 24/11/2026)

Scripts exatamente como rodaram na primeira reescrita. Método e regras: [`docs/05-reescrita-de-arranjo.md`](../../docs/05-reescrita-de-arranjo.md).

Ordem: `rw1_grid` → `rw2_chords` → (conferir acordes vs melodia) → `rw3_compose` → `rw4_midi_render` → `rw7_surdo` → `rw5_mix` → `rw6_master` (ou `tools/master.py`).

**Ainda não são genéricos:** caminhos (`/home/claude/ai2/stems`, `/home/claude/rw`), seções (`SEC`), *stops* (`STOPS`), tonalidade e alvos de loudness estão fixos no topo de cada arquivo. Para outra música, ajuste esses valores, ou transforme a etapa em CLI aqui (próximo passo natural).

Dependências extra: `mido`, `fluidsynth` + `FluidR3_GM.sf2` (`apt-get install fluidsynth fluid-soundfont-gm`). `rw6_master.py` carrega os blocos de `e3.py` (ver `arquivo/`); `tools/master.py` é a versão limpa da mesma cadeia.
