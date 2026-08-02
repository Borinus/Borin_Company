/* Base dos formularios da Borin — injetado por montar.py no marcador BASE-JS.
   Nao ha servidor: o formulario monta um texto e o cliente escolhe abrir o
   WhatsApp ou baixar o arquivo. O que e marcado com data-perfil fica no
   localStorage do navegador dele, pra nao repreencher no proximo pedido.

   Cada pagina define, antes deste script:
     DOC    — nome do documento (vai no titulo do texto e no arquivo)
     SECOES — [{titulo, campos:[[rotulo, id]], texto:[[rotulo, id]]}]
   e pode sobrescrever extraTexto() para acrescentar bloco proprio. */

var WHATS = '5554996642003';
var EMAIL = 'contato@borinprojetos.com.br';
var CHAVE = 'borin.padrao.v1';
var CHAVE_ENVIO = 'borin.envio';

function v(id) {
  var el = document.getElementById(id);
  if (!el) { return ''; }
  if (el.type === 'checkbox') { return el.checked ? 'sim' : ''; }
  return el.value ? el.value.trim() : '';
}

function radio(nome) {
  var el = document.querySelector('input[name="' + nome + '"]:checked');
  return el ? el.value : '';
}

function marcados(classe) {
  var out = [];
  document.querySelectorAll('.' + classe + ':checked').forEach(function (c) { out.push(c.value); });
  return out;
}

function linha(rotulo, valor) {
  return valor ? rotulo + ': ' + valor + '\n' : '';
}

/* Formata o telefone enquanto digita: +55 54 99664-2003.
   Guarda so os digitos e remonta, pra o cliente poder apagar no meio sem a
   mascara brigar com ele. */
/* O "+55" e escrito pela propria mascara. Se a gente ler os digitos do campo
   sem tirar esse prefixo antes, o 5 e o 5 que ela escreveu voltam como se o
   cliente tivesse digitado — e a cada tecla o codigo do pais se multiplica:
   "+55 5" vira "+55 55 54" vira "+55 55 549". Por isso o prefixo sai primeiro,
   e so o que sobra conta como numero nacional. */
function mascaraFone(el) {
  var t = el.value.trim();
  if (t.indexOf('+55') === 0) { t = t.slice(3); }

  var d = t.replace(/\D/g, '');
  /* colado com o pais na frente: 5554996642003 */
  if (d.length > 11 && d.slice(0, 2) === '55') { d = d.slice(2); }
  d = d.slice(0, 11);

  if (!d) { el.value = ''; return; }

  var ddd = d.slice(0, 2), n = d.slice(2);
  var out = '+55 ' + ddd;
  if (n) {
    /* O hifen so entra com o numero completo — fixo tem 8 digitos e celular
       tem 9. Colocando antes, ele anda sozinho a cada tecla apagada
       ("9966-420", "996-6420", "99-6642"), que parece defeito. */
    out += ' ' + (n.length >= 8 ? n.slice(0, n.length - 4) + '-' + n.slice(n.length - 4) : n);
  }
  el.value = out;
}

/* Data vem do input como 2026-09-15; no texto vai como 15/09/2026 */
function dataBR(iso) {
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  return m ? m[3] + '/' + m[2] + '/' + m[1] : (iso || '');
}

/* ---------- padrao guardado no navegador ---------- */

function camposPerfil() {
  return Array.prototype.slice.call(document.querySelectorAll('[data-perfil]'));
}

function lerPadrao() {
  try {
    var cru = localStorage.getItem(CHAVE);
    return cru ? JSON.parse(cru) : null;
  } catch (e) { return null; }
}

function salvarPadrao() {
  var atual = lerPadrao() || { campos: {} };
  var dados = { salvo_em: new Date().toISOString(), campos: atual.campos || {} };
  camposPerfil().forEach(function (el) {
    if (el.type === 'checkbox') { dados.campos[el.id] = el.checked ? '1' : ''; }
    else { dados.campos[el.id] = el.value; }
  });
  document.querySelectorAll('[data-perfil-radio]').forEach(function (el) {
    if (el.checked) { dados.campos['radio.' + el.name] = el.value; }
  });
  try { localStorage.setItem(CHAVE, JSON.stringify(dados)); } catch (e) { return false; }
  return true;
}

