#!/usr/bin/env python3
"""Baixa as fontes do Google Fonts e as embute como data URI.

Deixa o documento autossuficiente: o PDF, o Artifact e o HTML compartilhado
renderizam com a mesma tipografia, sem depender de rede na hora da leitura.
"""
import base64, re, subprocess, sys

CSS_URL = ("https://fonts.googleapis.com/css2?"
           "family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700;9..144,900"
           "&family=Barlow+Condensed:wght@500;600;700"
           "&family=Barlow:wght@400;500;600;700&display=swap")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
# pt-BR precisa de latin + latin-ext; os demais subsets só engordariam o arquivo.
SUBSETS = ("latin",)  # pt-BR cabe inteiro no subset latin (U+00C0-00FF)

def buscar(url, binario=False):
    r = subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-A", UA, url],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"falha ao buscar {url}: {r.stderr.decode()[:200]}")
    return r.stdout if binario else r.stdout.decode("utf-8")

css = buscar(CSS_URL)
blocos = re.findall(r"(/\*\s*([\w-]+)\s*\*/\s*)?@font-face\s*\{.*?\}", css, re.S)
partes, total = [], 0

for bloco in re.finditer(r"(?:/\*\s*(?P<sub>[\w-]+)\s*\*/\s*)?(?P<face>@font-face\s*\{.*?\})", css, re.S):
    sub, face = bloco.group("sub"), bloco.group("face")
    if sub and sub not in SUBSETS:
        continue
    m = re.search(r"url\((https://[^)]+\.woff2)\)", face)
    if not m:
        continue
    dados = buscar(m.group(1), binario=True)
    total += len(dados)
    b64 = base64.b64encode(dados).decode("ascii")
    partes.append(face.replace(m.group(1), f"data:font/woff2;base64,{b64}"))

if not partes:
    sys.exit("nenhuma @font-face capturada — abortando")

saida = "/* Fontes embutidas: Fraunces (display), Barlow (texto), Barlow Condensed (etiquetas) */\n"
saida += "\n".join(partes) + "\n"
open("fontes-embutidas.css", "w", encoding="utf-8").write(saida)
print(f"{len(partes)} @font-face embutidas · {total/1024:.0f} KB de fonte · "
      f"{len(saida)/1024:.0f} KB de CSS")
