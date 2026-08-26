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
| `capa-link.png` | Cartão de prévia do link, para o WhatsApp. |
| `gerador/cartao.html` | Fonte do cartão. |

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

## Decisões que valem explicar

**As fotos que não existem.** O acervo do Gabriel ainda não chegou. Em vez de
caixa cinza vazia — que faz o site parecer quebrado numa reunião de aprovação —
cada imagem é uma chapa de madeira desenhada por gradiente, com a peça em linha
por cima e uma etiqueta discreta dizendo o que entra ali. O site parece pronto e
o buraco fica visível para quem produz. **Esse é o caminho crítico da fase.**

**Um visual só, claro.** Sem tema escuro. É uma vitrine que o Gabriel vai abrir
na frente do cliente, na oficina, sob luz de dia; uma segunda aparência para
manter não vende mais um armário. Nogueira escura entra só nas faixas
estruturais — capa, rodapé, chamada de preço.

**Veio horizontal.** A primeira versão listrava na vertical e lia como cortina,
não como chapa. Ângulo corrigido para 2°.

**O aviso de prévia.** Fica no topo, some ao fechar e volta a cada nova sessão.
Ninguém deve confundir isto com a loja no ar.

**QR de demonstração.** O padrão desenhado não é um QR válido, de propósito:
ninguém pode pagar por engano numa prévia. O rótulo diz isso embaixo do código.

## O que precisa ser preenchido antes de subir

1. **WhatsApp.** `TEL` em `corpo.html` está em `5511900000000`. Trocar pelo real.
2. **Endereço, telefone e CNPJ.** Estão como `000`. Precisam bater **letra por
   letra** com o Google Meu Negócio e com o Instagram — é esse casamento que faz
   a oficina aparecer na busca de quem está a dois quarteirões.
3. **Fotos e vídeos.** Peças, ambientes entregues e a oficina.
4. **Preços reais.** Os do protótipo são ilustrativos.
5. **Depoimentos.** Trocar pelos reais do Google, com autorização de quem assina.
6. **Mapa.** Entra depois que o pin do Google estiver corrigido.
7. **Título da aba.** Está só `Casa do Marceneiro Tatuapé`, que é o nome. Na
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

89 asserções com Playwright dirigindo o site de verdade em celular emulado:
navegação por rota e por menu, filtro, busca, ordenação, cadeia de preço na
ficha, carrinho somando e persistindo, frete por três faixas de CEP, checkout
recusando CPF e cartão inválidos e aceitando os válidos, relógio do PIX
correndo, pedido concluído com número gerado e carrinho zerado, cinco ambientes
e três padrões do configurador dando faixas distintas, formulário de contato,
`Escape` fechando sobreposições, aviso de LGPD com memória. Sem estouro
horizontal em 360, 375, 393, 412, 768, 1280 e 1440 px. Zero erro de JavaScript.
Todo texto passa no piso de contraste WCAG AA, medido cor a cor.
