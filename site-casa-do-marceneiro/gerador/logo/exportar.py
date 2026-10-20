"""Gera o kit do logo em ../../marca/.

  desenho.py (geometria) + textura.py (madeira)
    ├─ vetor:   logo-madeira.svg  logo-creme.svg  logo-escuro.svg  icone.svg
    ├─ PNG transparente:  logo-madeira-4k.png (3840 px)  logo-madeira-hd.png (1920 px)
    │                     logo-escuro-4k.png
    ├─ com o fundo do original:  logo-4k-fundo.png (3840 x 2160)  logo-hd-fundo.png (1920 x 1080)
    │                            perfil-1080.png (foto de perfil de WhatsApp e Instagram)
    ├─ ícones:  favicon-32.png  apple-touch-icon.png (180)  icone-512.png
    └─ site:    logo-site.svg (vetor com textura leve embutida)

Os PNG saem do Chromium (rasteriza.js), que dá o antisserrilhado das bordas;
a madeira é aplicada por baixo da máscara, em Pillow.

Uso:  python exportar.py      (numpy e Pillow; Node com Playwright para rasterizar)
"""
import base64, io, os, pathlib, subprocess, tempfile
import numpy as np
from PIL import Image

import desenho as d
from textura import textura

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI.parent.parent / "marca"

CREME = "#F3E2C8"      # a média da madeira do original, para quando não há textura
ESCURO = "#241A12"     # a tinta do site, para fundo claro
FUNDO_TOPO, FUNDO_BASE = (5, 5, 5), (67, 66, 64)   # o degradê do original, medido

MARGEM = 6.0           # px do original em volta do desenho, nos arquivos de logo
x0, y0, x1, y1 = d.CAIXA
VB = (x0 - MARGEM, y0 - MARGEM, x1 - x0 + 2 * MARGEM, y1 - y0 + 2 * MARGEM)
VB_JUSTO = (x0 - 1.0, y0 - 1.0, x1 - x0 + 2.0, y1 - y0 + 2.0)   # para o site: sem respiro


def _vb(vb):
    return " ".join(f"{v:.3f}".rstrip("0").rstrip(".") for v in vb)


def svg(conteudo, vb, largura=None, titulo="Casa do Marceneiro", defs=""):
    larg = largura or vb[2] * 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="{_vb(vb)}" width="{larg:.0f}" height="{larg * vb[3] / vb[2]:.0f}" role="img">'
            f'<title>{titulo}</title>{"<defs>" + defs + "</defs>" if defs else ""}{conteudo}</svg>')


def svg_madeira(vb, img_bytes, mime, largura=None):
    """Vetor com a madeira por baixo: a máscara é o desenho, a imagem é a textura."""
    uri = f"data:{mime};base64,{base64.b64encode(img_bytes).decode()}"
    mascara = (f'<mask id="forma" maskUnits="userSpaceOnUse" x="{vb[0]:.3f}" y="{vb[1]:.3f}" '
               f'width="{vb[2]:.3f}" height="{vb[3]:.3f}">{d.formas("#fff")}</mask>')
    img = (f'<image href="{uri}" xlink:href="{uri}" x="{vb[0]:.3f}" y="{vb[1]:.3f}" width="{vb[2]:.3f}" '
           f'height="{vb[3]:.3f}" preserveAspectRatio="none" mask="url(#forma)"/>')
    return svg(img, vb, largura, defs=mascara)


def rasteriza(conteudo_svg, largura):
    """SVG → RGBA no Chromium, com fundo transparente."""
    env = dict(os.environ)
    if "NODE_PATH" not in env:
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp:
        ent, sai = pathlib.Path(tmp, "e.svg"), pathlib.Path(tmp, "s.png")
        ent.write_text(conteudo_svg, encoding="utf-8")
        subprocess.run(["node", str(AQUI / "rasteriza.js"), str(ent), str(sai), str(largura)],
                       check=True, env=env, capture_output=True)
        return np.asarray(Image.open(sai).convert("RGBA"))


def alfa(vb, largura, conteudo=None):
    return rasteriza(svg(conteudo or d.formas("#fff"), vb), largura)[..., 3]


def com_madeira(tex, a):
    """Junta a textura (RGB) e a máscara (alfa), no tamanho da máscara."""
    h, w = a.shape
    t = tex if tex.shape[:2] == (h, w) else np.asarray(Image.fromarray(tex).resize((w, h), Image.LANCZOS))
    return np.dstack([t, a]).astype(np.uint8)


def cor_solida(hexcor, a):
    rgb = tuple(int(hexcor[i:i + 2], 16) for i in (1, 3, 5))
    out = np.zeros(a.shape + (4,), np.uint8)
    out[..., :3] = rgb; out[..., 3] = a
    return out


def degrade(w, h, semente=3):
    """O fundo do original: degradê vertical do quase preto ao grafite, com pontilhado
    de meio tom para não aparecer faixa na tela 4K."""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    base = np.array(FUNDO_TOPO, np.float32) + (np.array(FUNDO_BASE, np.float32) - FUNDO_TOPO) * t
    rng = np.random.default_rng(semente)
    ruido = rng.random((h, w, 1), dtype=np.float32) - rng.random((h, w, 1), dtype=np.float32)
    return np.clip(np.broadcast_to(base, (h, w, 3)) + ruido, 0, 255).round().astype(np.uint8)


def sobre(fundo, logo, x, y):
    out = Image.fromarray(fundo).convert("RGBA")
    out.alpha_composite(Image.fromarray(logo), (x, y))
    return np.asarray(out.convert("RGB"))


