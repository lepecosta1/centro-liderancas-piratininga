# Primeira campanha do Google Ads — R$ 500 por mês

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

## Como montar

| Configuração | Valor | Por quê |
|---|---|---|
| Tipo | Rede de Pesquisa, sem Display e sem parceiros | Verba pequena vai inteira para quem está procurando |
| Orçamento | R$ 16 por dia (≈ R$ 500 no mês) | O Google pode gastar até o dobro num dia, mas fecha o mês dentro de 30,4 × o diário |
| Local | Raio de 6 km da Rua Elisiário, 143 — Tatuapé, só "presença" (quem está ou costuma estar ali) | A oficina atende perto; clique de quem só pesquisa sobre São Paulo de longe não vira visita |
| Idioma | Português | |
| Lances | Maximizar cliques com limite de CPC no começo; Maximizar conversões depois das primeiras 15 a 30 conversões | Estratégia de conversão sem histórico de conversão adivinha |
| Horário | Todos os dias, 7h às 22h | Quem procura móvel planejado pesquisa à noite; a mensagem fica no WhatsApp para o Gabriel responder de manhã |
| Grupos | Marcenaria · Móveis sob medida e planejados · Closet e guarda-roupa ligados; Móveis de madeira prontos pausado | A loja só liga com os preços confirmados |

Palavras em correspondência **exata** e **de frase**, nunca ampla: com R$ 500,
a ampla gasta a verba em busca parecida que não é cliente. As negativas tiram
curso, emprego, faça você mesmo, usado, loja de móvel pronto e corte de chapa
avulso, que a oficina não vende.

## Quanto rende R$ 500

Depende do custo por clique de cada palavra no Tatuapé, que só o Planejador de
Palavras-chave mostra, dentro da conta. A conta é simples:

| Se o clique custar | Cliques no mês | Se 1 em 10 chamar no WhatsApp |
|---|---|---|
| R$ 2 | 250 | 25 conversas |
| R$ 4 | 125 | 12 conversas |
| R$ 6 | 83 | 8 conversas |

Os números da tabela são hipóteses para mostrar a conta, não previsão. O
primeiro passo na conta é rodar as palavras de `campanha.py` no Planejador,
com o raio da oficina, e cortar as que passarem do que uma obra paga.

## O que olhar toda semana no primeiro mês

- **Termos de pesquisa:** o que as pessoas digitaram de verdade. Termo que não
  é cliente vira negativa em `campanha.py`.
- **Conversões por grupo:** grupo que gasta e não traz conversa perde verba.
- **Índice de Qualidade por palavra:** abaixo de 5, olhar se a página de destino
  fala daquilo — e, se não fala, o texto do site muda antes do lance.
