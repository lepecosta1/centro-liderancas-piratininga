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

(base / "artifact.html").write_text(corpo.strip() + "\n", encoding="utf-8")

titulo = re.search(r"<title>.*?</title>", corpo, re.S | re.I).group(0)
estilo = re.search(r"<style>.*?</style>", corpo, re.S | re.I).group(0)
miolo = corpo.replace(titulo, "").replace(estilo, "").strip()

(base / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#1A120C">
  <meta name="description" content="Proposta comercial de reconstrucao digital para a Casa do Marceneiro Tatuape: diagnostico dos quatro canais, resgate dos ativos e plano de oito semanas.">
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
