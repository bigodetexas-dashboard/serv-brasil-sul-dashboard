# -*- coding: utf-8 -*-
"""
Script para aplicar schema de deaths no banco de dados
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def apply_schema():
    """Aplica schema de deaths_log no banco"""
    print("[*] Conectando ao banco de dados...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("[*] Lendo schema_deaths.sql...")
        with open("schema_deaths.sql", "r", encoding="utf-8") as f:
            sql = f.read()

        print("[*] Aplicando schema...")
        cur.execute(sql)

        conn.commit()
        print("[OK] Schema de deaths aplicado com sucesso!")

        # Verificar se tabela foi criada
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'deaths_log'
        """)

        if cur.fetchone()[0] > 0:
            print("[OK] Tabela 'deaths_log' criada com sucesso!")

        # Verificar view
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.views
            WHERE table_name = 'deaths_stats_24h'
        """)

        if cur.fetchone()[0] > 0:
            print("[OK] View 'deaths_stats_24h' criada com sucesso!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"[ERRO] Erro ao aplicar schema: {e}")
        raise


if __name__ == "__main__":
    apply_schema()
