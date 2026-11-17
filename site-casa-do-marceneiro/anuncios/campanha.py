#!/usr/bin/env python3
"""Campanha de pesquisa do Google Ads da Casa do Marceneiro — fonte única.

    python3 anuncios/campanha.py            # gera os arquivos e confere
    python3 anuncios/campanha.py publicar/  # confere também as páginas de destino montadas

Uma campanha só, de R$ 50 por dia, para o Gabriel tocar sozinho pelo painel do
Google Ads: cinco grupos de anúncio, um por pedido de cliente. Gera, ao lado
deste arquivo:

    palavras-chave.csv   grupo, palavra, correspondência e página de destino (Google Ads Editor)
    negativas.csv        o que a campanha não deve pagar para aparecer
    anuncios.csv         um anúncio responsivo por grupo (15 títulos, 4 descrições)
    recursos.csv         sitelinks, frases de destaque e snippet estruturado
    kit-gabriel.txt      tudo isso em texto, para copiar e colar no painel, grupo a grupo

A conferência recusa título com mais de 30 caracteres, descrição com mais de
90, sitelink com mais de 25 (descrição de sitelink, 35), frase de destaque com
mais de 25 e caminho com mais de 15, que são os limites do Google. Com a pasta
publicar/, confere também se cada palavra-chave aparece na página para onde o
anúncio leva: a relevância da página de destino entra no Índice de Qualidade.

Os anúncios só dizem o que o site já diz e foi confirmado em 12/11: desde 1980,
garantia de 3 anos na estrutura, prazo em contrato e assistência técnica.
Preço não entra em anúncio: a loja não mostra valor. CasaCor também não: é
marca registrada de terceiros.
"""
import csv, html as H, pathlib, re, sys, unicodedata

AQUI = pathlib.Path(__file__).parent
SITE = "https://marceneirotatuape.com.br/"
CAMPANHA = "Casa do Marceneiro | Pesquisa | Tatuapé"
DIARIO = 50                     # reais por dia; o Gabriel sobe aos poucos (ver kit)
RAIO_KM = 10                    # em volta da Rua Elisiário, 143
# ValueTrack: o Google troca {keyword} pela palavra que trouxe o clique, e o
# site escreve essa palavra na mensagem de WhatsApp que o cliente envia.
SUFIXO = "utm_source=google&utm_medium=cpc&utm_campaign=pesquisa-tatuape&utm_term={keyword}"

TITULOS_GERAIS = [
    "Marcenaria Familiar Desde 1980", "Orçamento pelo WhatsApp", "Fotos Reais das Nossas Obras",
    "Garantia de 3 Anos", "Fale Direto com o Marceneiro", "Oficina Própria no Tatuapé",
    "Prazo Escrito em Contrato", "Projeto em 3D Antes de Fazer", "Site Novo: Veja as Obras",
    # fim de ano: tirar em fevereiro (ver kit)
    "Comece 2027 com a Casa Pronta", "Use o 13º na Casa Nova",
    "Medição no Local",
]
DESCRICOES_GERAIS = [
    "Marcenaria familiar desde 1980, com oficina própria no Tatuapé. Peça orçamento hoje.",
    "Garantia de 3 anos na estrutura, prazo em contrato e assistência técnica após a entrega.",
]

