"""Biblioteca das cenas 3D do site — madeira procedural, luz e câmera.

As fotos do acervo do Gabriel ainda não chegaram, e o site não pode ir para
a reunião com caixa vazia nem com foto de banco fingindo ser trabalho dele.
O meio-termo honesto é o que toda marcenaria já mostra ao cliente: o
projeto em 3D. Cada imagem do site sai daqui, renderizada no Blender
(Cycles), com madeira gerada por fórmula — nada baixado, nada de terceiros,
direito de uso total.

Uso:  python -m gerador.fotos.<cena>   (com o pacote `bpy` instalado)
"""
import math, random
import bpy, bmesh
from mathutils import Vector

DATAFILES = bpy.utils.system_resource("DATAFILES")


# ------------------------------------------------------------------ cena
def nova_cena(largura=1600, altura=1200, amostras=96, exposicao=-0.6, look="AgX - Medium High Contrast"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = amostras
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.03
    s.cycles.use_denoising = True
    s.cycles.denoiser = "OPENIMAGEDENOISE"
    s.cycles.max_bounces = 8
    s.cycles.diffuse_bounces = 4
    s.cycles.glossy_bounces = 4
    s.cycles.transparent_max_bounces = 4
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.blur_glossy = 1.0
    s.render.resolution_x = largura
    s.render.resolution_y = altura
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_depth = "8"
    s.view_settings.view_transform = "AgX"
    s.view_settings.exposure = exposicao
    s.view_settings.look = look
    s.render.film_transparent = False
    return s


def mundo(hdri="interior.exr", forca=0.35, rot=0.0, cor_fundo=None):
    """Luz ambiente vinda de um HDRI do próprio Blender. A câmera não vê o
    HDRI de baixa resolução: o fundo visível é sempre geometria da cena."""
    w = bpy.data.worlds.new("mundo")
    bpy.context.scene.world = w
    nt = w.node_tree
    nt.nodes.clear()
    saida = nt.nodes.new("ShaderNodeOutputWorld")
    luz = nt.nodes.new("ShaderNodeBackground")
    luz.inputs["Strength"].default_value = forca
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(f"{DATAFILES}/studiolights/world/{hdri}")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value[2] = math.radians(rot)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], luz.inputs["Color"])
    if cor_fundo is None:
        nt.links.new(luz.outputs["Background"], saida.inputs["Surface"])
    else:
        # câmera vê cor lisa; a luz continua vindo do HDRI
        fundo = nt.nodes.new("ShaderNodeBackground")
        fundo.inputs["Color"].default_value = (*cor_fundo, 1)
        fundo.inputs["Strength"].default_value = 1.0
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
        nt.links.new(luz.outputs["Background"], mix.inputs[1])
        nt.links.new(fundo.outputs["Background"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], saida.inputs["Surface"])
    return w


def luz_area(nome, local, alvo, tamanho=(2, 2), energia=400, cor=(1, 0.93, 0.84), forma="RECTANGLE"):
    d = bpy.data.lights.new(nome, "AREA")
    d.shape = forma
    d.size, d.size_y = tamanho
    d.energy = energia
    d.color = cor
    o = bpy.data.objects.new(nome, d)
    bpy.context.collection.objects.link(o)
    o.location = local
    mirar(o, alvo)
    return o


def luz_sol(angulo_xyz, energia=3.0, cor=(1, 0.92, 0.80), suavidade=2.0):
    d = bpy.data.lights.new("sol", "SUN")
    d.energy = energia
    d.color = cor
    d.angle = math.radians(suavidade)
    o = bpy.data.objects.new("sol", d)
    bpy.context.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in angulo_xyz)
    return o


def luz_ponto(nome, local, energia=40, cor=(1, 0.8, 0.55), raio=0.05):
    d = bpy.data.lights.new(nome, "POINT")
    d.energy = energia
    d.color = cor
    d.shadow_soft_size = raio
    o = bpy.data.objects.new(nome, d)
    bpy.context.collection.objects.link(o)
    o.location = local
    return o


def mirar(obj, alvo):
    dire = Vector(alvo) - obj.location
    obj.rotation_euler = dire.to_track_quat("-Z", "Y").to_euler()


