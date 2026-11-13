#!/usr/bin/env python3
"""Campanhas de pesquisa do Google Ads da Casa do Marceneiro — fonte única.

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

Os anúncios só dizem o que o site já diz e foi confirmado em 12/11: desde 1980,
garantia de 3 anos na estrutura, prazo em contrato e assistência técnica.
Preço não entra em anúncio: a loja não mostra valor.
"""
import csv, html as H, pathlib, re, sys, unicodedata

AQUI = pathlib.Path(__file__).parent
SITE = "https://marceneirotatuape.com.br/"
# Três campanhas de pesquisa, cada uma com verba própria, para a verba de uma
# não secar a outra: a local (casa, raio de 8 km), a comercial (empresa, cidade
# de São Paulo) e a de marca (quem já procura a Casa do Marceneiro pelo nome).
LOCAL, COMERCIAL, MARCA = "Pesquisa | Sob medida | Tatuapé 8 km", "Pesquisa | Comercial | São Paulo", "Pesquisa | Marca"
CAMPANHAS = {LOCAL: 30, COMERCIAL: 10, MARCA: 3}   # verba diária, em reais, no plano recomendado

# Títulos e descrições que servem a todos os grupos. Cada grupo soma os seus.
TITULOS_GERAIS = [
    "Marcenaria Familiar Desde 1980", "Orçamento pelo WhatsApp", "Fotos Reais das Nossas Obras",
    "Garantia de 3 Anos", "Fale Direto com o Marceneiro", "Projeto em 3D Antes de Fazer",
    "Medição no Local", "Casa do Marceneiro Tatuapé", "Madeira Maciça e MDF",
    "Oficina Própria no Tatuapé", "Prazo Escrito em Contrato", "Assistência Técnica",
]
DESCRICOES_GERAIS = [
    "Marcenaria familiar desde 1980, com oficina própria no Tatuapé. Peça orçamento hoje.",
    "Garantia de 3 anos na estrutura, prazo em contrato e assistência técnica após a entrega.",
]

# grupo → campanha, página, situação, palavras (exata e de frase), títulos e descrições próprios
GRUPOS = {
    "Marcenaria": dict(
        campanha=LOCAL, pagina="", ativo=True,
        palavras=["marcenaria tatuapé", "marcenaria zona leste", "marcenaria em são paulo",
                  "marcenaria são paulo", "marceneiro tatuapé", "marceneiro zona leste",
                  "marcenaria perto de mim", "marceneiro perto de mim", "marcenaria sob medida",
                  "marcenaria mooca", "marcenaria anália franco", "marcenaria vila formosa"],
        exige=["marcenaria"],
        titulos=["Marcenaria em São Paulo", "Marceneiro no Tatuapé", "Rua Elisiário, 143, Tatuapé"],
        descricoes=["Closet, cozinha, dormitório, cama e painel de TV. Fale direto com o marceneiro.",
                    "Mande a medida pelo WhatsApp e receba a faixa de investimento antes da visita."]),
    "Móveis sob medida e planejados": dict(
        campanha=LOCAL, pagina="", ativo=True,
        palavras=["móveis sob medida", "móveis planejados", "móveis sob medida tatuapé",
                  "móveis planejados tatuapé", "móveis planejados zona leste", "móveis sob medida zona leste",
                  "móveis planejados sob medida", "móveis planejados para apartamento",
                  "marcenaria de móveis planejados"],
        exige=["móveis sob medida", "planejados"],
        titulos=["Móveis Planejados no Tatuapé", "Móveis Sob Medida de Madeira", "Para a Casa Inteira"],
        descricoes=["Móveis planejados e sob medida feitos no Tatuapé, com medição e projeto em 3D.",
                    "Do apartamento compacto à casa inteira. Veja as fotos das obras no site."]),
    "Cozinha planejada": dict(
        campanha=LOCAL, pagina="projetos/", ativo=True,
        palavras=["cozinha planejada", "cozinha planejada tatuapé", "cozinha planejada zona leste",
                  "cozinha sob medida", "cozinha planejada sob medida", "armário de cozinha sob medida",
                  "cozinha planejada de madeira", "cozinha planejada para apartamento"],
        exige=["cozinha planejada"],
        titulos=["Cozinha Planejada Sob Medida", "Cozinha Planejada no Tatuapé", "Torre Quente e LED Embutido"],
        descricoes=["Armário até o teto, torre quente, tampo de pedra e LED. Medida da sua parede.",
                    "Veja as cozinhas entregues pela oficina e peça a sua pelo WhatsApp."]),
    "Closet e guarda-roupa": dict(
        campanha=LOCAL, pagina="projetos/", ativo=True,
        palavras=["guarda-roupa sob medida", "guarda-roupa planejado", "closet planejado",
                  "closet sob medida", "guarda roupa sob medida", "guarda roupa planejado",
                  "guarda-roupa com porta de espelho", "dormitório planejado"],
        exige=["guarda-roupa", "closet"],
        titulos=["Guarda-Roupa Sob Medida", "Closet Planejado no Tatuapé", "Guarda-Roupa Planejado"],
        descricoes=["Guarda-roupa planejado e closet sob medida, do quarto de casal ao apartamento.",
                    "Mande a medida da parede pelo WhatsApp e receba a faixa de investimento."]),
    "Cama sob medida": dict(
        campanha=LOCAL, pagina="projetos/", ativo=True,
        palavras=["cama sob medida", "cama planejada", "cama com gavetas sob medida", "bicama sob medida",
                  "cama alta planejada", "beliche sob medida", "cama com gavetão sob medida"],
        exige=["cama sob medida"],
        titulos=["Cama Sob Medida", "Cama com Gavetões e Bicama", "Cama Alta com Escada"],
        descricoes=["Cama com gavetões, bicama e cama alta com armário embaixo, na medida do quarto.",
                    "Sobra espaço no chão do quarto das crianças. Peça pelo WhatsApp."]),
    "Painel de TV e home office": dict(
        campanha=LOCAL, pagina="projetos/", ativo=True,
        palavras=["painel de tv sob medida", "painel ripado sob medida", "painel de tv planejado",
                  "rack sob medida", "home office planejado", "home office sob medida", "escrivaninha sob medida"],
        exige=["painel", "home office"],
        titulos=["Painel de TV Sob Medida", "Painel Ripado com LED", "Home Office Planejado"],
        descricoes=["Painel ripado com LED, rack suspenso e fiação escondida, na medida da sala.",
                    "Home office com escrivaninha e prateleiras que aproveitam o canto que sobrou."]),
    "Marcenaria comercial": dict(
        campanha=COMERCIAL, pagina="", ativo=True,
        palavras=["marcenaria comercial", "marcenaria corporativa", "móveis comerciais sob medida",
                  "balcão de atendimento sob medida", "balcão de recepção sob medida", "móveis para loja sob medida",
                  "marcenaria para restaurante", "marcenaria para escritório", "móveis para clínica sob medida",
                  "marcenaria para academia"],
        exige=["comercial"],
        titulos=["Marcenaria Comercial em SP", "Balcão de Recepção Sob Medida", "No Prazo da Inauguração"],
        descricoes=["Salão, recepção, loja, restaurante e academia. Projeto com o seu arquiteto.",
                    "Balcões, bancos e painéis para uso diário, com cronograma e garantia."]),
    "Marca": dict(
        campanha=MARCA, pagina="", ativo=True, so_exata=True,
        palavras=["casa do marceneiro", "casa do marceneiro tatuapé", "casa do marceneiro tatuape",
                  "casa do marceneiro são paulo"],
        exige=["casa do marceneiro"],
        titulos=["Site Oficial da Oficina", "Casa do Marceneiro Oficial", "Fale com o Gabriel"],
        descricoes=["Site oficial da Casa do Marceneiro Tatuapé. Fotos das obras, endereço e WhatsApp.",
                    "Rua Elisiário, 143, Tatuapé. Atendimento de segunda a sábado."]),
    "Móveis de madeira prontos": dict(
        campanha=LOCAL, pagina="loja/", ativo=False,   # liga quando o Gabriel quiser anunciar as peças prontas
        palavras=["aparador de madeira", "aparador de madeira maciça", "sapateira de madeira",
                  "sapateira ripada", "luminária de madeira", "nicho de madeira", "prateleira flutuante de madeira"],
        exige=["aparador", "sapateira"],
        titulos=["Aparador de Madeira", "Sapateira Ripada de Madeira", "Móveis de Madeira Prontos"],
        descricoes=["Aparador, sapateira, luminária e nicho de madeira prontos. Peça o valor pelo WhatsApp.",
                    "Feitos pela marcenaria do Tatuapé. Escolha a madeira e o tamanho e receba o valor."]),
}

