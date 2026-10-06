"""Cenas de ambiente — os projetos sob medida, a capa e a oficina.

    python ambientes.py <cena> <saida.png> [amostras] [escala%]
"""
import sys, math, random
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *


def sala(L=3.4, P=3.0, A=2.7, cor=(0.70, 0.66, 0.60), piso="assoalho", esquerda=True, direita=True, teto=True):
    """Caixa de cômodo aberta para o lado da câmera (y negativo)."""
    rb = reboco("reboco-sala", cor)
    caixa("p-fundo", (L + 0.2, 0.1, A), (0, 0.05, A / 2), rb, chanfro=0)
    if esquerda:
        caixa("p-esq", (0.1, P + 2, A), (-L / 2 - 0.05, -P / 2 - 1, A / 2), rb, chanfro=0)
    if direita:
        caixa("p-dir", (0.1, P + 2, A), (L / 2 + 0.05, -P / 2 - 1, A / 2), rb, chanfro=0)
    if teto:
        # o teto para na boca do cômodo: o sol baixo entra por baixo dele
        caixa("teto", (L + 0.2, P, 0.1), (0, -P / 2, A + 0.05), liso("teto", (0.82, 0.80, 0.76), 0.9), chanfro=0)
    if piso == "assoalho":
        assoalho("piso", (-L / 2, L / 2, -P - 2, 0.0), "carvalho")
    elif piso == "porcelanato":
        caixa("piso", (L, P + 2, 0.04), (0, -P / 2 - 1, -0.02), liso("porc", (0.56, 0.54, 0.50), 0.32), chanfro=0)
    elif piso == "concreto":
        caixa("piso", (L, P + 2, 0.04), (0, -P / 2 - 1, -0.02), concreto("concreto"), chanfro=0)


def preto():
    return liso("preto-fosco", (0.025, 0.025, 0.025), 0.42, metal=0.8)


def vidro_preto():
    return liso("vidro-preto", (0.01, 0.01, 0.012), 0.06, especular=0.8)


