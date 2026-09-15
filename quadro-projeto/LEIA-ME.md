# Quadro do projeto — Casa do Marceneiro Tatuapé

Lista de tarefas viva do projeto: o que já saiu da bancada, o que está na
serra hoje e o que espera na fila. Um toque num item muda o estado, e a
marcação fica salva.

Três leituras da mesma coisa, da mais resumida para a mais detalhada: a
**linha do tempo** com os nove marcos datados, o **roteiro da visita** à
oficina, e o **quadro** de três colunas com os 35 cartões.

## Como funciona a persistência

A página **é** o registro. O estado mora num bloco JSON dentro do próprio
documento; quando alguém marca um item, o documento é remontado com o estado
novo e republicado, e todas as janelas abertas recarregam para a versão nova.

Para conseguir se remontar sem se degradar, a página carrega o próprio molde e
o próprio código como **texto**, de blocos que nunca são tocados em tempo de
execução. Nada de serializar o DOM vivo, que carregaria o desenho atual junto e
incharia a cada geração. O teste percorre três gerações seguidas: a terceira
difere da primeira em **1 byte**.

Sem o Artifact — arquivo aberto solto no celular, ou visitante sem permissão de
escrita — cai para o `localStorage`, e o rodapé diz em qual dos dois modos está.

## Arquivos

| Arquivo | Papel |
|---|---|
| `estado.json` | Os marcos, o roteiro e os itens. É aqui que se edita conteúdo. |
| `molde.html` | Marcação estática (cabeçalho, roteiro, colunas, rodapé). |
| `app.js` | Desenho, ciclo de estado e republicação. |
| `quadro.css` | Sistema visual. |
| `montar.py` | Junta tudo nos dois formatos. |
| `index.html` | Página autônoma (gerada). |

`artifact.html` é saída de build e fica fora do versionamento.

```
python3 montar.py
```

O build injeta molde e código **duas vezes** — uma para rodar, outra como
texto para a remontagem. Duplicar isso à mão na fonte seria a primeira coisa a
sair de sincronia; por isso é trabalho do build, e ele recusa a montagem se o
molde ou o código contiverem `</script`, que fecharia o bloco de texto cedo.

## Decisões

**Escuro, um tema só.** É um quadro de oficina, olhado em pé, no celular, com
serragem no ar. Mesma nogueira e mesmo verniz da proposta, para quem abre os
dois reconhecer que é o mesmo trabalho.

**O marco não guarda estado próprio.** Cada marco carrega os `id` dos cartões
que dependem dele e soma o estado deles: concluído quando todos estão feitos,
em curso quando algum foi tocado. Assim a linha do tempo não tem como discordar
das colunas — foi exatamente esse tipo de divergência que produziu o "Fazendo 19"
ao lado de uma coluna com 8. O `montar.py` não valida essa cobertura; quem
editar `estado.json` deve conferir que todo cartão aparece em algum marco.

**Data sem prazo é honesta.** O marco do anúncio pago tem `ate: null` e diz
por quê: depende de o Google responder às três violações, não de nós. Inventar
uma data ali seria prometer o que não se controla.

**Numeração só onde há ordem.** O roteiro de hoje é numerado porque a ordem
carrega informação: quem aponta o domínio antes de saber de quem ele é, aponta
o domínio de outra pessoa. As colunas do quadro são estados, não sequência, e
por isso não têm número.

**Faixa vermelha para trava.** Cinco itens bloqueiam outros. A cor entra na
lateral do cartão e no rótulo da frente, para a trava se ler de relance sem
precisar abrir nada.

## Defeitos encontrados na conferência e corrigidos

- **A remontagem perdia o molde.** O documento republicado renderizava, mas não
  conseguia republicar de novo — a segunda geração seria a última.
- **O medidor se contradizia.** Contava os passos do roteiro junto com o quadro,
  então a legenda dizia "Fazendo 19" ao lado de uma coluna com 8. O roteiro
  ganhou contador próprio.
- **`--mut2` media 4,32:1 sobre a bancada**, abaixo do piso de 4,5 para texto
  pequeno. Recalibrado para `#A08A73`, que mede 4,93:1.
- **Linha de leitura longa demais no desktop**: as descrições esticavam pelos
  1180 px. Limitadas a 72 caracteres.
- **`::after` posicionado sem pai posicionado** no marcador de "fazendo".
- **A data de atualização era UTC.** `new Date().toISOString()` marcado às
  21h30 em São Paulo já gravava o dia seguinte. Passou a usar a data local,
  que agora importa porque a linha do tempo compara datas.
- **A tarja de "atrasado" media 3,89:1**: vermelho sobre vermelho a 14%, abaixo
  do piso. Virou tarja cheia com tinta quase preta, 5,26:1 — o mesmo padrão que
  o marcador de "feito" já usava.

Um alarme foi falso positivo do **medidor de contraste**, não da página: ele
parava no primeiro fundo não transparente e tratava `rgba(...,.13)` como cor
sólida, sem compor com o que estava atrás. Corrigi o medidor, não o CSS.

## Verificação

66 asserções com Playwright em celular emulado — 50 do quadro mais 16 da
linha do tempo (contagem dos marcos, posição da linha do "hoje" entre passado
e futuro, estado derivado dos cartões, fração por marco, alinhamento do trilho
com os nós, e o marco reagindo ao clique num cartão): contagens batendo com o JSON,
ciclo de estado nos dois sentidos, contador do roteiro, agrupamento das
publicações (um clique não vira uma publicação), ida e volta do documento por
três gerações com fonte, fundo e sprite intactos, visitante somente leitura
travado com aviso, conflito silencioso, queda para o navegador quando não há
Artifact, e persistência entre recarregamentos. Sem estouro horizontal de 360 a
1440 px. Zero erro de JavaScript. Todo texto acima do piso WCAG AA.
