#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicar schema no banco de PRODUCAO
IMPORTANTE: Este script usa o DATABASE_URL de producao do .env
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*80)
    print("APLICANDO SCHEMA NO BANCO DE PRODUCAO")
    print("="*80)
    print()
    
    schema_file = "schema_partial.sql"
    
    # Buscar DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("[ERRO] DATABASE_URL nao definido!")
        print()
        print("Defina no .env ou passe como argumento")
        return False
    
    print("[OK] Conectando ao banco de producao...")
    print(f"[INFO] Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'local'}")
    print()
    
    # Ler SQL
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"[OK] SQL lido ({len(sql_content)} caracteres)")
    print()
    
    # Confirmar
    print("ATENCAO: Isto vai criar tabelas no banco de PRODUCAO!")
    print()
    print("Tabelas que serao criadas:")
    print("  - activity_history")
    print("  - user_settings")
    print()
    
    resposta = input("Deseja continuar? (sim/nao): ").lower()
    
    if resposta != 'sim':
        print("Operacao cancelada.")
        return False
    
    print()
    print("Executando SQL...")
    print()
    
    # Executar
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        cur.execute(sql_content)
        conn.commit()
        
        print("="*80)
        print("[SUCESSO] SCHEMA APLICADO NO BANCO DE PRODUCAO!")
        print("="*80)
        print()
        print("Tabelas criadas:")
        print("  - activity_history")
        print("  - user_settings")
        print()
        print("Funcoes criadas:")
        print("  - add_activity_event()")
        print()
        
        # Verificar
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('activity_history', 'user_settings')
        """)
        tables = cur.fetchall()
        
        print(f"Verificacao: {len(tables)} tabelas criadas")
        for t in tables:
            print(f"  [OK] {t[0]}")
        print()
        
        cur.close()
        conn.close()
        
        print("Sistema pronto para uso em PRODUCAO!")
        print()
        return True
        
    except psycopg2.Error as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("="*80)
        print("PROXIMO PASSO: TESTAR O SITE")
        print("="*80)
        print()
        print("Acesse:")
        print("  https://serv-brasil-sul-dashboard.onrender.com/achievements")
        print("  https://serv-brasil-sul-dashboard.onrender.com/history")
        print("  https://serv-brasil-sul-dashboard.onrender.com/settings")
        print()
    
    input("Pressione ENTER para continuar...")