GRUPOS = {
    "Marcenaria e móveis planejados": dict(
        pagina="", ativo=True,
        palavras=["marcenaria tatuapé", "marcenaria zona leste", "marceneiro tatuapé", "marceneiro zona leste",
                  "marcenaria perto de mim", "marceneiro perto de mim", "marcenaria sob medida",
                  "marcenaria mooca", "marcenaria anália franco", "marcenaria vila formosa", "marcenaria penha",
                  "móveis planejados tatuapé", "móveis planejados zona leste", "móveis sob medida zona leste",
                  "móveis sob medida tatuapé", "móveis planejados para apartamento",
                  "casa do marceneiro", "casa do marceneiro tatuapé"],
        exige=["marcenaria", "planejados"],
        titulos=["Marceneiro no Tatuapé", "Móveis Planejados Zona Leste", "Rua Elisiário, 143, Tatuapé"],
        descricoes=["Cozinha, closet, cama, painel de TV e home office. Fale direto com o marceneiro.",
                    "Mande a medida pelo WhatsApp e receba a faixa de investimento antes da visita."],
        caminho=("marcenaria", "tatuape")),
    "Cozinha planejada": dict(
        pagina="projetos/", ativo=True,
        palavras=["cozinha planejada", "cozinha planejada tatuapé", "cozinha planejada zona leste",
                  "cozinha sob medida", "cozinha planejada sob medida", "armário de cozinha sob medida",
                  "cozinha planejada de madeira", "cozinha planejada para apartamento",
                  "cozinha planejada pequena", "cozinha planejada com ilha"],
        exige=["cozinha planejada"],
        titulos=["Cozinha Planejada Sob Medida", "Cozinha Planejada no Tatuapé", "Torre Quente e LED Embutido"],
        descricoes=["Armário até o teto, torre quente, tampo de pedra e LED. Na medida da sua parede.",
                    "Veja as cozinhas entregues pela oficina e peça a sua pelo WhatsApp."],
        caminho=("cozinha", "planejada")),
    "Quarto: closet, guarda-roupa e cama": dict(
        pagina="projetos/", ativo=True,
        palavras=["guarda-roupa sob medida", "guarda-roupa planejado", "guarda roupa planejado",
                  "closet planejado", "closet sob medida", "dormitório planejado", "quarto planejado",
                  "cama sob medida", "cama planejada", "cama com gavetas sob medida", "bicama sob medida",
                  "cama alta planejada", "quarto planejado infantil"],
        exige=["guarda-roupa", "closet", "cama sob medida"],
        titulos=["Guarda-Roupa Sob Medida", "Cama Sob Medida com Gavetões", "Quarto Planejado no Tatuapé"],
        descricoes=["Guarda-roupa até o teto, closet com espelho e cama com gavetões, na medida do quarto.",
                    "Cama alta, bicama e gaveteiro: sobra espaço no chão do quarto. Peça pelo WhatsApp."],
        caminho=("quarto", "sob-medida")),
    "Sala, painel de TV e home office": dict(
        pagina="projetos/", ativo=True,
        palavras=["painel de tv sob medida", "painel ripado sob medida", "painel de tv planejado",
                  "rack sob medida", "home office planejado", "home office sob medida",
                  "escrivaninha sob medida", "sala planejada", "estante sob medida"],
        exige=["painel", "home office"],
        titulos=["Painel de TV Sob Medida", "Painel Ripado com LED", "Home Office Planejado"],
        descricoes=["Painel ripado com LED, rack suspenso e fiação escondida, na medida da sala.",
                    "Home office com escrivaninha e prateleiras que aproveitam o canto que sobrou."],
        caminho=("sala", "home-office")),
    "Marcenaria comercial": dict(
        pagina="", ativo=True,
        palavras=["marcenaria comercial", "marcenaria corporativa", "móveis comerciais sob medida",
                  "balcão de atendimento sob medida", "balcão de recepção sob medida",
                  "móveis para loja sob medida", "marcenaria para restaurante", "marcenaria para escritório",
                  "móveis para clínica sob medida", "marcenaria para academia"],
        exige=["comercial"],
        titulos=["Marcenaria Comercial em SP", "Balcão de Recepção Sob Medida", "No Prazo da Inauguração"],
        descricoes=["Salão, recepção, loja, restaurante e academia. Projeto com o seu arquiteto.",
                    "Balcões, bancos e painéis para uso diário, com cronograma e garantia."],
        caminho=("comercial", "empresas")),
}

# Recursos (antes "extensões") da campanha: aparecem junto do anúncio e
# aumentam o espaço dele na tela do celular.
SITELINKS = [   # texto (25), descrição 1 e 2 (35 cada), página
    ("Fotos das Obras", "Cozinhas, quartos, salas e mais", "Tudo obra entregue pela oficina", "projetos/"),
    ("A Oficina Desde 1980", "Empresa familiar no Tatuapé", "Garantia e prazo em contrato", "oficina/"),
    ("Pedir Orçamento", "Mande a medida pelo WhatsApp", "Resposta no horário comercial", "contato/"),
    ("Peças Prontas", "Aparador, nicho, prateleira", "Imagens ilustrativas da loja", "loja/"),
]
FRASES = ["Desde 1980", "Oficina Própria", "Garantia de 3 Anos", "Prazo em Contrato",
          "Medição no Local", "Projeto em 3D", "Assistência Técnica", "Atende Casa e Empresa"]
