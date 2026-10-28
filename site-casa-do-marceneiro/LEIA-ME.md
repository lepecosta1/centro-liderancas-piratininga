# Site da Casa do Marceneiro Tatuapé

Reconstrução do `marceneirotatuape.com.br` como site próprio, navegável e com
loja que funciona de verdade. Não é maquete de tela: é o site rodando, para ser
testado antes de subir e antes do primeiro real de anúncio.

## O que abrir

| Arquivo | Para quê |
|---|---|
| `index.html` | A prévia num arquivo só, gerada pelo `montar.py`: abre em qualquer navegador, sem servidor. Fica fora do Git. |
| `vercel.json` | Como a Vercel monta e serve o site. |
| `corpo.html` | Fonte única — conteúdo, marcação e toda a lógica. |
| `site.css` | Sistema visual. |
| `montar.py` | Gera `index.html` e `artifact.html` a partir da fonte; com `--dominio`, o site de verdade em `publicar/`. |
| `lancamento.json` | O que precisa ser confirmado com o Gabriel antes de o site ir para o Google. |
| `gerador/fotos/importar.py` | Põe as fotos reais nos lugares das imagens 3D. |
| `capa-link.jpg` | Cartão de prévia do link, para o WhatsApp. |
| `gerador/cartao.html` | Fonte do cartão. |
| `gerador/cartao.js` | Fotografa o cartão em 1200 × 630. |
| `marca/` | O logo em vetor, HD e 4K, ícones e foto de perfil (ver "O logo"). |
| `gerador/logo/` | Desenho, textura e exportação do logo. |

`artifact.html`, `index.html` e `publicar/` são saída de build e ficam fora do versionamento.

**No ar: https://casa-do-marceneiro-tatuape.vercel.app/** — projeto próprio na Vercel, que monta o site
a partir deste repositório a cada atualização. O site saiu do GitHub Pages: o repositório guarda a
fonte, quem serve é a Vercel.

Para reconstruir depois de mexer em `corpo.html` ou `site.css`:

```
python3 montar.py
```

## O que funciona de verdade

Seis telas com endereço próprio (`#/loja`, `#/projetos`, …), então cada uma
tem link que se manda por WhatsApp e o botão voltar do celular se comporta.

**O simulador de sob medida está guardado.** A pedido do Gabriel (27/10), a tela
`#/sob-medida` sai do menu, da capa, do rodapé e do domínio, mas o código fica
inteiro em `corpo.html`, entre marcas `<!--SIMULADOR-->`. Onde ele aparecia, entra
o que está entre `<!--SEM-SIMULADOR-->` (o botão da capa vai para os projetos
concluídos, o balcão do meio pede a medida pelo WhatsApp). Para religar:
`SIMULADOR = True` no `montar.py` e montar de novo.

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
| Endereço | Rua Elisiário, 143 — Tatuapé, São Paulo/SP |
| E-mail | contato@marceneirotatuape.com.br |

O formulário de contato envia de verdade, sem servidor: abre o WhatsApp da
oficina (ou o e-mail de quem escreve) com a mensagem já montada. O pedido de
teste do checkout também avisa a oficina pelo WhatsApp, e a mensagem diz que é
teste.

O endereço precisa bater **letra por letra** com o Google Meu Negócio e com o
Instagram — é esse casamento que faz a oficina aparecer na busca de quem está a
dois quarteirões.

## Do site aprovado ao domínio — passo a passo

A prévia continua em `index.html`, fora do Google. O site de verdade sai de um
comando, numa pasta à parte, com uma página por tela (`/loja/`, `/projetos/`,
`/contato/`…), cada uma com título, descrição e endereço canônico próprios — é
isso que deixa "painel ripado no Tatuapé" achar a página de projetos, e não só a
capa:

```
python3 montar.py --dominio https://marceneirotatuape.com.br/
```

Sai em `publicar/` (fora do Git): as sete páginas, com estilo e código em
`estilo.css` e `site.js` compartilhados (cada página tem 54 KB em vez de 740),
`sitemap.xml`, `robots.txt`, `404.html`, `CNAME` (só fora da Vercel), o endereço
antigo `/portfolio/` levando a `/projetos/`, as fotos e só os arquivos do logo
que a página usa. No domínio não existe checkout simulado nem bandeira de cartão: o carrinho vira **Pedir pelo
WhatsApp**, com peça, opção, quantidade, valor e subtotal na mensagem.

