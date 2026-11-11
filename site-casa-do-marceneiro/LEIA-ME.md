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

A empresa é familiar e atua **há mais de 25 anos no mercado** — o texto do site
antigo da casa, que o Gabriel mandou manter em 10/11. O site não cita ano de
fundação em lugar nenhum (antes dizia 1980).

A página da oficina tem três blocos novos:

- **História** — empresa familiar, estilo artesanal, ofício passado de uma geração
  para a outra, parceria com escritório de arquitetura.
- **Missão, visão e valores** — cinco valores, cada um com um comportamento
  concreto em vez de um adjetivo. O quinto ocupa duas colunas, porque cinco
  cartões em três colunas deixariam uma célula vazia.
- **Ficha técnica** — duas colunas, o que entra e o que não entra. É o bloco mais
  afiado da página, e por isso mora na faixa escura, sozinho. A palavra MDP saiu
  do site inteiro em 10/11, a pedido: a coluna da recusa fala de chapa sem
  procedência, ferragem sem marca e acabamento só por fora.

**Números inventados saíram.** A capa anunciava "+800 projetos" e "4,9 no Google",
que eram invenção minha de protótipo. No lugar entraram três fatos que vêm da
própria empresa: o tempo de mercado, a matéria-prima de primeira linha e a garantia com assistência técnica.
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
| Endereço | Rua Elisiário, 143 — Tatuapé, São Paulo/SP · CEP 03306-080 (o CEP do perfil da oficina no Google Maps) |
| Ponto no mapa | -23.5483874, -46.575084 · perfil `cid=16711580082198323185` — tirados do link de rota do próprio perfil |
| E-mail | gabriellandiw@hotmail.com (o Gabriel não acompanha e-mail: o site só envia mensagem pelo WhatsApp) |

O formulário de contato envia de verdade, sem servidor: abre o WhatsApp da
oficina com a mensagem já montada (o envio por e-mail saiu em 10/11). O pedido de
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
`sitemap.xml`, `robots.txt`, `404.html`, o endereço antigo `/portfolio/` levando
a `/projetos/`, as fotos e só os arquivos do logo que a página usa. Fora da
Vercel saem também `CNAME`, `_redirects` e `_headers` (Cloudflare Pages, Netlify)
e `.htaccess` (HostGator e qualquer Apache), com as mesmas regras do
`vercel.json`: o redirecionamento do portfólio, a página 404, HTTPS e cache das
fotos. No domínio não existe checkout simulado nem bandeira de cartão: o carrinho vira **Pedir pelo
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
2. **Fotos reais.** As das obras já entraram (04/11, ver "Fotos reais das obras"):
   capa, os seis ambientes e o mosaico. Faltam a oficina, o corte e os nove
   produtos da loja: cada foto com o nome do lugar (`oficina.jpg`…) e
   `python gerador/fotos/importar.py <pasta>` — vira, corta, reduz, tira o GPS e
   marca o lugar em `fotos/reais.json`; o selo de 3D sai sozinho dali.
3. **Projetos reais.** Feito como galeria por ambiente (`obras.json`). Se o
   Gabriel quiser obras com bairro, metragem e prazo, ele passa os dados de cada
   uma e elas entram como mais um nível da galeria — sem isso, não se inventa.
4. **Confirmar com o Gabriel** e marcar no `lancamento.json`: CNPJ,
   horário, Instagram e as promessas que o site faz — garantia de 3 anos,
   visita sem custo, desconto por atraso, preço travado, prazos de retirada e
   entrega. Promessa publicada vira oferta e obriga (CDC, art. 30).
5. **Avaliações.** O `placeId` do perfil no Google (Google Meu Negócio → Pedir
   avaliações) em `GOOGLE.placeId` faz o botão abrir direto o formulário de nota.
   Comentários só entram em `AVALIACOES` com a autorização de quem escreveu.
6. **Domínio.** Conferir no Registro.br que o titular é o CNPJ do Gabriel e
   **anotar todos os registros de DNS de hoje, principalmente os MX**, para
   nenhum e-mail do domínio cair na troca.
