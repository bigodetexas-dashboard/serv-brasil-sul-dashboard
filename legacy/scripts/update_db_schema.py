import os
import psycopg2
from dotenv import load_dotenv

# Carregar variaveis de ambiente
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def update_schema():
    print("Conectando ao banco de dados para atualizar o esquema...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Adicionar last_daily_at na bank_accounts
        print(
            "Adicionando coluna last_daily_at a tabela bank_accounts (se nao existir)..."
        )
        cur.execute(
            """
            ALTER TABLE bank_accounts 
            ADD COLUMN IF NOT EXISTS last_daily_at TIMESTAMP WITH TIME ZONE;
        """
        )

        # 2. Criar tabela user_favorites
        print("Criando tabela user_favorites...")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_favorites (
                id SERIAL PRIMARY KEY,
                discord_id VARCHAR(255) NOT NULL,
                item_key VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(discord_id, item_key)
            );
        """
        )

        conn.commit()
        print("Esquema atualizado com sucesso!")

    except Exception as e:
        print(f"Erro ao atualizar esquema: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    update_schema()
