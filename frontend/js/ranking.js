const API_URL = "https://sitepedidosjovens-vztj.onrender.com";
const AUTO_REFRESH_MS = 15000;

let campeonatos = [];
let refreshTimer = null;

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function api(path) {
  const res = await fetch(`${API_URL}${path}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.erro || `Erro HTTP ${res.status}`);
  }
  return data;
}

function renderSelectCampeonatos(selectedId = null) {
  const select = document.getElementById("select-campeonato");

  if (!campeonatos.length) {
    select.innerHTML = `<option value="">Nenhum campeonato disponível</option>`;
    return;
  }

  select.innerHTML = campeonatos
    .map(c => `<option value="${c.id}">${escapeHtml(c.nome)} ${c.ativo ? "(Ativo)" : "(Encerrado)"}</option>`)
    .join("");

  if (selectedId && campeonatos.some(c => String(c.id) === String(selectedId))) {
    select.value = selectedId;
  } else {
    const primeiroAtivo = campeonatos.find(c => c.ativo);
    select.value = primeiroAtivo ? primeiroAtivo.id : campeonatos[0].id;
  }
}

async function carregarCampeonatos() {
  const select = document.getElementById("select-campeonato");
  const anterior = select.value;

  const data = await api("/jogo/campeonatos");
  campeonatos = data.campeonatos || [];
  renderSelectCampeonatos(anterior);
  await carregarRanking();
}

async function carregarRanking() {
  const select = document.getElementById("select-campeonato");
  const id = select.value;

  const tituloEl = document.getElementById("titulo-campeonato");
  const statusTextoEl = document.getElementById("status-texto");
  const badgeEl = document.getElementById("status-badge");
  const tbody = document.getElementById("tabela-ranking");

  if (!id) {
    tituloEl.textContent = "Sem campeonatos";
    statusTextoEl.textContent = "Nenhum campeonato cadastrado no momento.";
    badgeEl.style.display = "none";
    tbody.innerHTML = `<tr><td colspan="4" class="small">Nada para exibir.</td></tr>`;
    return;
  }

  try {
    const data = await api(`/jogo/campeonatos/${id}/ranking`);
    const camp = data.campeonato;
    const ranking = data.ranking || [];

    tituloEl.textContent = camp.nome;
    badgeEl.style.display = "inline-block";
    badgeEl.textContent = camp.ativo ? "Em andamento" : "Encerrado";
    badgeEl.className = `badge ${camp.ativo ? "ativo" : "inativo"}`;

    const hora = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    statusTextoEl.textContent = `Atualizado às ${hora}`;

    if (!ranking.length) {
      tbody.innerHTML = `<tr><td colspan="4" class="small">Ninguém pontuou neste campeonato ainda.</td></tr>`;
      return;
    }

    tbody.innerHTML = ranking
      .map(item => {
        const posClasse = item.posicao <= 3 ? `pos-${item.posicao}` : "";
        return `
          <tr class="${posClasse}">
            <td>${item.posicao}º</td>
            <td>${escapeHtml(item.jogador)}</td>
            <td>${item.total_acertos}</td>
            <td class="pts">${item.pontuacao_total}</td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    tituloEl.textContent = "Erro ao carregar";
    statusTextoEl.innerHTML = `<span class="erro">${escapeHtml(err.message)}</span>`;
    badgeEl.style.display = "none";
    tbody.innerHTML = `<tr><td colspan="4" class="small">Não foi possível obter o ranking.</td></tr>`;
  }
}

function bindEvents() {
  document.getElementById("select-campeonato").addEventListener("change", carregarRanking);
  document.getElementById("btn-atualizar").addEventListener("click", carregarRanking);
}

async function init() {
  bindEvents();
  try {
    await carregarCampeonatos();
  } catch (err) {
    document.getElementById("titulo-campeonato").textContent = "Erro de conexão";
    document.getElementById("status-texto").innerHTML = `<span class="erro">${escapeHtml(err.message)}</span>`;
  }

  clearInterval(refreshTimer);
  refreshTimer = setInterval(carregarRanking, AUTO_REFRESH_MS);
}

init();