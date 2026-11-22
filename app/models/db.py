import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


# ======================
# CRIAR CONEXÃO
# ======================
def get_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="require"
    )


# ======================
# CURSOR NOVO SEMPRE
# ======================
def get_cursor():
    conn = get_connection()
    return conn.cursor(), conn


print("Conectado com sucesso!")


# ======================
# CRIAR TABELAS
# ======================
conn = get_connection()
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidosclientes (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    produto VARCHAR(100) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT NOW(),
    entregue BOOLEAN NOT NULL DEFAULT FALSE
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS pagamentos (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    montante NUMERIC(15,2) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco NUMERIC(10,2) NOT NULL,
    disponivel BOOLEAN NOT NULL DEFAULT FALSE
);
""")


# ======================
# TABELAS DO JOGO (RANKING POR CAMPEONATO)
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS campeonatos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP NOT NULL DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS jogadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT NOW()
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS perguntas (
    id SERIAL PRIMARY KEY,
    enunciado TEXT NOT NULL,
    resposta_correta TEXT,
    pontos INT NOT NULL DEFAULT 1
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS acertos (
    id SERIAL PRIMARY KEY,
    campeonato_id INT NOT NULL REFERENCES campeonatos(id) ON DELETE CASCADE,
    jogador_id INT NOT NULL REFERENCES jogadores(id) ON DELETE CASCADE,
    pergunta_id INT NOT NULL REFERENCES perguntas(id) ON DELETE CASCADE,
    pontos_ganhos INT NOT NULL DEFAULT 1,
    registrado_em TIMESTAMP NOT NULL DEFAULT NOW()
);
""")


conn.commit()


cursor.close()
conn.close()