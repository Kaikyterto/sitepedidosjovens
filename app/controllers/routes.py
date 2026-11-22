from flask import request, Blueprint, jsonify
from app.models.db import get_cursor
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
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            SELECT id, nome, preco
            FROM produtos
            WHERE disponivel = TRUE
            ORDER BY id ASC
        """)

        dados = cursor.fetchall()

        produtos_lista = [
            {
                "id": r[0],
                "nome": r[1],
                "preco": float(r[2])
            }
            for r in dados
        ]

        return jsonify({"produtos": produtos_lista})

    except Exception as e:
        print("Erro produtos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# PESQUISAR CLIENTE/PEDIDO
# ======================
@cliente.route("/pesquisar", methods=["GET"])
def pesquisar():
    nome_pesquisa = request.args.get("nome")

    if not nome_pesquisa:
        return jsonify({"erro": "Parâmetro 'nome' é obrigatório"}), 400

    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            SELECT id, cliente, produto, entregue, data
            FROM pedidosclientes
            WHERE cliente ILIKE %s
            ORDER BY data DESC
        """, (f"%{nome_pesquisa}%",))

        resultados = cursor.fetchall()

        pedidos = [
            {
                "id": r[0],
                "cliente": r[1],
                "produto": r[2],
                "entregue": r[3],
                "data": r[4].isoformat()
            }
            for r in resultados
        ]

        return jsonify(pedidos)

    except Exception as e:
        print("Erro pesquisar:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/allprodutos", methods=["GET"])
