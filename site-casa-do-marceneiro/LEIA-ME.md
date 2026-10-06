# Site da Casa do Marceneiro Tatuapé — protótipo funcional

Reconstrução do `marceneirotatuape.com.br` como site próprio, navegável e com
loja que funciona de verdade. Não é maquete de tela: é o site rodando, para ser
testado antes de subir e antes do primeiro real de anúncio.

## O que abrir

| Arquivo | Para quê |
|---|---|
| `index.html` | O site. Abre em qualquer celular ou navegador, sem servidor. |
| `corpo.html` | Fonte única — conteúdo, marcação e toda a lógica. |
| `site.css` | Sistema visual. |
| `montar.py` | Gera `index.html` e `artifact.html` a partir da fonte. |
| `capa-link.jpg` | Cartão de prévia do link, para o WhatsApp. |
| `gerador/cartao.html` | Fonte do cartão. |
| `gerador/cartao.js` | Fotografa o cartão em 1200 × 630. |
| `marca/` | O logo em vetor, HD e 4K, ícones e foto de perfil (ver "O logo"). |
| `gerador/logo/` | Desenho, textura e exportação do logo. |

`artifact.html` é saída de build e fica fora do versionamento.

Para reconstruir depois de mexer em `corpo.html` ou `site.css`:

```
python3 montar.py
```

## O que funciona de verdade

Sete telas com endereço próprio (`#/loja`, `#/sob-medida`, …), então cada uma
tem link que se manda por WhatsApp e o botão voltar do celular se comporta.

- **Loja** — catálogo com filtro por categoria, busca e ordenação.
- **Ficha do produto** — madeira, acabamento e medida recalculam o preço na hora.
- **Carrinho** — soma, altera quantidade, remove, sobrevive ao recarregamento.
- **Frete** — tabela por faixa de CEP, com frete grátis acima de R$ 900 na capital.
- **Checkout em três passos** — dados, entrega e pagamento, com validação real:
  CPF pelos dois dígitos verificadores, cartão por Luhn, validade não vencida.
- **PIX, cartão e boleto** — cada um com seu bloco, desconto de 5% no PIX,
  parcelamento recalculado sobre o total.
- **Configurador sob medida** — ambiente, padrão e metragem devolvem faixa de
  investimento na hora e montam a mensagem de WhatsApp preenchida.
- **Contato** — validação de campos e aceite de LGPD antes de enviar.

Nada sai do aparelho. Não há servidor, não há pagamento, não há dado gravado
fora do `localStorage` do próprio navegador.

## A parte institucional

A empresa é familiar e trabalha **desde 1980**. A idade não está escrita à mão em
lugar nenhum: os elementos com `data-anos` recebem `anoAtual − 1980` na partida,
para o site não anunciar um número vencido em 1º de janeiro.

A página da oficina tem três blocos novos:

- **História** — empresa familiar, estilo artesanal, ofício passado de uma geração
  para a outra, parceria com escritório de arquitetura.
- **Missão, visão e valores** — cinco valores, cada um com um comportamento
  concreto em vez de um adjetivo. O quinto ocupa duas colunas, porque cinco
  cartões em três colunas deixariam uma célula vazia.
- **Ficha técnica** — duas colunas, o que entra e o que não entra. É o bloco mais
  afiado da página, e por isso mora na faixa escura, sozinho. **MDP não entra**:
  é a primeira linha da coluna da recusa, e a recusa aparece de novo nos valores.
  Uma marcenaria se define tanto pelo que usa quanto pelo que recusa.

**Números inventados saíram.** A capa anunciava "+800 projetos" e "4,9 no Google",
que eram invenção minha de protótipo. No lugar entraram três fatos que vêm da
própria empresa: a idade, a recusa do MDP e a garantia com assistência técnica.
A nota real do Google entra quando existir avaliação para citar.

## Decisões que valem explicar

**As imagens são projetos 3D, e o site diz isso.** O acervo do Gabriel ainda não
chegou, e foto de banco de imagem numa marcenaria é pior que nenhuma: o cliente
acha que é trabalho da casa. O meio-termo honesto é o que toda marcenaria já mostra
na venda, o projeto em 3D. As 17 imagens do site foram renderizadas no Blender a
partir de `gerador/fotos/`, com madeira gerada por fórmula: nada baixado de
terceiros, direito de uso total. Toda imagem de ambiente leva o selo
**"3D ilustrativo"**, e a página de projetos explica isso por escrito. Quando as
fotos reais chegarem, basta salvar com o mesmo nome em `fotos/` (ver abaixo) e
tirar o selo.