# ------------------------------------------------------------------ cozinha
def cozinha():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.28, rot=-20)
    L, P, A = 3.4, 3.0, 2.7
    sala(L, P, A, (0.74, 0.71, 0.66), "porcelanato")
    corpo = liso("corpo", (0.74, 0.72, 0.68), 0.45)
    amad = madeira("frente-amad", "amadeirado", semente=101, anel=130, rugosidade=0.4, verniz=0.15, veio="Z")
    branco = liso("mdf-branco", (0.78, 0.77, 0.73), 0.34, verniz=0.1)
    met = preto()
    tampo = madeira("tampo-freijo", "freijo", semente=102, anel=110, verniz=0.35)
    d, hb, zp = 0.6, 0.72, 0.1
    # fundo: inferiores
    x = -L / 2 + d
    for k, w in enumerate((0.6, 0.8, 0.8)):
        modulo(f"inf{k}", x, 0, zp, w, d, hb, corpo, amad, met, n_portas=1 if w <= 0.6 else 2,
               gavetas=3 if k == 0 else 0)
        x += w
    # esquerda: torre quente perto do fundo + inferiores para a frente
    xt = -L / 2
    caixa("torre", (d, 0.62, A - 0.3), (xt + d / 2, -d - 0.31, (A - 0.3) / 2 + 0.0),
          madeira("torre-lat", "amadeirado", semente=107, anel=130, rugosidade=0.4, verniz=0.15, veio="Z"))
    for k, (z0, h, m) in enumerate(((0.1, 0.8, amad), (1.52, 0.38, amad), (1.92, 0.48, amad))):
        f = caixa(f"torre-f{k}", (0.018, 0.616, h - 0.006), (xt + d + 0.009, -d - 0.31, z0 + h / 2), m, chanfro=0.0012)
    caixa("forno", (0.02, 0.58, 0.58), (xt + d + 0.01, -d - 0.31, 0.92 + 0.29), vidro_preto(), chanfro=0.003)
    caixa("forno-pux", (0.02, 0.48, 0.014), (xt + d + 0.03, -d - 0.31, 1.46), liso("inox", (0.6, 0.6, 0.6), 0.25, metal=1), chanfro=0.004)
    caixa("micro-nicho", (0.02, 0.58, 0.02), (xt + d + 0.01, -d - 0.31, 1.505), corpo)
    yl = -d - 0.62
    for k in range(2):
        caixa(f"esq-inf{k}", (d, 0.6, hb), (xt + d / 2, yl - 0.3 - 0.6 * k, zp + hb / 2), corpo)
        caixa(f"esq-f{k}", (0.018, 0.594, hb - 0.006), (xt + d + 0.009, yl - 0.3 - 0.6 * k, zp + hb / 2), amad, chanfro=0.0012)
        caixa(f"esq-pux{k}", (0.012, 0.012, 0.2), (xt + d + 0.03, yl - 0.05 - 0.6 * k - 0.45, zp + hb - 0.12), met, chanfro=0.003)
    # direita: inferiores com o cooktop
    xd = L / 2 - d
    for k in range(3):
        caixa(f"dir-inf{k}", (d, 0.6, hb), (xd + d / 2, -d - 0.3 - 0.6 * k, zp + hb / 2), corpo)
        caixa(f"dir-f{k}", (0.018, 0.594, hb - 0.006), (xd - 0.009, -d - 0.3 - 0.6 * k, zp + hb / 2), amad, chanfro=0.0012)
        caixa(f"dir-pux{k}", (0.012, 0.012, 0.2), (xd - 0.03, -d - 0.55 - 0.6 * k, zp + hb - 0.12), met, chanfro=0.003)
    caixa("dir-canto", (d, d, hb), (xd + d / 2, -d / 2, zp + hb / 2), corpo)
    # rodapé recuado em preto: o móvel parece flutuar
    rod = liso("rodape", (0.03, 0.03, 0.03), 0.6)
    caixa("rod-f", (L - 2 * d, 0.5, zp), (0, -0.25, zp / 2), rod, chanfro=0)
    caixa("rod-e", (0.5, 1.2, zp), (xt + 0.25, yl - 0.6, zp / 2), rod, chanfro=0)
    caixa("rod-d", (0.5, 2.4, zp), (L / 2 - 0.25, -1.2, zp / 2), rod, chanfro=0)
    # o tampo maciço contínuo em U
    zt = zp + hb + 0.02
    caixa("tampo-f", (L - 2 * d + 0.02, d + 0.02, 0.04), (0, -d / 2 - 0.01, zt), tampo, chanfro=0.002)
    caixa("tampo-e", (d + 0.02, 1.2, 0.04), (xt + d / 2 + 0.01, yl - 0.6, zt), madeira("tampo-e", "freijo", semente=103, anel=110, verniz=0.35, veio="Y"), chanfro=0.002)
    caixa("tampo-d", (d + 0.02, 2.4, 0.04), (xd + d / 2 - 0.01, -1.2, zt), madeira("tampo-d", "freijo", semente=104, anel=110, verniz=0.35, veio="Y"), chanfro=0.002)
    caixa("cooktop", (0.5, 0.56, 0.006), (xd + d / 2, -1.5, zt + 0.022), vidro_preto(), chanfro=0.002)
    # cuba e torneira na bancada do fundo
    inox = liso("inox", (0.62, 0.62, 0.63), 0.28, metal=1)
    caixa("cuba", (0.62, 0.42, 0.004), (0.55, -0.32, zt + 0.021), liso("cuba-esc", (0.18, 0.18, 0.19), 0.3, metal=1), chanfro=0)
    barra("torn-1", (0.55, -0.06, zt + 0.02), (0.55, -0.06, zt + 0.36), 0.013, inox)
    barra("torn-2", (0.55, -0.06, zt + 0.36), (0.55, -0.24, zt + 0.36), 0.012, inox)
    barra("torn-3", (0.55, -0.24, zt + 0.36), (0.55, -0.24, zt + 0.29), 0.011, inox)
    # superiores e prateleira aberta
    zs, hs, ds = 1.52, 0.72, 0.36
    x = -L / 2 + d
    for k, w in enumerate((0.6, 0.8)):
        modulo(f"sup{k}", x, 0, zs, w, ds, hs, corpo, amad, met, n_portas=2 if w > 0.6 else 1)
        x += w
    for k, zz in enumerate((1.62, 2.0)):
        caixa(f"prat-ab{k}", (1.38, 0.26, 0.035), (1.0, -0.13, zz), madeira(f"prat-ab{k}", "freijo", semente=105 + k))
    livros("lk", (0.4, -0.12, 1.6375), 4, semente=9)
    vaso("vk", (1.05, -0.12, 1.6375), 0.2, 0.06, liso("cer-k", (0.72, 0.42, 0.26), 0.6))
    tigela("tk", (1.4, -0.12, 1.6375), 0.1, 0.06, liso("cer-k2", (0.86, 0.84, 0.79), 0.5))
    for i in range(4):
        vaso(f"pote{i}", (0.5 + i * 0.25, -0.12, 2.0175), 0.16 + 0.03 * (i % 2), 0.05, liso(f"pote{i}", (0.84, 0.82, 0.78) if i % 2 else (0.15, 0.13, 0.11), 0.4))
    caixa("frontao", (L + 0.2, 0.02, A - zs - hs), (0, -0.01, zs + hs + (A - zs - hs) / 2), liso("frontao", (0.74, 0.72, 0.68), 0.6), chanfro=0)
    # em cima da bancada
    t = placa_arredondada("tab-k", (0.4, 0.26, 0.026), 0.03, (-0.35, -0.04, zt + 0.15),
                          madeira("tab-k", "cumaru", semente=106, verniz=0.05), rot=(82, 0, 0))
    tigela("tig-k", (xd + 0.3, -0.85, zt + 0.02), 0.13, 0.07, liso("cer-k3", (0.16, 0.14, 0.12), 0.45))
    lim = liso("limao", (0.62, 0.48, 0.05), 0.4)
    for i, (dx, dy) in enumerate(((0.0, 0.0), (0.05, 0.03), (0.02, -0.05))):
        esfera(f"lk{i}", 0.034, (xd + 0.3 + dx, -0.85 + dy, zt + 0.09), lim, 0.88)
    pendente("pk", 0.2, -1.5, A, 0.95, luz=30)
    # luz: janela atrás da câmera, à esquerda, e rebatedor grande
    sol_com_janela((0, -0.5, 1.0), azimute=-30, elevacao=24, energia=5.0, distancia=3.0, abertura=(1.6, 1.6), folhas=(3, 2))
    luz_area("reb", (0.4, -3.4, 2.2), (0, -0.8, 1.0), (2.6, 1.4), 90, (1, 0.97, 0.92))
    camera((0.25, -3.55, 1.58), (-0.05, -0.7, 1.08), 20, abertura=8)


