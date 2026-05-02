import psycopg2,os
from dotenv import load_dotenv

load_dotenv()



def get_connection():
    psycopg2.connect(
    os.environ["DATABASE_URL"],
    sslmode="require"
)

conn = get_connection()
cursor = conn.cursor()
print("Conectado com sucesso!")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidosclientes (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    produto VARCHAR(100) NOT NULL,
    data TIMESTAMP NOT NULL,
    entregue BOOLEAN NOT NULL DEFAULT FALSE
);
""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS pagamentos (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    montante NUMERIC(15,2) NOT NULL,
    pago BOOLEAN NOT NULL DEFAULT FALSE
    )
""")

conn.commit()
