#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicar schema parcial (apenas tabelas que faltam)
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*80)
    print("APLICANDO SCHEMA PARCIAL (activity_history + user_settings)")
    print("="*80)
    print()
    
    schema_file = "schema_partial.sql"
    if not os.path.exists(schema_file):
        print(f"[ERRO] Arquivo {schema_file} nao encontrado!")
        return False
    
    print(f"[OK] Arquivo encontrado: {schema_file}")
    print()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("[ERRO] DATABASE_URL nao definido!")
        return False
    
    print("[OK] DATABASE_URL encontrado!")
    print()
    
    # Ler SQL
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"[OK] SQL lido ({len(sql_content)} caracteres)")
    print()
    
    # Executar
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("Conectado ao banco!")
        print()
        print("Executando SQL...")
        print()
        
        cur.execute(sql_content)
        conn.commit()
        
        print("="*80)
        print("[SUCESSO] SCHEMA PARCIAL APLICADO!")
        print("="*80)
        print()
        print("Tabelas criadas:")
        print("   - activity_history (historico de eventos)")
        print("   - user_settings (configuracoes do usuario)")
        print()
        print("Funcoes criadas:")
        print("   - add_activity_event()")
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
            print(f"   [OK] {t[0]}")
        print()
        
        cur.close()
        conn.close()
        
        print("Sistema pronto para uso!")
        print()
        return True
        
    except psycopg2.Error as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("="*80)
        print("PROXIMO PASSO: TESTAR AS APIS")
        print("="*80)
        print()
        print("Execute: python test_apis.py")
        print()
    
    input("Pressione ENTER para continuar...")
