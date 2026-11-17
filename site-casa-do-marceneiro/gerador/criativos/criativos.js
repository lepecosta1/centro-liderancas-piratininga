// Fotografa as artes da campanha da Meta (Instagram e Facebook) a partir de criativo.html.
// uso: NODE_PATH=$(npm root -g) node gerador/criativos/criativos.js anuncios/meta
// Cada arte sai em 1080×1350 (feed) e 1080×1920 (stories e reels). Só foto real de obra.
const { chromium } = require("playwright");
const path = require("path"), fs = require("fs");
const ARTES = [
  ["cozinha", "cozinha-madeira-led", "50% 45%", "Cozinhas planejadas", "A cozinha que parece que <em>sempre esteve aí</em>.", "Armário até o teto, torre quente e LED embutido, na medida da sua parede."],
  ["closet", "closet-espelhado", "50% 40%", "Closet e guarda-roupa", "Até o teto. <em>Nenhum centímetro</em> perdido.", "Guarda-roupa planejado do quarto de casal ao apartamento compacto."],
  ["cama", "cama-alta-escada-branca", "50% 40%", "Cama sob medida", "O quarto das crianças <em>ganha o chão</em> de volta.", "Cama alta, gavetões e bicama, desenhados para o quarto de vocês."],
  ["painel", "sala-painel-iluminado", "50% 42%", "Painel de TV e sala", "Fiação escondida. <em>LED no lugar certo.</em>", "Painel ripado, rack suspenso e estante sob medida."],
  ["comercial", "comercial-salao-mesa-ilha", "50% 55%", "Para empresas", "Seu negócio inaugura no prazo. <em>A marcenaria também.</em>", "Salão, recepção, loja e restaurante, com o seu arquiteto ou direto com a oficina."],
  ["familia", "cozinha-sala-led-forro", "50% 42%", "Marcenaria familiar desde 1980", "Quem faz a sua peça <em>é quem responde</em> por ela.", "Oficina própria no Tatuapé, garantia de 3 anos e prazo em contrato."],
];
(async () => {
  const saida = path.resolve(process.argv[2] || "anuncios/meta"); fs.mkdirSync(saida, { recursive: true });
  const b = await chromium.launch(); const erros = [];
  for (const [nome, foto, foco, rot, tit, sub] of ARTES) {
    for (const [fmt, alt, tam] of [["feed", 1350, 76], ["stories", 1920, 86]]) {
      const p = await b.newPage({ viewport: { width: 1080, height: alt } });
      p.on("requestfailed", r => erros.push(r.url()));
      const q = new URLSearchParams({ foto, foco, rot, tit, sub, alt, tam });
      await p.goto("file://" + path.resolve(__dirname, "criativo.html") + "?" + q);
      await p.waitForTimeout(700);
      const ok = await p.$eval("#foto", i => i.complete && i.naturalWidth > 0);
      if (!ok) erros.push(foto);
      await p.screenshot({ path: path.join(saida, `${nome}-${fmt}.jpg`), type: "jpeg", quality: 90 });
      await p.close();
    }
  }
  await b.close();
  console.log(ARTES.length * 2 + " artes em " + saida + (erros.length ? " · falhas: " + erros.join(" ") : ""));
  process.exit(erros.length ? 1 : 0);
})();
