#!/usr/bin/env python3
"""Fecha a pasta publicar/ num .zip pronto para a HostGator.

    python3 montar.py --dominio https://marceneirotatuape.com.br/        (ou .../novo/ --forcar, para o ensaio)
    python3 gerador/pacote.py <arquivo.zip>

No cPanel: Gerenciador de arquivos, entrar na pasta de destino (public_html,
ou public_html/novo no ensaio), Carregar o .zip e Extrair ali mesmo. O
.htaccess vai dentro: ele cuida do cadeado, da página 404 e do endereço
antigo do portfólio. Ficam de fora os arquivos que só servem a outras
hospedagens (CNAME, .nojekyll, _redirects, _headers).
"""
import pathlib, sys, zipfile

PUB = pathlib.Path(__file__).resolve().parents[1] / "publicar"
FORA = {"CNAME", ".nojekyll", "_redirects", "_headers"}
saida = pathlib.Path(sys.argv[1])
arquivos = sorted(p for p in PUB.rglob("*") if p.is_file() and p.name not in FORA)
assert (PUB / "index.html").exists() and (PUB / ".htaccess").exists(), "rode antes o montar.py --dominio"
with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in arquivos:
        z.write(p, p.relative_to(PUB).as_posix())
print(f"{saida.name}: {len(arquivos)} arquivos, {saida.stat().st_size / 1024 / 1024:.1f} MB")
