#!/usr/bin/env python3
"""Monta o site a partir de uma fonte única.

  corpo.html (+ site.css, fontes compartilhadas)
        ├─→ artifact.html  corpo para publicação como Artifact
        ├─→ index.html     a prévia, para hospedar e compartilhar (fora do Google)
        └─→ publicar/      com --dominio: o site de verdade, uma página por tela

    python3 montar.py                                          # prévia
    python3 montar.py --dominio https://marceneirotatuape.com.br/

O modo domínio confere o lancamento.json e o texto final antes de sair
indexável: CNPJ de exemplo, foto 3D, preço não confirmado ou palavra de
prévia barram a publicação. --forcar monta assim mesmo, mas com noindex e
com o aviso de prévia no topo — para mostrar e testar no endereço de
verdade sem o Google guardar nada inventado nem o visitante tomar o
protótipo por loja pronta. É o que a Vercel roda (ver vercel.json).

As fontes vêm da Fase 1: mesmo cliente, mesma marca, arquivo já
versionado — não faz sentido baixar de novo nem duplicar 400 KB.
"""
import argparse, datetime, html as H, json, os, pathlib, re, shutil, sys
from urllib.parse import urlparse

base = pathlib.Path(__file__).parent
fonte = (base / "corpo.html").read_text(encoding="utf-8")
fontes = (base / ".." / "proposta-marcenaria-tatuape" / "fontes-embutidas.css").read_text(encoding="utf-8")
css = (base / "site.css").read_text(encoding="utf-8")

PREVIA = "https://casa-do-marceneiro-tatuape.vercel.app/"
RESUMO = ("Marcenaria em São Paulo desde 1980, no Tatuapé: móveis sob medida e planejados para closet, "
          "guarda-roupa, cozinha, dormitório e sala, e móveis de madeira prontos. Orçamento pelo WhatsApp.")

# O simulador de sob medida fica guardado, fora do ar, até o Gabriel liberar:
# tudo entre <!--SIMULADOR--> sai de todas as versões do site, e o que está
# entre <!--SEM-SIMULADOR--> ocupa o lugar. Para religar, True.
SIMULADOR = False
SO_DO_SIMULADOR = {"banheiro"}   # foto que só o simulador mostra
REDES = ["https://www.facebook.com/CasaDoMarceneiroTatuape/", "https://www.instagram.com/casadomarceneirotatuape/"]
CNPJ_EXEMPLO = "00.000.000/0001-00"

# Cada tela vira uma página no domínio, com título e descrição próprios:
# é assim que "painel ripado no Tatuapé" acha a página de projetos, e não só a capa.
TELAS = {
    "inicio": ("Marcenaria em São Paulo: móveis sob medida e planejados | Casa do Marceneiro Tatuapé", RESUMO),
    "loja": ("Móveis de madeira prontos: aparador, sapateira, nicho e mais | Casa do Marceneiro Tatuapé",
             "Móveis de madeira da marcenaria do Tatuapé, em São Paulo: aparador, sapateira, luminária, nicho, "
             "prateleira, mesa de cabeceira e bancada. Preço fechado e pedido pelo WhatsApp."),
    "sob-medida": ("Simulador de móveis sob medida | Casa do Marceneiro Tatuapé",
                   "Escolha o ambiente, os metros e o padrão de acabamento e veja na hora a faixa de investimento "
                   "de cozinha, closet, home office, painel ou banheiro sob medida."),
    "projetos": ("Móveis planejados e sob medida: projetos concluídos | Casa do Marceneiro Tatuapé",
                 "Closets, guarda-roupas, cozinhas, painéis de TV, home offices e dormitórios planejados e feitos "
                 "sob medida pela marcenaria Casa do Marceneiro, no Tatuapé, Zona Leste de São Paulo."),
    "oficina": ("Marcenaria familiar em São Paulo desde 1980 | Casa do Marceneiro Tatuapé",
                "Marcenaria familiar desde 1980 na Rua Elisiário, no Tatuapé, Zona Leste de São Paulo, com "
                "acabamento em maquinário de primeira linha. Missão, valores, garantias e como trabalhamos."),
    "contato": ("Marcenaria no Tatuapé: endereço, WhatsApp e orçamento | Casa do Marceneiro",
                "Orçamento de móveis sob medida pelo WhatsApp e telefone (11) 94752-3961. Marcenaria na "
                "Rua Elisiário, 143, Tatuapé, Zona Leste de São Paulo. Veja como chegar."),
    "politicas": ("Privacidade, trocas e devoluções | Casa do Marceneiro Tatuapé",
                  "Como a Casa do Marceneiro Tatuapé trata os seus dados e o que vale para trocas, devoluções e "
                  "defeitos, pelo Código de Defesa do Consumidor e pela LGPD."),
}
if not SIMULADOR:
    del TELAS["sob-medida"]
