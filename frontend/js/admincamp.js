const API_URL = "https://sitepedidosjovens-vztj.onrender.com";

const state = {
  campeonatos: [],
  jogadores: [],
  perguntas: []
};

let msgTimer = null;

function mostrarMsg(texto, erro = false) {
  const el = document.getElementById("msg");
  el.textContent = texto;
  el.className = erro ? "msg-err" : "msg-ok";
  clearTimeout(msgTimer);
  msgTimer = setTimeout(() => {
    el.className = "";
    el.style.display = "none";
  }, 3500);
}

async function api(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.erro || `Erro HTTP ${res.status}`);
  }
  return data;
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------- CAMPEONATOS ----------
async function carregarCampeonatos() {
  const data = await api("/jogo/campeonatos");
  state.campeonatos = data.campeonatos || [];
  renderCampeonatos();
  syncSelectsCampeonato();
  await carregarRanking();
}

function syncSelectsCampeonato() {
  const topSelect = document.getElementById("select-campeonato-ativo");
  const acertoSelect = document.getElementById("acerto-campeonato");
  const anterior = topSelect.value || acertoSelect.value;

  const optionsHtml = state.campeonatos.length
    ? state.campeonatos.map(c =>
        `<option value="${c.id}">${escapeHtml(c.nome)} ${c.ativo ? "(Ativo)" : "(Encerrado)"}</option>`
      ).join("")
    : `<option value="">Nenhum campeonato</option>`;

  topSelect.innerHTML = optionsHtml;
  acertoSelect.innerHTML = optionsHtml;

  if (anterior && state.campeonatos.some(c => String(c.id) === String(anterior))) {
    topSelect.value = anterior;
    acertoSelect.value = anterior;
  } else if (state.campeonatos.length) {
    topSelect.value = state.campeonatos[0].id;
    acertoSelect.value = state.campeonatos[0].id;
  }
}

function onCampeonatoChange() {
  const id = document.getElementById("select-campeonato-ativo").value;
  document.getElementById("acerto-campeonato").value = id;
  carregarRanking();
}

