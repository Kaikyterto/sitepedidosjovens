const pesquisarPedido = document.getElementById("pesquisar-pedido");
const divListaPedidos = document.getElementById("listaPedidos");

pesquisarPedido.addEventListener("input", async (evt) => {
  const valorPesquisa = evt.target.value;

  try {
    const dados = await fetch(
      `https://sitepedidosjovens.onrender.com/pesquisar?nome=${encodeURIComponent(
        valorPesquisa
      )}`,
      { method: "GET", headers: { "Content-Type": "application/json" } }
    );

    dados = await dados.json();
    dados = [...dados];

    dados.forEach((e) => {
      divListaPedidos.innerHTML = `Cliente:${e.cliente}, Produto:${e.produto}, Data:${e.data}`;
    });
  } catch (error) {
    console.error(error);
  }
});
