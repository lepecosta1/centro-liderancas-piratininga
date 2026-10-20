"""Desenho do logo da Casa do Marceneiro, em geometria pura.

Redesenhado a partir do arquivo de 421 x 162 px que a casa usa hoje. Cada
reta, arco e curva foi medido no original ampliado 8 vezes e ajustado por
sobreposição: o redesenho cobre 99,3% do telhado e 98,3% de MARCENEIRO; o
que sobra é o antisserrilhado do original, não diferença de desenho.

Coordenadas em pixels do original. Os cantos são vivos: o arredondado que
aparece no original ampliado é o antisserrilhado de letras de 35 px.

- telhado e janela: polígono por interseção de retas ajustadas por mínimos
  quadrados, e arco de perfil parabólico na janela;
- CASA DO: linhas de centro com um traço só, como o letreiro art déco de
  fio duplo que é;
- MARCENEIRO: polígonos, círculos e, no C, uma curva polar de Fourier.
"""
import math
import numpy as np

# ================================================================ telhado
def _reta(p, q):
    p, q = np.array(p, float), np.array(q, float)
    return p, (q - p) / np.linalg.norm(q - p)

def _horiz(y):
    return np.array([0.0, y]), np.array([1.0, 0.0])

def _corta(r1, r2):
    (p1, d1), (p2, d2) = r1, r2
    t = np.linalg.solve(np.array([d1, -d2]).T, p2 - p1)
    return p1 + d1 * t[0]

def _pol(pts):
    return "M" + "L".join(f"{x:.3f} {y:.3f}" for x, y in pts) + "Z"

Lt = _reta((115.696, 60.798), (178.198, 10.865))   # água esquerda, borda de cima
Lb = _reta((111.723, 67.500), (174.777, 18.264))   # água esquerda, borda de baixo
Bt = _reta((184.266, 19.913), (260.734, 43.420))   # tábua: borda de cima
Bb = _reta((191.624, 36.259), (254.751, 85.402))   # tábua: borda de baixo
Dt = _reta((274.624, 46.945), (354.126, 38.031))   # água-furtada: borda de cima
Rt = _reta((345.440, 16.445), (382.811, 87.180))   # perna direita, borda de fora
Rb = _reta((343.663, 19.079), (381.538, 89.546))   # perna direita, borda de dentro
Dl = _reta((318.548, 81.245), (374.309, 23.880))   # água-furtada: borda de baixo
Gd = _reta((285.908, 53.238), (352.467, 97.623))   # diagonal interna da base
Pt = _reta((348.976, 66.117), (405.879, 122.349))  # chanfro da ponta direita
Yd, Ybt, Ybb = _horiz(61.062), _horiz(89.062), _horiz(100.775)
CORTE_ESQ, CORTE_DIR = _horiz(59.30), _horiz(67.00)  # pontas dos traços finos

def telhado_pontos():
    return [_corta(Lt, Bt), _corta(Bt, Dt), _corta(Dt, Rt), _corta(Rt, CORTE_DIR), _corta(Rb, CORTE_DIR),
            _corta(Rb, Dl), _corta(Dl, Yd), _corta(Yd, Gd), _corta(Gd, Ybt), _corta(Ybt, Pt),
            _corta(Pt, Ybb), _corta(Ybb, Bb), _corta(Bb, Lb), _corta(Lb, CORTE_ESQ), _corta(Lt, CORTE_ESQ)]

def telhado():
    return _pol(telhado_pontos())

# janela: arco de perfil parabólico (medido linha a linha), não semicírculo
JX0, JX1, JTOPO, JNASC, JBASE = 347.40, 363.26, 59.90, 70.50, 82.90
K1, K2 = 0.16, 0.54   # tensões das alças do arco

def janela():
    xm = (JX0 + JX1) / 2; hw = (JX1 - JX0) / 2; h = JNASC - JTOPO
    return (f"M{JX0:.3f} {JBASE:.3f}V{JNASC:.3f}"
            f"C{JX0:.3f} {JNASC - K1 * h:.3f} {xm - K2 * hw:.3f} {JTOPO:.3f} {xm:.3f} {JTOPO:.3f}"
            f"C{xm + K2 * hw:.3f} {JTOPO:.3f} {JX1:.3f} {JNASC - K1 * h:.3f} {JX1:.3f} {JNASC:.3f}"
            f"V{JBASE:.3f}Z")