def camera(local, alvo, lente=35, foco=None, abertura=None, desloc_y=0.0):
    d = bpy.data.cameras.new("cam")
    d.lens = lente
    d.sensor_width = 36
    d.shift_y = desloc_y
    d.clip_start = 0.02
    o = bpy.data.objects.new("cam", d)
    bpy.context.collection.objects.link(o)
    o.location = local
    mirar(o, alvo)
    if abertura:
        d.dof.use_dof = True
        d.dof.aperture_fstop = abertura
        d.dof.focus_distance = foco if foco else (Vector(alvo) - Vector(local)).length
    bpy.context.scene.camera = o
    return o


def renderizar(caminho):
    bpy.context.scene.render.filepath = str(caminho)
    bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------- geometria
def caixa(nome, dim, local=(0, 0, 0), mat=None, chanfro=0.0015, rot=(0, 0, 0)):
    """Caixa com as medidas reais em metros, centrada no ponto dado.
    O chanfro de 1,5 mm é o que pega o brilho na quina, como na peça lixada."""
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dim[0]; v.co.y *= dim[1]; v.co.z *= dim[2]
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(o)
    o.location = local
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    if chanfro:
        b = o.modifiers.new("chanfro", "BEVEL")
        b.width = min(chanfro, min(dim) * 0.3)
        b.segments = 2
        b.limit_method = "ANGLE"
    if mat:
        o.data.materials.append(mat)
    return o


def cilindro(nome, raio, altura, local=(0, 0, 0), mat=None, vertices=48, rot=(0, 0, 0), chanfro=0.0):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=vertices, radius1=raio, radius2=raio, depth=altura)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(o)
    o.location = local
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    if chanfro:
        b = o.modifiers.new("chanfro", "BEVEL")
        b.width = chanfro; b.segments = 2; b.limit_method = "ANGLE"
    o.modifiers.new("suave", "WEIGHTED_NORMAL") if False else None
    if mat:
        o.data.materials.append(mat)
    return o


def torno(nome, perfil, local=(0, 0, 0), mat=None, passos=64):
    """Sólido de revolução a partir de um perfil [(raio, altura), ...] — vaso, tigela, xícara."""
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    aneis = []
    for i in range(passos):
        a = 2 * math.pi * i / passos
        aneis.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in perfil])
    for i in range(passos):
        A, B = aneis[i], aneis[(i + 1) % passos]
        for j in range(len(perfil) - 1):
            bm.faces.new((A[j], B[j], B[j + 1], A[j + 1]))
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(o)
    o.location = local
    sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
    if mat:
        o.data.materials.append(mat)
    return o


def plano(nome, dim, local=(0, 0, 0), mat=None, rot=(0, 0, 0)):
    return caixa(nome, (dim[0], dim[1], 0.002), local, mat, chanfro=0, rot=rot)


# -------------------------------------------------------------- materiais
def _sk(colecao, nome, tipo="RGBA"):
    """O nó Mix tem três soquetes chamados "A" (número, vetor, cor); pegar
    pelo nome sozinho liga a cor no soquete de número e a mistura some."""
    for k in colecao:
        if k.name == nome and k.type == tipo:
            return k
    raise KeyError(nome)


def _nos(nome):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def liso(nome, cor, rugosidade=0.5, metal=0.0, verniz=0.0, especular=0.5):
    m, nt, p = _nos(nome)
    p.inputs["Base Color"].default_value = (*cor, 1)
    p.inputs["Roughness"].default_value = rugosidade
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = verniz
    p.inputs["Coat Roughness"].default_value = 0.15
    p.inputs["Specular IOR Level"].default_value = especular
    return m