function renderCampeonatos() {
  const tbody = document.getElementById("tabela-campeonatos");
  if (!state.campeonatos.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="small">Nenhum campeonato cadastrado.</td></tr>`;
    return;
  }
  tbody.innerHTML = state.campeonatos.map(c => `
    <tr>
      <td>${c.id}</td>
      <td>${escapeHtml(c.nome)}</td>
      <td><span class="badge ${c.ativo ? "ativo" : "inativo"}">${c.ativo ? "Ativo" : "Encerrado"}</span></td>
      <td>
        <button type="button" class="secondary" data-camp-toggle="${c.id}" data-camp-ativo="${!c.ativo}">${c.ativo ? "Encerrar" : "Reabrir"}</button>
        <button type="button" class="danger" data-camp-delete="${c.id}">Excluir</button>
      </td>
    </tr>
  `).join("");
}

async function criarCampeonato(e) {
  e.preventDefault();
  const input = document.getElementById("camp-nome");
  try {
    await api("/jogo/campeonatos", {
      method: "POST",
      body: JSON.stringify({ nome: input.value.trim(), ativo: true })
    });
    input.value = "";
    mostrarMsg("Campeonato criado!");
    await carregarCampeonatos();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

async function toggleCampeonato(id, ativo) {
  try {
    await api(`/jogo/campeonatos/${id}`, {
      method: "PUT",
      body: JSON.stringify({ ativo })
    });
    mostrarMsg("Status do campeonato atualizado!");
    await carregarCampeonatos();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

async function deletarCampeonato(id) {
  if (!confirm("Excluir este campeonato e seus registros de acertos?")) return;
  try {
    await api(`/jogo/campeonatos/${id}`, { method: "DELETE" });
    mostrarMsg("Campeonato excluído!");
    await carregarCampeonatos();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

// ---------- JOGADORES ----------
async function carregarJogadores() {
  const data = await api("/jogo/jogadores");
  state.jogadores = data.jogadores || [];
  renderJogadores();
  syncSelectJogadores();
}

function syncSelectJogadores() {
  const sel = document.getElementById("acerto-jogador");
  sel.innerHTML = state.jogadores.length
    ? state.jogadores.map(j => `<option value="${j.id}">${escapeHtml(j.nome)}</option>`).join("")
    : `<option value="">Nenhum jogador</option>`;
}

function renderJogadores() {
  const tbody = document.getElementById("tabela-jogadores");
  if (!state.jogadores.length) {
    tbody.innerHTML = `<tr><td colspan="3" class="small">Nenhum jogador cadastrado.</td></tr>`;
    return;
  }
  tbody.innerHTML = state.jogadores.map(j => `
    <tr>
      <td>${j.id}</td>
      <td>${escapeHtml(j.nome)}</td>
      <td>
        <button type="button" class="secondary" data-jog-edit="${j.id}">Editar</button>
        <button type="button" class="danger" data-jog-delete="${j.id}">Excluir</button>
      </td>
    </tr>
  `).join("");
}

async function criarJogador(e) {
  e.preventDefault();
  const input = document.getElementById("jog-nome");
  try {
    await api("/jogo/jogadores", {
      method: "POST",
      body: JSON.stringify({ nome: input.value.trim() })
    });
    input.value = "";
    mostrarMsg("Jogador cadastrado!");
    await carregarJogadores();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

async function editarJogador(id) {
  const jogador = state.jogadores.find(j => Number(j.id) === Number(id));
  if (!jogador) return;
  const novoNome = prompt("Novo nome do jogador:", jogador.nome);
  if (!novoNome || !novoNome.trim()) return;
  try {
    await api(`/jogo/jogadores/${id}`, {
      method: "PUT",
      body: JSON.stringify({ nome: novoNome.trim() })
    });
    mostrarMsg("Jogador atualizado!");
    await carregarJogadores();
    await carregarRanking();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

async function deletarJogador(id) {
  if (!confirm("Excluir este jogador?")) return;
  try {
    await api(`/jogo/jogadores/${id}`, { method: "DELETE" });
    mostrarMsg("Jogador excluído!");
    await carregarJogadores();
    await carregarRanking();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

// ---------- PERGUNTAS ----------
async function carregarPerguntas() {
  const data = await api("/jogo/perguntas");
  state.perguntas = data.perguntas || [];
  renderPerguntas();
  syncSelectPerguntas();
}

function syncSelectPerguntas() {
  const sel = document.getElementById("acerto-pergunta");
  sel.innerHTML = state.perguntas.length
    ? state.perguntas.map(p =>
        `<option value="${p.id}" data-pontos="${p.pontos}">#${p.id} - ${escapeHtml(p.enunciado)} (${p.pontos} pts)</option>`
      ).join("")
    : `<option value="">Nenhuma pergunta</option>`;
  preencherPontosPadrao();
}

function preencherPontosPadrao() {
  const sel = document.getElementById("acerto-pergunta");
  const opt = sel.options[sel.selectedIndex];
  const ptsInput = document.getElementById("acerto-pontos");
  if (opt && opt.dataset.pontos !== undefined) {
    ptsInput.placeholder = `Padrão: ${opt.dataset.pontos}`;
  }
}

