// Conferência de ponta a ponta da prévia (index.html), no computador e em sete celulares.
//   NODE_PATH=$(npm root -g) node testes/site.js [index.html] [pasta de capturas]
const { chromium, devices } = require("playwright");
const fs = require("fs"), path = require("path");
const ARQ = "file://" + path.resolve(process.argv[2] || path.join(__dirname, "..", "index.html"));
const CAP = process.argv[3] || path.join(require("os").tmpdir(), "capturas-site");
fs.mkdirSync(CAP, { recursive: true });
let ok = 0; const falhas = [];
const confere = (c, msg) => { if (c) ok++; else { falhas.push(msg); console.log("  FALHOU:", msg); } };
const RUIDO = /maps\.google|googletagmanager|facebook|ERR_TUNNEL|ERR_NAME|ERR_INTERNET|net::ERR/;

async function abrir(b, op) {
  const ctx = await b.newContext(op);
  const p = await ctx.newPage();
  p.erros = [];
  p.on("pageerror", e => p.erros.push(String(e)));
  p.on("console", m => { if (m.type() === "error" && !RUIDO.test(m.text())) p.erros.push(m.text()); });
  await p.addInitScript(() => { window.__abriu = []; HTMLAnchorElement.prototype.click = function(){ window.__abriu.push(this.href); }; });
  await p.goto(ARQ); await p.waitForTimeout(600);
  if (await p.isVisible("#lgpd-ok")) await p.click("#lgpd-ok");
  return { ctx, p };
}
const ir = (p, r) => p.evaluate(rt => { location.hash = "#/" + rt; }, r).then(() => p.waitForTimeout(300));
async function carregarImagens(p) {
  await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
  await p.waitForTimeout(500);
  return p.$$eval(".rota.on img", is => is.filter(i => i.offsetParent !== null).map(i => ({ src: i.currentSrc || i.src, ok: i.complete && i.naturalWidth > 0 })));
}