def allprodutos():
    cursor, conn = get_cursor()

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
        print("Erro allprodutos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# CRIAR PEDIDO
# ======================
@cliente.route("/pedido", methods=["POST"])
def pedido():
    cursor, conn = get_cursor()

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
                INSERT INTO pedidosclientes
                (cliente, produto, data, entregue)
                VALUES (%s, %s, %s, FALSE)
            """, (
                nome,
                produto,
                datetime.now()
            ))

        conn.commit()

        return jsonify({
            "status": "ok"
        })

    except Exception as e:
        conn.rollback()
        print("Erro pedido:", e)
        return jsonify({
            "erro": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# MARCAR ENTREGUE
# ======================
@cliente.route("/marcar_entregue", methods=["POST"])
def marcar_entregue():
    cursor, conn = get_cursor()

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

        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({
                "erro": "Pedido não encontrado"
            }), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "id": resultado[0]
        })

    except Exception as e:
        conn.rollback()
        print("Erro entregar:", e)
        return jsonify({
            "erro": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# BUSCAR PEDIDOS
# ======================
@cliente.route("/buscar_pedidos", methods=["GET"])
def buscar_pedidos():
    cursor, conn = get_cursor()

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
                "data": r[4].isoformat()
            }
            for r in resultados
        ]

        return jsonify(pedidos)

    except Exception as e:
        print("Erro pedidos:", e)
        return jsonify({
            "erro": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# ALTERAR DISPONIBILIDADE
# ======================
@cliente.route("/produto/disponibilidade", methods=["POST"])
def alterar_disponibilidade():
    cursor, conn = get_cursor()

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    try:
        cursor.execute("""
            UPDATE produtos
            SET disponivel = %s
            WHERE id = %s
            RETURNING id, disponivel
        """, (
            bool(dados["disponivel"]),
            dados["id"]
        ))

        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({
                "erro": "Produto não encontrado"
            }), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "id": resultado[0],
            "disponivel": resultado[1]
        })

    except Exception as e:
        conn.rollback()
        print("Erro disponibilidade:", e)
        return jsonify({
            "erro": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# REGISTRAR PAGAMENTO (CRIAR)
# ======================
@cliente.route("/pagamento", methods=["POST"])
def pagamento():
    cursor, conn = get_cursor()

    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "erro": "JSON inválido"
        }), 400

    try:
        cursor.execute("""
            INSERT INTO pagamentos
            (cliente, montante, data, pago)
            VALUES (%s, %s, %s, FALSE)
            RETURNING id
        """, (
            dados["nome"],
            float(dados["montante"]),
            datetime.now()
        ))

        resultado = cursor.fetchone()
        conn.commit()

        return jsonify({
            "status": "ok",
            "id_pag": resultado[0]
        })

    except Exception as e:
        conn.rollback()
        print("Erro pagamento:", e)
        return jsonify({
            "erro": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# LISTAR PAGAMENTOS (NOVA ROTA)
# ======================
@cliente.route("/pagamentos", methods=["GET"])
def listar_pagamentos():
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            SELECT id, cliente, montante, data, pago
            FROM pagamentos
            ORDER BY data DESC
        """)

        resultados = cursor.fetchall()

        lista = [
            {
                "id": r[0],
                "cliente": r[1],
                "montante": float(r[2]),
                "data": r[3].isoformat() if r[3] else None,
                "pago": bool(r[4])
            }
            for r in resultados
        ]

        return jsonify(lista)

    except Exception as e:
        print("Erro listar pagamentos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# ATUALIZAR STATUS DE PAGAMENTO (NOVA ROTA)
# ======================
@cliente.route("/pagamento/pago", methods=["POST"])
def marcar_pagamento_pago():
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados or "id" not in dados:
        return jsonify({"erro": "ID obrigatório"}), 400

    try:
        cursor.execute("""
            UPDATE pagamentos
            SET pago = %s
            WHERE id = %s
            RETURNING id
        """, (
            bool(dados.get("pago", True)),
            dados["id"]
        ))

        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"erro": "Pagamento não encontrado"}), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "id": resultado[0]
        })

    except Exception as e:
        conn.rollback()
        print("Erro ao atualizar pagamento:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# JOGO: CAMPEONATOS (CRUD)
# ======================
@cliente.route("/jogo/campeonatos", methods=["GET"])
def listar_campeonatos():
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            SELECT id, nome, ativo, criado_em
            FROM campeonatos
            ORDER BY id DESC
        """)
        dados = cursor.fetchall()

        campeonatos = [
            {
                "id": r[0],
                "nome": r[1],
                "ativo": bool(r[2]),
                "criado_em": r[3].isoformat() if r[3] else None
            }
            for r in dados
        ]

        return jsonify({"campeonatos": campeonatos})

    except Exception as e:
        print("Erro listar campeonatos:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/campeonatos", methods=["POST"])
def criar_campeonato():
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = (dados.get("nome") or "").strip()
    ativo = bool(dados.get("ativo", True))

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    try:
        cursor.execute("""
            INSERT INTO campeonatos (nome, ativo)
            VALUES (%s, %s)
            RETURNING id, nome, ativo, criado_em
        """, (nome, ativo))

        r = cursor.fetchone()
        conn.commit()

        return jsonify({
            "status": "ok",
            "campeonato": {
                "id": r[0],
                "nome": r[1],
                "ativo": bool(r[2]),
                "criado_em": r[3].isoformat() if r[3] else None
            }
        }), 201

    except Exception as e:
        conn.rollback()
        print("Erro criar campeonato:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/campeonatos/<int:campeonato_id>", methods=["PUT", "PATCH"])
def atualizar_campeonato(campeonato_id):
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    campos = []
    valores = []

    if "nome" in dados:
        nome = (dados.get("nome") or "").strip()
        if not nome:
            return jsonify({"erro": "Nome não pode ser vazio"}), 400
        campos.append("nome = %s")
        valores.append(nome)

    if "ativo" in dados:
        campos.append("ativo = %s")
        valores.append(bool(dados["ativo"]))

    if not campos:
        return jsonify({"erro": "Informe 'nome' ou 'ativo'"}), 400

    valores.append(campeonato_id)

    try:
        cursor.execute(f"""
            UPDATE campeonatos
            SET {", ".join(campos)}
            WHERE id = %s
            RETURNING id, nome, ativo, criado_em
        """, valores)

        r = cursor.fetchone()
        if not r:
            conn.rollback()
            return jsonify({"erro": "Campeonato não encontrado"}), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "campeonato": {
                "id": r[0],
                "nome": r[1],
                "ativo": bool(r[2]),
                "criado_em": r[3].isoformat() if r[3] else None
            }
        })

    except Exception as e:
        conn.rollback()
        print("Erro atualizar campeonato:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/campeonatos/<int:campeonato_id>", methods=["DELETE"])
def deletar_campeonato(campeonato_id):
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            DELETE FROM campeonatos
            WHERE id = %s
            RETURNING id
        """, (campeonato_id,))

        r = cursor.fetchone()
        if not r:
            conn.rollback()
            return jsonify({"erro": "Campeonato não encontrado"}), 404

        conn.commit()

        return jsonify({"status": "ok", "id": r[0]})

    except Exception as e:
        conn.rollback()
        print("Erro deletar campeonato:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# JOGO: JOGADORES (CRUD)
# ======================
@cliente.route("/jogo/jogadores", methods=["GET"])
def listar_jogadores():
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            SELECT id, nome, criado_em
            FROM jogadores
            ORDER BY id ASC
        """)
        dados = cursor.fetchall()

        jogadores = [
            {
                "id": r[0],
                "nome": r[1],
                "criado_em": r[2].isoformat() if r[2] else None
            }
            for r in dados
        ]

        return jsonify({"jogadores": jogadores})

    except Exception as e:
        print("Erro listar jogadores:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/jogadores", methods=["POST"])
def criar_jogador():
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = (dados.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    try:
        cursor.execute("""
            INSERT INTO jogadores (nome)
            VALUES (%s)
            RETURNING id, nome, criado_em
        """, (nome,))

        r = cursor.fetchone()
        conn.commit()

        return jsonify({
            "status": "ok",
            "jogador": {
                "id": r[0],
                "nome": r[1],
                "criado_em": r[2].isoformat() if r[2] else None
            }
        }), 201

    except Exception as e:
        conn.rollback()
        print("Erro criar jogador:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/jogadores/<int:jogador_id>", methods=["PUT", "PATCH"])
def atualizar_jogador(jogador_id):
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    nome = (dados.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400

    try:
        cursor.execute("""
            UPDATE jogadores
            SET nome = %s
            WHERE id = %s
            RETURNING id, nome, criado_em
        """, (nome, jogador_id))

        r = cursor.fetchone()
        if not r:
            conn.rollback()
            return jsonify({"erro": "Jogador não encontrado"}), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "jogador": {
                "id": r[0],
                "nome": r[1],
                "criado_em": r[2].isoformat() if r[2] else None
            }
        })

    except Exception as e:
        conn.rollback()
        print("Erro atualizar jogador:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/jogadores/<int:jogador_id>", methods=["DELETE"])
def deletar_jogador(jogador_id):
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            DELETE FROM jogadores
            WHERE id = %s
            RETURNING id
        """, (jogador_id,))

        r = cursor.fetchone()
        if not r:
            conn.rollback()
            return jsonify({"erro": "Jogador não encontrado"}), 404

        conn.commit()

        return jsonify({"status": "ok", "id": r[0]})

    except Exception as e:
        conn.rollback()
        print("Erro deletar jogador:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# JOGO: PERGUNTAS (CRUD)
# ======================
@cliente.route("/jogo/perguntas", methods=["GET"])
def listar_perguntas():
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            SELECT id, enunciado, resposta_correta, pontos
            FROM perguntas
            ORDER BY id ASC
        """)
        dados = cursor.fetchall()

        perguntas = [
            {
                "id": r[0],
                "enunciado": r[1],
                "resposta_correta": r[2],
                "pontos": int(r[3])
            }
            for r in dados
        ]

        return jsonify({"perguntas": perguntas})

    except Exception as e:
        print("Erro listar perguntas:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/perguntas", methods=["POST"])
def criar_pergunta():
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    enunciado = (dados.get("enunciado") or "").strip()
    resposta_correta = dados.get("resposta_correta")
    pontos = dados.get("pontos", 1)

    if not enunciado:
        return jsonify({"erro": "Enunciado é obrigatório"}), 400

    try:
        pontos = int(pontos)
        if pontos < 0:
            return jsonify({"erro": "Pontos deve ser maior ou igual a 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"erro": "Pontos deve ser um número inteiro"}), 400

    if isinstance(resposta_correta, str):
        resposta_correta = resposta_correta.strip()

    try:
        cursor.execute("""
            INSERT INTO perguntas (enunciado, resposta_correta, pontos)
            VALUES (%s, %s, %s)
            RETURNING id, enunciado, resposta_correta, pontos
        """, (enunciado, resposta_correta, pontos))

        r = cursor.fetchone()
        conn.commit()

        return jsonify({
            "status": "ok",
            "pergunta": {
                "id": r[0],
                "enunciado": r[1],
                "resposta_correta": r[2],
                "pontos": int(r[3])
            }
        }), 201

    except Exception as e:
        conn.rollback()
        print("Erro criar pergunta:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/perguntas/<int:pergunta_id>", methods=["PUT", "PATCH"])
def atualizar_pergunta(pergunta_id):
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    campos = []
    valores = []

    if "enunciado" in dados:
        enunciado = (dados.get("enunciado") or "").strip()
        if not enunciado:
            return jsonify({"erro": "Enunciado não pode ser vazio"}), 400
        campos.append("enunciado = %s")
        valores.append(enunciado)

    if "resposta_correta" in dados:
        resp = dados.get("resposta_correta")
        if isinstance(resp, str):
            resp = resp.strip()
        campos.append("resposta_correta = %s")
        valores.append(resp)

    if "pontos" in dados:
        try:
            pontos = int(dados.get("pontos"))
            if pontos < 0:
                return jsonify({"erro": "Pontos deve ser maior ou igual a 0"}), 400
        except (TypeError, ValueError):
            return jsonify({"erro": "Pontos deve ser um número inteiro"}), 400
        campos.append("pontos = %s")
        valores.append(pontos)

    if not campos:
        return jsonify({"erro": "Nenhum campo para atualizar"}), 400

    valores.append(pergunta_id)

    try:
        cursor.execute(f"""
            UPDATE perguntas
            SET {", ".join(campos)}
            WHERE id = %s
            RETURNING id, enunciado, resposta_correta, pontos
        """, valores)

        r = cursor.fetchone()
        if not r:
            conn.rollback()
            return jsonify({"erro": "Pergunta não encontrada"}), 404

        conn.commit()

        return jsonify({
            "status": "ok",
            "pergunta": {
                "id": r[0],
                "enunciado": r[1],
                "resposta_correta": r[2],
                "pontos": int(r[3])
            }
        })

    except Exception as e:
        conn.rollback()
        print("Erro atualizar pergunta:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@cliente.route("/jogo/perguntas/<int:pergunta_id>", methods=["DELETE"])
def deletar_pergunta(pergunta_id):
    cursor, conn = get_cursor()

    try:
        cursor.execute("""
            DELETE FROM perguntas
            WHERE id = %s
            RETURNING id
        """, (pergunta_id,))

        r = cursor.fetchone()
        if not r:
            conn.rollback()
            return jsonify({"erro": "Pergunta não encontrada"}), 404

        conn.commit()

        return jsonify({"status": "ok", "id": r[0]})

    except Exception as e:
        conn.rollback()
        print("Erro deletar pergunta:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# JOGO: RESPONDER (REGISTRAR ACERTO)
# ======================
@cliente.route("/jogo/responder", methods=["POST"])
def responder_pergunta():
    cursor, conn = get_cursor()
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    campeonato_id = dados.get("campeonato_id")
    jogador_id = dados.get("jogador_id")
    pergunta_id = dados.get("pergunta_id")
    pontos_ganhos = dados.get("pontos_ganhos")

    if not campeonato_id or not jogador_id or not pergunta_id:
        return jsonify({"erro": "campeonato_id, jogador_id e pergunta_id são obrigatórios"}), 400

    try:
        cursor.execute("SELECT id, ativo FROM campeonatos WHERE id = %s", (campeonato_id,))
        camp = cursor.fetchone()
        if not camp:
            return jsonify({"erro": "Campeonato não encontrado"}), 404
        if not camp[1]:
            return jsonify({"erro": "Campeonato encerrado"}), 400

        cursor.execute("SELECT id FROM jogadores WHERE id = %s", (jogador_id,))
        if not cursor.fetchone():
            return jsonify({"erro": "Jogador não encontrado"}), 404

        cursor.execute("SELECT id, pontos FROM perguntas WHERE id = %s", (pergunta_id,))
        pergunta = cursor.fetchone()
        if not pergunta:
            return jsonify({"erro": "Pergunta não encontrada"}), 404

        if pontos_ganhos is None:
            pontos_finais = int(pergunta[1])
        else:
            try:
                pontos_finais = int(pontos_ganhos)
                if pontos_finais < 0:
                    return jsonify({"erro": "pontos_ganhos não pode ser negativo"}), 400
            except (TypeError, ValueError):
                return jsonify({"erro": "pontos_ganhos deve ser um número inteiro"}), 400

        cursor.execute("""
            INSERT INTO acertos (campeonato_id, jogador_id, pergunta_id, pontos_ganhos)
            VALUES (%s, %s, %s, %s)
            RETURNING id, campeonato_id, jogador_id, pergunta_id, pontos_ganhos, registrado_em
        """, (campeonato_id, jogador_id, pergunta_id, pontos_finais))

        r = cursor.fetchone()
        conn.commit()

        return jsonify({
            "status": "ok",
            "acerto": {
                "id": r[0],
                "campeonato_id": r[1],
                "jogador_id": r[2],
                "pergunta_id": r[3],
                "pontos_ganhos": int(r[4]),
                "registrado_em": r[5].isoformat() if r[5] else None
            }
        }), 201

    except Exception as e:
        conn.rollback()
        print("Erro registrar acerto:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ======================
# JOGO: RANKING DO CAMPEONATO
# ======================
@cliente.route("/jogo/campeonatos/<int:campeonato_id>/ranking", methods=["GET"])
def ranking_campeonato(campeonato_id):
    cursor, conn = get_cursor()

    try:
        cursor.execute("SELECT id, nome, ativo FROM campeonatos WHERE id = %s", (campeonato_id,))
        camp = cursor.fetchone()
        if not camp:
            return jsonify({"erro": "Campeonato não encontrado"}), 404

        cursor.execute("""
            SELECT
                j.id AS jogador_id,
                j.nome AS jogador,
                COUNT(a.id) AS total_acertos,
                COALESCE(SUM(a.pontos_ganhos), 0) AS pontuacao_total
            FROM jogadores j
            JOIN acertos a ON j.id = a.jogador_id
            WHERE a.campeonato_id = %s
            GROUP BY j.id, j.nome
            ORDER BY pontuacao_total DESC, total_acertos DESC, j.nome ASC
        """, (campeonato_id,))

        dados = cursor.fetchall()

        ranking = [
            {
                "posicao": idx,
                "jogador_id": r[0],
                "jogador": r[1],
                "total_acertos": int(r[2]),
                "pontuacao_total": int(r[3])
            }
            for idx, r in enumerate(dados, start=1)
        ]

        return jsonify({
            "campeonato": {
                "id": camp[0],
                "nome": camp[1],
                "ativo": bool(camp[2])
            },
            "ranking": ranking
        })

    except Exception as e:
        print("Erro ranking:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cursor.close()
        conn.close()