# ------------------------------------------------------------------- closet
def closet():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.25, rot=10)
    L, A = 3.2, 2.7
    sala(L, 3.0, A, (0.72, 0.69, 0.64), "assoalho")
    corpo = madeira("closet-carv", "carvalho", semente=111, anel=130, rugosidade=0.45, verniz=0.1, veio="Z")
    prat = madeira("closet-prat", "carvalho", semente=112, anel=130, rugosidade=0.45, verniz=0.1)
    met = preto()
    led = emissor("led", (1, 0.82, 0.58), 14)
    D = 0.58
    xs = [-L / 2, -0.75, 0.25, 0.9, L / 2]
    # laterais
    for i, x in enumerate(xs):
        caixa(f"lat{i}", (0.025, D, A - 0.1), (x + (0.0125 if i == 0 else -0.0125 if i == len(xs) - 1 else 0), -D / 2, (A - 0.1) / 2 + 0.05), corpo)
    caixa("teto-c", (L, D, 0.025), (0, -D / 2, A - 0.06), prat)
    caixa("base-c", (L, D, 0.08), (0, -D / 2, 0.04), prat)
    caixa("fundo-c", (L, 0.01, A), (0, -0.005, A / 2), madeira("fundo-c", "carvalho", semente=113, anel=140, veio="Z"))
    rnd = random.Random(5)
    cores_roupa = [(0.06, 0.08, 0.14), (0.62, 0.55, 0.44), (0.80, 0.78, 0.74), (0.22, 0.26, 0.18),
                   (0.05, 0.05, 0.05), (0.42, 0.20, 0.12), (0.55, 0.58, 0.62)]
    tecidos = [liso(f"tec{i}", c, 0.92, especular=0.25) for i, c in enumerate(cores_roupa)]

    def cabideiro(x0, x1, z, comprimento=(0.75, 1.05), n=None):
        barra(f"cab-{x0:.2f}-{z}", (x0 + 0.02, -D / 2, z), (x1 - 0.02, -D / 2, z), 0.012, met)
        n = n or int((x1 - x0) / 0.065)
        for k in range(n):
            xx = x0 + 0.06 + (x1 - x0 - 0.12) * k / max(1, n - 1)
            h = rnd.uniform(*comprimento)
            r = caixa(f"roupa-{x0:.2f}-{z}-{k}", (0.035, 0.46, h), (xx, -D / 2, z - 0.02 - h / 2), rnd.choice(tecidos),
                      chanfro=0.015, rot=(0, rnd.uniform(-3, 3), rnd.uniform(-8, 8)))
            r.modifiers["chanfro"].segments = 4

    # seção 1: cabideiro duplo
    cabideiro(xs[0], xs[1], 2.2, (0.65, 0.85))
    cabideiro(xs[0], xs[1], 1.15, (0.55, 0.75))
    caixa("p1-prat", (xs[1] - xs[0] - 0.04, D - 0.02, 0.025), ((xs[0] + xs[1]) / 2, -D / 2, 2.32), prat)
    caixa("p1-led", ((xs[1] - xs[0]) - 0.1, 0.01, 0.006), ((xs[0] + xs[1]) / 2, -D + 0.05, 2.304), led, chanfro=0)
    # seção 2: gaveteiro + prateleiras com roupa dobrada
    xc, wc = (xs[1] + xs[2]) / 2, xs[2] - xs[1] - 0.025
    for g in range(4):
        frente(f"gav{g}", (wc, 0.02, 0.2), (xc, -D + 0.01, 0.1 + 0.2 * g + 0.1),
               madeira(f"gav{g}", "carvalho", semente=114 + g, anel=130))
        caixa(f"gav-p{g}", (0.22, 0.012, 0.012), (xc, -D - 0.006, 0.1 + 0.2 * g + 0.16), met, chanfro=0.003)
    for k, z in enumerate((0.95, 1.35, 1.75, 2.15)):
        caixa(f"p2-prat{k}", (wc, D - 0.02, 0.025), (xc, -D / 2, z), prat)
        caixa(f"p2-led{k}", (wc - 0.06, 0.01, 0.006), (xc, -D + 0.05, z - 0.016), led, chanfro=0)
        x = xs[1] + 0.06
        while x < xs[2] - 0.3:
            alt = 0.0
            for j in range(rnd.randint(3, 6)):
                h = rnd.uniform(0.025, 0.045)
                caixa(f"dob{k}-{x:.2f}-{j}", (0.28, 0.32, h), (x + 0.14 + rnd.uniform(-0.006, 0.006), -D / 2 - 0.04,
                      z + 0.0125 + alt + h / 2), rnd.choice(tecidos), chanfro=0.008)
                alt += h
            x += 0.31
    # seção 3: sapateira inclinada
    xs3, ws3 = (xs[2] + xs[3]) / 2, xs[3] - xs[2] - 0.025
    couros = [liso(f"couro{i}", c, 0.45) for i, c in enumerate(((0.10, 0.05, 0.03), (0.30, 0.16, 0.08), (0.02, 0.02, 0.02), (0.62, 0.55, 0.44)))]
    for k in range(7):
        z = 0.2 + k * 0.28
        caixa(f"sap{k}", (ws3, D - 0.06, 0.02), (xs3, -D / 2 - 0.02, z), prat, rot=(-12, 0, 0))
        for j in range(2):
            caixa(f"sap{k}-{j}", (0.1, 0.27, 0.09), (xs3 - 0.14 + j * 0.28, -D / 2 - 0.03, z + 0.06), rnd.choice(couros),
                  chanfro=0.025, rot=(-12, 0, rnd.uniform(-5, 5)))
    # seção 4: cabideiro longo
    cabideiro(xs[3], xs[4], 2.2, (1.15, 1.45))
    caixa("p4-prat", (xs[4] - xs[3] - 0.04, D - 0.02, 0.025), ((xs[3] + xs[4]) / 2, -D / 2, 2.32), prat)
    # banco no meio do closet
    pufe = caixa("pufe", (0.9, 0.45, 0.42), (0.1, -1.6, 0.21), liso("pufe", (0.26, 0.13, 0.06), 0.5), chanfro=0.03)
    pufe.modifiers["chanfro"].segments = 5
    luz_area("teto-luz", (0, -1.3, A - 0.05), (0, -1.3, 0), (1.6, 0.8), 90, (1, 0.9, 0.78))
    luz_area("reb", (0.6, -3.8, 1.7), (0, -0.4, 1.3), (2.6, 1.6), 150, (1, 0.97, 0.92))
    sol_com_janela((0, -0.6, 1.2), azimute=-40, elevacao=22, energia=4.0, distancia=3.0, abertura=(1.2, 1.8), folhas=(2, 3))
    camera((0.45, -3.75, 1.38), (0.0, -0.4, 1.28), 21, abertura=8)


