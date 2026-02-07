async function buscarPedidos() {
    try {
      const res = await fetch("/buscar_pedidos");
      if (!res.ok) throw new Error("Erro ao buscar dados: " + res.status);
  
      const dados = await res.json();
      console.log(dados);
  
      const listaPedidos = document.getElementById("listaPedidos");
      listaPedidos.innerHTML = "";
  
      dados.forEach(pedido => {
        const item = document.createElement("div");
        item.classList = "item";
  
        
        const textoPedido = document.createElement("span");
        textoPedido.textContent = `Cliente: ${pedido.cliente} - Produto: ${pedido.produto}`;
  
        
        const btnEntregar = document.createElement("button");
        btnEntregar.textContent = pedido.entregue ? "Entregue" : "Marcar como entregue";
        btnEntregar.disabled = pedido.entregue; 
        btnEntregar.style.marginLeft = "10px";
  
        
        btnEntregar.addEventListener("click", async () => {
          try {
            const res = await fetch("/marcar_entregue", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ id: pedido.id }),
            });
            if (res.ok) {
              btnEntregar.textContent = "Entregue";
              btnEntregar.disabled = true;
            } else {
              const data = await res.json();
              alert("Erro ao atualizar: " + (data.erro || "Erro desconhecido"));
            }
          } catch (error) {
            alert("Erro na comunicação com o servidor");
            console.error(error);
          }
        });
  
        
        item.appendChild(textoPedido);
        item.appendChild(btnEntregar);
  
        listaPedidos.appendChild(item);
      });
  
    } catch (error) {
      console.error(error);
    }
  }
  
  setInterval(buscarPedidos, 2000);

buscarPedidos();