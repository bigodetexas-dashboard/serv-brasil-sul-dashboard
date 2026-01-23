import sqlite3
import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

SQLITE_DB = "bigode_unified.db"
POSTGRES_URL = os.getenv("DATABASE_URL")


def migrate():
    if not POSTGRES_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return

    print(f"🚀 Iniciando migração de {SQLITE_DB} para PostgreSQL...")

    # Conectar ao SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao abrir SQLite: {e}")
        return

    # Conectar ao PostgreSQL
    try:
        pg_conn = psycopg2.connect(POSTGRES_URL)
        pg_cur = pg_conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar PostgreSQL: {e}")
        sqlite_conn.close()
        return

    # Listar tabelas (excluindo sistema)
    sqlite_cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )
    tables = [row[0] for row in sqlite_cur.fetchall()]

    for table in tables:
        if table == "_lock_check":
            continue  # Ignorar tabela de trava de teste

        print(f"📦 Migrando tabela: {table}...")

        # 1. Pegar info das colunas no SQLite
        sqlite_cur.execute(f"PRAGMA table_info({table});")
        columns = sqlite_cur.fetchall()

        col_defs = []
        col_names = []
        for col in columns:
            name, dtype = col[1], col[2].upper()
            col_names.append(name)

            # Mapeamento básico de tipos
            if "INT" in dtype:
                pg_type = "BIGINT"
            elif "TEXT" in dtype or "CHAR" in dtype:
                pg_type = "TEXT"
            elif "REAL" in dtype or "FLOAT" in dtype or "DOUBLE" in dtype:
                pg_type = "DOUBLE PRECISION"
            elif "TIMESTAMP" in dtype or "DATETIME" in dtype:
                pg_type = "TIMESTAMP"
            elif "BOOLEAN" in dtype:
                pg_type = "BOOLEAN"
            else:
                pg_type = "TEXT"  # Fallback

            # Manter ID como Primary Key se for INTEGER PRIMARY KEY no SQLite
            if col[5] == 1:  # pk flag
                col_defs.append(f'"{name}" {pg_type} PRIMARY KEY')
            else:
                col_defs.append(f'"{name}" {pg_type}')

        # 2. Criar tabela no PostgreSQL
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(col_defs)});'
        pg_cur.execute(create_sql)
        pg_conn.commit()

        # 3. Limpar dados existentes (opcional, mas seguro para recomeçar)
        # pg_cur.execute(f'TRUNCATE TABLE "{table}" CASCADE;')

        # 4. Copiar dados
        sqlite_cur.execute(f'SELECT * FROM "{table}";')
        rows = sqlite_cur.fetchall()

        if rows:
            placeholders = ", ".join(["%s"] * len(col_names))
            insert_sql = f'INSERT INTO "{table}" ({", ".join([f'"{c}"' for c in col_names])}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;'

            data_to_insert = []
            for row in rows:
                row_data = []
                for val in row:
                    # Pequenas conversões de tipo
                    if val == "":
                        val = None
                    row_data.append(val)
                data_to_insert.append(tuple(row_data))

            extras.execute_batch(pg_cur, insert_sql, data_to_insert)
            pg_conn.commit()
            print(f"✅ {len(rows)} linhas migradas para {table}.")
        else:
            print(f"⚪ Tabela {table} vazia.")

    print("\n✨ Migração concluída com sucesso!")

    sqlite_conn.close()
    pg_conn.close()


if __name__ == "__main__":
    migrate()