CAMINHOS = {"Cozinha planejada": ("cozinha", "planejada"), "Closet e guarda-roupa": ("closet", "sob-medida"),
            "Cama sob medida": ("cama", "sob-medida"), "Painel de TV e home office": ("painel", "home-office"),
            "Marcenaria comercial": ("comercial", "sao-paulo"), "Marca": ("oficial", "tatuape"),
            "Móveis de madeira prontos": ("moveis", "madeira")}

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
                for tipo in (("Exact",) if g.get("so_exata") else ("Exact", "Phrase")):
                    w.writerow([g["campanha"], nome, "Enabled" if g["ativo"] else "Paused", p, tipo, SITE + g["pagina"]])
    with open(AQUI / "negativas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Campaign", "Keyword", "Criterion Type"])
        for camp in CAMPANHAS:
            for n in NEGATIVAS:
                w.writerow([camp, n, "Negative Phrase"])
        # a local e a comercial não pagam por quem já procura a oficina pelo nome
        for camp in (LOCAL, COMERCIAL):
            w.writerow([camp, "casa do marceneiro", "Negative Phrase"])
    with open(AQUI / "anuncios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Campaign", "Ad Group", "Ad type"] + [f"Headline {i}" for i in range(1, 16)]
                   + [f"Description {i}" for i in range(1, 5)] + ["Path 1", "Path 2", "Final URL"])
        for nome, g in GRUPOS.items():
            titulos = (TITULOS_GERAIS + g["titulos"] + [""] * 15)[:15]
            descricoes = (DESCRICOES_GERAIS + g["descricoes"] + [""] * 4)[:4]
            caminho = CAMINHOS.get(nome, ("marcenaria", "tatuape"))
            w.writerow([g["campanha"], nome, "Responsive search ad"] + titulos + descricoes + list(caminho)
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
    n = sum(len(g["palavras"]) * (1 if g.get("so_exata") else 2) for g in GRUPOS.values())
    print(f"{len(CAMPANHAS)} campanhas, {len(GRUPOS)} grupos, {n} palavras-chave (exata e de frase), {len(NEGATIVAS)} negativas, "
          f"{len(GRUPOS)} anúncios — dentro dos limites do Google"
          + (" e com cada palavra na sua página de destino" if len(sys.argv) > 1 else ""))
