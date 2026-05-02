const API_URL = "https://sitepedidosjovens.onrender.com";

const listaProdutos = document.getElementById("listaProdutos");

const pesquisarPedido = document.getElementById("pesquisar-pedidos");
const listaPedidos = document.getElementById("listaPedidos");

pesquisarPedido.addEventListener("input", async (evt) => {
  const valor = evt.target.value.trim();

  // se vazio, limpa e para
  if (!valor) {
    listaPedidos.innerHTML = "";
    return;
  }

  try {
    const res = await fetch(
      `${API_URL}/pesquisar?nome=${encodeURIComponent(valor)}`
    );

    if (!res.ok) throw new Error("Erro na API");

    const dados = await res.json();

    listaPedidos.innerHTML = "";

    dados.forEach((p) => {
      const item = document.createElement("div");
      item.classList.add("item");

      const texto = document.createElement("span");

      texto.textContent = `${p.cliente} - ${p.produto} - ${p.data}`;

      item.appendChild(texto);
      listaPedidos.appendChild(item);
    });
  } catch (err) {
    console.error("Erro ao pesquisar pedidos:", err);
  }
});

/* =========================
   CARREGAR PRODUTOS
========================= */
async function carregarProdutos() {
  try {
    const res = await fetch(`${API_URL}/produtos`);
    const data = await res.json();

    const produtos = data.produtos;

    listaProdutos.innerHTML = "";

    produtos.forEach((p) => {
      const item = document.createElement("div");
      item.classList.add("item");

      const texto = document.createElement("span");
      texto.textContent = `${p.nome} - R$ ${p.preco}`;

      const btn = document.createElement("button");

      // estado visual
      btn.textContent = p.disponivel ? "Desativar" : "Ativar";
      btn.style.marginLeft = "10px";

      btn.addEventListener("click", async () => {
        const novoEstado = !p.disponivel;

        try {
          const res = await fetch(`${API_URL}/produto/disponibilidade`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              nome: p.nome,
              disponivel: novoEstado,
            }),
          });

          if (!res.ok) throw new Error("Erro ao atualizar");

          // atualiza UI instantâneo
          p.disponivel = novoEstado;
          carregarProdutos();
        } catch (err) {
          console.error(err);
          alert("Erro ao atualizar produto");
        }
      });

      item.appendChild(texto);
      item.appendChild(btn);

      listaProdutos.appendChild(item);
    });
  } catch (error) {
    console.error("Erro ao carregar produtos:", error);
  }
}

/* inicializa */
carregarProdutos();