**A conferência de lançamento.** O comando se recusa a publicar indexável
enquanto houver CNPJ de exemplo, texto de prévia ou de imagem ilustrativa,
lugar de foto ainda em 3D ou item sem confirmar no `lancamento.json`. Ele lista
o que falta. `--forcar` monta assim mesmo, mas com `noindex`, `Disallow` e o
aviso de prévia no topo — é assim que a Vercel monta hoje: o site está no ar
para o Gabriel ver e aprovar, sem o Google guardar nada inventado. Quando a
última pendência sair, o mesmo build passa a sair indexável e sem o aviso.

A ordem:

1. **Gabriel aprova a prévia.**
2. **Fotos reais.** Na pasta Marceneiro Tatuapé do Drive, cada foto com o nome do
   lugar (`capa.jpg`, `cozinha.jpg`, `oficina.jpg`…). Depois
   `python gerador/fotos/importar.py <pasta>` — vira, corta, reduz, tira o GPS e
   marca o lugar em `fotos/reais.json`; o selo de 3D sai sozinho dali.
3. **Projetos reais.** Trocar os seis de `PROJETOS` no `corpo.html` pelas obras
   das fotos: o que é, o bairro, os metros e o prazo de verdade.
4. **Confirmar com o Gabriel** e marcar no `lancamento.json`: CNPJ, preços,
   horário, Instagram, 1980 e as promessas que o site faz — garantia de 3 anos,
   visita sem custo, desconto por atraso, preço travado, prazos de retirada e
   entrega. Promessa publicada vira oferta e obriga (CDC, art. 30).
5. **Avaliações.** O `placeId` do perfil no Google (Google Meu Negócio → Pedir
   avaliações) em `GOOGLE.placeId` faz o botão abrir direto o formulário de nota.
   Comentários só entram em `AVALIACOES` com a autorização de quem escreveu.
6. **Domínio.** Conferir no Registro.br que o titular é o CNPJ do Gabriel e
   **anotar todos os registros de DNS de hoje, principalmente os MX**: o
   `contato@marceneirotatuape.com.br` depende deles e não pode cair na troca.
7. **Hospedagem.** Já está na Vercel (`vercel.json`): o build roda o
   `montar.py --dominio` com o endereço de produção do projeto, e o cadeado é
   automático. Hoje o projeto está na conta do Leandro; a Vercel transfere o
   projeto para uma conta no e-mail do Gabriel sem tirar o site do ar.
8. **DNS.** Na Vercel, Settings → Domains → `marceneirotatuape.com.br` e
   `www.marceneirotatuape.com.br`. No DNS do domínio, os registros que ela
   mostrar — hoje, A `@` para `76.76.21.21` e CNAME `www` para
   `cname.vercel-dns.com`. MX e TXT do e-mail ficam como estão. Propagação:
   até 24 h. O build seguinte já sai com o domínio no canônico e no sitemap.
9. **Conferir no celular:** cadeado, `/contato/`, `/projetos/`, `/portfolio/`
   levando a projetos, WhatsApp e Ligar chamando o (11) 94752-3961.
10. **Google Search Console:** propriedade de domínio (registro TXT), enviar
    `sitemap.xml` e pedir a indexação da capa.
11. **Google Meu Negócio:** site `https://marceneirotatuape.com.br/`, o mesmo
    horário e o mesmo endereço do site, letra por letra.
12. **Medição** (ver abaixo), e só então os anúncios.
13. **O site antigo** só sai do ar depois de o novo abrir e de o portfólio dele
    estar salvo.

## Medição e anúncios

Os identificadores ficam em `medicao.json`, ao lado deste arquivo:

```json
{ "ga4": "G-XXXXXXX", "ads": "AW-XXXXXXXXX", "meta": "000000000000000",
  "conversoes": { "whatsapp": "<rótulo>", "ligacao": "<rótulo>",
                  "formulario": "<rótulo>", "pedido": "<rótulo>" } }
```

