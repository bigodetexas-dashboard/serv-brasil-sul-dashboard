import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def seed_test_data():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        print("Inserindo dados de teste...")
        
        # 1. Inserir usuário na economia (test_user_123)
        cur.execute("""
            INSERT INTO economy (discord_id, gamertag, balance, last_daily, inventory, transactions, favorites, achievements)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)
            ON CONFLICT (discord_id) DO UPDATE SET
                balance = EXCLUDED.balance
        """, (
            'test_user_123', 
            'TestPlayer123', 
            50000, # 50k coins
            '{}', '[]', '[]', 
            json.dumps({'first_kill': True, 'rich': True})
        ))
        
        # 2. Inserir link
        cur.execute("""
            INSERT INTO links (discord_id, gamertag)
            VALUES (%s, %s)
            ON CONFLICT (discord_id) DO NOTHING
        """, ('test_user_123', 'TestPlayer123'))
        
        # 3. Inserir stats do player
        cur.execute("""
            INSERT INTO players (gamertag, kills, deaths, best_killstreak, longest_shot, weapons_stats, first_seen, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s, 1000, 2000)
            ON CONFLICT (gamertag) DO NOTHING
        """, (
            'TestPlayer123',
            150, # kills
            50,  # deaths
            10,  # killstreak
            500, # longest shot
            json.dumps({'M4A1': 50, 'AKM': 30})
        ))
        
        conn.commit()
        print("Dados de teste inseridos com sucesso!")
        print("Usuário: test_user_123")
        print("Saldo: 50.000")
        
    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_test_data()
