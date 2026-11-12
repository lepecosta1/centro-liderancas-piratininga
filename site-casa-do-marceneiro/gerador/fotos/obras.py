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

"retoque" em obras.json cuida da privacidade sem mexer em móvel: "tela" escurece
uma TV que refletia gente, "borrar" desfaz um reflexo pequeno e "recorte" tira
da foto a faixa onde aparecia uma pessoa ou material de obra.

Nada dos metadados do celular é copiado (o GPS da casa do cliente fica fora).
O vídeo sai sem áudio, em H.264, com a imagem de capa tirada do próprio vídeo.

Foto que chega pequena (lado maior abaixo de 900 px) é ampliada até 1100 px
pelo mesmo melhorar da capa.

A capa é uma foto em pé, inteira, sem corte ("proporcao": null). Ela sai em
capa-720 e capa-1350, ampliada de um jeito que não pixela nem inventa detalhe
(ver melhorar), e com capa-fundo: a própria foto desfocada e com névoa, onde a
foto se desfaz no site.

Precisa do Pillow (pip install pillow), do ffmpeg e, para a capa, do OpenCV
(pip install opencv-python-headless).
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


def borrar(im, caixas):
    """Desfaz um reflexo pequeno (gente no espelho do fim do corredor): a área
    vira um borrão, com a borda esfumada. O móvel não muda."""
    w, h = im.size
    mascara = Image.new("L", (w, h), 0)
    for x0, y0, x1, y1 in caixas:
        ImageDraw.Draw(mascara).rectangle([round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)], fill=255)
    raio = max(6, round(min(w, h) * 0.022))
    return Image.composite(im.filter(ImageFilter.GaussianBlur(raio)), im, mascara.filter(ImageFilter.GaussianBlur(raio / 3)))


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


def melhorar(im, largura):
    """Amplia a foto do WhatsApp para a capa sem pixelar.

    Nada de inteligência artificial que redesenha a imagem: o móvel tem de ser
    o que o Gabriel fez. Quatro passos clássicos:
      1. tira os blocos da compressão só onde a foto é lisa (forro, parede,
         vidro) — onde tem textura, como o veio da madeira, ela fica como veio;
      2. amplia em Lanczos;
      3. devolve a nitidez que a ampliação tira, menos no liso;
      4. põe um grão fino, para o degradê do forro não virar faixas.
    """
    import cv2
    import numpy as np
    bgr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    f = bgr.astype(np.float32)
    limpa = cv2.fastNlMeansDenoisingColored(bgr, None, 4, 4, 7, 21).astype(np.float32)
    cinza = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    media = cv2.blur(cinza, (7, 7))
    desvio = np.sqrt(np.maximum(cv2.blur(cinza * cinza, (7, 7)) - media * media, 0))
    liso = cv2.GaussianBlur(np.clip((7.0 - desvio) / 5.0, 0, 1), (0, 0), 1.5)
    f = limpa * liso[..., None] + f * (1 - liso[..., None])
    tamanho = (largura, round(im.height * largura / im.width))
    up = cv2.resize(f, tamanho, interpolation=cv2.INTER_LANCZOS4)
    liso = cv2.resize(liso, tamanho)[..., None]
    up = up + (up - cv2.GaussianBlur(up, (0, 0), 1.2)) * (0.9 - 0.6 * liso)
    grao = cv2.GaussianBlur(np.random.default_rng(7).normal(0, 1, up.shape[:2]).astype(np.float32), (0, 0), 0.6)
    up = up + grao[..., None] * 2.0
    return Image.fromarray(cv2.cvtColor(np.clip(up, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))


def fumaca(im, foco, tamanho=(640, 360)):
    """O fundo da capa: a própria foto, desfocada, escurecida e com névoa. A
    foto nítida se desfaz nele, em vez de terminar numa borda."""
    import numpy as np
    w, h = tamanho
    base = cortar(im, tamanho, foco).resize((w // 8, h // 8), Image.LANCZOS)
    base = base.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14))
    arr = np.asarray(base).astype(np.float32) / 255 * 0.58
    rng = np.random.default_rng(3)
    nevoa = np.zeros((h, w), np.float32)
    for celulas, peso in ((3, .5), (6, .26), (12, .15), (24, .09)):
        grade = Image.fromarray((rng.random((max(2, round(celulas * h / w)), celulas)) * 255).astype(np.uint8))
        nevoa += np.asarray(grade.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(4)), np.float32) / 255 * peso
    nevoa = np.clip((nevoa - 0.42) / 0.38, 0, 1)
    nevoa = nevoa * nevoa * (3 - 2 * nevoa)
    tom = np.array([0.93, 0.80, 0.64], np.float32)
    arr = 1 - (1 - arr) * (1 - (tom * 0.2 * nevoa[..., None]))
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


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
            ret = f.get("retoque", {})
            if ret.get("tela"):
                im = apagar_tela(im, ret["tela"])
            if ret.get("borrar"):
                im = borrar(im, ret["borrar"])
            if ret.get("recorte"):                     # tira da foto a parte onde aparecia gente ou material de obra
                x0, y0, x1, y1 = ret["recorte"]
                im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
            if max(im.size) < 900:                     # foto pequena do WhatsApp: amplia como a capa, sem inventar detalhe
                im = melhorar(im, round(im.width * 1100 / max(im.size)))
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
        proporcao = cfg.get("proporcao", [4, 3])
        recorte = im if proporcao is None else cortar(im, proporcao, cfg["foco"])
        if lugar == "capa":
            assert recorte.height > recorte.width, "a capa do site é uma foto em pé"
            grande = melhorar(recorte, 1350) if recorte.width < 1350 else recorte
            gravar(grande, FOTOS / "capa-1350.webp", 1350, 84)
            gravar(grande, FOTOS / "capa-720.webp", 720, 84)
            fundo = fumaca(recorte, cfg["foco"])
            fundo.save(FOTOS / "capa-fundo.webp", "WEBP", quality=72, method=6)
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
