from flask import request, Blueprint, jsonify
from app.models.db import cursor, conn
from datetime import datetime

cliente = Blueprint("cliente", __name__)

# ======================
# HEALTH CHECK
# ======================
@cliente.route("/health")
def health():
    print("Acordando servidor")
    return jsonify({"status": "ok"})


# ======================
# PRODUTOS (FRONT BUSCA AQUI)
# ======================
@cliente.route("/produtos", methods=["GET"])
def produtos():
    try:
        cursor.execute("""
            SELECT nome, preco
            FROM produtos
            WHERE disponivel = TRUE
            ORDER BY id ASC
        """)
        resultados = cursor.fetchall()

        produtos = [
            {
                "nome": r[0],
                "preco": float(r[1])
            }
            for r in resultados
        ]

        return jsonify({"produtos": produtos})

    except Exception as e:
        print("Erro ao buscar produtos:", e)
        return jsonify({"erro": "Erro ao buscar produtos"}), 500


# ======================
# CRIAR PEDIDO (NOVO MODELO)
# ======================
@cliente.route("/pedido", methods=["POST"])
def pedido():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    produtos = dados.get("produtos")
    montante = dados.get("montante")

    if not nome or not produtos:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        for produto in produtos:
            cursor.execute("""
                INSERT INTO pedidosclientes (cliente, produto, data, entregue)
                VALUES (%s, %s, %s, %s)
            """, (nome, produto, datetime.now(), False))

        conn.commit()

        return jsonify({"status": "ok"})

    except Exception as e:
        conn.rollback()
        print("Erro ao salvar pedido:", e)
        return jsonify({"erro": "Erro ao salvar pedido"}), 500


# ======================
# BUSCAR PEDIDOS (ADMIN)
# ======================
@cliente.route("/buscar_pedidos", methods=["GET"])
def buscar_pedidos():
    try:
        cursor.execute("""
            SELECT id, cliente, produto, entregue, data
            FROM pedidosclientes
            WHERE data::date = CURRENT_DATE
            ORDER BY data ASC
        """)
        resultados = cursor.fetchall()

        pedidos = [
            {
                "id": r[0],
                "cliente": r[1],
                "produto": r[2],
                "entregue": r[3],
                "data": r[4].isoformat() if r[4] else None
            }
            for r in resultados
        ]

        return jsonify(pedidos)

    except Exception as e:
        conn.rollback()
        print("Erro ao buscar pedidos:", e)
        return jsonify({"erro": "Erro ao buscar pedidos"}), 500
    
# ======================
# ALTERAR DISPONIBILIDADE DO PRODUTO (ADMIN)
# ======================
@cliente.route("/produto/disponibilidade", methods=["POST"])
def alterar_disponibilidade():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    disponivel = dados.get("disponivel")

    if nome is None or disponivel is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        cursor.execute("""
            UPDATE produtos
            SET disponivel = %s
            WHERE nome = %s
        """, (disponivel, nome))

        conn.commit()

        return jsonify({"status": "ok"})

    except Exception as e:
        conn.rollback()
        print("Erro ao atualizar disponibilidade:", e)
        return jsonify({"erro": "Erro ao atualizar produto"}), 500


# ======================
# MARCAR COMO ENTREGUE
# ======================
@cliente.route("/marcar_entregue", methods=["POST"])
def marcar_entregue():
    dados = request.get_json(silent=True)

    if not dados or "id" not in dados:
        return jsonify({"erro": "ID do pedido é obrigatório"}), 400

    try:
        cursor.execute("""
            UPDATE pedidosclientes
            SET entregue = TRUE
            WHERE id = %s
        """, (dados["id"],))

        conn.commit()
        return jsonify({"status": "ok"})

    except Exception as e:
        conn.rollback()
        print("Erro ao atualizar pedido:", e)
        return jsonify({"erro": "Erro ao atualizar pedido"}), 500


# ======================
# PAGAMENTO PIX
# ======================
@cliente.route("/pagamento", methods=["POST"])
def pagamento():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    cliente_nome = dados.get("nome")
    montante = dados.get("montante")

    if not cliente_nome or montante is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        cursor.execute("""
            INSERT INTO pagamentos (cliente, montante, data)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (cliente_nome, montante, datetime.now()))

        pagamento_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "status": "ok",
            "id_pag": pagamento_id
        })

    except Exception as e:
        conn.rollback()
        print("Erro ao inserir pagamento:", e)
        return jsonify({"erro": "Erro ao inserir pagamento"}), 500


# ======================
# PESQUISA DE PEDIDOS
# ======================
@cliente.route("/pesquisar")
def pesquisar():

    cliente_nome = request.args.get("nome")

    if not cliente_nome:
        return jsonify({"erro": "Dados incompletos"}), 400

    cliente_nome = cliente_nome.strip()

    try:
        cursor.execute("""
            SELECT cliente, produto, data
            FROM pedidosclientes
            WHERE LOWER(cliente) LIKE LOWER(%s)
            ORDER BY data ASC
        """, (f"%{cliente_nome}%",))

        resultados = cursor.fetchall()

    except Exception as e:
        conn.rollback()
        print("Erro ao pesquisar pedidos:", e)
        return jsonify({"erro": "Erro ao pesquisar pedidos"}), 500

    pedidos = [
        {
            "cliente": r[0],
            "produto": r[1],
            "data": r[2].isoformat() if r[2] else None
        }
        for r in resultados
    ]

    return jsonify(pedidos)