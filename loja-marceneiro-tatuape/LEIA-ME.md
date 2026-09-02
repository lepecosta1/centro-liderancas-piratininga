# Fase 2 — Loja do Marceneiro

Proposta e protótipo funcional da loja online da Casa do Marceneiro Tatuapé.
Continuação da Fase 1 (`../proposta-marcenaria-tatuape/`), que já foi aceita.

## O que este documento decide

O ponto central: **e-commerce puro não funciona para marcenaria sob medida**, e
formulário de orçamento puro também não. A saída é um híbrido de três balcões —
Prateleira (compra direta), Balcão (configurador com faixa de preço na hora) e
Bancada (sob medida, como já é hoje).

A conclusão veio do benchmark, não de opinião: quem vende madeira online no
Brasil com sucesso **não vende catálogo, vende cálculo** — o cliente mexe em
alguma coisa e o preço responde na hora.

## Arquivos

| Arquivo | O que é |
|---|---|
| `corpo.html` | **Fonte única de verdade** — conteúdo, marcação da loja e toda a lógica |
| `base.css` | Sistema visual do documento, extraído da Fase 1 (mesmo cliente, mesma marca) |
| `loja.css` | Sistema visual da vitrine — tokens próprios, prefixados `--l-` |
| `montar.py` | Gera `index.html` e `artifact.html`; injeta as fontes já versionadas na Fase 1 |
| `index.html` | Documento autônomo, para PDF e hospedagem. *Gerado.* |
| `artifact.html` | Corpo para publicação como Artifact. *Gerado, fora do versionamento.* |
| `Proposta-Loja-Casa-do-Marceneiro.pdf` | 25 páginas, para enviar ao cliente |
| `capa-link.png` | Cartão de prévia de link |
| `gerador/` | Fonte do cartão |

## O protótipo

A aba "A loja" traz uma loja que funciona de verdade dentro da página: catálogo
com filtro, ficha de produto com opções que recalculam o preço, carrinho que
sobrevive ao recarregamento e configurador de orçamento que gera a mensagem de
WhatsApp já preenchida.

Ele existe para **validar decisão de produto e de fluxo antes de construir a loja
real** — errar no protótipo custa uma conversa, errar na loja pronta custa
dinheiro. Não processa pagamento, não guarda dado de ninguém e os valores são
ilustrativos: os reais saem na Semana 9, com o Gabriel.

## Decisões de projeto

**Dois mundos visuais no mesmo documento, de propósito.** O documento é a oficina
(nogueira escura); a loja é o balcão sob luz de dia (papel claro). Numa loja de
madeira quem tem que carregar a cor é o produto, não a interface. A vitrine
aparece emoldurada como uma janela de navegador — fica claro que é protótipo.

**A fronteira entre os dois é explícita.** O documento é escuro e pinta `b`,
`strong` e `.preco` para fundo escuro; dentro da loja isso desaparece no branco.
O bloco `.loja` reancora esses casos na entrada. Dois defeitos reais desse tipo
foram encontrados na conferência visual e corrigidos — vale conferir de novo ao
mexer no `base.css`.

**Cores calibradas por medição, não a olho.** `--l-mut2` foi ajustado até passar
o piso de 4,5:1 em texto pequeno, tanto no branco quanto no papel da loja.

## Conferência feita

Playwright dirigindo a loja de verdade: filtro de categoria, ficha, troca de
madeira e medida mudando o preço, carrinho somando e persistindo entre
recarregamentos, `Escape` fechando a ficha, cada ambiente e cada padrão do
configurador gerando faixa distinta, mensagem de WhatsApp com todos os campos.
Sem estouro horizontal em 375, 393 e 412 px. Zero erro de JavaScript.

Um alerta para quem for rodar os testes: use **caminho absoluto** para o
`index.html`. Com caminho relativo, o diretório de trabalho pode escorregar e o
teste carrega o `index.html` da Fase 1, falhando por motivo errado.

## Como reconstruir

```bash
python3 montar.py

/opt/pw-browsers/chromium --headless=new --no-sandbox --disable-gpu \
  --virtual-time-budget=30000 --force-color-profile=srgb \
  --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf=Proposta-Loja-Casa-do-Marceneiro.pdf "file://$PWD/index.html"
```
