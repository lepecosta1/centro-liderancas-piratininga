// Desenha, com as fontes e as cores do site, o que vai por cima das fotos no filme:
// cada legenda, a marca no alto e o cartão final. Sai um PNG transparente de cada.
//   NODE_PATH=$(npm root -g) node gerador/filme/quadros.js <pasta de saída>
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const AQUI = __dirname, SITE = path.join(AQUI, "..", "..");
const rot = JSON.parse(fs.readFileSync(path.join(AQUI, "roteiro.json"), "utf-8"));
const saida = path.resolve(process.argv[2] || path.join(AQUI, "quadros"));
fs.mkdirSync(saida, { recursive: true });
const fontes = fs.readFileSync(path.join(SITE, "..", "proposta-marcenaria-tatuape", "fontes-embutidas.css"), "utf-8");
const logo = fs.readFileSync(path.join(SITE, "marca", "logo-site.svg"), "utf-8").replace(/<\?xml[^>]*>/, "");
const W = rot.largura, H = rot.altura;
const base = `<!doctype html><meta charset="utf-8"><style>${fontes}
  html,body{margin:0;width:${W}px;height:${H}px;background:transparent;overflow:hidden}
  body{font-family:"Barlow",sans-serif;color:#F4E9D8;-webkit-font-smoothing:antialiased}
  em{font-style:normal;color:#F5C15C}
  .leg{position:absolute;left:54px;right:54px;bottom:150px}
  .leg i{display:block;width:46px;height:3px;background:#F5C15C;border-radius:2px;margin-bottom:22px}
  .leg p{margin:0;font-family:"Fraunces",serif;font-weight:600;font-size:47px;line-height:1.17;letter-spacing:-.012em;
    font-variation-settings:"SOFT" 40,"WONK" 1;text-shadow:0 2px 18px rgba(18,12,8,.55)}
  .leg p span{display:block}
  .marca{position:absolute;left:50px;top:54px;width:196px}
  .marca svg{display:block;width:100%;height:auto}
  .fim{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 60px}
  .fim .logo{width:330px}.fim .logo svg{display:block;width:100%;height:auto}
  .fim i{display:block;width:54px;height:3px;background:#F5C15C;border-radius:2px;margin:46px 0 40px}
  .fim h1{margin:0;font-family:"Fraunces",serif;font-weight:600;font-size:54px;line-height:1.15;letter-spacing:-.015em;
    font-variation-settings:"SOFT" 40,"WONK" 1}
  .fim h1 span{display:block}
  .fim .l1{margin-top:58px;font-family:"Barlow Condensed",sans-serif;font-size:35px;letter-spacing:.09em;text-transform:uppercase;color:#F5C15C}
  .fim .l2{margin-top:14px;font-size:25px;color:#DCCBB3}
</style>`;
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })).newPage();
  const tira = async (nome, html) => {
    await p.setContent(base + html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(120);
    await p.screenshot({ path: path.join(saida, nome), omitBackground: true });
  };
  const linhas = ls => ls.map(l => `<span>${l}</span>`).join("");
  await tira("marca.png", `<div class="marca">${logo}</div>`);
  let n = 0;
  for (const [bi, bat] of rot.batidas.entries()) {
    for (const [li, leg] of (bat.legendas || []).entries()) { await tira(`legenda-${bi}-${li}.png`, `<div class="leg"><i></i><p>${linhas(leg.linhas)}</p></div>`); n++; }
    if (bat.final) await tira("final.png", `<div class="fim"><div class="logo">${logo}</div><i></i><h1>${linhas(bat.final.titulo)}</h1>
      <div class="l1">${bat.final.linha1}</div><div class="l2">${bat.final.linha2}</div></div>`);
  }
  await b.close();
  console.log(`${n} legendas, a marca e o cartão final em ${saida}`);
})();
