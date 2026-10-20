"""Cenas das peças da loja — uma por produto do catálogo.

    python produtos.py <cena> <saida.png> [amostras] [escala%]
"""
import sys, math
sys.path.insert(0, __import__("os").path.dirname(__file__))
from lib import *


def parede_e_piso(cor=(0.60, 0.53, 0.45), piso="assoalho", largura=5.0, altura=3.0, fundo=3.5, z=0.0):
    caixa("parede", (largura, 0.06, altura), (0, 0.03, z + altura / 2), reboco("reboco", cor), chanfro=0)
    if piso == "assoalho":
        assoalho("piso", (-largura / 2, largura / 2, -fundo, 0.0), "carvalho", z=z)
    elif piso == "concreto":
        caixa("piso", (largura, fundo, 0.04), (0, -fundo / 2, z - 0.02), concreto("concreto"), chanfro=0)
    elif piso:
        caixa("piso", (largura, fundo, 0.04), (0, -fundo / 2, z - 0.02), piso, chanfro=0)


def nicho():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.22, rot=40)
    parede_e_piso((0.58, 0.50, 0.42), piso=None)
    fr = madeira("freijo-nicho", "freijo", semente=4)
    W, H, D, e, zc = 0.62, 0.32, 0.25, 0.018, 1.30
    z0 = zc - H / 2
    caixa("n-base", (W, D, e), (0, -D / 2, z0 + e / 2), fr)
    caixa("n-teto", (W, D, e), (0, -D / 2, z0 + H - e / 2), madeira("freijo-n2", "freijo", semente=5))
    caixa("n-lat-e", (e, D, H - 2 * e), (-W / 2 + e / 2, -D / 2, zc), madeira("freijo-n3", "freijo", veio="Z", semente=6))
    caixa("n-lat-d", (e, D, H - 2 * e), (W / 2 - e / 2, -D / 2, zc), madeira("freijo-n4", "freijo", veio="Z", semente=7))
    caixa("n-div", (e, D, H - 2 * e), (0.04, -D / 2, zc), madeira("freijo-n5", "freijo", veio="Z", semente=8))
    caixa("n-fundo", (W - 2 * e, 0.008, H - 2 * e), (0, -0.006, zc), madeira("freijo-n6", "freijo", semente=9, anel=140))
    ceram = liso("ceramica", (0.80, 0.77, 0.71), 0.55)
    vaso("vaso", (-0.17, -0.12, z0 + e), 0.2, 0.062, ceram)
    livros("liv", (0.09, -0.12, z0 + e), 5, semente=3)
    esfera("bola", 0.032, (0.24, -0.13, z0 + e + 0.032), liso("pedra-bola", (0.12, 0.11, 0.10), 0.35))
    # aparador embaixo, para a peça não flutuar no nada
    tampo = madeira("carvalho-ap", "carvalho", semente=2, anel=80)
    caixa("aparador", (1.6, 0.42, 0.04), (0.1, -0.21, 0.86), tampo)
    caixa("aparador-c", (1.56, 0.40, 0.4), (0.1, -0.21, 0.64), liso("branco-ap", (0.80, 0.78, 0.73), 0.4))
    tigela("tig", (0.42, -0.2, 0.88), 0.12, 0.06, liso("ceram2", (0.20, 0.16, 0.12), 0.45))
    sol_com_janela((0, 0, 1.3), azimute=-48, elevacao=30, energia=5.0, distancia=2.4, abertura=(1.1, 1.6), folhas=(2, 3))
    luz_area("rebatedor", (1.4, -1.6, 1.4), (0, 0, 1.2), (1.5, 1.5), 35, (1, 0.97, 0.92))
    camera((0.42, -1.78, 1.40), (0.02, -0.1, 1.22), 52, abertura=4.0, foco=1.82)