O desenho de chapa por gradiente continua existindo como reserva: aparece onde
ainda não há imagem e enquanto a foto carrega.

**Um visual só, claro.** Sem tema escuro. É uma vitrine que o Gabriel vai abrir
na frente do cliente, na oficina, sob luz de dia; uma segunda aparência para
manter não vende mais um armário. Nogueira escura entra só nas faixas
estruturais — topo, capa, rodapé, chamada de preço. O topo é escuro porque o
logo da casa é madeira clara sobre fundo escuro, e é assim que ele foi desenhado
para aparecer.

**Veio horizontal.** A primeira versão listrava na vertical e lia como cortina,
não como chapa. Ângulo corrigido para 2°.

**O aviso de prévia.** Fica no topo, some ao fechar e volta a cada nova sessão.
Ninguém deve confundir isto com a loja no ar.

**QR de demonstração.** O padrão desenhado não é um QR válido, de propósito:
ninguém pode pagar por engano numa prévia. O rótulo diz isso embaixo do código.

## Dados da empresa

Tirados do site atual da casa, e iguais em todo lugar onde aparecem (topo,
capa, faixa da oficina, contato, rodapé, ficha do Google em `index.html`):

| Dado | Valor |
|---|---|
| WhatsApp | (11) 94752-3961 — `TEL` em `corpo.html`; todo link `wa.me` já nasce com ele no HTML |
| Endereço | Rua Tuiuti, 2530, cj. 42 — São Paulo/SP |
| E-mail | contato@marceneirotatuape.com.br |

O formulário de contato envia de verdade, sem servidor: abre o WhatsApp da
oficina (ou o e-mail de quem escreve) com a mensagem já montada. O pedido de
teste do checkout também avisa a oficina pelo WhatsApp, e a mensagem diz que é
teste.

O endereço precisa bater **letra por letra** com o Google Meu Negócio e com o
Instagram — é esse casamento que faz a oficina aparecer na busca de quem está a
dois quarteirões.

## O que ainda falta confirmar antes de subir

1. **Desde 1980.** O site segue a fundação informada, 1980 (46 anos). O texto
   antigo da casa diz "há mais de 25 anos no mercado" e precisa ser corrigido onde
   ainda estiver no ar (site atual, Instagram), para a empresa não ter duas idades.
2. **Horário de atendimento.** Seg a sex 8h–18h, sáb 8h–12h é do protótipo.
3. **Instagram.** `@casadomarceneirotatuape` é do protótipo.
4. **CNPJ.** Está como `00.000.000/0001-00`.
5. **Fotos reais.** O portfólio do site atual tem as fotos das obras; entram no
   lugar dos renders com o mesmo nome (ver "As imagens").
6. **Preços reais.** Os do protótipo são ilustrativos.
7. **Depoimentos.** Trocar pelos reais do Google, com autorização de quem assina.
8. **Título da aba.** Está só `Casa do Marceneiro Tatuapé`, que é o nome. Na
   versão no ar vale acrescentar o que a oficina faz e onde — é o que aparece
   como linha azul no resultado do Google.

## Defeitos encontrados na conferência e corrigidos

- **O aviso de LGPD cobria o botão de adicionar ao carrinho no celular.** Estava
  em `z-index:80`, acima da ficha do produto. Um cliente de verdade bateria
  nisso. Foi para baixo de todas as sobreposições, e o corpo passou a reservar o
  espaço dele para não tapar o rodapé.
- **O nome da marcenaria sumia no cabeçalho do celular.** A regra que devia
  esconder só o subtítulo (`.marca span`) pegava também o bloco do nome. O
  subtítulo ganhou classe própria.
- **Buscar "freijó" não achava nada.** As madeiras vivem nas opções do produto,
  não no texto indexado. O índice passou a incluir as opções, e a busca dobra
  acento — ninguém digita "freijó" com acento no celular.
- **O rótulo do QR atravessava o código.** Foi para baixo.
- **Cor inválida no bloco do mapa.** Erro de digitação na redação da marcação.

Um alarme foi falso positivo do próprio teste: a asserção de "menor preço
primeiro" esperava a tábua de R$ 129 e esquecia do corte de chapa a R$ 68/m².
A ordenação estava certa; corrigi o teste, não o código.

## Verificação

**154 conferências** de ponta a ponta (desktop 1440 e Pixel 7) e **335 de
celular** em sete aparelhos: Galaxy de 320 px, iPhone SE, iPhone 13, iPhone 14
Pro Max, Pixel 7, iPad Mini e iPhone deitado. No celular, por tela: nada rola
para o lado, nenhum elemento sai da tela, nenhum alvo de toque abaixo de 24 px
(os do topo têm 44), nenhum campo abaixo de 16 px (o iPhone dá zoom ao tocar),
nenhuma letra abaixo de 11 px, nenhuma imagem esticada além da resolução; e o
fluxo de compra inteiro (ficha, carrinho, checkout, menu) em tela estreita.

