#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estado atual do banco de dados
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*80)
    print("VERIFICANDO ESTADO DO BANCO DE DADOS")
    print("="*80)
    print()
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("[ERRO] DATABASE_URL nao definido!")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("[OK] Conectado ao banco!")
        print()
        
        # Verificar tabelas existentes
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"Tabelas existentes ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
        print()
        
        # Verificar se achievements existe
        if any('achievements' in str(t) for t in tables):
            print("Tabela 'achievements' EXISTE!")
            print()
            print("Verificando estrutura...")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'achievements'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print("Colunas:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
            print()
            
            # Verificar quantas conquistas
            cur.execute("SELECT COUNT(*) FROM achievements")
            count = cur.fetchone()[0]
            print(f"Total de conquistas: {count}")
        else:
            print("Tabela 'achievements' NAO EXISTE!")
            print("Schema precisa ser aplicado.")
        
        print()
        
        # Verificar outras tabelas do sistema
        system_tables = ['user_achievements', 'activity_history', 'user_settings']
        for table_name in system_tables:
            if any(table_name in str(t) for t in tables):
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                print(f"[OK] {table_name}: {count} registros")
            else:
                print(f"[FALTA] {table_name}: nao existe")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERRO] {e}")

if __name__ == "__main__":
    main()
    input("\nPressione ENTER para continuar...")
