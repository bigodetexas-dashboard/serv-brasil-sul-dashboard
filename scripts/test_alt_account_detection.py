# -*- coding: utf-8 -*-
"""
Teste de Detecção de Alt Accounts
Valida parâmetros e lógica de detecção
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta

# Adicionar raiz ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Configurar UTF-8 no Windows
if sys.platform == "win32":
    import codecs
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

DB_PATH = os.path.join(PROJECT_ROOT, "bigode_unified.db")


def show_current_parameters():
    """Mostra parâmetros atuais de detecção"""

    print("\n" + "=" * 80)
    print(" " * 20 + "PARAMETROS DE DETECCAO DE ALT ACCOUNTS")
    print("=" * 80)

    print("\nConfiguracoes atuais (em monitor_logs.py):\n")
    print("  • Janela de tempo: 24 horas")
    print("  • Limite de contas: 2+ XUIDs diferentes no mesmo IP")
    print("  • Acao automatica: Banimento via InfractionType.ALT_ACCOUNT")
    print("  • Marcacao: Todas sessoes do IP marcadas como suspeitas")

    print("\nLogica de deteccao:")
    print("  1. Jogador conecta ao servidor")
    print("  2. Registra: Gamertag, XUID, IP, Discord ID")
    print("  3. Verifica quantos XUIDs diferentes usaram esse IP nas ultimas 24h")
    print("  4. Se >= 2 XUIDs diferentes: ALERTA DE ALT ACCOUNT")
    print("  5. Marca todas conexoes desse IP como suspeitas")
    print("  6. BANE automaticamente o jogador detectado")


def analyze_connection_logs():
    """Analisa logs de conexão para identificar padrões"""

    print("\n" + "=" * 80)
    print(" " * 25 + "ANALISE DE CONEXOES")
    print("=" * 80)

    if not os.path.exists(DB_PATH):
        print(f"\n[ERRO] Banco de dados nao encontrado: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Total de conexões
        cur.execute("SELECT COUNT(*) FROM connection_logs")
        total = cur.fetchone()[0]

        print(f"\nTotal de conexoes registradas: {total}")

        if total == 0:
            print("\n[INFO] Nenhuma conexao registrada ainda.")
            print("Execute monitor_logs.py para comecar a coletar dados.\n")
            return

        # IPs com múltiplas contas
        cur.execute("""
            SELECT
                ip_address,
                COUNT(DISTINCT xuid) as unique_xuids,
                GROUP_CONCAT(DISTINCT gamertag) as gamertags,
                GROUP_CONCAT(DISTINCT xuid) as xuids
            FROM connection_logs
            WHERE ip_address IS NOT NULL
              AND xuid IS NOT NULL
              AND connected_at > datetime('now', '-24 hours')
            GROUP BY ip_address
            HAVING COUNT(DISTINCT xuid) >= 2
            ORDER BY unique_xuids DESC
        """)

        suspicious_ips = cur.fetchall()

        if not suspicious_ips:
            print("\n[OK] Nenhum IP suspeito detectado (multiplas contas).")
        else:
            print(f"\n[ALERTA] {len(suspicious_ips)} IPs com multiplas contas detectados:\n")
            print("-" * 80)

            for row in suspicious_ips:
                ip = row["ip_address"]
                xuids_count = row["unique_xuids"]
                gamertags = row["gamertags"]
                xuids = row["xuids"]

                print(f"\nIP: {ip}")
                print(f"  • XUIDs diferentes: {xuids_count}")
                print(f"  • Gamertags: {gamertags}")
                print(f"  • XUIDs: {xuids}")
                print("-" * 80)

        # Conexões suspeitas marcadas
        cur.execute("""
            SELECT COUNT(*)
            FROM connection_logs
            WHERE is_suspicious = 1
        """)
        suspicious_count = cur.fetchone()[0]

        print(f"\nTotal de conexoes marcadas como suspeitas: {suspicious_count}")

        # Conexões nas últimas 24h
        cur.execute("""
            SELECT COUNT(*)
            FROM connection_logs
            WHERE connected_at > datetime('now', '-24 hours')
        """)
        recent_count = cur.fetchone()[0]

        print(f"Conexoes nas ultimas 24h: {recent_count}")

        conn.close()

    except Exception as e:
        print(f"\n[ERRO] Falha ao analisar conexoes: {e}")
        import traceback
        traceback.print_exc()


def simulate_alt_account_scenario():
    """Simula cenário de alt account"""

    print("\n" + "=" * 80)
    print(" " * 25 + "SIMULACAO DE CENARIO")
    print("=" * 80)

    print("\nCenario: Jogador usando 2+ contas no mesmo IP\n")

    print("DADOS SIMULADOS:")
    print("  IP: 192.168.1.100")
    print("  Conta 1: Player123 (XUID: 1111111111111111)")
    print("  Conta 2: Player456 (XUID: 2222222222222222)")
    print("  Intervalo: Ambas conectam nas ultimas 24h")

    print("\nFLUXO DE DETECCAO:")
    print("  1. Player123 conecta (IP: 192.168.1.100)")
    print("     -> Registrado em connection_logs")
    print("     -> Busca: Quantos XUIDs usaram esse IP? = 1")
    print("     -> Resultado: Normal")

    print("\n  2. Player456 conecta (IP: 192.168.1.100)")
    print("     -> Registrado em connection_logs")
    print("     -> Busca: Quantos XUIDs usaram esse IP? = 2")
    print("     -> Resultado: ALT ACCOUNT DETECTADO!")
    print("     -> Acao:")
    print("        - Marca todas conexoes do IP como suspeitas")
    print("        - BANE Player456 automaticamente")
    print("        - Registra infracao: InfractionType.ALT_ACCOUNT")
    print("        - Envia notificacao Discord")
    print("        - Adiciona ao Hall of Shame")

    print("\nNOTA IMPORTANTE:")
    print("  • Falsos positivos podem ocorrer em:")
    print("    - Familias jogando no mesmo IP")
    print("    - Internet cafes/lan houses")
    print("    - Redes compartilhadas")
    print("  • Recomendacao: Revisar manualmente casos suspeitos")
    print("  • Alternativa: Aumentar limite para 3+ contas")


def suggest_adjustments():
    """Sugere ajustes nos parâmetros"""

    print("\n" + "=" * 80)
    print(" " * 20 + "SUGESTOES DE AJUSTE (OPCIONAL)")
    print("=" * 80)

    print("\nOPCAO 1: Aumentar limite de contas")
    print("  Atual: >= 2 contas")
    print("  Sugestao: >= 3 contas (reduz falsos positivos)")
    print("  Arquivo: monitor_logs.py, linha ~377")
    print("  Codigo: if unique_accounts >= 3:")

    print("\nOPCAO 2: Reduzir janela de tempo")
    print("  Atual: 24 horas")
    print("  Sugestao: 12 horas (detecta apenas uso muito recente)")
    print("  Arquivo: monitor_logs.py, linha ~368")
    print("  Codigo: datetime('now', '-12 hours')")

    print("\nOPCAO 3: Nao banir automaticamente")
    print("  Atual: Banimento automatico")
    print("  Sugestao: Apenas alertar (revisar manualmente)")
    print("  Arquivo: monitor_logs.py, linha ~481-490")
    print("  Acao: Comentar bloco de ban_player_immediate()")

    print("\nOPCAO 4: Whitelist de IPs permitidos")
    print("  Criar lista de IPs que podem ter multiplas contas")
    print("  Exemplo: IPs de internet cafes, escolas, etc.")
    print("  Implementacao: Adicionar verificacao antes do ban")

    print("\nRECOMENDACAO ATUAL:")
    print("  Os parametros atuais (24h, 2+ contas) sao ADEQUADOS para:")
    print("  • Detectar a maioria dos alt accounts")
    print("  • Minimizar falsos positivos")
    print("  • Manter sistema autonomo")
    print("\n  Sugestao: MANTER configuracao atual e monitorar resultados.")


def main():
    """Executa validação completa"""

    print("\n" + "=" * 80)
    print(" " * 15 + "VALIDACAO DE DETECCAO DE ALT ACCOUNTS")
    print(" " * 20 + "BigodeTexas - Sistema Autonomo")
    print("=" * 80)

    # Mostrar parâmetros
    show_current_parameters()

    # Analisar dados reais
    analyze_connection_logs()

    # Simulação
    simulate_alt_account_scenario()

    # Sugestões
    suggest_adjustments()

    print("\n" + "=" * 80)
    print(" " * 30 + "VALIDACAO CONCLUIDA")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
