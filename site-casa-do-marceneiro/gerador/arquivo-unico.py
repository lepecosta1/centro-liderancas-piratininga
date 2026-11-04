#!/usr/bin/env python3
"""Gera um HTML único, com todas as fotos e o vídeo dentro, para testar o site sem servidor
— no celular do Gabriel, por WhatsApp ou e-mail.

    python3 gerador/arquivo-unico.py <arquivo de saída>

Parte da prévia (index.html, já montada pelo montar.py). Cada imagem entra uma
vez só, na largura grande: repetir a mesma foto embutida em duas larguras
dobraria o arquivo sem ganho visível.
"""
import base64, pathlib, re, sys

SITE = pathlib.Path(__file__).resolve().parents[1]
saida = pathlib.Path(sys.argv[1])
html = (SITE / "index.html").read_text(encoding="utf-8")
TIPOS = {".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".mp4": "video/mp4"}

def uri(arq):
    return f"data:{TIPOS[arq.suffix]};base64," + base64.b64encode(arq.read_bytes()).decode()

def troca(a, n):
    global html
    assert html.count(a) == 1, f"mudou no site: {a[:70]}"
    html = html.replace(a, n)

# capa: uma largura, sem pré-carregamento
html = re.sub(r'\s*<link rel="preload" as="image" href="fotos/capa-1600\.webp"[^>]*>', "", html)
troca(' srcset="fotos/capa-960.webp 960w, fotos/capa-1600.webp 1600w"', "")
troca('src="fotos/capa-1600.webp"', f'src="{uri(SITE / "fotos" / "capa-1600.webp")}"')
for nome in ("logo-site.svg", "icone.svg", "favicon-32.png", "apple-touch-icon.png"):
    html = html.replace(f'"marca/{nome}"', f'"{uri(SITE / "marca" / nome)}"')

# um mapa nome → arquivo embutido; as funções de imagem leem dele
emb = {p.stem: uri(p) for p in sorted((SITE / "fotos").glob("*.webp")) if not re.search(r"-(640|960|1600)$", p.stem)}
for p in sorted((SITE / "fotos" / "obras").glob("*")):
    if p.suffix == ".webp" and not p.stem.endswith("-640"):
        emb["obras/" + p.stem] = uri(p)
    elif p.suffix == ".mp4":
        emb["obras/" + p.stem + ".mp4"] = uri(p)
troca("  var FOTOS = \"fotos/\";", "  var FOTOS = \"fotos/\";\n  var EMB = " +
      "{" + ",".join(f'"{k}":"{v}"' for k, v in emb.items()) + "};")
troca('''    return '<img src="' + FOTOS + nome + '-640.webp" srcset="' + FOTOS + nome + '-640.webp 640w, ' +
      FOTOS + nome + '.webp ' + w + 'w" sizes="' + (sizes || "(max-width: 760px) 100vw, 420px") + '" width="' + w +''',
      '''    return '<img src="' + EMB[nome] + '" width="' + w +''')
troca('''    var base = FOTOS + "obras/" + f.id;
    return '<img src="' + base + '-640.webp" srcset="' + base + '-640.webp 640w, ' + base + '.webp ' + f.w + 'w" sizes="' +
      (sizes || "(max-width: 760px) 100vw, 420px") + '" width="' + f.w''',
      '''    return '<img src="' + EMB["obras/" + f.id] + '" width="' + f.w''')
troca('''var capa = FOTOS + "obras/" + item.id + "-capa.webp";''', '''var capa = EMB["obras/" + item.id + "-capa"];''')
troca('''<source src="' + FOTOS + 'obras/' + item.id + '.mp4" type="video/mp4">''', '''<source src="' + EMB["obras/" + item.id + ".mp4"] + '" type="video/mp4">''')
troca('''? '<img src="' + FOTOS + 'obras/' + item.id + '.webp" width="''', '''? '<img src="' + EMB["obras/" + item.id] + '" width="''')
troca(''': '<img src="' + FOTOS + 'obras/' + item.id + '-640.webp" alt=""''', ''': '<img src="' + EMB["obras/" + item.id] + '" alt=""''')
troca('''if (!v.video) (new Image()).src = FOTOS + "obras/" + v.id + ".webp";''', '''if (!v.video) (new Image()).src = EMB["obras/" + v.id];''')

sobra = re.findall(r'''(?:src|href|srcset)=["'](?:fotos|marca)/[^"']*''', html)
assert not sobra, sobra
saida.write_text(html, encoding="utf-8")
print(f"{saida.name}: {saida.stat().st_size / 1024 / 1024:.1f} MB, {len(emb)} arquivos dentro")