def emissor(nome, cor=(1, 0.85, 0.6), forca=8.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*cor, 1)
    em.inputs["Strength"].default_value = forca
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def reboco(nome, cor=(0.80, 0.76, 0.70), escala=60, relevo=0.04):
    """Parede pintada: cor quase lisa, com a ondulação leve do reboco."""
    m, nt, p = _nos(nome)
    N = nt.nodes; L = nt.links
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = escala
    nz.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    nz2 = N.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 2.5
    L.new(tc.outputs["Object"], nz2.inputs["Vector"])
    rampa = N.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].color = (cor[0] * 0.95, cor[1] * 0.95, cor[2] * 0.95, 1)
    rampa.color_ramp.elements[1].color = (min(1, cor[0] * 1.03), min(1, cor[1] * 1.03), min(1, cor[2] * 1.03), 1)
    L.new(nz2.outputs["Fac"], rampa.inputs["Fac"])
    L.new(rampa.outputs["Color"], p.inputs["Base Color"])
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = relevo
    L.new(nz.outputs["Fac"], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.88
    return m


def pedra(nome, cor=(0.86, 0.85, 0.82), veios=(0.55, 0.54, 0.52), rugosidade=0.18, escala=1.4):
    """Quartzo/mármore claro para tampo: base clara com veio fino."""
    m, nt, p = _nos(nome)
    N = nt.nodes; L = nt.links
    tc = N.new("ShaderNodeTexCoord")
    dist = N.new("ShaderNodeTexNoise")
    dist.inputs["Scale"].default_value = escala
    dist.inputs["Detail"].default_value = 10
    L.new(tc.outputs["Object"], dist.inputs["Vector"])
    onda = N.new("ShaderNodeTexWave")
    onda.wave_type = "BANDS"; onda.bands_direction = "DIAGONAL"
    onda.inputs["Scale"].default_value = escala * 0.8
    onda.inputs["Distortion"].default_value = 14
    onda.inputs["Detail"].default_value = 8
    L.new(tc.outputs["Object"], onda.inputs["Vector"])
    rampa = N.new("ShaderNodeValToRGB")
    e = rampa.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*veios, 1)
    e[1].position = 0.06; e[1].color = (*cor, 1)
    L.new(onda.outputs["Fac"], rampa.inputs["Fac"])
    L.new(rampa.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rugosidade
    return m


def concreto(nome, cor=(0.42, 0.41, 0.39)):
    m, nt, p = _nos(nome)
    N = nt.nodes; L = nt.links
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 12
    nz.inputs["Roughness"].default_value = 0.65
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    rampa = N.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].color = (cor[0] * 0.8, cor[1] * 0.8, cor[2] * 0.8, 1)
    rampa.color_ramp.elements[1].color = (cor[0] * 1.15, cor[1] * 1.15, cor[2] * 1.15, 1)
    L.new(nz.outputs["Fac"], rampa.inputs["Fac"])
    L.new(rampa.outputs["Color"], p.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.55; rr.inputs["To Max"].default_value = 0.85
    L.new(nz.outputs["Fac"], rr.inputs["Value"])
    L.new(rr.outputs["Result"], p.inputs["Roughness"])
    return m


# Paletas de madeira: (claro, escuro, variação) em sRGB linearizado à mão.
MADEIRAS = {
    "freijo":   ((0.42, 0.25, 0.12), (0.22, 0.12, 0.05), (0.33, 0.19, 0.08)),
    "nogueira": ((0.15, 0.08, 0.042), (0.045, 0.022, 0.011), (0.095, 0.05, 0.025)),
    "pinus":    ((0.78, 0.56, 0.33), (0.55, 0.33, 0.15), (0.70, 0.48, 0.26)),
    "carvalho": ((0.62, 0.43, 0.24), (0.38, 0.23, 0.11), (0.52, 0.35, 0.18)),
    "amadeirado": ((0.55, 0.36, 0.19), (0.36, 0.21, 0.10), (0.47, 0.30, 0.15)),
    "cumaru":   ((0.36, 0.19, 0.08), (0.17, 0.08, 0.03), (0.28, 0.14, 0.06)),
}


def madeira(nome, especie="freijo", escala=1.0, rugosidade=0.42, verniz=0.25, semente=None,
            veio="X", anel=100.0, distorcao=2.5, relevo=0.08, tardio=0.83):
    """Madeira procedural.

    Anéis de crescimento em torno de um eixo longe da peça (corte tangencial),
    distorcidos por ruído: no tampo aparecem as catedrais, no topo da tábua
    aparece o anel, como na chapa de verdade. `veio` diz em que eixo local da
    peça corre a fibra.
    """
    claro, escuro, meio = MADEIRAS[especie]
    rnd = random.Random(semente if semente is not None else nome)
    m, nt, p = _nos(nome)
    N = nt.nodes; L = nt.links
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    base = {"X": (0, 0, 0), "Y": (0, 0, math.pi / 2), "Z": (0, math.pi / 2, 0)}[veio]
    # a medula corre quase paralela à tábua, mas não exatamente: é essa
    # inclinação de 1 a 3 graus que faz o corte cruzar os anéis em arco
    incl = (rnd.uniform(-0.01, 0.01), rnd.uniform(0.008, 0.028) * rnd.choice((-1, 1)), rnd.uniform(-0.02, 0.02))
    mp.inputs["Rotation"].default_value = (base[0] + incl[0], base[1] + incl[1], base[2] + incl[2])
    mp.inputs["Location"].default_value = (rnd.uniform(-3, 3), rnd.uniform(-0.06, 0.06), rnd.uniform(0.07, 0.22))
    mp.inputs["Scale"].default_value = (escala, escala, escala)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])

    # fibra esticada ao longo do eixo X: ruído achatado, para a distorção
    est = N.new("ShaderNodeMapping")
    est.inputs["Scale"].default_value = (0.12, 1.0, 1.0)
    L.new(mp.outputs["Vector"], est.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.2
    nz.inputs["Detail"].default_value = 4
    L.new(est.outputs["Vector"], nz.inputs["Vector"])
    soma = N.new("ShaderNodeVectorMath"); soma.operation = "ADD"
    escn = N.new("ShaderNodeVectorMath"); escn.operation = "SCALE"
    escn.inputs["Scale"].default_value = 0.03
    sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (0.5, 0.5, 0.5)
    L.new(nz.outputs["Color"], sub.inputs[0])
    L.new(sub.outputs["Vector"], escn.inputs[0])
    L.new(est.outputs["Vector"], soma.inputs[0])
    L.new(escn.outputs["Vector"], soma.inputs[1])

    anelw = N.new("ShaderNodeTexWave")
    anelw.wave_type = "RINGS"; anelw.rings_direction = "X"
    anelw.wave_profile = "SAW"
    anelw.inputs["Scale"].default_value = anel
    # a distorção interna lê o vetor esticado ao longo da fibra: o anel
    # engrossa e afina ao longo da tábua sem virar onda de desenho animado
    anelw.inputs["Distortion"].default_value = distorcao
    anelw.inputs["Detail"].default_value = 2.0
    anelw.inputs["Detail Scale"].default_value = 0.8
    anelw.inputs["Detail Roughness"].default_value = 0.45
    L.new(soma.outputs["Vector"], anelw.inputs["Vector"])

    # anel duro: lenho tardio fino e escuro, lenho inicial largo e claro
    curva = N.new("ShaderNodeMapRange")
    curva.inputs["From Min"].default_value = tardio
    curva.inputs["From Max"].default_value = 1.0
    L.new(anelw.outputs["Fac"], curva.inputs["Value"])

    # poros e fibras finas
    fib_m = N.new("ShaderNodeMapping")
    fib_m.inputs["Scale"].default_value = (0.02, 1.0, 1.0)
    L.new(mp.outputs["Vector"], fib_m.inputs["Vector"])
    fib = N.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 900
    fib.inputs["Detail"].default_value = 2
    L.new(fib_m.outputs["Vector"], fib.inputs["Vector"])
    fib_r = N.new("ShaderNodeMapRange")
    fib_r.inputs["From Min"].default_value = 0.45
    fib_r.inputs["From Max"].default_value = 0.75
    L.new(fib.outputs["Fac"], fib_r.inputs["Value"])

    # variação larga de tom de uma tábua para outra
    var = N.new("ShaderNodeTexNoise")
    var.inputs["Scale"].default_value = 0.9
    L.new(est.outputs["Vector"], var.inputs["Vector"])

    r1 = N.new("ShaderNodeValToRGB")
    e = r1.color_ramp.elements
    e[0].color = (*claro, 1); e[1].color = (*escuro, 1)
    m_ = e.new(0.45); m_.color = (*meio, 1)
    L.new(curva.outputs["Result"], r1.inputs["Fac"])

    mix_var = N.new("ShaderNodeMix"); mix_var.data_type = "RGBA"; mix_var.blend_type = "MULTIPLY"
    r2 = N.new("ShaderNodeValToRGB")
    r2.color_ramp.elements[0].color = (0.82, 0.82, 0.82, 1)
    r2.color_ramp.elements[1].color = (1.08, 1.06, 1.04, 1)
    L.new(var.outputs["Fac"], r2.inputs["Fac"])
    _sk(mix_var.inputs, "Factor", "VALUE").default_value = 1.0
    L.new(r1.outputs["Color"], _sk(mix_var.inputs, "A"))
    L.new(r2.outputs["Color"], _sk(mix_var.inputs, "B"))

    mix_fib = N.new("ShaderNodeMix"); mix_fib.data_type = "RGBA"; mix_fib.blend_type = "MIX"
    _sk(mix_fib.inputs, "B").default_value = (*escuro, 1)
    fator = N.new("ShaderNodeMath"); fator.operation = "MULTIPLY"
    fator.inputs[1].default_value = 0.28
    L.new(fib_r.outputs["Result"], fator.inputs[0])
    L.new(fator.outputs["Value"], _sk(mix_fib.inputs, "Factor", "VALUE"))
    L.new(_sk(mix_var.outputs, "Result"), _sk(mix_fib.inputs, "A"))
    L.new(_sk(mix_fib.outputs, "Result"), p.inputs["Base Color"])

    # relevo: o anel fica um tico abaixo, como a madeira lixada e selada
    soma_h = N.new("ShaderNodeMath"); soma_h.operation = "ADD"
    L.new(curva.outputs["Result"], soma_h.inputs[0])
    meia = N.new("ShaderNodeMath"); meia.operation = "MULTIPLY"; meia.inputs[1].default_value = 0.4
    L.new(fib_r.outputs["Result"], meia.inputs[0])
    L.new(meia.outputs["Value"], soma_h.inputs[1])
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = relevo
    bump.inputs["Distance"].default_value = 0.0004
    bump.invert = True
    L.new(soma_h.outputs["Value"], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])

    p.inputs["Roughness"].default_value = rugosidade
    p.inputs["Coat Weight"].default_value = verniz
    p.inputs["Coat Roughness"].default_value = 0.22
    p.inputs["Specular IOR Level"].default_value = 0.45
    return m


