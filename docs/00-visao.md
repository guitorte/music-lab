# A ideia central

*Leitura proposta pelo assistente em 24/11/2026, depois de duas longas sessões de trabalho ("Transcrição MIDI" e a de masterização/arranjo). Deixa de lado se cada escolha foi boa ou ruim e pergunta só: o que está por trás de tudo isso?*

## Em uma frase

**Transformar a música gerada por IA, que chega como um arquivo de áudio fechado, numa obra aberta: algo que dá para ler, entender, corrigir e refazer só com linguagem. A voz e a letra do autor ficam no centro, e todo o resto vira matéria-prima.**

## O movimento que se repete

Olhando a sequência de pedidos, o mesmo gesto aparece em profundidades cada vez maiores. Cada passo abre a caixa um pouco mais:

| Profundidade | O que foi feito | O que isso abre |
|---|---|---|
| Superfície | masterizar faixas do Suno | o som final (volume, timbre, impacto) |
| Corte | trocar palavras, tirar refrões, emendar seções, inserir samples | a forma (a estrutura no tempo) |
| Camadas | trabalhar com stems, remontar a bateria, domar a multidão, trocar o shaker | os instrumentos separados |
| Notação | transcrever para MIDI, limpar o MIDI, comparar motores de transcrição | as notas (o que é tocado) |
| Linguagem | MIDI-TEXT / REMI, um formato de texto que uma IA lê e devolve como MIDI | a música em forma de texto |
| Entendimento | medir groove, camadas e timbres de uma banda real contra a faixa gerada | as regras que fazem música soar "tocada" |
| Reescrita | reescrever o arranjo inteiro em MIDI sob a voz original e renderizar | a autoria sobre o instrumental |

É uma **descompilação**. O áudio gerado é como um programa compilado: funciona, mas não se lê nem se altera por dentro. O trabalho todo tem sido recuperar o "código-fonte" da música (seções, stems, notas, texto) para poder mexer nele.

## O que fica fixo

Em quase todo processo, uma coisa é preservada a qualquer custo: **a voz cantando a letra**.
- As correções de palavras mexem em milissegundos e deixam o resto idêntico, bit a bit.
- A reescrita de arranjo troca o instrumental inteiro, mas mantém o stem vocal.
- O vocal-lab (repo `audio`) existe para tirar uma versão limpa da voz.
- A preferência constante é por voz que não fique na frente demais: integrada, não exibida.

A letra é sua, e a voz é a forma que ela ganhou. **O instrumental é tratado como andaime: o gerador entrega uma primeira versão, e ela pode ser refeita.**

## Por quê

Você escreve letras e não tem DAW, banda nem estúdio. O gerador resolve o problema de fazer a letra virar música, mas entrega um produto fechado, com defeitos que você ouve e não consegue consertar: palavras mal pronunciadas, artefatos, groove duro, camadas com buracos e timbres opacos. Também entrega um produto que não é inteiramente seu.

Por trás de tudo, então, há duas buscas juntas:

1. **Qualidade de verdade.** A comparação com a banda ao vivo deixa claro o alvo: camadas completas e distinguíveis, um groove que respira, contrastes entre seções, a imperfeição certa. Não é "mais alto" nem "mais limpo"; é soar **tocado por gente**.
2. **Controle e autoria.** Poder dizer "essa palavra", "essa pausa", "esse refrão mais forte", "esse instrumento diferente" e ver acontecer. O gerador vira o rascunho, a demo, e o produto final passa a ser dirigido por você.

## O instrumento escolhido para isso: a linguagem

O meio de trabalho é sempre o mesmo: **conversa + código**, sem interface gráfica. Por isso a música precisa caber em linguagem, e isso explica tanto o esforço em representações de texto (REMI) quanto em medidas (LUFS, punch, molde de acentos). Quem trabalha (o assistente) não ouve. Ele só decide por medidas e notação, e o seu ouvido é o juiz final. Assim o ciclo fica:

```
ouvido do autor (o que está errado)  →  palavra  →  medida / notação  →  código  →  áudio  →  ouvido do autor
```

## O laboratório

O pedido de transformar o processo em skill, em repositórios (`audio`, agora `music-lab`) e em documentação mostra a última camada da ideia: **não é fazer uma música, é montar um estúdio feito de método**. É uma linha de produção que acumula o que aprendeu, roda em qualquer sessão e melhora a cada faixa.

## Consequências práticas para o repositório

- O caminho principal deste laboratório é **letra/voz → arranjo próprio → mix → master**. A master de faixa gerada continua útil, mas é o caso mais raso.
- Toda ferramenta nova deve responder a uma de três perguntas: *isso abre mais a música?*, *isso aproxima do som tocado?* ou *isso dá mais controle ao autor?*
- O vocal é sagrado: nada deve degradar a voz sem que isso seja explícito.
