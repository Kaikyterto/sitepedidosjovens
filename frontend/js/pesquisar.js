const pesquisarPedido = document.getElementById("pesquisar-pedidos");
const divListaPedidos = document.getElementById("listaPedidos");

pesquisarPedido.addEventListener("input", async (evt) => {
  const valorPesquisa = evt.target.value.trim();

  // Evita chamada com campo vazio
  if (!valorPesquisa) {
    divListaPedidos.innerHTML = "";
    return;
  }

  try {
    const resposta = await fetch(
      `https://sitepedidosjovens-4gij.onrender.com/pesquisar?nome=${encodeURIComponent(
        valorPesquisa
      )}`
    );

    if (!resposta.ok) {
      console.log("Erro na API:", resposta.status);
      return;
    }

    const dados = await resposta.json();

    if (!Array.isArray(dados)) return;

    // Limpa antes de renderizar
    divListaPedidos.innerHTML = "";

    dados.forEach((e) => {
      console.log(e);
      divListaPedidos.innerHTML += `
        <p>
          Cliente: ${e.cliente} <br>
          Produto: ${e.produto} <br>
          Data: ${e.data}
        </p>
        <hr>
      `;
    });
  } catch (error) {
    console.error("Erro na pesquisa:", error);
  }
});
