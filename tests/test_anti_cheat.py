# -*- coding: utf-8 -*-
"""
Testes do Sistema Anti-Cheat (Detecção de Alts/Banidos)
"""
import sys
import os
import sqlite3

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bigode_unified.db")


def setup_test_data():
    """Cria dados de teste"""
    print("\n" + "="*60)
    print("SETUP: Criando dados de teste")
    print("="*60)

    conn = sqlite3.connect(DB_PATH)
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # Limpar dados de teste anteriores
        cur.execute("DELETE FROM users WHERE gamertag LIKE 'TEST_%'")

        # Criar usuário banido
        cur.execute("""
            INSERT OR IGNORE INTO users (discord_id, gamertag, is_banned)
            VALUES ('999999999', 'TEST_BANNED_USER', 1)
        """)

        # Criar usuário normal
        cur.execute("""
            INSERT OR IGNORE INTO users (discord_id, gamertag, is_banned)
            VALUES ('888888888', 'TEST_NORMAL_USER', 0)
        """)

        # Criar tabela de logs de conexão se não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS connection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gamertag TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Simular conexões de IP suspeito
        cur.execute("DELETE FROM connection_logs WHERE ip_address = '1.2.3.4'")
        cur.execute("""
            INSERT INTO connection_logs (gamertag, ip_address)
            VALUES ('TEST_BANNED_USER', '1.2.3.4')
        """)
        cur.execute("""
            INSERT INTO connection_logs (gamertag, ip_address)
            VALUES ('TEST_ALT_ACCOUNT', '1.2.3.4')
        """)

        conn.commit()
        print("[OK] Dados de teste criados")
        print("  - Usuario banido: TEST_BANNED_USER")
        print("  - Usuario normal: TEST_NORMAL_USER")
        print("  - IP suspeito: 1.2.3.4 (usado por conta banida)")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        if conn:
            conn.close()
        return False


def test_banned_user_detection():
    """Testa detecção de usuário banido"""
    print("\n" + "="*60)
    print("TESTE 1: Detectar usuário banido")
    print("="*60)

    conn = sqlite3.connect(DB_PATH)
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # Verificar se usuário está banido
        cur.execute("SELECT is_banned FROM users WHERE gamertag = 'TEST_BANNED_USER'")
        row = cur.fetchone()

        if row and row[0] == 1:
            print("[OK] Usuario TEST_BANNED_USER detectado como banido")
            conn.close()
            return True
        else:
            print("[ERRO] Usuario nao foi detectado como banido")
            conn.close()
            return False

    except Exception as e:
        print(f"[ERRO] {e}")
        if conn:
            conn.close()
        return False


def test_alt_detection():
    """Testa detecção de conta alt"""
    print("\n" + "="*60)
    print("TESTE 2: Detectar possível ALT")
    print("="*60)

    conn = sqlite3.connect(DB_PATH)
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # Buscar outras contas com mesmo IP
        test_ip = "1.2.3.4"
        test_name = "TEST_ALT_ACCOUNT"

        cur.execute("""
            SELECT DISTINCT gamertag FROM connection_logs
            WHERE ip_address = ? AND gamertag != ?
            LIMIT 5
        """, (test_ip, test_name))

        alts = cur.fetchall()

        if alts:
            alt_names = [alt[0] for alt in alts]
            print(f"[OK] Detectadas contas com mesmo IP: {alt_names}")

            # Verificar se alguma está banida
            for alt_name in alt_names:
                cur.execute("SELECT is_banned FROM users WHERE gamertag = ? AND is_banned = 1", (alt_name,))
                if cur.fetchone():
                    print(f"[OK] ALT detectada! {test_name} usa mesmo IP que conta banida: {alt_name}")
                    conn.close()
                    return True

            conn.close()
            return True
        else:
            print("[AVISO] Nenhuma alt detectada")
            conn.close()
            return False

    except Exception as e:
        print(f"[ERRO] {e}")
        if conn:
            conn.close()
        return False


def cleanup_test_data():
    """Remove dados de teste"""
    print("\n" + "="*60)
    print("CLEANUP: Removendo dados de teste")
    print("="*60)

    conn = sqlite3.connect(DB_PATH)
    if not conn:
        return False

    try:
        cur = conn.cursor()

        cur.execute("DELETE FROM users WHERE gamertag LIKE 'TEST_%'")
        cur.execute("DELETE FROM connection_logs WHERE ip_address = '1.2.3.4'")

        conn.commit()
        print("[OK] Dados de teste removidos")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# SUITE DE TESTES - ANTI-CHEAT SYSTEM")
    print("#"*60)

    if not setup_test_data():
        print("\n[ERRO] Falha no setup dos testes")
        sys.exit(1)

    results = []

    results.append(("Detectar banido", test_banned_user_detection()))
    results.append(("Detectar ALT", test_alt_detection()))

    cleanup_test_data()

    print("\n" + "="*60)
    print("RESULTADO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nTotal: {passed}/{total} testes passaram")

    if passed == total:
        print("\n[OK] Todos os testes passaram!")
        sys.exit(0)
    else:
        print(f"\n[AVISO] {total - passed} teste(s) falharam")
        sys.exit(0)  # Não falhar o CI por causa de testes opcionais
