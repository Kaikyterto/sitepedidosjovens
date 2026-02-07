class Produto {
    constructor(nome, preco) {
        this.nome = nome
        this.preco = preco
    }
}

const pix_mae = new Produto('pix de mãe',23.00)
const bolo_milho = new Produto('Bolo de milho', 3.00)
const bolo_chocolate = new Produto('Bolo de chocolate', 3.00)
const sopa = new Produto('Sopa', 3.00)
const cookies_p = new Produto('Cookie P', 3.00)
const cookies_m = new Produto('Cookie M', 6.00)
const cookies_g = new Produto('Cookie G', 12.50)
const brownie = new Produto('Brownie', 3.00)
const cafe = new Produto('Café', 0.50)

const produtos_hoje = [bolo_chocolate,cafe,cookies_m,cookies_p]

const div_principal = document.getElementById("principal")
const btn_nome = document.getElementById("btn_nome")
const nome_usuario = document.getElementById("nome_usuario")
const caixa_nome = document.getElementById("caixa_nome")
const cardapio = document.getElementById("cardapio")
const div_conta = document.getElementById("div_conta")

const principal_qr = document.getElementById("principal_qr")
const div_qrcode = document.getElementById("div_qrcode")
const div_pix_copia_cola = document.getElementById("div_pix-copia-cola")
const textarea_pix = document.getElementById("pix-copia-cola")
const btn_copiar = document.getElementById("btn-copiar")

const h1_total = document.createElement('h1')
h1_total.id = 'texto_total'
h1_total.textContent = 'Total: R$ 0,00'

const btn_fechar_pedido = document.createElement('button')
btn_fechar_pedido.id = 'btn_fechar_pedido'
btn_fechar_pedido.textContent = 'Fechar pedido'

let nome_cliente = ''
let produtos_cliente = []
let total = 0

btn_nome.addEventListener('click', (e) => {
    e.preventDefault()

    nome_cliente = nome_usuario.value.trim()
    if (!nome_cliente) return alert("Digite seu nome")

    caixa_nome.remove()
    cardapio.style.display = "flex"
})

produtos_hoje.forEach((produto) => {

    const div_produto = document.createElement('div')
    div_produto.classList.add('produto')

    const span = document.createElement('span')
    span.classList.add('texto_produto')
    span.textContent = `${produto.nome} - ${produto.preco.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    })}`

    const btn = document.createElement('button')
    btn.type = 'button'
    btn.classList.add('btn_produto')

    btn.addEventListener('click', () => {

        produtos_cliente.push(produto)

        total += produto.preco
        h1_total.textContent = `Total: ${total.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        })}`

        div_conta.style.display = "flex"

        let item = [...div_conta.children].find(el => el.dataset?.nome === produto.nome)

        if (item) {
            let qtd = Number(item.dataset.qtd) + 1
            item.dataset.qtd = qtd
            item.querySelector('.qtd').textContent = `${qtd}x`
        } else {
            const item_conta = document.createElement('div')
            item_conta.classList.add('produto_conta')
            item_conta.dataset.nome = produto.nome
            item_conta.dataset.qtd = 1

            const nome = document.createElement('span')
            nome.textContent = produto.nome

            const qtd = document.createElement('span')
            qtd.classList.add('qtd')
            qtd.textContent = '1x'

            item_conta.append(nome, qtd)
            if (div_conta.contains(h1_total)) div_conta.removeChild(h1_total);
            if (div_conta.contains(btn_fechar_pedido)) div_conta.removeChild(btn_fechar_pedido);
            div_conta.appendChild(item_conta);
            div_conta.appendChild(h1_total);
            div_conta.appendChild(btn_fechar_pedido);
        }

        if (!div_conta.contains(h1_total)) {
            div_conta.appendChild(h1_total);
        }
        if (!div_conta.contains(btn_fechar_pedido)) {
            div_conta.appendChild(btn_fechar_pedido);
        }
    })

    div_produto.append(span, btn)
    cardapio.appendChild(div_produto)
})

function crc16(payload) {
    let polinomio = 0x1021
    let resultado = 0xFFFF

    for (let i = 0; i < payload.length; i++) {
        resultado ^= payload.charCodeAt(i) << 8
        for (let j = 0; j < 8; j++) {
            if ((resultado <<= 1) & 0x10000) {
                resultado ^= polinomio
            }
            resultado &= 0xFFFF
        }
    }
    return resultado.toString(16).toUpperCase().padStart(4, '0')
}

function gerarPix({ chave, nome, cidade, valor, txid }) {
    const valorStr = valor.toFixed(2); // ponto decimal, não vírgula

    const gui = "BR.GOV.BCB.PIX";
    const guiLength = gui.length.toString().padStart(2, '0');

    const chaveLength = chave.length.toString().padStart(2, '0');
    const campo26Conteudo = `00${guiLength}${gui}01${chaveLength}${chave}`;
    const campo26Length = campo26Conteudo.length.toString().padStart(2, '0');
    const campo26 = `26${campo26Length}${campo26Conteudo}`;

    const txidVal = txid.length > 25 ? txid.slice(0, 25) : txid;
    const txidLength = txidVal.length.toString().padStart(2, '0');
    const campo62Conteudo = `05${txidLength}${txidVal}`;
    const campo62Length = campo62Conteudo.length.toString().padStart(2, '0');
    const campo62 = `62${campo62Length}${campo62Conteudo}`;

    const nomeLength = nome.length.toString().padStart(2, '0');
    const cidadeLength = cidade.length.toString().padStart(2, '0');
    const valorLength = valorStr.length.toString().padStart(2, '0');

    const payloadSemCRC =
        "000201" +
        "010212" +
        campo26 +
        "52040000" +
        "5303986" +
        "54" + valorLength + valorStr +
        "58" + "02" + "BR" +
        "59" + nomeLength + nome +
        "60" + cidadeLength + cidade +
        campo62 +
        "6304";

    const crc = crc16(payloadSemCRC);
    return payloadSemCRC + crc;
}


  



btn_fechar_pedido.addEventListener('click', async () => {

    for (const produto of produtos_cliente) {
        const res = await fetch("/pedir", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                nome: nome_cliente,
                produto: produto.nome
            })
        })

        const json = await res.json()
        if (json.status !== "ok") {
            alert("Erro ao salvar pedido")
            return
        }
    }

    const res_pag = await fetch("/pagamento", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nome: nome_cliente,
            montante: total
        })
    })

    const pagamento = await res_pag.json()
    if (pagamento.status !== "ok") {
        alert("Erro no pagamento")
        return
    }

    const txid = `PEDIDO${pagamento.id_pag.toString().padStart(5, '0')}`

    const payload = gerarPix({
        chave: "c400a935-9063-4cea-8fc6-0e2cdb73cbe7",
        nome: "Emily Natasha Mergulhao d",
        cidade: "SAO PAULO",
        valor: total,
        txid: txid
    })

    QRCode.toCanvas(
        document.getElementById("qrcode"),
        payload,
        { width: 250 }
    )

    textarea_pix.value = payload

    btn_copiar.onclick = () => {
        navigator.clipboard.writeText(payload)
        alert("PIX copiado!")
    }

    cardapio.style.display = "none"
    div_conta.style.display = "none"
    div_qrcode.style.display = "flex"
    div_pix_copia_cola.style.display = "flex"
    principal_qr.style.display = "flex"
    principal_qr.style.flexDirection = "column"
    principal_qr.style.gap = "20px"
})
