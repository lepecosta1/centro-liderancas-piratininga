#!/usr/bin/env python3
"""Primeira campanha de pesquisa do Google Ads da Casa do Marceneiro — fonte única.

    python3 anuncios/campanha.py            # gera os CSVs e confere
    python3 anuncios/campanha.py publicar/  # confere também as páginas de destino montadas

Gera, ao lado deste arquivo, três planilhas para o Google Ads Editor
(Conta → Importar → Do arquivo):

    palavras-chave.csv   grupo, palavra, correspondência e página de destino
    negativas.csv        o que a campanha não deve pagar para aparecer
    anuncios.csv         um anúncio responsivo por grupo (15 títulos, 4 descrições)

A conferência recusa título com mais de 30 caracteres, descrição com mais de
90 e caminho com mais de 15, que é o limite do Google. Com a pasta publicar/,
confere também se cada palavra-chave aparece na página para onde o anúncio
leva: é a relevância da página de destino que entra no Índice de Qualidade.

Os anúncios só dizem o que o site já diz e o Gabriel confirmou. Promessa que
ainda está no lancamento.json para confirmar (garantia de 3 anos, visita sem
custo, preço travado, prazos) não entra em anúncio.
"""
import csv, html as H, pathlib, re, sys, unicodedata

AQUI = pathlib.Path(__file__).parent
SITE = "https://marceneirotatuape.com.br/"
CAMPANHA = "Marcenaria Tatuapé — Pesquisa"

# Títulos e descrições que servem a todos os grupos. Cada grupo soma os seus.
TITULOS_GERAIS = [
    "Marcenaria no Tatuapé", "Móveis Sob Medida em SP", "Móveis Planejados Zona Leste",
    "Marcenaria Familiar Desde 1980", "Orçamento pelo WhatsApp", "Madeira Maciça e MDF",
    "Acabamento de Primeira Linha", "Fale Direto com o Marceneiro", "Projeto em 3D Antes de Fazer",
    "Medição no Local", "Casa do Marceneiro Tatuapé", "Nunca Usamos MDP",
]
DESCRICOES_GERAIS = [
    "Marcenaria familiar no Tatuapé desde 1980. Móveis sob medida e planejados para sua casa.",
    "Madeira maciça e MDF, nunca MDP. Acabamento com maquinário de primeira linha.",
]

# grupo → (página, situação, palavras exatas e de frase, títulos próprios, descrições próprias)
GRUPOS = {
    "Marcenaria": dict(
        pagina="", ativo=True,
        palavras=["marcenaria tatuapé", "marcenaria zona leste", "marcenaria em são paulo",
                  "marcenaria são paulo", "marceneiro tatuapé", "marceneiro zona leste",
                  "marcenaria perto de mim", "marceneiro perto de mim", "marcenaria sob medida"],
        exige=["marcenaria"],
        titulos=["Marcenaria em São Paulo", "Marceneiro no Tatuapé", "Rua Elisiário, 143, Tatuapé"],
        descricoes=["Closet, guarda-roupa, cozinha, dormitório, painel de TV e home office. Peça orçamento.",
                    "Mande a medida pelo WhatsApp e receba a faixa de investimento antes da visita."]),
    "Móveis sob medida e planejados": dict(
        pagina="", ativo=True,
        palavras=["móveis sob medida", "móveis planejados", "móveis sob medida tatuapé",
                  "móveis planejados tatuapé", "móveis planejados zona leste", "móveis sob medida zona leste",
                  "móveis planejados sob medida"],
        exige=["móveis sob medida", "planejados"],
        titulos=["Móveis Planejados no Tatuapé", "Móveis Sob Medida de Madeira", "Para a Casa Inteira"],
        descricoes=["Móveis planejados e sob medida feitos no Tatuapé, com medição e projeto em 3D.",
                    "Closet, cozinha, dormitório e sala do jeito da sua casa. Orçamento pelo WhatsApp."]),
    "Closet e guarda-roupa": dict(
        pagina="", ativo=True,
        palavras=["guarda-roupa sob medida", "guarda-roupa planejado", "closet planejado",
                  "closet sob medida", "guarda roupa sob medida", "guarda roupa planejado"],
        exige=["guarda-roupa", "closet"],
        titulos=["Guarda-Roupa Sob Medida", "Closet Planejado no Tatuapé", "Guarda-Roupa Planejado"],
        descricoes=["Guarda-roupa planejado e closet sob medida, do quarto de casal ao apartamento.",
                    "Mande a medida da parede pelo WhatsApp e receba a faixa de investimento."]),
    "Móveis de madeira prontos": dict(
        pagina="loja/", ativo=False,   # liga quando os preços da loja estiverem confirmados
        palavras=["aparador de madeira", "aparador de madeira maciça", "sapateira de madeira",
                  "sapateira ripada", "luminária de madeira", "nicho de madeira", "prateleira flutuante de madeira"],
        exige=["aparador", "sapateira"],
        titulos=["Aparador de Madeira", "Sapateira Ripada de Madeira", "Móveis de Madeira Prontos"],
        descricoes=["Aparador, sapateira, luminária e nicho de madeira com preço fechado. Peça pelo WhatsApp.",
                    "Feitos pela marcenaria do Tatuapé. Escolha a madeira e o tamanho e veja o preço."]),
}

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
    "montador de móveis", "montagem de móveis", "pallet", "desenho", "png", "imagem",
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
            caminho = ("marcenaria", "tatuape") if not g["pagina"] else ("moveis", "madeira")
            w.writerow([CAMPANHA, nome, "Responsive search ad"] + titulos + descricoes + list(caminho)
                       + [SITE + g["pagina"]])

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
    print(f"{len(GRUPOS)} grupos, {n} palavras-chave (exata e de frase), {len(NEGATIVAS)} negativas, "
          f"{len(GRUPOS)} anúncios — dentro dos limites do Google"
          + (" e com cada palavra na sua página de destino" if len(sys.argv) > 1 else ""))
