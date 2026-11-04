// Conferência do site como vai ao ar (publicar/), servido como raiz do domínio.
//   python3 montar.py --dominio https://marceneirotatuape.com.br/ --forcar
//   NODE_PATH=$(npm root -g) node testes/dominio.js [porta]
const { chromium, devices } = require("playwright");
const fs = require("fs"), path = require("path"), { spawn } = require("child_process");
const PUB = path.join(__dirname, "..", "publicar");
const PORTA = process.argv[2] || "8765";
const URL0 = `http://localhost:${PORTA}/`;
let ok = 0; const falhas = [];
const confere = (c, msg) => { if (c) ok++; else { falhas.push(msg); console.log("  FALHOU:", msg); } };
const COZ = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "obras.json"), "utf-8")).ambientes.find(a => a.id === "cozinhas");
const NCOZ = COZ.fotos.length + (COZ.video ? 1 : 0);   // itens da galeria de cozinhas; o vídeo é o último

(async () => {
  const servidor = spawn("python3", ["-m", "http.server", PORTA], { cwd: PUB, stdio: "ignore" });
  await new Promise(r => setTimeout(r, 900));
  const b = await chromium.launch();
  try {
    for (const [nome, op] of [["computador", { viewport: { width: 1440, height: 900 } }], ["pixel-7", devices["Pixel 7"]]]) {
      console.log("== " + nome);
      const ctx = await b.newContext(op); const p = await ctx.newPage();
      const erros = [], quebrados = [];
      p.on("pageerror", e => erros.push(String(e)));
      p.on("response", r => { if (r.status() >= 400 && r.url().startsWith(URL0)) quebrados.push(r.url() + " " + r.status()); });
      await p.addInitScript(() => { window.__abriu = []; HTMLAnchorElement.prototype.click = function(){ window.__abriu.push(this.href); }; });
      await p.goto(URL0); await p.waitForTimeout(700);
      if (await p.isVisible("#lgpd-ok")) await p.click("#lgpd-ok");
      const ini = await p.evaluate(() => ({ modo: document.documentElement.dataset.modo, t: document.title,
        robots: document.querySelector('meta[name="robots"]').content, canon: document.querySelector('link[rel="canonical"]').href,
        hash: document.querySelectorAll('a[href^="#/"]').length, capa: document.querySelector(".capa-foto img").currentSrc }));
      confere(ini.modo === "dominio" && /^Marcenaria em São Paulo/.test(ini.t), `capa no modo domínio com o título certo (${ini.t})`);
      confere(ini.hash === 0 && ini.canon === "https://marceneirotatuape.com.br/", "links por caminho e canônico do domínio");
      confere(/^http:\/\/localhost:\d+\/fotos\/capa-(720|1350)\.webp$/.test(ini.capa), `foto da capa a partir da raiz (${ini.capa})`);
      const ficha = await p.evaluate(() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => JSON.parse(s.textContent)).find(j => j.address));
      confere(ficha && ficha.address.postalCode === "03306-080" && ficha.geo && /cid=/.test(ficha.hasMap || ""), "ficha do Google com CEP, ponto no mapa e perfil");
      await p.evaluate(() => document.querySelector("#avaliacoes").scrollIntoView()); await p.waitForTimeout(400);
      const mapa = await p.evaluate(() => { const f = document.querySelector("#mapa-google iframe"); return f && f.src; });
      confere(mapa && /output=embed/.test(mapa) && /03306-080/.test(decodeURIComponent(mapa)), "no domínio, o mapa do Google entra com o endereço do perfil");
      // galeria funciona com os caminhos da raiz, inclusive numa página interna
      await p.goto(URL0 + "projetos/"); await p.waitForTimeout(600);
      await p.click('#galeria .proj-foto[data-album="cozinhas"]'); await p.waitForTimeout(500);
      const g = await p.evaluate(() => { const i = document.querySelector("#album-midia img"); return { src: i.currentSrc || i.src, ok: i.complete && i.naturalWidth > 0, conta: document.getElementById("album-conta").textContent }; });
      confere(g.ok && /^http:\/\/localhost:\d+\/fotos\/obras\//.test(g.src) && g.conta === `1 de ${NCOZ}`, `galeria em /projetos/ carrega da raiz (${g.src})`);
      for (let k = 0; k < NCOZ - 1; k++) { await p.keyboard.press("ArrowRight"); await p.waitForTimeout(120); }
      const v = await p.evaluate(() => { const v = document.querySelector("#album-midia video"); return v && v.querySelector("source").src; });
      confere(v && /\/fotos\/obras\/tour-sala-cozinha-madeira\.mp4$/.test(v), "o vídeo aponta para a raiz");
      const mp4 = await p.evaluate(async u => (await fetch(u)).status, v || URL0);
      confere(mp4 === 200, `o vídeo existe no servidor (${mp4})`);
      await p.keyboard.press("Escape");
      // todas as fotos de obra estão publicadas
      const IDS = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "obras.json"), "utf-8")).ambientes.flatMap(a => a.fotos.map(f => f.id));
      const faltando = await p.evaluate(async ids => {
        const r = await Promise.all(ids.flatMap(id => ["", "-640"].map(s => fetch("/fotos/obras/" + id + s + ".webp").then(x => x.ok ? null : id + s))));
        return { total: ids.length, faltando: r.filter(Boolean) };
      }, IDS);
      confere(faltando.total === IDS.length && IDS.length >= 34 && !faltando.faltando.length, `as ${IDS.length} fotos de obra publicadas nas duas larguras (${faltando.faltando.join(", ")})`);
      // pedido pelo WhatsApp no carrinho
      await p.goto(URL0 + "loja/"); await p.waitForTimeout(500);
      await p.click(".rota.on .prod"); await p.waitForTimeout(300); await p.click("#add-cesta"); await p.waitForTimeout(400);
      await p.click("#pedir-zap"); await p.waitForTimeout(200);
      const pedido = decodeURIComponent(await p.evaluate(() => window.__abriu.pop() || ""));
      confere(/^https:\/\/wa\.me\/5511947523961\?text=Olá! Montei este pedido/.test(pedido) && /Subtotal: R\$/.test(pedido), "o carrinho pede pelo WhatsApp com peça e subtotal");
      // endereço antigo
      await p.goto(URL0 + "portfolio/"); await p.waitForTimeout(700);
      confere(new URL(p.url()).pathname === "/projetos/", "/portfolio/ do site antigo leva a /projetos/");
      confere(!quebrados.length, `nenhum arquivo quebrado ${quebrados.join(" ")}`);
      confere(!erros.length, `nenhum erro de JavaScript ${erros.join(" | ")}`);
      await ctx.close();
    }
    const sm = fs.readFileSync(path.join(PUB, "sitemap.xml"), "utf-8");
    confere((sm.match(/<loc>/g) || []).length === 6 && !/sob-medida|checkout|portfolio/.test(sm), "sitemap com as 6 páginas");
    const idx = fs.readFileSync(path.join(PUB, "index.html"), "utf-8");
    const ld = JSON.parse(idx.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)[1]);
    confere(ld.address.streetAddress === "Rua Elisiário, 143 - Tatuapé" && ld.knowsAbout.includes("Móveis planejados"), "ficha do Google com endereço e o que a marcenaria faz");
    confere(!/capa-2400/.test(idx), "nada aponta para a capa de 2400 px que não existe mais");
  } finally {
    await b.close(); servidor.kill();
  }
  console.log(`\n${ok} conferências passaram, ${falhas.length} falharam`);
  process.exit(falhas.length ? 1 : 0);
})();
