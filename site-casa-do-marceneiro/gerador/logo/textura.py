"""Textura de madeira clara do logo, gerada por fórmula.

No logo original, o telhado e as letras são de madeira clara de veio
vertical sobre fundo escuro. Aqui a madeira é desenhada como na árvore:
cada anel tem lenho inicial claro e largo, que escurece aos poucos até o
lenho tardio fino, e corta seco para o anel seguinte. Os anéis não são
iguais entre si (uns marcam, outros quase somem), o espaçamento varia, o
veio ondula devagar ao longo da fibra, e por cima vão a fibra fina e uma
variação larga de tom. Nada é baixado: tudo sai de numpy e Pillow, com
semente fixa, então a mesma chamada devolve a mesma textura.

Coordenadas em pixels do original (421 x 162), para a textura casar com o
desenho em qualquer resolução: `regiao` diz que pedaço do original cobrir.

Uso:  python textura.py saida.png [largura] [semente]
"""
import sys
import numpy as np
from PIL import Image

LARGURA_ORIGINAL, ALTURA_ORIGINAL = 421, 162

CLARO = np.array((247, 234, 213), np.float32)    # lenho inicial
TARDIO = np.array((214, 186, 148), np.float32)   # lenho tardio, no anel mais marcado
LARGURA_ANEL = 4.6                               # px do original, em média


def _ruido(h, w, cel_y, cel_x, rng, oitavas=3):
    """Ruído suave (soma de oitavas de valor interpolado), média 0 e desvio ~1."""
    total = np.zeros((h, w), np.float32)
    amp, soma = 1.0, 0.0
    for _ in range(oitavas):
        gy, gx = max(2, int(h / cel_y) + 4), max(2, int(w / cel_x) + 4)
        g = rng.standard_normal((gy, gx)).astype(np.float32)
        grande = Image.fromarray(g, mode="F").resize((int(gx * cel_x), int(gy * cel_y)), Image.BICUBIC)
        a = np.asarray(grande)
        oy, ox = int(cel_y * 1.5), int(cel_x * 1.5)
        total += amp * a[oy:oy + h, ox:ox + w]
        soma += amp * amp
        amp *= 0.5; cel_y /= 2; cel_x /= 2
    return total / np.sqrt(soma)


def _degrau(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def textura(largura=3840, semente=7, regiao=(0, 0, LARGURA_ORIGINAL, ALTURA_ORIGINAL)):
    x0, y0, x1, y1 = regiao
    escala = largura / (x1 - x0)                        # px de saída por px do original
    altura = round((y1 - y0) * escala)
    rng = np.random.default_rng(semente)

    # o veio ondula devagar ao longo da fibra e um pouco mais rápido de través
    s = escala
    desvio = (5.0 * _ruido(altura, largura, 150 * s, 40 * s, rng)
              + 1.6 * _ruido(altura, largura, 60 * s, 12 * s, rng))
    # largura do anel muda de faixa para faixa (anos bons e anos secos)
    # a fase é a soma da frequência local ao longo de x: dividir x pela largura
    # variável amassaria os anéis onde ela muda, em vez de alargá-los
    ritmo = np.clip(1.0 + 0.28 * _ruido(altura, largura, 400 * s, 30 * s, rng, oitavas=2), 0.66, 1.6)
    fase = (np.cumsum(1.0 / (LARGURA_ANEL * ritmo), axis=1) / escala
            + (x0 + desvio) / LARGURA_ANEL)
    g = fase - np.floor(fase)
    anel = np.floor(fase).astype(np.int64)

    # perfil do anel: clareia logo depois da divisa, escurece aos poucos, corta seco
    perfil = _degrau(0.40, 0.93, g) * (1 - _degrau(0.955, 1.0, g))
    # cada anel com sua força, que ainda some e volta ao longo da fibra
    forca_anel = rng.uniform(0.12, 1.0, 4096).astype(np.float32) ** 1.6
    forca = forca_anel[anel % 4096] * np.clip(0.75 + 0.35 * _ruido(altura, largura, 90 * s, 20 * s, rng, 2), 0.2, 1.2)
    tardio = perfil * forca

    # fibra fina, esticada ao longo do veio
    fibra = _ruido(altura, largura, 26 * s, 0.55 * s, rng, oitavas=2)
    # variação larga de tom
    tom = _ruido(altura, largura, 120 * s, 120 * s, rng, oitavas=2)

    cor = CLARO + (TARDIO - CLARO) * (0.62 * tardio)[..., None]
    cor *= (1 + 0.012 * fibra + 0.018 * tom)[..., None]
    return np.clip(cor, 0, 255).round().astype(np.uint8)


if __name__ == "__main__":
    a = sys.argv[1:]
    Image.fromarray(textura(int(a[1]) if len(a) > 1 else 3840, int(a[2]) if len(a) > 2 else 7)).save(a[0])
