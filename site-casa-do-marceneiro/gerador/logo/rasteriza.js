// Rasteriza um SVG no Chromium, com fundo transparente: node rasteriza.js in.svg out.png largura
const { chromium } = require("playwright");
const fs = require("fs");
(async () => {
  const [entrada, saida, largura] = process.argv.slice(2);
  let svg = fs.readFileSync(entrada, "utf8");
  const vb = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  const w = parseInt(largura, 10), h = Math.round(w * vb[3] / vb[2]);
  svg = svg.replace(/width="[^"]*" height="[^"]*"/, `width="${w}" height="${h}"`);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await p.setContent(`<!doctype html><html><body style="margin:0;background:transparent">${svg}</body></html>`);
  await p.waitForTimeout(300);
  await p.screenshot({ path: saida, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
  await b.close();
  console.log(saida, w + "x" + h);
})();