def assoalho(nome_base, area, especie="carvalho", largura=0.19, comp=(1.2, 2.4), z=0.0, semente=3):
    """Piso de tábuas corridas, uma tábua por objeto — cada uma com seu veio."""
    rnd = random.Random(semente)
    x0, x1, y0, y1 = area
    mats = [madeira(f"{nome_base}-{i}", especie, rugosidade=0.38, verniz=0.35, semente=semente * 10 + i,
                    anel=26, relevo=0.05) for i in range(6)]
    y = y0; fila = 0
    while y < y1:
        x = x0 - rnd.uniform(0, comp[1])
        while x < x1:
            c = rnd.uniform(*comp)
            ini, fim = max(x, x0), min(x + c, x1)
            if fim - ini > 0.05:
                caixa(f"{nome_base}-t{fila}-{x:.2f}", (fim - ini - 0.003, largura - 0.003, 0.018),
                      ((ini + fim) / 2, y + largura / 2, z - 0.009), rnd.choice(mats), chanfro=0.0012)
            x += c
        y += largura; fila += 1


# ------------------------------------------------------- peças compostas
def sem_camera(o):
    """Objeto que só existe para a luz: a câmera e os reflexos não o veem."""
    o.visible_camera = False
    o.visible_glossy = False
    o.visible_diffuse = False
    return o


