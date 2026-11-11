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

// quantos itens tem a galeria de cozinhas (fotos e o tour em vídeo), lido da curadoria
const COZ = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "obras.json"), "utf-8")).ambientes.find(a => a.id === "cozinhas");
const NCOZ = COZ.fotos.length + (COZ.video ? 1 : 0);

// a entrada suave não pode deixar nada invisível: desce a tela inteira e conta o que ficou com opacidade zero
async function semEscondido(p) {
  await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 450) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); } });
  await p.waitForTimeout(1200);
  const n = await p.evaluate(() => [...document.querySelectorAll(".rota.on .revela")].filter(e => e.offsetParent !== null && getComputedStyle(e).opacity === "0").length);
  await p.evaluate(() => window.scrollTo(0, 0));
  return n;
}

// a capa nunca aparece maior do que tem pixel: px do arquivo por px da tela
async function nitidez(p) {
  return p.evaluate(() => {
    const i = document.querySelector(".capa-foto img"), r = i.getBoundingClientRect(), f = document.querySelector(".capa-fundo");
    const arq = +(i.currentSrc.match(/capa-(\d+)\.webp/) || [0, 0])[1], alto = Math.round(arq * 2395 / 1350);
    const mostrada = Math.max(r.width, r.height * arq / alto);
    return { arq, razao: +(arq / (mostrada * devicePixelRatio)).toFixed(2), fundo: f.complete && f.naturalWidth > 0 };
  });
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
  const capa = await p.$eval(".capa-foto img", i => ({ ok: i.complete && i.naturalWidth > 0, src: i.currentSrc, alt: i.alt }));
  confere(capa.ok && /capa-(720|1350)\.webp/.test(capa.src) && /^Cozinha planejada em madeira/.test(capa.alt), `capa com a foto real (${capa.src})`);
  const nt = await nitidez(p);
  confere(nt.razao >= 0.9 && nt.fundo, `capa sem pixelar no computador (${nt.arq} px, ${nt.razao} px por px) e com o fundo esfumaçado`);
  confere(!/ilustrativ/i.test(await p.$eval(".capa-legenda", e => e.innerText)), "legenda da capa sem 3D ilustrativo");

  // o filme: logo depois da capa, só baixa no play, e os arquivos existem
  const filme = await p.evaluate(() => { const v = document.querySelector("#filme-video"), ids = [...document.querySelectorAll('[data-rota="inicio"] [id]')].map(e => e.id);
    return { preload: v.preload, poster: v.getAttribute("poster"), src: v.querySelector("source").getAttribute("src"), botao: !!document.querySelector("#filme-play"),
      ordem: ids.indexOf("filme") >= 0 && ids.indexOf("filme") < ids.indexOf("mosaico") && ids.indexOf("mosaico") < ids.indexOf("destaques"),
      zap: decodeURIComponent(document.querySelector('[data-zap="filme"]').href), texto: document.querySelector(".filme-texto p").textContent.length }; });
  confere(filme.preload === "none" && filme.botao && /filme-capa\.webp$/.test(filme.poster) && /casa-do-marceneiro\.mp4$/.test(filme.src), "o filme só carrega no play e tem imagem de capa");
  confere(filme.ordem, "página inicial: o filme, depois as fotos reais dos ambientes, depois a loja");
  confere(/vi o filme/.test(filme.zap) && filme.texto > 200, "o pedido que sai do filme diz que a pessoa viu o filme, e o texto do filme está na página");
  const PASTA = path.dirname(ARQ.replace("file://", ""));
  confere(["filme-capa.webp", "casa-do-marceneiro.mp4"].every(a => fs.existsSync(path.join(PASTA, "fotos", "filme", a))), "os arquivos do filme estão ao lado da página");
  confere(await semEscondido(p) === 0, "entrada suave: depois de rolar a página inicial, nenhum bloco fica invisível");

  // mapa e rotas: o ponto exato do perfil da oficina no Maps, e um cartão onde o Google não pode entrar
  const rotas = await p.evaluate(() => {
    const as = [...document.querySelectorAll("a[data-rota]")].map(a => a.href);
    return { google: as.filter(h => /google\.com\/maps\/dir/.test(h)), waze: as.filter(h => /waze\.com/.test(h)),
      ver: document.querySelector("#ver-avaliacoes").href, cep: (document.body.textContent.match(/03306-080/g) || []).length };
  });
  confere(rotas.google.length >= 2 && rotas.google.every(h => h.includes("0x94ce5fc88811b433:0xe7eb758b02ec9ff1")), `rota do Google até o perfil exato da oficina (${rotas.google.length} botões)`);
  confere(rotas.waze.length >= 2 && rotas.waze.every(h => h.includes("ll=-23.5483874")), `Waze com o ponto exato (${rotas.waze.length} botões)`);
  confere(/cid=16711580082198323185/.test(rotas.ver), "ver as avaliações abre o perfil da oficina, não uma busca");
  confere(rotas.cep >= 5, `CEP 03306-080 em todo endereço (${rotas.cep})`);
  await p.evaluate(() => document.querySelector("#avaliacoes").scrollIntoView()); await p.waitForTimeout(500);
  const fora = await p.$eval("#mapa-google", m => { const f = m.querySelector("iframe"); return f && f.src; });
  confere(fora && /output=embed/.test(fora) && /03306-080/.test(decodeURIComponent(fora)), "fora de moldura, o mapa do Google entra com o endereço do perfil");
  const MOLD = path.join(CAP, "moldura.html");
  fs.writeFileSync(MOLD, `<!doctype html><meta charset="utf-8"><iframe src="${ARQ}" style="width:1200px;height:800px;border:0"></iframe>`);
  const pm = await ctx.newPage(); await pm.goto("file://" + MOLD); await pm.waitForTimeout(700);
  const fm = pm.frames()[1];
  await fm.evaluate(() => document.querySelector("#avaliacoes").scrollIntoView()); await pm.waitForTimeout(500);
  const dentro = await fm.$eval("#mapa-google", m => ({ sem: m.classList.contains("sem-mapa"), iframe: !!m.querySelector("iframe"), cartao: getComputedStyle(m.querySelector(".mapa-reserva")).display !== "none" }));
  confere(dentro.sem && !dentro.iframe && dentro.cartao, "dentro de moldura (como no visor da prévia), o cartão da oficina no lugar da tela de bloqueio");
  await pm.close();

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

  // projetos concluídos: nove álbuns de fotos reais (seis ambientes, camas, comercial e CasaCor)
  await ir(p, "projetos");
  const cartoes = await p.$$eval("#galeria .proj", cs => cs.map(c => ({ t: c.querySelector("h4").textContent, onde: c.querySelector(".onde").textContent, selo3d: !!c.querySelector(".selo3d") })));
  confere(cartoes.length === 9 && ["Cama sob medida", "Projetos comerciais", "CasaCor"].every(n => cartoes.some(c => c.t === n)) && cartoes.every(c => /fotos reais/.test(c.onde) && !c.selo3d), `nove álbuns de fotos reais (${cartoes.map(c => c.t).join(", ")})`);
  confere(!/ilustrativ|Vila Formosa|Anália Franco|22 dias|m lineares/.test(await p.$eval('[data-rota="projetos"]', e => e.innerText)), "nada dos projetos de exemplo (bairro, prazo, metragem)");
  const imgsProj = await carregarImagens(p);
  confere(imgsProj.length >= 6 && imgsProj.every(i => i.ok), `projetos: ${imgsProj.filter(i => i.ok).length}/${imgsProj.length} imagens`);
  await p.screenshot({ path: `${CAP}/computador-projetos.png` });

  // galeria: setas, teclado, miniatura, vídeo, pedido
  await p.click('#galeria .proj-foto[data-album="cozinhas"]'); await p.waitForTimeout(500);
  const g0 = await p.evaluate(() => ({ conta: document.getElementById("album-conta").textContent, mini: document.querySelectorAll("#album-miniaturas button").length, img: (() => { const i = document.querySelector("#album-midia img"); return i && i.complete && i.naturalWidth > 0; })() }));
  confere(g0.conta === `1 de ${NCOZ}` && g0.mini === NCOZ && g0.img, `galeria de cozinhas abre na 1 de ${NCOZ}, com ${NCOZ} miniaturas e a foto carregada (${g0.conta})`);
  await p.click(".album-seta.prox"); await p.waitForTimeout(200);
  await p.keyboard.press("ArrowRight"); await p.waitForTimeout(200);
  confere(await p.$eval("#album-conta", e => e.textContent) === `3 de ${NCOZ}`, "seta e teclado avançam");
  await p.keyboard.press("ArrowLeft"); await p.keyboard.press("ArrowLeft"); await p.keyboard.press("ArrowLeft"); await p.waitForTimeout(200);
  confere(await p.$eval("#album-conta", e => e.textContent) === `${NCOZ} de ${NCOZ}`, "volta da primeira para a última");
  const video = await p.evaluate(() => { const v = document.querySelector("#album-midia video"); return v && { preload: v.preload, src: v.querySelector("source").getAttribute("src"), poster: v.poster }; });
  confere(video && video.preload === "none" && /tour-sala-cozinha-madeira\.mp4$/.test(video.src) && /-capa\.webp$/.test(video.poster), "o tour em vídeo só carrega no play");
  await p.click('#album-miniaturas [data-album-ir="3"]'); await p.waitForTimeout(200);
  confere(await p.$eval("#album-conta", e => e.textContent) === `4 de ${NCOZ}` && await p.$eval('#album-miniaturas [data-album-ir="3"]', b => b.getAttribute("aria-current")) === "true", "miniatura leva à foto e fica marcada");
  const zapAlbum = await p.$eval("#album-zap", a => decodeURIComponent(a.href));
  confere(/^https:\/\/wa\.me\/5511947523961\?text=Olá! Vi as fotos de cozinhas planejadas .* cozinha planejada\.$/.test(zapAlbum), "o pedido da galeria diz qual ambiente a pessoa viu");
  await p.screenshot({ path: `${CAP}/computador-galeria.png` });
  await p.click(".album-topo .xis"); await p.waitForTimeout(200);
  confere(await p.$eval("#album", e => e.hidden), "o × fecha a galeria");

  // loja e pedido pelo WhatsApp continuam
  await ir(p, "loja");
  const pecas = await p.$$eval("#vitrine .prod h4", h => h.map(x => x.textContent));
  confere(pecas.length === 9 && pecas.includes("Aparador") && !pecas.some(n => /Banqueta|Corte de chapa/.test(n)), `loja com as nove peças (${pecas.length})`);
  // pedido de 10/11: loja sem valor, com aviso de imagem ilustrativa, e a peça vira mensagem
  const loja = await p.$eval('[data-rota="loja"]', e => e.innerText);
  confere(!/R\$|sem juros|carrinho/i.test(loja) && /Imagens ilustrativas/.test(loja) && /Valor sob medida/.test(loja), "loja sem valores, com aviso de imagens ilustrativas");
  confere(await p.$eval("#abre-cart", e => getComputedStyle(e).display === "none"), "carrinho fora do ar");
  await p.click('#vitrine .prod'); await p.waitForTimeout(250);
  const fichaTxt = await p.$eval("#ficha-g", e => e.innerText);
  confere(!/R\$|sem juros|Adicionar ao carrinho/i.test(fichaTxt) && /Receber o valor no WhatsApp/i.test(fichaTxt), "a ficha da peça pede o valor pelo WhatsApp");
  await p.evaluate(() => { window.__abriu = []; window.open = u => { window.__abriu.push(String(u)); return null; }; });
  await p.click("#pedir-valor"); await p.waitForTimeout(250);
  const pedido = decodeURIComponent((await p.evaluate(() => window.__abriu.join(" "))) || "");
  confere(/wa\.me\/5511947523961/.test(pedido) && /Qual o valor e o prazo\?/.test(pedido) && /Madeira: /.test(pedido), `o pedido de valor sai pronto no WhatsApp (${pedido.slice(-70)})`);
  await p.keyboard.press("Escape"); await p.waitForTimeout(200);

  // capa com a mensagem do site antigo, sem 1980 e sem MDP em lugar nenhum; e-mail do Gabriel
  const tudoHtml = await p.evaluate(() => document.body.textContent + " " + [...document.querySelectorAll("a[href^=mailto], meta[content], script[type='application/ld+json']")].map(e => e.outerHTML).join(" "));
  confere(!/\b1980\b|\bMDP\b|contato@marceneirotatuape/i.test(tudoHtml), "nada de 1980, MDP ou do e-mail antigo no site");
  confere((tudoHtml.match(/gabriellandiw@hotmail\.com/g) || []).length >= 4, "e-mail gabriellandiw@hotmail.com no lugar do antigo");
  await ir(p, "inicio");
  confere(/há mais de 25 anos/.test(await p.$eval(".capa-txt .sub", e => e.textContent)) && /\+25 anos/.test(await p.$eval(".capa .provas", e => e.textContent)), "capa: há mais de 25 anos no mercado");
  const com = await p.$eval("#comercial", e => ({ t: e.innerText, fotos: e.querySelectorAll("#comercial-fotos .tela img").length }));
  confere(/para empresas/i.test(com.t) && /Orçamento para minha empresa/i.test(com.t) && com.fotos === 3, "área comercial na página inicial, com três fotos e orçamento para empresa");
  await p.click('#comercial [data-album="comercial"].btn'); await p.waitForTimeout(300);
  confere(await p.$eval("#album", e => !e.hidden) && /Projetos comerciais/.test(await p.$eval("#album-titulo", e => e.textContent)), "o botão da área comercial abre o álbum");
  await p.keyboard.press("Escape"); await p.waitForTimeout(200);
  const esp = await p.$$eval("#especiais .tela .leg b", bs => bs.map(b => b.textContent));
  confere(esp.join("|") === "Cama sob medida|CasaCor", `especialidades: ${esp.join(", ")}`);
  await p.click('#especiais [data-album="casacor"]'); await p.waitForTimeout(300);
  confere(/CasaCor/.test(await p.$eval("#album-titulo", e => e.textContent)) && /5$/.test(await p.$eval("#album-conta", e => e.textContent)), "CasaCor abre com as cinco fotos");
  await p.keyboard.press("Escape"); await p.waitForTimeout(200);

  // contato: só WhatsApp
  await ir(p, "contato");
  const bts = await p.$$eval('#form-contato button[type="submit"]', bs => bs.map(b => b.textContent.trim()));
  confere(bts.length === 1 && /WhatsApp/.test(bts[0]), `contato só pelo WhatsApp (${bts.join(", ")})`);
  confere(p.erros.length === 0, `computador sem erro de JavaScript ${p.erros.join(" | ")}`);
  await ctx.close();

  // ------------------------------------------------------------ celulares
  const APARELHOS = { "iphone-se": devices["iPhone SE"], "iphone-13": devices["iPhone 13"], "pixel-7": devices["Pixel 7"],
    "galaxy-s9": devices["Galaxy S9+"], "galaxy-320": { ...devices["Galaxy S5"], viewport: { width: 320, height: 640 } },
    "ipad-mini": devices["iPad Mini"], "moto-g4": devices["Moto G4"] };
  for (const [nome, op] of Object.entries(APARELHOS)) {
    console.log("== " + nome);
    ({ ctx, p } = await abrir(b, op));
    await ir(p, "");
    const ntc = await nitidez(p);
    confere(await semEscondido(p) === 0, `${nome}: entrada suave sem bloco invisível`);
    const fq = await p.evaluate(() => { const r = document.querySelector(".filme-tela").getBoundingClientRect(); return { larg: Math.round(r.width), alt: Math.round(r.height), tela: innerHeight }; });
    confere(fq.larg >= 230 && fq.alt <= fq.tela, `${nome}: o filme cabe na tela (${fq.larg} × ${fq.alt} em ${fq.tela})`);
    confere(ntc.razao >= 0.9 && ntc.fundo, `${nome}: capa sem pixelar (${ntc.arq} px, ${ntc.razao} px por px)`);
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
