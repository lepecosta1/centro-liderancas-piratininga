#!/usr/bin/env python3
"""Imagens para os recursos de imagem do anúncio de pesquisa do Google.

    python3 gerador/criativos/imagens_google.py anuncios/google-imagens

Só foto real de obra, sem texto por cima (o Google recusa imagem com texto
sobreposto ou logo colado): paisagem 1200×628 (1,91:1) e quadrada 1200×1200,
cortadas em volta do foco. E o logotipo quadrado, 1200×1200, o mesmo do perfil. Precisa do Pillow.
"""
import pathlib, sys
from PIL import Image

SITE = pathlib.Path(__file__).resolve().parents[2]
OBRAS = SITE / "fotos" / "obras"
FOTOS = [   # foto, foco horizontal, foco vertical
    ("sala-jantar-nogueira", .5, .5), ("cozinha-preta-bancada-pedra", .5, .5),
    ("dormitorio-estante-suspensa", .5, .5), ("cama-gavetoes-quarto-rosa", .5, .55),
    ("sala-painel-led", .5, .45), ("comercial-salao-mesa-ilha", .5, .55),
]


def cortar(im, alvo, fx, fy):
    w, h = im.size
    if w / h > alvo:
        nw = round(h * alvo); x = min(max(0, round(fx * w - nw / 2)), w - nw)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / alvo); y = min(max(0, round(fy * h - nh / 2)), h - nh)
    return im.crop((0, y, w, y + nh))


def main(saida):
    saida = pathlib.Path(saida); saida.mkdir(parents=True, exist_ok=True)
    for nome, fx, fy in FOTOS:
        with Image.open(OBRAS / f"{nome}.webp") as im:
            im = im.convert("RGB")
            cortar(im, 1200 / 628, fx, fy).resize((1200, 628), Image.LANCZOS).save(saida / f"{nome}-paisagem.jpg", quality=88)
            q = cortar(im, 1, fx, fy)
            q.resize((1200, 1200) if q.width >= 1000 else (q.width, q.width), Image.LANCZOS).save(saida / f"{nome}-quadrada.jpg", quality=88)
    with Image.open(SITE / "marca" / "perfil-1080.png") as lg:   # o mesmo do perfil do Google e do Instagram
        lg.convert("RGB").resize((1200, 1200), Image.LANCZOS).save(saida / "logo-quadrado.png")
    print(f"{len(FOTOS) * 2 + 1} imagens em {saida}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else SITE / "anuncios" / "google-imagens")