def barra(nome, p1, p2, raio, mat=None, vertices=32, raio2=None):
    """Cilindro (ou tronco de cone) ligando dois pontos — perna, travessa, cabo."""
    p1, p2 = Vector(p1), Vector(p2)
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=vertices, radius1=raio,
                          radius2=raio2 if raio2 is not None else raio, depth=(p2 - p1).length)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(o)
    o.location = (p1 + p2) / 2
    o.rotation_euler = (p2 - p1).to_track_quat("Z", "Y").to_euler()
    b = o.modifiers.new("chanfro", "BEVEL"); b.width = min(raio * 0.25, 0.002); b.segments = 2
    b.limit_method = "ANGLE"
    if mat:
        o.data.materials.append(mat)
    return o


def placa_arredondada(nome, dim, raio, local=(0, 0, 0), mat=None, rot=(0, 0, 0), chanfro=0.002, passos=10):
    """Placa com cantos arredondados em planta — tábua de corte, tampo, assento."""
    w, d, h = dim
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    pts = []
    for cx, cy, a0 in ((w / 2 - raio, d / 2 - raio, 0), (-w / 2 + raio, d / 2 - raio, 90),
                       (-w / 2 + raio, -d / 2 + raio, 180), (w / 2 - raio, -d / 2 + raio, 270)):
        for i in range(passos + 1):
            a = math.radians(a0 + 90 * i / passos)
            pts.append((cx + raio * math.cos(a), cy + raio * math.sin(a)))
    base = [bm.verts.new((x, y, -h / 2)) for x, y in pts]
    f = bm.faces.new(base)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += h
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(o)
    o.location = local
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    if chanfro:
        b = o.modifiers.new("chanfro", "BEVEL"); b.width = chanfro; b.segments = 3
        b.limit_method = "ANGLE"; b.angle_limit = math.radians(50)
    if mat:
        o.data.materials.append(mat)
    return o


