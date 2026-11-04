#!/usr/bin/env python3
"""Põe as fotos reais das obras no site, a partir da curadoria em obras.json.

    python3 gerador/fotos/obras.py <pasta com os originais> [<outra pasta> ...]

Cada foto da curadoria é achada pelo hash do original (os 16 primeiros
caracteres do SHA-256), não pelo nome: o WhatsApp dá o mesmo nome a fotos
diferentes. Para cada uma:

    fotos/obras/<id>.webp       lado maior até 1600 px, para a galeria
    fotos/obras/<id>-640.webp   640 px de largura, para cartão e celular

Os "lugares" de obras.json (capa e as imagens fixas do site) saem cortados na
proporção do lugar em volta do foco, com o mesmo nome da imagem 3D que
substituem, e entram em fotos/reais.json — o selo de 3D sai sozinho.

Nada dos metadados do celular é copiado (o GPS da casa do cliente fica fora).
O vídeo sai sem áudio, em H.264, com a imagem de capa tirada do próprio vídeo.

Precisa do Pillow (pip install pillow) e do ffmpeg.
"""
import hashlib, json, pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps

SITE = pathlib.Path(__file__).resolve().parents[2]
FOTOS = SITE / "fotos"
OBRAS = FOTOS / "obras"
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}


def indexar(pastas):
    achados = {}
    for pasta in pastas:
        for arq in pathlib.Path(pasta).rglob("*"):
            if arq.is_file() and arq.suffix.lower() in EXTENSOES:
                achados.setdefault(hashlib.sha256(arq.read_bytes()).hexdigest()[:16], arq)
    return achados


def apagar_tela(im, cantos):
    """Escurece a tela de TV desligada que refletia quem fotografava: retoque de
    reflexo, o móvel fica como está."""
    w, h = im.size
    mascara = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mascara).polygon([tuple(p) for p in cantos], fill=255)
    mascara = mascara.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(1.2))
    tela = Image.new("RGB", (w, h))
    topo, base = min(y for _, y in cantos), max(y for _, y in cantos)
    for y in range(h):
        t = min(1, max(0, (y - topo) / max(1, base - topo)))
        tom = (round(34 - 18 * t), round(36 - 19 * t), round(41 - 21 * t))
        ImageDraw.Draw(tela).line([(0, y), (w, y)], fill=tom)
    return Image.composite(tela, im, mascara)


def cortar(im, proporcao, foco):
    """Corta na proporção pedida, com o foco o mais perto possível do centro."""
    w, h = im.size
    alvo = proporcao[0] / proporcao[1]
    if w / h > alvo:
        nw = round(h * alvo)
        x = min(max(0, round(foco[0] * w - nw / 2)), w - nw)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / alvo)
    y = min(max(0, round(foco[1] * h - nh / 2)), h - nh)
    return im.crop((0, y, w, y + nh))


def gravar(im, saida, largura, qualidade):
    if im.width > largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    im.save(saida, "WEBP", quality=qualidade, method=6)
    return im.size


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cur = json.loads((SITE / "obras.json").read_text(encoding="utf-8"))
    achados = indexar(sys.argv[1:])
    OBRAS.mkdir(parents=True, exist_ok=True)
    medidas, prontas, faltam = {}, {}, []

    for amb in cur["ambientes"]:
        for f in amb["fotos"]:
            arq = achados.get(f["fonte"])
            if not arq:
                faltam.append(f"{f['id']} ({f['fonte']})"); continue
            with Image.open(arq) as bruto:
                im = ImageOps.exif_transpose(bruto).convert("RGB")
            if f.get("retoque", {}).get("tela"):
                im = apagar_tela(im, f["retoque"]["tela"])
            prontas[f["id"]] = im
            lado = 1600 / max(im.size)
            grande = im if lado >= 1 else im.resize((round(im.width * lado), round(im.height * lado)), Image.LANCZOS)
            medidas[f["id"]] = list(gravar(grande, OBRAS / f"{f['id']}.webp", 1600, 84))
            gravar(im, OBRAS / f"{f['id']}-640.webp", 640, 80)
        v = amb.get("video")
        if v:
            arq = achados.get(v["fonte"])
            if not arq:
                faltam.append(f"{v['id']} ({v['fonte']})"); continue
            mp4 = OBRAS / f"{v['id']}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(arq), "-an", "-c:v", "libx264", "-preset", "slow",
                            "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-map_metadata", "-1", str(mp4)],
                           check=True)
            quadro = OBRAS / f"{v['id']}-capa.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(v.get("poster_seg", 1)), "-i", str(mp4),
                            "-frames:v", "1", str(quadro)], check=True)
            with Image.open(quadro) as q:
                medidas[v["id"]] = list(gravar(q.convert("RGB"), OBRAS / f"{v['id']}-capa.webp", 1600, 82))
            quadro.unlink()

    reais_arq = FOTOS / "reais.json"
    reais = json.loads(reais_arq.read_text(encoding="utf-8")) if reais_arq.exists() else {}
    for lugar, cfg in cur["lugares"].items():
        im = prontas.get(cfg["foto"])
        if im is None:
            faltam.append(f"lugar {lugar} ({cfg['foto']})"); continue
        recorte = cortar(im, cfg.get("proporcao", [4, 3]), cfg["foco"])
        if lugar == "capa":
            for w in (1600, 960):
                gravar(recorte, FOTOS / f"capa-{w}.webp", w, 88)
        else:
            gravar(recorte, FOTOS / f"{lugar}.webp", 1280, 86)
            gravar(recorte, FOTOS / f"{lugar}-640.webp", 640, 82)
        reais[lugar] = True
        print(f"  lugar {lugar:<11} ← {cfg['foto']} ({recorte.width}×{recorte.height})")

    (OBRAS / "medidas.json").write_text(json.dumps(medidas, indent=1) + "\n", encoding="utf-8")
    reais_arq.write_text(json.dumps(dict(sorted(reais.items())), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(p.stat().st_size for p in OBRAS.iterdir())
    print(f"{len(medidas)} mídias em fotos/obras/ ({total / 1024 / 1024:.1f} MB), {len(cur['lugares'])} lugares com foto real")
    if faltam:
        sys.exit("Faltou o original de: " + ", ".join(faltam))


if __name__ == "__main__":
    main()