O `montar.py --dominio` grava isso na página. Sem o arquivo, nenhum script de
terceiro carrega. Com ele, o aviso de cookies passa a pedir aceite, com
**Aceitar** e **Só o essencial**, e o Google (GA4 e Ads) e o pixel da Meta só
carregam depois do aceite — LGPD. O que se mede é o que vira cliente: clique no
WhatsApp, toque em Ligar, formulário enviado e pedido pela loja. No Google Ads,
cada um é uma conversão com o rótulo acima; na Meta, `Contact` e `Lead`.

## O que ainda falta confirmar antes de subir

O `lancamento.json` é a lista que o `montar.py --dominio` cobra. Em detalhe:

1. **Desde 1980.** O site segue a fundação informada, 1980 (46 anos). O texto
   antigo da casa diz "há mais de 25 anos no mercado" e precisa ser corrigido onde
   ainda estiver no ar (site atual, Instagram), para a empresa não ter duas idades.
2. **Horário de atendimento.** Seg a sex 8h–18h, sáb 8h–12h é do protótipo.
3. **Instagram.** `@casadomarceneirotatuape` é do protótipo.
4. **CNPJ.** Está como `00.000.000/0001-00`.
5. **Fotos reais.** O portfólio do site atual tem as fotos das obras; entram no
   lugar dos renders com o mesmo nome (ver "As imagens").
6. **Preços reais.** Os do protótipo são ilustrativos.
7. **Depoimentos.** Os inventados saíram. No lugar entrou a seção de avaliações
   do Google, com o mapa e a nota ao vivo; comentários só com autorização.
8. **Promessas comerciais.** Garantia de 3 anos, visita sem custo, desconto por
   atraso, preço travado e prazos de retirada e entrega são do protótipo.
9. **Formas de pagamento.** As bandeiras do rodapé só aparecem na prévia.

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

Em 21/10: **180 conferências** de ponta a ponta na prévia, **335 de celular**,
**34 do modo domínio** servido como raiz (páginas por caminho, título e
canônico por tela, voltar do celular, pedido pelo WhatsApp, `/portfolio/`,
sitemap, robots, CNAME, ficha do Google), **44 com a medição ligada** (nada do
Google nem da Meta antes do aceite; depois, evento e conversão no clique do
WhatsApp) e **13 do importador de fotos** (orientação do celular, corte,
larguras, GPS fora, foto sem lugar recusada).

A rodada achou e corrigiu: o atributo `hidden` perdia para o `display` do `.btn`
e mostrava o botão de recusar sem haver o que recusar; e o mapa do Google, com
proporção e altura mínima juntas, ficava com 442 px num celular de 320 e
empurrava a página para o lado. **O teste de celular não via isso**: media a
página contra o `innerWidth`, que no celular emulado cresce junto com o que
transborda. Passou a medir contra a largura do aparelho.

O mapa do Google não carrega aqui: a rede do ambiente de trabalho não alcança o
Google. As conferências checam o endereço do mapa e que ele só entra quando a
seção chega perto da tela; a nota aparece de verdade no celular de qualquer um.

Antes, **154 conferências** de ponta a ponta (desktop 1440 e Pixel 7) e **335 de
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
| `nicho`, `prateleira`, `tabua`, `ripado`, `aparador`, `cabeceira`, `sapateira`, `luminaria`, `bancada` | Peça da loja de mesmo nome |
| `cozinha`, `closet`, `escritorio`, `painel`, `compacta`, `dormitorio` | Projetos concluídos, mosaico da página inicial, simulador |
| `banheiro` | Simulador, ambiente Banheiro (guardado: não conta para o lançamento) |
| `oficina` | Faixa "Oficina aberta" da página inicial |
| `corte` | Detalhe da bancada na página A oficina |

Cada imagem tem duas larguras: `<nome>.webp` (1200 ou 1280 px) e `<nome>-640.webp`,
e o navegador escolhe pela largura em que ela aparece. Para trocar por foto real:
mesma proporção 4:3, mesmo nome, e rodar `python3 montar.py`. O
`gerador/fotos/importar.py` faz isso a partir das fotos do celular, com o nome do
lugar em cada arquivo: vira pela orientação, corta no centro, gera as larguras,
apaga os metadados (foto de celular traz o GPS de onde foi tirada, muitas vezes a
casa do cliente) e marca o lugar em `fotos/reais.json`.

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
