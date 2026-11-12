(function(){
  "use strict";

  /* ============================================================
     O estado mora no próprio documento, num bloco JSON. Quando
     alguém marca um item, o documento é remontado com o estado
     novo e republicado — a página é o registro. Sem o Artifact
     (arquivo solto no celular, ou visitante sem permissão de
     escrita) cai para o armazenamento do navegador.
     ============================================================ */

  var CHAVE = "cmt-quadro-v1";
  var elEstado = document.getElementById("estado");
  if (!elEstado || !document.getElementById("quadro")) return;

  var estado = JSON.parse(elEstado.textContent);
  var canal = null;          /* namespace do Artifact, quando houver */
  var somenteLeitura = false;
  var pendente = null;

  /* sobreposição local: só vale quando não há publicação */
  try {
    var salvo = localStorage.getItem(CHAVE);
    if (salvo) {
      var over = JSON.parse(salvo);
      if (over && over.versao === estado.versao) aplicarSobreposicao(over);
    }
  } catch (e) {}

  function aplicarSobreposicao(over){
    (estado.roteiro || []).forEach(function(p){
      if (over.roteiro && Object.prototype.hasOwnProperty.call(over.roteiro, p.id)) p.feito = !!over.roteiro[p.id];
    });
    (estado.itens || []).forEach(function(i){
      if (over.itens && over.itens[i.id]) i.estado = over.itens[i.id];
    });
    lugares().forEach(function(l){
      if (over.fotos && over.fotos[l.id]) l.estado = over.fotos[l.id];
    });
    passosSubida().forEach(function(x){
      if (over.subida && Object.prototype.hasOwnProperty.call(over.subida, x.id)) x.feito = !!over.subida[x.id];
    });
    parcelas().forEach(function(p){
      if (over.parcelas && Object.prototype.hasOwnProperty.call(over.parcelas, p.id)) p.pago = !!over.parcelas[p.id];
    });
  }

  function guardarLocal(){
    var over = { versao:estado.versao, roteiro:{}, itens:{}, fotos:{}, parcelas:{}, subida:{} };
    (estado.roteiro || []).forEach(function(p){ over.roteiro[p.id] = !!p.feito; });
    (estado.itens || []).forEach(function(i){ over.itens[i.id] = i.estado; });
    lugares().forEach(function(l){ over.fotos[l.id] = l.estado; });
    parcelas().forEach(function(p){ over.parcelas[p.id] = !!p.pago; });
    passosSubida().forEach(function(x){ over.subida[x.id] = !!x.feito; });
    try { localStorage.setItem(CHAVE, JSON.stringify(over)); } catch (e) {}
  }

  /* As seções novas são opcionais no estado: o financeiro só existe no
     artifact privado (ver montar.py), e uma versão antiga do documento
     pode não ter fotos. Nada aqui pode quebrar por falta delas. */
  function lugares(){ return (estado.fotos && estado.fotos.lugares) || []; }
  function parcelas(){ return (estado.financeiro && estado.financeiro.linhas) || []; }
  function passosSubida(){ return (estado.subida && estado.subida.passos) || []; }

  /* ---------- ferramentas ---------- */
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]; }); }
  function ic(id){ return '<svg viewBox="0 0 16 16" aria-hidden="true"><use href="#' + id + '"/></svg>'; }

  /* Data local, não UTC. new Date().toISOString() em São Paulo às 21h30
     já devolve o dia seguinte — e este quadro passou a comparar datas. */
  function hojeISO(){
    var d = new Date(), z = function(n){ return ("0" + n).slice(-2); };
    return d.getFullYear() + "-" + z(d.getMonth() + 1) + "-" + z(d.getDate());
  }
  function diaBr(iso){ var p = String(iso).split("-"); return p[2] + "/" + p[1]; }

  function torrada(txt, ruim){
    var caixa = document.getElementById("torradas");
    if (!caixa) return;
    var el = document.createElement("div");
    el.className = "torrada" + (ruim ? " ruim" : "");
    el.innerHTML = ic(ruim ? "q-alerta" : "q-check") + "<span>" + esc(txt) + "</span>";
    caixa.appendChild(el);
    setTimeout(function(){
      el.style.transition = "opacity .3s,transform .3s";
      el.style.opacity = "0"; el.style.transform = "translateY(8px)";
      setTimeout(function(){ if (el.parentNode) el.parentNode.removeChild(el); }, 320);
    }, 2800);
  }

  /* ---------- desenho ---------- */
  var COLUNAS = [
    { chave:"feito",   rot:"Feito",   cls:"col-feito" },
    { chave:"fazendo", rot:"Fazendo", cls:"col-fazendo" },
    { chave:"afazer",  rot:"A fazer", cls:"col-afazer" }
  ];

  /* O medidor conta só o quadro. Somar os passos de hoje aqui fazia a
     legenda dizer "Fazendo 19" ao lado de uma coluna com 8 — dois
     números para a mesma palavra na mesma tela. O roteiro tem contador
     próprio, no cabeçalho dele. */
  function contas(){
    var c = { feito:0, fazendo:0, afazer:0 };
    (estado.itens || []).forEach(function(i){ c[i.estado] = (c[i.estado] || 0) + 1; });
    c.total = c.feito + c.fazendo + c.afazer;
    return c;
  }

  function contaRoteiro(){
    var lista = estado.roteiro || [];
    var feitos = lista.filter(function(p){ return p.feito; }).length;
    return { feitos:feitos, total:lista.length };
  }

  /* O marco não guarda estado próprio: ele soma os cartões que carrega.
     Assim a linha do tempo não tem como discordar das colunas. */
  function estadoMarco(m){
    var mapa = {};
    (estado.itens || []).forEach(function(i){ mapa[i.id] = i.estado; });
    var feitos = 0, tocados = 0, total = 0;
    (m.itens || []).forEach(function(id){
      var e = mapa[id];
      if (!e) return;                       /* id que não existe mais não conta */
      total++;
      if (e === "feito") { feitos++; tocados++; }
      else if (e === "fazendo") tocados++;
    });
    return {
      estado: (total && feitos === total) ? "feito" : (tocados ? "fazendo" : "afazer"),
      feitos: feitos, total: total
    };
  }

  function linhaAgora(hoje){
    return '<li class="agora"><span class="pino" aria-hidden="true"><i></i></span>' +
      '<span class="txt">hoje · ' + esc(diaBr(hoje)) + '</span></li>';
  }

  function desenharMarcos(){
    var alvo = document.getElementById("marcos");
    if (!alvo) return;
    var lista = estado.marcos || [], hoje = hojeISO(), prontos = 0, html = "", k;

    /* a linha do "hoje" entra antes do primeiro marco que ainda está por vir;
       se todos já passaram, ela vai para o fim. Marco com a data de hoje que
       já está concluído fica do lado de trás da linha, não da frente. */
    var pos = -1;
    for (k = 0; k < lista.length; k++)
      if (lista[k].ate && lista[k].ate >= hoje && !(lista[k].ate === hoje && estadoMarco(lista[k]).estado === "feito")) { pos = k; break; }
    if (pos < 0) for (k = 0; k < lista.length; k++) if (!lista[k].ate) { pos = k; break; }
    if (pos < 0) pos = lista.length;

    lista.forEach(function(m, idx){
      if (idx === pos) html += linhaAgora(hoje);
      var c = estadoMarco(m);
      var atrasado = !!(m.ate && m.ate < hoje && c.estado !== "feito");
      if (c.estado === "feito") prontos++;
      html += '<li class="marco m-' + c.estado + (atrasado ? " atrasado" : "") + '">' +
        '<span class="no" aria-hidden="true">' +
          (c.estado === "feito" ? '<svg viewBox="0 0 16 16"><use href="#q-check"/></svg>' : (idx + 1)) +
        '</span>' +
        '<span class="corpo">' +
          '<span class="alto"><b>' + esc(m.rot) + '</b>' +
            '<span class="quando">' + esc(m.quando) + '</span>' +
            (m.antes ? '<span class="era">era ' + esc(m.antes) + '</span>' : '') +
            (atrasado ? '<span class="tarja">atrasado</span>' : '') +
          '</span>' +
          '<span class="entrega">' + esc(m.entrega) + '</span>' +
          '<span class="andamento">' +
            '<span class="tira"><i style="width:' + (c.total ? (c.feitos / c.total) * 100 : 0) + '%"></i></span>' +
            '<span class="frac">' + c.feitos + ' de ' + c.total + '</span>' +
          '</span>' +
        '</span></li>';
    });
    if (pos >= lista.length) html += linhaAgora(hoje);
    alvo.innerHTML = html;

    var cont = document.getElementById("conta-tempo");
    if (cont) cont.innerHTML = '<b>' + prontos + ' de ' + lista.length + '</b> marcos concluídos';
    var rp = document.getElementById("replano");
    if (rp) { rp.hidden = !estado.replanejado; rp.textContent = estado.replanejado || ""; }
  }

  function desenharMedidor(){
    var c = contas();
    var pct = c.total ? Math.round((c.feito / c.total) * 100) : 0;
    var alvo = document.getElementById("medidor");
    if (!alvo) return;
    alvo.innerHTML =
      '<div class="n">' + pct + '<small>%</small></div>' +
      '<div class="rot2">' + c.feito + ' de ' + c.total + ' concluídos</div>' +
      '<div class="barra" role="img" aria-label="' + pct + ' por cento concluído">' +
        '<i class="b-feito" style="width:' + (c.total ? (c.feito / c.total) * 100 : 0) + '%"></i>' +
        '<i class="b-fazendo" style="width:' + (c.total ? (c.fazendo / c.total) * 100 : 0) + '%"></i>' +
      '</div>' +
      '<div class="legenda">' +
        '<span><i style="background:var(--folha)"></i>Feito ' + c.feito + '</span>' +
        '<span><i style="background:var(--cera)"></i>Fazendo ' + c.fazendo + '</span>' +
        '<span><i style="background:var(--mut2)"></i>A fazer ' + c.afazer + '</span>' +
      '</div>';
  }

  function desenharRoteiro(){
    var alvo = document.getElementById("passos");
    if (!alvo) return;
    var rv = document.getElementById("rot-visita"), v = estado.visita, hj = hojeISO();
    if (rv) rv.textContent = !v ? "Na casa do Gabriel"
      : v === hj ? "Hoje · na casa do Gabriel"
      : v < hj ? "Visita de " + diaBr(v) + " · na casa do Gabriel"
      : "Em " + diaBr(v) + " · na casa do Gabriel";
    var r = contaRoteiro();
    var cont = document.getElementById("conta-hoje");
    if (cont) {
      cont.innerHTML = '<b>' + r.feitos + ' de ' + r.total + '</b> passos concluídos' +
        '<span class="barra-mini"><i style="width:' + (r.total ? (r.feitos / r.total) * 100 : 0) + '%"></i></span>';
    }
    alvo.innerHTML = listaDePassos(estado.roteiro || [], "data-passo");
  }

  function listaDePassos(lista, atributo){
    return lista.map(function(p, i){
      return '<li><button type="button" class="passo' + (p.feito ? " ok" : "") + '" ' + atributo + '="' + esc(p.id) + '"' +
        ' aria-pressed="' + (p.feito ? "true" : "false") + '">' +
        '<span class="n">' + (p.feito ? '<svg viewBox="0 0 16 16" aria-hidden="true"><use href="#q-check"/></svg>' : (i + 1)) + '</span>' +
        '<span class="txt"><b>' + esc(p.t) + '</b><span>' + esc(p.d) + '</span></span>' +
        '</button></li>';
    }).join("");
  }

  function desenharSubida(){
    var alvo = document.getElementById("subida-passos"), su = estado.subida;
    var sec = document.getElementById("s-subida");
    if (sec) sec.hidden = !su;
    if (!alvo || !su) return;
    texto("subida-intro", su.intro);
    var ps = passosSubida(), feitos = ps.filter(function(x){ return x.feito; }).length;
    var cont = document.getElementById("conta-subida");
    if (cont) cont.innerHTML = '<b>' + feitos + ' de ' + ps.length + '</b> passos concluídos' +
      '<span class="barra-mini"><i style="width:' + (ps.length ? feitos / ps.length * 100 : 0) + '%"></i></span>';
    alvo.innerHTML = listaDePassos(ps, "data-subida");
  }

  function desenharQuadro(){
    var alvo = document.getElementById("quadro");
    if (!alvo) return;
    alvo.innerHTML = COLUNAS.map(function(col){
      var lista = (estado.itens || []).filter(function(i){ return i.estado === col.chave; });
      return '<section class="coluna ' + col.cls + '" aria-label="' + col.rot + '">' +
        '<header><i></i><b>' + col.rot + '</b><span class="c">' + lista.length + '</span></header>' +
        '<div class="lista">' +
          (lista.length ? lista.map(cartao).join("")
            : '<p class="vazia">Nada aqui por enquanto.</p>') +
        '</div></section>';
    }).join("");
  }

  function cartao(i){
    return '<button type="button" class="cartao' + (i.trava ? " trava" : "") + '" data-item="' + esc(i.id) + '"' +
      ' aria-label="' + esc(i.t) + ' — avançar estado">' +
      '<span class="marca" aria-hidden="true"></span>' +
      '<span class="miolo">' +
        '<span class="bolha" aria-hidden="true"><svg viewBox="0 0 16 16"><use href="#q-check"/></svg></span>' +
        '<span class="dados">' +
          '<span class="frente">' + esc(i.frente) + (i.trava ? " · trava" : "") + '</span>' +
          '<b>' + esc(i.t) + '</b>' +
          (i.d ? '<span class="d">' + esc(i.d) + '</span>' : '') +
        '</span>' +
      '</span></button>';
  }

  function texto(id, valor){
    var el = document.getElementById(id);
    if (el) el.textContent = valor || "";
  }
  function lista(itens){
    return '<ul>' + (itens || []).map(function(t){ return '<li>' + esc(t) + '</li>'; }).join("") + '</ul>';
  }

  function desenharProximas(){
    var alvo = document.getElementById("etapas"), px = estado.proximas;
    var sec = document.getElementById("s-proximas");
    if (sec) sec.hidden = !px;
    if (!alvo || !px) return;
    texto("proximas-intro", px.intro);
    alvo.innerHTML = (px.etapas || []).map(function(e, i){
      return '<li class="etapa">' +
        '<div class="alto"><span class="n">' + (i + 1) + '</span>' +
          '<span><b>' + esc(e.t) + '</b><span class="sub2">' + esc(e.sub) + '</span></span></div>' +
        '<p class="porque">' + esc(e.porque) + '</p>' +
        '<div class="quem"><h3>O Leandro faz</h3>' + lista(e.leandro) + '</div>' +
        '<div class="quem gab"><h3>O Gabriel faz</h3>' + lista(e.gabriel) + '</div>' +
        '<p class="quando2">' + ic("q-chave") + '<span>' + esc(e.quando) + '</span></p>' +
        '</li>';
    }).join("");
  }

  function desenharCrescimento(){
    var alvo = document.getElementById("formas"), cr = estado.crescimento;
    var sec = document.getElementById("s-crescer");
    if (sec) sec.hidden = !cr;
    if (!alvo || !cr) return;
    texto("crescer-intro", cr.intro);
    alvo.innerHTML = (cr.itens || []).map(function(f, i){
      return '<li class="forma"><span class="n">' + (i + 1) + '</span><div>' +
        '<b>' + esc(f.t) + '</b>' +
        '<span class="selos"><span class="s-para">' + esc(f.para) + '</span>' +
          '<span>custo: ' + esc(f.custo) + '</span><span>efeito: ' + esc(f.prazo) + '</span></span>' +
        '<p>' + esc(f.d) + '</p></div></li>';
    }).join("");
    var o = document.getElementById("crescer-ordem");
    if (o) { o.hidden = !cr.ordem; o.querySelector("p").innerHTML = '<b>Por onde começar.</b> ' + esc(cr.ordem || ""); }
  }

  /* O lugar da foto tem três estados, no mesmo ciclo dos cartões. */
  var ROT_FOTO = { afazer:"3D no lugar", fazendo:"foto escolhida", feito:"foto real no site" };
  function desenharFotos(){
    var alvo = document.getElementById("lugares"), fo = estado.fotos;
    var sec = document.getElementById("s-fotos");
    if (sec) sec.hidden = !fo;
    if (!alvo || !fo) return;
    texto("fotos-intro", fo.intro);
    var ls = lugares(), reais = ls.filter(function(l){ return l.estado === "feito"; }).length;
    var cont = document.getElementById("conta-fotos");
    if (cont) cont.innerHTML = '<b>' + reais + ' de ' + ls.length + '</b> lugares com foto real';
    alvo.innerHTML = ls.map(function(l){
      var busca = "https://br.pinterest.com/search/pins/?q=" + encodeURIComponent(l.q);
      return '<li class="lugar f-' + esc(l.estado) + '">' +
        '<button type="button" class="estado-foto" data-foto="' + esc(l.id) + '" aria-label="' + esc(l.t) +
          ': ' + esc(ROT_FOTO[l.estado] || "") + ' — avançar estado">' +
          '<i aria-hidden="true"></i><span>' + esc(ROT_FOTO[l.estado] || "") + '</span></button>' +
        '<div class="dados"><b>' + esc(l.t) + '</b><span>' + esc(l.onde) + ' · <code>' + esc(l.arquivo) + '</code></span></div>' +
        '<a class="pin" href="' + esc(busca) + '" target="_blank" rel="noopener">Ver referências no Pinterest</a>' +
        '</li>';
    }).join("");
  }

  function reais(v){
    return "R$ " + Number(v).toLocaleString("pt-BR", { minimumFractionDigits:0, maximumFractionDigits:2 });
  }
  function desenharInvest(){
    var fin = estado.financeiro;
    var sec = document.getElementById("s-invest"), at = document.getElementById("atalho-invest");
    if (sec) sec.hidden = !fin;
    if (at) at.hidden = !fin;
    var alvo = document.getElementById("contas");
    if (!fin || !alvo) return;
    texto("invest-intro", fin.intro);
    texto("invest-depois", fin.depois);
    var ls = parcelas(), total = 0, pago = 0;
    ls.forEach(function(p){ total += p.v; if (p.pago) pago += p.v; });
    alvo.innerHTML =
      '<div class="resumo-inv">' +
        '<div><span>Pago</span><b class="v-pago">' + reais(pago) + '</b></div>' +
        '<div><span>Falta</span><b class="v-falta">' + reais(total - pago) + '</b></div>' +
        '<div><span>Total</span><b>' + reais(total) + '</b></div>' +
      '</div>' +
      '<span class="tira-inv" role="img" aria-label="' + Math.round(total ? pago / total * 100 : 0) + ' por cento pago">' +
        '<i style="width:' + (total ? pago / total * 100 : 0) + '%"></i></span>' +
      '<ul class="parcelas">' + ls.map(function(p){
        return '<li><button type="button" class="parcela' + (p.pago ? " ok" : "") + '" data-parcela="' + esc(p.id) + '"' +
          ' aria-pressed="' + (p.pago ? "true" : "false") + '">' +
          '<span class="bolha" aria-hidden="true"><svg viewBox="0 0 16 16"><use href="#q-check"/></svg></span>' +
          '<span class="txt"><b>' + esc(p.t) + '</b><span>' + esc(p.pago ? (p.recebido || "Pago.") : p.nota) + '</span></span>' +
          '<span class="v">' + reais(p.v) + '</span></button></li>';
      }).join("") + '</ul>';
  }

  function desenhar(){
    desenharMedidor();
    desenharMarcos();
    desenharRoteiro();
    desenharSubida();
    desenharProximas();
    desenharCrescimento();
    desenharFotos();
    desenharInvest();
    desenharQuadro();
  }

  /* ---------- interação ---------- */
  var CICLO = { afazer:"fazendo", fazendo:"feito", feito:"afazer" };

  document.addEventListener("click", function(e){
    if (somenteLeitura) return;
    var bp = e.target.closest("[data-passo]");
    if (bp) {
      (estado.roteiro || []).forEach(function(p){ if (p.id === bp.dataset.passo) p.feito = !p.feito; });
      mudou();
      return;
    }
    var bi = e.target.closest("[data-item]");
    if (bi) {
      (estado.itens || []).forEach(function(i){ if (i.id === bi.dataset.item) i.estado = CICLO[i.estado] || "afazer"; });
      mudou();
      return;
    }
    var bs = e.target.closest("[data-subida]");
    if (bs) {
      passosSubida().forEach(function(x){ if (x.id === bs.dataset.subida) x.feito = !x.feito; });
      mudou();
      return;
    }
    var bf = e.target.closest("[data-foto]");
    if (bf) {
      lugares().forEach(function(l){ if (l.id === bf.dataset.foto) l.estado = CICLO[l.estado] || "afazer"; });
      mudou();
      return;
    }
    var bpa = e.target.closest("[data-parcela]");
    if (bpa) {
      parcelas().forEach(function(p){ if (p.id === bpa.dataset.parcela) p.pago = !p.pago; });
      mudou();
    }
  });

  function mudou(){
    estado.atualizado = hojeISO();
    desenhar();
    guardarLocal();
    agendarPublicacao();
  }

  /* ---------- remontagem do documento ---------- */
  /* O molde e o código-fonte ficam em blocos de texto que nunca
     são tocados em tempo de execução — nada de serializar o DOM
     vivo, que carregaria o desenho atual junto. */
  function montarDocumento(){
    var css = document.getElementById("folha").textContent;
    var fonte = document.getElementById("fonte").textContent;
    var molde = document.getElementById("molde").textContent;
    var json = JSON.stringify(estado).replace(/</g, "\\u003c");
    var abre = "<scr" + "ipt", fecha = "</scr" + "ipt>";
    return '<!doctype html>\n<html lang="pt-BR">\n<head>\n' +
      '<meta charset="utf-8">\n' +
      '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' +
      '<meta name="theme-color" content="#1A120C">\n' +
      '<title>' + esc(estado.titulo) + '</title>\n' +
      '<style id="folha">' + css + '</style>\n' +
      '</head>\n<body>\n' +
      abre + ' type="application/json" id="estado">' + json + fecha + '\n' +
      molde + '\n\n' +
      abre + ' type="text/plain" id="molde">' + molde + fecha + '\n' +
      abre + ' type="text/plain" id="fonte">' + fonte + fecha + '\n' +
      abre + '>' + fonte + fecha + '\n' +
      '</body>\n</html>\n';
  }

  /* ---------- publicação ---------- */
  function sinal(classe, texto){
    var el = document.getElementById("sinc");
    if (!el) return;
    el.className = "estado-sinc " + classe;
    el.innerHTML = '<i></i><span>' + esc(texto) + '</span>';
  }

  function agendarPublicacao(){
    if (!canal) return;
    if (pendente) clearTimeout(pendente);
    pendente = setTimeout(publicar, 900);
  }

  function publicar(){
    pendente = null;
    if (!canal) return;
    sinal("", "salvando…");
    canal.publish(montarDocumento()).then(function(){
      sinal("viva", "salvo para todo mundo");
    }, function(err){
      var cod = err && err.code;
      if (cod === "conflict") return;                 /* outra aba ganhou; esta recarrega sozinha */
      if (cod === "not_granted" || cod === "not_writer") {
        somenteLeitura = true;
        sinal("local", "somente leitura");
        return;
      }
      sinal("local", "só neste aparelho");
      torrada("Não deu para salvar para todo mundo. Ficou guardado só neste aparelho.", true);
    });
  }

  /* ---------- partida ---------- */
  desenhar();
  sinal("local", "só neste aparelho");

  if (window.claude && typeof window.claude.use === "function") {
    window.claude.use("artifact").then(function(a){
      if (!a) return;
      canal = a;
      sinal("viva", "salvo para todo mundo");
    }, function(){});
  }
})();