# --------------------------------------------------------------- home office
def escritorio():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.25, rot=30)
    L, A = 2.6, 2.7
    sala(L, 2.8, A, (0.46, 0.50, 0.46), "assoalho")
    fr = madeira("of-freijo", "freijo", semente=121, anel=110, verniz=0.25)
    fr_v = madeira("of-freijo-v", "freijo", semente=122, anel=110, verniz=0.25, veio="Z")
    branco = liso("mdf-branco", (0.80, 0.79, 0.75), 0.34, verniz=0.1)
    met = preto()
    D = 0.6
    for x in (-L / 2 + 0.0125, L / 2 - 0.0125):
        caixa(f"of-lat{x}", (0.025, D, 0.75), (x, -D / 2, 0.375), fr_v)
    caixa("of-tampo", (L, D, 0.035), (0, -D / 2, 0.765), fr)
    modulo("gaveteiro", 0.55, -0.02, 0.0, 0.5, 0.55, 0.7, branco, branco, met, gavetas=3)
    for k, z in enumerate((1.25, 1.62, 1.99)):
        caixa(f"of-prat{k}", (L - 0.6 if k == 0 else L, 0.28, 0.03), (-0.3 if k == 0 else 0, -0.14, z), madeira(f"of-prat{k}", "freijo", semente=123 + k))
    livros("lo1", (-1.25, -0.14, 1.265), 8, semente=21)
    livros("lo2", (0.3, -0.14, 1.635), 6, semente=22)
    vaso("vo1", (-0.3, -0.13, 1.635), 0.2, 0.06, liso("cer-o", (0.80, 0.76, 0.68), 0.5))
    ramo("ro1", (-0.3, -0.13, 1.82), 0.3, semente=4)
    livros("lo3", (-0.9, -0.14, 2.005), 3, deitados=True, semente=23)
    tigela("to", (0.75, -0.14, 2.005), 0.09, 0.06, liso("cer-o2", (0.16, 0.14, 0.12), 0.45))
    vaso("vo2", (1.0, -0.13, 1.265), 0.26, 0.06, liso("cer-o3", (0.12, 0.12, 0.12), 0.45))
    # monitor, teclado, luminária
    zt = 0.7825
    caixa("monitor", (0.62, 0.025, 0.37), (-0.35, -0.18, zt + 0.12 + 0.185), liso("monitor", (0.02, 0.02, 0.025), 0.1, especular=0.7), chanfro=0.004)
    caixa("monitor-pe", (0.04, 0.03, 0.12), (-0.35, -0.16, zt + 0.06), met)
    caixa("monitor-base", (0.22, 0.16, 0.008), (-0.35, -0.18, zt + 0.004), met, chanfro=0.002)
    caixa("teclado", (0.42, 0.13, 0.012), (-0.35, -0.42, zt + 0.006), liso("tecl", (0.78, 0.77, 0.74), 0.5), chanfro=0.003)
    barra("lum-1", (0.3, -0.12, zt), (0.3, -0.12, zt + 0.42), 0.006, met)
    barra("lum-2", (0.3, -0.12, zt + 0.42), (0.14, -0.3, zt + 0.48), 0.006, met)
    torno("lum-cup", [(0.012, 0.0), (0.05, -0.02), (0.055, -0.09), (0.05, -0.09), (0.045, -0.025), (0.0, -0.01)],
          (0.14, -0.3, zt + 0.5), met)
    luz_ponto("lum-p", (0.14, -0.3, zt + 0.42), 6, (1, 0.8, 0.55), 0.02)
    livros("lo4", (0.6, -0.35, zt), 2, deitados=True, semente=24)
    # cadeira de madeira
    cad = madeira("cadeira", "nogueira", semente=125, anel=90)
    caixa("cad-ass", (0.45, 0.44, 0.03), (-0.3, -0.95, 0.46), cad, chanfro=0.006)
    for dx in (-0.2, 0.2):
        for dy in (-0.19, 0.19):
            barra(f"cad-p{dx}{dy}", (-0.3 + dx, -0.95 + dy, 0.445), (-0.3 + dx * 1.08, -0.95 + dy * 1.08, 0), 0.014, cad)
    for dx in (-0.2, 0.2):
        barra(f"cad-e{dx}", (-0.3 + dx, -0.95 + 0.19, 0.47), (-0.3 + dx, -0.95 + 0.25, 0.85), 0.013, cad)
    caixa("cad-enc", (0.46, 0.03, 0.12), (-0.3, -0.95 + 0.245, 0.8), cad, chanfro=0.006, rot=(-8, 0, 0))
    sol_com_janela((0, -0.4, 1.0), azimute=-48, elevacao=22, energia=5.0, distancia=2.8, abertura=(1.2, 1.7), folhas=(2, 3))
    luz_area("reb", (0.9, -3.4, 1.7), (0, -0.4, 1.1), (2.2, 1.6), 130, (1, 0.97, 0.92))
    camera((0.55, -3.35, 1.42), (0.0, -0.45, 1.12), 26, abertura=8)


