#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python para aplicar schema no banco de dados
Usa python-dotenv para carregar DATABASE_URL automaticamente
"""

import os
import subprocess
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()


def main():
    print("=" * 80)
    print("APLICANDO SCHEMA NO BANCO DE DADOS")
    print("=" * 80)
    print()

    # Verificar se arquivo existe
    schema_file = "schema_achievements_history.sql"
    if not os.path.exists(schema_file):
        print(f"[ERRO] Arquivo {schema_file} nao encontrado!")
        return False

    print(f"[OK] Arquivo de schema encontrado: {schema_file}")
    print()

    # Buscar DATABASE_URL
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("[ERRO] DATABASE_URL nao esta definido!")
        print()
        print("Por favor, defina DATABASE_URL no arquivo .env")
        print("Exemplo:")
        print("DATABASE_URL=postgresql://user:password@host:port/database")
        return False

    print("[OK] DATABASE_URL encontrado!")
    print()
    print("Aplicando schema...")
    print()

    # Executar psql
    try:
        result = subprocess.run(
            ["psql", database_url, "-f", schema_file],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode == 0:
            print()
            print("=" * 80)
            print("[SUCESSO] SCHEMA APLICADO COM SUCESSO!")
            print("=" * 80)
            print()
            print("O que foi criado:")
            print("   - Tabela: achievements (18 conquistas pre-cadastradas)")
            print("   - Tabela: user_achievements")
            print("   - Tabela: activity_history")
            print("   - Tabela: user_settings")
            print("   - Funcoes: update_achievement_progress(), add_activity_event()")
            print("   - Views: v_user_achievements_full, v_user_achievement_stats")
            print()
            print("Sistema pronto para uso!")
            print()

            # Mostrar output do psql
            if result.stdout:
                print("Output do PostgreSQL:")
                print(result.stdout)

            return True
        else:
            print()
            print("=" * 80)
            print("[ERRO] ERRO AO APLICAR SCHEMA!")
            print("=" * 80)
            print()
            print("Erro:")
            print(result.stderr)
            print()
            print("Possiveis causas:")
            print("   1. DATABASE_URL incorreto")
            print("   2. Banco de dados nao acessivel")
            print("   3. Permissoes insuficientes")
            print("   4. PostgreSQL nao instalado")
            print()
            return False

    except FileNotFoundError:
        print()
        print("[ERRO] Comando 'psql' nao encontrado!")
        print()
        print("Por favor, instale PostgreSQL ou adicione psql ao PATH")
        print()
        return False
    except Exception as e:
        print()
        print(f"[ERRO] ERRO INESPERADO: {e}")
        print()
        return False


if __name__ == "__main__":
    success = main()

    if success:
        print()
        print("Proximo passo: Testar as APIs")
        print("Execute: python test_apis.py")
        print()

    input("Pressione ENTER para continuar...")
