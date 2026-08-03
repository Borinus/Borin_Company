/**
 * Empresa e equipe.
 *
 * O modelo original prendia tudo ao email de uma pessoa: projeto:<email>:<cod>,
 * ficha:<email>:<tipo>. Funciona pra um cliente sozinho e quebra no primeiro
 * pedido real — o dono quer que o pessoal do campo abra o diagrama no celular
 * sem ele repassar arquivo por WhatsApp.
 *
 * Agora existe a EMPRESA. Projeto e ficha pertencem a ela, e as pessoas são
 * membros:
 *
 *   empresa:<id>          { id, nome, cnpj, dono, criada_em }
 *   cliente:<email>       { ..., empresa_id: <id>, empresa: "<nome>", papel }
 *   projeto:<id>:<codigo> { ... }
 *   ficha:<id>:<tipo>     { ... }
 *
 * O id fica em `empresa_id`, NUNCA em `empresa`. O campo `empresa` ja existia
 * e guarda o NOME que o cliente digitou — é ele que aparece na tela e no
 * email. Guardar o id ali faria a conta do cliente exibir "aB3xK9mQ2pLt" no
 * lugar de "Metalúrgica Serra Ltda", e perderia o nome pra sempre.
 *
 * Papéis, de propósito só dois:
 *   dono   — quem pediu o orçamento. Convida, remove, preenche ficha.
 *   membro — lê projeto e baixa arquivo. Não convida, não preenche, não paga.
 *
 * Não há convite com token e link de aceite. O dono digita o email, a conta
 * nasce com senha gerada e a senha vai por email — o mesmo caminho que já
 * funciona pro lead. Um passo a menos pra errar, e o membro entra do celular
 * sem clicar em link que expira.
 */

import { enviarPara } from "./correio.js";

const ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";

export function novoId() {
  const b = crypto.getRandomValues(new Uint8Array(12));
  return [...b].map((x) => ALFABETO[x % ALFABETO.length]).join("");
}

export function gerarSenha() {
  const b = crypto.getRandomValues(new Uint8Array(12));
  return [...b].map((x) => ALFABETO[x % ALFABETO.length]).join("");
}

/**
 * Toda conta precisa pertencer a uma empresa. As que existem desde antes deste
 * arquivo não pertencem, então a empresa nasce na primeira vez que a conta é
 * usada — com o titular como dono. Migração sem janela de manutenção e sem
 * script separado que alguém esquece de rodar.
 */
export async function garantirEmpresa(env, email, conta) {
  if (conta && conta.empresa_id) return conta;

  const id = novoId();
  await env.CLIENTES.put("empresa:" + id, JSON.stringify({
    id,
    nome: conta.empresa || "",
    dono: email,
    criada_em: conta.criado_em || new Date().toISOString(),
  }));

  const nova = { ...conta, empresa_id: id, papel: "dono" };
  await env.CLIENTES.put("cliente:" + email, JSON.stringify(nova));

  /* o que era da pessoa passa a ser da empresa */
  for (const prefixo of ["projeto:", "ficha:"]) {
    const lista = await env.CLIENTES.list({ prefix: prefixo + email + ":" });
    for (const k of lista.keys) {
      const v = await env.CLIENTES.get(k.name);
      if (v === null) continue;
      const resto = k.name.slice((prefixo + email + ":").length);
      await env.CLIENTES.put(prefixo + id + ":" + resto, v);
      await env.CLIENTES.delete(k.name);
    }
  }
  return nova;
}

export function ehDono(conta) {
  return !conta || !conta.papel || conta.papel === "dono";
}

