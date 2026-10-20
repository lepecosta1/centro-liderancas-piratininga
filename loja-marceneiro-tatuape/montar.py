#!/usr/bin/env python3
"""Monta os dois formatos de entrega da Fase 2 a partir de uma fonte única.

  corpo.html (+ base.css, loja.css, fontes compartilhadas)
        ├─→ artifact.html  corpo para publicação como Artifact
        └─→ index.html     documento autônomo, para PDF e compartilhamento

As fontes vêm da Fase 1: mesmo cliente, mesma marca, e o arquivo já está
versionado — não faz sentido baixar de novo nem duplicar 400 KB.
"""
import pathlib, re

base = pathlib.Path(__file__).parent
corpo = (base / "corpo.html").read_text(encoding="utf-8")

fontes = (base / ".." / "proposta-marcenaria-tatuape" / "fontes-embutidas.css").read_text(encoding="utf-8")
css_base = (base / "base.css").read_text(encoding="utf-8")
css_loja = (base / "loja.css").read_text(encoding="utf-8")

corpo = corpo.replace("/*CSS-BASE*/", fontes + "\n" + css_base).replace("/*CSS-LOJA*/", css_loja)

(base / "artifact.html").write_text(corpo.strip() + "\n", encoding="utf-8")

SITE = "https://lepecosta1.github.io/centro-liderancas-piratininga/loja-marceneiro-tatuape/"
RESUMO = ("Estudo de referencias, protótipo funcional e plano de execução da loja online "
          "da Casa do Marceneiro Tatuapé: tres balcoes, seguranca de pagamento e teste fechado antes dos anuncios.")

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
  <meta property="og:title" content="Loja do Marceneiro — Fase 2">
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
