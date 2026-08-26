# Proposta — Casa do Marceneiro Tatuapé

Proposta comercial de reconstrução digital para a marcenaria de Gabriel Landi
(Tatuapé, São Paulo). Documento interativo de oito abas, com versão em PDF para
compartilhamento.

## Arquivos

| Arquivo | O que é |
|---|---|
| `corpo.html` | **Fonte única de verdade.** Título, estilos e conteúdo. É aqui que se edita. |
| `fontes.py` | Baixa Fraunces, Barlow e Barlow Condensed do Google Fonts e gera `fontes-embutidas.css` com as fontes em data URI (subset `latin`, que cobre o pt-BR). |
| `montar.py` | Gera os dois formatos de entrega a partir de `corpo.html` + fontes embutidas. |
| `index.html` | Documento autônomo — o que se compartilha e o que vira PDF. *Gerado.* |
| `artifact.html` | Corpo para publicação como Artifact, sem `doctype`/`head`/`body`. *Gerado, fora do versionamento.* |
| `Proposta-Casa-do-Marceneiro-Tatuape.pdf` | Versão para enviar ao cliente. |

## Como reconstruir

```bash
python3 fontes.py   # só quando as fontes mudarem; precisa de rede
python3 montar.py   # gera index.html e artifact.html

/opt/pw-browsers/chromium --headless=new --no-sandbox --disable-gpu \
  --virtual-time-budget=25000 --force-color-profile=srgb \
  --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf=Proposta-Casa-do-Marceneiro-Tatuape.pdf "file://$PWD/index.html"
```

## Decisões de projeto

**Um mundo visual só.** Nogueira escura sob luz de verniz. A peça não troca de
tema conforme o sistema do leitor — todas as cores são pintadas explicitamente,
para o documento se manter igual em qualquer fundo.

**Impressão é o mesmo sistema, virado para o papel.** O bloco `@media print`
redefine apenas os tokens de cor: papel quente, tinta nogueira. Nenhum componente
declara cor fora dos tokens, então a virada é completa.

**Fontes viajam dentro do arquivo.** Embutidas em base64, para que PDF, Artifact e
HTML compartilhado tenham a mesma tipografia mesmo sem rede.

**O acordeão das semanas é melhoria progressiva.** Os `<details>` nascem `open` no
HTML — assim o PDF e a leitura sem JavaScript trazem o conteúdo inteiro. O script
fecha as semanas 2 a 8 na tela e reabre todas antes de imprimir.

**A paleta dos gráficos foi validada por script**, não a olho: as quatro trilhas do
cronograma e a rampa âmbar do funil passam nos testes de banda de luminosidade,
piso de croma, separação sob daltonismo e contraste contra o fundo.

## Pendência conhecida

O diagnóstico do domínio `marceneirotatuape.com.br` é **hipótese**, não laudo. A
tentativa de consultar o domínio a partir do ambiente de desenvolvimento foi
bloqueada pela política de saída de rede, então não foi possível distinguir
hospedagem vencida de domínio expirado. A proposta declara isso abertamente e
coloca a consulta oficial de WHOIS como primeiro item das 72 horas iniciais.