/** Quem pode ver a empresa, e em que papel. */
export async function listarEquipe(env, conta) {
  const empresa = conta.empresa_id;
  if (!empresa) return { dono: null, membros: [] };

  const cru = await env.CLIENTES.get("empresa:" + empresa);
  const e = cru ? JSON.parse(cru) : {};
  const idx = await env.CLIENTES.get("equipe:" + empresa);
  const emails = idx ? JSON.parse(idx) : [];

  const membros = [];
  for (const em of emails) {
    const c = await env.CLIENTES.get("cliente:" + em);
    if (!c) continue;
    const d = JSON.parse(c);
    membros.push({
      email: em,
      contato: d.contato || "",
      papel: d.papel || "membro",
      criado_em: d.criado_em,
      entrou_alguma_vez: !d.senha_provisoria,
    });
  }
  return { dono: e.dono || null, empresa: e.nome || "", membros };
}

async function guardarIndice(env, empresa, emails) {
  await env.CLIENTES.put("equipe:" + empresa, JSON.stringify([...new Set(emails)]));
}

/**
 * O dono libera acesso pra alguém. Se a pessoa já tem conta em OUTRA empresa,
 * recusa: uma conta não pode ver dois clientes, e mover ela por engano daria
 * a um terceiro o acervo inteiro de outra empresa.
 */
export async function adicionarMembro(env, conta, email, dados) {
  if (!ehDono(conta)) return { erro: "só quem contratou pode liberar acesso", status: 403 };

  const alvo = (dados.email || "").trim().toLowerCase();
  if (!alvo.includes("@") || alvo.length > 160) return { erro: "email inválido", status: 400 };

  const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
  const emails = idx ? JSON.parse(idx) : [];
  if (emails.includes(alvo)) return { erro: "essa pessoa já tem acesso", status: 409 };
  if (emails.length >= 25) return { erro: "limite de 25 pessoas por empresa", status: 409 };

  const existente = await env.CLIENTES.get("cliente:" + alvo);
  if (existente) {
    const d = JSON.parse(existente);
    if (d.empresa_id && d.empresa_id !== conta.empresa_id) {
      return { erro: "esse email já tem conta em outra empresa", status: 409 };
    }
  }

  const senha = gerarSenha();
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const saltHex = [...salt].map((b) => b.toString(16).padStart(2, "0")).join("");

  return {
    ok: true,
    alvo,
    senha,
    saltHex,
    emails: emails.concat([alvo]),
    nome: (dados.nome || "").slice(0, 120),
  };
}

export async function gravarMembro(env, conta, r, hash) {
  await env.CLIENTES.put("cliente:" + r.alvo, JSON.stringify({
    email: r.alvo,
    /* o id manda no acesso; o nome existe só pra tela dele nao ficar vazia */
    empresa_id: conta.empresa_id,
    empresa: conta.empresa || "",
    papel: "membro",
    contato: r.nome,
    salt: r.saltHex,
    hash,
    criado_em: new Date().toISOString(),
    senha_provisoria: true,
    /* quem responde por esse endereco e o dono da empresa, que digitou ele:
       nasce ativa e nao expira */
    estado: "ativa",
    origem: "liberado por " + (conta.email || "dono da conta"),
  }));
  await guardarIndice(env, conta.empresa_id, r.emails);
}

export async function removerMembro(env, conta, email) {
  if (!ehDono(conta)) return { erro: "só quem contratou pode remover acesso", status: 403 };
  const alvo = (email || "").trim().toLowerCase();

  const c = await env.CLIENTES.get("cliente:" + alvo);
  if (!c) return { erro: "sem conta", status: 404 };
  const d = JSON.parse(c);
  if (d.empresa_id !== conta.empresa_id) {
    return { erro: "essa pessoa não é da sua empresa", status: 403 };
  }
  if (d.papel === "dono") return { erro: "não dá para remover quem contratou", status: 400 };

  await env.CLIENTES.delete("cliente:" + alvo);
  await env.CLIENTES.delete("freio:" + alvo);
  /* a sessao aberta dele morre junto: sem isso, quem foi removido continua
     dentro ate o cookie expirar, com o acervo da empresa na mao */
  const sessoes = await env.CLIENTES.list({ prefix: "sessao:" });
  for (const k of sessoes.keys) {
    if ((await env.CLIENTES.get(k.name)) === alvo) {
      await env.CLIENTES.delete(k.name);
    }
  }

  const idx = await env.CLIENTES.get("equipe:" + conta.empresa_id);
  const emails = (idx ? JSON.parse(idx) : []).filter((x) => x !== alvo);
  await guardarIndice(env, conta.empresa_id, emails);
  return { ok: true, removido: alvo };
}

