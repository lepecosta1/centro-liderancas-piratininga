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
  }

  function guardarLocal(){
    var over = { versao:estado.versao, roteiro:{}, itens:{} };
    (estado.roteiro || []).forEach(function(p){ over.roteiro[p.id] = !!p.feito; });
    (estado.itens || []).forEach(function(i){ over.itens[i.id] = i.estado; });
    try { localStorage.setItem(CHAVE, JSON.stringify(over)); } catch (e) {}
  }

  /* ---------- ferramentas ---------- */
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]; }); }
  function ic(id){ return '<svg viewBox="0 0 16 16" aria-hidden="true"><use href="#' + id + '"/></svg>'; }

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
    var r = contaRoteiro();
    var cont = document.getElementById("conta-hoje");
    if (cont) {
      cont.innerHTML = '<b>' + r.feitos + ' de ' + r.total + '</b> passos concluídos' +
        '<span class="barra-mini"><i style="width:' + (r.total ? (r.feitos / r.total) * 100 : 0) + '%"></i></span>';
    }
    alvo.innerHTML = (estado.roteiro || []).map(function(p, i){
      return '<li><button type="button" class="passo' + (p.feito ? " ok" : "") + '" data-passo="' + esc(p.id) + '"' +
        ' aria-pressed="' + (p.feito ? "true" : "false") + '">' +
        '<span class="n">' + (p.feito ? '<svg viewBox="0 0 16 16" aria-hidden="true"><use href="#q-check"/></svg>' : (i + 1)) + '</span>' +
        '<span class="txt"><b>' + esc(p.t) + '</b><span>' + esc(p.d) + '</span></span>' +
        '</button></li>';
    }).join("");
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

  function desenhar(){
    desenharMedidor();
    desenharRoteiro();
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
    }
  });

  function mudou(){
    estado.atualizado = new Date().toISOString().slice(0, 10);
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
