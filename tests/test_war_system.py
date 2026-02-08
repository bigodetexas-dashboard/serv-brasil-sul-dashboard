# -*- coding: utf-8 -*-
"""
Testes do War System
"""
import sys
import os

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from war_system import ensure_clan_wars_table, update_war_scores
import database

def test_create_war():
    """Testa criação de guerra entre clãs"""
    print("\n" + "="*60)
    print("TESTE 1: Criar tabela clan_wars")
    print("="*60)

    result = ensure_clan_wars_table()
    if result:
        print("[OK] Tabela clan_wars criada com sucesso!")
    else:
        print("[ERRO] Falha ao criar tabela")

    return result


def test_war_kill():
    """Testa registro de kill em guerra"""
    print("\n" + "="*60)
    print("TESTE 2: Registrar kill em guerra")
    print("="*60)

    # Primeiro, inserir uma guerra de teste
    conn = database.get_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Limpar dados de teste anteriores
            cur.execute("DELETE FROM clan_wars WHERE clan1_tag IN ('TESTE_A', 'TESTE_B')")

            # Criar guerra de teste
            cur.execute("""
                INSERT INTO clan_wars (clan1_tag, clan2_tag, clan1_kills, clan2_kills, is_active)
                VALUES ('TESTE_A', 'TESTE_B', 0, 0, 1)
            """)
            conn.commit()
            print("[OK] Guerra de teste criada: TESTE_A vs TESTE_B")

            # Testar kill
            result = update_war_scores("TESTE_A", "TESTE_B")

            if result:
                print(f"[OK] Kill registrado! Score: {result['score']}")

                # Verificar no banco
                cur.execute("""
                    SELECT clan1_kills, clan2_kills FROM clan_wars
                    WHERE clan1_tag = 'TESTE_A' AND clan2_tag = 'TESTE_B'
                """)
                row = cur.fetchone()
                if row:
                    print(f"[OK] Verificado no DB: {row[0]} x {row[1]}")

                # Limpar
                cur.execute("DELETE FROM clan_wars WHERE clan1_tag = 'TESTE_A'")
                conn.commit()
                print("[OK] Dados de teste limpos")

                conn.close()
                return True
            else:
                print("[AVISO] Nenhum resultado (normal se não houver guerra ativa)")
                conn.close()
                return False

        except Exception as e:
            print(f"[ERRO] {e}")
            if conn:
                conn.close()
            return False

    return False


def test_no_war():
    """Testa quando não há guerra ativa"""
    print("\n" + "="*60)
    print("TESTE 3: Kill sem guerra ativa")
    print("="*60)

    result = update_war_scores("CLAN_X", "CLAN_Y")

    if result is None:
        print("[OK] Corretamente retornou None (sem guerra)")
        return True
    else:
        print("[ERRO] Deveria retornar None")
        return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# SUITE DE TESTES - WAR SYSTEM")
    print("#"*60)

    results = []

    results.append(("Criar tabela", test_create_war()))
    results.append(("Registrar kill", test_war_kill()))
    results.append(("Sem guerra ativa", test_no_war()))

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
        print(f"\n[ERRO] {total - passed} teste(s) falharam")
        sys.exit(1)
