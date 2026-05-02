const API_URL = "https://sitepedidosjovens.onrender.com";

/* =========================
   ESTADO GLOBAL
========================= */

let produtos_hoje = [];
let nome_cliente = "";
let produtos_cliente = [];
let total = 0;

/* =========================
   ELEMENTOS DOM
========================= */

const btn_nome = document.getElementById("btn_nome");
const nome_usuario = document.getElementById("nome_usuario");
const caixa_nome = document.getElementById("caixa_nome");

const cardapio = document.getElementById("cardapio");
const div_conta = document.getElementById("div_conta");

const principal_qr = document.getElementById("principal_qr");
const div_qrcode = document.getElementById("div_qrcode");
const div_pix_copia_cola = document.getElementById("div_pix-copia-cola");
const textarea_pix = document.getElementById("pix-copia-cola");
const btn_copiar = document.getElementById("btn-copiar");

/* =========================
   UI FIXA
========================= */

const h1_total = document.createElement("h1");
h1_total.id = "texto_total";
h1_total.textContent = "Total: R$ 0,00";

const btn_fechar_pedido = document.createElement("button");
btn_fechar_pedido.id = "btn_fechar_pedido";
btn_fechar_pedido.textContent = "Fechar pedido";

/* =========================
   LOGIN
========================= */

btn_nome.addEventListener("click", (e) => {
  e.preventDefault();

  nome_cliente = nome_usuario.value.trim();
  if (!nome_cliente) return alert("Digite seu nome");

  caixa_nome.remove();
  cardapio.style.display = "grid";

  carregarProdutos();
});

/* =========================
   CARREGAR PRODUTOS DO BACKEND
========================= */

async function carregarProdutos() {
  try {
    const res = await fetch(`${API_URL}/produtos`);
    const data = await res.json();

    produtos_hoje = data.produtos || [];

    renderizarProdutos();
  } catch (err) {
    console.error("Erro ao carregar produtos:", err);
    alert("Erro ao carregar cardápio");
  }
}

/* =========================
   RENDER CARDÁPIO
========================= */

function renderizarProdutos() {
  cardapio.innerHTML = "";

  produtos_hoje.forEach((produto) => {
    const div_produto = document.createElement("div");
    div_produto.classList.add("produto");

    const span = document.createElement("span");
    span.textContent = `${produto.nome} - ${Number(
      produto.preco
    ).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}`;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.classList.add("btn_produto");

    btn.addEventListener("click", () => adicionarProduto(produto));

    div_produto.append(span, btn);
    cardapio.appendChild(div_produto);
  });
}

/* =========================
   CARRINHO
========================= */

function adicionarProduto(produto) {
  produtos_cliente.push(produto);
  total += Number(produto.preco);

  h1_total.textContent = `Total: ${total.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  })}`;

  div_conta.style.display = "flex";

  let item = [...div_conta.children].find(
    (el) => el.dataset?.nome === produto.nome
  );

  if (item) {
    let qtd = Number(item.dataset.qtd) + 1;
    item.dataset.qtd = qtd;
    item.querySelector(".qtd").textContent = `${qtd}x`;
  } else {
    const item_conta = document.createElement("div");
    item_conta.classList.add("produto_conta");
    item_conta.dataset.nome = produto.nome;
    item_conta.dataset.qtd = 1;

    const nome = document.createElement("span");
    nome.textContent = produto.nome;

    const qtd = document.createElement("span");
    qtd.classList.add("qtd");
    qtd.textContent = "1x";

    item_conta.append(nome, qtd);

    if (!div_conta.contains(h1_total)) {
      div_conta.appendChild(h1_total);
    }

    if (!div_conta.contains(btn_fechar_pedido)) {
      div_conta.appendChild(btn_fechar_pedido);
    }

    div_conta.appendChild(item_conta);
  }

  if (!div_conta.contains(h1_total)) {
    div_conta.appendChild(h1_total);
  }

  if (!div_conta.contains(btn_fechar_pedido)) {
    div_conta.appendChild(btn_fechar_pedido);
  }
}

/* =========================
   PIX HELPERS (igual seu)
========================= */

function crc16(payload) {
  let polinomio = 0x1021;
  let resultado = 0xffff;

  for (let i = 0; i < payload.length; i++) {
    resultado ^= payload.charCodeAt(i) << 8;
    for (let j = 0; j < 8; j++) {
      if ((resultado <<= 1) & 0x10000) {
        resultado ^= polinomio;
      }
      resultado &= 0xffff;
    }
  }
  return resultado.toString(16).toUpperCase().padStart(4, "0");
}

function gerarPix({ chave, nome, cidade, valor, txid }) {
  const valorStr = valor.toFixed(2);

  const gui = "BR.GOV.BCB.PIX";
  const guiLength = gui.length.toString().padStart(2, "0");

  const chaveLength = chave.length.toString().padStart(2, "0");
  const campo26Conteudo = `00${guiLength}${gui}01${chaveLength}${chave}`;
  const campo26Length = campo26Conteudo.length.toString().padStart(2, "0");
  const campo26 = `26${campo26Length}${campo26Conteudo}`;

  const txidVal = txid.slice(0, 25);
  const txidLength = txidVal.length.toString().padStart(2, "0");
  const campo62 = `62${(6 + txidVal.length)
    .toString()
    .padStart(2, "0")}050${txidLength}${txidVal}`;

  const payloadSemCRC =
    "000201010212" +
    campo26 +
    "52040000" +
    "5303986" +
    `54${valorStr.length.toString().padStart(2, "0")}${valorStr}` +
    "5802BR" +
    `59${nome.length.toString().padStart(2, "0")}${nome}` +
    `60${cidade.length.toString().padStart(2, "0")}${cidade}` +
    campo62 +
    "6304";

  const crc = crc16(payloadSemCRC);
  return payloadSemCRC + crc;
}

/* =========================
   FINALIZAR PEDIDO
========================= */

btn_fechar_pedido.addEventListener("click", async () => {
  for (const produto of produtos_cliente) {
    const res = await fetch(`${API_URL}/pedir`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: nome_cliente,
        produto: produto.nome,
      }),
    });

    const json = await res.json();
    if (json.status !== "ok") {
      alert("Erro ao salvar pedido");
      return;
    }
  }

  const res_pag = await fetch(`${API_URL}/pagamento`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nome: nome_cliente,
      montante: total,
    }),
  });

  const pagamento = await res_pag.json();
  if (pagamento.status !== "ok") {
    alert("Erro no pagamento");
    return;
  }

  const txid = `PEDIDO${pagamento.id_pag.toString().padStart(5, "0")}`;

  const payload = gerarPix({
    chave: "c400a935-9063-4cea-8fc6-0e2cdb73cbe7",
    nome: "Emily Natasha Mergulhao d",
    cidade: "SAO PAULO",
    valor: total,
    txid,
  });

  QRCode.toCanvas(document.getElementById("qrcode"), payload, { width: 250 });

  textarea_pix.value = payload;

  btn_copiar.onclick = () => {
    navigator.clipboard.writeText(payload);
    alert("PIX copiado!");
  };

  cardapio.style.display = "none";
  div_conta.style.display = "none";
  div_qrcode.style.display = "flex";
  div_pix_copia_cola.style.display = "flex";
  principal_qr.style.display = "flex";
  principal_qr.style.flexDirection = "column";
  principal_qr.style.gap = "20px";
});
