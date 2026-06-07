from flask import request, Blueprint, jsonify
from app.models.db import get_cursor, conn
from datetime import datetime

cliente = Blueprint("cliente", __name__)

# ======================
# HEALTH
# ======================
@cliente.route("/health")
def health():
    return jsonify({"status": "ok"})


# ======================
# PRODUTOS
# ======================
@cliente.route("/produtos", methods=["GET"])
def produtos():
    cursor = get_cursor()

    try:
        cursor.execute("""
            SELECT id, nome, preco
            FROM produtos
            WHERE disponivel = TRUE
            ORDER BY id ASC
        """)

        dados = cursor.fetchall()

        produtos = [
            {
                "id": r[0],
                "nome": r[1],
                "preco": float(r[2])
            }
            for r in dados
        ]

        return jsonify({"produtos": produtos})

    except Exception as e:
        print("Erro produtos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close() 

@cliente.route("/allprodutos", methods=["GET"])
def allprodutos():
    cursor = get_cursor()

    try:
        cursor.execute("""
            SELECT id, nome, preco, disponivel
            FROM produtos
            ORDER BY id ASC
        """)

        dados = cursor.fetchall()

        produtos = [
            {
                "id": r[0],
                "nome": r[1],
                "preco": float(r[2]),
                "disponivel": bool(r[3])
            }
            for r in dados
        ]

        return jsonify({"produtos": produtos})

    except Exception as e:
        print("Erro produtos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()

# ======================
# CRIAR PEDIDO
# ======================
@cliente.route("/pedido", methods=["POST"])
def pedido():
    cursor = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    produtos = dados.get("produtos")

    if not nome or not isinstance(produtos, list) or len(produtos) == 0:
        return jsonify({"erro": "Carrinho vazio"}), 400

    try:
        for produto in produtos:
            cursor.execute("""
                INSERT INTO pedidosclientes (cliente, produto, data, entregue)
                VALUES (%s, %s, %s, FALSE)
            """, (nome, produto, datetime.now()))

        conn.commit()

        return jsonify({"status": "ok"})

    except Exception as e:
        conn.rollback()
        print("Erro pedido:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()

@cliente.route("/marcar_entregue", methods=["POST"])
def marcar_entregue():
    cursor = get_cursor()
    dados = request.get_json()

    if not dados or "id" not in dados:
        return jsonify({"erro": "ID obrigatório"}), 400

    try:
        cursor.execute("""
            UPDATE pedidosclientes
            SET entregue = TRUE
            WHERE id = %s
            RETURNING id
        """, (dados["id"],))

        atualizado = cursor.fetchone()

        if not atualizado:
            return jsonify({"erro": "Pedido não encontrado"}), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "id": atualizado[0]
        })

    except Exception as e:
        conn.rollback()
        print("Erro marcar entregue:", e)
        return jsonify({"erro": "Erro ao atualizar pedido"}), 500

@cliente.route("/buscar_pedidos", methods=["GET"])
def buscar_pedidos():
    cursor = get_cursor()

    try:
        cursor.execute("""
            SELECT id, cliente, produto, entregue, data
            FROM pedidosclientes
            WHERE entregue = FALSE
            ORDER BY data DESC
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
        print("Erro buscar pedidos abertos:", e)
        return jsonify({"erro": "Erro ao buscar pedidos"}), 500
    
@cliente.route("/produto/disponibilidade", methods=["POST"])
def alterar_disponibilidade():
    cursor = get_cursor()
    dados = request.get_json()

    # validação
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
            RETURNING id, disponivel
        """, (bool(disponivel), produto_id))

        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"erro": "Produto não encontrado"}), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "id": resultado[0],
            "disponivel": resultado[1]
        })

    except Exception as e:
        conn.rollback()
        print("Erro disponibilidade:", e)
        return jsonify({"erro": "Erro ao atualizar produto"}), 500


# ======================
# PAGAMENTO
# ======================
@cliente.route("/pagamento", methods=["POST"])
def pagamento():
    cursor = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = dados.get("nome")
    montante = dados.get("montante")

    if not nome or montante is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        
        montante = float(montante)

        cursor.execute("""
            INSERT INTO pagamentos (cliente, montante, data)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nome, montante, datetime.now()))

        resultado = cursor.fetchone()

        if not resultado:
            raise Exception("Falha ao retornar ID")

        pagamento_id = resultado[0]

        conn.commit()

        return jsonify({
            "status": "ok",
            "id_pag": pagamento_id
        })

    except Exception as e:
        conn.rollback()
        print("Erro pagamento:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()

# ======================
# PESQUISAR PEDIDOS
# ======================
@cliente.route("/pesquisar", methods=["GET"])
def pesquisar_pedidos():
    cursor = get_cursor()
    nome = request.args.get("nome", "").strip().lower()
    try:
        cursor.execute("""
            SELECT id, cliente, produto, data
            FROM pedidosclientes
            WHERE LOWER(cliente) LIKE %s
            ORDER BY data DESC
        """, (f"%{nome}%",))
        resultados = cursor.fetchall()
        pedidos = [
            {
                "id": r[0],
                "cliente": r[1],
                "produto": r[2],
                "data": r[3].isoformat() if r[3] else None
            }
            for r in resultados
        ]
        return jsonify(pedidos)
    except Exception as e:
        print("Erro pesquisar pedidos:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()