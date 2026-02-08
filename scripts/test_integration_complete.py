# -*- coding: utf-8 -*-
"""
Teste de Integração Completa - BigodeTexas
Verifica todas as conexões: Nitrado, Discord, Bot, Site, Banco de Dados
"""
import os
import sys
import sqlite3
import requests
from datetime import datetime
from ftplib import FTP
from dotenv import load_dotenv

# Adicionar raiz ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Configurar UTF-8 no Windows
if sys.platform == "win32":
    import codecs
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

load_dotenv()


class IntegrationTester:
    """Testa todas as integrações do sistema"""

    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        self.improvements = []

    def log_result(self, component, status, message, details=None):
        """Registra resultado de teste"""
        self.results[component] = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        if status == "ERROR":
            self.errors.append(f"{component}: {message}")
        elif status == "WARNING":
            self.warnings.append(f"{component}: {message}")

    def print_header(self, title):
        """Imprime cabeçalho"""
        print("\n" + "=" * 80)
        print(f" {title:^78} ")
        print("=" * 80)

    # ==================== TESTE 1: NITRADO FTP ====================

    def test_nitrado_ftp(self):
        """Testa conexão com servidor Nitrado via FTP"""

        self.print_header("TESTE 1: CONEXAO NITRADO (FTP)")

        ftp_host = os.getenv("FTP_HOST")
        ftp_user = os.getenv("FTP_USER")
        ftp_pass = os.getenv("FTP_PASS")
        ftp_port = int(os.getenv("FTP_PORT", 21))

        # Verificar credenciais
        if not all([ftp_host, ftp_user, ftp_pass]):
            self.log_result("Nitrado FTP", "ERROR",
                          "Credenciais FTP nao configuradas no .env")
            print("\n[X] Credenciais FTP NAO configuradas!")
            print("Configure no arquivo .env:")
            print("  FTP_HOST=seu_host")
            print("  FTP_USER=seu_usuario")
            print("  FTP_PASS=sua_senha")
            print("  FTP_PORT=21")
            return False

        print(f"\n[OK] Credenciais encontradas")
        print(f"  Host: {ftp_host}")
        print(f"  User: {ftp_user}")
        print(f"  Port: {ftp_port}")

        # Testar conexão
        try:
            print(f"\nConectando ao servidor FTP...")
            ftp = FTP()
            ftp.connect(ftp_host, ftp_port, timeout=10)
            ftp.login(ftp_user, ftp_pass)

            print(f"[OK] Conexao FTP estabelecida!")

            # Testar listagem de diretórios
            print(f"\nTestando acesso a diretorios...")
            try:
                ftp.cwd("/dayzxb")
                print(f"[OK] Acesso ao diretorio /dayzxb")

                # Verificar arquivo ban.txt
                try:
                    ftp.cwd("/dayzxb/config")
                    files = ftp.nlst()

                    if "ban.txt" in files:
                        print(f"[OK] Arquivo ban.txt encontrado")

                        # Testar leitura
                        from io import BytesIO
                        bio = BytesIO()
                        ftp.retrbinary("RETR ban.txt", bio.write)
                        bio.seek(0)
                        content = bio.read().decode("utf-8", errors="ignore")
                        ban_count = len(content.splitlines())

                        print(f"[OK] Leitura de ban.txt bem-sucedida")
                        print(f"  Bans atuais: {ban_count}")

                        self.log_result("Nitrado FTP", "SUCCESS",
                                      "Conexao e acesso completos",
                                      {"bans": ban_count})
                    else:
                        print(f"[AVISO] Arquivo ban.txt nao encontrado")
                        self.log_result("Nitrado FTP", "WARNING",
                                      "ban.txt nao encontrado")

                except Exception as e:
                    print(f"[AVISO] Erro ao acessar /dayzxb/config: {e}")
                    self.log_result("Nitrado FTP", "WARNING",
                                  f"Erro ao acessar config: {e}")

            except Exception as e:
                print(f"[X] Erro ao acessar /dayzxb: {e}")
                self.log_result("Nitrado FTP", "ERROR",
                              f"Erro ao acessar diretorio: {e}")
                return False

            ftp.quit()
            return True

        except Exception as e:
            print(f"\n[X] ERRO ao conectar ao FTP: {e}")
            self.log_result("Nitrado FTP", "ERROR",
                          f"Falha na conexao: {e}")
            return False

    # ==================== TESTE 2: DISCORD WEBHOOK ====================

    def test_discord_webhook(self):
        """Testa webhook Discord"""

        self.print_header("TESTE 2: DISCORD WEBHOOK")

        webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")

        if not webhook_url or webhook_url == "seu_webhook_url_aqui":
            print("\n[X] Webhook Discord NAO configurado!")
            print("Configure no arquivo .env:")
            print("  NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/...")
            self.log_result("Discord Webhook", "ERROR",
                          "Webhook nao configurado")
            return False

        print(f"\n[OK] Webhook configurado")
        print(f"  URL: {webhook_url[:50]}...")

        # Testar envio
        try:
            print(f"\nEnviando mensagem de teste...")

            embed = {
                "title": "TESTE DE INTEGRACAO - BigodeTexas",
                "description": "Sistema de integracao funcionando!",
                "color": 0x00FF00,
                "fields": [
                    {
                        "name": "Status",
                        "value": "Operacional",
                        "inline": True
                    },
                    {
                        "name": "Data",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Teste de Integracao Completa"
                }
            }

            payload = {
                "username": "Sistema de Integracao",
                "embeds": [embed]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)

            if response.status_code == 204:
                print(f"[OK] Webhook funcionando! Mensagem enviada ao Discord.")
                self.log_result("Discord Webhook", "SUCCESS",
                              "Webhook operacional")
                return True
            else:
                print(f"[X] Erro ao enviar: Status {response.status_code}")
                self.log_result("Discord Webhook", "ERROR",
                              f"Erro HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"\n[X] ERRO ao enviar webhook: {e}")
            self.log_result("Discord Webhook", "ERROR",
                          f"Falha ao enviar: {e}")
            return False

    # ==================== TESTE 3: BANCO DE DADOS ====================

    def test_database(self):
        """Testa banco de dados principal"""

        self.print_header("TESTE 3: BANCO DE DADOS (bigode_unified.db)")

        db_path = os.path.join(PROJECT_ROOT, "bigode_unified.db")

        if not os.path.exists(db_path):
            print(f"\n[X] Banco de dados NAO encontrado: {db_path}")
            self.log_result("Banco de Dados", "ERROR",
                          "Banco nao encontrado")
            return False

        print(f"\n[OK] Banco de dados encontrado")
        print(f"  Path: {db_path}")
        print(f"  Tamanho: {os.path.getsize(db_path) / 1024:.2f} KB")

        # Testar conexão e tabelas
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Listar tabelas
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]

            print(f"\n[OK] Conexao estabelecida")
            print(f"  Tabelas encontradas: {len(tables)}")

            # Verificar tabelas críticas
            critical_tables = [
                "users",
                "player_identities",
                "infractions",
                "connection_logs",
                "bases_v2",
                "events"
            ]

            missing_tables = []
            for table in critical_tables:
                if table in tables:
                    # Contar registros
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"  [OK] {table}: {count} registros")
                else:
                    print(f"  [X] {table}: NAO ENCONTRADA")
                    missing_tables.append(table)

            conn.close()

            if missing_tables:
                self.log_result("Banco de Dados", "WARNING",
                              f"Tabelas faltando: {', '.join(missing_tables)}",
                              {"missing": missing_tables})
            else:
                self.log_result("Banco de Dados", "SUCCESS",
                              "Todas tabelas criticas presentes",
                              {"tables": len(tables)})

            return len(missing_tables) == 0

        except Exception as e:
            print(f"\n[X] ERRO ao acessar banco: {e}")
            self.log_result("Banco de Dados", "ERROR",
                          f"Erro de acesso: {e}")
            return False

    # ==================== TESTE 4: SISTEMA DE FAILOVER ====================

    def test_failover_system(self):
        """Testa sistema de failover"""

        self.print_header("TESTE 4: SISTEMA DE FAILOVER (sync_queue.db)")

        sync_db_path = os.path.join(PROJECT_ROOT, "sync_queue.db")

        if not os.path.exists(sync_db_path):
            print(f"\n[AVISO] Banco sync_queue.db nao encontrado")
            print(f"  Sera criado automaticamente quando monitor_logs.py rodar")
            self.log_result("Sistema Failover", "WARNING",
                          "sync_queue.db nao existe ainda")
            return True  # Não é erro crítico

        print(f"\n[OK] Banco sync_queue.db encontrado")

        try:
            conn = sqlite3.connect(sync_db_path)
            cur = conn.cursor()

            # Verificar tabelas
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]

            if "system_status" in tables:
                print(f"[OK] Tabela system_status existe")

                # Status dos sistemas
                cur.execute("SELECT * FROM system_status")
                rows = cur.fetchall()

                if rows:
                    print(f"\nStatus dos sistemas:")
                    for row in rows:
                        print(f"  Sistema: {row}")
                else:
                    print(f"  [AVISO] Nenhum sistema registrado ainda")

            if "sync_queue" in tables:
                print(f"[OK] Tabela sync_queue existe")

            conn.close()

            self.log_result("Sistema Failover", "SUCCESS",
                          "Sistema de failover operacional")
            return True

        except Exception as e:
            print(f"\n[X] ERRO ao verificar failover: {e}")
            self.log_result("Sistema Failover", "ERROR",
                          f"Erro: {e}")
            return False

    # ==================== TESTE 5: AUTO-BAN SYSTEM ====================

    def test_auto_ban_system(self):
        """Testa sistema de auto-ban"""

        self.print_header("TESTE 5: AUTO-BAN SYSTEM")

        try:
            from auto_ban_system import (
                InfractionType,
                PROTECTED_XUIDS,
                ensure_infractions_table
            )

            print(f"\n[OK] Modulo auto_ban_system importado")

            # Verificar tabela infractions
            ensure_infractions_table()
            print(f"[OK] Tabela infractions verificada/criada")

            # Verificar tipos de infrações
            print(f"\nTipos de infracoes disponiveis:")
            for severity, types in InfractionType.CATEGORIES.items():
                print(f"  {severity}: {len(types)} tipos")

            # Verificar whitelist
            print(f"\nAdmins protegidos: {len(PROTECTED_XUIDS)}")
            for xuid in PROTECTED_XUIDS:
                print(f"  • {xuid}")

            self.log_result("Auto-Ban System", "SUCCESS",
                          "Sistema de auto-ban operacional",
                          {"protected_admins": len(PROTECTED_XUIDS)})
            return True

        except Exception as e:
            print(f"\n[X] ERRO ao testar auto-ban: {e}")
            self.log_result("Auto-Ban System", "ERROR",
                          f"Erro: {e}")
            return False

    # ==================== TESTE 6: SCRIPTS DE MONITORAMENTO ====================

    def test_monitoring_scripts(self):
        """Verifica scripts de monitoramento"""

        self.print_header("TESTE 6: SCRIPTS DE MONITORAMENTO")

        scripts_dir = os.path.join(PROJECT_ROOT, "scripts")

        required_scripts = [
            "monitor_logs.py",
            "test_discord_webhook.py",
            "test_failover_system.py",
            "hall_of_shame.py",
            "test_alt_account_detection.py"
        ]

        print(f"\nVerificando scripts...")

        missing = []
        for script in required_scripts:
            script_path = os.path.join(scripts_dir, script)
            if os.path.exists(script_path):
                size = os.path.getsize(script_path)
                print(f"  [OK] {script} ({size} bytes)")
            else:
                print(f"  [X] {script} NAO ENCONTRADO")
                missing.append(script)

        if missing:
            self.log_result("Scripts Monitoramento", "WARNING",
                          f"Scripts faltando: {', '.join(missing)}")
            return False
        else:
            self.log_result("Scripts Monitoramento", "SUCCESS",
                          "Todos scripts presentes")
            return True

    # ==================== ANALISE DE MELHORIAS ====================

    def analyze_improvements(self):
        """Analisa possíveis melhorias"""

        self.print_header("ANALISE DE MELHORIAS")

        print(f"\nAnalisando sistema...")

        # Melhoria 1: Webhook Discord
        webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
        if not webhook_url or webhook_url == "seu_webhook_url_aqui":
            self.improvements.append({
                "area": "Discord Webhook",
                "priority": "ALTA",
                "description": "Configurar webhook para notificacoes automaticas",
                "action": "Configure NOTIFICATION_WEBHOOK_URL no .env"
            })

        # Melhoria 2: Mais admins na whitelist
        try:
            from auto_ban_system import PROTECTED_XUIDS
            if len(PROTECTED_XUIDS) == 1:
                self.improvements.append({
                    "area": "Whitelist Admins",
                    "priority": "MEDIA",
                    "description": "Adicionar mais admins/moderadores a whitelist",
                    "action": "Editar PROTECTED_XUIDS em auto_ban_system.py"
                })
        except:
            pass

        # Melhoria 3: Monitoramento automático
        self.improvements.append({
            "area": "Monitoramento",
            "priority": "BAIXA",
            "description": "Criar script de health check automatico (cron/scheduled task)",
            "action": "Executar test_integration_complete.py periodicamente"
        })

        # Melhoria 4: Logs estruturados
        self.improvements.append({
            "area": "Logs",
            "priority": "BAIXA",
            "description": "Implementar sistema de logs estruturados (JSON)",
            "action": "Adicionar logging.json para facilitar auditoria"
        })

        # Exibir melhorias
        if self.improvements:
            print(f"\nMelhorias sugeridas: {len(self.improvements)}\n")
            for i, imp in enumerate(self.improvements, 1):
                print(f"{i}. [{imp['priority']}] {imp['area']}")
                print(f"   Descricao: {imp['description']}")
                print(f"   Acao: {imp['action']}\n")
        else:
            print(f"\n[OK] Sistema otimizado! Nenhuma melhoria critica necessaria.")

    # ==================== RELATORIO FINAL ====================

    def print_final_report(self):
        """Imprime relatório final"""

        self.print_header("RELATORIO FINAL DE INTEGRACAO")

        # Contar resultados
        success = sum(1 for r in self.results.values() if r["status"] == "SUCCESS")
        warnings = sum(1 for r in self.results.values() if r["status"] == "WARNING")
        errors = sum(1 for r in self.results.values() if r["status"] == "ERROR")
        total = len(self.results)

        print(f"\nRESUMO DOS TESTES:")
        print(f"  Total: {total}")
        print(f"  Sucesso: {success} ({success/total*100:.1f}%)")
        print(f"  Avisos: {warnings} ({warnings/total*100:.1f}%)")
        print(f"  Erros: {errors} ({errors/total*100:.1f}%)")

        # Status geral
        if errors == 0 and warnings == 0:
            status = "[OK] SISTEMA 100% OPERACIONAL"
        elif errors == 0:
            status = "[AVISO] SISTEMA OPERACIONAL COM AVISOS"
        else:
            status = "[X] SISTEMA COM ERROS CRITICOS"

        print(f"\nSTATUS GERAL: {status}")

        # Detalhes
        if self.errors:
            print(f"\nERROS CRITICOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\nAVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        # Salvar relatório em arquivo
        report_file = os.path.join(PROJECT_ROOT, "integration_report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("RELATORIO DE INTEGRACAO - BigodeTexas\n")
            f.write(f"Data: {datetime.now()}\n\n")
            f.write(f"Status: {status}\n\n")

            f.write(f"Resultados:\n")
            for component, result in self.results.items():
                f.write(f"  {component}: {result['status']} - {result['message']}\n")

            if self.errors:
                f.write(f"\nErros:\n")
                for error in self.errors:
                    f.write(f"  • {error}\n")

            if self.warnings:
                f.write(f"\nAvisos:\n")
                for warning in self.warnings:
                    f.write(f"  • {warning}\n")

        print(f"\nRelatorio salvo em: {report_file}")

    # ==================== EXECUCAO PRINCIPAL ====================

    def run_all_tests(self):
        """Executa todos os testes"""

        print("\n" + "=" * 80)
        print(" " * 20 + "TESTE DE INTEGRACAO COMPLETA")
        print(" " * 25 + "BigodeTexas - Sistema Autonomo")
        print("=" * 80)

        # Executar testes
        self.test_nitrado_ftp()
        self.test_discord_webhook()
        self.test_database()
        self.test_failover_system()
        self.test_auto_ban_system()
        self.test_monitoring_scripts()

        # Análise de melhorias
        self.analyze_improvements()

        # Relatório final
        self.print_final_report()

        print("\n" + "=" * 80)
        print(" " * 30 + "TESTE CONCLUIDO")
        print("=" * 80)


def main():
    """Ponto de entrada"""
    tester = IntegrationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