ANTIGOS = {"portfolio": "projetos"}   # endereços do site antigo que o Google já conhece

args = argparse.ArgumentParser()
args.add_argument("--dominio", help="endereço final, ex.: https://marceneirotatuape.com.br/")
args.add_argument("--forcar", action="store_true", help="monta mesmo com pendências, mas fora do Google")
args.add_argument("--medicao", default="medicao.json", help="arquivo com os identificadores de medição")
args = args.parse_args()

def ler_json(nome, padrao):
    arq = base / nome
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else padrao

reais = ler_json("fotos/reais.json", {})
medicao = ler_json(args.medicao, {})

def injetar(texto, nome, valor):
    alvo = f"  var {nome} = {{}};"
    assert texto.count(alvo) == 1, nome
    return texto.replace(alvo, f"  var {nome} = {json.dumps(valor, ensure_ascii=False)};")

guarda, mostra = ("SEM-SIMULADOR", "SIMULADOR") if SIMULADOR else ("SIMULADOR", "SEM-SIMULADOR")
fonte = re.sub(rf"<!--{guarda}-->.*?<!--/{guarda}-->", "", fonte, flags=re.S)
fonte = re.sub(rf"<!--/?{mostra}-->", "", fonte)
corpo = fonte.replace("/*CSS-SITE*/", fontes + "\n" + css)
corpo = injetar(corpo, "REAIS", reais)

# ---------------------------------------------------------------- prévia
(base / "artifact.html").write_text(corpo.strip() + "\n", encoding="utf-8")

def ficha(url):
    """Ficha da empresa para o Google: os mesmos dados do rodapé, letra por letra."""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FurnitureStore",
        "name": "Casa do Marceneiro Tatuapé",
        "description": RESUMO,
        "url": url,
        "logo": url + "marca/icone-512.png",
        "image": url + "capa-link.jpg",
        "telephone": "+55 11 94752-3961",
        "email": "contato@marceneirotatuape.com.br",
        "foundingDate": "1980",
        "address": {"@type": "PostalAddress", "streetAddress": "Rua Elisiário, 143 - Tatuapé",
                    "addressLocality": "São Paulo", "addressRegion": "SP", "addressCountry": "BR"},
        "areaServed": [{"@type": "City", "name": "São Paulo"},
                       {"@type": "Place", "name": "Tatuapé, Zona Leste de São Paulo"}],
        "knowsAbout": ["Marcenaria", "Móveis sob medida", "Móveis planejados", "Closet e guarda-roupa sob medida",
                       "Cozinha planejada", "Móveis de dormitório", "Painel de TV", "Home office",
                       "Móveis de banheiro", "Móveis de madeira maciça"],
        "sameAs": REDES,
    }, ensure_ascii=False).replace("</", "<\\/")

def pagina(miolo, *, titulo, descricao, url, canonico, raiz, robots, atributos):
    """Página inteira. O miolo traz o estilo (inline ou <link>) e o corpo."""
    t, d = H.escape(titulo), H.escape(descricao, quote=True)
    return f"""<!DOCTYPE html>
<html lang="pt-BR"{atributos}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#1A120C">
  <title>{t}</title>
  <meta name="description" content="{d}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{canonico}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="Casa do Marceneiro Tatuapé">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{canonico}">
  <meta property="og:image" content="{url}capa-link.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{url}capa-link.jpg">
  <link rel="preload" as="image" href="{raiz}fotos/capa-1600.webp" imagesrcset="{raiz}fotos/capa-960.webp 960w, {raiz}fotos/capa-1600.webp 1600w, {raiz}fotos/capa-2400.webp 2400w" imagesizes="(orientation: portrait) and (min-width: 761px) 150vh, 100vw" fetchpriority="high">
  <link rel="icon" type="image/svg+xml" href="{raiz}marca/icone.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="{raiz}marca/favicon-32.png">
  <link rel="apple-touch-icon" href="{raiz}marca/apple-touch-icon.png">
  <script type="application/ld+json">{ficha(url)}</script>
{miolo}
</html>
"""

