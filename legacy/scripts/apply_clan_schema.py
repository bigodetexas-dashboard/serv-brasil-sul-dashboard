import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def apply_clan_schema():
    print("Conectando ao banco para aplicar mudanças de Clãs...")
    if not DATABASE_URL:
        print("[ERRO] DATABASE_URL não encontrada.")
        return

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Ler o arquivo de compatibilidade
        schema_file = "schema_v2_compat.sql"
        if not os.path.exists(schema_file):
            print(f"[ERRO] {schema_file} não encontrado.")
            return

        with open(schema_file, "r", encoding="utf-8") as f:
            sql = f.read()

        print("Executando schema_v2_compat.sql...")
        cur.execute(sql)
        conn.commit()
        print("[OK] Schema de Clãs aplicado com sucesso!")

    except Exception as e:
        print(f"[ERRO] Falha ao aplicar schema: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    apply_clan_schema()