7. **Hospedagem.** O plano grátis da Vercel (Hobby) é só para uso não
   comercial: a prévia pode ficar lá, o site da loja não. Três caminhos, todos
   com o mesmo build:
   - **Cloudflare Pages (recomendado, grátis, uso comercial liberado).** Ligar
     ao repositório; pasta raiz `site-casa-do-marceneiro`, comando
     `python3 montar.py --dominio https://marceneirotatuape.com.br/`, saída
     `publicar`. Lê os `_redirects` e `_headers` gerados.
   - **HostGator (o plano que o Gabriel já paga).** Rodar o mesmo comando aqui e
     enviar o conteúdo de `publicar/` para `public_html` pelo gerenciador de
     arquivos ou FTP, `.htaccess` incluído (é arquivo oculto: conferir que subiu).
     Cada atualização é um novo envio.
   - **Vercel Pro (US$ 20 por mês).** `vercel.json` já pronto; a Vercel transfere
     o projeto para uma conta no e-mail do Gabriel sem tirar o site do ar.
8. **DNS.** MX e TXT do e-mail ficam como estão em qualquer caminho.
   - Cloudflare: o endereço sem `www` exige o domínio como zona do Cloudflare,
     ou seja, trocar os servidores de nome no Registro.br. Recriar antes, no
     Cloudflare, todos os registros anotados no passo 6.
   - HostGator: nada muda no DNS se o domínio já aponta para a hospedagem.
   - Vercel: Settings → Domains → `marceneirotatuape.com.br` e
     `www.marceneirotatuape.com.br`, e no DNS os registros que ela mostrar —
     hoje, A `@` para `76.76.21.21` e CNAME `www` para `cname.vercel-dns.com`.

   Propagação: até 24 h. O build seguinte já sai com o domínio no canônico e no
   sitemap.
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

## Palavras-chave

O site fala a língua de quem procura marcenaria, não só cozinha (27/10): cada
página tem título e descrição com **marcenaria**, **móveis sob medida e
planejados** e **São Paulo / Tatuapé / Zona Leste**, e a capa mostra os seis
ambientes da casa — closet e guarda-roupa, cozinha, dormitório, painel de TV e
sala, home office, banheiro e lavabo —, cada um com o seu pedido de orçamento no
WhatsApp (`data-msg` no botão). A ficha do Google traz o mesmo em `knowsAbout`.

A campanha do Google Ads que usa essas palavras está em `anuncios/` (ver o
LEIA-ME de lá): `anuncios/campanha.py publicar/` confere se cada palavra-chave
aparece na página para onde o anúncio leva. Mudou o texto do site, roda de novo.

## O que ainda falta confirmar antes de subir

O `lancamento.json` é a lista que o `montar.py --dominio` cobra. Em detalhe:

1. **Há mais de 25 anos.** O site usa o texto do site antigo e não cita ano de
   fundação. Falta confirmar com o Gabriel o que cada foto comercial mostra (o
   salão, a academia, as estantes) e o ano e o arquiteto do ambiente da CasaCor.
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

Os testes agora moram no repositório, em `testes/` (antes ficavam numa pasta
temporária e se perderam quando o ambiente de trabalho reiniciou):

```
python3 montar.py
NODE_PATH=$(npm root -g) node testes/site.js            # prévia: computador e sete celulares
python3 montar.py --dominio https://marceneirotatuape.com.br/ --forcar
NODE_PATH=$(npm root -g) node testes/dominio.js         # o site como vai ao ar, servido como raiz
```

**Publicar a prévia (Artifact) sempre com todos os arquivos.** A página do
Artifact carrega as fotos como arquivos à parte. Se só a página for publicada
de novo, os arquivos antigos continuam lá e os novos não sobem. Em 04/11 a capa
nova saiu quebrada assim, enquanto os testes locais passavam. Por isso:

1. O `montar.py` grava `artifact-arquivos.json`, com a lista completa do que a
   prévia usa.
2. A publicação leva todos esses arquivos, e o que estiver publicado e não
   estiver na lista vai como `null`.