# ================================================================ CASA DO
# medido no esqueleto do original: topo 71,30, base 99,50; círculos de raio
# 14,10; cordas do C e do O a 8,27 do centro; A com inclinação 0,4
YT, YB = 71.30, 99.50
YM = (YT + YB) / 2
R = (YB - YT) / 2
K = 8.27            # cordas do C e do O
INC = 0.40          # inclinação das pernas do A (dx por dy)
TRACO = 2.0         # espessura do fio, calibrada por sobreposição

def _c(cx):
    h = (R * R - K * K) ** 0.5
    return (f"M{cx + K:.3f} {YM - h:.3f}A{R:.3f} {R:.3f} 0 1 0 {cx + K:.3f} {YM + h:.3f}"
            f"M{cx - K:.3f} {YM - h:.3f}V{YM + h:.3f}")

def _a(ax):
    d = INC * (YM - YT)
    return (f"M{ax:.3f} {YT:.3f}L{ax + 2 * d:.3f} {YB:.3f}"
            f"M{ax - 2 * d:.3f} {YB:.3f}L{ax - d:.3f} {YM:.3f}H{ax + d:.3f}"
            f"M{ax:.3f} {YM:.3f}L{ax + d:.3f} {YB:.3f}")

def _s(xdu, xdl, x_fim_topo, x_ini_base, rx_sup, rx_inf):
    ry = (YM - YT) / 2
    return (f"M{x_fim_topo:.3f} {YT:.3f}H{xdu:.3f}A{rx_sup:.3f} {ry:.3f} 0 0 0 {xdu:.3f} {YM:.3f}"
            f"H{xdl:.3f}A{rx_inf:.3f} {ry:.3f} 0 0 1 {xdl:.3f} {YB:.3f}H{x_ini_base:.3f}"
            f"M{xdu:.3f} {YT:.3f}V{YM:.3f}M{xdl:.3f} {YM:.3f}V{YB:.3f}")

def _d(s1, s2, cx):
    return (f"M{s1:.3f} {YT:.3f}H{cx:.3f}A{R:.3f} {R:.3f} 0 0 1 {cx:.3f} {YB:.3f}H{s1:.3f}V{YM:.3f}"
            f"M{s2:.3f} {YM:.3f}V{YB:.3f}")

def _o(cx):
    h = (R * R - K * K) ** 0.5
    return (f"M{cx - R:.3f} {YM:.3f}A{R:.3f} {R:.3f} 0 1 0 {cx + R:.3f} {YM:.3f}A{R:.3f} {R:.3f} 0 1 0 {cx - R:.3f} {YM:.3f}"
            f"M{cx - K:.3f} {YM - h:.3f}V{YM + h:.3f}M{cx + K:.3f} {YM - h:.3f}V{YM + h:.3f}")

# pontas das barras e larguras das curvas do S, ajustadas por sobreposição
S_PARAM = dict(xdu=95.19, xdl=106.19, x_fim_topo=111.80, x_ini_base=89.40, rx_sup=5.74, rx_inf=5.65)

def casa_do():
    """Linhas de centro de CASA DO: vão com traço TRACO, ponta e quina redondas."""
    return (_c(41.98) + _a(69.85) + _s(**S_PARAM) + _a(131.49)
            + _d(166.06, 171.94, 174.75) + _o(211.16))

# ============================================================= MARCENEIRO
TOPO, BASE = 110.00, 144.62     # altura das maiúsculas; C e O passam um tico, como manda a óptica

def letra_m():
    xl, xr, xc = 27.25, 69.75, 48.50
    swl, swr = 8.37, 8.50
    sd = 0.470                     # inclinação das diagonais (dx por dy)
    meia_fundo = 4.59              # meia largura do fundo do V, na base
    meia_alto = 11.95              # borda de dentro da diagonal, no topo
    def x_fora(lado, y):
        return xc + lado * (meia_fundo + sd * (BASE - y))
    def x_dentro(lado, y):
        return xc + lado * (meia_alto - sd * (y - TOPO))
    y_notch = TOPO + meia_alto / sd
    yce = BASE - (xc - meia_fundo - (xl + swl)) / sd
    ycd = BASE - ((xr - swr) - xc - meia_fundo) / sd
    return _pol([(xl, BASE), (xl, TOPO), (x_dentro(-1, TOPO), TOPO), (xc, y_notch), (x_dentro(1, TOPO), TOPO),
                 (xr, TOPO), (xr, BASE), (xr - swr, BASE), (xr - swr, ycd), (x_fora(1, BASE), BASE),
                 (x_fora(-1, BASE), BASE), (xl + swl, yce), (xl + swl, BASE)])

