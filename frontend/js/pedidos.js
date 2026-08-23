const API_URL = "https://sitepedidosjovens-vztj.onrender.com";

/* =========================
   BUSCAR PEDIDOS
========================= */

async function buscarPedidos() {
  try {
    const res = await fetch(`${API_URL}/buscar_pedidos`);

    if (!res.ok) {
      throw new Error("Erro ao buscar pedidos: " + res.status);
    }

    const dados = await res.json();

    const listaPedidos = document.getElementById("listaPedidos");
    listaPedidos.innerHTML = "";

    dados
      .sort((a, b) => new Date(b.data) - new Date(a.data)) // mais recentes primeiro
      .forEach((pedido) => {
        const item = document.createElement("div");
        item.className = "item";

        /* =========================
           TEXTO DO PEDIDO
        ========================= */
        const textoPedido = document.createElement("span");

        textoPedido.textContent = `👤 ${pedido.cliente} | ${pedido.produto}`;

        if (pedido.entregue) {
          textoPedido.style.opacity = "0.5";
          textoPedido.textContent += " ✔ entregue";
        }

        /* =========================
           BOTÃO ENTREGAR
        ========================= */
        const btnEntregar = document.createElement("button");

        btnEntregar.textContent = pedido.entregue
          ? "Entregue"
          : "Marcar entregue";

        btnEntregar.disabled = pedido.entregue;

        btnEntregar.style.marginLeft = "10px";

        btnEntregar.addEventListener("click", async () => {
          try {
            const res = await fetch(`${API_URL}/marcar_entregue`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ id: pedido.id }),
            });

            if (!res.ok) {
              throw new Error("Erro ao atualizar pedido");
            }

            btnEntregar.textContent = "Entregue";
            btnEntregar.disabled = true;

            textoPedido.style.opacity = "0.5";
          } catch (error) {
            console.error(error);
            alert("Erro ao comunicar com o servidor");
          }
        });

        /* =========================
           MONTAGEM
        ========================= */
        item.appendChild(textoPedido);
        item.appendChild(btnEntregar);

        listaPedidos.appendChild(item);
      });
  } catch (error) {
    console.error("Erro geral:", error);
  }
}

/* =========================
   AUTO UPDATE (TEMPO REAL SIMPLES)
========================= */

setInterval(buscarPedidos, 2000);

buscarPedidos();