(async () => {
  const b = await chromium.launch();

  // ------------------------------------------------------------ computador
  console.log("== computador");
  let { ctx, p } = await abrir(b, { viewport: { width: 1440, height: 900 } });
  const tudo = await p.evaluate(() => [...document.querySelectorAll(".rota, .topo, .rodape")].map(e => e.textContent).join(" "));
  const html = await p.content();
  confere(/Rua Elisiário, 143/.test(tudo) && !/Tuiuti|2530/.test(html), "endereço novo, nada do antigo");
  const zaps = await p.$$eval('a[href*="wa.me"]', as => as.map(a => a.href));
  confere(zaps.length >= 15 && zaps.every(h => h.startsWith("https://wa.me/5511947523961")), `todo WhatsApp vai para (11) 94752-3961 (${zaps.length})`);
  confere(!(await p.$('[data-rota="sob-medida"]')) && !(await p.$('a[href*="sob-medida"]')), "simulador guardado: sem tela e sem link");
  confere(/^Móveis sob medida/.test(await p.$eval(".capa h1", h => h.textContent)), "título da capa com a palavra-chave");

  // capa com foto real, sem selo de 3D
  const capa = await p.$eval(".capa-foto img", i => ({ ok: i.complete && i.naturalWidth >= 960, src: i.currentSrc, alt: i.alt }));
  confere(capa.ok && /capa-(960|1600)\.webp/.test(capa.src) && /painel de TV/.test(capa.alt), `capa com a foto real (${capa.src})`);
  confere(!/ilustrativ/i.test(await p.$eval(".capa-legenda", e => e.innerText)), "legenda da capa sem 3D ilustrativo");

  // ambientes com foto real e os dois botões
  const amb = await p.$$eval("#ambientes .balcao", cs => cs.map(c => ({ img: !!c.querySelector(".ft img"), zap: c.querySelector("[data-zap]").dataset.msg, album: c.querySelector("[data-album]") && c.querySelector("[data-album]").dataset.album })));
  confere(amb.length === 6 && amb.every(a => a.img && /^Olá! .*orçamento de .+\.$/.test(a.zap) && a.album), "seis ambientes, cada um com foto, pedido de orçamento e ver fotos");
  const imgsInicio = await carregarImagens(p);
  confere(imgsInicio.length >= 15 && imgsInicio.every(i => i.ok), `início: ${imgsInicio.filter(i => i.ok).length}/${imgsInicio.length} imagens carregadas`);

  // mosaico abre a galeria já na foto clicada
  await p.$eval("#mosaico", e => e.scrollIntoView());
  await p.click("#mosaico .tela.grande"); await p.waitForTimeout(400);
  const doMosaico = await p.evaluate(() => ({ aberto: !document.getElementById("album").hidden, titulo: document.getElementById("album-titulo").textContent, leg: document.getElementById("album-legenda").textContent }));
  confere(doMosaico.aberto && /Salas/.test(doMosaico.titulo) && /jantar/.test(doMosaico.leg), `o mosaico abre a galeria na foto certa (${doMosaico.titulo}: ${doMosaico.leg.slice(0, 40)})`);
  await p.keyboard.press("Escape"); await p.waitForTimeout(200);
  confere(await p.$eval("#album", e => e.hidden) && await p.evaluate(() => document.body.style.overflow === ""), "Esc fecha a galeria e devolve a rolagem");

  // projetos concluídos: seis ambientes de fotos reais
  await ir(p, "projetos");
  const cartoes = await p.$$eval("#galeria .proj", cs => cs.map(c => ({ t: c.querySelector("h4").textContent, onde: c.querySelector(".onde").textContent, selo3d: !!c.querySelector(".selo3d") })));
  confere(cartoes.length === 6 && cartoes.every(c => /fotos reais/.test(c.onde) && !c.selo3d), `seis ambientes de fotos reais (${cartoes.map(c => c.t).join(", ")})`);
  confere(!/ilustrativ|Vila Formosa|Anália Franco|22 dias|m lineares/.test(await p.$eval('[data-rota="projetos"]', e => e.innerText)), "nada dos projetos de exemplo (bairro, prazo, metragem)");
  const imgsProj = await carregarImagens(p);
  confere(imgsProj.length >= 6 && imgsProj.every(i => i.ok), `projetos: ${imgsProj.filter(i => i.ok).length}/${imgsProj.length} imagens`);
  await p.screenshot({ path: `${CAP}/computador-projetos.png` });

  // galeria: setas, teclado, miniatura, vídeo, pedido
  await p.click('#galeria .proj-foto[data-album="cozinhas"]'); await p.waitForTimeout(500);
  const g0 = await p.evaluate(() => ({ conta: document.getElementById("album-conta").textContent, mini: document.querySelectorAll("#album-miniaturas button").length, img: (() => { const i = document.querySelector("#album-midia img"); return i && i.complete && i.naturalWidth > 0; })() }));
  confere(g0.conta === "1 de 9" && g0.mini === 9 && g0.img, `galeria de cozinhas abre na 1 de 9, com 9 miniaturas e a foto carregada (${g0.conta})`);
  await p.click(".album-seta.prox"); await p.waitForTimeout(200);
  await p.keyboard.press("ArrowRight"); await p.waitForTimeout(200);
  confere(await p.$eval("#album-conta", e => e.textContent) === "3 de 9", "seta e teclado avançam");
  await p.keyboard.press("ArrowLeft"); await p.keyboard.press("ArrowLeft"); await p.keyboard.press("ArrowLeft"); await p.waitForTimeout(200);
  confere(await p.$eval("#album-conta", e => e.textContent) === "9 de 9", "volta da primeira para a última");
  const video = await p.evaluate(() => { const v = document.querySelector("#album-midia video"); return v && { preload: v.preload, src: v.querySelector("source").getAttribute("src"), poster: v.poster }; });
  confere(video && video.preload === "none" && /tour-sala-cozinha-madeira\.mp4$/.test(video.src) && /-capa\.webp$/.test(video.poster), "o tour em vídeo só carrega no play");
  await p.click('#album-miniaturas [data-album-ir="3"]'); await p.waitForTimeout(200);
  confere(await p.$eval("#album-conta", e => e.textContent) === "4 de 9" && await p.$eval('#album-miniaturas [data-album-ir="3"]', b => b.getAttribute("aria-current")) === "true", "miniatura leva à foto e fica marcada");
  const zapAlbum = await p.$eval("#album-zap", a => decodeURIComponent(a.href));
  confere(/^https:\/\/wa\.me\/5511947523961\?text=Olá! Vi as fotos de cozinhas planejadas .* cozinha planejada\.$/.test(zapAlbum), "o pedido da galeria diz qual ambiente a pessoa viu");
  await p.screenshot({ path: `${CAP}/computador-galeria.png` });
  await p.click(".album-topo .xis"); await p.waitForTimeout(200);
  confere(await p.$eval("#album", e => e.hidden), "o × fecha a galeria");

  // loja e pedido pelo WhatsApp continuam
  await ir(p, "loja");
  const pecas = await p.$$eval("#vitrine .prod h4", h => h.map(x => x.textContent));
  confere(pecas.length === 9 && pecas.includes("Aparador") && !pecas.some(n => /Banqueta|Corte de chapa/.test(n)), `loja com as nove peças (${pecas.length})`);
  confere(p.erros.length === 0, `computador sem erro de JavaScript ${p.erros.join(" | ")}`);
  await ctx.close();

  // ------------------------------------------------------------ celulares
  const APARELHOS = { "iphone-se": devices["iPhone SE"], "iphone-13": devices["iPhone 13"], "pixel-7": devices["Pixel 7"],
    "galaxy-s9": devices["Galaxy S9+"], "galaxy-320": { ...devices["Galaxy S5"], viewport: { width: 320, height: 640 } },
    "ipad-mini": devices["iPad Mini"], "moto-g4": devices["Moto G4"] };
  for (const [nome, op] of Object.entries(APARELHOS)) {
    console.log("== " + nome);
    ({ ctx, p } = await abrir(b, op));
    for (const r of ["", "loja", "projetos", "oficina", "contato", "politicas"]) {
      await ir(p, r);
      const larg = await p.evaluate(() => ({ doc: document.documentElement.scrollWidth, tela: document.documentElement.clientWidth }));
      confere(larg.doc <= larg.tela + 1, `${nome} /${r}: sem rolagem para o lado (${larg.doc} > ${larg.tela})`);
    }
    await ir(p, "projetos");
    await p.click('#galeria .proj-foto[data-album="dormitorios"]'); await p.waitForTimeout(400);
    const caixa = await p.evaluate(() => { const m = document.querySelector("#album-midia img").getBoundingClientRect(); const z = document.getElementById("album-zap").getBoundingClientRect(); return { cabe: m.width <= innerWidth && m.bottom <= innerHeight, zap: z.bottom <= innerHeight + 1 && z.width > 0 }; });
    confere(caixa.cabe && caixa.zap, `${nome}: a foto cabe na tela e o botão de orçamento aparece`);
    const ini = await p.$eval("#album-conta", e => e.textContent);
    const box = await (await p.$("#album-midia")).boundingBox();
    await p.evaluate(({ x, y }) => {
      const el = document.getElementById("album-midia");
      const t = (cx) => [{ identifier: 1, target: el, clientX: cx, clientY: y }];
      el.dispatchEvent(Object.assign(new Event("touchstart"), { touches: t(x + 200), changedTouches: t(x + 200) }));
      el.dispatchEvent(Object.assign(new Event("touchend"), { touches: [], changedTouches: t(x) }));
    }, { x: box.x + 20, y: box.y + 50 });
    await p.waitForTimeout(200);
    confere(ini === "1 de 9" && await p.$eval("#album-conta", e => e.textContent) === "2 de 9", `${nome}: arrastar para o lado passa a foto`);
    if (nome === "iphone-13") await p.screenshot({ path: `${CAP}/celular-galeria.png` });
    await p.click(".album-topo .xis");
    confere(p.erros.length === 0, `${nome}: sem erro de JavaScript ${p.erros.join(" | ")}`);
    await ctx.close();
  }

  await b.close();
  console.log(`\n${ok} conferências passaram, ${falhas.length} falharam`);
  process.exit(falhas.length ? 1 : 0);
})();