function aplicarPadrao(p) {
  if (!p || !p.campos) { return 0; }
  var n = 0;
  camposPerfil().forEach(function (el) {
    var val = p.campos[el.id];
    if (!val) { return; }
    if (el.type === 'checkbox') { el.checked = (val === '1'); }
    else { el.value = val; }
    n++;
  });
  Object.keys(p.campos).forEach(function (k) {
    if (k.indexOf('radio.') !== 0) { return; }
    var nome = k.slice(6);
    var r = document.querySelector('input[name="' + nome + '"][value="' + p.campos[k] + '"]');
    if (r) { r.checked = true; }
  });
  return n;
}

function apagarPadrao() {
  try { localStorage.removeItem(CHAVE); } catch (e) {}
  location.reload();
}

function dataCurta(iso) {
  try {
    var d = new Date(iso);
    var p = function (n) { return (n < 10 ? '0' : '') + n; };
    return p(d.getDate()) + '/' + p(d.getMonth() + 1) + '/' + d.getFullYear();
  } catch (e) { return ''; }
}

/* ---------- blocos que recolhem ---------- */

var perfilAberto = false;

function blocosPerfil() {
  return Array.prototype.slice.call(document.querySelectorAll('.bloco.perfil'));
}

function recolherPerfil(recolher) {
  blocosPerfil().forEach(function (el) { el.classList.toggle('recolhido', recolher); });
  perfilAberto = !recolher;
  var bt = document.getElementById('btPerfil');
  if (bt) { bt.textContent = recolher ? 'Ver e editar' : 'Esconder'; }
}

