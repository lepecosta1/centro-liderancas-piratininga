#!/usr/bin/env python3
"""Monta o site a partir de uma fonte única.

  corpo.html (+ site.css, fontes compartilhadas)
        ├─→ artifact.html  corpo para publicação como Artifact
        └─→ index.html     página autônoma, para hospedar e compartilhar

As fontes vêm da Fase 1: mesmo cliente, mesma marca, arquivo já
versionado — não faz sentido baixar de novo nem duplicar 400 KB.
"""
import pathlib, re

base = pathlib.Path(__file__).parent
corpo = (base / "corpo.html").read_text(encoding="utf-8")

fontes = (base / ".." / "proposta-marcenaria-tatuape" / "fontes-embutidas.css").read_text(encoding="utf-8")
css = (base / "site.css").read_text(encoding="utf-8")

corpo = corpo.replace("/*CSS-SITE*/", fontes + "\n" + css)

(base / "artifact.html").write_text(corpo.strip() + "\n", encoding="utf-8")

SITE = "https://lepecosta1.github.io/centro-liderancas-piratininga/site-casa-do-marceneiro/"
RESUMO = ("Marcenaria propria no Tatuape desde 2009: pecas prontas com preco fechado, corte de chapa "
          "na medida e projeto sob medida com visita tecnica.")

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
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="Casa do Marceneiro Tatuapé">
  <meta property="og:title" content="Casa do Marceneiro Tatuapé">
  <meta property="og:description" content="{RESUMO}">
  <meta property="og:url" content="{SITE}">
  <meta property="og:image" content="{SITE}capa-link.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{SITE}capa-link.png">
  <link rel="icon" type="image/png" href="../proposta-marcenaria-tatuape/icone.png">
  <link rel="apple-touch-icon" href="../proposta-marcenaria-tatuape/icone.png">
  {titulo}
{estilo}
</head>
<body>
{miolo}
</body>
</html>
""", encoding="utf-8")

for nome in ("artifact.html", "index.html"):
    print(f"{nome:<16} {(base / nome).stat().st_size / 1024:>7.0f} KB")
