const API_URL = "https://sitepedidosjovens.onrender.com";

/* =========================
   ELEMENTOS
========================= */
const listaProdutos = document.getElementById("listaProdutos");
const pesquisarPedido = document.getElementById("pesquisar-pedidos");
const listaPedidos = document.getElementById("listaPedidos");

/* =========================
   PESQUISA DE PEDIDOS
========================= */
pesquisarPedido.addEventListener("input", async (evt) => {
  const valor = evt.target.value.trim();

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

    if (!res.ok) throw new Error("Erro ao buscar produtos");

    const data = await res.json();

    const produtos = data.produtos || [];

    listaProdutos.innerHTML = "";

    produtos.forEach((p) => {
      const item = document.createElement("div");
      item.classList.add("item");

      const texto = document.createElement("span");
      texto.textContent = `${p.nome} - R$ ${Number(p.preco).toFixed(2)}`;

      const btn = document.createElement("button");

      // estado visual
      btn.textContent = p.disponivel ? "Desativar" : "Ativar";

      btn.addEventListener("click", async () => {
        const novoEstado = !p.disponivel;

        try {
          const res = await fetch(`${API_URL}/produto/disponibilidade`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              nome: p.id,
              disponivel: novoEstado,
            }),
          });

          if (!res.ok) throw new Error("Erro ao atualizar produto");

          // atualiza estado local sem reload pesado
          p.disponivel = novoEstado;
          btn.textContent = novoEstado ? "Desativar" : "Ativar";
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

/* =========================
   INICIALIZAÇÃO
========================= */
carregarProdutos();
