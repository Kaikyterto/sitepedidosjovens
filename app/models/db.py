import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# CONEXÃO SEGURA
# ======================
def get_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="require"
    )

conn = get_connection()

def get_cursor():
    return conn.cursor()

print("Conectado com sucesso!")

cursor = get_cursor()

# ======================
# TABELA: PEDIDOS
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidosclientes (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    produto VARCHAR(100) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT NOW(),
    entregue BOOLEAN NOT NULL DEFAULT FALSE
);
""")

# ======================
# TABELA: PAGAMENTOS
# ======================
cursor.execute("""
CREATE TABLE IF NOT EXISTS pagamentos (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    montante NUMERIC(15,2) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT NOW()
);
""")


cursor.execute("""
ALTER TABLE pagamentos
ADD COLUMN IF NOT EXISTS data TIMESTAMP DEFAULT NOW();
""")

# ======================
# TABELA: PRODUTOS
# ======================
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
]

for nome, preco in produtos_iniciais:
    cursor.execute("""
        INSERT INTO produtos (nome, preco)
        VALUES (%s, %s)
        ON CONFLICT (nome) DO NOTHING;
    """, (nome, preco))

conn.commit()
print("Produtos iniciais garantidos no banco!")