# ------------------------------------------------------------------- painel
def painel():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.22, rot=-40)
    L, A = 3.8, 2.7
    sala(L, 3.4, A, (0.70, 0.67, 0.62), "assoalho")
    fundo = liso("fundo-rip", (0.04, 0.03, 0.022), 0.6)
    caixa("rip-fundo", (2.6, 0.012, A), (0.1, -0.006, A / 2), fundo, chanfro=0)
    mats = [madeira(f"rp{i}", "freijo", veio="Z", semente=130 + i, anel=120) for i in range(7)]
    x, i = -1.17, 0
    while x < 1.37:
        caixa(f"rp{i}", (0.034, 0.022, A), (x, -0.023, A / 2), mats[i % 7], chanfro=0.002)
        x += 0.05; i += 1
    caixa("tv", (1.45, 0.03, 0.83), (0.1, -0.05, 1.42), liso("tela", (0.012, 0.012, 0.014), 0.08, especular=0.8), chanfro=0.004)
    nog = madeira("rack", "nogueira", semente=137, anel=90, verniz=0.3)
    caixa("rack", (2.2, 0.42, 0.34), (0.1, -0.25, 0.48), nog, chanfro=0.002)
    for k in range(4):
        frente(f"rack-f{k}", (0.55, 0.018, 0.34), (-0.725 + 0.55 * k, -0.469, 0.48), madeira(f"rack-f{k}", "nogueira", semente=138 + k, anel=90, verniz=0.3))
    caixa("rack-led", (2.1, 0.01, 0.006), (0.1, -0.35, 0.307), emissor("led-r", (1, 0.8, 0.55), 10), chanfro=0)
    livros("lp", (-0.75, -0.25, 0.65), 3, deitados=True, semente=31)
    vaso("vp", (0.95, -0.25, 0.65), 0.3, 0.075, liso("cer-p", (0.78, 0.74, 0.66), 0.55))
    ramo("rpm", (0.95, -0.25, 0.93), 0.5, semente=11)
    tigela("tp", (-0.35, -0.25, 0.65), 0.1, 0.05, liso("cer-p2", (0.16, 0.14, 0.12), 0.45))
    tap = caixa("tapete", (2.4, 1.6, 0.012), (0.1, -1.5, 0.006), liso("tapete", (0.34, 0.28, 0.22), 0.95), chanfro=0.004)
    sol_com_janela((0, -0.3, 1.0), azimute=-62, elevacao=20, energia=5.5, distancia=3.0, abertura=(1.4, 2.0), folhas=(2, 3))
    luz_area("reb", (2.2, -2.4, 1.8), (0, -0.3, 1.0), (2.2, 2.2), 120, (1, 0.97, 0.92))
    camera((1.35, -3.95, 1.38), (0.05, -0.3, 1.05), 26, abertura=8)


# ----------------------------------------------------------- cozinha compacta
def compacta():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.28, rot=10)
    L, A = 3.2, 2.6
    sala(L, 2.6, A, (0.78, 0.76, 0.72), "porcelanato")
    branco = liso("mdf-branco", (0.80, 0.79, 0.75), 0.32, verniz=0.12)
    amad = madeira("comp-amad", "carvalho", semente=141, anel=130, rugosidade=0.42, verniz=0.12, veio="Z")
    met = liso("latao", (0.62, 0.45, 0.20), 0.3, metal=1.0)
    d, zp, hb = 0.6, 0.1, 0.74
    x = -L / 2
    for k, w in enumerate((0.45, 0.6, 0.8, 0.6, 0.75)):
        modulo(f"ci{k}", x, 0, zp, w, d, hb, branco, branco, met, n_portas=1 if w < 0.7 else 2,
               gavetas=3 if k == 1 else 0)
        x += w
    caixa("ci-rod", (L, 0.5, zp), (0, -0.25, zp / 2), liso("rod", (0.04, 0.04, 0.04), 0.6), chanfro=0)
    zt = zp + hb + 0.015
    caixa("ci-tampo", (L, d + 0.02, 0.03), (0, -d / 2 - 0.01, zt), pedra("quartzo-c", (0.84, 0.83, 0.80)), chanfro=0.002)
    # superiores até o teto, em madeira, com nicho aberto
    zs = 1.5
    x = -L / 2
    for k, w in enumerate((0.45, 0.6, 0.8, 0.6, 0.75)):
        if k == 2:
            modulo(f"cs{k}", x, 0, zs, w, 0.35, A - zs, amad, amad, None, aberto=True)
            caixa("cs-nicho-prat", (w - 0.036, 0.33, 0.02), (x + w / 2, -0.175, zs + 0.45), amad)
            livros("lc", (x + 0.05, -0.17, zs + 0.018), 5, semente=41)
            vaso("vc", (x + 0.55, -0.16, zs + 0.46), 0.18, 0.05, liso("cer-c", (0.72, 0.42, 0.26), 0.6))
            caixa("cs-led", (w - 0.06, 0.01, 0.006), (x + w / 2, -0.32, zs - 0.004), emissor("led-c", (1, 0.8, 0.55), 10), chanfro=0)
        else:
            modulo(f"cs{k}", x, 0, zs, w, 0.35, A - zs, amad, amad, None, n_portas=1)
            caixa(f"cs-pux{k}", (0.012, 0.014, 0.14), (x + w - 0.045, -0.35 - 0.025, zs + 0.09), met, chanfro=0.003)
        x += w
    # mesa retrátil embutida no balcão, aberta
    tampo_m = madeira("mesa-c", "freijo", semente=142, anel=110, verniz=0.3)
    caixa("mesa", (1.1, 0.7, 0.03), (0.75, -0.95, 0.76), tampo_m, chanfro=0.002)
    barra("mesa-pe", (1.25, -1.22, 0.745), (1.25, -1.22, 0.0), 0.022, liso("preto", (0.03, 0.03, 0.03), 0.4, metal=0.8))
    banqueta_m = madeira("banq-c", "freijo", semente=143, anel=110)
    for k, xx in enumerate((0.45, 0.95)):
        placa_arredondada(f"bq{k}", (0.34, 0.34, 0.03), 0.16, (xx, -1.45, 0.455), banqueta_m, passos=12)
        for j in range(4):
            a = math.radians(45 + 90 * j)
            barra(f"bq{k}-{j}", (xx + 0.11 * math.cos(a), -1.45 + 0.11 * math.sin(a), 0.44),
                  (xx + 0.16 * math.cos(a), -1.45 + 0.16 * math.sin(a), 0), 0.014, banqueta_m)
    tigela("tc", (0.6, -0.9, 0.775), 0.12, 0.06, liso("cer-c2", (0.16, 0.14, 0.12), 0.45))
    caixa("cooktop", (0.55, 0.48, 0.006), (-0.85, -0.3, zt + 0.018), vidro_preto(), chanfro=0.002)
    t = placa_arredondada("tab-c", (0.36, 0.24, 0.024), 0.03, (0.3, -0.05, zt + 0.14),
                          madeira("tab-c", "cumaru", semente=144, verniz=0.05), rot=(82, 0, 0))
    sol_com_janela((0, -0.6, 1.0), azimute=-35, elevacao=22, energia=5.0, distancia=3.0, abertura=(1.4, 1.6), folhas=(2, 2))
    luz_area("reb", (0.8, -3.2, 2.0), (0, -0.6, 1.0), (2.4, 1.4), 150, (1, 0.97, 0.92))
    camera((0.95, -3.25, 1.5), (-0.05, -0.6, 1.1), 22, abertura=8)