def prateleira():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.22, rot=60)
    parede_e_piso((0.66, 0.60, 0.52), piso=None)
    for i, (x, z) in enumerate(((-0.12, 1.52), (0.18, 1.12))):
        caixa(f"prat{i}", (0.80, 0.23, 0.032), (x, -0.115, z), madeira(f"prat-m{i}", "freijo", semente=20 + i))
    livros("l1", (-0.50, -0.12, 1.536), 6, semente=11)
    vaso("v1", (0.08, -0.11, 1.536), 0.16, 0.055, liso("cer-a", (0.72, 0.42, 0.26), 0.6))
    ramo("r1", (0.08, -0.11, 1.68), 0.28, semente=5)
    esfera("bola1", 0.028, (0.2, -0.12, 1.536 + 0.028), liso("lat", (0.55, 0.40, 0.18), 0.28, metal=1.0))
    livros("l2", (-0.12, -0.11, 1.136), 4, deitados=True, semente=7)
    tigela("t2", (0.32, -0.11, 1.136), 0.09, 0.06, liso("cer-b", (0.86, 0.84, 0.79), 0.5))
    vaso("v2", (0.47, -0.10, 1.136), 0.24, 0.05, liso("cer-c", (0.10, 0.10, 0.10), 0.5))
    sol_com_janela((0, 0, 1.3), azimute=-52, elevacao=28, energia=5.0, distancia=2.6, abertura=(1.2, 1.8), folhas=(2, 4))
    luz_area("rebatedor", (1.3, -1.8, 1.5), (0, 0, 1.3), (1.5, 1.5), 30, (1, 0.97, 0.92))
    camera((0.36, -2.05, 1.50), (0.05, -0.1, 1.42), 45, abertura=4.5)


def tabua():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.25, rot=20)
    parede_e_piso((0.74, 0.70, 0.64), piso=None)
    zt = 0.92
    caixa("bancada", (3.0, 0.65, 0.03), (0, -0.325, zt - 0.015), pedra("quartzo"), chanfro=0.002)
    # a tábua em pé, encostada na parede, mostra o veio inteiro
    t1 = placa_arredondada("tabua1", (0.30, 0.48, 0.026), 0.04, (-0.16, -0.065, zt + 0.235),
                           madeira("tab1", "cumaru", semente=31, rugosidade=0.5, verniz=0.05, veio="Y"),
                           rot=(80, 0, 4))
    furar(t1, 0.016, (0, 0.19, 0), 0.1)
    # a deitada, com uso: faca e limão cortado em cima
    t2 = placa_arredondada("tabua2", (0.46, 0.30, 0.03), 0.035, (0.12, -0.30, zt + 0.015),
                           madeira("tab2", "freijo", semente=32, rugosidade=0.5, verniz=0.05),
                           rot=(0, 0, -12))
    furar(t2, 0.014, (0.19, 0, 0), 0.1)
    aco = liso("aco", (0.62, 0.62, 0.64), 0.22, metal=1.0)
    cabo = madeira("cabo", "nogueira", semente=3, rugosidade=0.4)
    caixa("lamina", (0.17, 0.034, 0.0022), (0.04, -0.33, zt + 0.031), aco, chanfro=0.0006, rot=(0, 0, 8))
    caixa("cabo", (0.11, 0.022, 0.016), (0.177, -0.31, zt + 0.038), cabo, chanfro=0.005, rot=(0, 0, 8))
    lim = liso("limao", (0.62, 0.48, 0.05), 0.4)
    polpa = liso("polpa", (0.78, 0.66, 0.22), 0.3)
    esfera("lim1", 0.036, (-0.04, -0.24, zt + 0.03 + 0.03), lim, 0.85)
    esfera("lim2", 0.036, (0.04, -0.21, zt + 0.03 + 0.03), lim, 0.85)
    tigela("tig", (0.46, -0.20, zt), 0.10, 0.065, liso("cer", (0.16, 0.14, 0.12), 0.45))
    for i, (dx, dy) in enumerate(((0.44, -0.2), (0.49, -0.18), (0.46, -0.24))):
        esfera(f"l{i}", 0.034, (dx, dy, zt + 0.06), lim, 0.88)
    sol_com_janela((0, -0.2, zt), azimute=-60, elevacao=34, energia=5.2, distancia=2.2, abertura=(1.0, 1.4), folhas=(2, 2))
    luz_area("reb", (1.0, -1.4, 1.6), (0.1, -0.2, zt), (1.2, 1.2), 30, (1, 0.97, 0.92))
    camera((0.34, -1.30, 1.50), (0.12, -0.17, zt + 0.10), 50, abertura=3.5)