3. Depois de publicar, baixe a lista do que está no ar e monte uma pasta só
   com esses arquivos e a página publicada. Rode `node testes/site.js
   <pasta>/index.html` nela: imagem que não subiu aparece como falha.

Em 10/11: **118 conferências** na prévia e **31** no modo domínio, com o filme, a
entrada suave sem bloco invisível e o filme cabendo na tela dos sete celulares.

Em 04/11, com as fotos reais: **93 conferências** na prévia — endereço,
WhatsApp, simulador guardado, capa com foto real e sem pixelar em nenhuma tela, os seis ambientes com foto e
pedido próprio, o mosaico abrindo a galeria na foto clicada, os seis ambientes
de projetos sem nada de exemplo, a galeria (setas, teclado, miniaturas, vídeo
só no play, pedido dizendo o ambiente, Esc e ×), a loja; e, em sete celulares
(iPhone SE e 13, Pixel 7, Galaxy S9+ e de 320 px, iPad Mini, Moto G4), as seis
telas sem rolagem para o lado, a foto cabendo na tela e o arrastar para passar
de foto. **25 do modo domínio**: título e canônico, a galeria carregando da
raiz em `/projetos/`, as 33 fotos e o vídeo publicados, o pedido pelo
carrinho, `/portfolio/`, sitemap e a ficha do Google. Zero erro de JavaScript.

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

**Mapa e rotas (04/11).** O mapa do Google não entra quando a página está dentro
de outro site. É o caso do visor onde a prévia é aprovada, e ali aparecia a tela
cinza de "conteúdo bloqueado". O site agora percebe essa situação: dentro de uma
moldura, ou quando o navegador avisa que barrou o Maps, entra um cartão da
oficina sobre um traçado de ruas desenhado. Esse traçado é enfeite e não
pretende ser o mapa. O cartão abre o perfil no Google Maps. Logo abaixo do
mapa, com ele ou sem ele, ficam sempre dois botões:

- **Traçar a rota:** o link de rota do próprio perfil, até a porta.
- **Ir com o Waze:** abre no ponto exato.

Os mesmos botões estão no Como chegar do contato. "Ver as avaliações" abre o
perfil exato, e não uma busca. Cada clique de rota é medido: `como_chegar` no
Google e `FindLocation` na Meta. A ficha do Google ganhou CEP, coordenadas e o
link do perfil.

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

## A revisão de 10/11: filme, privacidade e o caminho para subir

**O filme.** A página inicial ganhou um filme de 35 segundos, em pé (720 × 1280),
feito só com fotos reais das obras: movimento lento de câmera, legendas na
tipografia do site, a marca e um cartão final com o endereço e o WhatsApp. O
vídeo só baixa quando alguém aperta o play; antes disso a página carrega uma
capa de 50 KB. O texto do filme está na página, para quem não vê ou não ouve.
O play é medido (`filme` no Google, `ViewContent` na Meta). O mesmo arquivo
serve para Reels, Stories e anúncio na Meta.

```
NODE_PATH=$(npm root -g) node gerador/filme/quadros.js <pasta dos quadros>
python3 gerador/filme/filme.py <pasta dos quadros> [--narracao <pasta>]
```

`gerador/filme/roteiro.json` guarda as falas, as legendas e as cenas. Com
`--narracao`, a pasta traz uma gravação por batida (`1.wav` … `5.wav`, ou mp3,
m4a, ogg): cada batida passa a durar o que a fala dura e o som entra no filme.
Sem narração o filme sai mudo, e as legendas contam a mesma história.

**A ordem da página inicial.** O trabalho real vem primeiro: capa, filme, os
ambientes com foto das obras, e só depois as três formas de comprar, as peças
prontas (ainda em 3D), as avaliações e a oficina.

**Privacidade: segunda conferência das fotos.** A curadoria de 04/11 olhou as
fotos em miniatura e deixou passar gente em quatro delas. Em 10/11 as 34 foram
vistas uma a uma, ampliadas:

| Foto | O que tinha | O que foi feito |
|---|---|---|
| `hall-revestido-madeira` | Uma pessoa agachada no corredor e uma sacola | Recorte: ficam a parede de madeira e o aparador |
| `dormitorio-painel-tv` | Uma pessoa na borda, latas de tinta e sacos de obra | Recorte: ficam o guarda-roupa, as prateleiras e o painel |
| `corredor-painel-tv` | Quem fotografava, refletido no espelho do fim do corredor | Borrão só no reflexo |
| `sala-painel-iluminado` | Duas pessoas refletidas na tela da TV | Tela escurecida, como já era na antiga capa |

Tudo isso mora no campo `retoque` de cada foto, em `obras.json` (`recorte`,
`borrar`, `tela`), e o `obras.py` aplica. Nenhum móvel foi alterado. Ficaram
como estão: colchão ainda no plástico em cinco fotos de dormitório, uma
furadeira sobre o guarda-corpo e uma mochila numa bancada.

**Refinamento visual.** Os blocos entram na tela com um movimento curto, uma
vez só (nada disso roda para quem pediu menos movimento, nem sem JavaScript);
o rótulo de cada seção ganhou um fio, como marca de régua; os títulos quebram
de forma equilibrada.

**Para subir sem risco: o ensaio em `/novo/`.** O site pode ser montado para
uma pasta do próprio domínio, fora do Google, sem tocar no site atual:

```
python3 montar.py --dominio https://marceneirotatuape.com.br/novo/ --forcar
python3 gerador/pacote.py ensaio.zip      # o .zip que se extrai em public_html/novo
```

O Gabriel abre `marceneirotatuape.com.br/novo/` e aprova vendo no domínio
dele. Na troca de verdade, o mesmo `pacote.py` fecha o `.zip` da raiz.

**As imagens 3D da loja.** As nove peças da loja ainda não têm foto. Há dois
caminhos, e a escolha é do Gabriel: fotografar cada peça pronta, ou aprovar
que elas vão ao ar com a imagem 3D e a etiqueta "Imagem 3D ilustrativa"
(`"imagens_3d_da_loja_aprovadas": true` no `lancamento.json`). A oficina e a
bancada não entram nessa exceção: ali a foto tem de ser do lugar.

## As imagens

### Fotos reais das obras (04/11)

O Gabriel mandou pelo Drive 60 arquivos: 31 fotos soltas, três `.zip` e uma
pasta que era um dos `.zip` já aberto, além de três vídeos. Comparadas pelo
conteúdo — o WhatsApp dá o mesmo nome a fotos diferentes —, eram **53 fotos
diferentes**: seis cópias exatas e uma recomprimida. Das 53 ficaram **33**: dez
pares quase iguais perderam a pior de cada par, e saíram as fotos com gente, com
bagunça de obra e a de uma TV mostrando imagem de terceiros. Na capa, a tela da
TV desligada refletia quem fotografava e foi escurecida; o móvel ficou como está.

- `obras.json` é a curadoria: cada foto (achada pelo hash do original), o
  ambiente, o texto alternativo, o foco do recorte e os lugares fixos do site.
- `gerador/fotos/obras.py <pastas dos originais>` gera `fotos/obras/<id>.webp`
  (lado maior de 1600 px) e `-640.webp`, os lugares fixos recortados no foco, o
  vídeo sem áudio e sem metadados, e marca os lugares em `fotos/reais.json`.
  Nada do GPS do celular é copiado.
- O `montar.py` junta a curadoria com os tamanhos e entrega ao site; recusa
  montar se faltar uma foto.

Os projetos concluídos são por **ambiente** — cozinhas, dormitórios e closets,
salas e home office, halls e divisórias, banheiros e lavabos, área gourmet —,
e não por obra: sem a confirmação do Gabriel, agrupar fotos em "obras" com
bairro, metragem e prazo seria inventar. Cada ambiente abre uma galeria em
tela cheia; o de cozinhas traz o tour em vídeo de 23 segundos.

Dois `.zip` do Drive (12 e 16 MB) e o vídeo maior passam do limite de 10 MB da
ferramenta de leitura do Drive e não foram abertos. Pelo tamanho, o de 16 MB
deve ser o vídeo de 15 MB; se algum tiver foto diferente, basta abrir a pasta
no próprio Drive, como foi feito com o primeiro.