# --------------------------------------------------------------- dormitório
def dormitorio():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.24, rot=-10)
    L, A = 3.8, 2.7
    sala(L, 3.6, A, (0.66, 0.61, 0.55), "assoalho")
    fr = madeira("dor-freijo", "freijo", semente=151, anel=110, verniz=0.25)
    fr_v = madeira("dor-freijo-v", "freijo", semente=152, anel=110, verniz=0.25, veio="Z")
    # painel de cabeceira com moldura de madeira e estofado
    caixa("cab-moldura", (2.6, 0.04, 1.2), (0.2, -0.02, 0.6 + 0.35), fr)
    est = liso("estofado", (0.44, 0.40, 0.34), 0.95)
    for k in range(4):
        p = caixa(f"cab-est{k}", (0.58, 0.06, 1.0), (-0.66 + 0.58 * k, -0.07, 0.95), est, chanfro=0.025)
        p.modifiers["chanfro"].segments = 5
    # cama
    caixa("cama-base", (1.7, 2.05, 0.28), (0.2, -1.1, 0.2), fr)
    lencol = liso("lencol", (0.84, 0.82, 0.78), 0.9)
    col = caixa("colchao", (1.62, 2.0, 0.26), (0.2, -1.1, 0.46), lencol, chanfro=0.05)
    col.modifiers["chanfro"].segments = 6
    manta = caixa("manta", (1.72, 0.85, 0.03), (0.2, -1.65, 0.6), liso("manta", (0.55, 0.36, 0.22), 0.95), chanfro=0.012)
    for k, dx in enumerate((-0.38, 0.38)):
        t = caixa(f"trav{k}", (0.68, 0.42, 0.16), (0.2 + dx, -0.34, 0.66), liso("fronha", (0.88, 0.86, 0.82), 0.9), chanfro=0.06)
        t.modifiers["chanfro"].segments = 6
    # criados-mudos suspensos
    for k, xc in enumerate((-1.0, 1.4)):
        caixa(f"cm{k}", (0.48, 0.38, 0.22), (xc, -0.23, 0.52), fr, chanfro=0.002)
        frente(f"cm-f{k}", (0.48, 0.018, 0.22), (xc, -0.429, 0.52), madeira(f"cm-f{k}", "freijo", semente=153 + k, anel=120))
        caixa(f"cm-led{k}", (0.42, 0.01, 0.006), (xc, -0.3, 0.407), emissor("led-d", (1, 0.8, 0.55), 10), chanfro=0)
    torno("abaj", [(0.0, 0.0), (0.06, 0.0), (0.065, 0.02), (0.05, 0.14), (0.02, 0.24), (0.0, 0.24)], (-1.0, -0.22, 0.63),
          liso("abaj-cer", (0.70, 0.60, 0.48), 0.5))
    torno("abaj-c", [(0.13, 0.0), (0.128, 0.004), (0.09, 0.17), (0.088, 0.17), (0.125, 0.004), (0.127, 0.0)],
          (-1.0, -0.22, 0.84), liso("linho", (0.86, 0.80, 0.70), 0.9))
    luz_ponto("abaj-l", (-1.0, -0.22, 0.92), 16, (1, 0.75, 0.48), 0.03)
    livros("ldo", (1.25, -0.22, 0.63), 2, deitados=True, semente=51)
    vaso("vdo", (1.52, -0.22, 0.63), 0.2, 0.06, liso("cer-d", (0.80, 0.76, 0.68), 0.5))
    ramo("rdo", (1.52, -0.22, 0.82), 0.32, semente=12)
    # guarda-roupa na parede esquerda
    xg = -L / 2
    corpo = liso("corpo-g", (0.74, 0.72, 0.68), 0.45)
    caixa("gr-corpo", (0.6, 1.6, A - 0.1), (xg + 0.3, -2.4, (A - 0.1) / 2), corpo)
    for k in range(3):
        caixa(f"gr-p{k}", (0.02, 0.528, A - 0.11), (xg + 0.61, -1.87 - 0.533 * k, (A - 0.1) / 2),
              madeira(f"gr-p{k}", "freijo", semente=155 + k, anel=120, veio="Z"), chanfro=0.0012)
        caixa(f"gr-pux{k}", (0.014, 0.014, 0.4), (xg + 0.64, -1.87 - 0.533 * k + (0.22 if k % 2 else -0.22), 1.1),
              liso("preto", (0.03, 0.03, 0.03), 0.4, metal=0.8), chanfro=0.004)
    sol_com_janela((0.2, -0.6, 0.8), azimute=-48, elevacao=21, energia=5.0, distancia=3.0, abertura=(1.4, 1.9), folhas=(2, 3))
    luz_area("reb", (2.0, -3.8, 1.8), (0, -1.0, 0.8), (2.4, 2.0), 140, (1, 0.97, 0.92))
    camera((1.6, -4.1, 1.45), (-0.05, -0.8, 0.85), 24, abertura=8)


# --------------------------------------------------------------------- capa
def capa():
    """A capa é a cozinha em U, em quadro panorâmico: é o pedido que mais
    chega na oficina, e o tampo maciço contínuo é a assinatura da casa."""
    cozinha()
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = 2400, 1350
    cam = s.camera
    cam.location = (0.55, -3.6, 1.42)
    mirar(cam, (-0.15, -0.75, 1.12))
    cam.data.lens = 19