def salvar(arr, nome, **kw):
    caminho = SAIDA / nome
    Image.fromarray(arr).save(caminho, optimize=True, **kw)
    print(f"  {nome:<26} {arr.shape[1]:>5} x {arr.shape[0]:<5} {caminho.stat().st_size / 1024:>7.0f} KB")


def escreve(texto, nome):
    (SAIDA / nome).write_text(texto, encoding="utf-8")
    print(f"  {nome:<26} {'vetor':>13} {(SAIDA / nome).stat().st_size / 1024:>7.0f} KB")


def _vb_icone(frac):
    pts = np.array(d.telhado_pontos())
    tx0, ty0 = pts.min(0); tx1, ty1 = pts.max(0)
    lado = (tx1 - tx0) / frac                     # o telhado ocupa `frac` da largura
    cx, cy = (tx0 + tx1) / 2, (ty0 + ty1) / 2
    return (cx - lado / 2, cy - lado / 2, lado, lado)


def icone_svg(tamanho=512, frac=0.84):
    """Símbolo (telhado e janela) num quadrado de canto arredondado, no degradê do original."""
    vb = _vb_icone(frac)
    fundo = (f'<linearGradient id="f" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="#050505"/><stop offset="1" stop-color="#434240"/></linearGradient>')
    corpo = (f'<rect x="{vb[0]:.3f}" y="{vb[1]:.3f}" width="{vb[2]:.3f}" height="{vb[3]:.3f}" rx="{vb[2] * 0.2:.3f}" fill="url(#f)"/>'
             + d.icone_formas(CREME))
    return svg(corpo, vb, tamanho, defs=fundo)


def icone_png(lado, frac=0.84, arredondado=True):
    """Ícone em PNG: degradê do original e telhado de madeira; canto arredondado com
    antisserrilhado, ou quadrado e opaco (o iOS arredonda sozinho)."""
    vb = _vb_icone(frac)
    a = alfa(vb, lado, d.icone_formas("#fff"))
    tex = textura(lado, semente=7, regiao=(vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3]))[:lado, :lado]
    img = sobre(degrade(lado, lado), com_madeira(tex, a), 0, 0)
    if not arredondado:
        return img
    k = 4
    m = Image.new("L", (lado * k, lado * k), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).rounded_rectangle((0, 0, lado * k - 1, lado * k - 1), radius=round(lado * k * 0.2), fill=255)
    m = m.resize((lado, lado), Image.LANCZOS)
    return np.dstack([img, np.asarray(m)])


def main():
    SAIDA.mkdir(exist_ok=True)
    print("textura de madeira (4K)…")
    W4 = 3840
    tex4 = textura(W4, semente=7, regiao=(VB[0], VB[1], VB[0] + VB[2], VB[1] + VB[3]))
    h4 = round(W4 * VB[3] / VB[2])
    tex4 = tex4[:h4]

    print("vetores:")
    escreve(svg(d.formas(CREME), VB, 1600), "logo-creme.svg")
    escreve(svg(d.formas(ESCURO), VB, 1600), "logo-escuro.svg")
    buf = io.BytesIO(); Image.fromarray(tex4).resize((2560, round(2560 * VB[3] / VB[2])), Image.LANCZOS).save(buf, "JPEG", quality=90, optimize=True)
    escreve(svg_madeira(VB, buf.getvalue(), "image/jpeg", 1600), "logo-madeira.svg")

    # site: caixa justa, textura leve em WebP (o fio de CASA DO continua vetor)
    x, y, w, h = VB_JUSTO
    i0 = round((x - VB[0]) / VB[2] * W4); j0 = round((y - VB[1]) / VB[3] * h4)
    i1 = round((x + w - VB[0]) / VB[2] * W4); j1 = round((y + h - VB[1]) / VB[3] * h4)
    recorte = Image.fromarray(tex4[j0:j1, i0:i1]).resize((960, round(960 * h / w)), Image.LANCZOS)
    buf = io.BytesIO(); recorte.save(buf, "WEBP", quality=80, method=6)
    escreve(svg_madeira(VB_JUSTO, buf.getvalue(), "image/webp", 360), "logo-site.svg")

    print("PNG transparente:")
    a4 = alfa(VB, W4)
    salvar(com_madeira(tex4, a4), "logo-madeira-4k.png")
    salvar(com_madeira(tex4, alfa(VB, 1920)), "logo-madeira-hd.png")
    salvar(cor_solida(ESCURO, alfa(VB, W4, d.formas("#fff"))), "logo-escuro-4k.png")

    print("com o fundo do original:")
    for nome, (W, H), frac in (("logo-4k-fundo.png", (3840, 2160), 0.70), ("logo-hd-fundo.png", (1920, 1080), 0.70),
                               ("perfil-1080.png", (1080, 1080), 0.80)):
        lw = round(W * frac)
        a = alfa(VB, lw)
        logo = com_madeira(tex4, a)
        lh = a.shape[0]
        salvar(sobre(degrade(W, H), logo, (W - lw) // 2, (H - lh) // 2), nome)

    print("ícones:")
    escreve(icone_svg(512), "icone.svg")
    salvar(icone_png(512), "icone-512.png")
    salvar(icone_png(180, arredondado=False), "apple-touch-icon.png")
    salvar(icone_png(32, frac=0.92), "favicon-32.png")

if __name__ == "__main__":
    os.chdir(AQUI)
    main()
