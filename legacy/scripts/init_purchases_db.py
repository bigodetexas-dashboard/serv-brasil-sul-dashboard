import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def init_purchases_table():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        print("Criando tabela de compras...")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS purchases (
                id SERIAL PRIMARY KEY,
                discord_id VARCHAR(255) NOT NULL,
                items JSONB NOT NULL,
                total INTEGER NOT NULL,
                coordinates JSONB,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """
        )
        conn.commit()
        print("Tabela 'purchases' criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    init_purchases_table()
