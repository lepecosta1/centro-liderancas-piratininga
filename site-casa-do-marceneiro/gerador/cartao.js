// Fotografa gerador/cartao.html em 1200×630 e grava o cartão de prévia do link.
// uso: NODE_PATH=$(npm root -g) node gerador/cartao.js gerador/cartao.html capa-link.png
// (depois: python3 -c "from PIL import Image; Image.open('capa-link.png').convert('RGB').save('capa-link.jpg', quality=88, optimize=True, progressive=True)")
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  const erros = [];
  p.on("requestfailed", r => erros.push(r.url()));
  await p.goto("file://" + path.resolve(process.argv[2]));
  await p.waitForTimeout(800);
  const ok = await p.$$eval("img", is => is.every(i => i.complete && i.naturalWidth > 0));
  await p.screenshot({ path: process.argv[3] });
  console.log("imagens carregaram:", ok, "falhas:", erros.length);
  await b.close();
  process.exit(ok && !erros.length ? 0 : 1);
})();