def letra_a():
    xa, meia_topo, sa, wa = 94.625, 4.695, 0.4255, 8.81
    y_barra_cima, y_barra_baixo = 132.25, 139.00
    pe = meia_topo + sa * (BASE - TOPO)           # meia abertura de fora, na base
    def dentro(y): return pe - wa - sa * (BASE - y)
    y_ap = BASE - (pe - wa) / sa
    fora = [(xa - meia_topo, TOPO), (xa + meia_topo, TOPO), (xa + pe, BASE), (xa + pe - wa, BASE),
            (xa + dentro(y_barra_baixo), y_barra_baixo), (xa - dentro(y_barra_baixo), y_barra_baixo),
            (xa - (pe - wa), BASE), (xa - pe, BASE)]
    furo = [(xa, y_ap), (xa + dentro(y_barra_cima), y_barra_cima), (xa - dentro(y_barra_cima), y_barra_cima)]
    return _pol(fora) + _pol(furo)

def letra_r(dx=0.0):
    x0, sw = 119.50 + dx, 8.50
    ocx, ocy, oR = 135.56 + dx, 122.94, 12.94
    icx, icy, ir = 134.93 + dx, 123.065, 5.185
    y_barra = 135.88
    sp = 0.66                                    # perna: dx por dy
    esq = (np.array((136.95 + dx, 140.86)), np.array((sp, 1.0)) / math.hypot(sp, 1.0))
    dir_ = (np.array((146.47 + dx, 140.00)), np.array((sp, 1.0)) / math.hypot(sp, 1.0))
    # onde a perna encontra o arco de fora, abaixo do centro
    p, d = dir_
    q = p - (ocx, ocy)
    b = 2 * d @ q; c = q @ q - oR * oR
    jx, jy = p + d * (-b + math.sqrt(b * b - 4 * c)) / 2
    ang_j = math.atan2(jy - ocy, jx - ocx)
    chao, barra = _horiz(BASE), _horiz(y_barra)
    n = 64
    arco = [(ocx + oR * math.cos(th), ocy + oR * math.sin(th))
            for th in (-math.pi / 2 + (ang_j + math.pi / 2) * k / n for k in range(n + 1))]
    fora = ([(x0, BASE), (x0, TOPO)] + arco
            + [tuple(_corta(dir_, chao)), tuple(_corta(esq, chao)), tuple(_corta(esq, barra)),
               (x0 + sw, y_barra), (x0 + sw, BASE)])
    furo = (f"M{x0 + sw:.3f} {icy - ir:.3f}H{icx:.3f}A{ir:.3f} {ir:.3f} 0 0 1 {icx:.3f} {icy + ir:.3f}"
            f"H{x0 + sw:.3f}Z")
    return _pol(fora) + furo

# C: borda de fora em série polar de Fourier, de dentro um círculo, cortes retos
C_CENTRO = np.array((171.2467, 127.0660))
C_RAIO_DENTRO = 10.2075
C_COEF = (18.13764, -0.12831, 0.30743, -0.05962, -0.10868, -0.02187)
C_CORTES = {"sup": ((183.3125, 120.4920), (0.86668, -0.49887)),
            "inf": ((182.6375, 133.4625), (0.87759, 0.47942))}

