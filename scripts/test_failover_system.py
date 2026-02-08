# -*- coding: utf-8 -*-
"""
Script de Teste - Sistema de Failover Autônomo
Verifica estado do sistema de failover e simula cenários.
"""
import os
import sys
import sqlite3
import time
from datetime import datetime, timedelta

# Adicionar raiz ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Configurar UTF-8 no Windows
if sys.platform == "win32":
    import codecs
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

try:
    from utils.heartbeat import send_heartbeat, check_primary_alive, get_system_status
    from utils.sync_manager import SyncManager
    FAILOVER_AVAILABLE = True
except ImportError as e:
    FAILOVER_AVAILABLE = False
    print(f"[ERRO] Sistema de failover nao disponivel: {e}")


def check_database():
    """Verifica se banco de sincronização existe"""
    db_path = os.path.join(PROJECT_ROOT, "sync_queue.db")

    print("\n" + "=" * 60)
    print("VERIFICACAO DO BANCO DE DADOS DE FAILOVER")
    print("=" * 60)

    if not os.path.exists(db_path):
        print(f"\n[X] Banco nao encontrado: {db_path}")
        print("\nO banco sync_queue.db sera criado automaticamente quando:")
        print("• monitor_logs.py for executado pela primeira vez")
        print("• ou watchdog_service.py for iniciado")
        return False

    print(f"\n[OK] Banco encontrado: {db_path}")

    # Verificar tabelas
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Verificar tabela system_status
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_status'")
        if cur.fetchone():
            print("[OK] Tabela 'system_status' existe")

            # Mostrar status atual
            cur.execute("SELECT * FROM system_status")
            rows = cur.fetchall()

            if rows:
                print("\nStatus atual dos sistemas:")
                for row in rows:
                    print(f"  • Sistema: {row[0]}")
                    print(f"    Ativo: {row[1]}")
                    print(f"    Status: {row[2]}")
                    print(f"    Ultimo heartbeat: {row[3]}")
                    print()
            else:
                print("  [AVISO] Nenhum sistema registrado ainda")
        else:
            print("[X] Tabela 'system_status' nao existe")

        # Verificar tabela sync_queue
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_queue'")
        if cur.fetchone():
            print("[OK] Tabela 'sync_queue' existe")

            cur.execute("SELECT COUNT(*) FROM sync_queue WHERE processed = 0")
            pending = cur.fetchone()[0]
            print(f"  • Eventos pendentes: {pending}")
        else:
            print("[X] Tabela 'sync_queue' nao existe")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao verificar banco: {e}")
        return False


