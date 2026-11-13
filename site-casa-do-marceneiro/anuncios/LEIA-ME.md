# Campanhas do Google Ads e da Meta

Campanha de pesquisa local da Casa do Marceneiro, pronta para importar no
Google Ads Editor no dia em que a conta estiver liberada. A fonte é
`campanha.py`: mudou palavra, título ou negativa, muda ali e roda de novo.

```
python3 montar.py --dominio https://marceneirotatuape.com.br/ --forcar
python3 anuncios/campanha.py publicar/
```

O segundo comando recusa gravar se um título passar de 30 caracteres, uma
descrição de 90, ou se uma palavra-chave não aparecer na página para onde o
anúncio leva — relevância da página de destino é um dos três componentes do
Índice de Qualidade, junto com a taxa de cliques esperada e a relevância do
anúncio.

## Antes do primeiro real

1. **A conta existente liberada.** As três violações lidas e resolvidas, na
   conta que já existe. Conta nova para fugir de penalidade é violação por si só.
2. **O site no domínio**, `marceneirotatuape.com.br`, com cadeado.
3. **O site sem nada de exemplo.** Projeto ilustrativo, CNPJ de exemplo ou preço
   não confirmado em página de destino é o que o Google trata como deturpação —
   o mesmo tipo de problema que já travou a conta. É a mesma lista que o
   `montar.py --dominio` cobra para liberar a indexação: os dois ligam juntos.
4. **Medição ligada.** No Google Ads, criar duas conversões de site — *Clique
   no WhatsApp* e *Clique para ligar* — e pôr o `AW-…` e os rótulos no
   `medicao.json` (ver o LEIA-ME do site). Sem isso não há como saber que
   palavra traz cliente e qual só gasta.

## Como montar (plano de 13/11)

Três campanhas de Pesquisa, cada uma com verba própria (`CAMPANHAS` em
`campanha.py`), no cenário recomendado de R$ 1.300 por mês:

| Campanha | Onde | Por dia | Grupos |
|---|---|---|---|
| Pesquisa \| Sob medida \| Tatuapé 8 km | Raio de 8 km da Rua Elisiário, 143, opção "Presença" | R$ 30 | Marcenaria · Móveis sob medida e planejados · Cozinha planejada · Closet e guarda-roupa · Cama sob medida · Painel de TV e home office (+ loja, pausada) |
| Pesquisa \| Comercial \| São Paulo | Cidade de São Paulo | R$ 10 | Marcenaria comercial |
| Pesquisa \| Marca | Cidade de São Paulo | R$ 3 | Marca (só exata) |

Só Rede de Pesquisa, sem Display e sem parceiros; todos os dias, 7h às 22h;
correspondência exata e de frase, nunca ampla; "Maximizar cliques" com limite
de CPC no primeiro mês, "Maximizar conversões" depois de 30 conversões. A
local e a comercial têm "casa do marceneiro" como negativa, para não pagar por
quem já procura a oficina pelo nome.

## Meta Ads

As artes estão em `meta/`, geradas por `gerador/criativos/criativos.js` a
partir de fotos reais de obra (feed 1080 × 1350 e stories/Reels 1080 × 1920,
com o texto fora das faixas que o Instagram cobre). O filme do site
(`fotos/filme/casa-do-marceneiro.mp4`) é o Reels principal. Campanhas, públicos
e verbas: no documento "Plano de Crescimento — Casa do Marceneiro".

## O que olhar toda semana no primeiro mês

- **Termos de pesquisa:** o que as pessoas digitaram de verdade. Termo que não
  é cliente vira negativa em `campanha.py`.
- **Conversões por grupo:** grupo que gasta e não traz conversa perde verba.
- **Índice de Qualidade por palavra:** abaixo de 5, olhar se a página de destino
  fala daquilo — e, se não fala, o texto do site muda antes do lance.