def ripado():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.18, rot=-30)
    parede_e_piso((0.52, 0.46, 0.39), piso="assoalho")
    base = liso("base-rip", (0.05, 0.035, 0.025), 0.6)
    caixa("fundo-rip", (2.0, 0.012, 2.5), (0.15, -0.006, 1.25), base, chanfro=0)
    x = -0.85
    i = 0
    while x < 1.15:
        caixa(f"ripa{i}", (0.032, 0.022, 2.5), (x, -0.023, 1.25),
              madeira(f"rip{i % 7}", "freijo", veio="Z", semente=40 + i % 7, anel=120) if i < 7 else
              bpy.data.materials[f"rip{i % 7}"], chanfro=0.002)
        x += 0.032 + 0.016
        i += 1
    # banco baixo na frente, em nogueira, para dar escala
    nog = madeira("nog-banco", "nogueira", semente=3, anel=90)
    caixa("banco-t", (1.3, 0.38, 0.045), (0.25, -0.55, 0.43), nog)
    for dx in (-0.35, 0.85):
        caixa(f"banco-p{dx}", (0.05, 0.34, 0.41), (dx, -0.55, 0.205), nog)
    livros("lb", (0.3, -0.55, 0.4525), 3, deitados=True, semente=5)
    vaso("vb", (0.7, -0.55, 0.4525), 0.30, 0.075, liso("cer-v", (0.78, 0.74, 0.66), 0.55))
    ramo("rb", (0.7, -0.55, 0.72), 0.45, semente=9)
    # luz rasante pela esquerda: é ela que desenha o relevo do ripado
    sol_com_janela((0.1, 0, 1.2), azimute=-72, elevacao=22, energia=5.0, distancia=2.6, abertura=(1.4, 2.0), folhas=(2, 3))
    luz_area("reb", (1.8, -2.2, 1.6), (0.2, 0, 1.0), (2, 2), 55, (1, 0.97, 0.92))
    camera((1.15, -2.65, 1.25), (0.15, 0, 1.05), 35, abertura=5.6)


def banqueta_peca(prefixo, x, y, mat, altura=0.75, giro=0):
    assento = placa_arredondada(prefixo + "-as", (0.36, 0.36, 0.034), 0.17, (x, y, altura - 0.017), mat,
                                rot=(0, 0, giro), chanfro=0.004, passos=12)
    pernas = []
    for k in range(4):
        a = math.radians(45 + 90 * k + giro)
        topo = (x + 0.115 * math.cos(a), y + 0.115 * math.sin(a), altura - 0.034)
        pe = (x + 0.19 * math.cos(a), y + 0.19 * math.sin(a), 0)
        pernas.append((topo, pe))
        barra(f"{prefixo}-pe{k}", topo, pe, 0.016, mat, raio2=0.013)
    zt = 0.25
    for k in range(4):
        (t1, p1), (t2, p2) = pernas[k], pernas[(k + 1) % 4]
        f = (altura - 0.034 - zt) / (altura - 0.034)
        a1 = Vector(p1).lerp(Vector(t1), 1 - f)
        a2 = Vector(p2).lerp(Vector(t2), 1 - f)
        a1.z = a2.z = zt
        barra(f"{prefixo}-tr{k}", a1, a2, 0.011, mat)


def banqueta():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.22, rot=0)
    parede_e_piso((0.70, 0.66, 0.60), piso="concreto")
    branco = liso("mdf-branco", (0.80, 0.79, 0.75), 0.36, verniz=0.1)
    tampo = pedra("quartzo", (0.82, 0.81, 0.78))
    # ilha na altura de bar
    caixa("ilha-tampo", (2.4, 0.7, 0.03), (0, -0.95, 1.035), tampo, chanfro=0.002)
    for k in range(4):
        frente(f"ilha-f{k}", (0.6, 0.018, 0.98), (-0.9 + 0.6 * k, -0.62, 0.53), branco)
    caixa("ilha-rodape", (2.4, 0.5, 0.06), (0, -0.95, 0.03), liso("rodape", (0.05, 0.05, 0.05), 0.6))
    caixa("ilha-corpo", (2.38, 0.6, 0.95), (0, -0.95, 0.535), branco)
    nog = madeira("banq", "freijo", semente=51, anel=110)
    banqueta_peca("b1", -0.25, -1.48, nog, giro=8)
    banqueta_peca("b2", 0.38, -1.52, madeira("banq2", "freijo", semente=52, anel=110), giro=-5)
    tigela("tig", (0.55, -0.95, 1.05), 0.13, 0.07, liso("cer", (0.18, 0.15, 0.12), 0.45))
    vaso("v", (-0.6, -0.9, 1.05), 0.28, 0.07, liso("cer2", (0.80, 0.76, 0.68), 0.5))
    ramo("r", (-0.6, -0.9, 1.31), 0.42, semente=3)
    pendente("pd1", -0.4, -0.95, 3.0, 1.15, luz=25)
    pendente("pd2", 0.45, -0.95, 3.0, 1.15, luz=25)
    sol_com_janela((0, -1.3, 0.6), azimute=-55, elevacao=30, energia=4.6, distancia=2.6, abertura=(1.4, 1.8), folhas=(2, 3))
    luz_area("reb", (2.2, -3.2, 1.8), (0, -1.2, 0.8), (2.5, 2.5), 90, (1, 0.97, 0.92))
    camera((0.85, -3.65, 1.20), (0.05, -1.25, 0.76), 45, abertura=4.0)