function alternarPerfil() {
  recolherPerfil(perfilAberto);
  if (perfilAberto) {
    var b = blocosPerfil()[0];
    if (b) { b.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  }
}

/* ---------- campos que aparecem conforme a resposta ---------- */

function alternarEscopo() {
  var el = document.querySelector('input[name="escopo"]:checked');
  var b = el && el.value === 'B';
  document.querySelectorAll('.se-b').forEach(function (x) { x.classList.toggle('ativo', b); });
}

function alternarNr12() {
  var el = document.querySelector('input[name="nr12"]:checked');
  var sim = el && el.value === 'sim';
  document.querySelectorAll('.se-nr12').forEach(function (x) { x.classList.toggle('ativo', sim); });
}

/* ---------- texto final ---------- */

function extraTexto() { return ''; }

/* completo = true  -> arquivo baixado e previa (leva anexo colado inteiro)
   completo = false -> WhatsApp (so o resumo, senao a URL estoura) */
function montar(completo) {
  var t = DOC.toUpperCase() + ' — BORIN PROJETOS ELÉTRICOS\n';
  t += new Array(t.length).join('=') + '\n';

  SECOES.forEach(function (s) {
    var corpo = '';
    (s.campos || []).forEach(function (par) { corpo += linha(par[0], v(par[1])); });
    (s.texto || []).forEach(function (par) {
      var val = v(par[1]);
      if (val) { corpo += par[0] + ':\n' + val + '\n'; }
    });
    if (s.extra) { corpo += s.extra(completo); }
    if (corpo) { t += '\n' + s.titulo.toUpperCase() + '\n' + corpo; }
  });

  t += extraTexto(completo);
  return t;
}

function verResumo() {
  var r = document.getElementById('resumo');
  r.textContent = montar(true);
  r.classList.add('ativo');
  r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ---------- conta do cliente ---------- */

/* Uma chamada ao Worker. Devolve sempre um objeto, nunca lanca: quem chama
   trata o campo `erro`, e falha de rede vira erro legivel em vez de tela
   travada. */
function api(rota, dados) {
  return fetch('/api/acesso/' + rota, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify(dados || {})
  }).then(function (r) {
    return r.json().catch(function () { return { erro: 'resposta inesperada' }; });
  }).catch(function () {
    return { erro: 'sem conexão com o servidor' };
  });
}

/* Le a conta e, se houver, a ficha guardada nela. Chamado pelas paginas que
   ficam atras do login. */
function carregarDaConta(tipo) {
  return fetch('/api/acesso/eu', { credentials: 'same-origin' })
    .then(function (r) { return r.json(); })
    .then(function (u) {
      if (!u.entrou) { return { entrou: false }; }
      return fetch('/api/acesso/ficha?tipo=' + encodeURIComponent(tipo),
                   { credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (f) { return { entrou: true, usuario: u, ficha: f.dados, em: f.em }; });
    })
    .catch(function () { return { entrou: false }; });
}

function guardarNaConta(tipo, dados) {
  return api('ficha', { tipo: tipo, dados: dados });
}

/* ---------- a ficha inteira, de ida e de volta ---------- */

/* Le tudo que o cliente preencheu, inclusive as linhas que ele adicionou.
   Serve pra guardar na conta e pra devolver do jeito que estava. */
function lerFormulario() {
  var d = { campos: {}, radios: {}, listas: {} };

  document.querySelectorAll('form input, form select, form textarea').forEach(function (el) {
    if (el.type === 'radio') {
      if (el.checked) { d.radios[el.name] = el.value; }
      return;
    }
    if (!el.id) { return; }
    d.campos[el.id] = el.type === 'checkbox' ? (el.checked ? 1 : 0) : el.value;
  });

  document.querySelectorAll('.repetivel').forEach(function (caixa) {
    var linhas = [];
    caixa.querySelectorAll('.linha').forEach(function (l) {
      var selects = l.querySelectorAll('.linha__topo select');
      var m = l.querySelector('.item-macro');
      var f = [];
      l.querySelectorAll('.item-funcao').forEach(function (i) { f.push(i.value); });
      linhas.push({
        cat: selects.length > 1 ? selects[0].value : '',
        macro: m ? m.value : '',
        qtd: (l.querySelector('.item-qtd') || {}).value || '1',
        funcoes: f
      });
    });
    if (linhas.length) { d.listas[caixa.dataset.lista] = linhas; }
  });

  return d;
}

function aplicarFormulario(d) {
  if (!d) { return 0; }
  var n = 0;

  Object.keys(d.campos || {}).forEach(function (id) {
    var el = document.getElementById(id);
    if (!el) { return; }
    var val = d.campos[id];
    if (el.type === 'checkbox') { el.checked = !!val; }
    else { if (val === '') { return; } el.value = val; }
    n++;
  });

  Object.keys(d.radios || {}).forEach(function (nome) {
    var r = document.querySelector('input[name="' + nome + '"][value="' + d.radios[nome] + '"]');
    if (r) { r.checked = true; n++; }
  });

  Object.keys(d.listas || {}).forEach(function (lista) {
    var caixa = document.querySelector('.repetivel[data-lista="' + lista + '"]');
    if (!caixa || typeof addLinha !== 'function') { return; }
    caixa.querySelectorAll('.linha').forEach(function (l) { l.remove(); });
    d.listas[lista].forEach(function (item) {
      addLinha(caixa.querySelector('.link-acao'));
      var l = caixa.querySelectorAll('.linha')[caixa.querySelectorAll('.linha').length - 1];
      var selects = l.querySelectorAll('.linha__topo select');
      if (item.cat && selects.length > 1) {
        selects[0].value = item.cat;
        selects[0].dispatchEvent(new Event('change'));
      }
      var m = l.querySelector('.item-macro');
      if (m) { m.value = item.macro; }
      var q = l.querySelector('.item-qtd');
      if (q) { q.value = item.qtd; q.dispatchEvent(new Event('input')); }
      var f = l.querySelectorAll('.item-funcao');
      (item.funcoes || []).forEach(function (t, i) { if (f[i]) { f[i].value = t; } });
      n++;
    });
  });

  if (typeof alternarEscopo === 'function') { alternarEscopo(); }
  if (typeof alternarNr12 === 'function') { alternarNr12(); }
  return n;
}

/* ---------- ligar a pagina na conta ---------- */

var CONTA = { tipo: null, salvando: null, barra: null };

function avisoConta(txt, acao) {
  if (!CONTA.barra) {
    var b = document.createElement('div');
    b.className = 'perfil-barra ativo';
    b.id = 'barraConta';
    var f = document.querySelector('form');
    f.parentNode.insertBefore(b, f);
    CONTA.barra = b;
  }
  CONTA.barra.innerHTML =
    '<span class="perfil-barra__topo"><span class="no" aria-hidden="true"></span>'
    + '<span class="rotulo">Sua conta</span></span>'
    + '<p class="perfil-barra__resumo">' + txt + '</p>'
    + (acao ? '<div class="perfil-barra__acoes">' + acao + '</div>' : '');
}

function horaCurta() {
  var d = new Date(), z = function (n) { return (n < 10 ? '0' : '') + n; };
  return z(d.getHours()) + ':' + z(d.getMinutes());
}

/* Guarda sozinho, um pouco depois da ultima tecla. Sem botao de salvar:
   formulario longo com botao de salvar e formulario que o cliente perde. */
function salvarDepois() {
  if (!CONTA.tipo) { return; }
  clearTimeout(CONTA.salvando);
  CONTA.salvando = setTimeout(function () {
    guardarNaConta(CONTA.tipo(), lerFormulario()).then(function (r) {
      if (r.ok) {
        avisoConta('Salvo na sua conta às ' + horaCurta() + '.',
                   '<a class="link-acao" href="/entrar" style="text-decoration:none">Minha conta</a>');
      } else if ((r.erro || '').indexOf('sessão') >= 0) {
        CONTA.tipo = null;
        avisoConta('Sua sessão expirou. O que você digitou continua aqui.',
                   '<a class="link-acao" href="/entrar?ir=' + location.pathname
                   + '" style="text-decoration:none">Entrar de novo</a>');
      }
    });
  }, 1200);
}

/* tipoFn e funcao porque no /projeto o tipo depende do codigo, que o cliente
   digita depois de a pagina carregar */
function ligarConta(tipoFn) {
  carregarDaConta(tipoFn()).then(function (r) {
    if (!r.entrou) {
      avisoConta('Você não entrou. O que preencher aqui fica só neste navegador.',
                 '<a class="link-acao" href="/entrar?ir=' + location.pathname
                 + '" style="text-decoration:none">Entrar na minha conta</a>');
      return;
    }
    CONTA.tipo = tipoFn;
    var n = aplicarFormulario(r.ficha);
    avisoConta(
      '<b>' + (r.usuario.empresa || r.usuario.email) + '</b> — '
      + (n ? n + (n === 1 ? ' campo recuperado' : ' campos recuperados') + ' da sua conta.'
           : 'o que você preencher fica salvo automaticamente.'),
      '<a class="link-acao" href="/entrar" style="text-decoration:none">Minha conta</a>');

    document.addEventListener('input', salvarDepois);
    document.addEventListener('change', salvarDepois);
  });
}

/* ---------- envio ---------- */

/* A pagina define API quando o pedido tambem deve chegar por email. So o
   /orcamento faz isso: o /padrao e o /projeto carregam o padrao interno e o
   desenho da maquina do cliente, e esses nao saem do navegador dele.

   Dispara junto com o clique, em segundo plano. keepalive faz a requisicao
   sobreviver a navegacao pra /enviado. Falha aqui nao trava nada — o WhatsApp
   abre do mesmo jeito e o cliente nunca ve erro. */
var API = '';

function notificar(intencao) {
  if (!API || typeof fetch !== 'function') { return Promise.resolve(false); }

  var pedido = fetch(API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      doc: DOC,
      intencao: intencao,
      empresa: v('empresa'),
      contato: v('contato'),
      email: v('email'),
      fone: v('fone'),
      website: v('website'),
      /* vao pro assunto: sem isso o Gmail junta todos os pedidos numa
         conversa so e nao da pra separar por projeto */
      codigo: v('codigo') || v('projeto_numero'),
      equipamento: v('equipamento') || v('projeto_descricao'),
      texto: montar(true)
    })
  }).then(function (r) {
    return r.ok ? r.json().catch(function () { return { ok: true }; }) : { ok: false };
  }).then(function (d) {
    return !!(d && d.ok);
  }).catch(function () { return false; });

  /* rede lenta nao pode prender o cliente numa tela de "enviando" pra sempre;
     estourou o tempo, trata como falha e a pagina seguinte oferece os outros
     caminhos */
  var estouro = new Promise(function (r) { setTimeout(function () { r(false); }, 12000); });
  return Promise.race([pedido, estouro]);
}

