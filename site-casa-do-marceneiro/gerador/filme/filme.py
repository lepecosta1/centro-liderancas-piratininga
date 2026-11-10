#!/usr/bin/env python3
"""Monta o filme institucional do site a partir de roteiro.json.

    NODE_PATH=$(npm root -g) node gerador/filme/quadros.js <pasta dos quadros>
    python3 gerador/filme/filme.py <pasta dos quadros> [--narracao <pasta>]

Só entram fotos reais das obras (fotos/obras/). Cada foto ganha um movimento
lento de câmera; as legendas, a marca e o cartão final vêm prontos do
quadros.js, na tipografia do site. Sai em fotos/filme/:

    casa-do-marceneiro.mp4   720 × 1280, H.264, sem metadados
    filme-capa.webp          a imagem que aparece antes do play

Narração: uma gravação por batida do roteiro (1.wav, 2.wav … ou .mp3, .m4a,
.ogg) na pasta de --narracao. Com ela, cada batida dura o que a fala dura,
e o som entra junto. Sem ela, o filme sai mudo, no tempo de leitura das
legendas — que contam a mesma história.

Precisa de numpy, opencv-python-headless, Pillow e do ffmpeg.
"""
import argparse, json, pathlib, subprocess, sys
import cv2
import numpy as np
from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
SITE = AQUI.parents[1]
OBRAS = SITE / "fotos" / "obras"
SAIDA = SITE / "fotos" / "filme"
NOGUEIRA = np.array([12, 18, 26], np.float32)          # #1A120C em BGR


def abrir(foto):
    im = Image.open(OBRAS / f"{foto}.webp").convert("RGB")
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)