SNIPPET = ("Serviços", ["Cozinha Planejada", "Closet", "Guarda-Roupa", "Cama Sob Medida",
                        "Painel de TV", "Home Office", "Marcenaria Comercial"])

# Quem procura isto não vai contratar marcenaria: curso, emprego, faça você
# mesmo, móvel usado, loja de móvel pronto e corte de chapa (a oficina não
# vende corte avulso).
NEGATIVAS = [
    "curso", "cursos", "aula", "apostila", "escola", "emprego", "vaga", "vagas", "salário", "trabalhe conosco",
    "como fazer", "faça você mesmo", "diy", "passo a passo", "pdf", "molde", "projeto grátis", "grátis", "gratis",
    "usado", "usados", "seminovo", "segunda mão", "olx", "mercado livre", "shopee", "magalu", "casas bahia",
    "madeiramadeira", "mobly", "tok stok", "leroy merlin", "todeschini", "italínea", "dell anno", "ikea",
    "ferramentas", "máquina", "maquina", "tupia", "serra circular", "promob", "sketchup",
    "chapa de mdf", "corte de mdf", "plano de corte", "seccionadora", "madeireira",
    "montador de móveis", "montagem de móveis", "pallet", "desenho", "png", "imagem", "barato", "preço de fábrica",
]


def tira_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def conferir_textos():
    erros = []
    for nome, g in GRUPOS.items():
        titulos = TITULOS_GERAIS + g["titulos"]
        descricoes = DESCRICOES_GERAIS + g["descricoes"]
        if len(titulos) > 15: erros.append(f"{nome}: {len(titulos)} títulos (máximo 15)")
        if len(descricoes) > 4: erros.append(f"{nome}: {len(descricoes)} descrições (máximo 4)")
        if len(set(titulos)) != len(titulos): erros.append(f"{nome}: título repetido")
        erros += [f"{nome}: título com {len(t)} caracteres: {t}" for t in titulos if len(t) > 30]
        erros += [f"{nome}: descrição com {len(d)} caracteres: {d}" for d in descricoes if len(d) > 90]
        erros += [f"{nome}: '!' em título: {t}" for t in titulos if "!" in t]
        erros += [f"{nome}: caminho com mais de 15: {c}" for c in g["caminho"] if len(c) > 15]
    for t, d1, d2, _ in SITELINKS:
        if len(t) > 25: erros.append(f"sitelink com {len(t)} caracteres: {t}")
        erros += [f"descrição de sitelink com {len(d)}: {d}" for d in (d1, d2) if len(d) > 35]
    erros += [f"frase de destaque com {len(f)}: {f}" for f in FRASES if len(f) > 25]
    erros += [f"snippet com {len(v)}: {v}" for v in SNIPPET[1] if len(v) > 25]
    return erros


def texto_da_pagina(pub, pagina):
    t = (pub / pagina / "index.html").read_text(encoding="utf-8")
    titulo = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
    corpo = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return tira_acento(H.unescape(titulo + " " + re.sub(r"<[^>]+>", " ", corpo)).lower())


def conferir_paginas(pub):
    erros = []
    for nome, g in GRUPOS.items():
        txt = texto_da_pagina(pub, g["pagina"])
        for termo in g["exige"]:
            if tira_acento(termo.lower()).replace("-", " ") not in txt.replace("-", " "):
                erros.append(f"{nome}: a página /{g['pagina']} não tem “{termo}”")
    for _, _, _, pagina in SITELINKS:
        if not (pub / pagina / "index.html").exists():
            erros.append(f"sitelink para /{pagina}, que não existe")
    return erros