def separar(texto):
    titulo = re.search(r"<title>.*?</title>", texto, re.S | re.I).group(0)
    estilo = re.search(r"<style>.*?</style>", texto, re.S | re.I).group(0)
    resto = texto.replace(titulo, "").replace(estilo, "").strip()
    return estilo, resto

estilo, resto = separar(corpo)
(base / "index.html").write_text(pagina(f"{estilo}\n</head>\n<body>\n{resto}\n</body>",
    titulo="Casa do Marceneiro Tatuapé", descricao=RESUMO, url=PREVIA, canonico=PREVIA, raiz="",
    robots="noindex, nofollow", atributos=' data-modo="previa"'), encoding="utf-8")

for nome in ("artifact.html", "index.html"):
    print(f"{nome:<16} {(base / nome).stat().st_size / 1024:>7.0f} KB")
if not args.dominio:
    sys.exit(0)

# ---------------------------------------------------------------- domínio
url = args.dominio.rstrip("/") + "/"
if not urlparse(url).hostname:
    sys.exit(f"--dominio sem endereço: {args.dominio!r}")
raiz = urlparse(url).path or "/"
lanc = ler_json("lancamento.json", {})
destino = base / "publicar"

dom = re.sub(r"<!--PREVIA-->.*?<!--/PREVIA-->", "", corpo, flags=re.S)
dom = injetar(dom, "MEDICAO", medicao)
dom = injetar(dom, "TITULOS", {k: v[0] for k, v in TELAS.items()})
if lanc.get("cnpj"):
    dom = dom.replace("CNPJ " + CNPJ_EXEMPLO, "CNPJ " + lanc["cnpj"])
# links de tela viram caminhos; foto e marca, endereço a partir da raiz
dom = re.sub(r'href="#/([a-z-]*)"', lambda m: f'href="{raiz}{m.group(1) + "/" if m.group(1) else ""}"', dom)
dom = re.sub(r'(?<![\w/.-])(fotos/|marca/)', lambda m: raiz + m.group(1), dom)

# --- a conferência de lançamento (o aviso de prévia não conta: ele só
# fica quando há pendência, e sai sozinho quando tudo estiver resolvido)
def texto_visivel(t):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    return H.unescape(re.sub(r"<[^>]+>", " ", t))

pendencias = []
visivel = texto_visivel(re.sub(r"<!--AVISO-->.*?<!--/AVISO-->", "", dom, flags=re.S))
for marca_, motivo in ((CNPJ_EXEMPLO, "o CNPJ ainda é o de exemplo"),
                       ("ilustrativ", "ainda há texto de imagem ou projeto ilustrativo"),
                       ("prévia", "ainda há texto de prévia"), ("Prévia", "ainda há texto de prévia"),
                       ("protótipo", "ainda há texto de protótipo")):
    if marca_ in visivel:
        pendencias.append(f"{motivo} (“{marca_}” no texto)")
lugares = sorted({p.stem for p in (base / "fotos").glob("*.webp")
                  if not re.search(r"-(640|960|1600|2400)$", p.stem)
                  and (SIMULADOR or p.stem not in SO_DO_SIMULADOR)} | {"capa"})
sem_foto = [n for n in lugares if not reais.get(n)]
if sem_foto:
    pendencias.append(f"{len(sem_foto)} de {len(lugares)} lugares ainda com imagem 3D: {', '.join(sem_foto)}")
for chave, motivo in (("precos_confirmados", "preços das peças não confirmados com o Gabriel"),
                      ("horario_confirmado", "horário de atendimento não confirmado"),
                      ("promessas_confirmadas", "promessas comerciais não confirmadas (garantia de 3 anos, visita sem "
                                                "custo, prazo em contrato com desconto, preço travado, prazos de entrega)"),
                      ("projetos_reais", "a página de projetos ainda descreve projetos de exemplo"),
                      ("instagram_confirmado", "o @ do Instagram não foi confirmado"),
                      ("fundacao_1980_confirmada", "o ano de fundação, 1980, não foi confirmado")):
    if not lanc.get(chave):
        pendencias.append(motivo)