def furar(alvo, raio, local, profundidade=0.2, rot=(0, 0, 0)):
    """Furo passante por subtração — o furo de pendurar da tábua."""
    c = cilindro(alvo.name + "-furo", raio, profundidade, local, rot=rot)
    c.parent = alvo          # `local` é medido na própria peça
    c.hide_render = True
    b = alvo.modifiers.new("furo", "BOOLEAN")
    b.object = c
    b.operation = "DIFFERENCE"
    # o furo entra antes do chanfro, para a borda do furo também ganhar quina
    alvo.modifiers.move(alvo.modifiers.find("furo"), 0)
    return c


def gobo_janela(centro, normal, abertura=(1.4, 1.6), folhas=(2, 2), montante=0.06, tamanho=5.0):
    """Moldura de janela invisível entre o sol e a cena: projeta na parede a
    sombra da caixilharia, que é o que faz uma imagem parecer luz de verdade."""
    from mathutils import Matrix
    W, H = abertura
    T = tamanho
    pecas = []
    pecas.append(((-(T + W) / 4 - 0 + 0, 0), ((T - W) / 2, T)))
    pecas = [
        ((-(W / 2 + (T / 2 - W / 2) / 2), 0), (T / 2 - W / 2, T)),
        (((W / 2 + (T / 2 - W / 2) / 2), 0), (T / 2 - W / 2, T)),
        ((0, (H / 2 + (T / 2 - H / 2) / 2)), (W, T / 2 - H / 2)),
        ((0, -(H / 2 + (T / 2 - H / 2) / 2)), (W, T / 2 - H / 2)),
    ]
    for i in range(1, folhas[0]):
        pecas.append(((-W / 2 + W * i / folhas[0], 0), (montante, H)))
    for j in range(1, folhas[1]):
        pecas.append(((0, -H / 2 + H * j / folhas[1]), (W, montante)))
    raiz = bpy.data.objects.new("gobo", None)
    bpy.context.collection.objects.link(raiz)
    raiz.location = centro
    raiz.rotation_euler = Vector(normal).to_track_quat("Z", "Y").to_euler()
    for k, ((x, y), (w, h)) in enumerate(pecas):
        o = caixa(f"gobo{k}", (w, h, 0.02), (x, y, 0), None, chanfro=0)
        o.parent = raiz
        sem_camera(o)
    return raiz


def sol_com_janela(alvo, azimute=-35, elevacao=32, energia=4.5, distancia=2.2, abertura=(1.3, 1.7),
                   folhas=(2, 3), cor=(1.0, 0.86, 0.68), suavidade=1.2):
    """Sol entrando por uma janela fora de quadro, mirando o ponto `alvo`."""
    az, el = math.radians(azimute), math.radians(elevacao)
    # direção de onde vem a luz (do alvo para o sol)
    para_sol = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    sol = luz_sol((0, 0, 0), energia, cor, suavidade)
    sol.rotation_euler = para_sol.to_track_quat("Z", "Y").to_euler()
    gobo_janela(Vector(alvo) + para_sol * distancia, para_sol, abertura, folhas)
    return sol


