#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script seguro para aplicar schema no banco de dados
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def verificar_tabelas():
    """Verifica quais tabelas já existem"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL não definido!")
        return None

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Verificar tabelas existentes
        cur.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )

        tables = [t[0] for t in cur.fetchall()]
        cur.close()
        conn.close()

        return tables
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None


def aplicar_schema():
    """Aplica o schema de forma segura"""
    print("=" * 80)
    print("🔧 APLICANDO SCHEMA NO BANCO DE DADOS")
    print("=" * 80)
    print()

    # Verificar estado atual
    print("📊 Verificando estado atual do banco...")
    tables = verificar_tabelas()

    if tables is None:
        return

    print(f"✅ Conectado! {len(tables)} tabelas encontradas")
    print()

    # Verificar se tabelas críticas já existem
    tabelas_necessarias = ["activity_history", "user_settings"]
    tabelas_faltando = [t for t in tabelas_necessarias if t not in tables]

    if not tabelas_faltando:
        print("✅ Todas as tabelas necessárias já existem!")
        print()
        print("Tabelas encontradas:")
        for t in tabelas_necessarias:
            print(f"   ✓ {t}")
        print()
        print("✅ SCHEMA JÁ ESTÁ APLICADO!")
        return

    print("⚠️  Tabelas faltando:")
    for t in tabelas_faltando:
        print(f"   ✗ {t}")
    print()

    # Perguntar confirmação
    resposta = input("🤔 Deseja aplicar o schema agora? (sim/não): ").strip().lower()

    if resposta not in ["sim", "s", "yes", "y"]:
        print("❌ Operação cancelada pelo usuário.")
        return

    print()
    print("🚀 Aplicando schema...")
    print()

    # Ler arquivo SQL
    schema_file = "schema_achievements_history.sql"

    if not os.path.exists(schema_file):
        print(f"❌ Arquivo {schema_file} não encontrado!")
        return

    with open(schema_file, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    # Aplicar no banco
    database_url = os.getenv("DATABASE_URL")

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Executar SQL
        cur.execute(sql_commands)
        conn.commit()

        print("✅ Schema aplicado com sucesso!")
        print()

        # Verificar resultado
        print("📊 Verificando resultado...")
        cur.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('activity_history', 'user_settings')
            ORDER BY table_name
        """
        )

        novas_tabelas = cur.fetchall()
        print(f"✅ {len(novas_tabelas)} tabelas criadas:")
        for t in novas_tabelas:
            print(f"   ✓ {t[0]}")

        # Verificar conquistas
        cur.execute("SELECT COUNT(*) FROM achievements")
        count = cur.fetchone()[0]
        print(f"✅ {count} conquistas cadastradas")

        cur.close()
        conn.close()

        print()
        print("=" * 80)
        print("🎉 SCHEMA APLICADO COM SUCESSO!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Erro ao aplicar schema: {e}")
        print()
        print("💡 Dica: Verifique se o arquivo SQL está correto")


if __name__ == "__main__":
    aplicar_schema()
    print()
    input("Pressione ENTER para continuar...")