# ------------------------------------------------------------------ oficina
def oficina():
    s = nova_cena(1600, 1200, exposicao=-0.85, look="AgX - High Contrast")
    mundo("interior.exr", 0.12, rot=120)
    L, A = 6.0, 3.6
    caixa("p-fundo", (L, 0.1, A), (0, 0.05, A / 2), concreto("parede-of", (0.36, 0.34, 0.31)), chanfro=0)
    caixa("p-esq", (0.1, 6, A), (-L / 2, -3, A / 2), concreto("parede-of2", (0.36, 0.34, 0.31)), chanfro=0)
    caixa("p-dir", (0.1, 7, A), (L / 2, -3, A / 2), concreto("parede-of3", (0.36, 0.34, 0.31)), chanfro=0)
    caixa("piso", (L, 7, 0.04), (0, -3, -0.02), concreto("piso-of", (0.30, 0.29, 0.27)), chanfro=0)
    # o teto para antes da câmera: o sol entra pela boca da oficina e cai na bancada
    caixa("teto", (L, 4.5, 0.1), (0, -2.25, A + 0.05), liso("teto-of", (0.5, 0.48, 0.45), 0.9), chanfro=0)
    rnd = random.Random(9)
    # estante de madeira bruta na parede do fundo
    met = liso("metal-of", (0.06, 0.06, 0.065), 0.5, metal=0.8)
    for x in (-2.6, -1.2, 0.2, 1.6):
        caixa(f"mao{x}", (0.05, 0.5, 0.05), (x, -0.25, 2.6), met, chanfro=0.003)
        caixa(f"mao{x}b", (0.05, 0.5, 0.05), (x, -0.25, 1.8), met, chanfro=0.003)
        caixa(f"mao{x}c", (0.05, 0.5, 0.05), (x, -0.25, 1.0), met, chanfro=0.003)
        caixa(f"mon{x}", (0.06, 0.06, 2.9), (x, -0.03, 1.45), met, chanfro=0.003)
    especies = ["freijo", "pinus", "cumaru", "carvalho", "nogueira"]
    mats = [madeira(f"est{i}", especies[i % 5], semente=180 + i, anel=90, rugosidade=0.6, verniz=0.0) for i in range(10)]
    for nivel in (1.025, 1.825, 2.625):
        z = nivel + 0.025
        for camada in range(rnd.randint(4, 6)):
            y = -0.05
            while y > -0.45:
                w = rnd.uniform(0.1, 0.22)
                caixa(f"est-{nivel}-{camada}-{y:.2f}", (4.6 + rnd.uniform(-0.3, 0.1), w - 0.004, 0.03),
                      (-0.5 + rnd.uniform(-0.15, 0.15), y - w / 2, z + 0.015), rnd.choice(mats), chanfro=0.0015)
                y -= w
            z += 0.031
    # chapas de MDF em pé, encostadas
    branco = liso("chapa-b", (0.80, 0.79, 0.75), 0.36)
    amad = madeira("chapa-a", "amadeirado", semente=190, anel=130, veio="Z")
    for i in range(6):
        caixa(f"chapa{i}", (0.018, 1.84, 2.6), (-L / 2 + 0.25 + i * 0.03, -2.6 + i * 0.07, 1.29), amad if i % 3 else branco,
              chanfro=0.001, rot=(0, -6, 0))
    # bancada central com morsa, sargentos e peça em andamento
    banc = madeira("banc-of", "pinus", semente=191, anel=70, rugosidade=0.6, verniz=0.0)
    caixa("banc-tampo", (2.4, 0.9, 0.08), (0.4, -2.0, 0.86), banc, chanfro=0.004)
    for dx in (-1.05, 1.05):
        for dy in (-0.35, 0.35):
            caixa(f"banc-pe{dx}{dy}", (0.09, 0.09, 0.82), (0.4 + dx, -2.0 + dy, 0.41), banc)
    caixa("banc-prat", (2.2, 0.8, 0.03), (0.4, -2.0, 0.22), banc)
    for i in range(3):
        caixa(f"banc-chapa{i}", (0.9, 0.5, 0.018), (0.0, -2.0, 0.245 + 0.018 * i), branco, chanfro=0.0008)
    # um gaveteiro em montagem, de frente aberta: a peça em andamento
    pfr = madeira("peca", "freijo", semente=192, anel=110, verniz=0.0, rugosidade=0.5)
    modulo("peca", 0.12, -1.85, 0.9, 0.86, 0.42, 0.5, pfr, pfr, None, aberto=True)
    caixa("peca-prat", (0.82, 0.4, 0.018), (0.55, -2.06, 1.15), pfr)
    for k in range(2):
        caixa(f"frente-solta{k}", (0.42, 0.2, 0.018), (-0.45 + k * 0.05, -2.1 - k * 0.02, 0.909 + 0.018 * k),
              madeira(f"fs{k}", "freijo", semente=193 + k, anel=110), chanfro=0.0012, rot=(0, 0, 4 - 6 * k))
    verm = liso("sargento", (0.62, 0.08, 0.04), 0.45)
    for k, x in enumerate((0.25, 0.85)):
        caixa(f"sg{k}a", (0.02, 0.02, 0.55), (x, -2.25, 1.1), met)
        caixa(f"sg{k}b", (0.04, 0.12, 0.03), (x, -2.2, 1.32), verm, chanfro=0.006)
        caixa(f"sg{k}c", (0.04, 0.12, 0.03), (x, -2.2, 0.88), verm, chanfro=0.006)
    # serra de mesa
    verde = liso("maquina", (0.10, 0.12, 0.13), 0.45)
    caixa("serra-corpo", (0.8, 0.7, 0.82), (2.15, -1.2, 0.41), verde, chanfro=0.01)
    caixa("serra-mesa", (1.0, 0.8, 0.03), (2.15, -1.2, 0.835), liso("mesa-aco", (0.42, 0.42, 0.43), 0.32, metal=1), chanfro=0.003)
    cilindro("serra-disco", 0.12, 0.003, (2.15, -1.2, 0.82), liso("disco", (0.55, 0.55, 0.57), 0.2, metal=1), rot=(0, 90, 0))
    caixa("serra-guia", (0.04, 0.8, 0.06), (2.37, -1.2, 0.88), liso("guia", (0.65, 0.45, 0.08), 0.4), chanfro=0.004)
    # luminárias industriais
    for k, x in enumerate((-0.6, 1.4)):
        pendente(f"of-pd{k}", x, -2.0, A, 1.4, raio=0.22, cor_cupula=(0.06, 0.07, 0.065), luz=90)
    sol_com_janela((0.2, -1.6, 1.0), azimute=-38, elevacao=32, energia=5.5, distancia=3.6, abertura=(2.0, 1.6), folhas=(4, 2))
    luz_area("reb", (1.0, -5.6, 2.2), (0, -1.5, 1.2), (3.0, 2.0), 160, (1, 0.95, 0.88))
    camera((1.25, -5.4, 1.5), (0.25, -1.7, 1.15), 26, abertura=8)