function renderPerguntas() {
  const tbody = document.getElementById("tabela-perguntas");
  if (!state.perguntas.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="small">Nenhuma pergunta cadastrada.</td></tr>`;
    return;
  }
  tbody.innerHTML = state.perguntas.map(p => `
    <tr>
      <td>${p.id}</td>
      <td>${escapeHtml(p.enunciado)}</td>
      <td>${escapeHtml(p.resposta_correta || "-")}</td>
      <td>${p.pontos}</td>
      <td>
        <button type="button" class="danger" data-perg-delete="${p.id}">Excluir</button>
      </td>
    </tr>
  `).join("");
}

async function criarPergunta(e) {
  e.preventDefault();
  const enunciadoEl = document.getElementById("perg-enunciado");
  const respostaEl = document.getElementById("perg-resposta");
  const pontosEl = document.getElementById("perg-pontos");

  try {
    await api("/jogo/perguntas", {
      method: "POST",
      body: JSON.stringify({
        enunciado: enunciadoEl.value.trim(),
        resposta_correta: respostaEl.value.trim() || null,
        pontos: Number(pontosEl.value || 1)
      })
    });
    enunciadoEl.value = "";
    respostaEl.value = "";
    pontosEl.value = "1";
    mostrarMsg("Pergunta adicionada!");
    await carregarPerguntas();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

async function deletarPergunta(id) {
  if (!confirm("Excluir esta pergunta?")) return;
  try {
    await api(`/jogo/perguntas/${id}`, { method: "DELETE" });
    mostrarMsg("Pergunta excluída!");
    await carregarPerguntas();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

// ---------- ACERTOS & RANKING ----------
async function registrarAcerto(e) {
  e.preventDefault();
  const campeonato_id = Number(document.getElementById("acerto-campeonato").value);
  const jogador_id = Number(document.getElementById("acerto-jogador").value);
  const pergunta_id = Number(document.getElementById("acerto-pergunta").value);
  const pontosRaw = document.getElementById("acerto-pontos").value;

  const payload = { campeonato_id, jogador_id, pergunta_id };
  if (pontosRaw !== "") {
    payload.pontos_ganhos = Number(pontosRaw);
  }

  try {
    await api("/jogo/responder", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    document.getElementById("acerto-pontos").value = "";
    document.getElementById("select-campeonato-ativo").value = campeonato_id;
    mostrarMsg("Acerto registrado e ranking atualizado!");
    await carregarRanking();
  } catch (err) {
    mostrarMsg(err.message, true);
  }
}

async function carregarRanking() {
  const id = document.getElementById("select-campeonato-ativo").value;
  const tbody = document.getElementById("tabela-ranking");
  const info = document.getElementById("ranking-info");

  if (!id) {
    info.textContent = "Nenhum campeonato selecionado.";
    tbody.innerHTML = "";
    return;
  }

  try {
    const data = await api(`/jogo/campeonatos/${id}/ranking`);
    info.textContent = `${data.campeonato.nome} — ${data.campeonato.ativo ? "Ativo" : "Encerrado"}`;
    const ranking = data.ranking || [];

    if (!ranking.length) {
      tbody.innerHTML = `<tr><td colspan="4" class="small">Nenhum acerto registrado ainda neste campeonato.</td></tr>`;
      return;
    }

    tbody.innerHTML = ranking.map(r => `
      <tr>
        <td><strong>${r.posicao}º</strong></td>
        <td>${escapeHtml(r.jogador)}</td>
        <td>${r.total_acertos}</td>
        <td><strong>${r.pontuacao_total}</strong></td>
      </tr>
    `).join("");
  } catch (err) {
    info.textContent = "Erro ao carregar ranking.";
    tbody.innerHTML = `<tr><td colspan="4" class="small">${escapeHtml(err.message)}</td></tr>`;
  }
}

// ---------- EVENTOS ----------
function bindEvents() {
  document.getElementById("select-campeonato-ativo").addEventListener("change", onCampeonatoChange);
  document.getElementById("acerto-pergunta").addEventListener("change", preencherPontosPadrao);
  document.getElementById("btn-atualizar-ranking").addEventListener("click", carregarRanking);

  document.getElementById("form-acerto").addEventListener("submit", registrarAcerto);
  document.getElementById("form-campeonato").addEventListener("submit", criarCampeonato);
  document.getElementById("form-jogador").addEventListener("submit", criarJogador);
  document.getElementById("form-pergunta").addEventListener("submit", criarPergunta);

  document.getElementById("tabela-campeonatos").addEventListener("click", (e) => {
    const toggleBtn = e.target.closest("[data-camp-toggle]");
    if (toggleBtn) {
      toggleCampeonato(Number(toggleBtn.dataset.campToggle), toggleBtn.dataset.campAtivo === "true");
      return;
    }
    const delBtn = e.target.closest("[data-camp-delete]");
    if (delBtn) {
      deletarCampeonato(Number(delBtn.dataset.campDelete));
    }
  });

  document.getElementById("tabela-jogadores").addEventListener("click", (e) => {
    const editBtn = e.target.closest("[data-jog-edit]");
    if (editBtn) {
      editarJogador(Number(editBtn.dataset.jogEdit));
      return;
    }
    const delBtn = e.target.closest("[data-jog-delete]");
    if (delBtn) {
      deletarJogador(Number(delBtn.dataset.jogDelete));
    }
  });

  document.getElementById("tabela-perguntas").addEventListener("click", (e) => {
    const delBtn = e.target.closest("[data-perg-delete]");
    if (delBtn) {
      deletarPergunta(Number(delBtn.dataset.pergDelete));
    }
  });
}

async function init() {
  bindEvents();
  try {
    await Promise.all([carregarCampeonatos(), carregarJogadores(), carregarPerguntas()]);
  } catch (err) {
    mostrarMsg("Erro ao carregar dados iniciais: " + err.message, true);
  }
}

init();