def livros(prefixo, inicio, n=5, direcao=(1, 0, 0), deitados=False, semente=1, mats=None):
    """Fileira de livros de lombadas sóbrias, alturas e espessuras variadas."""
    rnd = random.Random(semente)
    cores = [(0.36, 0.12, 0.08), (0.11, 0.17, 0.16), (0.62, 0.55, 0.43), (0.08, 0.08, 0.09),
             (0.45, 0.33, 0.18), (0.70, 0.67, 0.60), (0.20, 0.26, 0.33), (0.52, 0.30, 0.20)]
    mats = mats or [liso(f"{prefixo}-capa{i}", c, 0.62) for i, c in enumerate(cores)]
    x, y, z = inicio
    feitos = []
    for i in range(n):
        esp = rnd.uniform(0.018, 0.038)
        alt = rnd.uniform(0.19, 0.27)
        prof = rnd.uniform(0.13, 0.17)
        m = rnd.choice(mats)
        if deitados:
            o = caixa(f"{prefixo}{i}", (alt, prof, esp), (x, y, z + esp / 2), m, chanfro=0.002,
                      rot=(0, 0, rnd.uniform(-6, 6)))
            z += esp
        else:
            o = caixa(f"{prefixo}{i}", (esp, prof, alt), (x + esp / 2, y, z + alt / 2), m, chanfro=0.002)
            x += esp + 0.001
        feitos.append(o)
    return feitos


def vaso(nome, local, altura=0.22, raio=0.07, mat=None):
    r, h = raio, altura
    perfil = [(0.0, 0.0), (r * 0.62, 0.0), (r * 0.9, h * 0.08), (r, h * 0.35), (r * 0.92, h * 0.62),
              (r * 0.52, h * 0.86), (r * 0.42, h * 0.97), (r * 0.46, h), (r * 0.38, h), (r * 0.33, h * 0.9)]
    return torno(nome, perfil, local, mat)


def tigela(nome, local, raio=0.11, altura=0.07, mat=None):
    r, h = raio, altura
    perfil = [(0.0, 0.0), (r * 0.45, 0.0), (r * 0.5, h * 0.06), (r * 0.82, h * 0.3), (r, h),
              (r * 0.95, h), (r * 0.78, h * 0.36), (r * 0.42, h * 0.14), (0.0, h * 0.14)]
    return torno(nome, perfil, local, mat)


def esfera(nome, raio, local, mat=None, achatar=1.0):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=raio)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(o)
    o.location = local
    o.scale = (1, 1, achatar)
    if mat:
        o.data.materials.append(mat)
    return o


def ramo(prefixo, base, altura=0.45, folhas=9, semente=2, mat=None):
    """Galho seco de eucalipto no vaso: haste fina e folhas ovais pequenas."""
    rnd = random.Random(semente)
    mat = mat or liso(prefixo + "-folha", (0.30, 0.36, 0.28), 0.55)
    haste = liso(prefixo + "-haste", (0.24, 0.17, 0.10), 0.7)
    bx, by, bz = base
    topo = Vector((bx + rnd.uniform(-0.06, 0.06), by + rnd.uniform(-0.03, 0.03), bz + altura))
    barra(prefixo + "-h", (bx, by, bz), topo, 0.003, haste, 8)
    for i in range(folhas):
        t = 0.35 + 0.65 * i / max(1, folhas - 1)
        p = Vector((bx, by, bz)).lerp(topo, t)
        lado = 1 if i % 2 else -1
        f = esfera(f"{prefixo}-f{i}", 0.022, p + Vector((lado * 0.022, rnd.uniform(-0.01, 0.01), 0)), mat)
        f.scale = (1.0, 0.18, 0.62)
        f.rotation_euler = (math.radians(rnd.uniform(-20, 20)), 0, math.radians(lado * rnd.uniform(20, 50)))
    return topo