if pendencias and not args.forcar:
    print("\nNão publico no domínio ainda. Falta resolver:")
    for p in pendencias:
        print("  ·", p)
    print("\nCada item se resolve no lancamento.json, no corpo.html ou com as fotos reais (gerador/fotos/importar.py).")
    print("Para testar no domínio assim mesmo, fora do Google: --forcar")
    sys.exit(1)

robots = "noindex, nofollow" if pendencias else "index, follow"
if not pendencias:
    dom = re.sub(r"<!--AVISO-->.*?<!--/AVISO-->", "", dom, flags=re.S)
if destino.exists():
    shutil.rmtree(destino)
destino.mkdir()
# só o que a página usa: o kit 4K do logo fica no repositório, não no ar
shutil.copytree(base / "fotos", destino / "fotos", ignore=shutil.ignore_patterns("*.json"))
(destino / "marca").mkdir()
for arq in ("logo-site.svg", "icone.svg", "icone-512.png", "favicon-32.png", "apple-touch-icon.png"):
    shutil.copy2(base / "marca" / arq, destino / "marca" / arq)
shutil.copy2(base / "capa-link.jpg", destino / "capa-link.jpg")

estilo, resto = separar(dom)
codigo = re.search(r"<script>\n(.*?)</script>", resto, re.S)
assert codigo and resto.count("<script>") == 1, "esperava um único <script> no corpo"
(destino / "site.js").write_text(codigo.group(1), encoding="utf-8")
resto = resto.replace(codigo.group(0), f'<script src="{raiz}site.js"></script>')
(destino / "estilo.css").write_text(re.sub(r"^<style>\n?|</style>$", "", estilo.strip()), encoding="utf-8")
estilo = f'<link rel="stylesheet" href="{raiz}estilo.css">'
for tela, (titulo, descricao) in TELAS.items():
    miolo = resto
    if tela != "inicio":
        miolo = miolo.replace('<section class="rota on" data-rota="inicio"', '<section class="rota" data-rota="inicio"', 1)
        alvo = f'<section class="rota" data-rota="{tela}"'
        assert miolo.count(alvo) == 1, tela
        miolo = miolo.replace(alvo, f'<section class="rota on" data-rota="{tela}"', 1)
    caminho = "" if tela == "inicio" else tela + "/"
    saida = destino / caminho / "index.html"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(pagina(f"{estilo}\n</head>\n<body>\n{miolo}\n</body>", titulo=titulo, descricao=descricao,
        url=url, canonico=url + caminho, raiz=raiz, robots=robots,
        atributos=f' data-modo="dominio" data-raiz="{raiz}"'), encoding="utf-8")

# página perdida: a capa, fora do Google
(destino / "404.html").write_text((destino / "index.html").read_text(encoding="utf-8")
    .replace(f'content="{robots}"', 'content="noindex, nofollow"', 1), encoding="utf-8")

for antigo, novo in ANTIGOS.items():
    (destino / antigo).mkdir(exist_ok=True)
    (destino / antigo / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>Casa do Marceneiro Tatuapé</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{url}{novo}/">
<meta http-equiv="refresh" content="0; url={raiz}{novo}/"></head>
<body><p><a href="{raiz}{novo}/">Os projetos da Casa do Marceneiro estão aqui.</a></p></body></html>
""", encoding="utf-8")

hoje = datetime.date.today().isoformat()
(destino / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{url}{'' if t == 'inicio' else t + '/'}</loc><lastmod>{hoje}</lastmod></url>\n" for t in TELAS) +
    "</urlset>\n", encoding="utf-8")
(destino / "robots.txt").write_text(
    ("User-agent: *\nAllow: /\n" if not pendencias else "User-agent: *\nDisallow: /\n") +
    f"\nSitemap: {url}sitemap.xml\n", encoding="utf-8")
if raiz == "/" and not os.environ.get("VERCEL"):   # CNAME é coisa do GitHub Pages
    (destino / "CNAME").write_text(urlparse(url).hostname + "\n", encoding="utf-8")
(destino / ".nojekyll").write_text("", encoding="utf-8")

total = sum(f.stat().st_size for f in destino.rglob("*") if f.is_file())
print(f"publicar/        {total / 1024 / 1024:>7.1f} MB · {len(TELAS)} páginas para {url}")
if pendencias:
    print(f"montado com --forcar e FORA do Google (noindex): {len(pendencias)} pendências")
