"""Converte os renders (PNG) nas imagens do site (WebP), em duas larguras.

    python otimizar.py <pasta-dos-png> <pasta-fotos-do-site>

Cada imagem sai com o nome da cena: `<nome>.webp` na largura do render e
`<nome>-640.webp` para cartão e celular. A capa ganha 2400, 1600 e 960.
"""
import sys, pathlib
from PIL import Image

origem, destino = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
destino.mkdir(parents=True, exist_ok=True)
total = 0
for png in sorted(origem.glob("*.png")):
    nome = png.stem
    im = Image.open(png).convert("RGB")
    larguras = {"capa": (2400, 1600, 960)}.get(nome, (im.width, 640))
    for w in larguras:
        h = round(im.height * w / im.width)
        saida = destino / (f"{nome}.webp" if w == im.width and nome != "capa" else f"{nome}-{w}.webp")
        # parede lisa de render comprime demais e mostra bloco: qualidade alta
        # custa pouco aqui, porque o denoiser já tirou o ruído
        q = 92 if nome == "capa" else (88 if w > 700 else 84)
        im.resize((w, h), Image.LANCZOS).save(saida, "WEBP", quality=q, method=6)
        total += saida.stat().st_size
        print(f"{saida.name:<26} {w}x{h}  {saida.stat().st_size / 1024:6.0f} KB")
print(f"total {total / 1024 / 1024:.2f} MB")