def gravar():
    with open(AQUI / "palavras-chave.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Campaign", "Ad Group", "Ad Group Status", "Keyword", "Criterion Type", "Final URL"])
        for nome, g in GRUPOS.items():
            for p in g["palavras"]:
                for tipo in ("Exact", "Phrase"):
                    w.writerow([CAMPANHA, nome, "Enabled" if g["ativo"] else "Paused", p, tipo, SITE + g["pagina"]])
    with open(AQUI / "negativas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Campaign", "Keyword", "Criterion Type"])
        for n in NEGATIVAS:
            w.writerow([CAMPANHA, n, "Negative Phrase"])
    with open(AQUI / "anuncios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Campaign", "Ad Group", "Ad type"] + [f"Headline {i}" for i in range(1, 16)]
                   + [f"Description {i}" for i in range(1, 5)] + ["Path 1", "Path 2", "Final URL"])
        for nome, g in GRUPOS.items():
            titulos = (TITULOS_GERAIS + g["titulos"] + [""] * 15)[:15]
            descricoes = (DESCRICOES_GERAIS + g["descricoes"] + [""] * 4)[:4]
            w.writerow([CAMPANHA, nome, "Responsive search ad"] + titulos + descricoes + list(g["caminho"])
                       + [SITE + g["pagina"]])
    with open(AQUI / "recursos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Tipo", "Texto", "Descrição 1", "Descrição 2", "URL final"])
        for t, d1, d2, pg in SITELINKS:
            w.writerow(["Sitelink", t, d1, d2, SITE + pg])
        for fr in FRASES:
            w.writerow(["Frase de destaque", fr, "", "", ""])
        w.writerow(["Snippet estruturado: " + SNIPPET[0], "; ".join(SNIPPET[1]), "", "", ""])
    (AQUI / "kit-gabriel.txt").write_text(kit(), encoding="utf-8")


def kit():
    """O texto que o Gabriel cola no painel, na ordem em que o painel pede."""
    L = [f"CAMPANHA: {CAMPANHA}", f"Orçamento: R$ {DIARIO} por dia · Raio: {RAIO_KM} km da Rua Elisiário, 143, Tatuapé",
         f"Sufixo do URL final (Configurações da campanha > Opções de URL da campanha):\n{SUFIXO}", ""]
    for nome, g in GRUPOS.items():
        L += ["=" * 60, f"GRUPO DE ANÚNCIOS: {nome}", f"URL final: {SITE + g['pagina']}",
              f"Caminho de exibição: {g['caminho'][0]} / {g['caminho'][1]}", "",
              "Palavras-chave (cole todas de uma vez):"]
        for p in g["palavras"]:
            L += [f"[{p}]", f'"{p}"']
        L += ["", "Títulos (15):"] + [f"  {t}" for t in TITULOS_GERAIS + g["titulos"]]
        L += ["", "Descrições (4):"] + [f"  {d}" for d in DESCRICOES_GERAIS + g["descricoes"]] + [""]
    L += ["=" * 60, "PALAVRAS NEGATIVAS DA CAMPANHA (cole todas de uma vez):"] + [f'"{n}"' for n in NEGATIVAS]
    L += ["", "=" * 60, "SITELINKS:"]
    for t, d1, d2, pg in SITELINKS:
        L += [f"  {t} | {d1} | {d2} | {SITE + pg}"]
    L += ["", "FRASES DE DESTAQUE:"] + [f"  {fr}" for fr in FRASES]
    L += ["", f"SNIPPET ESTRUTURADO ({SNIPPET[0]}):"] + [f"  {v}" for v in SNIPPET[1]]
    L += ["", "Em fevereiro, tirar os títulos “Comece 2027 com a Casa Pronta” e “Use o 13º na Casa Nova”."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    erros = conferir_textos()
    if len(sys.argv) > 1:
        erros += conferir_paginas(pathlib.Path(sys.argv[1]))
    if erros:
        print("Não gravei. Falta corrigir:")
        for e in erros: print("  ·", e)
        sys.exit(1)
    gravar()
    n = sum(len(g["palavras"]) * 2 for g in GRUPOS.values())
    print(f"1 campanha (R$ {DIARIO}/dia), {len(GRUPOS)} grupos, {n} palavras-chave (exata e de frase), "
          f"{len(NEGATIVAS)} negativas, {len(GRUPOS)} anúncios, {len(SITELINKS)} sitelinks, {len(FRASES)} frases"
          + (" — com cada palavra na sua página de destino" if len(sys.argv) > 1 else ""))
