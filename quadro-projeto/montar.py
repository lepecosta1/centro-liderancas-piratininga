#!/usr/bin/env python3
"""Monta o quadro do projeto a partir de fontes separadas.

  molde.html + estado.json + quadro.css + app.js
        ├─→ artifact.html  corpo para publicação como Artifact
        └─→ index.html     página autônoma, abre de um arquivo

A página republica a si mesma quando alguém marca um item, e para
isso precisa carregar o próprio molde e o próprio código como texto,
além de executá-los. Em vez de duplicar isso à mão na fonte — que
seria a primeira coisa a sair de sincronia — o build injeta o mesmo
conteúdo nos dois lugares.
"""
import json, pathlib, re

base = pathlib.Path(__file__).parent
corpo = (base / "corpo.html").read_text(encoding="utf-8")
molde = (base / "molde.html").read_text(encoding="utf-8").strip()
app = (base / "app.js").read_text(encoding="utf-8").strip()
css = (base / "quadro.css").read_text(encoding="utf-8")
fontes = (base / ".." / "proposta-marcenaria-tatuape" / "fontes-embutidas.css").read_text(encoding="utf-8")

for nome, texto in (("molde.html", molde), ("app.js", app)):
    if "</script" in texto.lower():
        raise SystemExit(f"{nome} contém </script>, o que fecharia o bloco de texto cedo demais")

publico = json.loads((base / "estado.json").read_text(encoding="utf-8"))

# O financeiro mora em privado.json, fora do Git: o repositório e o GitHub
# Pages são públicos, o artifact não. Só o artifact recebe esses campos.
privado = {}
if (base / "privado.json").exists():
    privado = json.loads((base / "privado.json").read_text(encoding="utf-8"))
    choque = set(privado) & set(publico)
    if choque:
        raise SystemExit(f"privado.json repete campos do estado público: {sorted(choque)}")

A, F = "<scr" + "ipt", "</scr" + "ipt>"

def montar(estado):
    texto = json.dumps(estado, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return (corpo
            .replace("/*CSS*/", fontes + "\n" + css)
            .replace("<!--ESTADO-->", f'{A} type="application/json" id="estado">{texto}{F}')
            .replace("<!--MOLDE-->", molde + "\n\n" + f'{A} type="text/plain" id="molde">{molde}{F}')
            .replace("<!--FONTE-->", f'{A} type="text/plain" id="fonte">{app}{F}')
            .replace("<!--APP-->", f"{A}>{app}{F}"))

(base / "artifact.html").write_text(montar({**publico, **privado}).strip() + "\n", encoding="utf-8")

corpo = montar(publico)
titulo = re.search(r"<title>.*?</title>", corpo, re.S | re.I).group(0)
estilo = re.search(r'<style id="folha">.*?</style>', corpo, re.S | re.I).group(0)
miolo = corpo.replace(titulo, "").replace(estilo, "").strip()
for campo in privado:
    if f'"{campo}"' in miolo:
        raise SystemExit(f"o campo privado {campo!r} vazou para o index.html público")

(base / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#1A120C">
<meta name="robots" content="noindex, nofollow">
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
print("privado.json     " + ("montado só no artifact" if privado else "ausente — artifact sem financeiro"))