def frente(nome, dim, local, mat, folga=0.003, chanfro=0.0012):
    """Porta ou frente de gaveta: a medida do vão menos a folga dos dois lados."""
    w, d, h = dim
    return caixa(nome, (w - 2 * folga, d, h - 2 * folga), local, mat, chanfro=chanfro)


def modulo(prefixo, x0, y0, z0, w, d, h, corpo, porta, metal=None, n_portas=1, gavetas=0,
           puxador="barra", aberto=False, esp=0.018):
    """Módulo de marcenaria: caixa em MDF de 18 mm e frentes com folga de 3 mm.
    (x0, y0, z0) é o canto de trás-esquerda-baixo; a frente fica em y0 - d."""
    feitos = []
    cx = x0 + w / 2
    yf = y0 - d
    feitos.append(caixa(prefixo + "-lat-e", (esp, d, h), (x0 + esp / 2, y0 - d / 2, z0 + h / 2), corpo))
    feitos.append(caixa(prefixo + "-lat-d", (esp, d, h), (x0 + w - esp / 2, y0 - d / 2, z0 + h / 2), corpo))
    feitos.append(caixa(prefixo + "-base", (w - 2 * esp, d, esp), (cx, y0 - d / 2, z0 + esp / 2), corpo))
    feitos.append(caixa(prefixo + "-teto", (w - 2 * esp, d, esp), (cx, y0 - d / 2, z0 + h - esp / 2), corpo))
    feitos.append(caixa(prefixo + "-fundo", (w - 2 * esp, 0.006, h - 2 * esp), (cx, y0 - 0.003, z0 + h / 2), corpo))
    if aberto:
        return feitos
    if gavetas:
        hg = h / gavetas
        for g in range(gavetas):
            zc = z0 + hg * g + hg / 2
            feitos.append(frente(f"{prefixo}-g{g}", (w, esp, hg), (cx, yf - esp / 2, zc), porta))
            if metal and puxador == "barra":
                feitos.append(caixa(f"{prefixo}-pg{g}", (min(0.32, w * 0.55), 0.012, 0.012),
                                    (cx, yf - esp - 0.012, zc + hg / 2 - 0.045), metal, chanfro=0.003))
    else:
        wp = w / n_portas
        for k in range(n_portas):
            xc = x0 + wp * k + wp / 2
            feitos.append(frente(f"{prefixo}-p{k}", (wp, esp, h), (xc, yf - esp / 2, z0 + h / 2), porta))
            if metal and puxador == "barra":
                xs = xc + (wp / 2 - 0.05) * (1 if k % 2 == 0 else -1) * (-1 if n_portas == 1 else 1)
                feitos.append(caixa(f"{prefixo}-pp{k}", (0.012, 0.012, min(0.22, h * 0.4)),
                                    (xs, yf - esp - 0.012, z0 + h - min(0.2, h * 0.3)) if z0 < 1.0 else
                                    (xs, yf - esp - 0.012, z0 + min(0.2, h * 0.3)), metal, chanfro=0.003))
    return feitos


def pendente(prefixo, x, y, z_teto, comprimento=0.8, raio=0.11, cor_cupula=(0.05, 0.05, 0.05), luz=35):
    fio = liso(prefixo + "-fio", (0.02, 0.02, 0.02), 0.5)
    cup = liso(prefixo + "-cup", cor_cupula, 0.38, metal=0.6)
    barra(prefixo + "-f", (x, y, z_teto), (x, y, z_teto - comprimento), 0.0025, fio, 8)
    zc = z_teto - comprimento
    perfil = [(0.012, 0.0), (0.03, -0.01), (raio * 0.55, -0.05), (raio * 0.9, -0.12), (raio, -0.16),
              (raio * 0.97, -0.16), (raio * 0.86, -0.12), (raio * 0.5, -0.055), (0.025, -0.012)]
    torno(prefixo + "-c", perfil, (x, y, zc), cup)
    lamp = esfera(prefixo + "-l", 0.03, (x, y, zc - 0.1), emissor(prefixo + "-e", (1, 0.82, 0.55), 18))
    luz_ponto(prefixo + "-p", (x, y, zc - 0.11), luz, (1, 0.78, 0.5), 0.04)
    return lamp
