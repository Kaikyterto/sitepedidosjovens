const API_URL = "https://sitepedidosjovens.onrender.com";

/* =========================
   ESTADO GLOBAL
========================= */

let produtos_hoje = [];
let nome_cliente = "";
let produtos_cliente = [];
let total = 0;
carrinho_criado = false;

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
   ELEMENTOS CRIADOS
========================= */

const lista_carrinho = document.createElement("div");
lista_carrinho.id = "lista_carrinho";

const texto_total = document.createElement("h1");
texto_total.id = "texto_total";
texto_total.textContent = "Total: R$ 0,00";

const btn_fechar_pedido = document.createElement("button");
btn_fechar_pedido.id = "btn_fechar_pedido";
btn_fechar_pedido.textContent = "Fechar pedido";

div_conta.appendChild(lista_carrinho);
div_conta.appendChild(texto_total);
div_conta.appendChild(btn_fechar_pedido);

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
   CARREGAR PRODUTOS
========================= */

async function carregarProdutos() {
  try {
    const res = await fetch(`${API_URL}/produtos`);
    const data = await res.json();

    produtos_hoje = data.produtos || [];

    renderizarProdutos();
  } catch (err) {
    console.error(err);
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
    ).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    })}`;

    const btn = document.createElement("button");
    btn.textContent = "Adicionar";
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
  div_conta.style.display = "flex";

  if (carrinho_criado == false) {
    const btn_toggle_carrinho = document.createElement("button");
    btn_toggle_carrinho.id = "btn_toggle_carrinho";
    carrinho_criado = true;
    document.body.appendChild(btn_toggle_carrinho);
  }

  /* estado aberto/fechado */
  let carrinho_aberto = true;
  btn_toggle_carrinho.textContent = carrinho_aberto ? "X" : "🛒";

  btn_toggle_carrinho.addEventListener("click", () => {
    carrinho_aberto = !carrinho_aberto;

    div_conta.style.display = carrinho_aberto ? "flex" : "none";
    btn_toggle_carrinho.textContent = carrinho_aberto ? "X" : "🛒";
  });

  total += Number(produto.preco);

  texto_total.textContent = `Total: ${total.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  })}`;

  let itemExistente = [...lista_carrinho.children].find(
    (el) => el.dataset.nome === produto.nome
  );

  if (itemExistente) {
    let qtd = Number(itemExistente.dataset.qtd) + 1;
    itemExistente.dataset.qtd = qtd;
    itemExistente.querySelector(".qtd").textContent = `${qtd}x`;
  } else {
    const item = document.createElement("div");
    item.classList.add("produto_conta");
    item.dataset.nome = produto.nome;
    item.dataset.qtd = 1;

    const nome = document.createElement("span");
    nome.textContent = produto.nome;

    const qtd = document.createElement("span");
    qtd.classList.add("qtd");
    qtd.textContent = "1x";

    item.append(nome, qtd);

    lista_carrinho.appendChild(item);
  }

  produtos_cliente.push(produto.nome);
}

/* =========================
   PIX HELPERS
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
  const valorStr = Number(valor).toFixed(2);

  const gui = "BR.GOV.BCB.PIX";
  const campo26 = `26${(4 + gui.length + 4 + chave.length)
    .toString()
    .padStart(2, "0")}00${gui.length
    .toString()
    .padStart(2, "0")}${gui}01${chave.length
    .toString()
    .padStart(2, "0")}${chave}`;

  const nomeLimpo = nome.substring(0, 25);
  const cidadeLimpa = cidade.substring(0, 15);

  const payloadSemCRC =
    "000201010212" +
    campo26 +
    "52040000" +
    "5303986" +
    `54${valorStr.length.toString().padStart(2, "0")}${valorStr}` +
    "5802BR" +
    `59${nomeLimpo.length.toString().padStart(2, "0")}${nomeLimpo}` +
    `60${cidadeLimpa.length.toString().padStart(2, "0")}${cidadeLimpa}` +
    `62${(4 + txid.length).toString().padStart(2, "0")}05${txid.length
      .toString()
      .padStart(2, "0")}${txid}` +
    "6304";

  return payloadSemCRC + crc16(payloadSemCRC);
}

/* =========================
   FINALIZAR PEDIDO
========================= */

btn_fechar_pedido.addEventListener("click", async () => {
  try {
    if (produtos_cliente.length === 0) {
      alert("Carrinho vazio");
      return;
    }

    // pedido
    const res = await fetch(`${API_URL}/pedido`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        nome: nome_cliente,
        produtos: produtos_cliente,
      }),
    });

    const json = await res.json();

    if (json.status !== "ok") {
      alert("Erro ao salvar pedido");
      return;
    }

    // pagamento
    const res_pag = await fetch(`${API_URL}/pagamento`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        nome: nome_cliente,
        montante: total,
      }),
    });

    const pagamento = await res_pag.json();

    if (!pagamento.id_pag) {
      alert("Erro no pagamento");
      return;
    }

    document.getElementById("principal").style.display = "none";

    const txid = `PEDIDO${pagamento.id_pag.toString().padStart(5, "0")}`;

    const payload = gerarPix({
      chave: "c400a935-9063-4cea-8fc6-0e2cdb73cbe7",
      nome: "EMILY NATASHA",
      cidade: "SAO PAULO",
      valor: total,
      txid,
    });

    QRCode.toCanvas(document.getElementById("qrcode"), payload, {
      width: 220,
    });

    textarea_pix.value = payload;

    btn_copiar.onclick = () => {
      navigator.clipboard.writeText(payload);
      alert("PIX copiado!");
    };

    div_qrcode.style.display = "flex";
    div_pix_copia_cola.style.display = "flex";
    principal_qr.style.display = "flex";
  } catch (err) {
    console.error(err);
    alert("Erro geral no pedido");
  }
});
