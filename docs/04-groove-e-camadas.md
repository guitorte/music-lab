# Groove, camadas e timbres: banda real vs faixa gerada

Medido em nov. 2026 com stems + MIDIs de uma **faixa de referência ao vivo** (banda de pagode de verdade) e da **faixa gerada "Mente"** (letra original do autor). Não são a mesma música, então as comparações são de perfil, não de alinhamento. Ferramenta: `tools/groove_report.py`; métricas em `lib/metrics.py`.

## Os números

| Medida | Banda ao vivo | Faixa IA | O que significa |
|---|---|---|---|
| Tempo | 79,5 BPM | 90,7 BPM | — |
| **Acentos por semicolcheia** (1ª/2ª/3ª/4ª) | 1,00 / **0,23** / ~1,0 / 0,59 | 1,00 / **0,69** / 0,91 / 1,17 | na banda a 2ª é quase fantasma e a 4ª é média; na IA tudo tem peso parecido e o contratempo pesa mais que o tempo. É o "duro" |
| Microtempo | 2ª e 4ª semicolcheias alguns ms atrasadas, espalhamento de ±5 ms | grade rígida | o "balanço" |
| **Punch do surdo** (p95 − p50, 45–120 Hz, stem de bateria) | 21 dB | 32,6 dB | IA: picos soltos num fundo vazio |
| Nível das ghost notes | −30 dB | −38 dB | — |
| Voz vs banda | **−3,1 LU** | +3,4 LU | na IA a voz fica na frente e a banda atrás |
| Baixo (vs soma) | −10,8 LU | −18,7 LU | baixo quase ausente |
| Guitarra / piano / outros | −9,0 / −15,0 / −14,3 | — | proporções-alvo da mix |
| **Camadas simultâneas** (média) | 5,6 (≥ 4 camadas 100% do tempo) | 3,1 | — |
| Baixo ativo | 86% do tempo | 14% | — |
| Independência entre bandas da bateria | 0,50 | 0,92 | na banda, surdo, caixa e chimbal tocam frases próprias; na IA andam juntos |
| Ocupação espectral | 54% | 36% | buracos |
| Baixo e cavaco vs bateria | dentro de ±3 ms | — | — |

## Timbres

- **Teclados da IA abafados:** topo em ~5,6 kHz e decaimento de 107 ms. Notas cortadas, sem cauda.
- **Baixo da IA:** ataque lento (74 ms) e decaimento curto (21 ms), o oposto de um baixo tocado.
- **Todos os stems da IA vão até 20–22 kHz** com energia plana, um artefato: instrumento real cai antes.
- O MIDI combinado "B" do pacote estava vazio nas duas exportações, o que parece um bug do pipeline de origem.

## Diagnóstico em uma linha

A faixa gerada não tem **camadas completas e distinguíveis**. Ela tem pedaços: notas que começam e somem, instrumentos que entram e saem, acentos sem hierarquia. O ouvido percebe isso como "cortado", "com buracos", "duro". A banda real é um tecido: cada instrumento sustenta a sua parte o tempo todo, com hierarquia de acentos e pequenos atrasos.

## Como usar isso

- Como **alvo de mix**: proporções de loudness dos stems, voz cerca de 3 LU abaixo da banda (o autor prefere voz integrada).
- Como **alvo de arranjo**: molde de acentos, microtempo, camadas contínuas (ver `05-reescrita-de-arranjo.md`).
- Como **checagem** de qualquer master de pagode: punch medido no mesmo tipo de sinal (stem com stem, mix com mix; não misturar).
