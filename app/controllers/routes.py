from flask import request, Blueprint, jsonify
from app.models.db import cursor, conn
from datetime import datetime

cliente = Blueprint("cliente", __name__)

# ======================
# HEALTH CHECK
# ======================
@cliente.route("/health")
def health():
    return jsonify({"status": "ok"})


# ======================
# PRODUTOS (FRONT)
# ======================
@cliente.route("/produtos", methods=["GET"])
def produtos():
    try:
        cursor.execute("""
            SELECT id, nome, preco, disponivel
            FROM produtos
            ORDER BY id ASC
        """)
        resultados = cursor.fetchall()

        produtos = [
            {
                "id": r[0],
                "nome": r[1],
                "preco": float(r[2]),
                "disponivel": r[3]
            }
            for r in resultados
        ]

        return jsonify({"produtos": produtos})

    except Exception as e:
        print("Erro ao buscar produtos:", e)
        return jsonify({"erro": "Erro ao buscar produtos"}), 500


# ======================
# ALTERAR DISPONIBILIDADE (ADMIN)
# ======================
@cliente.route("/produto/disponibilidade", methods=["POST"])
def alterar_disponibilidade():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    produto_id = dados.get("id")
    disponivel = dados.get("disponivel")

    if produto_id is None or disponivel is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        cursor.execute("""
            UPDATE produtos
            SET disponivel = %s
            WHERE id = %s
        """, (disponivel, produto_id))

        conn.commit()

        return jsonify({"status": "ok"})

    except Exception as e:
        conn.rollback()
        print("Erro ao atualizar produto:", e)
        return jsonify({"erro": "Erro ao atualizar produto"}), 500


# ======================
# CRIAR PEDIDO
# ======================
@cliente.route("/pedido", methods=["POST"])
def pedido():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    produtos = dados.get("produtos")

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
        return jsonify({"erro": "Erro ao buscar pedidos"}), 500


# ======================
# MARCAR ENTREGUE
# ======================
@cliente.route("/marcar_entregue", methods=["POST"])
def marcar_entregue():
    dados = request.get_json(silent=True)

    if not dados or "id" not in dados:
        return jsonify({"erro": "ID obrigatório"}), 400

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
        return jsonify({"erro": "Erro ao atualizar"}), 500


# ======================
# PAGAMENTO
# ======================
@cliente.route("/pagamento", methods=["POST"])
def pagamento():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    montante = dados.get("montante")

    if not nome or montante is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        cursor.execute("""
            INSERT INTO pagamentos (cliente, montante, data)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nome, montante, datetime.now()))

        pagamento_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "status": "ok",
            "id_pag": pagamento_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": "Erro no pagamento"}), 500


# ======================
# PESQUISA PEDIDOS
# ======================
@cliente.route("/pesquisar")
def pesquisar():
    nome = request.args.get("nome")

    if not nome:
        return jsonify({"erro": "Nome obrigatório"}), 400

    try:
        cursor.execute("""
            SELECT cliente, produto, data
            FROM pedidosclientes
            WHERE LOWER(cliente) LIKE LOWER(%s)
            ORDER BY data ASC
        """, (f"%{nome}%",))

        resultados = cursor.fetchall()

        pedidos = [
            {
                "cliente": r[0],
                "produto": r[1],
                "data": r[2].isoformat() if r[2] else None
            }
            for r in resultados
        ]

        return jsonify(pedidos)

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": "Erro na pesquisa"}), 500