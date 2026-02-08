# -*- coding: utf-8 -*-
"""
Health Check Completo - BigodeTexas
Verifica status de todos os componentes do sistema
"""
import os
import sys
import sqlite3
from datetime import datetime

# Cores para terminal (Windows)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_ok(text):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}[ERRO]{Colors.RESET} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}[AVISO]{Colors.RESET} {text}")

def check_file_exists(path, name):
    """Verifica se arquivo existe"""
    if os.path.exists(path):
        print_ok(f"{name}: {path}")
        return True
    else:
        print_error(f"{name} NAO ENCONTRADO: {path}")
        return False

def check_database():
    """Verifica integridade do banco de dados"""
    print_header("VERIFICACAO DO BANCO DE DADOS")

    db_path = "bigode_unified.db"
    if not os.path.exists(db_path):
        print_error(f"Banco de dados nao encontrado: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Listar tabelas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]

        print_ok(f"Banco conectado: {db_path}")
        print(f"   Total de tabelas: {len(tables)}")

        # Verificar tabelas essenciais
        essential_tables = ['users', 'deaths_log', 'shop_items', 'clans']
        for table in essential_tables:
            if table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print_ok(f"Tabela '{table}': {count} registros")
            else:
                print_warning(f"Tabela '{table}' nao encontrada")

        # Verificar tabela clan_wars (novo)
        if 'clan_wars' in tables:
            cur.execute("SELECT COUNT(*) FROM clan_wars WHERE is_active = 1")
            active_wars = cur.fetchone()[0]
            print_ok(f"Tabela 'clan_wars': {active_wars} guerras ativas")
        else:
            print_warning("Tabela 'clan_wars' nao criada (War System nao usado ainda)")

        conn.close()
        return True

    except Exception as e:
        print_error(f"Erro ao verificar banco: {e}")
        return False

def check_config_files():
    """Verifica arquivos de configuração"""
    print_header("VERIFICACAO DE ARQUIVOS DE CONFIGURACAO")

    checks = []
    checks.append(check_file_exists(".env", "Environment File"))
    checks.append(check_file_exists("config.json", "Bot Config"))
    checks.append(check_file_exists("new_dashboard/.env", "Dashboard Env"))

    return all(checks)

def check_modules():
    """Verifica módulos Python"""
    print_header("VERIFICACAO DE MODULOS")

    modules_to_check = [
        'discord',
        'flask',
        'flask_socketio',
        'dotenv',
        'requests'
    ]

    checks = []
    for module in modules_to_check:
        try:
            __import__(module)
            print_ok(f"Modulo '{module}' instalado")
            checks.append(True)
        except ImportError:
            print_error(f"Modulo '{module}' NAO instalado")
            checks.append(False)

    return all(checks)

def check_war_system():
    """Verifica War System"""
    print_header("VERIFICACAO DO WAR SYSTEM")

    # Caminho correto para war_system.py (na raiz do BigodeBot)
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    war_system_path = os.path.join(root_path, "war_system.py")

    if not os.path.exists(war_system_path):
        print_error(f"war_system.py nao encontrado em: {war_system_path}")
        return False

    print_ok("Modulo war_system.py existe")

    try:
        # Adicionar raiz ao path
        sys.path.insert(0, root_path)
        import war_system

        # Testar criação de tabela
        result = war_system.ensure_clan_wars_table()
        if result:
            print_ok("Tabela clan_wars verificada/criada")
            return True
        else:
            print_error("Falha ao criar/verificar tabela clan_wars")
            return False

    except Exception as e:
        print_error(f"Erro ao importar war_system: {e}")
        return False

def check_anti_cheat():
    """Verifica sistema Anti-Cheat"""
    print_header("VERIFICACAO DO SISTEMA ANTI-CHEAT")

    db_path = "bigode_unified.db"
    if not os.path.exists(db_path):
        print_error("Banco de dados nao encontrado")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Verificar se tabela users tem coluna is_banned
        cur.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cur.fetchall()]

        if 'is_banned' in columns:
            print_ok("Coluna 'is_banned' existe na tabela users")

            # Contar banidos
            cur.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
            banned_count = cur.fetchone()[0]
            if banned_count > 0:
                print_warning(f"{banned_count} usuario(s) banido(s) no sistema")
            else:
                print_ok("Nenhum usuario banido")

        else:
            print_warning("Coluna 'is_banned' nao encontrada")

        # Verificar tabela connection_logs
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='connection_logs'")
        if cur.fetchone():
            cur.execute("SELECT COUNT(*) FROM connection_logs")
            logs_count = cur.fetchone()[0]
            print_ok(f"Tabela 'connection_logs': {logs_count} conexoes registradas")
        else:
            print_warning("Tabela 'connection_logs' nao criada")

        conn.close()
        return True

    except Exception as e:
        print_error(f"Erro ao verificar anti-cheat: {e}")
        return False

def generate_report():
    """Gera relatório final"""
    print_header("RELATORIO FINAL DE SAUDE DO SISTEMA")

    results = []
    results.append(("Arquivos de Config", check_config_files()))
    results.append(("Banco de Dados", check_database()))
    results.append(("Modulos Python", check_modules()))
    results.append(("War System", check_war_system()))
    results.append(("Anti-Cheat", check_anti_cheat()))

    print("\n" + "="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}[PASS]{Colors.RESET}" if result else f"{Colors.RED}[FAIL]{Colors.RESET}"
        print(f"{status} {name}")

    print("="*60)
    percentage = (passed / total) * 100

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}SISTEMA 100% SAUDAVEL!{Colors.RESET}")
        print(f"Todos os {total} componentes passaram na verificacao.\n")
        return 0
    elif percentage >= 70:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}SISTEMA PARCIALMENTE SAUDAVEL{Colors.RESET}")
        print(f"{passed}/{total} componentes OK ({percentage:.0f}%)\n")
        return 1
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}SISTEMA COM PROBLEMAS CRITICOS{Colors.RESET}")
        print(f"Apenas {passed}/{total} componentes OK ({percentage:.0f}%)\n")
        return 2

if __name__ == "__main__":
    print(f"\n{Colors.BOLD}BIGODETEXAS - HEALTH CHECK COMPLETO{Colors.RESET}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    exit_code = generate_report()
    sys.exit(exit_code)