def recorte(img, cx, cy, zoom, W, H):
    """A janela 9:16 dentro da foto, com (cx, cy) no centro e o zoom pedido."""
    h, w = img.shape[:2]
    jw, jh = (h * W / H, h) if w / h > W / H else (w, w * H / W)
    jw, jh = jw / zoom, jh / zoom
    x = min(max(cx * w - jw / 2, 0), w - jw)
    y = min(max(cy * h - jh / 2, 0), h - jh)
    M = np.float32([[W / jw, 0, -x * W / jw], [0, H / jh, -y * H / jh]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)


def suave(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


def camada(arq):
    """PNG transparente → (cor pré-multiplicada, alfa), prontos para somar."""
    rgba = np.asarray(Image.open(arq).convert("RGBA")).astype(np.float32)
    a = rgba[..., 3:4] / 255
    return cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2BGR) * a, a


def por(quadro, cam, forca):
    if forca <= 0:
        return quadro
    cor, a = cam
    return quadro * (1 - a * forca) + cor * forca


def duracao(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("quadros")
    ap.add_argument("--narracao")
    ap.add_argument("--saida", default=str(SAIDA))
    args = ap.parse_args()
    rot = json.loads((AQUI / "roteiro.json").read_text(encoding="utf-8"))
    W, H, FPS, XF = rot["largura"], rot["altura"], rot["fps"], rot["fusao"]
    quadros = pathlib.Path(args.quadros)
    saida = pathlib.Path(args.saida); saida.mkdir(parents=True, exist_ok=True)

    # as falas, se houver: cada batida dura o que a fala dura, com um respiro
    falas = []
    if args.narracao:
        pasta = pathlib.Path(args.narracao)
        for i in range(len(rot["batidas"])):
            achou = [p for e in ("wav", "mp3", "m4a", "ogg") for p in [pasta / f"{i + 1}.{e}"] if p.exists()]
            if not achou:
                sys.exit(f"falta a gravação da batida {i + 1} em {pasta}")
            falas.append(achou[0])
    ENTRA, RESPIRO = 0.45, 0.75
    t, linha, legendas, sons = 0.0, [], [], []
    for i, bat in enumerate(rot["batidas"]):
        dur = bat["dur"]
        if falas:
            dur = max(duracao(falas[i]) + ENTRA + RESPIRO, 3.2 if not bat.get("final") else 5.0)
            sons.append((falas[i], t + ENTRA))
        for li, leg in enumerate(bat.get("legendas", [])):
            legendas.append((camada(quadros / f"legenda-{i}-{li}.png"), t + leg["de"] * dur, t + leg["ate"] * dur))
        cenas = bat.get("cenas") or [{"foto": bat["final"]["fundo"], "de": [0.5, 0.5, 1.0], "para": [0.5, 0.46, 1.1],
                                      "peso": 1, "final": True}]
        soma = sum(c["peso"] for c in cenas)
        for c in cenas:
            d = dur * c["peso"] / soma
            linha.append({**c, "ini": t, "fim": t + d, "img": abrir(c["foto"])})
            t += d
    total = t
    for c in linha:
        if c.get("final"):                              # o cartão final: a foto da capa, desfocada e escura
            c["img"] = cv2.GaussianBlur(c["img"], (0, 0), 16)
            c["escuro"] = 0.74
    marca, final = camada(quadros / "marca.png"), camada(quadros / "final.png")
    ini_final = next(c["ini"] for c in linha if c.get("final"))

    # o escuro de cima (para a marca) e o de baixo (para a legenda), na cor da nogueira
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    sombra = np.clip((0.2 - y) / 0.2, 0, 1) ** 1.4 * 0.62 + np.clip((y - 0.47) / 0.53, 0, 1) ** 1.25 * 0.86

    def cena(c, tt):
        p = suave((tt - (c["ini"] - XF)) / (c["fim"] - c["ini"] + 2 * XF)) if not c.get("final") else \
            (tt - c["ini"] + XF) / (c["fim"] - c["ini"] + XF)
        a, b = c["de"], c["para"]
        q = recorte(c["img"], *(a[k] + (b[k] - a[k]) * p for k in range(3)), W, H)
        e = c.get("escuro")
        return q * (1 - e) + NOGUEIRA * e if e else q

    comando = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    for arq, _ in sons:
        comando += ["-i", str(arq)]
    if sons:
        filtro = ";".join(f"[{k + 1}:a]aresample=48000,adelay={round(quando * 1000)}:all=1[a{k}]" for k, (_, quando) in enumerate(sons))
        filtro += ";" + "".join(f"[a{k}]" for k in range(len(sons))) + f"amix=inputs={len(sons)}:normalize=0,alimiter=limit=0.95[som]"
        comando += ["-filter_complex", filtro, "-map", "0:v", "-map", "[som]", "-c:a", "aac", "-b:a", "128k"]
    mp4 = saida / "casa-do-marceneiro.mp4"
    comando += ["-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-map_metadata", "-1", "-t", f"{total:.3f}", str(mp4)]
    ff = subprocess.Popen(comando, stdin=subprocess.PIPE)
    t_capa = linha[1]["ini"] + (linha[1]["fim"] - linha[1]["ini"]) * 0.6      # a capa: a segunda cena, com a primeira legenda
    n = round(total * FPS)
    for f in range(n):
        tt = f / FPS
        i = max(k for k, c in enumerate(linha) if c["ini"] <= tt)
        q = cena(linha[i], tt)
        if i + 1 < len(linha) and tt > linha[i]["fim"] - XF:          # fusão com a cena seguinte
            m = suave((tt - (linha[i]["fim"] - XF)) / XF)
            q = q * (1 - m) + cena(linha[i + 1], tt) * m
        s = sombra * (1 - suave((tt - ini_final + XF) / XF) * 0.0)
        q = q * (1 - s) + NOGUEIRA * s
        q = por(q, marca, suave(tt / 0.6) * (1 - suave((tt - ini_final + XF) / XF)))
        for cam, de, ate in legendas:
            q = por(q, cam, min(suave((tt - de - 0.12) / 0.38), suave((ate - 0.05 - tt) / 0.32)))
        q = por(q, final, suave((tt - ini_final - 0.25) / 0.7))
        q = q * min(1.0, suave(tt / 0.5), suave((total - tt) / 0.45) + 0.0)          # abre e fecha no escuro
        quadro = np.clip(q, 0, 255).astype(np.uint8)
        ff.stdin.write(quadro.tobytes())
        if f == round(t_capa * FPS):
            Image.fromarray(cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)).save(saida / "filme-capa.webp", "WEBP", quality=82, method=6)
    ff.stdin.close()
    if ff.wait():
        sys.exit("o ffmpeg falhou")
    (saida / "filme.json").write_text(json.dumps({"segundos": round(total, 1), "largura": W, "altura": H,
                                                   "narrado": bool(sons)}, indent=1) + "\n", encoding="utf-8")
    print(f"{mp4.name}: {total:.1f} s, {mp4.stat().st_size / 1024 / 1024:.1f} MB, {'com narração' if sons else 'mudo, com legendas'}")


if __name__ == "__main__":
    main()
