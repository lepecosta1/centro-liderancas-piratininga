#!/usr/bin/env python3
"""Gera os dois formatos de entrega a partir de uma única fonte de verdade.

  corpo.html + fontes-embutidas.css
        ├─→ artifact.html  corpo para publicação como Artifact (sem doctype/head/body)
        └─→ index.html     documento autônomo, para PDF e compartilhamento direto

As fontes entram embutidas em ambos, para que PDF, Artifact e HTML compartilhado
tenham exatamente a mesma tipografia — e funcionem sem rede.
"""
import re, pathlib

base = pathlib.Path(__file__).parent
corpo = (base / "corpo.html").read_text(encoding="utf-8")
fontes = (base / "fontes-embutidas.css").read_text(encoding="utf-8")

# as fontes deixam de vir da rede e passam a viajar dentro do arquivo
corpo = re.sub(r'<link\b[^>]*>\s*', "", corpo, flags=re.I)
corpo = corpo.replace("<style>", "<style>\n" + fontes, 1)

# O Artifact não tem o PDF ao lado; o botão só existe na versão hospedada.
(base / "artifact.html").write_text(
    corpo.replace("<!--BOTAO-PDF-->", "").strip() + "\n", encoding="utf-8")

# Endereço público da versão hospedada. Trocar aqui se a proposta mudar de casa
# (por exemplo, para um subdomínio do próprio marceneirotatuape.com.br).
SITE = "https://lepecosta1.github.io/centro-liderancas-piratininga/proposta-marcenaria-tatuape/"
PDF = "Proposta-Casa-do-Marceneiro-Tatuape.pdf"
RESUMO = ("Diagnóstico completo dos quatro canais, resgate dos ativos digitais e plano "
          "de oito semanas para a Casa do Marceneiro Tatuapé voltar ao mapa, à vitrine e à busca.")

botao = (f'<a class="baixar" href="{PDF}" download>'
         '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M8 1.8v8.4M4.6 6.9 8 10.3l3.4-3.4M2 12.6v1.6h12v-1.6"/></svg>'
         'Baixar em PDF</a><br>')
corpo = corpo.replace("<!--BOTAO-PDF-->", botao)

titulo = re.search(r"<title>.*?</title>", corpo, re.S | re.I).group(0)
estilo = re.search(r"<style>.*?</style>", corpo, re.S | re.I).group(0)
miolo = corpo.replace(titulo, "").replace(estilo, "").strip()

(base / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#1A120C">
  <meta name="description" content="{RESUMO}">
  <meta name="robots" content="noindex, nofollow">
  <link rel="canonical" href="{SITE}">

  <!-- Cartão de prévia: é o que WhatsApp, Telegram e iMessage mostram ao receber o link. -->
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="Casa do Marceneiro Tatuapé">
  <meta property="og:title" content="Casa do Marceneiro Tatuapé — Proposta comercial">
  <meta property="og:description" content="{RESUMO}">
  <meta property="og:url" content="{SITE}">
  <meta property="og:image" content="{SITE}capa-link.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="De volta ao mapa, à vitrine e à busca — proposta para a Casa do Marceneiro Tatuapé.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Casa do Marceneiro Tatuapé — Proposta comercial">
  <meta name="twitter:description" content="{RESUMO}">
  <meta name="twitter:image" content="{SITE}capa-link.png">

  <!-- Salvar na tela de início do celular -->
  <link rel="icon" type="image/png" href="icone.png">
  <link rel="apple-touch-icon" href="icone.png">
  <meta name="apple-mobile-web-app-title" content="Marceneiro Tatuapé">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  {titulo}
{estilo}
</head>
<body>
{miolo}
</body>
</html>
""", encoding="utf-8")

for nome in ("artifact.html", "index.html"):
    kb = (base / nome).stat().st_size / 1024
    print(f"{nome:<16} {kb:>7.0f} KB")