### A capa (04/11, à tarde)

A capa é a foto da cozinha integrada à sala com LED no forro, que o Leandro
mandou à parte pelo chat. A foto do painel de TV, que era a capa, continua na
galeria de salas. Ela é uma foto **em pé**, de WhatsApp, com 902 × 1600 px e
119 KB. Esticada na largura de um computador, numa faixa deitada, ela
apareceria com menos de um pixel de arquivo por pixel de tela: pixelada. Por
isso a capa mudou de forma:

- **No computador**, a foto fica inteira, em pé, à direita. Ela se desfaz em
  fumaça para a esquerda, sobre `capa-fundo.webp`, que é a própria foto
  desfocada, escurecida e com névoa, e é ali que fica o texto. Uma névoa morna
  passa devagar sobre a emenda, e para quem pediu menos movimento ela fica
  parada.
- **No celular**, que também é em pé, a foto ocupa a largura toda e se desfaz
  para baixo, onde começa o título. O recorte tira um pouco do forro e mostra
  mais marcenaria.

A foto foi tratada pelo `obras.py` (função `melhorar`) com quatro passos
clássicos, sem inteligência artificial que redesenha a imagem: o móvel tem de
ser o que o Gabriel fez.

1. Os blocos da compressão saem só onde a foto é lisa: forro, parede e vidro.
   O veio da madeira e o mármore ficam como vieram.
2. A foto é ampliada em Lanczos para 1350 × 2395 px.
3. A nitidez volta só onde há borda.
4. Um grão fino entra para o degradê do forro não virar faixas.

O teste confere, no computador e nos sete celulares, que a capa sempre aparece
com pelo menos 0,9 pixel de arquivo por pixel de tela. A conta de hoje vai de
0,92 no Galaxy S9+, a tela mais densa, a 1,4 no iPad; no computador fica em
1,0. O tratamento da capa precisa do OpenCV
(`pip install opencv-python-headless`). O original não vai para o repositório,
como os demais: ele está no chat e precisa entrar na pasta do Drive.

### Os lugares fixos

| Arquivo em `fotos/` | Onde aparece | Foto |
|---|---|---|
| `capa-1350/720.webp` e `capa-fundo.webp` | Capa do site | Real: cozinha integrada à sala, com LED no forro (ver "A capa") |
| `cozinha`, `closet`, `escritorio`, `painel`, `dormitorio`, `banheiro` | Os seis ambientes da página inicial; simulador guardado | Real |
| `nicho`, `prateleira`, `tabua`, `ripado`, `aparador`, `cabeceira`, `sapateira`, `luminaria`, `bancada` | Peça da loja de mesmo nome | 3D — falta a foto da peça pronta |
| `oficina` | Faixa "Oficina aberta" da página inicial | 3D — falta a foto da oficina |
| `corte` | Detalhe da bancada na página A oficina | 3D — falta a foto da bancada |

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

## Pedido de 10/11

- **Capa** com a mensagem do site antigo (empresa familiar, há mais de 25 anos,
  estilo artesanal, matéria-prima de primeira linha, prazo, assistência e garantia).
- **Área comercial**: faixa escura na página inicial (`#comercial`) e o álbum
  "Projetos comerciais" em `obras.json`.
- **Cama sob medida** e **CasaCor**: dois álbuns novos, com chamada na página
  inicial (`#especiais`). As fotos da pasta Projetos concluídos entraram nos
  álbuns de cozinhas e de salas.
- **Loja sem valor** (`SEM_PRECO` em `corpo.html`): cada peça diz "Valor sob
  medida" e o botão manda a escolha (peça, madeira, medida, quantidade) para o
  WhatsApp. Aviso de imagens ilustrativas no topo da loja e em cada cartão. O
  carrinho e o pagamento ficaram no código, fora do ar; `SEM_PRECO = false` religa.
- **Contato só por WhatsApp**; o e-mail mostrado passou a ser o do Gabriel.
- Fotos pequenas (lado maior abaixo de 900 px, caso das da CasaCor) são ampliadas
  pelo `obras.py` com o mesmo `melhorar` da capa.