/* Usado so pelo /orcamento, onde existe servidor. Espera a resposta antes de
   mandar pra confirmacao — dizer "recebido" sem ter recebido seria mentira. */
function solicitar(botao) {
  if (typeof validar === 'function' && !validar()) { return; }
  salvarPadrao();

  var rotulo = botao.textContent;
  botao.disabled = true;
  botao.textContent = 'Enviando…';

  notificar('site').then(function (ok) {
    guardarEnvio(ok ? 'ok' : 'falhou');
    if (!ok) {
      botao.disabled = false;
      botao.textContent = rotulo;
    }
    location.href = destinoEnvio();
  });
}

function urlWhats(texto) {
  return 'https://wa.me/' + WHATS + '?text=' + encodeURIComponent(texto);
}

function urlEmail(texto) {
  return 'mailto:' + EMAIL
       + '?subject=' + encodeURIComponent(DOC + ' — ' + (v('empresa') || 'sem empresa'))
       + '&body=' + encodeURIComponent(texto);
}

/* Abre um destino externo (WhatsApp ou cliente de email) sem derrubar a aba
   de origem. Precisa sair de dentro do clique, senao o navegador bloqueia. */
function abrirExterno(url, novaAba) {
  var a = document.createElement('a');
  a.href = url;
  if (novaAba) { a.target = '_blank'; a.rel = 'noopener'; }
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function destinoEnvio() {
  return location.protocol === 'file:' ? 'enviado.html' : '/enviado';
}

/* Guarda o pedido pra pagina de confirmacao poder reoferecer os outros caminhos
   se o primeiro nao funcionar. Se o navegador nao deixar guardar, o envio ja
   aconteceu de qualquer forma — so nao ha o que reoferecer depois. */
function guardarEnvio(intencao) {
  try {
    sessionStorage.setItem(CHAVE_ENVIO, JSON.stringify({
      doc: DOC,
      intencao: intencao,
      curto: montar(false),
      completo: montar(true),
      empresa: v('empresa') || '',
      assunto: DOC + ' — ' + (v('empresa') || 'sem empresa')
    }));
    return true;
  } catch (e) { return false; }
}

/* O envio dispara e a aba de origem vira a confirmacao. Antes o cliente clicava,
   caia no WhatsApp e nunca mais via o site — sem retorno, sem prazo de resposta
   e sem segundo caminho se a janela nao abrisse. */
function enviar(intencao) {
  /* a pagina define validar() quando tem campo obrigatorio; sem ela, segue */
  if (typeof validar === 'function' && !validar()) { return; }
  salvarPadrao();
  var guardou = guardarEnvio(intencao);
  var texto = intencao === 'email' ? montar(true) : montar(false);
  abrirExterno(intencao === 'email' ? urlEmail(texto) : urlWhats(texto), intencao !== 'email');
  /* Vai pra confirmacao SEMPRE, mesmo que o sessionStorage tenha falhado.
     Antes isso ficava dentro de "if (guardou)", e guardou e false no
     navegador embutido do Instagram e do WhatsApp: o cliente enviava e
     ficava parado na mesma tela. A /enviado tambem e a unica marca de
     conversao que a medicao consegue contar. */
  setTimeout(function () { location.href = destinoEnvio(); }, 400);
}

function enviarWhats() { enviar('whats'); }
function enviarEmail() { enviar('email'); }

function baixarTexto(texto, doc, quem) {
  var nome = (quem || 'cliente').replace(/[^a-zA-Z0-9-_ ]/g, '').trim() || 'cliente';
  var blob = new Blob([texto], { type: 'text/plain;charset=utf-8' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = doc + ' - ' + nome + '.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}

function baixar() {
  salvarPadrao();
  baixarTexto(montar(true), DOC, v('empresa'));
}

function copiar(texto, botao) {
  var rotulo = botao ? botao.textContent : '';
  function avisar(ok) {
    if (!botao) { return; }
    botao.textContent = ok ? 'Copiado' : 'Não deu — selecione e copie';
    setTimeout(function () { botao.textContent = rotulo; }, 2200);
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(texto).then(function () { avisar(true); }, function () { avisar(false); });
  } else {
    avisar(false);
  }
}

function copiarPedido(botao) { copiar(montar(true), botao); }

/* ---------- inicializacao ---------- */

function iniciarForm(opcoes) {
  opcoes = opcoes || {};
  var p = lerPadrao();
  var n = p ? aplicarPadrao(p) : 0;

  if (n > 0) {
    var barra = document.getElementById('perfilBarra');
    if (barra) {
      var quem = (p.campos.empresa || p.campos.contato || 'seu padrão');
      var d = dataCurta(p.salvo_em);
      var txt = '<b>' + quem + '</b> — ' + n + (n === 1 ? ' campo' : ' campos')
              + ' já preenchidos' + (d ? ', salvos em ' + d : '') + '.';
      document.getElementById('perfilResumo').innerHTML = txt;
      barra.classList.add('ativo');
    }
    if (opcoes.recolher !== false) { recolherPerfil(true); }
    if (opcoes.aoVoltar) { opcoes.aoVoltar(p); }
  } else {
    recolherPerfil(false);
  }

  alternarEscopo();
  alternarNr12();
}