/** O email que o funcionário recebe. Curto: ele vai ler no celular, no chão de fábrica. */
export function avisoDeAcesso(empresa, quem, email, senha) {
  const nome = (quem || "").split(" ")[0];
  return [
    '<div style="margin:0;padding:24px 16px;background:#F4F4F4;',
    "font-family:'Segoe UI',Arial,Helvetica,sans-serif\">",
    '<div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #111111">',
    '<div style="padding:24px 26px 18px;border-bottom:1px solid #111111">',
    '<div style="font-size:26px;font-weight:700;letter-spacing:4px;color:#111111">BORIN</div>',
    '<div style="height:3px;background:#111111;width:148px;margin:5px 0 0"></div>',
    '<div style="font-family:Consolas,monospace;font-size:10px;letter-spacing:.12em;',
    'text-transform:uppercase;color:#6B6B6B;margin-top:5px">projetos elétricos industriais</div>',
    "</div>",
    '<div style="padding:22px 26px 0">',
    '<h1 style="font-size:20px;font-weight:700;margin:0 0 10px;color:#111111">',
    (nome ? nome + ", você tem acesso" : "Você tem acesso"), "</h1>",
    '<p style="font-size:14px;line-height:1.6;color:#111111;margin:0 0 16px">',
    empresa ? ("A " + empresa + " liberou seu acesso") : "Liberaram seu acesso",
    " aos projetos elétricos feitos pela Borin. Dá para abrir do celular, no campo.",
    "</p></div>",
    '<div style="padding:0 26px">',
    '<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;',
    'border:1px solid #DCDCDC">',
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;width:32%;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;",
    'color:#6B6B6B">Endereço</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;color:#111111">',
    "borinprojetos.com.br/entrar</td></tr>",
    '<tr><td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;',
    "font-family:Consolas,monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;",
    'color:#6B6B6B">Email</td>',
    '<td style="padding:10px 12px;border-bottom:1px solid #DCDCDC;font-size:14px;color:#111111">',
    email, "</td></tr>",
    '<tr><td style="padding:10px 12px;font-family:Consolas,monospace;font-size:10px;',
    'letter-spacing:.08em;text-transform:uppercase;color:#6B6B6B">Senha</td>',
    '<td style="padding:10px 12px;font-family:Consolas,monospace;font-size:18px;',
    'font-weight:700;letter-spacing:1px;color:#111111">', senha, "</td></tr>",
    "</table></div>",
    '<div style="padding:18px 26px 22px">',
    '<p style="font-size:13px;line-height:1.6;color:#6B6B6B;margin:0">',
    "Na primeira entrada o site pede para você trocar essa senha. Você vê e baixa os documentos; ",
    "quem contratou é quem preenche as fichas e libera acesso.",
    "</p></div>",
    '<div style="padding:13px 26px;border-top:1px solid #DCDCDC;',
    'font-family:Consolas,monospace;font-size:10px;color:#6B6B6B">',
    "Borin Projetos Elétricos &middot; Caxias do Sul / RS &middot; contato@borinprojetos.com.br",
    "</div></div></div>",
  ].join("");
}

export async function avisarNovoMembro(env, empresa, r) {
  try {
    await enviarPara(env, {
      para: r.alvo,
      assunto: "Seu acesso aos projetos — Borin Projetos Elétricos",
      corpo: avisoDeAcesso(empresa, r.nome, r.alvo, r.senha),
      html: true,
    });
    return true;
  } catch (e) {
    console.error("aviso de acesso falhou:", e && e.message);
    return false;
  }
}
