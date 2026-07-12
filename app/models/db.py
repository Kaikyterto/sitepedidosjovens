import psycopg2
import os
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


conn.commit()


# ======================
# POPULAR PRODUTOS
# ======================

produtos_iniciais = [
    ("Tapioca", 3.00),
    ("Café", 0.50),
    ("Bolo de milho", 3.00),
    ("Bolo de chocolate", 3.00),
    ("Mini-pastel", 1.00),
    ("Promoção : 5 Mini-pastéis", 4.00),
    ("Refrigerante", 1.00),
    ("Hambúrguer", 10.00),
    ("Brownie", 3.00),
    ("Sopa", 5.00),
    ("Cookie P", 3.00),
    ("Cookie M", 6.00),
    ("Cookie G", 12.50),
    ("Cuzcuz", 4.00),
    ("Chocolate quente", 2.00),
]


for nome, preco in produtos_iniciais:

    cursor.execute(
        "SELECT 1 FROM produtos WHERE nome = %s;",
        (nome,)
    )

    existe = cursor.fetchone()

    if not existe:
        cursor.execute(
            "INSERT INTO produtos (nome, preco) VALUES (%s,%s);",
            (nome, preco)
        )


conn.commit()

cursor.close()
conn.close()