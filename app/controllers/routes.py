from flask import request, Blueprint, jsonify
from models.db import cursor, conn
from datetime import datetime

cliente = Blueprint("cliente", __name__)

# ======================
# BUSCAR PEDIDOS
# ======================
@cliente.route("/buscar_pedidos", methods=["GET"])
def buscar_pedidos():
    try:
        cursor.execute("""
            SELECT id, cliente, produto, entregue
            FROM pedidosclientes
            WHERE data::date = CURRENT_DATE
            AND entregue = FALSE
        """)
        resultados = cursor.fetchall()

        pedidos = [
            {
                "id": r[0],
                "cliente": r[1],
                "produto": r[2],
                "entregue": r[3]
            }
            for r in resultados
        ]

        return jsonify(pedidos)

    except Exception as e:
        conn.rollback()
        print("Erro ao buscar pedidos:", e)
        return jsonify({"erro": "Erro ao buscar pedidos"}), 500


# ======================
# FAZER PEDIDO
# ======================
@cliente.route("/pedir", methods=["POST"])
def pedir():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    produto = dados.get("produto")

    if not nome or not produto:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        cursor.execute("""
            INSERT INTO pedidosclientes (cliente, produto, data)
            VALUES (%s, %s, %s)
        """, (nome, produto, datetime.now()))

        conn.commit()
        return jsonify({"status": "ok"})

    except Exception as e:
        conn.rollback()
        print("Erro ao salvar pedido:", e)
        return jsonify({"erro": "Erro ao salvar pedido"}), 500


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
# PAGAMENTO
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
            INSERT INTO pagamentos (cliente, montante)
            VALUES (%s, %s)
            RETURNING id
        """, (cliente_nome, montante))

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


@cliente.route("/health")
def health():
    print("Acordando servidor")
    return jsonify({"status": "ok"})

@cliente.route("/pesquisar")
def pesquisar():

    cliente = request.args.get("nome")

    if not cliente:
        return jsonify({"erro": "Dados incompletos"}), 400

    cliente = cliente.strip().title()

    try:
        cursor.execute("""
            SELECT cliente, produto, data 
            FROM pedidosclientes 
            WHERE cliente = %s
            ORDER BY data ASC
        """, (cliente,))
        resultados = cursor.fetchall()
    except Exception as e:
        conn.rollback()
        print("Erro ao pesquisar pedidos:", e)
        return jsonify({"erro": "Erro ao pesquisar pedidos"}), 500

    pedidos = [{"cliente": r[0], "produto": r[1], "data": r[2]} for r in resultados]

    return jsonify(pedidos)
