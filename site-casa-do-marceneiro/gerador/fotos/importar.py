"""Põe as fotos reais da oficina no lugar das imagens 3D.

    python importar.py <pasta-com-as-fotos> [<pasta-fotos-do-site>]

Cada foto chega com o nome do lugar que ela ocupa no site — cozinha.jpg,
capa.jpg, oficina.heic convertido em jpg, e assim por diante (a lista
está em LUGARES, e o quadro do projeto mostra o lugar de cada uma). A
foto é virada pela orientação do celular, cortada no centro na proporção
do lugar (a capa em 16:9, o resto em 4:3), reduzida às larguras que o
site usa e gravada em WebP. Depois, `fotos/reais.json` passa a marcar o
lugar como foto real, e o montar.py tira o selo de 3D dali.

Foto de celular carrega a localização GPS de onde foi tirada — muitas
vezes a casa do cliente. Nada dos metadados (EXIF) é copiado.

Precisa do Pillow: pip install pillow
"""
import json, pathlib, sys
from PIL import Image, ImageOps

# lugar → (proporção largura/altura, larguras geradas). A primeira largura
# é a do arquivo principal; as outras ganham o sufixo -<largura>.
CAPA = (16 / 9, (2400, 1600, 960))
AMBIENTE = (4 / 3, (1280, 640))
PECA = (4 / 3, (1200, 640))
LUGARES = {
    "capa": CAPA,
    "cozinha": AMBIENTE, "closet": AMBIENTE, "escritorio": AMBIENTE, "painel": AMBIENTE,
    "compacta": AMBIENTE, "dormitorio": AMBIENTE, "banheiro": AMBIENTE, "oficina": AMBIENTE,
    "corte": PECA, "nicho": PECA, "prateleira": PECA, "tabua": PECA, "ripado": PECA,
    "aparador": PECA, "cabeceira": PECA, "sapateira": PECA, "luminaria": PECA, "bancada": PECA,
}
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}


def cortar(im, proporcao):
    """Corta no centro até a proporção pedida, sem esticar."""
    w, h = im.size
    if w / h > proporcao:
        novo = round(h * proporcao)
        x = (w - novo) // 2
        return im.crop((x, 0, x + novo, h))
    novo = round(w / proporcao)
    y = (h - novo) // 2
    return im.crop((0, y, w, y + novo))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    origem = pathlib.Path(sys.argv[1])
    destino = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parents[2] / "fotos"
    registro = destino / "reais.json"
    reais = json.loads(registro.read_text(encoding="utf-8")) if registro.exists() else {}

    fotos = [f for f in sorted(origem.iterdir()) if f.suffix.lower() in EXTENSOES]
    desconhecidas = [f.name for f in fotos if f.stem.lower() not in LUGARES]
    if desconhecidas:
        print("Sem lugar no site (renomeie para um destes: " + ", ".join(LUGARES) + "):")
        for nome in desconhecidas:
            print("  ·", nome)

    for arq in fotos:
        nome = arq.stem.lower()
        if nome not in LUGARES:
            continue
        proporcao, larguras = LUGARES[nome]
        with Image.open(arq) as bruto:
            im = cortar(ImageOps.exif_transpose(bruto).convert("RGB"), proporcao)
        if im.width < larguras[0]:
            print(f"  ! {arq.name}: {im.width} px de largura depois do corte, abaixo dos {larguras[0]} do site."
                  " Vai ampliada; se houver original maior, prefira.")
        for i, w in enumerate(larguras):
            h = round(w / proporcao)
            saida = destino / (f"{nome}-{w}.webp" if (nome == "capa" or i > 0) else f"{nome}.webp")
            im.resize((w, h), Image.LANCZOS).save(saida, "WEBP", quality=90 if nome == "capa" else 86, method=6)
        reais[nome] = True
        print(f"  ok {arq.name:<24} → {nome} ({im.width}×{im.height} depois do corte)")

    registro.write_text(json.dumps(dict(sorted(reais.items())), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    faltam = [n for n in LUGARES if not reais.get(n)]
    print(f"\n{len(LUGARES) - len(faltam)} de {len(LUGARES)} lugares com foto real."
          + (f" Faltam: {', '.join(faltam)}." if faltam else ""))
    print("Agora rode python3 montar.py na pasta do site.")


if __name__ == "__main__":
    main()