def letra_c():
    cx, cy = C_CENTRO
    def p_fora(th):
        r = sum(a * math.cos(k * th) for k, a in enumerate(C_COEF))
        return np.array([cx + r * math.cos(th), cy + r * math.sin(th)])
    def corte(nome):
        p, d = C_CORTES[nome]
        p, d = np.array(p), np.array(d)
        return p, d / np.linalg.norm(d)
    def acha_fora(reta):
        # ângulo em que a reta do corte cruza a borda de fora (bissecção)
        p, d = reta
        nrm = np.array([-d[1], d[0]])
        f = lambda th: (p_fora(th) - p) @ nrm
        th0 = math.atan2(p[1] - cy, p[0] - cx)
        a, b = th0 - 0.5, th0 + 0.5
        for _ in range(60):
            m = (a + b) / 2
            if f(a) * f(m) <= 0: b = m
            else: a = m
        return (a + b) / 2
    def acha_dentro(reta):
        # a reta cruza o círculo de dentro duas vezes; vale a do mesmo lado do corte
        p, d = reta
        q = p - C_CENTRO
        b = 2 * d @ q; c = q @ q - C_RAIO_DENTRO ** 2
        raiz = math.sqrt(b * b - 4 * c)
        return p + d * min((-b + raiz) / 2, (-b - raiz) / 2, key=abs)
    rs, ri = corte("sup"), corte("inf")
    a0 = acha_fora(rs) % (2 * math.pi)
    a1 = acha_fora(ri) % (2 * math.pi)
    if a1 > a0: a1 -= 2 * math.pi
    ds, di = acha_dentro(rs), acha_dentro(ri)
    n = 220
    fora = [tuple(p_fora(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    b0 = math.atan2(di[1] - cy, di[0] - cx) % (2 * math.pi)
    b1 = math.atan2(ds[1] - cy, ds[0] - cx) % (2 * math.pi)
    if b1 < b0: b1 += 2 * math.pi
    dentro = [(cx + C_RAIO_DENTRO * math.cos(b0 + (b1 - b0) * k / n), cy + C_RAIO_DENTRO * math.sin(b0 + (b1 - b0) * k / n))
              for k in range(n + 1)]
    return _pol(fora + dentro)

def letra_e(dx=0.0):
    x0, sw = 192.75 + dx, 8.37
    comp, comp_meio = 26.44, 23.37
    b1, m0, m1, b2 = 117.82, 123.50, 130.80, 136.62
    return _pol([(x0, TOPO), (x0 + comp, TOPO), (x0 + comp, b1), (x0 + sw, b1), (x0 + sw, m0), (x0 + comp_meio, m0),
                 (x0 + comp_meio, m1), (x0 + sw, m1), (x0 + sw, b2), (x0 + comp, b2), (x0 + comp, BASE), (x0, BASE)])

def letra_n():
    xl, swl, xr, swr, s = 225.38, 8.43, 259.50, 8.38, 0.8333
    xs_top = 233.75                  # borda de cima da diagonal, no topo
    xi_base = 251.20                 # borda de baixo da diagonal, na base
    y_cd = TOPO + ((xr - swr) - xs_top) / s
    y_ce = BASE - (xi_base - (xl + swl)) / s
    return _pol([(xl, BASE), (xl, TOPO), (xs_top, TOPO), (xr - swr, y_cd), (xr - swr, TOPO), (xr, TOPO), (xr, BASE),
                 (xr - swr, BASE), (xl + swl, y_ce), (xl + swl, BASE)])

def letra_i():
    return _pol([(299.75, TOPO), (308.06, TOPO), (308.06, BASE), (299.75, BASE)])

def letra_o():
    cx, cy, R_, r = 365.82, 127.29, 17.71, 10.05
    return (f"M{cx - R_:.3f} {cy:.3f}A{R_:.3f} {R_:.3f} 0 1 0 {cx + R_:.3f} {cy:.3f}A{R_:.3f} {R_:.3f} 0 1 0 {cx - R_:.3f} {cy:.3f}Z"
            f"M{cx - r:.3f} {cy:.3f}A{r:.3f} {r:.3f} 0 1 1 {cx + r:.3f} {cy:.3f}A{r:.3f} {r:.3f} 0 1 1 {cx - r:.3f} {cy:.3f}Z")

def marceneiro():
    # o segundo E e o segundo R são cópias exatas do primeiro, deslocadas
    return (letra_m() + letra_a() + letra_r() + letra_c() + letra_e() + letra_n() + letra_e(73.87)
            + letra_i() + letra_r(196.12) + letra_o())

# ================================================================ conjunto
# caixa do desenho, já com a meia espessura do fio de CASA DO
CAIXA = (26.875, 16.0, 384.125, 145.0)   # x0, y0, x1, y1, medida no desenho rasterizado a 8x

def formas(cor="#F3E2C8", traco_cor=None):
    """O logo inteiro como elementos SVG, numa cor só."""
    traco_cor = traco_cor or cor
    return (f'<g fill="{cor}" fill-rule="evenodd"><path d="{telhado()}"/><path d="{janela()}"/>'
            f'<path d="{marceneiro()}"/></g>'
            f'<path d="{casa_do()}" fill="none" stroke="{traco_cor}" stroke-width="{TRACO:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')

def icone_formas(cor="#F3E2C8"):
    """Só o telhado e a janela: o símbolo, para favicon e avatar."""
    return f'<g fill="{cor}" fill-rule="evenodd"><path d="{telhado()}"/><path d="{janela()}"/></g>'