A revisão de celular achou e corrigiu: campos a 15,5 px que davam zoom no
iPhone e no iPad; botões do topo com 35 px; selo "3D ilustrativo" a 10,5 px; o
logo espremido pelo menu no iPad (o menu agora vira gaveta abaixo de 980 px);
a foto da capa sem resolução no iPad em pé; a escolha de madeira encavalada no
selo da foto em 320 px; o item do carrinho escondido atrás do total no iPhone
SE; e o aviso de "peça adicionada" tapando o botão de finalizar.

Da primeira rodada, 89 asserções com Playwright dirigindo o site de verdade em celular emulado:
navegação por rota e por menu, filtro, busca, ordenação, cadeia de preço na
ficha, carrinho somando e persistindo, frete por três faixas de CEP, checkout
recusando CPF e cartão inválidos e aceitando os válidos, relógio do PIX
correndo, pedido concluído com número gerado e carrinho zerado, cinco ambientes
e três padrões do configurador dando faixas distintas, formulário de contato,
`Escape` fechando sobreposições, aviso de LGPD com memória. Sem estouro
horizontal em 360, 375, 393, 412, 768, 1280 e 1440 px. Zero erro de JavaScript.
Todo texto passa no piso de contraste WCAG AA, medido cor a cor.

## As imagens

| Arquivo em `fotos/` | Onde aparece |
|---|---|
| `capa-2400/1600/960.webp` | Capa do site (cozinha em U, quadro panorâmico) |
| `nicho`, `prateleira`, `tabua`, `ripado`, `banqueta`, `cabeceira`, `corte`, `bancada` | Peça da loja de mesmo nome |
| `cozinha`, `closet`, `escritorio`, `painel`, `compacta`, `dormitorio` | Projetos, mosaico da página inicial, simulador |
| `banheiro` | Simulador, ambiente Banheiro |
| `oficina` | Faixa "Oficina aberta" da página inicial |

Cada imagem tem duas larguras: `<nome>.webp` (1200 ou 1280 px) e `<nome>-640.webp`,
e o navegador escolhe pela largura em que ela aparece. Para trocar por foto real:
mesma proporção 4:3, mesmo nome, e rodar `python3 montar.py`.

Para refazer os renders (precisa do pacote `bpy`, o Blender como módulo Python):

```
python gerador/fotos/produtos.py nicho saida.png 40 75     # peça da loja
python gerador/fotos/ambientes.py cozinha saida.png 48 80   # ambiente
python gerador/fotos/otimizar.py <pasta-dos-png> fotos/     # PNG → WebP
```

## O logo

Redesenhado em vetor a partir do arquivo de 421 × 162 px que a casa usa hoje,
em geometria pura: cada reta, arco e curva foi medido no original ampliado 8
vezes e ajustado por sobreposição. O redesenho cobre 99,3% do telhado e 98,3%
de MARCENEIRO; o que sobra é o antisserrilhado do original. A madeira clara é
gerada por fórmula (`gerador/logo/textura.py`), de veio vertical como no
original. Nada baixado, nenhuma fonte de terceiros.

| Arquivo em `marca/` | Para quê |
|---|---|
| `logo-madeira.svg` | O logo oficial: vetor com a madeira por baixo. Amplia sem perder nada |
| `logo-creme.svg`, `logo-escuro.svg` | Vetor de uma cor só: gráfica, adesivo, bordado, corte a laser, fundo claro |
| `logo-madeira-4k.png` (3840 px), `logo-madeira-hd.png` (1920 px) | Fundo transparente |
| `logo-escuro-4k.png` | Fundo transparente, para papel e fundo claro |
| `logo-4k-fundo.png` (3840 × 2160), `logo-hd-fundo.png` (1920 × 1080) | No degradê escuro do original: TV, apresentação, tela de fundo |
| `perfil-1080.png` | Foto de perfil do WhatsApp Business e do Instagram (cabe no círculo) |
| `icone.svg`, `icone-512.png`, `apple-touch-icon.png`, `favicon-32.png` | Símbolo: aba do navegador, atalho na tela do celular |
| `logo-site.svg` | O do topo e do rodapé do site, com textura leve embutida |

Para refazer tudo (numpy, Pillow e Node com Playwright):

```
python gerador/logo/exportar.py
```