def cabeceira():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.2, rot=20)
    parede_e_piso((0.50, 0.50, 0.44), piso="assoalho")
    fr = madeira("cab", "freijo", semente=61, anel=110)
    fr2 = madeira("cab2", "freijo", semente=62, anel=110)
    W, D, H, zl = 0.52, 0.40, 0.42, 0.18
    x0 = -0.15
    # caixa
    caixa("cb-teto", (W, D, 0.022), (x0, -D / 2 - 0.02, zl + H - 0.011), fr)
    caixa("cb-base", (W, D, 0.022), (x0, -D / 2 - 0.02, zl + 0.011), fr2)
    caixa("cb-le", (0.022, D, H - 0.044), (x0 - W / 2 + 0.011, -D / 2 - 0.02, zl + H / 2), madeira("cb3", "freijo", veio="Z", semente=63))
    caixa("cb-ld", (0.022, D, H - 0.044), (x0 + W / 2 - 0.011, -D / 2 - 0.02, zl + H / 2), madeira("cb4", "freijo", veio="Z", semente=64))
    caixa("cb-fundo", (W - 0.044, 0.01, H - 0.044), (x0, -0.025, zl + H / 2), fr2)
    caixa("cb-prat", (W - 0.044, D - 0.02, 0.018), (x0, -D / 2 - 0.02, zl + 0.2), fr)
    gav = madeira("cb-gav", "freijo", semente=65, anel=120)
    caixa("cb-gav", (W - 0.05, 0.02, 0.17), (x0, -D - 0.02 + 0.008, zl + H - 0.022 - 0.09), gav, chanfro=0.002)
    esfera("puxador", 0.012, (x0, -D - 0.02 - 0.008, zl + H - 0.11), liso("latao", (0.62, 0.45, 0.20), 0.25, metal=1.0))
    for k, (dx, dy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        barra(f"cb-pe{k}", (x0 + dx * (W / 2 - 0.04), -D / 2 - 0.02 + dy * (D / 2 - 0.04), zl),
              (x0 + dx * (W / 2 - 0.025), -D / 2 - 0.02 + dy * (D / 2 - 0.025), 0), 0.015, fr, raio2=0.011)
    livros("lc", (x0 - 0.18, -0.2, zl + 0.218), 3, semente=4)
    livros("ld", (x0 - 0.05, -0.22, zl + H), 2, deitados=True, semente=8)
    # abajur
    zt = zl + H
    torno("abaj-base", [(0.0, 0.0), (0.055, 0.0), (0.06, 0.02), (0.05, 0.12), (0.03, 0.2), (0.012, 0.24), (0.0, 0.24)],
          (x0 + 0.12, -0.2, zt), liso("abaj-cer", (0.70, 0.60, 0.48), 0.5))
    cup = torno("abaj-cup", [(0.13, 0.0), (0.128, 0.004), (0.085, 0.18), (0.083, 0.18), (0.125, 0.004), (0.127, 0.0)],
                (x0 + 0.12, -0.2, zt + 0.2), liso("linho", (0.86, 0.80, 0.70), 0.9))
    luz_ponto("abaj-luz", (x0 + 0.12, -0.2, zt + 0.29), 18, (1, 0.75, 0.48), 0.03)
    # cama ao lado
    lencol = liso("lencol", (0.78, 0.76, 0.72), 0.85)
    caixa("cama-base", (1.7, 2.0, 0.3), (x0 + W / 2 + 0.04 + 0.85, -1.0, 0.2), madeira("cama", "nogueira", semente=1))
    colchao = caixa("colchao", (1.62, 1.96, 0.24), (x0 + W / 2 + 0.06 + 0.83, -1.0, 0.47), lencol, chanfro=0.04)
    colchao.modifiers["chanfro"].segments = 6
    trav = caixa("travesseiro", (0.62, 0.42, 0.14), (x0 + W / 2 + 0.42, -0.28, 0.66), liso("fronha", (0.86, 0.84, 0.80), 0.9), chanfro=0.05)
    trav.modifiers["chanfro"].segments = 6
    caixa("cabeceira-painel", (1.9, 0.08, 0.9), (x0 + W / 2 + 0.04 + 0.85, -0.04, 0.85), liso("estofado", (0.40, 0.36, 0.30), 0.95), chanfro=0.02)
    sol_com_janela((x0, -0.2, 0.6), azimute=-58, elevacao=26, energia=4.0, distancia=2.4, abertura=(1.0, 1.6), folhas=(2, 3))
    luz_area("reb", (1.6, -2.2, 1.4), (x0, -0.3, 0.5), (1.6, 1.6), 30, (1, 0.97, 0.92))
    camera((0.40, -1.95, 0.98), (x0 + 0.08, -0.25, 0.55), 40, abertura=4.0)


def corte():
    s = nova_cena(1600, 1200, exposicao=-0.75)
    mundo("interior.exr", 0.16, rot=90)
    parede_e_piso((0.42, 0.40, 0.37), piso="concreto")
    banc = madeira("bancada-of", "pinus", semente=71, anel=70, rugosidade=0.6, verniz=0.0)
    caixa("bancada", (2.2, 0.9, 0.06), (0, -0.75, 0.87), banc)
    for k, x in enumerate((-1.0, 1.0)):
        for y in (-0.38, -1.12):
            caixa(f"pe{k}{y}", (0.08, 0.08, 0.84), (x, y, 0.42), banc)
    branco = liso("mdf-face", (0.82, 0.81, 0.77), 0.34, verniz=0.1)
    nucleo = liso("mdf-nucleo", (0.48, 0.36, 0.23), 0.85)
    amad = madeira("mdf-amad", "amadeirado", semente=72, anel=130, rugosidade=0.38)
    z = 0.90
    pecas = [((0.95, 0.42), branco, 3), ((0.80, 0.38), amad, -2), ((0.72, 0.36), branco, 5),
             ((0.60, 0.30), amad, -4), ((0.48, 0.28), branco, 2)]
    for i, ((w, d), m, g) in enumerate(pecas):
        o = caixa(f"chapa{i}", (w, d, 0.018), (-0.18 + i * 0.015, -0.72 - i * 0.008, z + 0.009), m, chanfro=0.0008, rot=(0, 0, g))
        z += 0.018
    # pilha de tiras em pé, com a borda crua aparecendo: a diferença da fita
    for i in range(6):
        caixa(f"tira{i}", (0.6, 0.018, 0.09), (0.62, -0.42 - i * 0.03, 0.9 + 0.045), nucleo if i % 2 else branco,
              chanfro=0.0008, rot=(0, 0, -3 + i))
    trena_c = liso("trena", (0.72, 0.52, 0.04), 0.4)
    cilindro("trena", 0.035, 0.035, (0.55, -0.95, 0.9 + 0.0175), trena_c, rot=(0, 0, 0), chanfro=0.006)
    caixa("trena-fita", (0.32, 0.019, 0.001), (0.36, -0.97, 0.901), liso("fita", (0.80, 0.68, 0.10), 0.3, metal=0.6), chanfro=0)
    lapis = liso("lapis", (0.75, 0.58, 0.08), 0.5)
    cilindro("lapis", 0.0045, 0.17, (0.25, -1.08, 0.905), lapis, vertices=6, rot=(0, 90, 20))
    aco = liso("aco", (0.6, 0.6, 0.62), 0.3, metal=1.0)
    caixa("esq-a", (0.30, 0.03, 0.002), (-0.05, -1.08, 0.902), aco, chanfro=0.0005, rot=(0, 0, 4))
    caixa("esq-b", (0.035, 0.16, 0.012), (-0.19, -1.0, 0.906), madeira("esq-cabo", "nogueira", semente=2), chanfro=0.002, rot=(0, 0, 4))
    sol_com_janela((0, -0.7, 0.9), azimute=-35, elevacao=40, energia=5.0, distancia=2.8, abertura=(1.6, 1.4), folhas=(3, 2))
    luz_area("reb", (1.8, -2.4, 1.8), (0, -0.8, 0.9), (2, 2), 70, (1, 0.97, 0.92))
    camera((0.55, -2.15, 1.68), (0.12, -0.78, 0.92), 45, abertura=5.0)


def bancada():
    s = nova_cena(1600, 1200)
    mundo("interior.exr", 0.24, rot=-10)
    parede_e_piso((0.68, 0.64, 0.58), piso="assoalho", largura=9.0, fundo=6.0)
    branco = liso("mdf-branco", (0.80, 0.79, 0.75), 0.36, verniz=0.1)
    # parede do fundo com armário baixo e prateleira
    for k in range(4):
        modulo(f"fundo{k}", -1.6 + 0.8 * k, 0.0, 0.1, 0.8, 0.58, 0.78, branco, branco, None, n_portas=2)
    caixa("fundo-tampo", (3.2, 0.6, 0.03), (0, -0.30, 0.895), pedra("quartzo-f", (0.80, 0.79, 0.76)))
    caixa("prat-fundo", (1.6, 0.25, 0.04), (-0.4, -0.125, 1.55), madeira("prat-f", "freijo", semente=81))
    livros("lf", (-1.0, -0.12, 1.57), 5, semente=2)
    vaso("vf", (-0.25, -0.12, 1.57), 0.22, 0.06, liso("cer-f", (0.72, 0.42, 0.26), 0.6))
    tigela("tf", (0.15, -0.12, 1.57), 0.1, 0.06, liso("cer-g", (0.86, 0.84, 0.79), 0.5))
    # a ilha com o tampo maciço — a estrela da cena
    tampo = madeira("tampo-ilha", "freijo", semente=82, anel=110, verniz=0.3)
    caixa("ilha-tampo", (2.2, 0.95, 0.05), (0.0, -1.9, 0.925), tampo, chanfro=0.003)
    caixa("ilha-corpo", (2.1, 0.85, 0.85), (0.0, -1.9, 0.475), branco)
    for k in range(3):
        frente(f"ilha-f{k}", (0.7, 0.018, 0.85), (-0.7 + 0.7 * k, -2.335, 0.475), branco)
    caixa("ilha-rod", (2.0, 0.8, 0.05), (0, -1.9, 0.025), liso("rod", (0.05, 0.05, 0.05), 0.6))
    zt = 0.95
    t = placa_arredondada("tab", (0.42, 0.26, 0.026), 0.03, (0.35, -1.85, zt + 0.013),
                          madeira("tab-i", "cumaru", semente=83, rugosidade=0.5, verniz=0.05), rot=(0, 0, 14))
    furar(t, 0.013, (0.17, 0, 0), 0.1)
    tigela("ti", (-0.45, -1.8, zt), 0.14, 0.08, liso("cer-i", (0.16, 0.14, 0.12), 0.45))
    lim = liso("limao", (0.62, 0.48, 0.05), 0.4)
    for i, (dx, dy) in enumerate(((-0.47, -1.8), (-0.42, -1.77), (-0.45, -1.84))):
        esfera(f"li{i}", 0.034, (dx, dy, zt + 0.07), lim, 0.88)
    pendente("pd1", -0.55, -1.9, 2.9, 1.05, luz=22)
    pendente("pd2", 0.55, -1.9, 2.9, 1.05, luz=22)
    sol_com_janela((0, -1.6, 0.9), azimute=-62, elevacao=30, energia=4.5, distancia=3.0, abertura=(1.6, 1.8), folhas=(2, 3))
    luz_area("reb", (2.4, -4.0, 2.0), (0, -1.8, 0.8), (2.5, 2.5), 110, (1, 0.97, 0.92))
    camera((1.35, -4.25, 1.58), (0.0, -1.6, 0.85), 40, abertura=5.6)


CENAS = {f.__name__: f for f in (nicho, prateleira, tabua, ripado, banqueta, cabeceira, corte, bancada)}

if __name__ == "__main__":
    nome, saida = sys.argv[1], sys.argv[2]
    amostras = int(sys.argv[3]) if len(sys.argv) > 3 else 96
    escala = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    CENAS[nome]()
    sc = bpy.context.scene
    sc.cycles.samples = amostras
    sc.render.resolution_percentage = escala
    renderizar(saida)
