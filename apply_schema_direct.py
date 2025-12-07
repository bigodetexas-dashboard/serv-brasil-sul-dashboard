#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python para aplicar schema no banco de dados
Usa psycopg2 diretamente (não precisa de psql instalado)
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

def main():
    print("="*80)
    print("APLICANDO SCHEMA NO BANCO DE DADOS")
    print("="*80)
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
    
    # Ler arquivo SQL
    print("Lendo arquivo SQL...")
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except Exception as e:
        print(f"[ERRO] Erro ao ler arquivo: {e}")
        return False
    
    print(f"[OK] Arquivo lido ({len(sql_content)} caracteres)")
    print()
    
    # Conectar ao banco e executar
    print("Conectando ao banco de dados...")
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("[OK] Conectado!")
        print()
        print("Executando SQL...")
        print()
        
        # Executar o SQL
        cur.execute(sql_content)
        conn.commit()
        
        print()
        print("="*80)
        print("[SUCESSO] SCHEMA APLICADO COM SUCESSO!")
        print("="*80)
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
        
        # Verificar quantas conquistas foram inseridas
        cur.execute("SELECT COUNT(*) FROM achievements")
        count = cur.fetchone()[0]
        print(f"Conquistas cadastradas: {count}")
        print()
        
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print()
        print("="*80)
        print("[ERRO] ERRO AO APLICAR SCHEMA!")
        print("="*80)
        print()
        print(f"Erro: {e}")
        print()
        print("Possiveis causas:")
        print("   1. DATABASE_URL incorreto")
        print("   2. Banco de dados nao acessivel")
        print("   3. Permissoes insuficientes")
        print("   4. Tabelas ja existem (normal se ja aplicou antes)")
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
        print("="*80)
        print("PROXIMO PASSO: TESTAR AS APIS")
        print("="*80)
        print()
        print("Execute: python test_apis.py")
        print()
    
    input("Pressione ENTER para continuar...")