# ------------------------------------------------------------------ banheiro
def banheiro():
    s = nova_cena(1600, 1200, exposicao=-0.95, look="AgX - High Contrast")
    mundo("interior.exr", 0.25, rot=-20)
    L, A = 2.4, 2.6
    sala(L, 2.4, A, (0.72, 0.70, 0.66), "porcelanato")
    # parede de fundo em pedra clara até o teto
    caixa("rev", (L, 0.012, A), (0, -0.006, A / 2), pedra("rev-pedra", (0.80, 0.78, 0.74), (0.55, 0.53, 0.50), 0.3, 0.9), chanfro=0)
    fr = madeira("ban-freijo", "freijo", semente=201, anel=110, verniz=0.35)
    # gabinete suspenso com duas gavetas
    W, D, H, z0 = 1.2, 0.5, 0.42, 0.42
    caixa("gab", (W, D, H), (0, -D / 2 - 0.012, z0 + H / 2), fr, chanfro=0.002)
    for k in range(2):
        frente(f"gab-g{k}", (W / 2, 0.02, H), (-W / 4 + k * W / 2, -D - 0.012 - 0.01, z0 + H / 2),
               madeira(f"gab-g{k}", "freijo", semente=202 + k, anel=110, verniz=0.35))
    caixa("gab-tampo", (W + 0.02, D + 0.01, 0.02), (0, -D / 2 - 0.012, z0 + H + 0.01), pedra("tampo-b", (0.86, 0.85, 0.82)), chanfro=0.002)
    cuba = tigela("cuba", (0.0, -0.27, z0 + H + 0.02), 0.2, 0.13, liso("loucas", (0.90, 0.89, 0.86), 0.18, especular=0.6))
    inox = liso("metal-b", (0.06, 0.06, 0.06), 0.35, metal=0.9)
    barra("tb-1", (0.0, -0.04, 1.30), (0.0, -0.2, 1.30), 0.011, inox)
    cilindro("tb-2", 0.025, 0.06, (0.0, -0.03, 1.30), inox, rot=(90, 0, 0))
    # espelho com moldura de madeira e nicho ao lado
    caixa("esp-mold", (0.7, 0.03, 0.9), (0, -0.027, 1.78), fr, chanfro=0.004)
    caixa("espelho", (0.64, 0.01, 0.84), (0, -0.045, 1.78), liso("espelho", (0.92, 0.92, 0.92), 0.02, metal=1.0), chanfro=0)
    nb = caixa("nicho-b", (0.36, 0.12, 0.6), (0.72, -0.07, 1.6), fr, chanfro=0.002)
    # os dois vãos são cortados de verdade na peça: fundo e laterais em madeira, com sombra
    for k, (zc, h) in enumerate(((1.75, 0.25), (1.45, 0.23))):
        corte = caixa(f"nicho-vao{k}", (0.32, 0.12, h), (0.72, -0.11, zc), None, chanfro=0)
        corte.hide_render = True
        b = nb.modifiers.new(f"vao{k}", "BOOLEAN"); b.object = corte; b.operation = "DIFFERENCE"
        nb.modifiers.move(nb.modifiers.find(f"vao{k}"), 0)
    vaso("vb1", (0.68, -0.08, 1.615), 0.12, 0.04, liso("cer-b1", (0.80, 0.76, 0.68), 0.5))
    vaso("vb2", (0.78, -0.08, 1.615), 0.09, 0.035, liso("cer-b2", (0.16, 0.14, 0.12), 0.45))
    toalha = liso("toalha", (0.62, 0.55, 0.44), 0.95)
    for k in range(3):
        caixa(f"toalha{k}", (0.28, 0.2, 0.035), (0.72, -0.08, 1.335 + 0.036 * k), toalha, chanfro=0.012)
    vaso("vb3", (-0.45, -0.3, z0 + H + 0.02), 0.2, 0.05, liso("cer-b3", (0.72, 0.42, 0.26), 0.6))
    ramo("rb3", (-0.45, -0.3, z0 + H + 0.2), 0.3, semente=21)
    caixa("led-b", (W - 0.06, 0.01, 0.006), (0, -D + 0.02, z0 - 0.004), emissor("led-ban", (1, 0.8, 0.55), 10), chanfro=0)
    # parede atrás da câmera que só o espelho enxerga: sem ela o reflexo é o vazio
    pf = caixa("p-frente", (L + 0.2, 0.1, A), (0, -3.2, A / 2), reboco("reboco-frente", (0.72, 0.70, 0.66)), chanfro=0)
    pf.visible_camera = False; pf.visible_shadow = False; pf.visible_diffuse = False
    sol_com_janela((0, -0.3, 1.0), azimute=-42, elevacao=24, energia=4.6, distancia=2.6, abertura=(1.0, 1.4), folhas=(2, 2))
    luz_area("reb", (0.6, -2.9, 1.8), (0, -0.3, 1.0), (2.0, 1.4), 110, (1, 0.97, 0.92))
    camera((0.55, -2.65, 1.35), (0.05, -0.25, 1.08), 26, abertura=8)


CENAS = {f.__name__: f for f in (cozinha, closet, escritorio, painel, compacta, dormitorio, capa, oficina, banheiro)}

if __name__ == "__main__":
    nome, saida = sys.argv[1], sys.argv[2]
    amostras = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    escala = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    CENAS[nome]()
    sc = bpy.context.scene
    sc.cycles.samples = amostras
    sc.render.resolution_percentage = escala
    renderizar(saida)