def test_heartbeat():
    """Testa sistema de heartbeat"""

    print("\n" + "=" * 60)
    print("TESTE DE HEARTBEAT")
    print("=" * 60)

    if not FAILOVER_AVAILABLE:
        print("\n[X] Modulos de failover nao disponiveis")
        return False

    try:
        # Enviar heartbeat de teste
        print("\nEnviando heartbeat de teste (primary)...")
        send_heartbeat("primary")
        print("[OK] Heartbeat enviado")

        # Verificar se foi registrado
        time.sleep(1)
        status = get_system_status("primary")

        if status:
            print(f"\n[OK] Sistema primary registrado:")
            print(f"  • Ativo: {status.get('is_active')}")
            print(f"  • Status: {status.get('status')}")
            print(f"  • Ultimo heartbeat: {status.get('last_heartbeat')}")
        else:
            print("[X] Status do sistema nao encontrado")

        return True

    except Exception as e:
        print(f"[ERRO] Falha no teste de heartbeat: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_failover_detection():
    """Testa detecção de failover"""

    print("\n" + "=" * 60)
    print("TESTE DE DETECCAO DE FAILOVER")
    print("=" * 60)

    if not FAILOVER_AVAILABLE:
        print("\n[X] Modulos de failover nao disponiveis")
        return False

    try:
        # Verificar se primary está vivo
        print("\nVerificando se sistema primary esta vivo...")
        is_alive = check_primary_alive(timeout_seconds=120)

        if is_alive:
            print("[OK] Sistema primary ATIVO")
            print("  O backup nao assumiria controle")
        else:
            print("[!] Sistema primary OFFLINE")
            print("  O backup assumiria controle automaticamente!")

        # Mostrar tempo desde último heartbeat
        status = get_system_status("primary")
        if status and status.get('last_heartbeat'):
            last_hb = datetime.fromisoformat(status['last_heartbeat'])
            elapsed = (datetime.now() - last_hb).total_seconds()
            print(f"\nTempo desde ultimo heartbeat: {int(elapsed)} segundos")

            if elapsed > 120:
                print("  [!] Mais de 2 minutos - FAILOVER SERIA ATIVADO!")
            else:
                print("  [OK] Menos de 2 minutos - Sistema saudavel")

        return True

    except Exception as e:
        print(f"[ERRO] Falha no teste de deteccao: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sync_manager():
    """Testa gerenciador de sincronização"""

    print("\n" + "=" * 60)
    print("TESTE DO SYNC MANAGER")
    print("=" * 60)

    if not FAILOVER_AVAILABLE:
        print("\n[X] Modulos de failover nao disponiveis")
        return False

    try:
        sync_mgr = SyncManager()

        # Verificar eventos pendentes
        has_pending = sync_mgr.has_pending_sync()
        print(f"\nEventos pendentes de sincronizacao: {'SIM' if has_pending else 'NAO'}")

        # Obter estatísticas
        stats = sync_mgr.get_sync_stats()
        if stats:
            print("\nEstatisticas de sincronizacao:")
            print(f"  • Total de eventos: {stats.get('total', 0)}")
            print(f"  • Pendentes: {stats.get('pending', 0)}")
            print(f"  • Sincronizados: {stats.get('synced', 0)}")

        return True

    except Exception as e:
        print(f"[ERRO] Falha no teste do sync manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def simulate_failover_scenario():
    """Simula cenário de failover"""

    print("\n" + "=" * 60)
    print("SIMULACAO DE CENARIO DE FAILOVER")
    print("=" * 60)

    print("\nCenario: Sistema primary para de responder\n")
    print("FLUXO ESPERADO:")
    print("1. monitor_logs.py para de enviar heartbeat")
    print("2. Ultimo heartbeat fica com mais de 2 minutos")
    print("3. bot_main.py detecta via auto_failover.should_activate_backup()")
    print("4. bot_main.py ASSUME CONTROLE automaticamente")
    print("5. Eventos processados sao salvos em sync_queue")
    print("6. Quando monitor_logs.py retornar:")
    print("   • Eventos sao sincronizados")
    print("   • Backup libera controle")
    print("   • Sistema volta ao normal")

    print("\n[INFO] Para testar na pratica:")
    print("1. Execute monitor_logs.py em um terminal")
    print("2. Aguarde 5 minutos (um ciclo completo)")
    print("3. Pare monitor_logs.py (Ctrl+C)")
    print("4. Execute este script novamente")
    print("5. Observe que primary esta OFFLINE")
    print("6. bot_main.py assumira controle no proximo ciclo (5 min)")


def main():
    """Executa todos os testes"""

    print("\n" + "=" * 60)
    print("TESTE DO SISTEMA DE FAILOVER AUTONOMO")
    print("BigodeTexas - Modo 100% Autonomo")
    print("=" * 60)

    results = []

    # Teste 1: Banco de dados
    results.append(("Banco de dados", check_database()))

    # Teste 2: Heartbeat
    results.append(("Sistema de Heartbeat", test_heartbeat()))

    # Teste 3: Detecção de failover
    results.append(("Deteccao de Failover", test_failover_detection()))

    # Teste 4: Sync Manager
    results.append(("Sync Manager", test_sync_manager()))

    # Simulação
    simulate_failover_scenario()

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for test_name, success in results:
        status = "[OK]" if success else "[X]"
        print(f"{status} {test_name}")

    print("\n" + "=" * 60)
    print("TESTE CONCLUIDO")
    print("=" * 60)


if __name__ == "__main__":
    main()
